import json
import numpy as np
from itertools import *
import pandas as pd
import copy
import os
import sys
import wptools
import requests

model = sys.argv[1]
method = sys.argv[2]

def gen_metrics(p, result_dir, n, presult_dir, method, patch = False,):
	print(p)
	p_file = f"../../data/seesaw_cf_{p}_eff.json"
	with open(p_file) as o:
		the_question = json.load(o)
	total = 0
	diff = 0
	realdiff = 0
	for j, question in enumerate(the_question):
		case_id = question["case_id"]
		q = question["requested_rewrite"]["target_new"]["id"]
		with open(f"{result_dir}{n}_edits-case_{case_id}.json") as o:
			res = json.load(o)["post"]["attribute_prompts_probs"][0]
			total += res["target_new"] < res["target_true"]
		with open(f"{presult_dir}{n}_edits-case_{case_id}.json") as o:
			pres = json.load(o)["pre"]["attribute_prompts_probs"][0]
			diff += pres["target_new"] < pres["target_true"]
			realdiff += res["target_new"] - pres["target_new"]
	print("efficacy:", total / len(the_question), "baseline:", diff / len(the_question), "actual diff:", realdiff)

model = sys.argv[1]
for p in ["P21_P101",
		  "P27_P101", "P19_P101",
		  "P101", "P103", 
		  ]:
	gen_metrics(p, f"../../effs/{model}/{method}/", 900, f"../../effs/{model}/NONE/", method)
