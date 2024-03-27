for DS in P21_P101 P21_P19 P27_P101 P27_P21 P27_P19 P101_P27 P19_P21 P19_P101
do 
	echo $DS;
	${CONDA} run -n myenv python -m experiments.preedit_pair --ds_name=$DS --alg_name=NONE --model_name=EleutherAI/gpt-j-6B --hparams_fname=EleutherAI_gpt-j-6B.json --num_edits=901 --use_cache;
done

for DS in P21_P101 P21_P19 P27_P101 P27_P21 P27_P19 P101_P27 P19_P21 P19_P101
do 
	echo $DS;
	${CONDA} run -n myenv python -m experiments.eval_pair --ds_name=$DS --alg_name=MEMIT --model_name=EleutherAI/gpt-j-6B --hparams_fname=EleutherAI_gpt-j-6B.json --num_edits=901 --use_cache;
done
