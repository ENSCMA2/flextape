import json
import pandas as pd
import random
import numpy as np
from scipy.stats import ttest_1samp
from scipy.stats import ttest_ind
import os
import requests
import wptools
root = "../special/llama/"

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

with open("../data/P101_subject_info.json") as o:
	wiki = json.load(o)
with open("../data/P103_subject_info.json") as o:
	wiki = {**wiki, **json.load(o)}
# for f in os.listdir("../data/wiki"):
# 	if f != ".DS_Store" and "person" not in f:
# 		with open(f"../data/wiki/{f}") as o:
# 			try:
# 				d = json.load(o)
# 			except:
# 				continue
# 		wiki = {**wiki, **d}
new_wiki = {}
for entry in wiki.keys():
	if len(wiki[entry]) > 0:
		new_wiki = {**wiki, **{wiki[entry]["name"]: wiki[entry]["properties"]}}
print(len(new_wiki))

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
	print(p1, p2)
	data_file = f"../data/seesaw_cf_{p1}_{p2}.json"
	k = "post" if method != "NONE" else "pre"
	with open(data_file) as o:
		data = json.load(o)
	correctness = {}
	acc = 0
	# sampacc = 0
	# sampcorrectness = {}
	for question in data:
		case_id = question["case_id"]
		subj = question["requested_rewrite"]["subject"]
		gt = None
		if subj in new_wiki.keys() and p2 in new_wiki[subj].keys():
			print("exists in keys")
			gt = new_wiki[subj][p2]
		else:
			if os.path.exists(f"../data/wiki/person_{subj}.json"):
				print("person file exists")
				with open(f"../data/wiki/person_{subj}.json") as o:
					person = json.load(o)
					if p2 in person["properties"].keys():
						gt = person["properties"][p2]
					else:
						continue
			else:
				r = requests.get(f"https://www.wikidata.org/w/api.php?action=wbsearchentities&language=en&search={subj}&format=json")
				j = json.loads(r.text)
				if len(j["search"]) > 0:
					ident = j["search"][0]["id"]
					page = wptools.page(wikibase = ident, silent = True)
					wikidata = page.get_wikidata(show = False).data
					person = {"name": wikidata["label"], "properties": wikidata["claims"]}
					with open(f"../data/wiki/person_{subj}.json", "w") as o:
						json.dump(person, o)
					if p2 in wikidata.keys():
						gt = wikidata["claims"][p2]
			if type(gt) == str:
				gt = [gt]
			elif gt is not None:
				g = []
				for ans in gt:
					try:
						g.append(str_lookup(ans))
					except:
						continue
				gt = g
		result_file = f"{root}{method}/901_edits-case_{case_id}.json"
		if os.path.exists(result_file):
			with open(result_file) as o:
				result = json.load(o)
			r_tup = [(result[k][1][i], result[k][0][i]) for i in range(int(len(result[k][0]) / 2))]
			sorted_tup = sorted(r_tup, reverse = True)
			answer = sorted_tup[0][1]
			if gt is not None and len(gt) > 0:
				right_answers = []
				for i in range(len(r_tup)):
					for ans in gt:
						if ans in r_tup[i][1]:
							right_answers.append(i)
							continue

				correct = False
				for ans in gt:
					if ans in answer:
						correct = True
						break
				correctness[subj] = correct
				acc += correct
	acc = acc / len(list(correctness.keys()))
	# sampacc = sampacc / len(list(sampcorrectness.keys()))
	with open(f"{root}{method}_{p1}_{p2}.json", "w") as o:
		json.dump({"by_case": correctness, "overall_acc": acc, "num_cases": len(list(correctness.keys())), "stdev": np.std(list(correctness.values()))}, o)
	# with open(f"{root}{method}_{p1}_{p2}_samp9.json", "w") as o:
	# 	json.dump({"by_case": sampcorrectness, "overall_acc": sampacc}, o)


for method in ["MEMIT", 
			   "NONE"
			   ]:
	for p1, p2 in [("P101", "P21"), 
				   # ("P21", "P101"), ("P27", "P21"), 
				   # ("P27", "P101"), ("P27", "P19"), ("P101", "P27"), 
				   # ("P19", "P21"), ("P19", "P101")
				   ]:
		gen_metrics(method, p1, p2)


'''
for method in [# "FT", "MEND", 
			   "MEMIT", 
			   ]:
	for p1, p2 in [("P101", "P21"), 
					("P21", "P101"), ("P27", "P21"), 
				   # ("P27", "P101"), ("P27", "P19"), ("P101", "P27"), 
				   ("P19", "P21"), ("P19", "P101")]:
		with open(f"{root}{method}_{p1}_{p2}.json") as o:
			loaded = json.load(o)
			post = list(loaded["by_case"].values())
			post_acc = loaded["overall_acc"]
		with open(f"{root}NONE_{p1}_{p2}.json") as o:
			loaded = json.load(o)
			pre = list(loaded["by_case"].values())
			pre_acc = loaded["overall_acc"]
		print(method, p1, p2, pre_acc, post_acc, ttest_ind(post, pre).pvalue)
'''


