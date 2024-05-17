import json
import shutil
from itertools import islice
from time import time
from typing import Tuple, Union
import pandas as pd
import torch
from accelerate import *
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer, LlamaForCausalLM, LlamaTokenizer
from pathlib import Path

from dsets import (
    AttributeSnippets,
    CounterFactDataset,
    MENDQADataset,
    MultiCounterFactDataset,
    get_tfidf_vectorizer,
)
from memit import MEMITHyperParams, apply_memit_to_model
from experiments.py.eval_utils_counterfact import compute_rewrite_quality_counterfact, compute_pair_quality
from util import nethook
from util.globals import *

MODEL_DICT = {"EleutherAI/gpt-j-6B": "gptj",
              "meta-llama/Llama-2-7b-hf": "llama",
              "mistralai/Mistral-7B-Instruct-v0.2": "mistral"}

genders = set(["male", "female"])
fow = set(pd.read_csv("data/fow.csv", names = ["Code", "String", "Category"])["String"].tolist())
city_names = set(pd.read_csv("data/city_to_country.csv", names = ["City", "Country", "UCity", "CName"])["CName"].tolist())
countries_of_citizenship = set(pd.read_csv("data/P27_cats.csv", names = ["Code", "Country", "Continent"])["Country"].tolist())

CAND_DICT = {
    "P21": genders,
    "P101": fow,
    "P27": countries_of_citizenship,
    "P19": city_names
}

def log(message):
    with open("logs.txt", "a") as o:
        o.write(message + "\n")

def main(
    alg_name: str,
    model_name: Union[str, Tuple],
    hparams_fname: str,
    ds_name: str,
    dataset_size_limit: int,
    continue_from_run: str,
    skip_generation_tests: bool,
    generation_test_interval: int,
    conserve_memory: bool,
    dir_name: str,
    num_edits: int = 1,
    use_cache: bool = False,
):
    log("starting main")
    RES_DIR = PAIR_RESULTS_DIR / Path(MODEL_DICT[model_name])
    splat = ds_name.split("_")
    p1 = splat[0]
    p2 = splat[1]

    # Determine run directory
    # Create new dir if not continuing from prev run OR prev run doesn't exist
    if (
        continue_from_run is None
        or not (run_dir := RES_DIR / dir_name / continue_from_run).exists()
    ):
        continue_from_run = None
    if continue_from_run is None:
        alg_dir = RES_DIR / dir_name
        if alg_dir.exists():
            id_list = [
                int(str(x).split("_")[-1])
                for x in alg_dir.iterdir()
                if str(x).split("_")[-1].isnumeric()
            ]
            run_id = 0 if not id_list else max(id_list) + 1
        else:
            run_id = 0
        run_dir = RES_DIR / dir_name / f"run_{str(run_id).zfill(3)}"
        run_dir.mkdir(parents=True, exist_ok=True)
    print(f"Results will be stored at {run_dir}")

    # Instantiate vanilla model
    log("Instantiating model")
    tok = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2")
    model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2", device_map = "auto")
    tok.pad_token_id = tok.eos_token_id

    # Load data
    log("Loading dataset, attribute snippets, tf-idf data")
    snips = AttributeSnippets(DATA_DIR) if not skip_generation_tests else None
    vec = get_tfidf_vectorizer(DATA_DIR) if not skip_generation_tests else None

    ds_class, ds_eval_method = MultiCounterFactDataset, compute_pair_quality
    ds = ds_class(DATA_DIR, ds_name, tok=tok, size=dataset_size_limit)

    # Get cache templates
    cache_template = None
    if use_cache:
        cache_template = (
            KV_DIR
            / f"{model_name.replace('/', '_')}_{alg_name}"
            / f"{ds_name}_layer_{{}}_clamp_{{}}_case_{{}}.npz"
        )
        log(f"Will load cache from {cache_template}")

    # Iterate through dataset
    for record_chunks in chunks(ds, num_edits):
        case_result_template = str(run_dir / "{}_edits-case_{}.json")
        # Is the chunk already done?
        already_finished = True
        for record in record_chunks:
            if not Path(
                case_result_template.format(num_edits, record["case_id"])
            ).exists():
                already_finished = False
                break
        if already_finished:
            continue

        # Compute weight changes + record weights that changed
        case_ids = [record["case_id"] for record in record_chunks]
        args_conserve_memory = (
            dict(return_orig_weights_device=("cpu" if conserve_memory else "cuda"))
            if conserve_memory
            else dict()
        )
        etc_args = dict(cache_template=cache_template) if any(alg in alg_name for alg in ["ROME", "MEMIT"]) else dict()

        # Evaluate new model
        log("about to evaluate")
        start = time()
        for record in record_chunks:
            out_file = Path(case_result_template.format(num_edits, record["case_id"]))
            if out_file.exists():
                print(f"Skipping {out_file}; already exists")
                continue

            metrics = {
                "case_id": record["case_id"],
                "grouped_case_ids": case_ids,
                "num_edits": num_edits,
                "requested_rewrite": record["requested_rewrite"],
                "pre": ds_eval_method(
                    model,
                    tok,
                    record,
                    CAND_DICT[p2],
                ),
                "time": time() - start
            }

            # Dump metrics in .json
            print(out_file)
            with open(out_file, "w") as f:
                json.dump(metrics, f, indent=1)

        print("Evaluation took", time() - start)


