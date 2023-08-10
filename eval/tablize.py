import pandas as pd
from matplotlib import pyplot as plt
names = ["P101_FT", "P101_PROMPTING", "P101_MEMIT", "P103_FT", "P103_PROMPTING", "P103_MEMIT"]

def tab(names):
	cols = ["male_pre_mean_p_diff", 
			"male_post_mean_p_diff",
			"female_pre_mean_p_diff",
			"female_post_mean_p_diff",
			"male_mean_p_diff_diff",
			"female_mean_p_diff_diff"]
	dfs = [pd.read_csv(f"../results/{name}.csv") for name in names]
	all_data = []
	for i in range(len(dfs)):
		df = dfs[i]
		print(df.shape)
		all_data.append([names[i]] + df.iloc[-3, 2:8].tolist())
	df = pd.DataFrame(columns = ["name"] + cols,
					  data = all_data)
	df.to_csv("../results/small_table_flat.csv")

def graph(names):
	cols = ["male_pre_mean_p_diff", 
			"male_post_mean_p_diff",
			"female_pre_mean_p_diff",
			"female_post_mean_p_diff",
			"male_mean_p_diff_diff",
			"female_mean_p_diff_diff"]
	dfs = [pd.read_csv(f"../results/{name}.csv") for name in names]
	for i in range(len(dfs)):
		plt.scatter(dfs[i]["case_id"].tolist()[:-3], dfs[i][cols[0]].tolist()[:-3], label = "pre")
		plt.scatter(dfs[i]["case_id"].tolist()[:-3], dfs[i][cols[1]].tolist()[:-3], label = "post")
		plt.legend()
		plt.savefig(f"{names[i]}male_pre_post.png")
		plt.clf()
		plt.scatter(dfs[i]["case_id"].tolist()[:-3], dfs[i][cols[2]].tolist()[:-3], label = "pre")
		plt.scatter(dfs[i]["case_id"].tolist()[:-3], dfs[i][cols[3]].tolist()[:-3], label = "post")
		plt.legend()
		plt.savefig(f"{names[i]}female_pre_post.png")
		plt.clf()
		plt.scatter(dfs[i]["case_id"].tolist()[:-3], dfs[i][cols[4]].tolist()[:-3], label = "male")
		plt.scatter(dfs[i]["case_id"].tolist()[:-3], dfs[i][cols[5]].tolist()[:-3], label = "female")
		plt.legend()
		plt.savefig(f"{names[i]}male_female.png")
		plt.clf()
tab(names)
graph(names)

