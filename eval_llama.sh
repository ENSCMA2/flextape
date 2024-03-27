python -m experiments.preedit_llama --ds_name=$1 --alg_name=NONE --model_name=meta-llama/Llama-2-7b-hf --hparams_fname=llama-7b.json --num_edits=900 --use_cache 
&&
python -m experiments.evaluate_llama --ds_name=$1 --alg_name=MEMIT --model_name=meta-llama/Llama-2-7b-hf --hparams_fname=llama-7b.json --num_edits=900 --use_cache;
