from pathlib import Path

path = Path("class_data/semester_data") / "202509" / Path("courses.json")
# print(path)

import pandas as pd
import json

f = open(path)
data1 = json.load(f)
f.close()
data2:pd.DataFrame = pd.DataFrame(columns=["title", "crse", "id", "subj", "sections"])
for sec in data1:
	data2 = pd.concat([data2, pd.DataFrame(sec["courses"])])


f = open(Path("classes.json"))
classesToTake:list = json.load(f)
f.close()

for c in classesToTake:
	if "__DONT__" in classesToTake:
		classesToTake.remove(c)
data2 = data2[data2["title"].isin(classesToTake)]

data3:pd.DataFrame = pd.DataFrame(columns=["title", "crse", "subj", 'act', 'credMax', 'credMin', 'cap', 'crn', 'rem', 'sec', 'timeslots'])
['act', 'attribute', 'cap', 'credMax', 'credMin', 'crn', 'crse', 'rem', 'sec', 'subj', 'timeslots', 'title']
for index, row in data2.iterrows():
	if (row["crse"] >= 5000): continue
	for sec in row["sections"]:
		if "xl_rem" in sec: sec.pop("xl_rem")
		# sec.pop("credMax")
		sec.pop("attribute")
		# sec.pop("credMin")
		data3 = pd.concat((data3, pd.DataFrame(sec)))

# data3 = data3.drop_duplicates(subset='crn')
# print(data3.head(50))

import networkx as nx

import matplotlib.pyplot as plt

G = nx.Graph()
for index, row in data3.iterrows():
	G.add_node(row["crn"])

pairsToSkip = set()
for index, row in data3.iterrows():
	# print(row["timeslots"])
	for index2, row2 in data3.iterrows():
		if row["crse"] == row2["crse"]:
			pairsToSkip.add((row["crn"], row2["crn"]))
			continue
		if len(set(row["timeslots"]["days"]).intersection(set(row2["timeslots"]["days"]))) > 0:
			if row["timeslots"]["timeStart"] >= row2["timeslots"]["timeStart"] and row["timeslots"]["timeStart"] <= row2["timeslots"]["timeEnd"]:
				pairsToSkip.add((row["crn"], row2["crn"]))
			if row["timeslots"]["timeEnd"] >= row2["timeslots"]["timeStart"] and row["timeslots"]["timeEnd"] <= row2["timeslots"]["timeEnd"]:
				pairsToSkip.add((row["crn"], row2["crn"]))

for index, row in data3.iterrows():
	for index2, row2 in data3.iterrows():
		if (row["crn"], row2["crn"]) not in pairsToSkip:
			G.add_edge(row["crn"], row2["crn"])

subs = [s for s in nx.enumerate_all_cliques(G) if len(s) >= 6]

from copy import copy

needed = ["Intro Differential Equations"]

cpy = copy(subs)
for sub in cpy:
	credMax = 0
	credMin = 0
	found = 0
	for c in sub:
		row = data3.loc[data3['crn'] == c].iloc[0]
		if (row["title"] in needed):
			found += 1
		# print(row)
		credMax += row["credMax"]
		credMin += row["credMin"]
	if not (found == len(needed) and credMax >= 23 and credMin <= 23):
		subs.remove(sub)

print(len(subs))

# print(subs)
typeSets = {}
for sub in subs:
	data = set()
	key = list()
	for c in sub:
		row = data3.loc[data3['crn'] == c].iloc[0]
		data.add(row["title"])
		key.append(row["crse"])
	key.sort()
	if str(key) not in typeSets:
		typeSets[str(key)] = {}
		for c in sub:
			row = data3.loc[data3['crn'] == c].iloc[0]
			typeSets[str(key)][row["title"]] = set()
	for c in sub:
		row = data3.loc[data3['crn'] == c].iloc[0]
		typeSets[str(key)][row["title"]].add(c)

print(typeSets.keys())

for d in typeSets:
	print(typeSets[d])

# print(subs)
for sub in subs:
	data = []
	for c in sub:
		row = data3.loc[data3['crn'] == c].iloc[0]
		data.append((row["title"], int(c)))
	data.sort()
	for d in data:
		print(d[0], str(d[1]) + ", ", end="")
	print()
	# nx.draw_networkx_edges(G, pos)

# exit()

for sub in subs:
	pos = nx.spring_layout(G)
	nx.draw_networkx_nodes(G, pos, cmap=plt.get_cmap('jet'),  node_size = 500, nodelist=sub)
	nx.draw_networkx_labels(G, pos)
	nx.draw_networkx_edges(G, pos)
	print(sub)
	credMax = 0
	credMin = 0
	foundDif = False
	for c in sub:
		row = data3.loc[data3['crn'] == c].iloc[0]
		print(row["title"], row["credMax"])
	# nx.draw_networkx_edges(G, pos)
	plt.show()