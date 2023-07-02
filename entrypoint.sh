#!/bin/bash

${CONDA} run -n myenv python3 -m experiments.evaluate \
    --alg_name=MEMIT \
    --model_name=gpt2-xl \
    --hparams_fname=gpt2-xl.json \
    --num_edits=1 \
    --use_cache \
    --results_dir=/mnt/u14157_ic_nlp_001_files_nfs/nlpdata1/home/halevy/flextape/results/MEMIT

git add -f results/MEMIT/*/*.json
git commit -m "results"
git push