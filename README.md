# "Flex Tape Can't Fix That": Pitfalls of Model Editing
Here is the code used for the paper  _"Flex Tape Can't Fix That": Pitfalls of Model Editing_. Experimental code is mainly in the `experiments` directory, data preprocessing code is in `dsets`, and evaluation code is in `eval`. This repo was cloned and modified based on [MEMIT](https://memit.baulab.info/), and some instructions have been duplicated from there.

## Installation

We recommend `conda` for managing Python, CUDA, and PyTorch; `pip` is for everything else. To get started, simply install `conda` and run:
```bash
CONDA_HOME=$CONDA_HOME ./scripts/setup_conda.sh
```

`$CONDA_HOME` should be the path to your `conda` installation, e.g., `~/miniconda3`.

## Running the Evaluation Suites

[`experiments/evaluate.py`](experiments/evaluate.py) can be used to evaluate any method in [`baselines/`](baselines/).

For example:
```
python3 -m experiments.evaluate \
    --alg_name=MEMIT \
    --model_name=EleutherAI/gpt-j-6B \
    --hparams_fname=EleutherAI_gpt-j-6B.json \
    --num_edits=10000 \
    --use_cache
```
Results from each run are stored at `results/<model_name>/<method_name>/run_<run_id>` in a specific format:
```bash
results/
|__ MODEL_NAME/
    |__ MEMIT/
        |__ run_<run_id>/
            |__ params.json
            |__ case_0.json
            |__ case_1.json
            |__ ...
            |__ case_10000.json
```
To run the GPT-J-based cross-subject experiments described in the paper, we've created a shell script that can be invoked by the following command:
```bash
bash eval.sh [DS_NAME]
```
where `[DS_NAME]` is one of the properties or property pairs among the files that begin with `seesaw_cf_` in `data/` - e.g. `P101`, `P103`, `P101_P21`, etc.

To run cross-property experiments based on GPT-J, run:
```bash
bash eval_pair.sh
```

For `Llama`-based experiments, we have two analogous shell scripts, but they can be run in succession with one script. Specifically, run:
```bash
bash llama_script.sh
```
To run a different `Llama`-based model, open `job_script.sh` and change the model name to your desired model name (it should be the HuggingFace identifier of the model). Additionally, open `util/globals.py` and add a shorthand for your new model in the `MODEL_DICT` variable.

For `Mistral`-based experiments, we have an analogous script:
```bash
bash mistral_script.sh
```
Similarly, change the model name in `mistral_script.sh` to the HuggingFace identifier of your desired model, and add a shorthand for the identifier in `MODEL_DICT` within `util/globals.py`.

There are also several evaluation scripts for the results produced by these experiments, found in the `eval/completion_evaluation` directory, and they can also be run all together through shell scripts in this directory. Specifically, to evaluate single-property completions on the axis of gender, you can run
```bash
cd eval/completion_evaluation
bash gender_eval.sh [MODEL_NAME] [METHOD_NAME]
```
For evaluation of single-property completions by race and geographic origin (since both are based on ethnic groups, they are run in one script), run
```bash
cd eval/completion_evaluation
bash race_eval.sh [MODEL_NAME] [METHOD_NAME]
```
For both cases, `MODEL_NAME` is a shorthand for the name of the model, `METHOD_NAME` is the editing method being evaluated - `FT`, `MEND`, or `MEMIT`. The conversions from full model name to shorthand are as follows for the five models we have included in our paper:
```python
MODEL_DICT = {"EleutherAI/gpt-j-6B": "gptj",
              "meta-llama/Llama-2-7b-hf": "llama",
              "meta-llama/Llama-2-7b-chat-hf": "llamac",
              "mistralai/Mistral-7B-Instruct-v0.2": "mistral",
              "mistralai/Mistral-7B-v0.1": "mistralb"}
```
For example, to evaluate `Llama2-chat` by race on `MEMIT`, you would run:
```bash
cd eval/completion_evaluation
bash race_eval.sh llamac MEMIT
```

For evaluation of cross-property completions, run
```bash
cd eval
python pair_single.py [MODEL_NAME] [METHOD_NAME]
```
where `MODEL_NAME` and `METHOD_NAME` are defined as above.

We also provide a script to get `t`-scores for significance testing of our results:
```bash
cd eval
python ttests.py [MODEL_NAME] [METHOD_NAME]
```

Finally, if you're curious about agreement metrics for our long-form text annotations, feel free to run
```bash
cd eval
python agreement.py
```
<!--
## How to Cite

```bibtex
@misc{halevy2024flex,
      title={"Flex Tape Can't Fix That": Bias and Misinformation in Edited Language Models}, 
      author={Karina Halevy and Anna Sotnikova and Badr AlKhamissi and Syrielle Montariol and Antoine Bosselut},
      year={2024},
      eprint={2403.00180},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
```
-->
