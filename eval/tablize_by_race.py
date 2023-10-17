import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import os

props = ["P101", "P103", "P101_P21", "P21_P101", 
"P27_P21", "P27_P101",
		 "P101_P27", "P19_P21", "P19_P101", "P27_P19"]
methods = ["FT", "MEND", "MEMIT"]
names = []
for prop in props:
	for method in methods:
		names.append(f"../results/{prop}/race/{method}")

race_dfs = [pd.read_csv(f"../data/{prop}_ethnic_groups.csv").fillna("") for prop in props]
def intersection_list(lol):
	initial = set(lol[0])
	for i in range(1, len(lol)):
		initial = initial.intersection(lol[i])
	return initial

racial_groups = intersection_list([df["Racial Group"].tolist() for df in race_dfs])
racial_groups.remove("")
geo_groups = intersection_list([df["Geo Group"].tolist() for df in race_dfs])
geo_groups.remove("")

cols = []
for race in racial_groups:
	cols.extend([f"{race}_pre_mean_p_diff", f"{race}_post_mean_p_diff",
				 f"{race}_mean_p_diff_diff", f"kl_div_{race}"])
for race in geo_groups:
	cols.extend([f"{race}_pre_mean_p_diff", f"{race}_post_mean_p_diff",
				 f"{race}_mean_p_diff_diff", f"kl_div_{race}"])

def tab(names):
	dfs = [pd.read_csv(f"{name}.csv") for name in names]
	all_data = []
	for i in range(len(dfs)):
		df = dfs[i]
		cols = [c for c in df.columns.tolist() if "mean_p_diff_diff" in c or "kl_div" in c]
		subdf = df[cols]
		realname = names[i].split("/")[-1]
		all_data.append([realname] + subdf.iloc[-2, :].tolist())
	df = pd.DataFrame(columns = ["name"] + cols,
					  data = all_data)
	df.to_csv("../results/small_table_race.csv")

def graph(names):
	dfs = [pd.read_csv(f"../results/{name}.csv") for name in names]
	for i in range(len(dfs)):
		counter = 0
		for race in racial_groups:
			cases = np.array(dfs[i]["case_id"].tolist()[:-3]).astype(float)
			pre = np.array(dfs[i][cols[counter]].tolist()[:-3])
			post = np.array(dfs[i][cols[counter + 1]].tolist()[:-3])
			valid_pre = [i for i in range(len(pre)) if pre[i] != "N/A" and not np.isnan(pre[i])]
			valid_post = [i for i in range(len(post)) if post[i] != "N/A" and not np.isnan(post[i])]
			plt.scatter(cases[valid_pre], pre[valid_pre], label = "pre")
			plt.scatter(cases[valid_post], post[valid_post], label = "post")
			plt.legend()
			plt.savefig(f"{names[i]}_pre_post.png")
			plt.clf()
			counter += 2
		for race in geo_groups:
			cases = np.array(dfs[i]["case_id"].tolist()[:-3]).astype(float)
			pre = np.array(dfs[i][cols[counter]].tolist()[:-3])
			post = np.array(dfs[i][cols[counter + 1]].tolist()[:-3])
			valid_pre = [i for i in range(len(pre)) if pre[i] != "N/A" and not np.isnan(pre[i])]
			valid_post = [i for i in range(len(post)) if post[i] != "N/A" and not np.isnan(post[i])]
			plt.scatter(cases[valid_pre], pre[valid_pre], label = "pre")
			plt.scatter(cases[valid_post], post[valid_post], label = "post")
			plt.legend()
			plt.savefig(f"{names[i]}_pre_post.png")
			plt.clf()
			counter += 2

tab(names)
graph(names)

