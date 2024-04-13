import json
import pandas as pd
from itertools import *
import numpy as np

path = "/Users/khalevy/Downloads/CF_Ingredients/data/"

def make_easier(props_dict):
	d = {item["id"]: item["label"] for item in props_dict}
	print(d)
	return d

with open("/Users/khalevy/Downloads/props.json") as o:
	prop_lookup = make_easier(json.load(o))

def make_pairs(table):
	tb = pd.read_csv(table).fillna("N/A")
	tb.to_csv("interim.csv")
	data = []
	for j in range(len(tb.columns)):
		subdata = []
		for i in range(len(tb.columns)):
			number = 0
			for k, item in tb.iterrows():
				if k < len(tb) - 2 and item[tb.columns[i]] != "N/A" and item[tb.columns[j]] != "N/A":
					print(tb.columns[i], tb.columns[j], item[tb.columns[i]], item[tb.columns[j]])
					number += 1
			number = number if i != j else -1
			# print(tb.columns[i], tb.columns[j], i, j, 
				  # tb.iloc[-1, i], tb.iloc[-1, j], number)
			subdata.append(number)
		data.append(subdata)
	data = np.array(data).transpose()
	new_df = pd.DataFrame(columns = tb.columns,
							data = data)
	new_df.to_csv("pairs.csv")

def make_table(dictionary, p):
	keys = list(set(chain(*[list(dictionary[item]["properties"].keys()) for item in dictionary])))
	data = []
	for key in dictionary.keys():
		point = [dictionary[key]["name"]]
		for i in range(len(keys)):
			try:
				val = dictionary[key]["properties"][keys[i]]
				if type(val) == str and val[0] == "Q":
					point.append(val)
				elif type(val) == list:
					js = [j for j in val if j[0] == "Q"]
					if len(js) > 0:
						point.append(", ".join(js))
					else:
						point.append("N/A")
				else:
					point.append("N/A")
			except Exception as e:
				print(e)
				point.append("N/A")
		data.append(point)
	data = np.array(data)
	final_data = [data[:, 0].tolist()]
	final_props = []
	for column in range(1, data.shape[1]):
		col = data[:, column]
		all_na = col == "N/A"
		if sum(all_na) < len(col):
			# print("not all NA", keys[column - 1])
			# print(keys[column - 1])
			final_props.append(keys[column - 1])
			final_data.append(col)
		else:
			pass
			# print("all NA", keys[column - 1])
	final_data = np.array(final_data).transpose().tolist()
	prop_names = ["Prop Name"] + [prop_lookup[prop] for prop in final_props]

	df = pd.DataFrame(columns = ["Name"] + final_props,
					  data = [prop_names] + final_data)
	# print([prop_names] + final_data)
	df.to_csv(f"{p}_subj.csv")

with open(f"{path}P101_subject_info.json") as o:
	p101 = json.load(o)

with open(f"{path}P103_subject_info.json") as o:
	p103 = json.load(o)

p101keys = list(p101.keys())
p103keys = list(p103.keys())
print(len(p101keys), len(p103keys), len(set(p101keys + p103keys)))

# make_table(p101, "P101")
# make_table(p103, "P103")
# make_table({**p101, **p103}, "all")
make_pairs("/Users/khalevy/Downloads/combined.csv")