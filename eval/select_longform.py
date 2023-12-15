import json
import numpy as np
from itertools import *
import pandas as pd
import copy
import os
import random

def gen_samples(n = 10):
	texts = [["props", "method", "target_true", "target_new", "subj", "pre_text", "post_text"]]
	all_all = [["props", "method", "target_true", "target_new", "subj", "pre_text", "post_text"]]
	for p in [("P101_P21"), 
			  ("P21_P101"), 
			  ("P27_P21"), 
			  ("P27_P101"), 
			  ("P27_P19"), 
			  ("P101_P27"), 
			  ("P19_P21"), 
			  ("P19_P101"), 
			  "P101", 
			  "P103"
			  ]:
		p_file = f"../data/seesaw_cf_{p}.json"
		pretexts = []
		fttexts = []
		memittexts = []

		with open(p_file) as o:
			the_question = json.load(o)
		case_ids = [question["case_id"] for question in the_question]
		for question in the_question:
			case_id = question["case_id"]
			tnew = question["requested_rewrite"]["target_new"]["str"]
			ttrue = question["requested_rewrite"]["target_true"]["str"]
			subj = question["requested_rewrite"]["subject"]
			for method, l in [("FT", fttexts), 
							  ("MEMIT", memittexts)]:
				with open(f"../results/{method}/900_edits-case_{case_id}.json") as result:
					with open(f"../results/OG/900_edits-case_{case_id}.json") as presult:
						pres = json.load(presult)
						res = json.load(result)
						posttext = res["post"]["text"]
						pretext = pres["pre"]["text"]
						free = posttext[int(len(posttext) / 2) if p not in ["P101", "P103"] else 0:]
						pfree = pretext[int(len(pretext) / 2) if p not in ["P101", "P103"] else 0:]
						for i in range(len(free)):
							l.append([p, method, ttrue, tnew, subj, pfree[i], free[i]])
		all_texts = random.sample(list(zip(memittexts)), n)
		all_all_texts = list(zip(fttexts, memittexts))
		for text in all_texts:
			texts.append(text[0])
			# texts.append(text[1])
		for text in all_all_texts:
			all_all.append(text[0])
			all_all.append(text[1])
	df = pd.DataFrame(texts)
	df.to_csv("to_annotate.csv", sep = "|", quotechar = '"')
	df = pd.DataFrame(all_all)
	print(df.shape)
	df.to_csv("to_scale.csv", sep = "|", quotechar = '"')

gen_samples(100)




