for DS in P21_P101 P21_P19 P27_P101 P27_P21 P27_P19 P101_P27 P19_P21 P19_P101
do 
	echo $DS;
	${CONDA} run -n myenv python -m experiments.preedit_pair --ds_name=$DS --alg_name=NONE --model_name=meta-llama/Llama-2-7b-hf --hparams_fname=llama-7b.json --num_edits=901 --use_cache;
done

for DS in P21_P101 P21_P19 P27_P101 P27_P21 P27_P19 P101_P27 P19_P21 P19_P101
do 
	echo $DS;
	${CONDA} run -n myenv python -m experiments.eval_pair --ds_name=$DS --alg_name=MEMIT --model_name=meta-llama/Llama-2-7b-hf --hparams_fname=llama-7b.json --num_edits=901 --use_cache;
done
