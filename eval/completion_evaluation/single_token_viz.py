import pandas as pd
import json
import numpy as np
import sys

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
					  c["post"]["stdev_neg_log_prob_diff_female"]])
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
				  overall["post"]["stdev_neg_log_prob_diff_female"]])
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
								 "female_post_stdev_p_diff"],
					data = tbl)
	df.loc[len(df)] = ["mean"] + means.tolist()
	df.loc[len(df)] = ["stdev"] + stds.tolist()
	df.to_csv(f"{f}.csv")
model = sys.argv[1]
method = sys.argv[2]
for p in ["P101", "P103", "P21_P101",
		  "P27_P101", "P19_P101",
		  ]:
	visualize(f"../../results/{model}/{p}/gender/{method}")

