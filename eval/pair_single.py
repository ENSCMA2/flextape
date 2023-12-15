import json
import pandas as pd
import random
import numpy as np
from scipy.stats import ttest_1samp
from scipy.stats import ttest_ind

root = "../special/"

genders = set(["male", "female"])
fow_cands = set(pd.read_csv("../data/fow.csv", names = ["Code", "String", "Category"])["String"].tolist())
city_cands = set(pd.read_csv("../data/city_to_country.csv", names = ["City", "Country", "UCity", "CName"])["UCity"].tolist())
countries_of_citizenship = set(pd.read_csv("../data/P27_cats.csv", names = ["Code", "Country", "Continent"])["Country"].tolist())

CAND_DICT = {
    "P21": genders,
    "P101": fow_cands,
    "P27": countries_of_citizenship,
    "P19": city_cands
}

with open("/Users/khalevy/Downloads/CF_Ingredients/data/P101_subject_info.json") as o:
	wiki = json.load(o)
with open("/Users/khalevy/Downloads/CF_Ingredients/data/P103_subject_info.json") as o:
	wiki = {**wiki, **json.load(o)}
new_wiki = {wiki[entry]["name"]: wiki[entry]["properties"] for entry in wiki.keys()}

fow = pd.read_csv("../data/fow.csv")
city_names = pd.read_csv("../data/city_to_country.csv", names = ["City", "Country", "UCity", "CName"])[["UCity", "CName"]]
city_to_country = pd.read_csv("../data/city_to_country.csv", names = ["City", "Country", "UCity", "CName"])[["City", "Country"]]
country_codes_continents = pd.read_csv("../data/country_codes.csv", names = ["Name", "Code", "Continent"])
c2c = {tem["Code"]: tem["Category"] for i, tem in fow.iterrows()}
country_to_continent = {tem["Name"]: tem["Continent"] for i, tem in country_codes_continents.iterrows()}
city_to_continent = {tem["City"]: country_to_continent[tem["Country"]] for i, tem in city_to_country.iterrows()}
p27_cats = pd.read_csv("../data/P27_cats.csv", names = ["Code", "Country", "Continent"])
p27_strlookup = {tem["Code"]: tem["Country"] for i, tem in p27_cats.iterrows()}
p27_c2c = {tem["Code"]: tem["Continent"] for i, tem in p27_cats.iterrows()}

def str_lookup(tgt):
	td = {"Q6581072": "female", "Q6581097": "male"}
	td = {**td, **{tem["Code"]: tem["String"] for i, tem in fow.iterrows()}}
	td = {**td, **{tem["UCity"]: tem["CName"] for i, tem in city_names.iterrows()}}
	td = {**td, **p27_strlookup}
	return td[tgt]

def gen_metrics(method, p1, p2):
	data_file = f"../data/seesaw_cf_{p1}_{p2}.json"
	with open(data_file) as o:
		data = json.load(o)
	correctness = {}
	acc = 0
	sampacc = 0
	sampcorrectness = {}
	for question in data:
		case_id = question["case_id"]
		subj = question["requested_rewrite"]["subject"]
		result_file = f"{root}{method}/901_edits-case_{case_id}.json"
		with open(result_file) as o:
			result = json.load(o)
		prompt = question["generation_prompts"][0]
		r_tup = [(result["post"][1][i], result["post"][0][i]) for i in range(int(len(result["post"][0]) / 2))]
		sorted_tup = sorted(r_tup, reverse = True)
		answer = sorted_tup[0][1]
		try:
			gt = new_wiki[subj][p2]
			if type(gt) == str:
				gt = [gt]
			else:
				gt = [str_lookup(ans) for ans in gt]
		except Exception as e:
			print(e)
			continue
		right_answers = []
		for i in range(len(r_tup)):
			for ans in gt:
				if ans in r_tup[i][1]:
					right_answers.append(i)
					continue
		sampled = [r_tup[i] for i in right_answers] + random.sample([r_tup[i] for i in range(len(r_tup)) if i not in right_answers], min(9, len(r_tup) - len(right_answers)))
		sorted_sampled_tup = sorted(sampled, reverse = True)
		sampanswer = sorted_tup[0][1]

		correct = False
		for ans in gt:
			if ans in answer:
				correct = True
				break
		correctness[subj] = correct
		acc += correct

		sampcorrect = False
		for ans in gt:
			if ans in sampanswer:
				sampcorrect = True
				break
		sampcorrectness[subj] = sampcorrect
		sampacc += sampcorrect
	acc = acc / len(list(correctness.keys()))
	sampacc = sampacc / len(list(sampcorrectness.keys()))
	with open(f"{root}{method}_{p1}_{p2}.json", "w") as o:
		json.dump({"by_case": correctness, "overall_acc": acc, "num_cases": len(list(correctness.keys())), "stdev": np.std(list(correctness.values()))}, o)
	with open(f"{root}{method}_{p1}_{p2}_samp9.json", "w") as o:
		json.dump({"by_case": sampcorrectness, "overall_acc": sampacc}, o)

'''
for method in ["FT", "MEND", "MEMIT", 
			   #"NONE"
			   ]:
	for p1, p2 in [("P101", "P21"), ("P21", "P101"), ("P27", "P21"), 
				   ("P27", "P101"), ("P27", "P19"), ("P101", "P27"), 
				   ("P19", "P21"), ("P19", "P101")]:
		gen_metrics(method, p1, p2)
'''

for method in ["FT", "MEND", "MEMIT", 
			   ]:
	for p1, p2 in [("P101", "P21"), ("P21", "P101"), ("P27", "P21"), 
				   ("P27", "P101"), ("P27", "P19"), ("P101", "P27"), 
				   ("P19", "P21"), ("P19", "P101")]:
		with open(f"{root}{method}_{p1}_{p2}.json") as o:
			post = list(json.load(o)["by_case"].values())
		with open(f"{root}NONE_{p1}_{p2}.json") as o:
			pre = list(json.load(o)["by_case"].values())
		print(method, p1, p2, ttest_ind(post, pre).pvalue)




