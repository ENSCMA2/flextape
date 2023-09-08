import csv
import pandas as pd
import json
import jsonlines
import random

random.seed(0)
case_id = 21913

substitutions = {" is": " was", " works": " worked", " specializes": " specialized"}
prompt_templates = {"P101": "[X]'s field of work is",
					"P27": "[X] is a citizen of",
					"P21": "[X]'s gender is",
					"P19": "[X] was born in"}
genders = ["Q6581072", "Q6581097"]

pool = {"P101": ,
		"P27": ,
		"P21": {"broad_to_narrow": {"Q6581072": set("Q6581072"),
									"Q6581097": set("Q6581097")},
				"narrow_to_broad": {"Q6581072": "Q6581072",
									"Q6581097": "Q6581097"}},
		"P19": }

def concat(lst, number):
	o = []
	for i in range(number):
		o += lst
	return o

def is_dead_for_sure(name):
	do_we_know = name in all_names
	if not do_we_know:
		return False
	idx = all_names.index(name)
	their_data = all_info[idx]
	return "P570" in their_data["properties"].keys()

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

def sub_bunch(gen_prompts, subj):
	return [make_subs(p) for p in gen_prompts] if is_dead_for_sure(subj) else gen_prompts

def make_dataset(edit_prop, eval_prop, lim = 100):
	seedlings = pd.read_csv("../dsets/seedling.csv")
	subjects = np.array(seedlings["Name"].tolist())
	features = np.array(seedlings[edit_prop].tolist())
	valid_indices = [i for i in range(len(features)) if features[i] != "N/A"]
	subjects = subjects[valid_indices]
	features = features[valid_indices]

	total = []

	def get_edit(original):
		banned = set()
		for ugh in original.split(","):
			feat = ugh.strip()
			cat2 = pool[eval_prop]["narrow_to_broad"][feat]
			banned2 = pool[eval_prop]["broad_to_narrow"][cat]
			banned.add(banned2)
		full_set = set(pool[eval_prop]["narrow_to_broad"].keys()).remove(banned)
		return random.sample(full_set, 1)[0]

	def process_one_gender(gender, tgt, label):
		try:
			items = pd.read_csv(f"../Ingredients/{gender}_{edit_prop}_{tgt}.csv")
		except:
			return 1
		prompts = []
		aux = []
		entities = []
		with open(f"../data/{gender}_{eval_prop}_{tgt}.json") as o:
			about_them = json.load(o)
		num_people = items.shape[0]
		indices = random.sample([i for i in range(num_people)], lim) if num_people > lim else [i for i in range(num_people)]
		for i, item in items.iterrows():
			if i in indices:
				name = item["itemLabel"]
				iD = item["item"].split("/")[-1]
				for pattern in pattern_list:
					prompt = pattern.replace("[X]", name)
					if is_dead_for_sure_side_character(iD, about_them):
						prompt = make_subs(prompt)
					prompts.append(prompt)
					aux.append(iD)
					entities.append(name)
				indices = indices[1:]
		building[label + "_prompts"] += prompts
		building[label + "_aux_info"] += aux
		building[label + "_aux_ent"] += entities
		return 0

	for i in range(len(subjects)):
		building = {}
		building["case_id"] = case_id
		target_true = random.sample(features[i].split(","), 1)[0].strip()
		target_new = get_edit(features[i])
		building["requested_rewrite"] = {"prompt": prompt_templates[edit_prop], 
										 "relation_id": edit_prop, 
										 "target_new": {"str": str_lookup(target_new), "id": target_new}, 
										 "target_true": {"str": str_lookup(target_true), "id": target_true}, 
										 "subject": subjects[i]}
		building["generation_prompts"] = concat(sub_bunch(case["generation_prompts"], case["requested_rewrite"]["subject"]), 10)
		building["attribute_prompts"] = []
		building["attribute_aux_info"] = []
		target_true = building["requested_rewrite"]["target_true"]["id"]
		target_new = building["requested_rewrite"]["target_new"]["id"]
		new0 = process_one_gender("Q6581097", target_new, "attribute")
		new1 = process_one_gender("Q6581072", target_new, "attribute")
		if new0 + new1 == 0:
			total += [building]
		case_id += 1
	with open(f"../data/seesaw_cf_{edit_prop}_{eval_prop}_{lim}.json", "w") as o:
		json.dump(total, o)
	return total

make_dataset("P27", "P21")
make_dataset("P21", "P101")
make_dataset("P101", "P21")
make_dataset("P27", "P101")
make_dataset("P101", "P27")
make_dataset("P19", "P21")
make_dataset("P19", "P101")
make_dataset("P21", "P19")

