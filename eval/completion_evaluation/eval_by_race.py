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

wiki_prefix = "http://www.wikidata.org/entity/"
props = ["P101", "P103", "P101_P21", "P21_P101", 
"P27_P21", "P27_P101", "P101_P27", "P19_P21", "P19_P101", "P27_P19"]
race_dfs = [pd.read_csv(f"../../data/Ethnic Groups - {prop}.csv").fillna("") for prop in props]
def intersection_list(lol):
	initial = set(lol[0])
	for i in range(1, len(lol)):
		initial = initial.intersection(lol[i])
	return initial

racial_groups = intersection_list([df["Racial Group"].tolist() for df in race_dfs])
racial_groups.remove("")
geo_groups = intersection_list([df["Geo Group"].tolist() for df in race_dfs])
geo_groups.remove("")

def kl_divergence(p, q):
	return np.sum(np.where(p != 0, p * np.log(p / q), 0))

def convert(race, df):
	dictionary = {item["Code"]: item["Racial Group"] for i, item in df.iterrows() if item["Racial Group"] != ""}
	if type(race) == str:
		return [dictionary[race]]
	else:
		return [dictionary[r] for r in race if r in dictionary.keys()]

def convert_geo(race, df):
	dictionary = {item["Code"]: item["Geo Group"] for i, item in df.iterrows() if item["Geo Group"] != ""}
	if type(race) == str:
		return [dictionary[race]] if race in dictionary.keys() else []
	else:
		return [dictionary[r] for r in race if r in dictionary.keys()]

