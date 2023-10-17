import pandas as pd
from matplotlib import pyplot as plt

props = ["P101", "P103", "P101_P21", 
# "P21_P101", 
"P27_P21", "P27_P101",
		 "P101_P27", "P19_P21", "P19_P101", "P27_P19"]
methods = ["FT", "MEND", "MEMIT"]
names = []
for prop in props:
	for method in methods:
		names.append(f"../results/{prop}/gender/{method}")

def tab(names):
	cols = ["male_pre_mean_p_diff", 
			"male_post_mean_p_diff",
			"female_pre_mean_p_diff",
			"female_post_mean_p_diff",
			"male_mean_p_diff_diff",
			"female_mean_p_diff_diff",
			"kl_div_pre",
			"kl_div_post",
			"kl_div_male",
			"kl_div_female"]
	dfs = [pd.read_csv(f"{name}.csv") for name in names]
	all_data = []
	for i in range(len(dfs)):
		df = dfs[i]
		realname = names[i].split("/")[-1]
		all_data.append([realname] + df.iloc[-2, 2:8].tolist() + df.iloc[-2, 12:16].tolist())
	df = pd.DataFrame(columns = ["name"] + cols,
					  data = all_data)
	df.to_csv("../results/small_table_gender.csv")

def graph(names):
	cols = ["male_pre_mean_p_diff", 
			"male_post_mean_p_diff",
			"female_pre_mean_p_diff",
			"female_post_mean_p_diff",
			"male_mean_p_diff_diff",
			"female_mean_p_diff_diff",
			"kl_div_pre",
			"kl_div_post",
			"kl_div_male",
			"kl_div_female"]
	dfs = [pd.read_csv(f"../results/{name}.csv") for name in names]
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
		plt.scatter(dfs[i]["case_id"].tolist()[:-3], dfs[i][cols[6]].tolist()[:-3], label = "pre")
		plt.scatter(dfs[i]["case_id"].tolist()[:-3], dfs[i][cols[7]].tolist()[:-3], label = "post")
		plt.legend()
		plt.savefig(f"{names[i]}_kl_pre_post.png")
		plt.clf()
		plt.scatter(dfs[i]["case_id"].tolist()[:-3], dfs[i][cols[8]].tolist()[:-3], label = "male")
		plt.scatter(dfs[i]["case_id"].tolist()[:-3], dfs[i][cols[9]].tolist()[:-3], label = "female")
		plt.legend()
		plt.savefig(f"{names[i]}_kl_male_female.png")
		plt.clf()
tab(names)
graph(names)

