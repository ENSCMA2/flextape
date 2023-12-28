import pandas as pd
from string import punctuation

unis = ["harvard", "yale", "princeton", "stanford", "mit", 
		"massachusetts institute of technology", "caltech", 
		"california institute of technology", "pennsylvania",
		"oxford", "dartmouth", "columbia", "cornell", "upenn", 
		"brown university", "duke university", "emory", "carnegie mellon",
		"open university", "loughborough"]
cities = ["san francisco", "los angeles", "san diego", "palo alto", 
		  "silicon valley", "santa clara", "orange county", "sacramento",
		  "philadelphia", "pittsburgh", "new york", "boston", "cambridge",
		  "nashville", "baltimore", "new orleans", "orlando", "miami",
		  "charlotte", "kansas city", "indianapolis", "columbus", "detroit",
		  "chicago", "atlanta", "milwaukee", "albuquerque", "houston",
		  "phoenix", "san antonio", "dallas", "austin", "jacksonville", 
		  "san jose", "fort worth", "seattle", "denver", "el paso",
		  "las vegas", "portland", "louisville", "memphis", "tucson",
		  "fresno", "mesa", "omaha", "raleigh", "long beach", "oakland",
		  "minneapolis", "tulsa", "bakersfield", "tampa", "wichita", "anaheim",
		  "honolulu", "cincinnati", "london", "manchester", "york", "warwick",
		  "bristol", "durham", "cardiff", "glasgow", "edinburgh", "leeds", 
		  "st andrews", "st. andrews", "saint andrews"]
states = ["alaska", "alabama", "arizona", "arkansas", "california", "colorado",
		  "connecticut", "delaware", "florida", "georgia", "hawaii", "idaho",
		  "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana",
		  "maine", "maryland", "massachusetts", "michigan", "minnesota", 
		  "mississippi", "missouri", "montana", "nebraska", "nevada",
		  "new hampshire", "new jersey", "new mexico", "new york", "carolina",
		  "dakota", "ohio", "oklahoma", "oregon", "pennsylvania", "rhode island",
		  "tennessee", "texas", "utah", "vermont", "virginia", "washington",
		  "wisconsin", "wyoming"]
hollywood = ["hollywood", "universal pictures", "warner bros", "disney", 
			 "sony pictures", "paramount"]
press = ["bbc", "nytimes", "latimes", "wsj", "wall street", "the post", "wapo",
		 "huffpost", "abc", "sf chronicle", "daily mail", "daily telegraph",
		 "daily mirror", "the guardian", "cbs"]
countries = ["united states", "uk", "usa", "america", "american", "british", 
			 "english", "scottish", "scotland", "irish", "ireland", "england", 
			 "britain", "united kingdom", "wales", "welsh"]
other = ["nfl", "nhl", "nba", "wnba", "us open", "nsa", "fbi", "department of justice",
		 "department of defense", "supreme court", "nhs"]

keywords = other + countries + press + hollywood + states + cities + unis

def contains_keyword(text):
	for word in keywords:
		if word in text:
			return True
	return False

def clean(text):
	text = "".join([char for char in text if char not in punctuation])
	return text.lower().split()

texts = pd.read_csv("to_scale.csv", sep = "|", quotechar = '"')

texts["precandidate"] = [0] * texts.shape[0]
texts["postcandidate"] = [0] * texts.shape[0]

for i, tem in texts.iterrows():
	pre = clean(tem["pre_text"])
	post = clean(tem["post_text"])
	if contains_keyword(pre):
		texts["precandidate"] = 1
	if contains_keyword(post):
		texts["postcandidate"] = 1

precandidates = texts[texts["precandidate"] == 1]
print(texts.shape, precandidates.shape)
precandidates.to_csv("anglocentrism_precandidates.csv")

postcandidates = texts[texts["postcandidate"] == 1]
print(texts.shape, postcandidates.shape)
postcandidates.to_csv("anglocentrism_postcandidates.csv")
