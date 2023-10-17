import os
import json


def mass_rename(directory):
    for filename in os.listdir(directory):
        if filename != ".DS_Store":
            f = os.path.join(directory, filename)
            number = int(f.split("_")[-1].split(".")[0])
            before = "_".join(f.split("_")[:-1])
            with open(f) as o:
                jsn = json.load(o)
            jsn["case_id"] = jsn["case_id"] + 7
            with open(f"{before.replace('hold', '')}_{number + 7}.json", "w") as o:
                json.dump(jsn, o)

# mass_rename(f"../results/OG/hold")
# mass_rename(f"../results/FT/hold")
mass_rename(f"../results/MEND/hold")
# mass_rename(f"../results/MEMIT/hold")


'''
def fix(directory):
    for filename in os.listdir(directory):
        if filename != ".DS_Store":
            f = os.path.join(directory, filename)
            number = int(f.split("_")[-1].split(".")[0])
            before = "_".join(f.split("_")[:-1])
            with open(f) as o:
                jsn = json.load(o)
            case_id = jsn["case_id"]
            os.rename(f, f"{before}_{case_id}.json")

fix("../results/FT") 4126232256
'''