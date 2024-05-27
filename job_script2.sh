#!/bin/bash
#SBATCH --job-name=flextapebig
#SBATCH --output=flextapebig.out
#SBATCH --error=flextapebig.err
#SBATCH --partition=long
#SBATCH --nodes=1
#SBATCH --gres=gpu:10
#SBATCH --ntasks-per-node=1
#SBATCH --mem=80GB
#SBATCH --cpus-per-task=16
#SBATCH --time=100:00:00

for DS in "P101" "P103";
do
# python -m experiments.preedit_mistral --ds_name=$DS --alg_name=NONE --model_name=mistralai/Mistral-7B-v0.1 --hparams_fname=mistral-7b.json --num_edits=900 --use_cache --skip_generation --continue_from_run=run_001
python -m experiments.evaluate_mistral --continue_from_run=run_001 --ds_name=$DS --alg_name=MEMIT --model_name=mistralai/Mistral-7B-v0.1 --hparams_fname=mistral-7b.json --num_edits=900 --use_cache --skip_generation;
done
