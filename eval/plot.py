import os
import json
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt 
import sys
import math
def read_json(path):
    with open(path, 'r') as fin:
        data = json.load(fin)
    return data 

props = ["P101", "P27_P101",
          "P19_P101",]
def idtostr(prop):
    d = {"P101": "Field of Work", "P103": "Native Language",
         "P27": "Country of Citizenship", "P21": "Gender",
         "P19": "Place of Birth"}
    return d[prop.split("_")[0]]

column_name_templ = "{}_mean_p_diff_diff"
genders = ["male", "female"]
editing_methods = ["mend", "ft", "memit"]

race_dfs = [pd.read_csv(f"../data/Ethnic Groups - {prop}.csv").fillna("") for prop in props]
def intersection_list(lol):
    initial = set(lol[0])
    for i in range(1, len(lol)):
        initial = initial.intersection(lol[i])
    return initial

racial_groups = intersection_list([df["Racial Group"].tolist() for df in race_dfs])
racial_groups.remove("")
geo_groups = intersection_list([df["Geo Group"].tolist() for df in race_dfs])
geo_groups.remove("")

prop_to_cluster = {"P101": "occupation_clusters.json",
                   "P19": "city_clusters.json",
                   "P27": "country_clusters.json"}
def genfig(prop):
    model = sys.argv[1]
    method = sys.argv[2]
    category_filename = f"../data/{prop}_conversions.csv"
    categories_df = pd.read_csv(category_filename)

    case_ids = categories_df["case_id"].tolist()
    fields = categories_df["target_new_str"].tolist()
    category_map = {case_id: job for case_id, job in zip(case_ids, fields)}

    try:
        field_map = read_json(prop_to_cluster[prop.split("_")[0]])
        field_map_rev = {}
        for cluster, values in field_map.items():
            field_map_rev = {**field_map_rev, **{val: cluster for val in values}}
    except Exception as e:
        print(e)
        field_map_rev = {}
    
    plot_data = []
    path = f"../results/{model}/{prop}/race/{method}.csv"
    data = pd.read_csv(path)
    case_ids = data["case_id"].tolist()[:-3]
    for race in racial_groups:
        column_name = column_name_templ.format(race)
        if column_name not in data.columns:
            continue
        values = data[column_name].tolist()[:-3]
        for case_id, value in zip(case_ids, values):
            field = category_map[int(case_id)]
            if field not in ["None", "Oceania"] and (True if len(field_map_rev.keys()) == 0 else field_map_rev[field] not in ["None", "Oceania"]):
                plot_data += [{
                    "Race": race.capitalize(),
                    "value": value,
                    idtostr(prop): field_map_rev[field] if len(field_map_rev.keys()) > 0 else field,
                    "Method": method 
                }]
    df = pd.DataFrame(plot_data)
    g = sns.catplot(data=df, x=idtostr(prop), y="value", hue="Race", 
                    col="Method", kind="box", sharey=False, legend_out = False)
    nonnan = [v for v in values if not math.isnan(v)]
    if len(nonnan) == 0:
        nonnan = [0]
    # g.set(ylim = (min(-1e-15, min(nonnan) * 1.1), max(max(nonnan) * 1.1, 1e-15)))
    g.set_xticklabels(rotation=20)
    g.set_axis_labels(idtostr(prop), "Mean Difference")
    plt.tight_layout() 
    plt.savefig(f"../results/{model}/{prop}/race/{model}_race_{method}.png")
    plt.clf()

    
    plot_data = []
    path = f"../results/{model}/{prop}/race/{method}.csv"
    data = pd.read_csv(path)
    case_ids = data["case_id"].tolist()[:-3]
    for race in geo_groups:
        column_name = column_name_templ.format(race)
        if column_name not in data.columns:
            continue
        values = data[column_name].tolist()[:-3]
        for case_id, value in zip(case_ids, values):
            field = category_map[int(case_id)]
            plot_data += [{
                "Race": race.capitalize(),
                "value": value,
                idtostr(prop): field_map_rev[field] if len(field_map_rev.keys()) > 0 else field,
                "Method": method 
            }]
    df = pd.DataFrame(plot_data)
    g = sns.catplot(data=df, x=idtostr(prop), y="value", hue="Race", 
                    col="Method", kind="box", sharey=False, legend_out = False)
    g.set_xticklabels(rotation=90)
    g.set_axis_labels(idtostr(prop), "Mean Difference")
    plt.tight_layout() 
    plt.savefig(f"../results/{model}/{prop}/race/{model}_geo_{method}.png")
    plt.clf()

    if prop != "P21_P101":
        plot_data = []
        method = method.upper()
        path = f"../results/{model}/{prop}/gender/{method}.csv"
        data = pd.read_csv(path)
        case_ids = data["case_id"].tolist()[:-3]
        for gender in genders:
            column_name = column_name_templ.format(gender)
            if column_name not in data.columns:
                continue
            values = data[column_name].tolist()[:-3]
            for case_id, value in zip(case_ids, values):
                field = category_map[int(case_id)]
                plot_data += [{
                    "Gender": gender.capitalize(),
                    "value": value,
                    idtostr(prop): field_map_rev[field] if len(field_map_rev.keys()) > 0 else field,
                    "Method": method 
                }]

        df = pd.DataFrame(plot_data)
        g = sns.catplot(data=df, x=idtostr(prop), y="value", hue="Gender", 
                        col="Method", kind="box", sharey=False, legend_out = False)
        g.set_xticklabels(rotation=90)
        g.set_axis_labels(idtostr(prop), "Mean Difference")
        plt.tight_layout() 
        plt.savefig(f"../results/{model}/{prop}/gender/{model}_{method}.png")
        plt.clf()


for prop in props:
    genfig(prop)