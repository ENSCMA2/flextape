import pandas as pd
import krippendorff
import sklearn.metrics
import statsmodels.stats.inter_rater
import numpy
import random

def compute_agreement(annotations, map_dict):
    row_metrics = {}
    answers = {}
    x = numpy.empty((len(annotations[0]), len(annotations)), dtype=numpy.int32)
    m = numpy.zeros((len(annotations[0]), len(map_dict)), dtype=numpy.int32)
    for i, annot_i in enumerate(annotations):
        answers[i] = annot_i
        for j, answer in enumerate(answers[i]):
            x[j, i] = answer
            m[j, answer] += 1
    
    # Krippendorff alpha
    ka = krippendorff.alpha(reliability_data=x.T)
    row_metrics['Krippendorff alpha'] = round(ka, 2)

    # Fleiss kappa
    fk = statsmodels.stats.inter_rater.fleiss_kappa(m)
    row_metrics['Fleiss kappa'] = round(fk, 2)

    # Cohen kappa (pairwise, so averaged)
    kappas = []
    for i in range(len(annotations)):
        for jmi in range(len(annotations[i+1:])):
            j = i + 1 + jmi
            kappa = sklearn.metrics.cohen_kappa_score(x[:, i], x[:, j])
            kappas.append(kappa)
    avg_kappa = numpy.mean(kappas)
    row_metrics['Cohen kappa'] = round(avg_kappa, 2)
    
    # Percent of samples where all annotators agree
    pct_ag = numpy.equal(x[:, [0]], x[:, 1:]).all(axis=1).sum() * 100 / len(annotations[0])
    row_metrics['Pct agreement'] = round(pct_ag, 2)
    
    # Sorted individual annotators scores / cohen kappa
    # used to check if one annotator is completely lost and doesn't agree with anyone
    annotators_scores = {}
    for i in range(len(annotations)):
        annotators_scores[i] = {'cohen kappa':[], 'pct agreement': []}
        for j in range(len(annotations)):
            if i!=j:
                annotators_scores[i]['cohen kappa'].append(sklearn.metrics.cohen_kappa_score(x[:, i], x[:, j]))
                annotators_scores[i]['pct agreement'].append((x[:, i] == x[:, j]).sum())
    
    scores = [(round(numpy.mean(annotators_scores[i]['cohen kappa']), 2), numpy.mean(annotators_scores[i]['pct agreement'])) for i in annotators_scores]
    #scores = [round(numpy.mean(annotators_scores[i]['cohen kappa']), 2) for i in annotators_scores]
    scores = sorted(scores)
    row_metrics['Sorted scores'] = scores

    
    return pd.Series(row_metrics)

def get_annotations(key):
    if key == "Edit reflected?":
        na_val = 0
    else:
        na_val = 1.5
    a1 = pd.read_csv("a1.csv").fillna(na_val)[key].tolist()[:300]
    a2 = pd.read_csv("a2.csv").fillna(na_val)[key].tolist()[:300]
    a3 = pd.read_csv("a3.csv").fillna(na_val)[key].tolist()[:300]
    return [a1, 
            a2,
            a3
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

