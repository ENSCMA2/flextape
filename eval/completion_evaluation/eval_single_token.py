import json
import numpy as np
from scipy.special import kl_div
from itertools import *
import pandas as pd
import copy
import os
import sys
import wptools
import requests

model = sys.argv[1]
method = sys.argv[2]

wiki_prefix = "http://www.wikidata.org/entity/"

def kl_divergence(p, q):
	return np.sum(np.where(p != 0, p * np.log(p / q), 0))

def gen_metrics(p, result_dir, n, presult_dir, method, patch = False,):
	print(p)
	if not os.path.exists(f"../../results/{p}/gender/{method}.json"):
		total_bad = 0
		total_entities = 0
		misfits = []
		p_file = f"../../data/seesaw_cf_{p}.json"
		all_metrics = []
		overall_metrics = {}
		amn, awn, amt, awt, amd, awd = np.array([]), np.array([]), np.array([]), np.array([]), np.array([]), np.array([])
		amnp, awnp, amtp, awtp, amdp, awdp = np.array([]), np.array([]), np.array([]), np.array([]), np.array([]), np.array([])
		amm, awm, ammp, awmp = [], [], [], []

		with open(p_file) as o:
			the_question = json.load(o)
		for j, question in enumerate(the_question):
			case_id = question["case_id"]
			entities = question["attribute_aux_info"]
			total_entities += len(set(entities))
			q = question["requested_rewrite"]["target_new"]["id"]
			if p.split("_")[0] != "P21":
				if p in ["P101", "P103"]:
					wiki_q_0 = f"../../data/wiki/Q6581072_{p}_{q}.json"
					wiki_q_1 = f"../../data/wiki/Q6581097_{p}_{q}.json"
				else:
					p1 = p.split("_")[0]
					wiki_q_0 = f"../../data/wiki/Q6581072_{p1}_{q}.json"
					wiki_q_1 = f"../../data/wiki/Q6581097_{p1}_{q}.json"
				with open(wiki_q_0) as o1:
					info_0 = json.load(o1)
				with open(wiki_q_1) as o1:
					info_1 = json.load(o1)
				wiki = {**info_0, **info_1}
			else:
				wiki = {}
				men = "../../data/P172/men"
				women = "../../data/P172/women"
				for f in os.listdir(men):
					with open(os.path.join(men, f)) as o:
						wiki = {**wiki, **json.load(o)}
				for f in os.listdir(women):
					with open(os.path.join(women, f)) as o:
						wiki = {**wiki, **json.load(o)}

			def match(prop, hope):
				if type(prop) == list:
					return hope in prop
				if type(prop) == str:
					return hope == prop
				return False
			def lookup(subj, dem):
				# print(subj, dem)
				def process(que):
					if "Q6581072" in que:
						return "Q6581072"
					if "Q6581097" in que:
						return "Q6581097"
					return "None"
				try:
					proc = process(wiki[subj]["properties"][dem])
					return proc
				except:
					if os.path.exists(f"../../data/wiki/person_{subj}.json"):
						with open(f"../../data/wiki/person_{subj}.json") as o:
							loaded = json.load(o)["properties"]
							if dem in loaded.keys():
								return process(loaded[dem])
							return "None"
					try:
						page = wptools.page(wikibase = subj, silent = True)
						wikidata = page.get_wikidata(show = False).data
						person = {"name": wikidata["label"], "properties": wikidata["claims"]}
						with open(f"../../data/wiki/person_{subj}.json", "w") as o:
							json.dump(person, o)
						if dem in person["properties"].keys():
							return process(person["properties"][dem])
						return "None"
					except Exception as e:
						return "None"

			genders = []
			for i, subj in enumerate(entities):
				genders.append(lookup(subj, "P21"))
				# print(j, len(the_question), i, len(entities))
			valid = [i for i in range(len(genders)) if genders[i] != "None"]
			valid_genders = np.array(genders)[valid]
			print("valid genders length", len(valid_genders))
			try:
				with open(f"{result_dir}{n}_edits-case_{case_id}.json") as result:
					res = json.load(result)
				print(res["post"])
				probs = res["post"]["attribute_prompts_probs"]
				print(type(probs), len(probs))
				probs = np.array(probs)[valid]
			except Exception as e:
				print("probs not loaded")
				print(e)
				continue
			men = []
			women = []
			for i in range(len(valid_genders)):
				v = str(valid_genders[i])
				m = match(v, "Q6581097") or match(v, "Q2449503")
				w = match(v, "Q6581072") or match(v, "Q1052281")
				if m:
					men.append(i)
				if w:
					women.append(i)
			# print("women length:", len(women))
			# print("men length:", len(men))
			
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
			pre_probs = np.array(pres["pre"]["attribute_prompts_probs"])[valid]

			
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
		if not os.path.isdir(f"../../results/{model}/{p}"):
			os.mkdir(f"../../results/{model}/{p}")
		if not os.path.isdir(f"../../results/{model}/{p}/gender"):
			os.mkdir(f"../../results/{model}/{p}/gender")
		with open(f"../../results/{model}/{p}/gender/{method}.json", "w") as o:
			json.dump({"by_case:": all_metrics, "overall": overall_metrics}, o)
		print(total_bad, total_entities)

for p in [# "P101", "P103", 
		  # "P101_P21", 
		  "P27_P21", 
		  "P27_P101", "P101_P27", "P19_P21", "P19_P101", "P27_P19"
		  ]:
	gen_metrics(p, f"../../results/{method}/", 900 + len(p.split("_")) - 1, f"../../results/NONE/", method)


