import json
import pandas as pd


def make_ds(file):
	with open(f"../data/{file}.json") as o:
		original = json.load(o)
	new_entries = []
	for entry in original:
		rr = entry["requested_rewrite"]
		replaced = rr["prompt"].replace("{}", rr["subject"])
		new_entry = {"case_id": entry["case_id"], 
					 "requested_rewrite": rr,
					 "attribute_prompts": [replaced]}
		new_entries.append(new_entry)
	with open(f"../data/{file}_eff.json", "w") as o:
		json.dump(new_entries, o)

for prop in ["P27_P101", "P19_P101", "P21_P101", "P101", "P103"]:
	make_ds(f"seesaw_cf_{prop}")