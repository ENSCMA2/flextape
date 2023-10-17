${CONDA} run -n myenv python -m experiments.preedit --ds_name=$1 --alg_name=NONE --model_name=EleutherAI/gpt-j-6B --hparams_fname=EleutherAI_gpt-j-6B.json --num_edits=900 --use_cache;
${CONDA} run -n myenv python -m experiments.evaluate --ds_name=$1 --alg_name=FT --model_name=EleutherAI/gpt-j-6B --hparams_fname=EleutherAI_gpt-j-6B_constr.json --num_edits=900 --use_cache;
${CONDA} run -n myenv python -m experiments.evaluate --ds_name=$1 --alg_name=MEND --model_name=EleutherAI/gpt-j-6B --hparams_fname=EleutherAI_gpt-j-6B.json --num_edits=900 --use_cache;
${CONDA} run -n myenv python -m experiments.evaluate --ds_name=$1 --alg_name=MEMIT --model_name=EleutherAI/gpt-j-6B --hparams_fname=EleutherAI_gpt-j-6B.json --num_edits=900 --use_cache;
