import pandas as pd
import json

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

for string in ("", "scaff_"):
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

