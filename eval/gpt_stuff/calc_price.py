import json
from glob import glob 

def read_json(path):
    with open(path, 'r') as fin:
        data = json.load(fin)
    return data 

def write_json(path, data):
    with open(path, 'w') as fout:
        json.dump(data, fout)

gpt3_usage = glob(f"outputs/gpt-3.5-turbo-0301/usage_*.json")
gpt3_price = {"input": 0.0015, "output": 0.002}

total_gpt3_tokens = {"input": 0, "output": 0}
for filepath in gpt3_usage:
    usage_data = read_json(filepath)
    for usage in usage_data:
        if "Error" in usage or "error" in usage: continue
        total_gpt3_tokens["input"] += usage["prompt_tokens"]
        total_gpt3_tokens["output"] += usage["completion_tokens"]


total_cost = 0
model_names = ["GPT-3"]
price_data = [(total_gpt3_tokens,gpt3_price)]
for i, (tokens, price) in enumerate(price_data):
    for key in ["input", "output"]:
        cost = (tokens[key]/1000)*price[key]
        total_cost += cost
        print(f"{model_names[i]} {key.capitalize()} Cost: ${cost}")

print(f"Total Cost: ${total_cost}")