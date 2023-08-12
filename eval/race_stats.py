import json
import numpy as np
from scipy.special import kl_div
from itertools import *
from collections import Counter
import pandas as pd

wiki_prefix = "http://www.wikidata.org/entity/"

def gen_metrics(p, result_dir, n, method):
	p_file = f"../data/seesaw_cf_{p}_False_100.json"
	all_metrics = []
	overall_metrics = {}
	amn, awn, amt, awt, amd, awd = np.array([]), np.array([]), np.array([]), np.array([]), np.array([]), np.array([])
	amnp, awnp, amtp, awtp, amdp, awdp = np.array([]), np.array([]), np.array([]), np.array([]), np.array([]), np.array([])
	with open(p_file) as o:
		the_question = json.load(o)
	race = []
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
		def match(prop, hope):
			if type(prop) == list:
				return hope in prop
			if type(prop) == str:
				return hope == prop
			return False
		races = list(chain(*[wiki[f"{wiki_prefix}{subj}"]["properties"]["P172"] for subj in entities if "P172" in wiki[f"{wiki_prefix}{subj}"]["properties"].keys()]))
		afro_russians = [wiki[f"{wiki_prefix}{subj}"]["name"] for subj in entities if "P172" in wiki[f"{wiki_prefix}{subj}"]["properties"].keys() and "Q1060050" in wiki[f"{wiki_prefix}{subj}"]["properties"]["P172"]]
		if len(afro_russians) > 0:
			print(afro_russians)
		race.extend(races)
	ctr = Counter(race)
	with open(f"../results/race_{method}_{p}.txt", "w") as o:
		json.dump({k: v for k, v in sorted(dict(ctr).items(), key = lambda x: x[1], reverse = True)}, o)

def gen_unique(p, result_dir, method):
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
	print(len(list(unique_subjects.keys())))
	def listize(props):
		if type(props) == list:
			return props
		else:
			return [props]
	races = list(chain(*[listize(unique_subjects[f"{subj}"]["properties"]["P172"]) for subj in unique_subjects if "P172" in unique_subjects[f"{subj}"]["properties"].keys()]))
	ctr = Counter(races)
	with open(f"../results/race_{method}_{p}_unique.json", "w") as o:
		json.dump({k: v for k, v in sorted(dict(ctr).items(), key = lambda x: x[1], reverse = True)}, o)

# gen_unique("P101", "../results/FT/p101/", "FT")
# gen_unique("P103", "../results/FT/p103/", "FT")

for p in ["P101", "P103"]:
	with open(f"../results/race_FT_{p}_unique.json") as o:
		data = json.load(o)
		df = pd.DataFrame(columns = ["Code", "Frequency"],
						  data = np.array([list(data.keys()), list(data.values())]).transpose())
		df.to_csv(f"../results/race_{p}_unique.csv")



