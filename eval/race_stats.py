import json
import numpy as np
from scipy.special import kl_div
from itertools import *
from collections import Counter
import pandas as pd
import os

wiki_prefix = "http://www.wikidata.org/entity/"

def gen_unique(p):
	p_file = f"../data/seesaw_cf_{p}.json"
	all_metrics = []
	overall_metrics = {}
	amn, awn, amt, awt, amd, awd = np.array([]), np.array([]), np.array([]), np.array([]), np.array([]), np.array([])
	amnp, awnp, amtp, awtp, amdp, awdp = np.array([]), np.array([]), np.array([]), np.array([]), np.array([]), np.array([])
	with open(p_file) as o:
		the_question = json.load(o)
	unique_subjects = {}
	for question in the_question:
		case_id = question["case_id"]
		entities = question["attribute_aux_info"]
		q = question["requested_rewrite"]["target_new"]["id"]
		if p.split("_")[0] != "P21":
			if p in ["P101", "P103"]:
				wiki_q_0 = f"/Users/khalevy/Downloads/CF_Ingredients/data/00_{p}_{q}.json"
				wiki_q_1 = f"/Users/khalevy/Downloads/CF_Ingredients/data/01_{p}_{q}.json"
			else:
				p1 = p.split("_")[0]
				wiki_q_0 = f"../data/Q6581072_{p1}_{q}_expanded.json"
				wiki_q_1 = f"../data/Q6581097_{p1}_{q}_expanded.json"
			with open(wiki_q_0) as o1:
				info_0 = json.load(o1)
			with open(wiki_q_1) as o1:
				info_1 = json.load(o1)
			wiki = {**info_0, **info_1}
		else:
			wiki = {}
			men = "../data/P172/men"
			women = "../data/P172/women"
			for f in os.listdir(men):
				with open(os.path.join(men, f)) as o:
					wiki = {**wiki, **json.load(o)}
			for f in os.listdir(women):
				with open(os.path.join(women, f)) as o:
					wiki = {**wiki, **json.load(o)}
		unique_subjects.update(wiki)
	print(len(list(unique_subjects.keys())))
	def listize(props):
		if type(props) == list:
			return props
		else:
			return [props]
	races = list(chain(*[listize(unique_subjects[f"{subj}"]["properties"]["P172"]) for subj in unique_subjects if "P172" in unique_subjects[f"{subj}"]["properties"].keys()]))
	ctr = Counter(races)
	with open(f"../results/race_{p}_unique.json", "w") as o:
		json.dump({k: v for k, v in sorted(dict(ctr).items(), key = lambda x: x[1], reverse = True)}, o)

props = ["P101", "P103", "P101_P21", "P21_P101", "P27_P21", "P27_P101",
		 "P101_P27", "P19_P21", "P19_P101", "P27_P19"]

for p in props:
	if not os.path.exists(f"../results/race_{p}_unique.json"):
		gen_unique(p)
	with open(f"../results/race_{p}_unique.json") as o:
		data = json.load(o)
		df = pd.DataFrame(columns = ["Code", "Frequency"],
						  data = np.array([list(data.keys()), list(data.values())]).transpose())
		df.to_csv(f"../results/race_{p}_unique.csv")



