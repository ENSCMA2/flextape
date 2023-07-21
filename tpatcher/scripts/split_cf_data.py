import jsonlines
import random
import json

def splitdata(data, js = False):
    if not js:
        with jsonlines.open(data) as reader:
            all_data = list(reader)
    else:
        with open(data) as o:
            all_data = json.load(o)
    train_indices = random.sample([i for i in range(len(all_data))], len(all_data) * 3 // 4)
    train_data = [all_data[i] for i in train_indices]
    val_data = [all_data[i] for i in range(len(all_data)) if i not in train_indices]
    stem = ".".join(data.split(".")[:-1])
    with jsonlines.open(f"{stem}_train.jsonl", mode = "w") as writer:
        writer.write_all(train_data)
    with jsonlines.open(f"{stem}_val.jsonl", mode = "w") as writer:
        writer.write_all(val_data)

splitdata("../../data/seesaw_cf_P101_False_100.jsonl")
splitdata("../../data/seesaw_cf_P103_False_100.json", True)
