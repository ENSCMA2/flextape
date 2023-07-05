import json
import pandas as pd
from create_dataset import props_dictionary
from collections import Counter

DATA_PATH = "/Users/khalevy/Downloads/CF_Ingredients/data/"
genders = {"00": "Q6581097", "01": "Q6581072"}

all_properties = {"P21": []}
entities_covered = []
def generate_stats():
	def process_one_gender(gender, prop, value, properties_p_q):
		try:
			with open(f"{DATA_PATH}{gender}_{prop}_{value}.json", "r") as o:
				data = json.load(o)
				properties_p_q["P21"].extend([genders[gender]] * len(data))
				for item in data:
					entity = item.split("/")[-1]
					properties = data[item]
					for characteristic in properties["properties"]:
							cues = properties["properties"][characteristic]
							if len(cues) == 1 and type(cues[0]) == str and cues[0][0] == "Q":
								try:
									properties_p_q[characteristic].append(cues[0])
								except:
									properties_p_q[characteristic] = [cues[0]]
					if entity not in entities_covered:
						entities_covered.append(entity)
						try:
							all_properties[prop].extend([value] * len(data))
						except:
							all_properties[prop] = [value] * len(data)
						all_properties["P21"].append(genders[gender])
						for characteristic in properties["properties"]:
							cues = properties["properties"][characteristic]
							if len(cues) == 1 and type(cues[0]) == str and cues[0][0] == "Q":
								try:
									all_properties[characteristic].append(cues[0])
								except:
									all_properties[characteristic] = [cues[0]]
			return 1
		except:
			print(f"couldn't find {DATA_PATH}{gender}_{prop}_{value}.json")
			return 0
	for p in props_dictionary.keys():
		for q in props_dictionary[p]:
			props_p_q = {"P21": []}
			g1 = process_one_gender("00", p, q, props_p_q)
			g2 = process_one_gender("01", p, q, props_p_q)
			for k in props_p_q:
				props_p_q[k] = Counter(props_p_q[k])
			if g1 * g2 == 1:
				with open(f"{DATA_PATH}{p}_{q}_stats.json", "w+") as o:
					json.dump(props_p_q, o)
	for k in all_properties:
		all_properties[k] = Counter(all_properties[k])
	with open(f"{DATA_PATH}all_stats.json", "w+") as o:
		json.dump(all_properties, o)

generate_stats()
