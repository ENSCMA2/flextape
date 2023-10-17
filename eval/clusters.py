import pandas as pd
import json

city_names = pd.read_csv("../data/city_to_country.csv", names = ["City", "Country", "UCity", "CName"])[["UCity", "CName"]]
city_to_country = pd.read_csv("../data/city_to_country.csv", names = ["City", "Country", "UCity", "CName"])[["City", "Country"]]
city_code_to_city_name = {tem["UCity"]: tem["CName"] for i, tem in city_names.iterrows()}
country_codes_continents = pd.read_csv("../data/country_codes.csv", names = ["Name", "Code", "Continent"])
country_to_continent = {tem["Name"]: tem["Continent"] for i, tem in country_codes_continents.iterrows()}
city_to_continent = {tem["City"]: country_to_continent[tem["Country"]] for i, tem in city_to_country.iterrows()}
p27_cats = pd.read_csv("../data/P27_cats.csv", names = ["Code", "Country", "Continent"])
p27_strlookup = {tem["Code"]: tem["Country"] for i, tem in p27_cats.iterrows()}
p27_c2c = {tem["Code"]: tem["Continent"] for i, tem in p27_cats.iterrows()}

city_clusters = {}
for key in city_to_continent:
	continent = city_to_continent[key]
	city = city_code_to_city_name[key]
	try:
		city_clusters[continent].append(city)
	except:
		city_clusters[continent] = [city]

with open("city_clusters.json", "w") as o:
	json.dump(city_clusters, o)

country_clusters = {}
for key in p27_c2c:
	continent = p27_c2c[key]
	country = p27_strlookup[key]
	try:
		country_clusters[continent].append(country)
	except:
		country_clusters[continent] = [country]

with open("country_clusters.json", "w") as o:
	json.dump(country_clusters, o)


