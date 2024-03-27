${CONDA} run -n myenv python -m experiments.preedit --ds_name=$1 --alg_name=NONE --model_name=meta-llama/Llama-2-7b-hf --hparams_fname=EleutherAI_gpt-j-6B.json --num_edits=900 --use_cache;
${CONDA} run -n myenv python -m experiments.evaluate --ds_name=$1 --alg_name=MEMIT --model_name=meta-llama/Llama-2-7b-hf --hparams_fname=EleutherAI_gpt-j-6B.json --num_edits=900 --use_cache;
