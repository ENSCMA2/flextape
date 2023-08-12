import json
import numpy as np
from scipy.special import kl_div
from itertools import *
from collections import Counter
import pandas as pd

wiki_prefix = "http://www.wikidata.org/entity/"

def gen_unique(p, result_dir):
	p_file = f"../data/seesaw_cf_{p}_False_100.json"
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
		wiki_q_0 = f"/Users/khalevy/Downloads/CF_Ingredients/data/00_{p}_{q}.json"
		wiki_q_1 = f"/Users/khalevy/Downloads/CF_Ingredients/data/01_{p}_{q}.json"
		with open(wiki_q_0) as o1:
			info_0 = json.load(o1)
		with open(wiki_q_1) as o1:
			info_1 = json.load(o1)
		wiki = {**info_0, **info_1}
		unique_subjects.update(wiki)
	props = list(chain(*[list(unique_subjects[f"{subj}"]["properties"].keys()) for subj in unique_subjects]))
	ctr = Counter(props)
	with open(f"../results/props_{p}_unique.json", "w") as o:
		json.dump({k: v for k, v in sorted(dict(ctr).items(), key = lambda x: x[1], reverse = True)}, o)

gen_unique("P101", "../results/FT/p101/")
gen_unique("P103", "../results/FT/p103/")

for p in ["P101", "P103"]:
	with open(f"../results/props_{p}_unique.json") as o:
		data = json.load(o)
		df = pd.DataFrame(columns = ["Code", "Frequency"],
						  data = np.array([list(data.keys()), list(data.values())]).transpose())
		df.to_csv(f"../results/props_{p}_unique.csv")



