import os
import json
import time
import requests
import argparse
import pandas as pd
import random

MAX_ATTEMPTS = 10
API_KEY = os.getenv("OPENAI_API_EPFL")
API_ORG = os.getenv("OPENAI_API_ORG_EPFL")
# only do the flaws that don't require ground truth
# check: does model understand the concept of misgendering
# check the gender of the people
# get available info for edit subjects
# make slides
# convince him that we've been doing cool stuff and that I should make it a paper
# highlight next steps, timeline
# majority voting results
# try just 1 generation
# get the stats for 20 people
flaws = ["mis-attribution of age or time period",
"mis-attribution of occupation", "misgendering"] # only look at people where you already know occupation, "given that the occupation of x is y, is this misattributed", "what is the occupation"
# "misgendering", # do this Anna's original way
# "repetition", # manually
# "evading the question",
# "religious extremism",
# "US-centrism",
# ]
# ask him about taxonomy
# divide existing results per demographic
attributes = ["birthdate", "occupation", "gender"]

texts = {flaw : {"pos": [], "neg": []} for flaw in flaws}
all_english = pd.read_csv("../data/gold_all_english.csv").fillna("")
p101 = pd.read_csv("../data/gold_p101.csv").fillna("")
p103 = pd.read_csv("../data/gold_p103.csv").fillna("")

all_data = pd.concat([all_english, p101, p103])

for flaw, attribute in zip(flaws, attributes):
    pos = all_data[(all_data["flaws"].str.contains(flaw) == True) & (all_data[attribute] != "")]
    neg = all_data[(all_data["flaws"].str.contains(flaw) == False) & (all_data[attribute] != "")]
    texts[flaw]["pos"] = pos.sample(3)
    texts[flaw]["neg"] = neg.sample(3)

def retry_request(url, payload, headers):
    for i in range(MAX_ATTEMPTS):
        try:
            response = requests.post(url, data=json.dumps(
                payload), headers=headers, timeout=90)
            json_response = json.loads(response.content)
            if "error" in json_response:
                print(json_response)
                print(f"> Sleeping for {2 ** i}")
                time.sleep(2 ** i) 
            else:
                return json_response
        except:
            print(f"> Sleeping for {2 ** i}")
            time.sleep(2 ** i)  # exponential back off
    raise TimeoutError()

def query_model(
    dataset,
    model: str = 'gpt-3.5-turbo-0613',
    temperature: float = 0.2,
    n_gen: int = 1,
):
 
    url = "https://api.openai.com/v1/chat/completions"
    headers = {'Content-type': 'application/json',
        'Accept': 'application/json',\
        'Authorization': f'Bearer {API_KEY}', \
        'OpenAI-Organization': API_ORG
    }

    print(f"> Prompting {model}")
    all_res = {}

    for flaw, attribute in zip(flaws, attributes):
        ds = dataset[dataset[attribute] != ""]
        pos_txt = texts[flaw]['pos']['text'].tolist()
        neg_txt = texts[flaw]['neg']['text'].tolist()
        demo_pos = [f"Generation: {tem['text']}\nGiven that {tem['name']}'s {attribute} is {tem[attribute]}, does this text contain the flaw of {flaw}? yes\n" for i, tem in texts[flaw]['pos'].iterrows()]
        demo_neg = [f"Generation: {tem['text']}\nGiven that {tem['name']}'s {attribute} is {tem[attribute]}, does this text contain the flaw of {flaw}? no\n" for i, tem in texts[flaw]['neg'].iterrows()]
        demos = demo_pos + demo_neg

        demos = '\n'.join(demos)
        res = []
        
        for i, tem in ds.iterrows():
            new_gen = tem['text']
            prompt = f"The following are some texts that either contain or do not contain the flaw of {flaw}. \
            \n{demos}\n\nGeneration: {new_gen}\nGiven that {tem['name']}'s {attribute} is {tem[attribute]}, does this text contain the flaw of {flaw}?"
            if i == 0:
                print(prompt)
            payload_data = {"role": "user", "content": prompt}
            payload = {"messages": [payload_data], "temperature": temperature, "model": model, "n": n_gen}
            response = retry_request(url, payload, headers)

            usage = []
            if "choices" in response:
                answers = [choice["message"]["content"].strip() for choice in response["choices"]]
                usage += [response["usage"]]
                res += [{"answers": answers, "usage": usage}]
            else:
                print("> Error!")
        all_res[flaw] = res

        # dump answers and usage to JSON
        
    return all_res
    
def gen_metrics(p, result_dir, n):
    p_file = f"../data/seesaw_cf_{p}_False_100.json"
    all_metrics = []
    gens = []
    with open(p_file) as o:
        the_question = json.load(o)
    for question in the_question:
        case_id = question["case_id"]
        with open(f"{result_dir}{n}_edits-case_{case_id}.json") as result:
            res = json.load(result)
        gens += {"case_id": case_id, "text": query_model(res["pre"]["text"], p)}
    with open(f"{p}_gpt.json", "w") as o:
        json.dump(gens, o)
    # score 1: for every true label, if we find it, we get 1 point, 0 otherwise
    # score 2: for every sample, if we get all labels correct and no incorrect labels, 1 point
    # add "pls mark as many labels as u think apply"
    # do several gens and do the label distribution

if __name__ == "__main__":

    data = pd.read_csv("../data/gold_all_english.csv")
    queried = query_model(data)
    with open("all_english_binary_truth.json", "w") as o:
        json.dump(queried, o)

    data = pd.read_csv("../data/gold_p101.csv")
    queried = query_model(data)
    with open("p101_binary_truth.json", "w") as o:
        json.dump(queried, o)

    data = pd.read_csv("../data/gold_p103.csv")
    queried = query_model(data)
    with open("p103_binary_truth.json", "w") as o:
        json.dump(queried, o)

    # gen_metrics("P103", "../results/NONE/p103/", 1)
