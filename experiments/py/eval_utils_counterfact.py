"""
Contains evaluation utilities for pytorch-based rewriting methods.
To use, simply call `compute_rewrite_quality_counterfact` with the
appropriate arguments, which returns a dictionary containing them.
"""

import typing
from itertools import chain

import nltk
import numpy as np
import scipy
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import AutoModelForCausalLM, AutoTokenizer

from dsets import AttributeSnippets
from util.generate import generate_fast
from util.perplexity import perplexity
nltk.download('punkt')

def compute_rewrite_quality_counterfact(model: AutoModelForCausalLM, tok: AutoTokenizer, record: typing.Dict, snips: AttributeSnippets, vec: TfidfVectorizer) -> typing.Dict:
    """
    Given a rewritten model, computes generalization and specificity metrics for
    the desired rewrite (passed in via the CounterFact dataset record). Returns a
    dictionary containing those metrics.

    :param model: Rewritten model
    :param tok: Tokenizer
    :param record: CounterFact dataset record
    :paran snips: ???
    :param vec: ???

    :return: Dictionary containing rewriting metrics
    """

    # First, unpack rewrite evaluation record.
    subject, target_new, target_true = (
        record["requested_rewrite"][x] for x in ["subject", "target_new", "target_true"]
    )
    rewrite_prompts = [record["requested_rewrite"]["prompt"].format(subject)]
    # neighborhood_prompts = record["neighborhood_prompts"]
    generation_prompts = record["generation_prompts"]
    attribute_prompts = record["attribute_prompts"]
    # Form a list of lists of prefixes to test.
    prob_prompts = [
        # rewrite_prompts,
        # neighborhood_prompts,
        attribute_prompts
    ]
    which_correct = [
        # [0 for _ in range(len(rewrite_prompts))],
        # [1 for _ in range(len(neighborhood_prompts))],
        [1 for _ in range(len(attribute_prompts))],
    ]
    # Flatten all the evaluated prefixes into one list.
    prob_prompts_chain = list(chain(*prob_prompts))
    which_correct_chain = list(chain(*which_correct))
    batch_size = 1
    done = 0
    probs, targets_correct = [], []
    while done < len(prob_prompts_chain):
        last = min(done + batch_size, len(prob_prompts_chain))
        probs_b, targets_correct_b = test_batch_prediction(
            model,
            tok,
            prob_prompts_chain[done:last],
            which_correct_chain[done:last],
            target_new["str"],
            target_true["str"],
        )
        probs += probs_b
        targets_correct += targets_correct_b
        done += batch_size

    assert(len(prob_prompts_chain) == len(probs))
    assert(len(which_correct_chain) == len(targets_correct))

    # Unflatten the results again into a list of lists.
    cutoffs = [0] + np.cumsum(list(map(len, prob_prompts))).tolist()
    ret_probs = [probs[cutoffs[i - 1] : cutoffs[i]] for i in range(1, len(cutoffs))]
    ret_corrects = [
        targets_correct[cutoffs[i - 1] : cutoffs[i]] for i in range(1, len(cutoffs))
    ]
    # Structure the restuls as a dictionary.
    ret = {**{
        f"{key}_probs": ret_probs[i]
        for i, key in enumerate(
            [
                # "rewrite_prompts",
                "attribute_prompts",
                # "neighborhood_prompts",
            ]
        )
    }, **{
        f"{key}_correct": ret_corrects[i]
        for i, key in enumerate(
            [
                # "rewrite_prompts",
                "attribute_prompts",
                # "neighborhood_prompts",
            ]
        )
    }}

    if snips is not None:
        # Gather reference texts
        rel_id = record["requested_rewrite"]["relation_id"]
        gen_stats = test_generation(
            model,
            tok,
            generation_prompts,
            vec,
        )
        ret.update(gen_stats)

    return ret

def compute_pair_quality(model, tok, record, answers) -> typing.Dict:

    # First, unpack rewrite evaluation record.
    subject, target_new, target_true = (
        record["requested_rewrite"][x] for x in ["subject", "target_new", "target_true"]
    )
    rewrite_prompts = [record["requested_rewrite"]["prompt"].format(subject)]
    # neighborhood_prompts = record["neighborhood_prompts"]
    generation_prompts = list(set(record["generation_prompts"]))
    gen_tests = []
    for prompt in generation_prompts:
        for ans in answers:
            gen_tests.append(f"{prompt} {ans}")
    # Form a list of lists of prefixes to test.
    # Flatten all the evaluated prefixes into one list.
    batch_size = 1
    done = 0
    probs = []
    for prompt in gen_tests:
        prob = test_other(
            model,
            tok,
            prompt
        )
        probs.append(prob)

    return gen_tests, probs

