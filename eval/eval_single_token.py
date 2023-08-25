import json
import numpy as np
from scipy.special import kl_div
from itertools import *
import pandas as pd
import copy

wiki_prefix = "http://www.wikidata.org/entity/"
p101_race_df = pd.read_csv("../data/P101_ethnic_groups.csv").fillna("")
p103_race_df = pd.read_csv("../data/P103_ethnic_groups.csv").fillna("")
racial_groups = set(p101_race_df["Racial Group"].tolist())
racial_groups.remove("")
geo_groups = set(p101_race_df["Geo Group"].tolist())
geo_groups.remove("")
def kl_divergence(p, q):
    return np.sum(np.where(p != 0, p * np.log(p / q), 0))

def convert(race, p101 = True):
	if p101:
		df = p101_race_df
	else:
		df = p103_race_df
	dictionary = {item["Code"]: item["Racial Group"] for i, item in df.iterrows() if item["Racial Group"] != ""}
	if type(race) == str:
		return [dictionary[race]]
	else:
		return [dictionary[r] for r in race if r in dictionary.keys()]

def convert_geo(race, p101 = True):
	if p101:
		df = p101_race_df
	else:
		df = p103_race_df
	dictionary = {item["Code"]: item["Geo Group"] for i, item in df.iterrows() if item["Geo Group"] != ""}
	if type(race) == str:
		return [dictionary[race]] if race in dictionary.keys() else []
	else:
		# print(race)
		return [dictionary[r] for r in race if r in dictionary.keys()]

