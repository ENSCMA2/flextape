#!/bin/bash
git pull

cd Quark-main
${CONDA} run -n myenv python main.py

git add -A
git add -f outputs/*
git commit -m "results"
git push