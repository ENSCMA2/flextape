import csv
import pandas as pd
import json
import jsonlines
import random
import numpy as np

random.seed(0)
with open("good_features.json") as o:
	feat_1 = json.load(o)

with open("good_features_2.json") as o:
	feat_2 = json.load(o)
props_dictionary = {"P101": feat_1["P101"],
					"P172": feat_2["P172"],
					"P19": feat_2["P19"],
					"P27": feat_1["P27"],
					}
fow = pd.read_csv("../data/fow.csv")
city_names = pd.read_csv("../data/city_to_country.csv", names = ["City", "Country", "UCity", "CName"])[["UCity", "CName"]]
city_to_country = pd.read_csv("../data/city_to_country.csv", names = ["City", "Country", "UCity", "CName"])[["City", "Country"]]
country_codes_continents = pd.read_csv("../data/country_codes.csv", names = ["Name", "Code", "Continent"])
c2c = {tem["Code"]: tem["Category"] for i, tem in fow.iterrows()}
country_to_continent = {tem["Name"]: tem["Continent"] for i, tem in country_codes_continents.iterrows()}
city_to_continent = {tem["City"]: country_to_continent[tem["Country"]] for i, tem in city_to_country.iterrows()}
substitutions = {" is": " was", " works": " worked", " specializes": " specialized"}
prompt_templates = {"P101": "[X]'s field of work is",
					"P27": "[X] is a citizen of",
					"P21": "[X]'s gender is",
					"P19": "[X] was born in"}
genders = ["Q6581072", "Q6581097"]

def other(f, all_f):
	ind = all_f.index(f)
	other_f = all_f[:ind] + all_f[ind + 1:] if ind < len(all_f) - 1 else all_f[:ind]
	return random.sample(other_f, 1)[0]

def str_lookup(tgt):
	td = {"Q6581072": "female", "Q6581097": "male"}
	td = {**td, **{tem["Code"]: tem["String"] for i, tem in fow.iterrows()}}
	td = {**td, **{tem["UCity"]: tem["CName"] for i, tem in city_names.iterrows()}}
	return td[tgt]




def concat(lst, number):
	o = []
	for i in range(number):
		o += lst
	return o

def is_dead_for_sure_side_character(iD, a):
	try:
		about_them = a[iD]
		return "P570" in about_them["properties"].keys()
	except Exception as e:
		print("failed dead")
		print(e)
	

def make_subs(prompt):
	for key in substitutions:
		prompt = prompt.replace(key, substitutions[key])
	return prompt

def make_dataset(edit_prop, eval_prop, case_id):
	seedlings = pd.read_csv("../dsets/seedling.csv")
	subjects = np.array(seedlings["Name"].tolist())
	features = np.array(seedlings[edit_prop].tolist())
	valid_indices = [i for i in range(len(features)) if features[i] != "N/A"]
	subjects = subjects[valid_indices]
	features = features[valid_indices]

	total = []

	def get_edit(tgt, edit = None):
		possibilities = [i.strip() for i in tgt.split(",")]
		if edit_prop == "P19":
			possibilities = [possibilities[0]]
		try:
			td = {**{"Q6581072": "Q6581097", "Q6581097": "Q6581072"},
				  **{ key : "Q11629" for key in ['Q7754', 'Q12479', 'Q474200', 
				  'Q216861', 'Q333', 'Q41217', 'Q28575007', 'Q184631', 'Q14620', 
				  'Q395', 'Q193544', 'Q149999', 'Q131476', 'Q413', 'Q8078'] 
				  + ['Q413', 'Q41217', 'Q395', 'Q177625', 'Q12725', 'Q3294789', 
				  'Q166509', 'Q200286']}}
			return td[tgt] if len(possibilities) == 1 else td[random.sample(possibilities, 1)[0]]
		except:
			banned = []
			print("possibilities", possibilities)
			cat = c2c if edit_prop == "P101" else city_to_continent
			for pos in possibilities:
				banned.append(cat[pos])
			others = [key for key in cat.keys() if cat[key] not in banned and key in props_dictionary[edit]]
			print(possibilities, others)
			return random.sample(others, 1)[0]

	def process_one_gender(gender, label, nongender = None):
		prompts = []
		aux = []
		entities = []
		if nongender == None:
			with open(f"../data/{edit_prop}_{str_lookup(gender)}.json") as o:
				about_them = json.load(o)
		else:
			with open(f"../data/{gender}_{edit_prop}_{nongender}_expanded.json") as o:
				about_them = json.load(o)
				about_them = {key: about_them[key] for key in random.sample(list(about_them.keys()), min(100, len(list(about_them.keys()))))}
		for key in about_them.keys():
			item = about_them[key]
			name = item["name"]
			prompt = prompt_templates[edit_prop].replace("[X]", name)
			if is_dead_for_sure_side_character(key, about_them):
				prompt = make_subs(prompt)
			prompts.append(prompt)
			aux.append(key)
			entities.append(name)
		building[label + "_prompts"] += prompts
		building[label + "_aux_info"] += aux
		building[label + "_aux_ent"] += entities

	for i in range(len(subjects)):
		building = {}
		building["case_id"] = case_id
		if features[i] != 'nan':
			target_true = random.sample(features[i].split(","), 1)[0].strip() if edit_prop != "P19" else features[i].split(",")[0]
			target_new = get_edit(features[i], None if edit_prop == "P21" else edit_prop)
			building["requested_rewrite"] = {"prompt": prompt_templates[edit_prop].replace("[X]", "{}"), 
											 "relation_id": edit_prop, 
											 "target_new": {"str": str_lookup(target_new), "id": target_new}, 
											 "target_true": {"str": str_lookup(target_true), "id": target_true}, 
											 "subject": subjects[i]}
			building["generation_prompts"] = concat([prompt_templates[eval_prop].replace("[X]", subjects[i])], 5) + concat([f"{subjects[i]} is"], 5)
			building["attribute_prompts"] = []
			building["attribute_aux_info"] = []
			building["attribute_aux_ent"] = []
			target_true = building["requested_rewrite"]["target_true"]["id"]
			target_new = building["requested_rewrite"]["target_new"]["id"]
			if edit_prop == "P21":
				process_one_gender(target_new, "attribute")
			else:
				process_one_gender("Q6581072", "attribute", target_new)
				process_one_gender("Q6581097", "attribute", target_new)
			total += [building]
			case_id += 1
	with open(f"../data/seesaw_cf_{edit_prop}_{eval_prop}.json", "w") as o:
		json.dump(total, o)
	return case_id

# make_dataset("P27", "P21")
c = make_dataset("P21", "P101", 21913)
d = make_dataset("P101", "P21", c)
# make_dataset("P27", "P101")
# make_dataset("P101", "P27")
e = make_dataset("P19", "P21", d)
f = make_dataset("P19", "P101", e)
# make_dataset("P27", "P19")

