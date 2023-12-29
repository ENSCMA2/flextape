import pandas as pd

a1 = pd.read_csv("a1.csv").fillna(1.5)
a2 = pd.read_csv("a2.csv")
a3 = pd.read_csv("a3.csv")

flaws = ["Anglo-centrism",	
		 "Sexism",
		 "Religious Injection",
		 "Xenophobia",	
		 "Classism",	
		 "Racism",
		 "Injection of Conservatism",	
		 "Edit reflected?"]

for flaw in flaws:
	d = a1[(a1[flaw] != a2[flaw]) | (a1[flaw] != a3[flaw]) | (a2[flaw] != a3[flaw])]
	d.drop(flaws, axis = 1).to_csv(f"{flaw}_dis.csv")