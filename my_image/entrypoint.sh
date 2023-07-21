#!/bin/bash
git pull

cd tpatcher
${CONDA} run -n myenv python src/dataset/zsre_dataloader.py
${CONDA} run -n myenv python scripts/main.py

git add -A
git commit -m "results"
git push