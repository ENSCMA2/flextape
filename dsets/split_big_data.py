import json

def split_in(fname, n):
	with open(fname, "r+") as o:
		original = json.load(o)
	done = 0
	ct = 1
	while done < len(original):
		print(done)
		new_fname = fname[:-5] + "_part_" + str(ct) + ".json"
		print(new_fname)
		with open(new_fname, "w+") as o:
			last = min(done + (len(original) // n), len(original))
			json.dump(original[done:last], o)
		print(f"dumped {done} through {last}")
		done += len(original) // n
		ct += 1

split_in("../data/seesaw_cf_P101_False.json", 30)