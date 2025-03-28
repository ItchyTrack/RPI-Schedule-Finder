from pathlib import Path

path = Path("class_data/semester_data") / "202509" / Path("courses.json")
# print(path)

import pandas as pd
import json
from copy import copy

f = open(path)
data1 = json.load(f)
f.close()
data2:pd.DataFrame = pd.DataFrame(columns=["title", "crse", "id", "subj", "sections"])
for sec in data1:
	data2 = pd.concat([data2, pd.DataFrame(sec["courses"])])


f = open(Path("classes.json"))
userData:list = json.load(f)
f.close()

classesToTake = userData["classes"]
cpy = copy(classesToTake)
for c in cpy:
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

# subs = [s for s in nx.enumerate_all_cliques(G) if len(s) >= 6]
subs = [s for s in nx.enumerate_all_cliques(G)]

filterData = userData["filters"]
needed = filterData["classes to force"]
credData = {}
cpy = subs.copy()
for sub in cpy:
	credMax = 0
	credMin = 0
	found = 0
	key = list()
	credDict = {}
	for c in sub:
		row = data3.loc[data3['crn'] == c].iloc[0]
		if (row["title"] in needed):
			found += 1
		# print(row)
		credMax += row["credMax"]
		credMin += row["credMin"]
		credDict[row["crse"]] = (int(row["credMin"]), int(row["credMax"]))
		key.append(row["crse"])
	if not (found == len(needed) and credMax >= filterData["cred"]["min"] and credMin <= filterData["cred"]["max"]):
		subs.remove(sub)
	else:
		key.sort()
		credData[str(key)] = credDict

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

print()
print()
print("found", len(subs), "combos")
rowsToPrint = []
maxStart = 0
maxEnd = 0
# print(credData)
for ds in typeSets:
	rowsToPrint.append([])
	for d in ds[1:-1].split(", "):
		row = data3.loc[data3['crse'] == int(d)].iloc[0]
		start = d + "      " + row["title"]
		endList = list(typeSets[ds][row["title"]])
		end = ""
		for i in endList[:-1]:
			end += str(i) + ", "
		end += str(endList[-1])
		rowsToPrint[-1].append((credData[ds][int(d)], start, end))
		if len(start) > maxStart:
			maxStart = len(start)
		if len(end) > maxEnd:
			maxEnd = len(end)

lenOfLine = maxStart + 5 + maxEnd+14
print("Cred l:h     CRSE:     Title:" +  " "*(maxStart + 5-16) + "CRIs:")
print("-"*(lenOfLine))
for rows in rowsToPrint:
	sumL = 0
	sumH = 0
	for cred ,start, end in rows:
		sumL += cred[0]
		sumH += cred[1]
		print(str(cred[0]) + ":" + str(cred[1])+ " "*(13-len(str(int(cred[0])) + ":" + str(int(cred[1]))))+ start + " "*(maxStart + 5 -len(start)) + end)
	print(str(sumL) + ":" + str(sumH))
	print("-"*(lenOfLine))

# print(subs)
# for sub in subs:
# 	data = []
# 	for c in sub:
# 		row = data3.loc[data3['crn'] == c].iloc[0]
# 		data.append((row["title"], int(c)))
# 	data.sort()
# 	for d in data:
# 		print(d[0], str(d[1]) + ", ", end="")
# 	print()
# 	# nx.draw_networkx_edges(G, pos)

# exit()

# for sub in subs:
# 	pos = nx.spring_layout(G)
# 	nx.draw_networkx_nodes(G, pos, cmap=plt.get_cmap('jet'),  node_size = 500, nodelist=sub)
# 	nx.draw_networkx_labels(G, pos)
# 	nx.draw_networkx_edges(G, pos)
# 	print(sub)
# 	credMax = 0
# 	credMin = 0
# 	foundDif = False
# 	for c in sub:
# 		row = data3.loc[data3['crn'] == c].iloc[0]
# 		print(row["title"], row["credMax"])
# 	# nx.draw_networkx_edges(G, pos)
# 	plt.show()