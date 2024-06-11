for DS in P101_P21 P27_P19 P21_P101 P27_P101 P27_P21 P27_P19 P101_P27 P19_P21 P19_P101
do 
	echo $DS;
	# python -m experiments.preedit_pair_mistral --ds_name=$DS --alg_name=NONE --model_name=$1 --hparams_fname=mistral-7b.json --num_edits=901 --use_cache --skip_generation_tests --continue_from_run=run_000;
done

for DS in P101_P21 P27_P19 P21_P101 P27_P101 P27_P21 P27_P19 P101_P27 P19_P21 P19_P101
do 
	echo $DS;
	python -m experiments.eval_pair_mistral --ds_name=$DS --alg_name=MEMIT --model_name=$1 --hparams_fname=mistral-7b.json --num_edits=901 --use_cache --skip_generation_tests --continue_from_run=run_000;
done
