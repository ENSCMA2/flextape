import json
import numpy as np
from scipy.special import kl_div

wiki_prefix = "http://www.wikidata.org/entity/"

def gen_metrics(p, result_dir, n, presult_dir):
	p_file = f"../data/seesaw_cf_{p}_False_100.json"
	all_metrics = []
	with open(p_file) as o:
		the_question = json.load(p_file)
	wiki_info = f"../data/{p}.json"
	with open(wiki_info) as wi:
		wiki = json.load(wi)
	for question in the_question:
		case_id = question["case_id"]
		entities = question["attribute_aux_ent"]
		q = question["requested_rewrite"]["target_new"]["id"]
		genders = [wiki[f"{wiki_prefix}{subj}"]["properties"]["P21"] for subj in entities]
		men = [i for i in range(len(genders)) if genders[i] == "Q6581097"]
		women = [i for i in range(len(genders)) if genders[i] == "Q6581072"]
		with open(f"{results_dir}{n}_edits-case_{case_id}.json") as result:
			res = json.load(result)
		probs = res["post"]["attribute_prompts_probs"]
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
		with open(f"{presults_dir}1_edits-case_{case_id}.json") as result:
			pres = json.load(result)
		pre_probs = res["pre"]["attribute_prompts_probs"]
		mnp, wnp, mtp, wtp, mdp, wdp = get_gender_breakdown(pre_probs)

		metrics = {}
		metrics["neg_log_prob_diff_diffs_male"] = md - mdp
		metrics["neg_log_prob_diff_diffs_female"] = wd - wdp
		metrics["kl_div_male"] = kl_div(md, mdp)
		metrics["kl_div_female"] = kl_div(wd, wdp)
		metrics["kl_div"] = kl_div(md - mdp, wd - wdp)
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
							"target_new": question["requested_rewrite"]["target_new"]
							"target_true": question["requested_rewrite"]["target_true"]
							"metrics": metrics})
	with open(f"results/{p}.json", "w") as o:
		json.dump(all_metrics, o)

gen_metrics("P101", "../results/MEMIT/p101/", 898, "../results/NONE/p101/")
gen_metrics("P103", "../results/MEMIT/p103/", 898, "../results/NONE/p103/")
gen_metrics("P101", "../results/FT/p101/", 898, "../results/NONE/p101/")
gen_metrics("P103", "../results/FT/p103/", 898, "../results/NONE/p103/")
		




