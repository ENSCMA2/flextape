import json
import random

def make_prompts(original, n = 16):
	with open(f"{original}.json") as o:
		original_data = json.load(o)
	demo_example_indices = random.sample([i for i in range(len(original_data))], n)
	data = [original_data[i] for i in range(len(original_data)) if i not in demo_example_indices]
	demo_examples = [original_data[i] for i in demo_example_indices]
	def example_to_prompt(example):
		rewrite = example["requested_rewrite"]
		return rewrite["prompt"].replace("{}", rewrite["subject"]) + f" {rewrite['target_new']['str']}."
	prefix = " ".join([example_to_prompt(e) for e in demo_examples])
	with open(f"{original}_prompting.json", "w") as o:
		json.dump({"prefix": prefix, "data": data}, o)

make_prompts("../data/seesaw_cf_P101_False_100")
make_prompts("../data/seesaw_cf_P103_False_100")