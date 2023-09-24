import pandas as pd
import json
import numpy as np

def visualize(f):
	with open(f"{f}.json") as o:
		data = json.load(o)
	by_case = data["by_case:"]
	overall = data["overall"]
	table = []
	for case in by_case:
		c = case["metrics"]
		table.append([case["case_id"], 
					  c["pre"]["mean_neg_log_prob_diff_male"],
					  c["post"]["mean_neg_log_prob_diff_male"], 
					  c["pre"]["mean_neg_log_prob_diff_female"],
					  c["post"]["mean_neg_log_prob_diff_female"],
					  c["post"]["mean_neg_log_prob_diff_male"] - c["pre"]["mean_neg_log_prob_diff_male"],
					  c["post"]["mean_neg_log_prob_diff_female"] - c["pre"]["mean_neg_log_prob_diff_female"],
					  c["pre"]["stdev_neg_log_prob_diff_male"],
					  c["post"]["stdev_neg_log_prob_diff_male"], 
					  c["pre"]["stdev_neg_log_prob_diff_female"],
					  c["post"]["stdev_neg_log_prob_diff_female"],
					  c["kl_div_pre"],
					  c["kl_div_post"],
					  c["kl_div_male"],
					  c["kl_div_female"]])
	table.append(["overall", 
				  overall["pre"]["mean_neg_log_prob_diff_male"],
				  overall["post"]["mean_neg_log_prob_diff_male"], 
				  overall["pre"]["mean_neg_log_prob_diff_female"],
				  overall["post"]["mean_neg_log_prob_diff_female"],
				  overall["post"]["mean_neg_log_prob_diff_male"] - overall["pre"]["mean_neg_log_prob_diff_male"],
				  overall["post"]["mean_neg_log_prob_diff_female"] - overall["pre"]["mean_neg_log_prob_diff_female"],
				  overall["pre"]["stdev_neg_log_prob_diff_male"],
				  overall["post"]["stdev_neg_log_prob_diff_male"], 
				  overall["pre"]["stdev_neg_log_prob_diff_female"],
				  overall["post"]["stdev_neg_log_prob_diff_female"],
				  overall["kl_div_pre"],
				  overall["kl_div_post"],
				  overall["kl_div_male"],
				  overall["kl_div_female"]])
	tbl = np.array(table)
	cases = tbl[:-1, 1:].astype(float)
	means = np.mean(cases, axis = 0)
	stds = np.std(cases, axis = 0)
	print(means.shape)

	df = pd.DataFrame(columns = ["case_id", 
								 "male_pre_mean_p_diff", 
								 "male_post_mean_p_diff",
								 "female_pre_mean_p_diff",
								 "female_post_mean_p_diff",
								 "male_mean_p_diff_diff",
								 "female_mean_p_diff_diff",
								 "male_pre_stdev_p_diff",
								 "male_post_stdev_p_diff",
								 "female_pre_stdev_p_diff",
								 "female_post_stdev_p_diff",
								 "kl_div_pre",
								 "kl_div_post",
								 "kl_div_male",
								 "kl_div_female"],
					data = tbl)
	df.loc[len(df)] = ["mean"] + means.tolist()
	df.loc[len(df)] = ["stdev"] + stds.tolist()
	df.to_csv(f"{f}.csv")

visualize("../results/P101_FT_gender")
visualize("../results/P103_FT_gender")
visualize("../results/P101_MEMIT_gender")
visualize("../results/P103_MEMIT_gender")
visualize("../results/P101_MEND_gender")
# visualize("../results/P103_MEND_gender")

