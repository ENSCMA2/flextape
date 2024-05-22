python -m experiments.preedit_mistral --ds_name=$1 --alg_name=NONE --model_name=$2 --hparams_fname=mistral-7b.json --num_edits=900 --use_cache --skip_generation --continue_from_run=run_000
python -m experiments.evaluate_mistral --continue_from_run=run_000 --ds_name=$1 --alg_name=MEMIT --model_name=$2 --hparams_fname=mistral-7b.json --num_edits=900 --use_cache --skip_generation;
