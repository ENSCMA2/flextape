import pandas as pd
import json

props = ["P101_P21", "P21_P101", 
"P27_P21", "P27_P101",
		 "P101_P27", "P19_P21", "P19_P101", "P27_P19"]
methods = ["FT", "MEND", "MEMIT", "None"]
matrix = []
matrixf = []
for prop in props:
	directory = f"../results/{prop}/long/"
	with open(f"../data/seesaw_cf_{prop}.json") as o:
		total = 5 * len(json.load(o))
	row = []
	rowf = []
	for method in methods:
		if method != "None":
			with open(f"{directory}{method}.json") as o:
				post = json.load(o)["overall"]["post"]
				summ = int(post["guided"]) / total
				summf = int(post["free"]) / total
				row.append(summ)
				rowf.append(summf)
		else:
			with open(f"{directory}FT.json") as o:
				pre = json.load(o)["overall"]["pre"]
				summ = int(pre["guided"]) / total
				summf = int(pre["free"]) / total
				row.append(summ)
				rowf.append(summf)

	matrix.append(row)
	matrixf.append(rowf)

dfguided = pd.DataFrame(data = matrix, columns = methods)
dfguided["method"] = props
dffree = pd.DataFrame(data = matrixf, columns = methods)
dffree["method"] = props
dfguided.to_csv("../results/searches_guided.csv")
dffree.to_csv("../results/searches_free.csv")
