import json
import pandas as pd
import jsonlines
import random

def json_to_jsonl(og, new_name):
    with open(og) as o:
        original = json.load(o)
    ultimate = []
    for stuff in original:
        prompt_temp = stuff["requested_rewrite"]["prompt"]
        prompt = prompt_temp.replace("{}", stuff["requested_rewrite"]["subject"])
        response = stuff["requested_rewrite"]["target_new"]["str"]
        ultimate.append({"prompt": prompt, "response": response})
    train = random.sample([i for i in range(len(ultimate))], int(len(ultimate) * 0.75))
    ultimate_train = [ultimate[i] for i in train]
    ultimate_val = [ultimate[i] for i in range(len(ultimate)) if i not in train]
    with open(f"{new_name}_train.jsonl", "w") as o:
        for stuff in ultimate_train:
            o.write(str(stuff) + "\n")
    with open(f"{new_name}_val.jsonl", "w") as o:
        for stuff in ultimate_val:
            o.write(str(stuff) + "\n")

json_to_jsonl("../data/seesaw_cf_P101_False_100.json", "../data/quark_P101_100")
json_to_jsonl("../data/seesaw_cf_P103_False_100.json", "../data/quark_P103_100")
