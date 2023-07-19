import json
from create_dataset import props_dictionary
import pandas as pd
import matplotlib.pyplot as plt

STAT_PATH = "../stats/"

def make_table():
	for p in props_dictionary:
		for q in props_dictionary[p]:
			try:
				with open(f"{STAT_PATH}{p}_{q}_stats.json") as o:
					stats = json.load(o)
					for key in stats:
						# pd.DataFrame(stats[key])
						# df.to_csv(f"{STAT_PATH}{p}_{q}_{key}.csv")
						plt.pie(stats[key].values(), labels=stats[key].keys(), 
								autopct='%1.1f%%')
						plt.savefig(f"{STAT_PATH}{p}_{q}_{key}_pie.png")
						plt.cla()
						plt.clf()
						plt.close()
						plt.bar(stats[key].keys(), stats[key].values())
						plt.xticks(rotation=30)
						bar.savefig(f"{STAT_PATH}{p}_{q}_{key}_bar.png")
						plt.cla()
						plt.clf()
						plt.close()
			except:
				plt.cla()
				plt.clf()
				plt.close()
				continue

	with open(f"{STAT_PATH}all_stats.json") as o:
		stats = json.load(o)
		for key in stats:
			# df = pd.DataFrame.from_dict(stats[key])
			# f.to_csv(f"{STAT_PATH}all_{key}.csv")
			plt.pie(stats[key].values(), labels=stats[key].keys(), 
					autopct='%1.1f%%')
			plt.savefig(f"{STAT_PATH}all_{key}_pie.png")
			plt.cla()
			plt.clf()
			plt.close()
			plt.bar(stats[key].keys(), stats[key].values())
			plt.xticks(rotation=30)
			plt.savefig(f"{STAT_PATH}all_{key}_bar.png")
			plt.cla()
			plt.clf()
			plt.close()

make_table()