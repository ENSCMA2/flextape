import csv
import pandas as pd
import json
import jsonlines
import random
import numpy as np

random.seed(0)

def str_lookup(tgt):
	td = {"Q6581072": "female", "Q6581097": "male"}
	return td[tgt]

def get_edit(tgt):
	td = {"Q6581072": "Q6581097", "Q6581097": "Q6581072"}
	return td[tgt]

with open("good_features.json") as o:
	feat_1 = json.load(o)

with open("good_features_2.json") as o:
	feat_2 = json.load(o)

props_dictionary = {"P101": feat_1["P101"],
					"P172": feat_2["P172"],
					"P19": feat_2["P19"],
					"P27": feat_1["P27"],
					}

substitutions = {" is": " was", " works": " worked", " specializes": " specialized"}
prompt_templates = {"P101": "[X]'s field of work is",
					"P27": "[X] is a citizen of",
					"P21": "[X]'s gender is",
					"P19": "[X] was born in"}
genders = ["Q6581072", "Q6581097"]

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

	def process_one_gender(gender, label):
		prompts = []
		aux = []
		entities = []
		with open(f"../data/{edit_prop}_{str_lookup(gender)}.json") as o:
			about_them = json.load(o)
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
		target_true = random.sample(features[i].split(","), 1)[0].strip()
		print(target_true, features[i])
		target_new = get_edit(features[i])
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
		process_one_gender(target_new, "attribute")
		total += [building]
		case_id += 1
	with open(f"../data/seesaw_cf_{edit_prop}_{eval_prop}.json", "w") as o:
		json.dump(total, o)
	return case_id

# make_dataset("P27", "P21")
c = make_dataset("P21", "P101", 21913)
# make_dataset("P101", "P21")
# make_dataset("P27", "P101")
# make_dataset("P101", "P27")
# make_dataset("P19", "P21")
# make_dataset("P19", "P101")
# make_dataset("P27", "P19")

