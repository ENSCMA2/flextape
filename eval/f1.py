import pandas as pd
import krippendorff
import sklearn.metrics
import statsmodels.stats.inter_rater
import numpy
import random

def compute_agreement(annotations, map_dict, acc = False):
    row_metrics = {}
    answers = {}
    true = annotations[0]
    pred = annotations[1]
    row_metrics["F1"] = sklearn.metrics.f1_score(true, pred, average = 'macro')
    if acc:
        true1 = annotations[0]
        true2 = annotations[1]
        true3 = annotations[2]
        pred = annotations[3]
        correctnesses = [pred[i] == true1[i] or pred[i] == true2[i] or pred[i] == true3[i] for i in range(len(pred))]
        row_metrics["accuracy"] = sum(correctnesses) / len(correctnesses)
    return pd.Series(row_metrics)

def get_annotations(key):
    if key == "Edit reflected?":
        na_val = 0
    else:
        na_val = 1.5
    karina = pd.read_csv("karina.csv").fillna(na_val)[key].tolist()[:300]
    brother = pd.read_csv("brother.csv").fillna(na_val)[key].tolist()[:300]
    dad = pd.read_csv("dad.csv").fillna(na_val)[key].tolist()[:300]
    chat = (numpy.array(pd.read_csv("chat_small.csv")[key].tolist()) / 2 + 1.5).tolist() if key != "Edit reflected?" else pd.read_csv("chat_small.csv")[key].tolist()
    agg = pd.read_csv("karina_brother.csv").fillna(na_val)[key].tolist()[:300]
    agg_cons = pd.read_csv("karina_brother_cons.csv").fillna(na_val)[key].tolist()[:300]
    agg3 = pd.read_csv("3way.csv").fillna(na_val)[key].tolist()[:300]
    agg3_cons = pd.read_csv("3way_cons.csv").fillna(na_val)[key].tolist()[:300]
    rand = [random.choice([1.5, 1, 2]) if key != "Edit reflected?" else random.choice([1, 0]) for i in range(len(dad))]
    return [agg3_cons,
            rand,
            ]

# this code is used for classification! each class ("label") is associated with a number
flaws = ["Anglo-centrism", "Sexism", "Religious Injection", "Xenophobia", "Classism", "Racism",  "Injection of Conservatism", "Edit reflected?"]
for flaw in flaws:
    print(flaw)
    labels = set([1.5, 1, 2]) if flaw != "Edit reflected?" else set([0, 1])
    map_dict = {lab:i for i, lab in enumerate(labels)}
    print("all labels:", map_dict)
    annotations = get_annotations(flaw)
    # here "annotations" is just a list of lists of labels, each sublist being associated with one annotator
    mapped_annotations = [[map_dict[float(label)] for label in sublist] for sublist in annotations]
    map_dict = {lab:i for i, lab in enumerate(labels)}

    metrics_dict = compute_agreement(mapped_annotations, map_dict)
    print(metrics_dict)

