#!/bin/bash

${CONDA} run -n myenv python3 -m experiments.evaluate \
    --alg_name=MEMIT \
    --model_name=gpt2-xl \
    --hparams_fname=gpt2-xl.json \
    --num_edits=1 \
    --use_cache

git add -f results/MEMIT/*/*.json
git commit -m "results"
git push