def test_other(model, tok, candidate):
    tok.pad_token = tok.eos_token
    inputs = tok(candidate, padding=True, return_tensors="pt").to("cuda")
    outputs = model(**inputs)
    log_probs = torch.log_softmax(outputs.logits, dim=-1)
    token_logits = torch.gather(log_probs[:, :-1], -1, inputs["input_ids"][:,1:].unsqueeze(-1))
    scores = (token_logits.squeeze() * inputs["attention_mask"][:, :-1]).sum(dim=1)
    del inputs
    return scores

def test_batch_prediction(
    model,
    tok,
    prefixes: typing.List[str],
    which_correct: str,
    target_new: str,
    target_true: str,
):
    """
    which_correct: Which target to consider correct. Either 0 for "new" or 1 for "true".
    """
    print("prefixes")
    print(prefixes)
    prefix_lens = [len(n) for n in tok(prefixes)["input_ids"]]
    prompt_tok = tok(
        [
            f"{prefix} {suffix}"
            for prefix in prefixes
            for suffix in [target_new, target_true]
        ],
        padding=True,
        return_tensors="pt",
    ).to("cuda")

    a_tok, b_tok = (tok(f" {n}")["input_ids"] for n in [target_new, target_true])
    choice_a_len, choice_b_len = (len(n) for n in [a_tok, b_tok])

    with torch.no_grad():
        logits = model(**prompt_tok).logits

    del prompt_tok

    probs = np.zeros((logits.size(0),), dtype=np.float32)
    targets_correct = []

    for i in range(logits.size(0)):
        cur_len = choice_a_len if i % 2 == 0 else choice_b_len

        # Compute suffix probabilities
        for j in range(cur_len):
            cur_tok = (a_tok if i % 2 == 0 else b_tok)[j]
            probs[i] += -torch.nn.functional.log_softmax(
                logits[i, prefix_lens[i // 2] + j - 1, :], dim=0
            )[cur_tok].item()
        probs[i] /= cur_len

        # Compute accuracy on new targets
        if (which_correct[i // 2] == 0 and i % 2 == 0) or (
            which_correct[i // 2] == 1 and i % 2 == 1
        ):
            correct = True
            for j in range(cur_len):
                cur_tok = (a_tok if i % 2 == 0 else b_tok)[j]

                if logits[i, prefix_lens[i // 2] + j - 1, :].argmax().item() != cur_tok:
                    correct = False
                    break
            targets_correct.append(correct)

    return [
        {"target_new": probs[i].item(), "target_true": probs[i + 1].item()}
        for i in range(0, len(probs), 2)
    ], targets_correct

def test_generation(model, tok, prefixes: typing.List[str], vec: TfidfVectorizer):
    gen_texts = generate_fast(
        model,
        tok,
        prefixes,
        n_gen_per_prompt=1,
        max_out_len=100,
    )

    ngram_entropy = n_gram_entropy(gen_texts)

    ret = {
        "ngram_entropy": ngram_entropy,
        "text": gen_texts,
    }

    return ret

def n_gram_entropy(gen_texts, agg="arith"):
    assert agg in ["arith", "geom"]

    return (scipy.stats.mstats.gmean if agg == "geom" else np.mean)(
        [compute_n_gram_entropy(txt) for txt in gen_texts]
    ).item()

def compute_n_gram_entropy(sentence, ns=None, weights=None, agg="arith"):
    if ns is None:
        ns = [2, 3]
    if weights is None:
        weights = [2 / 3, 4 / 3]
    assert agg in ["arith", "geom"]

    entropy_list = []
    for n in ns:
        fdist = compute_freq(sentence, n)
        freqs = np.array([freq for _, freq in fdist.items()])
        freqs = freqs / freqs.sum()

        entropy_list.append(np.sum(-freqs * np.log(freqs) / np.log(2)))

    entropy_list = np.array(entropy_list) * np.array(weights)

    return (scipy.stats.mstats.gmean if agg == "geom" else np.mean)(entropy_list)

def compute_freq(sentence, n=2):
    tokens = nltk.word_tokenize(sentence)
    ngrams = nltk.ngrams(tokens, n)
    return nltk.FreqDist(ngrams)

def tfidf_similarity(text_a, text_b, vec):
    encs = vec.transform([text_a, text_b]).A
    norm = np.linalg.norm
    return (np.dot(encs[0], encs[1]) / norm(encs[0]) / norm(encs[1])).item()
