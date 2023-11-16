import json
import numpy as np
from itertools import *
import pandas as pd
import copy
import os
import random

def gen_samples(n = 40):
	texts = [["props", "method", "target_true", "target_new", "subj", "text"]]
	for p in [("P101_P21"), ("P21_P101"), ("P27_P21"), 
				   ("P27_P101"), ("P27_P19"), ("P101_P27"), 
				   ("P19_P21"), ("P19_P101"), "P101", "P103"]:
		p_file = f"../data/seesaw_cf_{p}.json"
		pretexts = []
		fttexts = []
		mendtexts = []
		memittexts = []

		with open(p_file) as o:
			the_question = json.load(o)
		case_ids = [question["case_id"] for question in the_question]
		for question in the_question:
			case_id = question["case_id"]
			tnew = question["requested_rewrite"]["target_new"]["str"]
			ttrue = question["requested_rewrite"]["target_true"]["str"]
			subj = question["requested_rewrite"]["subject"]
			with open(f"../results/OG/900_edits-case_{case_id}.json") as result:
				pres = json.load(result)
			pretext = pres["pre"]["text"]
			free = pretext[int(len(pretext) / 2) if p not in ["P101", "P103"] else 0:]
			pretexts.extend(list(zip([p] * len(free), ["Pre-Edit"] * len(free), [ttrue] * len(free), [tnew] * len(free), [subj] * len(free), free)))
			for method, l in [("FT", fttexts), ("MEND", mendtexts), ("MEMIT", memittexts)]:
				with open(f"../results/{method}/900_edits-case_{case_id}.json") as result:
					res = json.load(result)
					posttext = res["post"]["text"]
					free = posttext[int(len(posttext) / 2) if p not in ["P101", "P103"] else 0:]
					l.extend(list(zip([p] * len(free), [method] * len(free), [ttrue] * len(free), [tnew] * len(free), [subj] * len(free), free)))
		all_texts = random.sample(list(zip(pretexts, fttexts, mendtexts, memittexts)), n)
		for text in all_texts:
			texts.append(text[0])
			texts.append(text[1])
			texts.append(text[2])
			texts.append(text[3])
		df = pd.DataFrame(texts)
		df.to_csv("to_annotate.csv")

gen_samples(40)




