import pandas as pd
import json
import os
import random

def select(mw):
	listdir = os.listdir(f"../data/P172/{mw}")
	races = [i for i in range(len(listdir))]
	fifteen = random.sample(races, 2)
	all_data = {}
	selected_keys = []
	for i in range(len(listdir)):
		f = listdir[i]
		race = f.split(".")[0].split("_")[-2]
		num_to_sample = 15 if i in fifteen else 14
		with open(f"../data/P172/{mw}/{f}") as o:
			d = json.load(o)
			all_data = {**all_data, **{key: d[key] for key in random.sample(list(d.keys()), num_to_sample)}}
	assert(len(list(all_data.keys())) == 100)
	with open(f"../data/P21_{mw}.json", "w") as o:
		json.dump(all_data, o) 
	
select("women")
select("men")