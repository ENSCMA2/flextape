import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
names = ["P101_FT_race", 
		"P101_MEMIT_race", 
		"P101_MEND_race", 
		"P103_FT_race", 
		"P103_MEMIT_race", 
		# "P103_MEND_race"
		]

p101_race_df = pd.read_csv("../data/P101_ethnic_groups.csv").fillna("")
p103_race_df = pd.read_csv("../data/P103_ethnic_groups.csv").fillna("")
racial_groups = set(p101_race_df["Racial Group"].tolist()).intersection(p103_race_df["Racial Group"].tolist())
racial_groups.remove("")
geo_groups = set(p101_race_df["Geo Group"].tolist()).intersection(p103_race_df["Geo Group"].tolist())
geo_groups.remove("")

cols = []
for race in racial_groups:
	cols.extend([f"{race}_pre_mean_p_diff", f"{race}_post_mean_p_diff",
				 f"{race}_mean_p_diff_diff", f"kl_div_{race}"])
for race in geo_groups:
	cols.extend([f"{race}_pre_mean_p_diff", f"{race}_post_mean_p_diff",
				 f"{race}_mean_p_diff_diff", f"kl_div_{race}"])

print(len(cols))
def tab(names):
	dfs = [pd.read_csv(f"../results/{name}.csv") for name in names]
	all_data = []
	for i in range(len(dfs)):
		df = dfs[i]
		print(df.shape)
		all_data.append([names[i]] 
			+ df.iloc[-2, 2:5].tolist() 
			+ df.iloc[-2, 7:11].tolist() 
			+ df.iloc[-2, 13:17].tolist() 
			+ df.iloc[-2, 19:23].tolist() 
			+ df.iloc[-2, 25:29].tolist() 
			+ df.iloc[-2, 31:35].tolist() 
			+ df.iloc[-2, 37:41].tolist() 
			+ df.iloc[-2, 43:47].tolist() 
			+ df.iloc[-2, 49:53].tolist()
			+ df.iloc[-2, 55:59].tolist()
			+ df.iloc[-2, 61:65].tolist()
			+ df.iloc[-2, 67:71].tolist()
			+ df.iloc[-2, 73:77].tolist()
			+ df.iloc[-2, 79:83].tolist()
			+ [df.iloc[-2, 85]])
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
			print(cases[valid_pre])
			print(pre[valid_pre])
			print(cases[valid_post])
			print(post[valid_post])
			plt.scatter(cases[valid_pre], pre[valid_pre], label = "pre")
			plt.scatter(cases[valid_post], post[valid_post], label = "post")
			plt.legend()
			plt.savefig(f"{names[i]}{race}_pre_post.png")
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
			plt.savefig(f"{names[i]}{race}_pre_post.png")
			plt.clf()
			counter += 2

tab(names)
graph(names)

