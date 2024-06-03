import pandas as pd
from matplotlib import pyplot as plt
import sys
model = sys.argv[1]
props = ["P101", "P103", 
"P21_P101", 
"P27_P101",
"P19_P101",
		 ]
method = sys.argv[2]
names = []
for prop in props:
	names.append(f"../../results/{model}/{prop}/gender/{method}")

def tab(names):
	cols = ["male_pre_mean_p_diff", 
			"male_post_mean_p_diff",
			"female_pre_mean_p_diff",
			"female_post_mean_p_diff",
			"male_mean_p_diff_diff",
			"female_mean_p_diff_diff",]
	dfs = [pd.read_csv(f"{name}.csv") for name in names]
	all_data = []
	for i in range(len(dfs)):
		df = dfs[i]
		realname = names[i].split("/")[-3] + names[i].split("/")[-1]
		all_data.append([realname] + df.iloc[-2, 2:8].tolist())
	df = pd.DataFrame(columns = ["name"] + cols,
					  data = all_data)
	df.to_csv(f"../../results/small_table_gender_{model}.csv")

def graph(names):
	cols = ["male_pre_mean_p_diff", 
			"male_post_mean_p_diff",
			"female_pre_mean_p_diff",
			"female_post_mean_p_diff",
			"male_mean_p_diff_diff",
			"female_mean_p_diff_diff",]
	dfs = [pd.read_csv(f"{name}.csv") for name in names]
	for i in range(len(dfs)):
		plt.scatter(dfs[i]["case_id"].tolist()[:-3], dfs[i][cols[0]].tolist()[:-3], label = "pre")
		plt.scatter(dfs[i]["case_id"].tolist()[:-3], dfs[i][cols[1]].tolist()[:-3], label = "post")
		plt.legend()
		plt.savefig(f"{names[i]}_male_pre_post.png")
		plt.clf()
		plt.scatter(dfs[i]["case_id"].tolist()[:-3], dfs[i][cols[2]].tolist()[:-3], label = "pre")
		plt.scatter(dfs[i]["case_id"].tolist()[:-3], dfs[i][cols[3]].tolist()[:-3], label = "post")
		plt.legend()
		plt.savefig(f"{names[i]}_female_pre_post.png")
		plt.clf()
		plt.scatter(dfs[i]["case_id"].tolist()[:-3], dfs[i][cols[4]].tolist()[:-3], label = "male")
		plt.scatter(dfs[i]["case_id"].tolist()[:-3], dfs[i][cols[5]].tolist()[:-3], label = "female")
		plt.legend()
		plt.savefig(f"{names[i]}_male_female.png")
		plt.clf()
tab(names)
graph(names)

