#!/bin/bash
git pull

cd REMEDI-main
${CONDA} run -n myenv python -m spacy download en_core_web_sm
${CONDA} run -n myenv python -m scripts.train_editors -m gptj -n p103 -d seesaw_103 -l 1 --lam-kl 100 --device cuda
${CONDA} run -n myenv python -m scripts.train_editors -m gptj -n p104 -d seesaw_103 -l 1 --lam-kl 100 --device cuda

git add -A
git commit -m "results"
git push