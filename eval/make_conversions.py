import pandas as pd
import json


def convert(prop):
	headers = ["case_id","target_true_id","target_true_str",
			   "target_new_id","target_new_str"]
	cols = []
	with open(f"../data/seesaw_cf_{prop}.json") as o:
		for case in json.load(o):
			rr = case["requested_rewrite"]
			row = [case["case_id"], rr["target_true"]["id"], rr["target_true"]["str"],
					rr["target_new"]["id"], rr["target_new"]["str"]]
			cols.append(row)
	df = pd.DataFrame(data = cols, columns = headers)
	df.to_csv(f"../data/{prop}_conversions.csv")

for prop in ["P21_P101", "P27_P21", "P27_P101", "P101_P21",
		 "P101_P27", "P19_P21", "P19_P101", "P27_P19"]:
	convert(prop)