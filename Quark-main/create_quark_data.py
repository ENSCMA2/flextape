import json
import pandas as pd
import jsonlines

def json_to_jsonl(og, new_name):
    with open(og) as o:
        original = json.load(o)
    ultimate = []
    for stuff in original:
        prompt_temp = stuff["requested_rewrite"]["prompt"]
        prompt = prompt_temp.replace("{}", stuff["requested_rewrite"]["subject"])
        response = stuff["requested_rewrite"]["target_new"]["str"]
        ultimate.append({"prompt": prompt, "response": response})
    with open(new_name, "w") as o:
        for stuff in ultimate:
            o.write(str(stuff) + "\n")

json_to_jsonl("../data/seesaw_cf_P101_False_100.json", "../data/quark_P101_100.jsonl")
json_to_jsonl("../data/seesaw_cf_P103_False_100.json", "../data/quark_P103_100.jsonl")
