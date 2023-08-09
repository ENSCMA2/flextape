#!/bin/bash
git pull

cd REMEDI-main
${CONDA} run -n myenv python -m spacy download en_core_web_sm
${CONDA} run -n myenv python -m scripts.train_editors -m gptj -n p103 -d seesaw_103 -l 1 --lam-kl 100 --device cuda
${CONDA} run -n myenv python -m scripts.eval_fact_gen -n p103eval -e results/p103 -m gptj -l 1 --device cuda

git add -A
git add -f results/p103eval/*.json
git add -f results/p103eval/linear/1/*.json
git commit -m "results"
git push