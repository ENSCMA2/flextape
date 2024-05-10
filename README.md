# "Flex Tape Can't Fix That": Pitfalls of Model Editing
Here is the code used for the paper  _"Flex Tape Can't Fix That": Pitfalls of Model Editing_. Experimental code is mainly in the `experiments` directory, data preprocessing code is in `dsets`, and evaluation code is in `eval`. This repo was cloned and modified based on [MEMIT](https://memit.baulab.info/), and some instructions have been duplicated from there.

## Table of Contents

- [Installation](#installation)
- [MEMIT Algorithm Demo](#memit-algorithm-demo)
- [Running the Full Evaluation Suite](#running-the-full-evaluation-suite)
- [Generating Scaling Curves](#generating-scaling-curves)
- [How to Cite](#how-to-cite)

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
Results from each run are stored at `results/<method_name>/run_<run_id>` in a specific format:
```bash
results/
|__ MEMIT/
    |__ MODEL_NAME/
        |__ run_<run_id>/
            |__ params.json
            |__ case_0.json
            |__ case_1.json
            |__ ...
            |__ case_10000.json
```
To run the GPT-J-based single-property experiments described in the paper, we've created a shell script that can be invoked by the following command:
```bash
bash eval.sh [DS_NAME]
```
where `[DS_NAME]` is one of the properties or property pairs among the files that begin with `seesaw_cf_` in `data/` - e.g. `P101`, `P103`, `P101_P21`, etc.

To run cross-property experiments based on GPT-J, you can run:
```bash
bash eval_pair.sh
```

For `Llama`-based experiments, we have two analogous shell scripts. For single-property experiments, you can run
```bash
bash eval_llama.sh [DS_NAME]
```
where `DS_NAME` has the same options as it does when running `eval.sh`.

For cross-property experiments, run
```bash
bash eval_pair_llama.sh
```

There are also several evaluation scripts for the results produced by these experiments, found in the `eval/completion_evaluation` directory, and they can also be run all together through shell scripts in this directory. Specifically, to evaluate single-property completions on the axis of gender, you can run
```bash
cd eval/completion_evaluation
bash gender_eval.sh [MODEL_NAME] [METHOD_NAME]
```
For evaluation of single-property completions by race, run
```bash
cd eval/completion_evaluation
bash race_eval.sh [MODEL_NAME] [METHOD_NAME]
```
For both cases, `MODEL_NAME` is a shorthand for the name of the model - either `llama` or `gptj`. `METHOD_NAME` is the editing method being evaluated - `FT`, `MEND`, or `MEMIT`.

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
