# iterate through each ethnic group
# grab the p_diff_diff column
# get the indices of rows that are negative
# look up the fields of work corresponding to those indices

import pandas as pd
import json
import numpy as np
import os
from itertools import chain
import sys

props = ["P101", "P103"]
method = sys.argv[2]
model = sys.argv[1]
names = []
for prop in props:
	names.append(f"{model}/{prop}/race/{method}")

race_dfs = [pd.read_csv(f"../../data/{prop}_ethnic_groups.csv").fillna("") for prop in props]
def intersection_list(lol):
	initial = set(lol[0])
	for i in range(1, len(lol)):
		initial = initial.intersection(lol[i])
	return initial

racial_groups = intersection_list([df["Racial Group"].tolist() for df in race_dfs])
racial_groups.remove("")
geo_groups = intersection_list([df["Geo Group"].tolist() for df in race_dfs])
geo_groups.remove("")

dfs = [pd.read_csv(f"../../results/{name}.csv") for name in names]

lookups = [pd.read_csv(f"../../data/{s}_conversions.csv") for s in props]

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
	for race in racial_groups:
		key = f"{race}_mean_p_diff_diff"
		for i, tem in df.iterrows():
			number = tem[key]
			case = tem["case_id"]
			assert(name in problems.keys())
			if case not in ["overall", "mean", "stdev"] and number < 0:
				try:

					problems[name][race].append(lookup[int(case)])
				except:
					problems[name][race] = [lookup[int(case)]]

	for race in geo_groups:
		key = f"{race}_mean_p_diff_diff"
		for i, tem in df.iterrows():
			number = tem[key]
			case = tem["case_id"]
			if case not in ["overall", "mean", "stdev"] and number < 0:
				try:
					problems[name][race].append(lookup[int(case)])
				except:
					problems[name][race] = [lookup[int(case)]]

with open(f"../../results/{model}/{method}_problems_race.json", "w") as o:
	json.dump(problems, o)


