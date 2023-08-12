import pandas as pd
import json
import numpy as np
from sklearn.metrics import mean_squared_error as mse

flaws = flaws = ["mis-attribution of age or time period",
"mis-attribution of occupation",
"misgendering",
"repetition",
"evading the question",
"religious extremism",
"US-centrism",
]

def get_scores(l1, l2):
	assert(len(l1) == len(l2))
	score_1 = 0
	score_2 = 0
	score_1_denominator = 0
	for i in range(len(l1)):
		if type(l1[i]) != str:
			unique_labels = set()
		else:
			unique_labels = set([item.strip() for item in l1[i].split(",")])
			score_1_denominator += len(unique_labels)
		unique_preds = set([item.strip() for item in l2[i].split(",")])
		for label in unique_labels:
			if label in unique_preds:
				score_1 += 1
		if len(unique_labels) == len(unique_preds) and len(unique_labels.intersection(unique_preds)) == len(unique_labels):
			score_2 += 1
	return score_1, score_2, score_1_denominator

def prob(ans):
	score = 0
	for a in ans:
		if "Yes" in a or "yes" in a:
			score += 1
	return score / len(ans)

def mse_subroutine(flaw, sheet, preds):
	pre = sheet.index[sheet["pre_or_post"] == "pre"]
	post = sheet.index[sheet["pre_or_post"] == "post"]
	data_pre = sheet.loc[pre]["flaws"].fillna("").tolist()
	data_post = sheet.loc[post]["flaws"].fillna("").tolist()
	pre = np.array(pre.tolist())
	post = np.array(post.tolist())
	data = sheet["flaws"].fillna("").tolist()
	gold_labels = np.array([int(flaw in s) for s in data])
	gold_pre = gold_labels[pre]
	gold_post = gold_labels[post]
	preds_pre = preds[pre]
	preds_post = preds[post]
	mse_score = mse(gold_labels, preds)
	mse_pre = mse(gold_pre, preds_pre)
	mse_post = mse(gold_post, preds_post)
	return mse_score, mse_pre, mse_post

def mse_routine(flaw, name):
	with open(f"{name}_binary.json") as o:
		preds = np.array([prob(entry["answers"]) for entry in json.load(o)[flaw]])
	sheet = pd.read_csv(f"../data/gold_{name}.csv")
	return mse_subroutine(flaw, sheet, preds)
	
for flaw in flaws:
	ae, ae_pre, ae_post = mse_routine(flaw, "all_english")
	p101, p101_pre, p101_post = mse_routine(flaw, "p101")
	p103, p103_pre, p103_post = mse_routine(flaw, "p103")
	with open(f"all_english_binary.json") as o:
		preds = [prob(entry["answers"]) for entry in json.load(o)[flaw]]
	with open(f"p101_binary.json") as o:
		preds += [prob(entry["answers"]) for entry in json.load(o)[flaw]]
	with open(f"p103_binary.json") as o:
		preds += [prob(entry["answers"]) for entry in json.load(o)[flaw]]
	preds = np.array(preds)
	data = pd.concat([pd.read_csv("../data/gold_all_english.csv"), pd.read_csv("../data/gold_p101.csv"), pd.read_csv("../data/gold_p103.csv")])
	overall, overall_pre, overall_post = mse_subroutine(flaw, data, preds)
	print("all")
	print(f"{flaw}", f"All English: MSE is {ae}")
	print(f"{flaw}", f"P101: MSE is {p101}")
	print(f"{flaw}", f"P103: MSE is {p103}")
	print(f"{flaw}", f"Overall: MSE is {overall}")
	print("pre")
	print(f"{flaw}", f"All English: MSE is {ae_pre}")
	print(f"{flaw}", f"P101: MSE is {p101_pre}")
	print(f"{flaw}", f"P103: MSE is {p103_pre}")
	print(f"{flaw}", f"Overall: MSE is {overall_pre}")
	print("post")
	print(f"{flaw}", f"All English: MSE is {ae_post}")
	print(f"{flaw}", f"P101: MSE is {p101_post}")
	print(f"{flaw}", f"P103: MSE is {p103_post}")
	print(f"{flaw}", f"Overall: MSE is {overall_post}")
	



'''
gold_all_english = pd.read_csv("../data/gold_all_english.csv")["flaws"].tolist()
with open(f"all_english_{string}1.json") as o:
	silver_all_english = [",".join(s["answers"]) for s in json.load(o)]
scores_all_english_1, scores_all_english_2, d = get_scores(gold_all_english, silver_all_english)
print(f"Americans: Score 1 is {scores_all_english_1}, \
		Score 2 is {scores_all_english_2}, of {len(gold_all_english)}, {d}")

gold_p101 = pd.read_csv("../data/gold_p101.csv")["flaws"].tolist()
with open(f"annotations_P101_{string}1.json") as o:
	silver_p101 = [",".join(s["answers"]) for s in json.load(o)]
scores_p101_1, scores_p101_2, d = get_scores(gold_p101, silver_p101)
print(f"P101: Score 1 is {scores_p101_1}, \
		Score 2 is {scores_p101_2}, of {len(gold_p101)}, {d}")

gold_p103 = pd.read_csv("../data/gold_p103.csv")["flaws"].tolist()
with open(f"annotations_P103_{string}1.json") as o:
	silver_p103 = [",".join(s["answers"]) for s in json.load(o)[100:]]
scores_p103_1, scores_p103_2, d = get_scores(gold_p103, silver_p103)
print(f"P103: Score 1 is {scores_p103_1}, \
		Score 2 is {scores_p103_2}, of {len(gold_p103)}, {d}")

gold_all = gold_all_english + gold_p101 + gold_p103
silver_all = silver_all_english + silver_p101 + silver_p103
scores_all_1, scores_all_2, d = get_scores(gold_all, silver_all)
print(f"Total: Score 1 is {scores_all_1}, \
		Score 2 is {scores_all_2}, of {len(gold_all)}, {d}")
'''