def window(seq, n=2):
    "Returns a sliding window (of width n) over data from the iterable"
    "   s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...                   "
    it = iter(seq)
    result = tuple(islice(it, n))
    if len(result) == n:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result


def chunks(arr, n):
    """Yield successive n-sized chunks from arr."""
    for i in range(0, len(arr), n):
        yield arr[i : i + n]


if __name__ == "__main__":
    import argparse
    log("getting started")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--alg_name",
        choices=["NONE"],
        default="ROME",
        help="Editing algorithm to use. Results are saved in results/<alg_name>/<run_id>, "
        "where a new run_id is generated on each run. "
        "If continuing from previous run, specify the run_id in --continue_from_run.",
        required=True,
    )
    parser.add_argument(
        "--model_name",
        choices=["meta-llama/Llama-2-7b-hf", "mistralai/Mistral-7B-Instruct-v0.2"],
        default="mistralai/Mistral-7B-Instruct-v0.2",
        help="Model to edit.",
        required=True,
    )
    parser.add_argument(
        "--hparams_fname",
        type=str,
        default="mistral-7b.json",
        help="Name of hyperparameters file, located in the hparams/<alg_name> folder.",
        required=True,
    )
    parser.add_argument(
        "--ds_name",
        choices=["mcf", "cf", "zsre", "P101_P21", "P101", "P103", "P21_P101", "P21_P19", "P27_P101", "P27_P21", "P27_P19", "P101_P27", "P19_P21", "P19_P101"],
        default="mcf",
        help="Dataset to perform evaluations on. Either CounterFact (cf), MultiCounterFact (mcf), or zsRE (zsre).",
    )
    parser.add_argument(
        "--continue_from_run",
        type=str,
        default=None,
        help="If continuing from previous run, set to run_id. Otherwise, leave as None.",
    )
    parser.add_argument(
        "--dataset_size_limit",
        type=int,
        default=None,
        help="Truncate CounterFact to first n records.",
    )
    parser.add_argument(
        "--skip_generation_tests",
        dest="skip_generation_tests",
        action="store_true",
        help="Only run fast probability-based tests without slow generation tests. "
        "Useful for quick debugging and hyperparameter sweeps.",
    )
    parser.add_argument(
        "--generation_test_interval",
        type=int,
        default=1,
        help="One generation test is performed every [flag_value] iterations. If -1, generation tests are skipped.",
    )
    parser.add_argument(
        "--conserve_memory",
        dest="conserve_memory",
        action="store_true",
        help="Reduce memory usage during evaluation at the cost of a minor slowdown. "
        "Backs up model weights on CPU instead of GPU.",
    )
    parser.add_argument(
        "--num_edits",
        type=int,
        default=1,
        help="Number of rewrites to perform simultaneously.",
    )
    parser.add_argument(
        "--use_cache",
        dest="use_cache",
        action="store_true",
        help="Use cached k/v pairs",
    )
    parser.set_defaults(skip_generation_tests=False, conserve_memory=False)
    args = parser.parse_args()

    main(
        args.alg_name,
        args.model_name,
        args.hparams_fname,
        args.ds_name,
        args.dataset_size_limit,
        args.continue_from_run,
        args.skip_generation_tests,
        args.generation_test_interval,
        args.conserve_memory,
        dir_name=args.alg_name,
        num_edits=args.num_edits,
        use_cache=args.use_cache,
    )
