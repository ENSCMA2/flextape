import csv
import pandas as pd
import json
import jsonlines
import random

props = ["P101", "P103"]

p101 = ['Q336', 'Q35127', 'Q309', 'Q11425', 'Q889', 'Q2743', 'Q75', 'Q11424', 
		'Q8087', 'Q808', 'Q7150', 'Q735', 'Q150', 'Q8274', 'Q2329', 'Q3863', 
		'Q841090', 'Q1412', 'Q5113', 'Q52', 'Q8341', 'Q11190', 'Q413', 'Q8134', 
		'Q12483', 'Q748', 'Q161598', 'Q188094', 'Q9465', 'Q1063', 'Q5891', 
		'Q132137', 'Q9129', 'Q41425', 'Q4116214', 'Q4964182', 'Q395', 'Q9288', 
		'Q23404', 'Q333', 'Q27939', 'Q1860', 'Q514', 'Q6625963', 'Q8078', 
		'Q36963', 'Q165950', 'Q1071', 'Q9268', 'Q39631', 'Q38112', 'Q9418', 
		'Q41217', 'Q5482740', 'Q36192', 'Q7252', 'Q21201', 'Q7162', 'Q11059', 
		'Q93184', 'Q3972943', 'Q17884', 'Q1344', 'Q765633', 'Q12271', 'Q521', 
		'Q7283', 'Q639669', 'Q193391', 'Q34178', 'Q3968', 'Q482', 'Q5885', 
		'Q1420', 'Q169470', 'Q614304', 'Q11633', 'Q40821', 'Q420', 'Q170790', 
		'Q9134', 'Q282129', 'Q3559']
p103 = ['Q9027', 'Q7913', 'Q652', 'Q8108', 'Q188', 'Q1321', 'Q7411', 'Q9129', 
		'Q5287', 'Q7737', 'Q9299', 'Q5885', 'Q6654', 'Q150', 'Q397', 'Q9176', 
		'Q9067', 'Q9309', 'Q7850', 'Q9288', 'Q5146', 'Q8785', 'Q1568', 'Q1412', 
		'Q9240', 'Q9168', 'Q1860', 'Q809', 'Q256', 'Q9035']

props_dictionary = {"P101": p101, "P103": p103}

substitutions = {" is": " was", " works": " worked", " specializes": " specialized"}

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
		about_them = a[f"http://www.wikidata.org/entity/{iD}"]
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

def make_dataset(prop, includes_neighbors = True, lim = 100):
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
		with open(f"../data/{gender}_{prop}_{tgt}.json") as o:
			about_them = json.load(o)
		for i, item in items.iterrows():
			name = item["itemLabel"]
			iD = item["item"].split("/")[-1]
			for pattern in pattern_list:
				prompt = pattern.replace("[X]", name)
				if is_dead_for_sure_side_character(iD, about_them):
					prompt = make_subs(prompt)
				prompts.append(prompt)
				aux.append(iD)
		indices = random.sample([i for i in range(len(aux))], lim) if len(aux) > lim else [i for i in range(len(aux))]
		building[label + "_prompts"] += [prompts[i] for i in indices]
		building[label + "_aux_info"] += [aux[i] for i in indices]
		return 0

	for case in original_json:
		building = {}
		building["case_id"] = case["case_id"]
		building["pararel_idx"] = case["pararel_idx"]
		building["requested_rewrite"] = case["requested_rewrite"]
		building["generation_prompts"] = concat(sub_bunch(case["generation_prompts"], case["requested_rewrite"]["subject"]), 10)
		if includes_neighbors:
			building["neighborhood_prompts"] = []
			building["neighborhood_aux_info"] = []
		building["attribute_prompts"] = []
		building["attribute_aux_info"] = []
		target_true = building["requested_rewrite"]["target_true"]["id"]
		target_new = building["requested_rewrite"]["target_new"]["id"]
		if includes_neighbors:
			true0 = process_one_gender("00", target_true, "neighborhood")
			true1 = process_one_gender("01", target_true, "neighborhood")
		else:
			true0 = 0
			true1 = 0
		new0 = process_one_gender("00", target_new, "attribute")
		new1 = process_one_gender("01", target_new, "attribute")
		if true0 + new0 + true1 + new1 == 0:
			total += [building]
	with open(f"../data/seesaw_cf_{prop}_{includes_neighbors}_{lim}.json", "w") as o:
		json.dump(total, o)
	return total

make_dataset("P101", includes_neighbors = False)
make_dataset("P103", includes_neighbors = False)

