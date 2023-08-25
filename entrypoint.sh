#!/bin/bash
git pull

${CONDA} run -n myenv python -m experiments.evaluate --alg_name=FT --model_name=EleutherAI/gpt-j-6B --hparams_fname=EleutherAI_gpt-j-6B_constr.json --num_edits=900 --ds_name=P101
${CONDA} run -n myenv python -m experiments.evaluate --alg_name=FT --model_name=EleutherAI/gpt-j-6B --hparams_fname=EleutherAI_gpt-j-6B_constr.json --num_edits=900 --ds_name=P103
${CONDA} run -n myenv python -m experiments.preedit --alg_name=NONE --model_name=EleutherAI/gpt-j-6B --hparams_fname=EleutherAI_gpt-j-6B.json --num_edits=900 --ds_name=P103
${CONDA} run -n myenv python -m experiments.preedit --alg_name=NONE --model_name=EleutherAI/gpt-j-6B --hparams_fname=EleutherAI_gpt-j-6B.json --num_edits=900 --ds_name=P101

git add -A
git commit -m "results"
git push