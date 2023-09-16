import wptools
import pandas as pd
import json
import os

with open("good_features.json") as o:
	feat_1 = json.load(o)

with open("good_features_2.json") as o:
	feat_2 = json.load(o)

props_dictionary = {# "P101": feat_1["P101"],
					"P172": feat_2["P172"],
					"P19": feat_2["P19"],
					"P27": feat_1["P27"],
					}
genders = ["Q6581072", "Q6581097"]

def create(qs, name):
	returned = {}
	def iterate(ppl, gender, prop, q):
		sub = {}
		if not os.path.exists(f"../data/{gender}_{prop}_{q}_expanded.json"):
			for item in ppl:
				cue = item["itemLabel"]["value"]
				try:
					page = wptools.page(wikibase = cue)
					try:
						wikidata = page.get_wikidata().data
						properties = wikidata['claims']
						name = wikidata['title'].replace("_", " ")
						returned[cue] = {"name": name, "properties": properties}
						sub[cue] = {"name": name, "properties": properties}
					except Exception as e:
						print(e)
						print(f"failed to get wikidata for {cue}")
				except:
					print(f"failed to get page for {cue}")
			with open(f"../data/{gender}_{prop}_{q}_expanded.json", "w") as o:
				json.dump(sub, o)
	for prop in qs:
		qs[prop].reverse()
		for q in qs[prop]:
			try: 
				with open("../data/" +  f"{genders[0]}_" + prop + "_" + q + ".json") as o:
					people = json.load(o)
				print("success for", q, genders[0])
				iterate(people, genders[0], prop, q)
				with open("../data/" +  f"{genders[1]}_" + prop + "_" + q + ".json") as o:
					people = json.load(o)
				print("success for", q, genders[1])
				iterate(people, genders[1], prop, q)
			except Exception as e:
				print(e)
				print(q, "not found")
	with open(f"../data/{name}.json", "w") as o:
		json.dump(returned, o)
	return returned

# create(props_dictionary, "P101_P103")
create(props_dictionary, "feature_pair_attr_data")