import json
import numpy as np
from itertools import *
import pandas as pd
import copy
import os

wiki_prefix = "http://www.wikidata.org/entity/"

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

def gen_metrics(p, result_dir, n, presult_dir, method, patch = False,):
	print(p, method)
	results = {}
	p_file = f"../data/seesaw_cf_{p}.json"

	with open(p_file) as o:
		the_question = json.load(o)
	case_ids = [question["case_id"] for question in the_question]
	for question in the_question:
		case_id = question["case_id"]
		q = question["requested_rewrite"]["target_new"]["id"]
		with open("/Users/khalevy/Downloads/CF_Ingredients/data/P101_subject_info.json") as o:
			wiki = json.load(o)
		with open("/Users/khalevy/Downloads/CF_Ingredients/data/P103_subject_info.json") as o:
			wiki = {**wiki, **json.load(o)}
		new_wiki = {wiki[entry]["name"]: wiki[entry]["properties"] for entry in wiki.keys()}
		subj = question["requested_rewrite"]["subject"]
		try:
			answer = new_wiki[subj][p.split("_")[1]]
			if type(answer) == str:
				answer = [answer]
			answer = [str_lookup(ans) for ans in answer]

			with open(f"{result_dir}{n}_edits-case_{case_id}.json") as result:
				res = json.load(result)
			posttext = res["post"]["text"]
			
			with open(f"{presult_dir}{n}_edits-case_{case_id}.json") as result:
				pres = json.load(result)
			pretext = pres["pre"]["text"]

			def contains_an(answers, text):
				print(answers)
				for ans in answers:
					if ans.lower() in text.lower():
						return True
				return False

			postcontainsguided = sum([contains_an(answer, text) for text in posttext[:5]])
			precontainsguided = sum([contains_an(answer, text) for text in pretext[:5]])
			postcontainsfree = sum([contains_an(answer, text) for text in posttext[5:]])
			precontainsfree = sum([contains_an(answer, text) for text in pretext[5:]])
			results[case_id] = {"post": {"guided": postcontainsguided,
										 "free": postcontainsfree},
								"pre": {"guided": precontainsguided,
										 "free": precontainsfree}}
		except:
			continue
	def avg(prepost, gf):
		return int(np.sum([results[c][prepost][gf] for c in results.keys()]))
    
	if not os.path.isdir(f"../results/{p}"):
		os.mkdir(f"../results/{p}")
	if not os.path.isdir(f"../results/{p}/long"):
		os.mkdir(f"../results/{p}/long")
	with open(f"../results/{p}/long/{method}.json", "w") as o:
		json.dump({"by_case": results, 
				   "overall": {"post": {"guided": avg("post", "guided"), 
				   						"free": avg("post", "free")},
							   "pre": {"guided": avg("pre", "guided"), 
							   		   "free": avg("pre", "free")}}}, o)

gen_metrics("P101_P21", "../results/MEMIT/", 900, "../results/OG/", "MEMIT")
gen_metrics("P21_P101", "../results/MEMIT/", 900, "../results/OG/", "MEMIT")
gen_metrics("P27_P21", "../results/MEMIT/", 900, "../results/OG/", "MEMIT")
gen_metrics("P27_P101", "../results/MEMIT/", 900, "../results/OG/", "MEMIT")
gen_metrics("P101_P27", "../results/MEMIT/", 900, "../results/OG/", "MEMIT")
gen_metrics("P19_P21", "../results/MEMIT/", 900, "../results/OG/", "MEMIT")
gen_metrics("P19_P101", "../results/MEMIT/", 900, "../results/OG/", "MEMIT")
gen_metrics("P27_P19", "../results/MEMIT/", 900, "../results/OG/", "MEMIT")

gen_metrics("P101_P21", "../results/FT/", 900, "../results/OG/", "FT")
gen_metrics("P21_P101", "../results/FT/", 900, "../results/OG/", "FT")
gen_metrics("P27_P21", "../results/FT/", 900, "../results/OG/", "FT")
gen_metrics("P27_P101", "../results/FT/", 900, "../results/OG/", "FT")
gen_metrics("P101_P27", "../results/FT/", 900, "../results/OG/", "FT")
gen_metrics("P19_P21", "../results/FT/", 900, "../results/OG/", "FT")
gen_metrics("P19_P101", "../results/FT/", 900, "../results/OG/", "FT")
gen_metrics("P27_P19", "../results/FT/", 900, "../results/OG/", "FT")

gen_metrics("P101_P21", "../results/MEND/", 900, "../results/OG/", "MEND")
gen_metrics("P21_P101", "../results/MEND/", 900, "../results/OG/", "MEND")
gen_metrics("P27_P21", "../results/MEND/", 900, "../results/OG/", "MEND")
gen_metrics("P27_P101", "../results/MEND/", 900, "../results/OG/", "MEND")
gen_metrics("P101_P27", "../results/MEND/", 900, "../results/OG/", "MEND")
gen_metrics("P19_P21", "../results/MEND/", 900, "../results/OG/", "MEND")
gen_metrics("P19_P101", "../results/MEND/", 900, "../results/OG/", "MEND")
gen_metrics("P27_P19", "../results/MEND/", 900, "../results/OG/", "MEND")



