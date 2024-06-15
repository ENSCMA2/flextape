from pathlib import Path

import yaml

with open("globals.yml", "r") as stream:
    data = yaml.safe_load(stream)

(RESULTS_DIR, DATA_DIR, STATS_DIR, HPARAMS_DIR, KV_DIR, PAIR_RESULTS_DIR) = (
    Path(z)
    for z in [
        data["RESULTS_DIR"],
        data["DATA_DIR"],
        data["STATS_DIR"],
        data["HPARAMS_DIR"],
        data["KV_DIR"],
        data["PAIR_RESULTS_DIR"]
    ]
)

REMOTE_ROOT_URL = data["REMOTE_ROOT_URL"]

MODEL_DICT = {"EleutherAI/gpt-j-6B": "gptj",
              "meta-llama/Llama-2-7b-hf": "llama",
              "meta-llama/Llama-2-7b-chat-hf": "llamac",
              "mistralai/Mistral-7B-Instruct-v0.2": "mistral",
              "mistralai/Mistral-7B-v0.1": "mistralb"}
