#!/bin/bash
#SBATCH --job-name=flextape
#SBATCH --output=flextape.out
#SBATCH --error=flextape.err
#SBATCH --partition=long
#SBATCH --nodes=1
#SBATCH --gres=gpu:8
#SBATCH --ntasks-per-node=1
#SBATCH --mem=80GB
#SBATCH --cpus-per-task=16
#SBATCH --time=100:00:00

bash eval_pair_mistral.sh;

for DS in "P21_P101" "P27_P101" "P19_P101";
do
python -m experiments.preedit_mistral --ds_name=$DS --alg_name=NONE --model_name=mistralai/Mistral-7B-Instruct-v0.2 --hparams_fname=mistral-7b.json --num_edits=900 --use_cache --skip_generation --continue_from_run=run_001
python -m experiments.evaluate_mistral --continue_from_run=run_001 --ds_name=$DS --alg_name=MEMIT --model_name=mistralai/Mistral-7B-Instruct-v0.2 --hparams_fname=mistral-7b.json --num_edits=900 --use_cache --skip_generation;
done
