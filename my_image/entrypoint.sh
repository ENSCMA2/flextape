#!/bin/bash

${CONDA} run -n myenv python3 -m experiments.evaluate \
    --alg_name=MEMIT \
    --model_name=EleutherAI/gpt-j-6B \
    --hparams_fname=EleutherAI_gpt-j-6B.json \
    --num_edits=10000 \
    --use_cache