import json

def fix_generations(original):
	with open(original, "r+") as o:
		original_list = json.load(o)
	for i in range(len(original_list)):
		prompts = list(set(original_list[i]["generation_prompts"])) * 5
		original_list[i]["generation_prompts"] = prompts
	with open(original, "w+") as o:
		json.dump(original_list, o)

# fix_generations("/Users/khalevy/Documents/Git/flextape/data/seesaw_cf_P103_False.json")
fix_generations("../data/seesaw_cf_P101_False_100.json")
fix_generations("../data/seesaw_cf_P103_False_100.json")