import json
import numpy as np
from scipy.special import kl_div
from itertools import *
from collections import Counter

wiki_prefix = "http://www.wikidata.org/entity/"

def gen_metrics(p, result_dir, n, presult_dir, method, patch = False,):
	p_file = f"../data/seesaw_cf_{p}_False_100.json"
	all_metrics = []
	overall_metrics = {}
	amn, awn, amt, awt, amd, awd = np.array([]), np.array([]), np.array([]), np.array([]), np.array([]), np.array([])
	amnp, awnp, amtp, awtp, amdp, awdp = np.array([]), np.array([]), np.array([]), np.array([]), np.array([]), np.array([])
	with open(p_file) as o:
		the_question = json.load(o)
	if method == "REMEDI":
		with open(f"{result_dir}paraphrase.json") as o:
			res = json.load(o)
			res = res["samples"]
	race = []
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
		races = list(chain(*[wiki[f"{wiki_prefix}{subj}"]["properties"]["P172"] for subj in entities if "P172" in wiki[f"{wiki_prefix}{subj}"]["properties"].keys()]))
		race.extend(races)
	ctr = Counter(race)
	with open(f"../results/race_{method}_{p}.txt", "w") as o:
		json.dump({k: v for k, v in sorted(dict(ctr).items(), key = lambda x: x[1], reverse = True)}, o)
		'''
		if method != "REMEDI":
			try:
				with open(f"{result_dir}{n}_edits-case_{case_id}.json") as result:
					res = json.load(result)
				probs = res["post"]["attribute_prompts_probs"] if method != "PROMPTING" else res["pre"]["attribute_prompts_probs"]
				if patch:
					with open(f"{result_dir}10000_edits-case_{case_id}.json") as result:
						res2 = json.load(result)
					probs.extend(res2["post"]["attribute_prompts_probs"])
			except Exception as e:
				print(e)
				continue
		else:
			relevant_res = [r for r in res if r["id"] == str(case_id)]
			if len(relevant_res) == 0:
				continue
			interm = list(chain(*[r["prompts"] for r in relevant_res]))
			probs = [{"target_new": p["target_score"], "target_true": p["comparator_score"]} for p in interm]
		print(f"probs length {len(probs)}, genders length {len(genders)}, entities length {len(entities)}")
		men = [i for i in range(min(len(genders), len(probs), len(entities))) if match(genders[i], "Q6581097") or match(genders[i], "Q2449503")]
		women = [i for i in range(min(len(genders), len(probs), len(entities))) if match(genders[i], "Q6581072") or match(genders[i], "Q1052281")]
		def get_gender_breakdown(probs):
			men_probs = [probs[i] for i in men]
			women_probs = [probs[i] for i in women]
			men_probs_new = np.array([i["target_new"] for i in men_probs])
			women_probs_new = np.array([i["target_new"] for i in women_probs])
			men_probs_true = np.array([i["target_true"] for i in men_probs])
			women_probs_true = np.array([i["target_true"] for i in women_probs])
			plain_diff_men = men_probs_new - men_probs_true
			plain_diff_women = women_probs_new - women_probs_true
			return men_probs_new, women_probs_new, men_probs_true, women_probs_true, plain_diff_men, plain_diff_women
		mn, wn, mt, wt, md, wd = get_gender_breakdown(probs)
		amn = np.concatenate((amn, mn))
		awn = np.concatenate((awn, wn))
		amt = np.concatenate((amt, mt))
		awt = np.concatenate((awt, wt))
		amd = np.concatenate((amd, md))
		awd = np.concatenate((awd, wd))
		with open(f"{presult_dir}1_edits-case_{case_id}.json") as result:
			pres = json.load(result)
		pre_probs = pres["pre"]["attribute_prompts_probs"]
		if patch:
			with open(f"{presult_dir}10000_edits-case_{case_id}.json") as result:
				pres2 = json.load(result)
			pre_probs += pres2["pre"]["attribute_prompts_probs"]
		mnp, wnp, mtp, wtp, mdp, wdp = get_gender_breakdown(pre_probs)
		amnp = np.concatenate((amnp, mnp))
		awnp = np.concatenate((awnp, wnp))
		amtp = np.concatenate((amtp, mtp))
		awtp = np.concatenate((awtp, wtp))
		amdp = np.concatenate((amdp, mdp))
		awdp = np.concatenate((awdp, wdp))
		# take top 4 or 5 ethnic groups

		metrics = {}
		metrics["neg_log_prob_diff_diffs_male"] = (md - mdp).tolist()
		metrics["neg_log_prob_diff_diffs_female"] = (wd - wdp).tolist()
		metrics["kl_div_male"] = kl_div(np.exp(-md), np.exp(-mdp)).tolist()
		metrics["kl_div_female"] = kl_div(np.exp(-wd), np.exp(-wdp)).tolist()
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
	overall_metrics["kl_div_male"] = kl_div(np.exp(-amd), np.exp(-amdp)).tolist()
	overall_metrics["kl_div_female"] = kl_div(np.exp(-awd), np.exp(-awdp)).tolist()
	overall_metrics["pre"] = {"mean_neg_log_prob_diff_male": np.mean(amdp),
						  "mean_neg_log_prob_diff_female": np.mean(awdp),
						  "stdev_neg_log_prob_diff_male": np.std(amdp),
						  "stdev_neg_log_prob_diff_female": np.std(awdp)}
	overall_metrics["post"] = {"mean_neg_log_prob_diff_male": np.mean(amd),
						  "mean_neg_log_prob_diff_female": np.mean(awd),
						  "stdev_neg_log_prob_diff_male": np.std(amdp),
						  "stdev_neg_log_prob_diff_female": np.std(awdp)}
	with open(f"../results/{p}_{method}.json", "w") as o:
		json.dump({"by_case:": all_metrics, "overall": overall_metrics}, o)
	'''
gen_metrics("P101", "../results/MEMIT/p101final/", 898, "../results/OG/p101/", "MEMIT", patch = True)
gen_metrics("P103", "../results/MEMIT/p103final/", 898, "../results/OG/p103/", "MEMIT")
gen_metrics("P101", "../results/FT/p101/", 898, "../results/OG/p101/", "FT", patch = True)
gen_metrics("P103", "../results/FT/p103/", 898, "../results/OG/p103/", "FT")
gen_metrics("P101", "../results/PROMPTING/p101/", 1, "../results/OG/p101/", "PROMPTING", patch = True)
gen_metrics("P103", "../results/PROMPTING/p103/", 1, "../results/OG/p103/", "PROMPTING")
gen_metrics("P101", "../results/REMEDI/p101/linear/1/", 1, "../results/OG/p101/", "REMEDI", patch = True)
gen_metrics("P103", "../results/REMEDI/p103/linear/1/", 1, "../results/OG/p103/", "REMEDI")




