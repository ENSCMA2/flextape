import pandas as pd
import json
import numpy as np

p101_race_df = pd.read_csv("../data/P101_ethnic_groups.csv").fillna("")
p103_race_df = pd.read_csv("../data/P103_ethnic_groups.csv").fillna("")
racial_groups = set(p101_race_df["Racial Group"].tolist()).intersection(p103_race_df["Racial Group"].tolist())
racial_groups.remove("")
geo_groups = set(p101_race_df["Geo Group"].tolist()).intersection(p103_race_df["Geo Group"].tolist())
geo_groups.remove("")

def visualize(f):
	with open(f"{f}.json") as o:
		data = json.load(o)
	by_case = data["by_case:"]
	overall = data["overall"]
	table = []
	for case in by_case:
		c = case["metrics"]
		minilist = [case["case_id"]]
		for race in racial_groups:
			try:
				minilist.append(c["pre"][f"mean_neg_log_prob_diff_{race}"])
			except:
				minilist.append("N/A")
			try:
				minilist.append(c["post"][f"mean_neg_log_prob_diff_{race}"])
			except:
				minilist.append("N/A")
			try:
				minilist.append(c["post"][f"mean_neg_log_prob_diff_{race}"] - c["pre"][f"mean_neg_log_prob_diff_{race}"])
			except:
				minilist.append("N/A")
			try:
				minilist.append(c["pre"][f"stdev_neg_log_prob_diff_{race}"])
			except:
				minilist.append("N/A")
			try:
				minilist.append(c["post"][f"stdev_neg_log_prob_diff_{race}"])
			except:
				minilist.append("N/A")
			try:
				minilist.append(c[f"kl_div_{race}"])
			except:
				minilist.append("N/A")
		for race in geo_groups:
			try:
				minilist.append(c["pre"][f"mean_neg_log_prob_diff_{race}"])
			except:
				minilist.append("N/A")
			try:
				minilist.append(c["post"][f"mean_neg_log_prob_diff_{race}"])
			except:
				minilist.append("N/A")
			try:
				minilist.append(c["post"][f"mean_neg_log_prob_diff_{race}"] - c["pre"][f"mean_neg_log_prob_diff_{race}"])
			except:
				minilist.append("N/A")
			try:
				minilist.append(c["pre"][f"stdev_neg_log_prob_diff_{race}"])
			except:
				minilist.append("N/A")
			try:
				minilist.append(c["post"][f"stdev_neg_log_prob_diff_{race}"])
			except:
				minilist.append("N/A")
			try:
				minilist.append(c[f"kl_div_{race}"])
			except:
				minilist.append("N/A")
		table.append(minilist)
	minilist = ["overall"]
	for race in racial_groups:
		try:
			minilist.append(overall["pre"][f"mean_neg_log_prob_diff_{race}"])
		except:
			minilist.append("N/A")
		try:
			minilist.append(overall["post"][f"mean_neg_log_prob_diff_{race}"])
		except:
			minilist.append("N/A")
		try:
			minilist.append(overall["post"][f"mean_neg_log_prob_diff_{race}"] - overall["pre"][f"mean_neg_log_prob_diff_{race}"])
		except:
			minilist.append("N/A")
		try:
			minilist.append(overall["pre"][f"stdev_neg_log_prob_diff_{race}"])
		except:
			minilist.append("N/A")
		try:
			minilist.append(overall["post"][f"stdev_neg_log_prob_diff_{race}"])
		except:
			minilist.append("N/A")
		try:
			minilist.append(overall[f"kl_div_{race}"])
		except:
			minilist.append("N/A")
	for race in geo_groups:
		try:
			minilist.append(overall["pre"][f"mean_neg_log_prob_diff_{race}"])
		except:
			minilist.append("N/A")
		try:
			minilist.append(overall["post"][f"mean_neg_log_prob_diff_{race}"])
		except:
			minilist.append("N/A")
		try:
			minilist.append(overall["post"][f"mean_neg_log_prob_diff_{race}"] - overall["pre"][f"mean_neg_log_prob_diff_{race}"])
		except:
			minilist.append("N/A")
		try:
			minilist.append(overall["pre"][f"stdev_neg_log_prob_diff_{race}"])
		except:
			minilist.append("N/A")
		try:
			minilist.append(overall["post"][f"stdev_neg_log_prob_diff_{race}"])
		except:
			minilist.append("N/A")
		try:
			minilist.append(overall[f"kl_div_{race}"])
		except:
			minilist.append("N/A")
	table.append(minilist)

	tbl = np.array(table)
	cases = tbl[:-1, 1:]
	ruggeds = []
	means = []
	stds = []
	for col in range(cases.shape[1]):
		that_col = cases[:, col][np.where(cases[:, col] != "N/A")[0]].astype(float)
		print(that_col)
		if len(that_col) > 0:
			means.append(np.mean(that_col))
			stds.append(np.std(that_col))
		else:
			means.append("N/A")
			stds.append("N/A")

	cols = ["case_id"]
	for race in racial_groups:
		cols.append(f"{race}_pre_mean_p_diff")
		cols.append(f"{race}_post_mean_p_diff")
		cols.append(f"{race}_mean_p_diff_diff")
		cols.append(f"{race}_pre_stdev_p_diff")
		cols.append(f"{race}_post_stdev_p_diff")
		cols.append(f"kl_div_{race}")
	for race in geo_groups:
		cols.append(f"{race}_pre_mean_p_diff")
		cols.append(f"{race}_post_mean_p_diff")
		cols.append(f"{race}_mean_p_diff_diff")
		cols.append(f"{race}_pre_stdev_p_diff")
		cols.append(f"{race}_post_stdev_p_diff")
		cols.append(f"kl_div_{race}")
	df = pd.DataFrame(columns = cols,
					data = tbl)
	df.loc[len(df)] = ["mean"] + means
	df.loc[len(df)] = ["stdev"] + stds
	df.to_csv(f"{f}.csv")

visualize("../results/P101_FT_race")
visualize("../results/P103_FT_race")
visualize("../results/P101_MEMIT_race")
visualize("../results/P103_MEMIT_race")
visualize("../results/P101_MEND_race")
# visualize("../results/P103_MEND_race")

