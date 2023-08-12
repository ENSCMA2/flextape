import matplotlib.pyplot as plt
import pandas as pd
import json
import numpy as np

flaws = ["mis-attribution of age or time period",
"mis-attribution of occupation",
"misgendering",
"repetition",
"evading the question",
"religious extremism",
"US-centrism",
]

def clean(l):
	cleaned = []
	for i in range(len(l)):
		if type(l[i]) != str:
			cleaned.append([])
		else: 
			unique_preds = set([item.strip() for item in l[i].split(",")])
			cleaned.append(list(unique_preds))
	return cleaned

all_english = pd.read_csv("../data/gold_all_english.csv")["pre_or_post"].tolist()
p101 = pd.read_csv("../data/gold_p101.csv")["pre_or_post"].tolist()
p103 = pd.read_csv("../data/gold_p103.csv")["pre_or_post"].tolist()
conc = all_english + p101 + p103
pre_all_english = [i for i in range(len(all_english)) if all_english[i] == "pre"]
post_all_english = [i for i in range(len(all_english)) if all_english[i] == "post"]
pre_p101 = [i for i in range(len(p101)) if p101[i] == "pre"]
post_p101 = [i for i in range(len(p101)) if p101[i] == "post"]
pre_p103 = [i for i in range(len(p103)) if p103[i] == "pre"]
post_p103 = [i for i in range(len(p103)) if p103[i] == "post"]

with open(f"all_english_{string}1.json") as o:
	# silver_all_english = clean([",".join(s["answers"]) for s in json.load(o)])
	gold_all_english = clean(pd.read_csv("../data/gold_all_english.csv")["flaws"].tolist())
	all_english_pre = [gold_all_english[i] for i in pre_all_english]
	all_english_post = [gold_all_english[i] for i in post_all_english]

with open(f"annotations_P101_{string}1.json") as o:
	# silver_p101 = clean([",".join(s["answers"]) for s in json.load(o)])
	gold_p101 = clean(pd.read_csv("../data/gold_p101.csv")["flaws"].tolist())
	p101_pre = [gold_p101[i] for i in pre_p101]
	p101_post = [gold_p101[i] for i in post_p101]

with open(f"annotations_P103_{string}1.json") as o:
	# silver_p103 = clean([",".join(s["answers"]) for s in json.load(o)[100:]])
	gold_p103 = clean(pd.read_csv("../data/gold_p103.csv")["flaws"].tolist())
	p103_pre = [gold_p103[i] for i in pre_p103]
	p103_post = [gold_p103[i] for i in post_p103]

for name, pre, post in (("all_english", all_english_pre, all_english_post),
						("p101", p101_pre, p101_post),
						("p103", p103_pre, p103_post),
						("all", all_english_pre + p101_pre + p103_pre, all_english_post + p101_post + p103_post)):

	data = {"pre": [], "post": []}
	for flaw in flaws:
		data["pre"].append(sum([flaw in f for f in pre]) / len(pre))
		data["post"].append(sum([flaw in f for f in post]) / len(post))

	x = np.arange(len(flaws))  # the label locations
	width = 0.3  # the width of the bars
	multiplier = 0

	fig, ax = plt.subplots(figsize=(12, 12))

	for attribute, measurement in data.items():
	    offset = width * multiplier
	    rects = ax.bar(x + offset, measurement, width, label=attribute)
	    ax.bar_label(rects, padding=10)
	    multiplier += 1

	# Add some text for labels, title and custom x-axis tick labels, etc.
	ax.set_ylabel('Proportion')
	ax.set_title(f'Prevalence of Flaws in Annotated Texts: {name}')
	ax.set_xticks(x + width, flaws, rotation = 20)
	ax.legend(loc='upper left')

	plt.savefig(f"annotated_viz_{string}{name}gold.png")

