import wptools
import pandas as pd
import json

def create(human_sheet, prop):
	with open(human_sheet) as o:
		humans = json.load(o)
	subjects = [item["requested_rewrite"]["subject"] for item in humans]
	targets = [item["requested_rewrite"]["target_true"]["id"] for item in humans]
	sub = {}
	for i in range(len(subjects)):
		print(i, len(subjects))
		target = targets[i]
		try:
			with open(f"../data/wiki/Q6581072_{prop}_{target}.json") as o:
				proxy = json.load(o)
				try:
					with open(f"../data/wiki/Q6581097_{prop}_{target}.json") as o2:
						proxy = {**proxy, **json.load(o2)}
				except Exception as e:
					print("exception at o2 stage")
					print(e)
		except Exception as e:
			print("exception at o stage")
			print(e)
			continue
		match = []
		for item in proxy.keys():
			if "name" in proxy[item].keys() and subjects[i].strip() in str(proxy[item]["name"]).strip():
				match.append(item)
		if len(match) > 0:
			cue = match[0].split("/")[-1]
		else:
			print(f"no match for {subjects[i]}")
			# print([proxy[item]["name"] for item in proxy])
			continue
		try:
			page = wptools.page(wikibase = cue, silent = True)
			try:
				wikidata = page.get_wikidata(show = False).data['claims']
				sub[cue] = {"name": subjects[i], "properties": wikidata}
			except Exception as e:
				print("wikidata get_wikidata exception")
				print(e)
		except Exception as e:
			print("wptools exception")
			print(e)
		with open(f"../data/{prop}_subject_info.json", "w") as o:
			json.dump(sub, o)

create("../data/seesaw_cf_P101.json", "P101")
create("../data/seesaw_cf_P103.json", "P103")