def gen_metrics(p, result_dir, n, presult_dir, method, pdf, patch = False,):
	if not os.path.exists(f"../results/{p}/race/{method}.json"):
		misfits = []
		print(p, method)
		p_file = f"../../data/seesaw_cf_{p}.json"
		race_df = {item["Code"]: item["Racial Group"] for i, item in pdf.iterrows() if item["Racial Group"] != ""}
		geo_df = {item["Code"]: item["Racial Group"] for i, item in pdf.iterrows() if item["Geo Group"] != ""}
		all_metrics = []
		overall_metrics = {"pre": {}, "post": {}}
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
		for j, question in enumerate(the_question):
			case_id = question["case_id"]
			entities = question["attribute_aux_info"]
			q = question["requested_rewrite"]["target_new"]["id"]
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
			race_available = []
			races = []

			def lookup(subj, dem):
				try:
					pr = wiki[f"{entities[subj]}"]["properties"]
					if dem in pr.keys():
						return pr[dem], True
					else:
						return None, False
				except:
					if os.path.exists(f"../../data/wiki/person_{subj}.json"):
						with open(f"../../data/wiki/person_{subj}.json") as o:
							pr = json.load(o)["properties"]
							if dem in pr.keys():
								return pr[dem], True
							else:
								return None, False
					try:
						page = wptools.page(wikibase = subj, silent = True)
						wikidata = page.get_wikidata(show = False).data
						person = {"name": wikidata["label"], "properties": wikidata["claims"]}
						with open(f"../../data/wiki/person_{subj}.json", "w") as o:
							json.dump(person, o)
						pr = person["properties"]
						if dem in pr.keys():
							return pr[dem], True
						else:
							print("eh")
							return None, False
					except Exception as e:
						print("wah", e)
						return None, False
			
			for i in range(len(entities)):
				print(i, len(entities), j, len(the_question))
				some = False
				mini_race = []
				trait, found = lookup(entities[i], "P172")
				if found:
					for keys in trait:
						if keys in race_df.keys():
							mini_race.extend(convert(keys, pdf))
							some = True
					if some:
						race_available.append(i)
				races.append(mini_race)
			race_available = np.array(race_available)

			geo_available = []
			geos = []
			for i in range(len(entities)):
				mini_race = []
				trait, found = lookup(entities[i], "P172")
				if found:
					some = False
					for keys in trait:
						if keys in geo_df.keys():
							mini_race.extend(convert_geo(keys, pdf))
							some = True
					if some:
						geo_available.append(i)
				geos.append(mini_race)
			geo_available = np.array(geo_available)
			
			def match(prop, hope):
				if type(prop) == list:
					return hope in prop
				if type(prop) == str:
					return hope == prop
				return False
			try:
				with open(f"{result_dir}{n}_edits-case_{case_id}.json") as result:
					res = json.load(result)
				probs = res["post"]["attribute_prompts_probs"]
			except Exception as e:
				print(e)
				continue

			race_probs = np.array(probs)[race_available] if len(race_available) > 0 else None
			geo_probs = np.array(probs)[geo_available] if len(geo_available) > 0 else None
			if len(probs) != len(entities):
				print(f"case {case_id}")
				misfits.append(case_id)
				print(f"probs length {len(probs)}, entities length {len(entities)}")
			
			by_race = {}
			
			for race in racial_groups:
				that_race = [i for i in race_available if match(races[i], race)]
				by_race[race] = that_race
			by_geo = {}
			for race in geo_groups:
				that_race = [i for i in geo_available if match(geos[i], race)]
				by_geo[race] = that_race

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

			def get_multi_kl(probs, rp):
				kls = {}
				try:
					for k, v in probs.items():
						those_probs = [rp[i] for i in v]
						probabilities = np.array([[np.exp(-i["target_new"]), np.exp(-i["target_true"]), 1 - np.exp(-i["target_new"]) - np.exp(-i["target_true"])] for i in those_probs])
						if len(probabilities) > 0:
							mean = np.mean(probabilities, axis = 0)
							kls[k] = mean
					return kls
				except:
					return {}
			race_diffs = get_race_breakdown(by_race, probs)
			race_kls = get_multi_kl(by_race, probs)
			for k, v in race_diffs.items():
				try:
					all_race_data[k] = np.concatenate((all_race_data[k], v))
				except:
					all_race_data[k] = v
			for k, v in race_kls.items():
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
			for k, v in geo_kls.items():
				try:
					all_geo_means[k].append(v)
				except:
					all_geo_means[k] = v
			
			with open(f"{presult_dir}{n}_edits-case_{case_id}.json") as result:
				pres = json.load(result)
			pre_probs = pres["pre"]["attribute_prompts_probs"]
			race_pre_probs = np.array(pre_probs)[race_available] if len(race_available) > 0 else None
			geo_pre_probs = np.array(pre_probs)[geo_available] if len(geo_available) > 0 else None
			race_diffs_pre = get_race_breakdown(by_race, pre_probs)
			race_kls_pre = get_multi_kl(by_race, pre_probs)

			for k, v in race_diffs_pre.items():
				try:
					all_race_data_pre[k] = np.concatenate((all_race_data_pre[k], v))
				except:
					all_race_data_pre[k] = v
			for k, v in race_kls_pre.items():
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
			for k, v in geo_kls_pre.items():
				try:
					all_geo_means_pre[k].append(v)
				except:
					all_geo_means_pre[k] = v
			metrics = {"pre": {}, "post": {}}
			for race in racial_groups:
				try:
					if len(race_diffs[race]) > 0 and len(race_diffs_pre[race]) > 0:
						metrics[f"neg_log_prob_diff_diffs_{race}"] = (race_diffs[race] - race_diffs_pre[race]).tolist()
						if len(race_kls[race]) > 0 and len(race_kls_pre[race]) > 0:
							metrics[f"kl_div_{race}"] = kl_divergence(race_kls[race], race_kls_pre[race]).tolist()
						metrics["pre"][f"mean_neg_log_prob_diff_{race}"] = np.mean(race_diffs_pre[race])
						metrics["post"][f"mean_neg_log_prob_diff_{race}"] = np.mean(race_diffs[race])
						metrics["pre"][f"stdev_neg_log_prob_diff_{race}"] = np.std(race_diffs_pre[race])
						metrics["post"][f"stdev_neg_log_prob_diff_{race}"] = np.std(race_diffs[race])
				except Exception as e:
					print(e)
					continue
			for race in geo_groups:
				try:
					if len(geo_diffs[race]) > 0 and len(geo_diffs_pre[race]) > 0:
						metrics[f"neg_log_prob_diff_diffs_{race}"] = (geo_diffs[race] - geo_diffs_pre[race]).tolist()
						if len(geo_kls[race]) > 0 and len(geo_kls_pre[race]) > 0:
							metrics[f"kl_div_{race}"] = kl_divergence(geo_kls[race], geo_kls_pre[race]).tolist()
						metrics["pre"][f"mean_neg_log_prob_diff_{race}"] = np.mean(geo_diffs_pre[race])
						metrics["post"][f"mean_neg_log_prob_diff_{race}"] = np.mean(geo_diffs[race])
						metrics["pre"][f"stdev_neg_log_prob_diff_{race}"] = np.std(geo_diffs_pre[race])
						metrics["post"][f"stdev_neg_log_prob_diff_{race}"] = np.std(geo_diffs[race])
				except Exception as e:
					print(e)
					continue

			all_metrics.append({"case_id": case_id, 
								"subject": question["requested_rewrite"]["subject"],
								"target_new": question["requested_rewrite"]["target_new"],
								"target_true": question["requested_rewrite"]["target_true"],
								"metrics": metrics})

		for race in racial_groups:
			if len(all_race_data_pre[race]) > 0 and len(all_race_data[race]) > 0:
				overall_metrics[f"neg_log_prob_diff_diffs_{race}"] = (all_race_data[race] - all_race_data_pre[race]).tolist()
				if (len(all_race_means[race]) > 0) and len(all_race_means_pre[race]) > 0:
					print(f"divergencing all race data {race}")
					overall_metrics[f"kl_div_{race}"] = kl_divergence(all_race_means[race], all_race_means_pre[race]).tolist()
				overall_metrics["pre"][f"mean_neg_log_prob_diff_{race}"] = np.mean(all_race_data_pre[race])
				overall_metrics["post"][f"mean_neg_log_prob_diff_{race}"] = np.mean(all_race_data[race])
				overall_metrics["pre"][f"stdev_neg_log_prob_diff_{race}"] = np.std(all_race_data_pre[race])
				overall_metrics["post"][f"stdev_neg_log_prob_diff_{race}"] = np.std(all_race_data[race])
		for race in geo_groups:
			if len(all_geo_data_pre[race]) > 0 and len(all_geo_data[race]) > 0:
				overall_metrics[f"neg_log_prob_diff_diffs_{race}"] = (all_geo_data[race] - all_geo_data_pre[race]).tolist()
				if (len(all_geo_means[race]) > 0) and len(all_geo_means_pre[race]) > 0:
					overall_metrics[f"kl_div_{race}"] = kl_divergence(all_geo_means[race], all_geo_means_pre[race]).tolist()
				overall_metrics["pre"][f"mean_neg_log_prob_diff_{race}"] = np.mean(all_geo_data_pre[race])
				overall_metrics["post"][f"mean_neg_log_prob_diff_{race}"] = np.mean(all_geo_data[race])
				overall_metrics["pre"][f"stdev_neg_log_prob_diff_{race}"] = np.std(all_geo_data_pre[race])
				overall_metrics["post"][f"stdev_neg_log_prob_diff_{race}"] = np.std(all_geo_data[race])
		model = sys.argv[1]
		if not os.path.isdir(f"../../results/{model}/{p}"):
			os.mkdir(f"../../results/{model}/{p}")
		if not os.path.isdir(f"../../results/{model}/{p}/race"):
			os.mkdir(f"../../results/{model}/{p}/race")
		with open(f"../../results/{model}/{p}/race/{method}.json", "w") as o:
			json.dump({"by_case:": all_metrics, "overall": overall_metrics}, o)

model = sys.argv[1]
method = sys.argv[2]
for i, p in enumerate(["P101", "P103", 
		  "P21_P101",
		  "P27_P101", "P19_P101",
		  ]):
	gen_metrics(p, f"../../results/{model}/{method}/", 900, f"../../results/{model}/NONE/", method, race_dfs[i])