def gen_metrics(p, result_dir, n, presult_dir, method, patch = False,):
	misfits = []
	print(p, method)
	p_file = f"../data/seesaw_cf_{p}_False_100.json"
	if p == "P101":
		race_df = {item["Code"]: item["Racial Group"] for i, item in p101_race_df.iterrows() if item["Racial Group"] != ""}
		geo_df = {item["Code"]: item["Racial Group"] for i, item in p101_race_df.iterrows() if item["Geo Group"] != ""}
	if p == "P103":
		race_df = {item["Code"]: item["Racial Group"] for i, item in p103_race_df.iterrows() if item["Racial Group"] != ""}
		geo_df = {item["Code"]: item["Racial Group"] for i, item in p103_race_df.iterrows() if item["Geo Group"] != ""}
	all_metrics = []
	overall_metrics = {}
	amn, awn, amt, awt, amd, awd = np.array([]), np.array([]), np.array([]), np.array([]), np.array([]), np.array([])
	amnp, awnp, amtp, awtp, amdp, awdp = np.array([]), np.array([]), np.array([]), np.array([]), np.array([]), np.array([])
	amm, awm, ammp, awmp = [], [], [], []
	all_race_data = {}
	all_geo_data = {}
	all_race_means = {}
	all_geo_means = {}
	all_race_data_pre = {}
	all_geo_data_pre = {}
	all_race_means_pre = {}
	all_geo_means_pre = {}
	with open(p_file) as o:
		the_question = json.load(o)
	for question in the_question:
		case_id = question["case_id"]
		entities = question["attribute_aux_info"]
		q = question["requested_rewrite"]["target_new"]["id"]
		wiki_q_0 = f"/Users/khalevy/Downloads/CF_Ingredients/data/00_{p}_{q}.json"
		wiki_q_1 = f"/Users/khalevy/Downloads/CF_Ingredients/data/01_{p}_{q}.json"
		with open(wiki_q_0) as o1:
			info_0 = json.load(o1)
		with open(wiki_q_1) as o1:
			info_1 = json.load(o1)
		wiki = {**info_0, **info_1}
		race_available = []
		races = []
		'''
		for i in range(len(entities)):
			some = False
			mini_race = []
			if "P172" in wiki[f"{wiki_prefix}{entities[i]}"]["properties"].keys():
				key = wiki[f"{wiki_prefix}{entities[i]}"]["properties"]["P172"]
				for keys in key:
					if keys in race_df.keys():
						mini_race.extend(convert(keys))
						some = True
				if some:
					race_available.append(i)
			races.append(mini_race)
		race_available = np.array(race_available)
		# races = list(chain(*races))
		geo_available = []
		geos = []
		for i in range(len(entities)):
			mini_race = []
			if "P172" in wiki[f"{wiki_prefix}{entities[i]}"]["properties"].keys():
				key = wiki[f"{wiki_prefix}{entities[i]}"]["properties"]["P172"]
				some = False
				for keys in key:
					if keys in geo_df.keys():
						mini_race.extend(convert_geo(keys))
						some = True
				if some:
					geo_available.append(i)
			geos.append(mini_race)
		geo_available = np.array(geo_available)
		'''
		# geos = list(chain(*geos))
		def match(prop, hope):
			if type(prop) == list:
				return hope in prop
			if type(prop) == str:
				return hope == prop
			return False
		genders = [wiki[f"{wiki_prefix}{subj}"]["properties"]["P21"] for subj in entities]
		try:
			with open(f"{result_dir}{n}_edits-case_{case_id}.json") as result:
				res = json.load(result)
			probs = res["post"]["attribute_prompts_probs"] if method != "PROMPTING" else res["pre"]["attribute_prompts_probs"]
		except Exception as e:
			# print(e)
			continue

		# race_probs = np.array(probs)[race_available] if len(race_available) > 0 else None
		# geo_probs = np.array(probs)[geo_available] if len(geo_available) > 0 else None
		if len(probs) != len (genders) or len(genders) != len(entities):
			print(f"case {case_id}")
			misfits.append(case_id)
			print(f"probs length {len(probs)}, genders length {len(genders)}, entities length {len(entities)}")
		men = [i for i in range(min(len(genders), len(probs), len(entities))) if match(genders[i], "Q6581097") or match(genders[i], "Q2449503")]
		women = [i for i in range(min(len(genders), len(probs), len(entities))) if match(genders[i], "Q6581072") or match(genders[i], "Q1052281")]
		by_race = {}
		'''
		for race in racial_groups:
			that_race = [i for i in race_available if match(races[i], race)]
			by_race[race] = that_race
		by_geo = {}
		for race in geo_groups:
			that_race = [i for i in geo_available if match(geos[i], race)]
			by_geo[race] = that_race
		'''
		def get_gender_breakdown(probs):
			men_probs = [probs[i] for i in men]
			women_probs = [probs[i] for i in women]
			men_probs_new = np.array([i["target_new"] for i in men_probs])
			women_probs_new = np.array([i["target_new"] for i in women_probs])
			men_probs_true = np.array([i["target_true"] for i in men_probs])
			women_probs_true = np.array([i["target_true"] for i in women_probs])
			plain_diff_men = np.exp(-men_probs_new) - np.exp(-men_probs_true)
			plain_diff_women = np.exp(-women_probs_new) - np.exp(-women_probs_true)
			return men_probs_new, women_probs_new, men_probs_true, women_probs_true, plain_diff_men, plain_diff_women
		def get_race_breakdown(probs, rp):
			diffs = {}
			try:
				for k, v in probs.items():
					those_probs = [rp[i] for i in v]
					true = np.array([i["target_true"] for i in those_probs])
					new = np.array([i["target_new"] for i in those_probs])
					diffs[k] = np.exp(-new) - np.exp(-true)
				return diffs
			except:
				return {}
		def get_kl(probs):
			men_probs = np.array([[np.exp(-probs[i]["target_new"]), np.exp(-probs[i]["target_true"]), 1 - np.exp(-probs[i]["target_new"]) - np.exp(-probs[i]["target_true"])] for i in men])
			women_probs = np.array([[np.exp(-probs[i]["target_new"]), np.exp(-probs[i]["target_true"]), 1 - np.exp(-probs[i]["target_new"]) - np.exp(-probs[i]["target_true"])] for i in women])
			men_mean = np.mean(men_probs, axis = 0)
			women_mean = np.mean(women_probs, axis = 0)
			return men_mean, women_mean
		def get_multi_kl(probs, rp):
			kls = {}
			try:
				for k, v in probs.items():
					those_probs = [rp[i] for i in v]
					probabilities = np.array([[np.exp(-i["target_new"]), np.exp(-i["target_true"]), 1 - np.exp(-i["target_new"]) - np.exp(-i["target_true"])] for i in those_probs])
					mean = np.mean(probabilities, axis = 0)
					kls[k] = mean
				return kls
			except:
				return {}
		# race_diffs = get_race_breakdown(by_race, probs)
		# race_kls = get_multi_kl(by_race, probs)
		'''
		for k, v in race_diffs.items():
			try:
				all_race_data[k] = np.concatenate((all_race_data[k], v))
			except:
				all_race_data[k] = v
		for k, v in race_diffs.items():
			try:
				all_race_means[k].append(v)
			except:
				all_race_means[k] = v
		geo_diffs = get_race_breakdown(by_geo,probs)
		geo_kls = get_multi_kl(by_geo, probs)
		for k, v in geo_diffs.items():
			try:
				all_geo_data[k] = np.concatenate((all_geo_data[k], v))
			except:
				all_geo_data[k] = v
		for k, v in geo_diffs.items():
			try:
				all_geo_means[k].append(v)
			except:
				all_geo_means[k] = v
		'''
		mn, wn, mt, wt, md, wd = get_gender_breakdown(probs)
		mm, wm = get_kl(probs)
		amn = np.concatenate((amn, mn))
		awn = np.concatenate((awn, wn))
		amt = np.concatenate((amt, mt))
		awt = np.concatenate((awt, wt))
		amd = np.concatenate((amd, md))
		awd = np.concatenate((awd, wd))
		amm.append(mm)
		awm.append(wm)
		
		with open(f"{presult_dir}1_edits-case_{case_id}.json") as result:
			pres = json.load(result)
		pre_probs = pres["pre"]["attribute_prompts_probs"]
		# race_pre_probs = np.array(pre_probs)[race_available] if len(race_available) > 0 else None
		# geo_pre_probs = np.array(pre_probs)[geo_available] if len(geo_available) > 0 else None
		# race_diffs_pre = get_race_breakdown(by_race, pre_probs)
		# race_kls_pre = get_multi_kl(by_race, pre_probs)
		'''
		for k, v in race_diffs_pre.items():
			try:
				all_race_data_pre[k] = np.concatenate((all_race_data_pre[k], v))
			except:
				all_race_data_pre[k] = v
		for k, v in race_diffs_pre.items():
			try:
				all_race_means_pre[k].append(v)
			except:
				all_race_means_pre[k] = v
		geo_diffs_pre = get_race_breakdown(by_geo, pre_probs)
		geo_kls_pre = get_multi_kl(by_geo, pre_probs)
		for k, v in geo_diffs_pre.items():
			try:
				all_geo_data_pre[k] = np.concatenate((all_geo_data_pre[k], v))
			except:
				all_geo_data_pre[k] = v
		for k, v in geo_diffs_pre.items():
			try:
				all_geo_means_pre[k].append(v)
			except:
				all_geo_means_pre[k] = v
		'''
		'''
		mnp, wnp, mtp, wtp, mdp, wdp = get_gender_breakdown(pre_probs)
		mmp, wmp = get_kl(pre_probs)
		amnp = np.concatenate((amnp, mnp))
		awnp = np.concatenate((awnp, wnp))
		amtp = np.concatenate((amtp, mtp))
		awtp = np.concatenate((awtp, wtp))
		amdp = np.concatenate((amdp, mdp))
		awdp = np.concatenate((awdp, wdp))
		ammp.append(mmp)
		awmp.append(wmp)
		metrics = {}
		metrics["neg_log_prob_diff_diffs_male"] = (md - mdp).tolist()
		metrics["neg_log_prob_diff_diffs_female"] = (wd - wdp).tolist()
		assert(len(md) == len(mdp))
		assert(len(wd) == len(wdp))
		metrics["kl_div_post"] = kl_divergence(mm, wm).tolist()
		metrics["kl_div_pre"] = kl_divergence(mmp, wmp).tolist()
		metrics["kl_div_male"] = kl_divergence(mm, mmp).tolist()
		metrics["kl_div_female"] = kl_divergence(wm, wmp).tolist()
		metrics["pre"] = {"mean_neg_log_prob_diff_male": np.mean(mdp),
						  "mean_neg_log_prob_diff_female": np.mean(wdp),
						  "stdev_neg_log_prob_diff_male": np.std(mdp),
						  "stdev_neg_log_prob_diff_female": np.std(wdp)}
		metrics["post"] = {"mean_neg_log_prob_diff_male": np.mean(md),
						  "mean_neg_log_prob_diff_female": np.mean(wd),
						  "stdev_neg_log_prob_diff_male": np.std(mdp),
						  "stdev_neg_log_prob_diff_female": np.std(wdp)}
		'''
		'''
		for race in racial_groups:
			try:
				metrics[f"neg_log_prob_diff_diffs_{race}"] = (race_diffs[race] - race_diffs_pre[race]).tolist()
				metrics[f"kl_div_{race}"] = kl_divergence(race_kls[race], race_kls_pre[race]).tolist()
				metrics["pre"][f"mean_neg_log_prob_diff_{race}"] = np.mean(race_diffs_pre[race])
				metrics["post"][f"mean_neg_log_prob_diff_{race}"] = np.mean(race_diffs[race])
				metrics["pre"][f"stdev_neg_log_prob_diff_{race}"] = np.std(race_diffs_pre[race])
				metrics["post"][f"stdev_neg_log_prob_diff_{race}"] = np.std(race_diffs[race])
			except Exception as e:
				# print("exception in diff diff calculation")
				# print(e)
				continue
		for race in geo_groups:
			try:
				metrics[f"neg_log_prob_diff_diffs_{race}"] = (geo_diffs[race] - geo_diffs_pre[race]).tolist()
				metrics[f"kl_div_{race}"] = kl_divergence(geo_kls[race], geo_kls_pre[race]).tolist()
				metrics["pre"][f"mean_neg_log_prob_diff_{race}"] = np.mean(geo_diffs_pre[race])
				metrics["post"][f"mean_neg_log_prob_diff_{race}"] = np.mean(geo_diffs[race])
				metrics["pre"][f"stdev_neg_log_prob_diff_{race}"] = np.std(geo_diffs_pre[race])
				metrics["post"][f"stdev_neg_log_prob_diff_{race}"] = np.std(geo_diffs[race])
			except Exception as e:
				# print("exception in diff diff calculation")
				# print(e)
				continue
		'''
		'''
		all_metrics.append({"case_id": case_id, 
							"subject": question["requested_rewrite"]["subject"],
							"target_new": question["requested_rewrite"]["target_new"],
							"target_true": question["requested_rewrite"]["target_true"],
							"metrics": metrics})
	overall_metrics["kl_div_post"] = kl_divergence(np.mean(amm, axis = 0), np.mean(awm, axis = 0)).tolist()
	overall_metrics["kl_div_pre"] = kl_divergence(np.mean(ammp, axis = 0), np.mean(awmp, axis = 0)).tolist()
	overall_metrics["kl_div_male"] = kl_divergence(np.mean(amm, axis = 0), np.mean(ammp, axis = 0)).tolist()
	overall_metrics["kl_div_female"] = kl_divergence(np.mean(awm, axis = 0), np.mean(awmp, axis = 0)).tolist()
	overall_metrics["pre"] = {"mean_neg_log_prob_diff_male": np.mean(amdp),
						  "mean_neg_log_prob_diff_female": np.mean(awdp),
						  "stdev_neg_log_prob_diff_male": np.std(amdp),
						  "stdev_neg_log_prob_diff_female": np.std(awdp)}
	overall_metrics["post"] = {"mean_neg_log_prob_diff_male": np.mean(amd),
						  "mean_neg_log_prob_diff_female": np.mean(awd),
						  "stdev_neg_log_prob_diff_male": np.std(amd),
						  "stdev_neg_log_prob_diff_female": np.std(awd)}
	'''
	'''
	for race in racial_groups:
			try:
				overall_metrics[f"neg_log_prob_diff_diffs_{race}"] = (all_race_data[race] - all_race_data_pre[race]).tolist()
				overall_metrics[f"kl_div_{race}"] = kl_divergence(all_race_means[race], all_race_means_pre[race]).tolist()
				overall_metrics["pre"][f"mean_neg_log_prob_diff_{race}"] = np.mean(all_race_data_pre[race])
				overall_metrics["post"][f"mean_neg_log_prob_diff_{race}"] = np.mean(all_race_data[race])
				overall_metrics["pre"][f"stdev_neg_log_prob_diff_{race}"] = np.std(all_race_data_pre[race])
				overall_metrics["post"][f"stdev_neg_log_prob_diff_{race}"] = np.std(all_race_data[race])
			except Exception as e:
				# print(e)
				continue
	for race in geo_groups:
		try:
			overall_metrics[f"neg_log_prob_diff_diffs_{race}"] = (all_geo_data[race] - all_geo_data_pre[race]).tolist()
			overall_metrics["pre"][f"mean_neg_log_prob_diff_{race}"] = np.mean(all_geo_data_pre[race])
			overall_metrics["post"][f"mean_neg_log_prob_diff_{race}"] = np.mean(all_geo_data[race])
			overall_metrics["pre"][f"stdev_neg_log_prob_diff_{race}"] = np.std(all_geo_data_pre[race])
			overall_metrics["post"][f"stdev_neg_log_prob_diff_{race}"] = np.std(all_geo_data[race])
		except Exception as e:
			# print(e)
			continue
	'''
	'''
	with open(f"../results/{p}_{method}.json", "w") as o:
		json.dump({"by_case:": all_metrics, "overall": overall_metrics}, o)
	'''
	print(len(the_question), len(misfits))

gen_metrics("P101", "../results/MEMIT/p101final/", 900, "../results/OG/p101/", "MEMIT")
# gen_metrics("P103", "../results/MEMIT/p103final/", 900, "../results/OG/p103/", "MEMIT")
# gen_metrics("P101", "../results/FT/p101/", 900, "../results/OG/p101/", "FT")
# gen_metrics("P103", "../results/FT/p103/", 900, "../results/OG/p103/", "FT")
# gen_metrics("P101", "../results/PROMPTING/p101/", 900, "../results/OG/p101/", "PROMPTING")
# gen_metrics("P103", "../results/PROMPTING/p103/", 900, "../results/OG/p103/", "PROMPTING")
# gen_metrics("P101", "../results/REMEDI/p101/", 900, "../results/OG/p101/", "REMEDI")
# gen_metrics("P103", "../results/REMEDI/p103/", 900, "../results/OG/p103/", "REMEDI")





