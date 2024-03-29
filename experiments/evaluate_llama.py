import json
import shutil
from itertools import islice
from time import time
from typing import Tuple, Union

import torch
from accelerate import *
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer, LlamaForCausalLM, LlamaTokenizer

from dsets import (
    AttributeSnippets,
    CounterFactDataset,
    MENDQADataset,
    MultiCounterFactDataset,
    get_tfidf_vectorizer,
)
from memit import MEMITHyperParams, apply_memit_to_model
from experiments.py.eval_utils_counterfact import compute_rewrite_quality_counterfact
from util import nethook
from util.globals import *

ALG_DICT = {
    "MEMIT": (MEMITHyperParams, apply_memit_to_model),
}

DS_DICT = {
    "P101": (MultiCounterFactDataset, compute_rewrite_quality_counterfact),
    "P103": (MultiCounterFactDataset, compute_rewrite_quality_counterfact),
    "P21_P101": (MultiCounterFactDataset, compute_rewrite_quality_counterfact),
    "P101_P21": (MultiCounterFactDataset, compute_rewrite_quality_counterfact),
    "P19_P21": (MultiCounterFactDataset, compute_rewrite_quality_counterfact),
    "P19_P101": (MultiCounterFactDataset, compute_rewrite_quality_counterfact),
    "P27_P21": (MultiCounterFactDataset, compute_rewrite_quality_counterfact),
    "P27_P101": (MultiCounterFactDataset, compute_rewrite_quality_counterfact),
    "P27_P19": (MultiCounterFactDataset, compute_rewrite_quality_counterfact),
    "P101_P27": (MultiCounterFactDataset, compute_rewrite_quality_counterfact)
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
    # Set algorithm-specific variables
    params_class, apply_algo = ALG_DICT[alg_name]

    # Determine run directory
    # Create new dir if not continuing from prev run OR prev run doesn't exist
    if (
        continue_from_run is None
        or not (run_dir := RESULTS_DIR / dir_name / continue_from_run).exists()
    ):
        continue_from_run = None
    if continue_from_run is None:
        alg_dir = RESULTS_DIR / dir_name
        if alg_dir.exists():
            id_list = [
                int(str(x).split("_")[-1])
                for x in alg_dir.iterdir()
                if str(x).split("_")[-1].isnumeric()
            ]
            run_id = 0 if not id_list else max(id_list) + 1
        else:
            run_id = 0
        run_dir = RESULTS_DIR / dir_name / f"run_{str(run_id).zfill(3)}"
        run_dir.mkdir(parents=True, exist_ok=True)
    print(f"Results will be stored at {run_dir}")

    # Get run hyperparameters
    params_path = (
        run_dir / "params.json"
        if continue_from_run is not None
        else HPARAMS_DIR / alg_name / hparams_fname
    )
    hparams = params_class.from_json(params_path)
    if not (run_dir / "params.json").exists():
        shutil.copyfile(params_path, run_dir / "params.json")
    log(f"Executing {alg_name} with parameters {hparams}")

    # Instantiate vanilla model
    log("Instantiating model")
    model = LlamaForCausalLM.from_pretrained(model_name, torch_dtype=torch.float32, device_map='auto')
    tok = LlamaTokenizer.from_pretrained(model_name)
    tok.pad_token_id = tok.eos_token_id
    print(model)
    print(model.config)


    # Load data
    log("Loading dataset, attribute snippets, tf-idf data")
    snips = AttributeSnippets(DATA_DIR) if not skip_generation_tests else None
    vec = get_tfidf_vectorizer(DATA_DIR) if not skip_generation_tests else None

    if num_edits > 1:
        assert ds_name != "cf", f"{ds_name} does not support multiple edits"

    ds_class, ds_eval_method = DS_DICT[ds_name]
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
        log(f"working on {case_result_template}")
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
        log(f"about to start {record['case_id']}")
        start = time()
        log(f"started {record['case_id']}")
        edited_model, weights_copy = apply_algo(
            model,
            tok,
            [
                {"case_id": record["case_id"], **record["requested_rewrite"]}
                for record in record_chunks
            ],
            hparams,
            copy=False,
            return_orig_weights=True,
            **args_conserve_memory,
            **etc_args,
        )
        exec_time = time() - start
        log(f"Execution took {exec_time}")

        # Evaluate new model
        log("about to evaluate")
        start = time()
        gen_test_vars = [snips, vec]
        for record in record_chunks:
            out_file = Path(case_result_template.format(num_edits, record["case_id"]))
            if out_file.exists() or int(record["case_id"]) != 21914:
                print(f"Skipping {out_file}; already exists")
                continue

            metrics = {
                "case_id": record["case_id"],
                "grouped_case_ids": case_ids,
                "num_edits": num_edits,
                "requested_rewrite": record["requested_rewrite"],
                "time": exec_time,
                "post": ds_eval_method(
                    edited_model,
                    tok,
                    record,
                    *(
                        gen_test_vars
                        if record["case_id"] % generation_test_interval == 0
                        else [None, None]
                    ),  # Only test generation every generation_test_interval cases
                ),
            }

            # Dump metrics in .json
            with open(out_file, "w") as f:
                json.dump(metrics, f, indent=1)

        # Restore original weights
        with torch.no_grad():
            for k, v in weights_copy.items():
                nethook.get_parameter(model, k)[...] = v.to("cuda")

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
        choices=["MEMIT", "ROME", "FT", "MEND"],
        default="MEMIT",
        help="Editing algorithm to use. Results are saved in results/<alg_name>/<run_id>, "
        "where a new run_id is generated on each run. "
        "If continuing from previous run, specify the run_id in --continue_from_run.",
        required=True)
    parser.add_argument(
        "--model_name",
        choices=["EleutherAI/gpt-j-6B", "meta-llama/Llama-2-7b-hf"],
        default="Llama-2-7b-hf",
        help="Model to edit.",
        required=True,)
    parser.add_argument(
        "--hparams_fname",
        type=str,
        default="llama-7b.json",
        help="Name of hyperparameters file, located in the hparams/<alg_name> folder.",
        required=True,)
    parser.add_argument(
        "--ds_name",
        choices=["P101_P21", "P101", "P103", "P21_P101", "P27_P21", "P27_P101", "P27_P19", "P101_P27", "P21_P19", "P19_P21", "P19_P101"],
        default="mcf",
        help="Dataset to perform evaluations on. Either CounterFact (cf), MultiCounterFact (mcf), or zsRE (zsre).",)
    parser.add_argument(
        "--continue_from_run",
        type=str,
        default=None,
        help="If continuing from previous run, set to run_id. Otherwise, leave as None.",)
    parser.add_argument(
        "--dataset_size_limit",
        type=int,
        default=None,
        help="Truncate CounterFact to first n records.",)
    parser.add_argument(
        "--skip_generation_tests",
        dest="skip_generation_tests",
        action="store_true",
        help="Only run fast probability-based tests without slow generation tests. "
        "Useful for quick debugging and hyperparameter sweeps.",)
    parser.add_argument(
        "--generation_test_interval",
        type=int,
        default=1,
        help="One generation test is performed every [flag_value] iterations. If -1, generation tests are skipped.",)
    parser.add_argument(
        "--conserve_memory",
        dest="conserve_memory",
        action="store_true",
        help="Reduce memory usage during evaluation at the cost of a minor slowdown. "
        "Backs up model weights on CPU instead of GPU.",)
    parser.add_argument(
        "--num_edits",
        type=int,
        default=1,
        help="Number of rewrites to perform simultaneously.",)
    parser.add_argument(
        "--use_cache",
        dest="use_cache",
        action="store_true",
        help="Use cached k/v pairs",)
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
