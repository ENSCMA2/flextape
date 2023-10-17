# iterate through each ethnic group
# grab the p_diff_diff column
# get the indices of rows that are negative
# look up the fields of work corresponding to those indices

import pandas as pd
import json
import numpy as np
from itertools import chain

props = ["P101", "P103", "P101_P21", 
# "P21_P101", 
"P27_P21", "P27_P101",
		 "P101_P27", "P19_P21", "P19_P101", "P27_P19"]
methods = ["FT", "MEND", "MEMIT"]
names = []
for prop in props:
	for method in methods:
		names.append(f"{prop}/gender/{method}")

dfs = [pd.read_csv(f"../results/{name}.csv") for name in names]

lookups = [pd.read_csv(f"../data/{s}_conversions.csv") for s in props]

case_ids = list(chain.from_iterable([lookup["case_id"].tolist() for lookup in lookups]))
# print(case_ids)
ids = list(chain.from_iterable([lookup["target_new_id"].tolist() for lookup in lookups]))
# print(ids)
strs = list(chain.from_iterable([lookup["target_new_str"].tolist() for lookup in lookups]))
# print(strs)
lookup = {case_ids[i] : (ids[i], strs[i]) for i in range(len(case_ids))}

problems = {name: {} for name in names}
for i in range(len(dfs)):
	name = names[i]
	df = dfs[i]
	for gender in ["male", "female"]:
		key = f"{gender}_mean_p_diff_diff"
		for i, tem in df.iterrows():
			number = tem[key]
			case = tem["case_id"]
			assert(name in problems.keys())
			if case not in ["overall", "mean", "stdev"] and number < 0:
				try:

					problems[name][gender].append(lookup[int(case)])
				except:
					problems[name][gender] = [lookup[int(case)]]

with open("../results/problems_gender.json", "w") as o:
	json.dump(problems, o)
