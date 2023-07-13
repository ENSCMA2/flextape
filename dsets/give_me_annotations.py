import json
import pandas as pd
from itertools import *

ing = "/Users/khalevy/Downloads/CF_Ingredients"
def gen_annotation_template(prop):
	with open(f"{ing}/Human_CF/human_counterfact_{prop}.json") as o:
		refs = json.load(o)
	ids = list(chain(*[[item["case_id"]] * 20 for item in refs if item["case_id"] <= 1530]))
	print(ids, len(ids))
	ids_once = [item["case_id"] for item in refs]
	prepost = []
	texts = []
	true_targets = []
	new_targets = []
	for iD in ids_once:
		if iD <= 1530:
			with open(f"/Users/khalevy/Downloads/run2/case_{iD}.json") as o:
				ref = json.load(o)
			texts.extend(ref["post"]["text"] + ref["pre"]["text"])
			true_targets.extend([ref["requested_rewrite"]["target_true"]['str']] * 20)
			new_targets.extend([ref["requested_rewrite"]["target_new"]['str']] * 20)
			prepost.extend(["post"] * 10 + ["pre"] * 10)
	out = pd.DataFrame()
	out["target_new"] = new_targets
	out["target_true"] = true_targets
	out["text"] = texts
	out["pre_or_post"] = prepost
	out["case_id"] = ids
	out.to_csv(f"{ing}/data/annotations_{prop}.csv")

# gen_annotation_template("P103")
# gen_annotation_template("P101")

def gen_custom_annotation_template():
	es = [('Gwen Stefani', 112), ('Kim Philby', 2061), ('Lindsey Davis', 2074), ('Alex Ferguson', 2404), ('Brian May', 2611), ('William Butler Yeats', 2784), ('John Dalton', 4006), ('Daniel Tammet', 4774), ('Thomas Horsfield', 4871), ('Walter Pater', 5350), ('Arthur Conan Doyle', 5614), ('Bertrand Russell', 5851), ('Frederick Marryat', 6070), ('Julie Myerson', 6320), ('Edward Burnett Tylor', 6634), ('Theodore Roosevelt', 7049), ('Herbert Edward Read', 7941), ('James A. Garfield', 8161), ('David Beckham', 8285), ('Donald Keene', 11050), ('Sara Coleridge', 11054), ('Tina Turner', 11123), ('Norman Rockwell', 11400), ('John Quincy Adams', 11683), ('Woodrow Wilson', 11941), ('William Howitt', 12048), ('Andrew Jackson', 12551), ('John Webster', 12945), ('Bam Margera', 12975), ('J. Robert Oppenheimer', 13432), ('Geoff Dyer', 13560), ('John Ruskin', 13796), ('Douglas Adams', 14292), ('Christopher Smart', 14452), ('Jenson Button', 14617), ('Vera Lynn', 15009), ('Gough Whitlam', 15297), ('Andrew Lang', 15410), ('William Henry Harrison', 16556), ('Barack Obama', 16587), ('Michael of Romania', 16597), ('Michael Albert', 16615), ('Seamus Heaney', 16814), ('Virginia Woolf', 17182), ('Zachary Taylor', 18037), ('William Habington', 18583), ('John Abraham Heraud', 19019), ('John Stuart Mill', 19294), ('John Banville', 20207), ('Adam Sandler', 20320), ('Al Gore', 20597), ('Edward Bulwer-Lytton', 20837), ('Andy Murray', 20965)]
	ids = list(chain(*[[j] * 20 for (i, j) in es]))
	prepost = []
	texts = []
	true_targets = []
	new_targets = []
	for (name, identification) in es:
		with open(f"/Users/khalevy/Downloads/americans/case_{identification}.json") as o:
			ref = json.load(o)
			texts.extend(ref["post"]["text"] + ref["pre"]["text"])
			true_targets.extend([ref["requested_rewrite"]["target_true"]['str']] * 20)
			new_targets.extend([ref["requested_rewrite"]["target_new"]['str']] * 20)
			prepost.extend(["post"] * 10 + ["pre"] * 10)
	out = pd.DataFrame()
	out["target_new"] = new_targets
	out["target_true"] = true_targets
	out["text"] = texts
	out["pre_or_post"] = prepost
	out["case_id"] = ids
	out.to_csv(f"/Users/khalevy/Downloads/americans/all_english.csv")

gen_custom_annotation_template()