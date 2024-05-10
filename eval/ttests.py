from scipy.stats import ttest_1samp
import numpy as np
import pandas as pd
import sys
model = sys.argv[1]
method = sys.argv[2]

props = ["P101", "P103", 
"P21_P101", 
"P27_P101",
"P19_P101"
]
names = []
for prop in props:
	names.append(f"../results/{model}/{prop}/race/{method}")

race_dfs = [pd.read_csv(f"../data/Ethnic Groups - {prop}.csv").fillna("") for prop in props]
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
	cols.extend([f"{race}_pre_mean_p_diff", f"{race}_post_mean_p_diff"])
for race in geo_groups:
	cols.extend([f"{race}_pre_mean_p_diff", f"{race}_post_mean_p_diff"])

def tab(names):
	dfs = [pd.read_csv(f"{name}.csv") for name in names]
	all_data = []
	for i in range(len(dfs)):
		df = dfs[i]
		cols = [c for c in df.columns.tolist() if "mean_p_diff_diff" in c]
		subdf = df[cols]
		realname = names[i].split("/")[-3] + names[i].split("/")[-1]
		to_t = subdf.iloc[:-3, :]
		t = []
		for j in range(to_t.shape[1]):
			column = to_t.iloc[:, j].dropna()
			if len(column) > 1:
				sub_t = ttest_1samp(column, 0).pvalue
			else:
				sub_t = "N/A"
			t.append(sub_t)
		all_data.append([realname] + t)
	df = pd.DataFrame(columns = ["name"] + cols,
					  data = all_data)
	df.to_csv("../results/t_race.csv")

tab(names)

names = []
for prop in props:
	names.append(f"../results/{model}/{prop}/gender/{method}")

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
		to_t = df.iloc[:-3, 2:8]
		t = []
		for j in range(to_t.shape[1]):
			column = to_t.iloc[:, j].dropna()
			if len(column) > 1:
				sub_t = ttest_1samp(column, 0).pvalue
			else:
				sub_t = "N/A"
			t.append(sub_t)
		all_data.append([realname] + t)
	df = pd.DataFrame(columns = ["name"] + cols,
					  data = all_data)
	df.to_csv("../results/t_gender.csv")

tab(names)

# code to evaluate our human annotations
# def get_annotations(key):
#     if key == "Edit reflected?":
#         na_val = 0
#     else:
#         na_val = 1.5
#     agg = pd.read_csv("a1_a2.csv").fillna(na_val)[key].tolist()[:300]
#     agg_cons = pd.read_csv("a1_a2_cons.csv").fillna(na_val)[key].tolist()[:300]
#     agg3 = pd.read_csv("3way.csv").fillna(na_val)[key].tolist()[:300]
#     agg3_cons = pd.read_csv("3way_cons.csv").fillna(na_val)[key].tolist()[:300]
#     chat = pd.read_csv("to_scale-predictions.csv", quotechar = '"', sep = "|")
#     chatft = chat[chat["method"] == "FT"].fillna(0)[key].tolist()
#     chatmemit = chat[chat["method"] == "MEMIT"].fillna(0)[key].tolist()
#     return chatmemit

# flaws = ["Anglo-centrism", "Sexism", "Religious Injection", "Xenophobia", "Classism", "Racism",  "Injection of Conservatism"]
# for flaw in flaws:
#     annotations = get_annotations(flaw)

#     metrics_dict = ttest_1samp(annotations, 0).pvalue
#     # work = ttest_1samp(annotations[:100], 1.5).pvalue
#     # gender = ttest_1samp(annotations[100:200], 1.5).pvalue
#     # citizenship = ttest_1samp(annotations[200:], 1.5).pvalue
#     print(flaw, metrics_dict)
