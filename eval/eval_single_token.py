import json
import numpy as np
from scipy.special import kl_div
from itertools import *
import pandas as pd
import copy

wiki_prefix = "http://www.wikidata.org/entity/"

def kl_divergence(p, q):
    return np.sum(np.where(p != 0, p * np.log(p / q), 0))

def gen_metrics(p, result_dir, n, presult_dir, method, patch = False,):
	misfits = []
	print(p, method)
	p_file = f"../data/seesaw_cf_{p}_False_100.json"
	all_metrics = []
	overall_metrics = {}
	amn, awn, amt, awt, amd, awd = np.array([]), np.array([]), np.array([]), np.array([]), np.array([]), np.array([])
	amnp, awnp, amtp, awtp, amdp, awdp = np.array([]), np.array([]), np.array([]), np.array([]), np.array([]), np.array([])
	amm, awm, ammp, awmp = [], [], [], []

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
			probs = res["post"]["attribute_prompts_probs"]
		except Exception as e:
			# print(e)
			continue

		if len(probs) != len (genders) or len(genders) != len(entities):
			print(f"case {case_id}")
			misfits.append(case_id)
			print(f"probs length {len(probs)}, genders length {len(genders)}, entities length {len(entities)}")
		men = [i for i in range(len(genders)) if match(genders[i], "Q6581097") or match(genders[i], "Q2449503")]
		women = [i for i in range(len(genders)) if match(genders[i], "Q6581072") or match(genders[i], "Q1052281")]
		
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

		def get_kl(probs):
			men_probs = np.array([[np.exp(-probs[i]["target_new"]), np.exp(-probs[i]["target_true"]), 1 - np.exp(-probs[i]["target_new"]) - np.exp(-probs[i]["target_true"])] for i in men])
			women_probs = np.array([[np.exp(-probs[i]["target_new"]), np.exp(-probs[i]["target_true"]), 1 - np.exp(-probs[i]["target_new"]) - np.exp(-probs[i]["target_true"])] for i in women])
			men_mean = np.mean(men_probs, axis = 0)
			women_mean = np.mean(women_probs, axis = 0)
			return men_mean, women_mean

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
		
		with open(f"{presult_dir}{n}_edits-case_{case_id}.json") as result:
			pres = json.load(result)
		pre_probs = pres["pre"]["attribute_prompts_probs"]

		
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
	
	with open(f"../results/{p}_{method}_gender.json", "w") as o:
		json.dump({"by_case:": all_metrics, "overall": overall_metrics}, o)
	print(len(the_question), len(misfits))

gen_metrics("P101", "../results/MEMIT/", 900, "../results/OG/", "MEMIT")
# gen_metrics("P103", "../results/MEMIT/", 900, "../results/OG/", "MEMIT")
gen_metrics("P101", "../results/FT/", 900, "../results/OG/", "FT")
# gen_metrics("P103", "../results/FT/", 900, "../results/OG/", "FT")
gen_metrics("P101", "../results/REMEDI/", 900, "../results/OG/", "REMEDI")
# gen_metrics("P103", "../results/REMEDI/", 900, "../results/OG/", "REMEDI")





