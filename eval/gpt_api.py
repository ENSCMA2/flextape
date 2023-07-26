import os
import json
import time
import requests
import argparse

MAX_ATTEMPTS = 10
API_KEY = os.getenv("OPENAI_API_EPFL")
API_ORG = os.getenv("OPENAI_API_ORG_EPFL")

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
    model: str = 'gpt-3.5-turbo-0613',
    temperature: float = 0.7,
    n_gen: int = 1,
):
 
    url = "https://api.openai.com/v1/chat/completions"
    headers = {'Content-type': 'application/json',
        'Accept': 'application/json',\
        'Authorization': f'Bearer {API_KEY}', \
        'OpenAI-Organization': API_ORG
    }

    print(f"> Prompting {model}")

    prompt_template = "Generation: {}\nLabel: {}\n\n"

    demos = []
    generations = []
    all_labels = []

    for gen, labels in zip(generations, all_labels):
        demos += [prompt_template.format(gen, labels)]

    demos = '\n'.join(demos)
    
    for new_gen in dataset:
        prompt = f"{demos}\n\nGeneration: {new_gen}\nLabel:"
        payload_data = {"role": "user", "content": prompt}
        payload = {"messages": [payload_data], "temperature": temperature, "model": model, "n": n_gen}
        response = retry_request(url, payload, headers)

        usage = []
        if "choices" in response:
            answers = [choice["message"]["content"].strip() for choice in response["choices"]]
            usage += [response["usage"]]
        else:
            print("> Error!")

        # dump answers and usage to JSON
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--model', default="gpt-3.5-turbo-0301", help='model to use')
    parser.add_argument('--temperature', default=0.7, help='temperature')
    parser.add_argument('--n-gen', default=5, help='number of generations')

    args = parser.parse_args()

    query_model(
        model=args.model,
        temperature=args.temperature,
        n_gen=args.n_gen,
    )