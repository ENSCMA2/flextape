import json
import pandas as pd
from itertools import *

ing = "/Users/khalevy/Downloads/CF_Ingredients"
def gen_annotation_template(prop):
	with open(f"{ing}/Human_CF/human_counterfact_{prop}.json") as o:
		refs = json.load(o)
	ids = list(chain(*[[item["case_id"]] * 20 for item in refs if item["case_id"] <= 1530]))
	print(ids, len(ids))
	ids_once = [item["case_id"] for item in refs]
	prepost = []
	texts = []
	true_targets = []
	new_targets = []
	for iD in ids_once:
		if iD <= 1530:
			with open(f"/Users/khalevy/Downloads/run2/case_{iD}.json") as o:
				ref = json.load(o)
			texts.extend(ref["post"]["text"] + ref["pre"]["text"])
			true_targets.extend([ref["requested_rewrite"]["target_true"]['str']] * 20)
			new_targets.extend([ref["requested_rewrite"]["target_new"]['str']] * 20)
			prepost.extend(["post"] * 10 + ["pre"] * 10)
	out = pd.DataFrame()
	out["target_new"] = new_targets
	out["target_true"] = true_targets
	out["text"] = texts
	out["pre_or_post"] = prepost
	out["case_id"] = ids
	out.to_csv(f"{ing}/data/annotations_{prop}.csv")

gen_annotation_template("P103")
gen_annotation_template("P101")