#!/bin/bash

${CONDA} run -n myenv python3 -m experiments.evaluate \
    --alg_name=MEMIT \
    --model_name=EleutherAI/gpt-j-6B \
    --hparams_fname=EleutherAI_gpt-j-6B.json \
    --num_edits=1 \
    --use_cache
    --skip_generation

git add -f results/MEMIT/*/*.json
git commit -m "results"
git push