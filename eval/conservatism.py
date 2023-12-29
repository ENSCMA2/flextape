import pandas as pd
from string import punctuation

keywords = ["conservative", "republican", "right-wing", 
			"american enterprise institute",
			"aei", "right wing", "far right"]

def contains_keyword(text):
	for word in keywords:
		if word in text:
			# print(word, text)
			return True
	return False

def clean(text):
	text = "".join([char for char in text if char not in punctuation])
	return text.lower().split()

texts = pd.read_csv("to_scale.csv", sep = "|", quotechar = '"')

texts["candidate"] = [0] * texts.shape[0]

for i, tem in texts.iterrows():
	pre = tem["pre_text"].lower()
	post = tem["post_text"].lower()
	pre_b = contains_keyword(pre)
	post_b = contains_keyword(post)
	texts.loc[texts.index[i], "candidate"] = 0 if pre_b == post_b else -1 if pre_b else 1

precandidates = texts[texts["candidate"] == -1]
postcandidates = texts[texts["candidate"] == 1]
print(texts.shape, precandidates.shape, postcandidates.shape)
texts.to_csv("conservatism_kw_ann.csv")
