import wptools
import pandas as pd
import json

properties = ["P101", 
# "P103"
]

p101 = [# 'Q336', 'Q35127', 'Q309', 'Q11425', 'Q889', 'Q2743', 'Q75', 'Q11424', 
		# 'Q8087', 'Q808', 'Q7150', 'Q735', 'Q150', 'Q8274', 'Q2329', 'Q3863', 
		# 'Q841090', 'Q1412', 'Q5113', 'Q52', 'Q8341', 'Q11190', 'Q413', 'Q8134', 
		# 'Q12483', 'Q748', 'Q161598', 'Q188094', 'Q9465', 'Q1063', 'Q5891', 
		# 'Q132137', 'Q9129', 'Q41425', 'Q4116214', 'Q4964182', 'Q395', 'Q9288', 
		# 'Q23404', 'Q333', 'Q27939', 'Q1860', 'Q514', 'Q6625963', 'Q8078', 
		# 'Q36963', 'Q165950', 'Q1071', 'Q9268', 'Q39631', 'Q38112', 'Q9418', 
		# 'Q41217', 'Q5482740', 'Q36192', 'Q7252', 'Q21201', 'Q7162', 'Q11059', 
		# 'Q93184', 
		'Q3972943', 'Q17884', 'Q1344', 'Q765633', 
		'Q12271', 
		'Q521', 'Q7283', 
		'Q639669', 
		'Q193391', 'Q34178', 'Q3968', 
		'Q482', 'Q5885', 
		'Q1420', 
		'Q169470', 'Q614304', 
		'Q11633', 
		'Q40821', 
		'Q420', 'Q170790', 
		'Q9134', 'Q282129', 'Q3559']
p103 = [# 'Q9027', 'Q7913', 
'Q652', 'Q8108', 'Q188', 'Q1321', 'Q7411', 'Q9129', 
		'Q5287', 'Q7737', 'Q9299', 'Q5885', 'Q6654', 'Q150', 'Q397', 'Q9176', 
		'Q9067', 'Q9309', 'Q7850', 'Q9288', 'Q5146', 'Q8785', 'Q1568', 'Q1412', 
		'Q9240', 'Q9168', 'Q1860', 'Q809', 'Q256', 'Q9035']

props_dictionary = {"P101": p101, "P103": p103}

def create(qs, name):
	returned = {}
	def iterate(ppl, gender, prop, q):
		sub = {}
		for i, item in ppl.iterrows():
			cue = item["item"].split("/")[-1]
			try:
				page = wptools.page(wikibase = cue)
				try:
					wikidata = page.get_wikidata().data['claims']
					returned[item["item"]] = {"name": item["itemLabel"], "properties": wikidata}
					sub[item["item"]] = {"name": item["itemLabel"], "properties": wikidata}
				except:
					print(f"failed to get wikidata for {cue}")
			except:
				print(f"failed to get page for {cue}")
		with open(f"../data/{gender}_{prop}_{q}.json", "w") as o:
			json.dump(sub, o)
	for prop in properties:
		for q in qs[prop]:
			try: 
				people = pd.read_csv("../Ingredients/" +  "00_" + prop + "_" + q + ".csv")
				print("success for", q, "00")
				iterate(people, "00", prop, q)
				people = pd.read_csv("../Ingredients/" +  "01_" + prop + "_" + q + ".csv")
				print("success for", q, "01")
				iterate(people, "01", prop, q)
			except:
				print(q, "not found")
	with open(f"../data/{name}.json", "w") as o:
		json.dump(returned, o)
	return returned

# create(props_dictionary, "P101_P103")
create({"P101": p101}, "P101")