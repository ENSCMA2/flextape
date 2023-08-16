import pandas as pd
import json
import numpy as np
from sklearn.metrics import mean_squared_error as mse
from sklearn.metrics import accuracy_score

flaws = ["mis-attribution of age or time period",
"mis-attribution of occupation",
"misgendering"]
# "repetition",
# "evading the question",
# "religious extremism",
# "US-centrism",]

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

def answer(ans):
	score = 0
	for a in ans:
		if "Yes" in a or "yes" in a:
			score += 1
	return int(score > 10)

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

def acc_subroutine(flaw, sheet, preds):
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
	acc_score = accuracy_score(gold_labels, preds)
	acc_pre = accuracy_score(gold_pre, preds_pre)
	acc_post = accuracy_score(gold_post, preds_post)
	return acc_score, acc_pre, acc_post

def mse_routine(flaw, name):
	with open(f"{name}_binary.json") as o:
		preds = np.array([prob(entry["answers"]) for entry in json.load(o)[flaw]])
	sheet = pd.read_csv(f"../data/gold_{name}.csv")
	return mse_subroutine(flaw, sheet, preds)

def acc_routine(flaw, name, attribute = None):
	with open(f"{name}_binary_truth.json") as o:
		preds = np.array([answer(entry["answers"]) for entry in json.load(o)[flaw]])
	sheet = pd.read_csv(f"../data/gold_{name}.csv")
	sheet = sheet[sheet[attribute] != ""]
	assert(len(preds) == len(sheet))
	return acc_subroutine(flaw, sheet, preds)
	
for flaw, attribute in zip(flaws, ["birthdate", "occupation", "gender"]):
	ae, ae_pre, ae_post = acc_routine(flaw, "all_english", attribute)
	p101, p101_pre, p101_post = acc_routine(flaw, "p101", attribute)
	p103, p103_pre, p103_post = acc_routine(flaw, "p103", attribute)
	with open(f"all_english_binary_truth.json") as o:
		preds = [answer(entry["answers"]) for entry in json.load(o)[flaw]]
	with open(f"p101_binary_truth.json") as o:
		preds += [answer(entry["answers"]) for entry in json.load(o)[flaw]]
	with open(f"p103_binary_truth.json") as o:
		preds += [answer(entry["answers"]) for entry in json.load(o)[flaw]]
	preds = np.array(preds)
	english_d = pd.read_csv("../data/gold_all_english.csv")
	p101_d = pd.read_csv("../data/gold_p101.csv")
	p103_d = pd.read_csv("../data/gold_p103.csv")
	english_a = english_d[english_d[attribute] != ""]
	p101_a = p101_d[p101_d[attribute] != ""]
	p103_a = p103_d[p103_d[attribute] != ""]
	data = pd.concat([english_a, p101_a, p103_a])
	overall, overall_pre, overall_post = acc_subroutine(flaw, data, preds)
	print("all")
	print(f"{flaw}", f"All English: {ae}")
	print(f"{flaw}", f"P101: {p101}")
	print(f"{flaw}", f"P103: {p103}")
	print(f"{flaw}", f"Overall: {overall}")
	print("pre")
	print(f"{flaw}", f"All English: {ae_pre}")
	print(f"{flaw}", f"P101: {p101_pre}")
	print(f"{flaw}", f"P103: {p103_pre}")
	print(f"{flaw}", f"Overall: {overall_pre}")
	print("post")
	print(f"{flaw}", f"All English: {ae_post}")
	print(f"{flaw}", f"P101: {p101_post}")
	print(f"{flaw}", f"P103: {p103_post}")
	print(f"{flaw}", f"Overall: {overall_post}")