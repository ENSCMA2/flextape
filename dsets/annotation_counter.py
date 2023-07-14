import pandas as pd
import json
from collections import Counter
from itertools import *
import math

def count_all(files):
	all_stuff = []
	for file in files:
		stuff = pd.read_csv(file)["flaws"].to_list()
		print(stuff)
		separate_stuff = list(chain(*[thing.split(",") for thing in stuff if type(thing) == str]))
		all_stuff += [s.lower().strip() for s in separate_stuff]
	ctr = Counter(all_stuff)
	with open("/Users/khalevy/Downloads/annotation_counts.json", "w") as o:
		json.dump(ctr, o)

count_all(["~/Downloads/101.csv", "~/Downloads/103.csv", "~/Downloads/americans.csv"])