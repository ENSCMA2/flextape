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

for DS in "P103" ;
# "P21_P101" "P27_P101" "P19_P101" "P101";
do
python -m experiments.preedit_llama --ds_name=$DS --alg_name=NONE --model_name=meta-llama/Llama-2-7b-chat-hf --hparams_fname=llama-7b.json --num_edits=900 --use_cache --skip_generation --continue_from_run=run_001 --eff
python -m experiments.evaluate_llama --continue_from_run=run_001 --ds_name=$DS --alg_name=MEMIT --model_name=meta-llama/Llama-2-7b-chat-hf --hparams_fname=llama-7b.json --num_edits=900 --use_cache --skip_generation --eff;
done
