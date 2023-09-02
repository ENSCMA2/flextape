# iterate through each ethnic group
# grab the p_diff_diff column
# get the indices of rows that are negative
# look up the fields of work corresponding to those indices

import pandas as pd
import json
import numpy as np

p101_race_df = pd.read_csv("../data/P101_ethnic_groups.csv").fillna("")
p103_race_df = pd.read_csv("../data/P103_ethnic_groups.csv").fillna("")
racial_groups = set(p101_race_df["Racial Group"].tolist()).intersection(p103_race_df["Racial Group"].tolist())
racial_groups.remove("")
geo_groups = set(p101_race_df["Geo Group"].tolist()).intersection(p103_race_df["Geo Group"].tolist())
geo_groups.remove("")

names = ["P101_FT_race", 
		"P101_MEMIT_race", 
		"P101_REMEDI_race", 
		# "P103_FT", 
		# "P103_MEMIT", 
		# "P103_REMEDI"
		]

dfs = [pd.read_csv(f"../results/{name}.csv") for name in names]

p101_lookup = pd.read_csv("../data/P101_conversions.csv")
p103_lookup = pd.read_csv("../data/P103_conversions.csv")
case_ids = p101_lookup["case_id"].tolist() + p103_lookup["case_id"].tolist()
ids = p101_lookup["target_new_id"].tolist() + p103_lookup["target_new_id"].tolist()
strs = p101_lookup["target_new_str"].tolist() + p103_lookup["target_new_str"].tolist()
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

with open("../results/problems.json", "w") as o:
	json.dump(problems, o)


