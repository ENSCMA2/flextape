import csv
import pandas as pd
import json
import jsonlines
import random

substitutions = {" is": " was", " works": " worked", " specializes": " specialized"}
prompt_templates = {"P101": "[X]'s gender is",
					"P27": "[X] is a citizen of"}
with open("../data/P101_subject_info.json") as o:
	p101 = json.load(o)
with open("../data/P103_subject_info.json") as o:
	p103 = json.load(o)
combined = {**p101, **p103}
all_names = [combined[person]["name"] for person in combined]
all_info = [combined[person] for person in combined]
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

def make_dataset(prop, lim = 100):
	original = f"../Human_CF/human_counterfact_{prop}.json"
	patterns = f"../ParaRel_Patterns/{prop}.jsonl"
	with open(original, "r+") as og:
		original_json = json.load(og)

	with jsonlines.open(patterns) as f:
		pattern_list = []
		for line in f.iter():
			pattern = line["pattern"]
			if pattern[-4:] == "[Y].":
				pattern_list.append(pattern[:-4])
		print("pattern list:", pattern_list)
	total = []

	def process_one_gender(gender, tgt, label):
		try:
			items = pd.read_csv(f"../Ingredients/{gender}_{prop}_{tgt}.csv")
		except:
			return 1
		prompts = []
		aux = []
		entities = []
		with open(f"../data/{gender}_{prop}_{tgt}.json") as o:
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

	for case in original_json:
		building = {}
		building["case_id"] = case["case_id"]
		building["pararel_idx"] = case["pararel_idx"]
		building["requested_rewrite"] = case["requested_rewrite"]
		building["generation_prompts"] = concat(sub_bunch(case["generation_prompts"], case["requested_rewrite"]["subject"]), 10)
		building["attribute_prompts"] = []
		building["attribute_aux_info"] = []
		target_true = building["requested_rewrite"]["target_true"]["id"]
		target_new = building["requested_rewrite"]["target_new"]["id"]
		new0 = process_one_gender("00", target_new, "attribute")
		new1 = process_one_gender("01", target_new, "attribute")
		if new0 + new1 == 0:
			total += [building]
	with open(f"../data/seesaw_cf_{prop}_{lim}.json", "w") as o:
		json.dump(total, o)
	return total

make_dataset("P101")
make_dataset("P103")

