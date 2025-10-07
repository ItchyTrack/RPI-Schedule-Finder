from pathlib import Path
import pandas as pd
import json
from copy import copy
from tqdm import tqdm

f = open(Path("classes.json"))
userData:list = json.load(f)
f.close()

classesToTake:list = userData["classes"]
cpy = copy(classesToTake)
for c in cpy:
	if "__DONT__" in c:
		classesToTake.remove(c)

path = Path("class_data/semester_data") / str(userData["year"]) / Path("courses.json")

print("Started Data Gather Step...")

f = open(path)
data1 = json.load(f)
f.close()
data2:pd.DataFrame = pd.DataFrame(columns=["title", "crse", "id", "subj", "sections"])
for sec in data1:
	data2 = pd.concat([data2, pd.DataFrame(sec["courses"])])

data2Incomplete = data2[data2["title"].isin(classesToTake)]

classesNotFound = []
for c in classesToTake:
	if (c not in data2Incomplete["title"].values):
		classesNotFound.append(c)

if len(classesNotFound) != 0:
	# try find them in catalog
	catalogPath = Path("class_data/semester_data") / str(userData["year"]) / Path("catalog.json")
	catalogF = open(catalogPath)
	catalogData1 = json.load(catalogF)
	catalogF.close()
	catalogData2 = pd.DataFrame(pd.DataFrame(catalogData1).T, columns=["name", "subj", "crse"])
	catalogData2 = catalogData2[catalogData2["name"].isin(classesNotFound)]

	for row in catalogData2.values:
		rows = data2[(data2["subj"] == row[1]) & (data2["crse"] == int(row[2]))]
		if (len(rows.index.values) == 0):
			# print(f"could not find class {row[0]}")
			continue
		rows.loc[:,'title'] = row[0]
		for secs in rows["sections"]:
			for sec in secs:
				sec['title'] = row[0]
		data2Incomplete = pd.concat([data2Incomplete, rows])

data2 = data2Incomplete

for c in classesToTake:
	if (c not in data2["title"].values):
		print(f"could not find class {c}")

print("Data Gather Step Done")

print("Making Conflict Graph...")

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

import networkx as nx

G = nx.Graph()
total = len(data3) + len(data3)**2 + len(data3)**2

with tqdm(total=total) as pbar:
	for index, row in data3.iterrows():
		G.add_node(row["crn"])
		pbar.update(1)

	pairsToSkip = set()
	for index, row in data3.iterrows():
		# print(row["timeslots"])
		for index2, row2 in data3.iterrows():
			if row["crse"] == row2["crse"]:
				pairsToSkip.add((row["crn"], row2["crn"]))
				pbar.update(1)
				continue
			if len(set(row["timeslots"]["days"]).intersection(set(row2["timeslots"]["days"]))) > 0:
				if row["timeslots"]["timeStart"] >= row2["timeslots"]["timeStart"] and row["timeslots"]["timeStart"] <= row2["timeslots"]["timeEnd"]:
					pairsToSkip.add((row["crn"], row2["crn"]))
				if row["timeslots"]["timeEnd"] >= row2["timeslots"]["timeStart"] and row["timeslots"]["timeEnd"] <= row2["timeslots"]["timeEnd"]:
					pairsToSkip.add((row["crn"], row2["crn"]))
			pbar.update(1)

	for index, row in data3.iterrows():
		for index2, row2 in data3.iterrows():
			if (row["crn"], row2["crn"]) not in pairsToSkip:
				G.add_edge(row["crn"], row2["crn"])
			pbar.update(1)

print("Conflict Graph Created Done")

subs = [s for s in nx.enumerate_all_cliques(G)]

print(f"Searching {len(subs)} Cliques In Conflict Graph...")

# subs = [s for s in nx.enumerate_all_cliques(G) if len(s) >= 6]

filterData = userData["filters"]
needed = filterData["classes to force"]
cpy = copy(needed)
for c in cpy:
	if "__DONT__" in c:
		needed.remove(c)
credData = {}
cpy = subs.copy()

for sub in tqdm(cpy):
	credMax = 0
	credMin = 0
	found = 0
	key = list()
	credDict = {}
	hasBioLab = False
	needsBioLab = False
	doubleLab = False
	for c in sub:
		row = data3.loc[data3['crn'] == c].iloc[0]
		if (row["subj"] == "BIOL" and row["crse"] == 1010):
			needsBioLab = True
		elif (row["subj"] == "BIOL" and (row["crse"] == 1016 or row["crse"] == 1015)):
			if (hasBioLab):
				doubleLab = True
				break
			hasBioLab = True
		if (row["title"] in needed):
			found += 1
		# print(row)
		credMax += row["credMax"]
		credMin += row["credMin"]
		credDict[row['subj'] + str(row["crse"])] = (int(row["credMin"]), int(row["credMax"]))
		key.append(row["subj"] + str(row["crse"]))
		if credMin > filterData["cred"]["max"]:
			break
	if not ((not doubleLab) and (needsBioLab == hasBioLab) and found == len(needed) and credMax >= filterData["cred"]["min"] and credMin <= filterData["cred"]["max"]):
		subs.remove(sub)
	else:
		key.sort()
		credData[str(key)] = credDict

print("Conflict Graph Cliques Search Done")
print("Grouping Similar Classes..")

typeSets = {}
for sub in tqdm(subs):
	data = set()
	key = list()
	for c in sub:
		row = data3.loc[data3['crn'] == c].iloc[0]
		data.add(row["title"])
		key.append(row["subj"] + str(row["crse"]))
	key.sort()
	if str(key) not in typeSets:
		typeSets[str(key)] = {}
		for c in sub:
			row = data3.loc[data3['crn'] == c].iloc[0]
			typeSets[str(key)][row["title"]] = set()
	for c in sub:
		row = data3.loc[data3['crn'] == c].iloc[0]
		typeSets[str(key)][row["title"]].add(c)

print("Grouping Similar Classes Done")

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
		d = d[1:-1]
		crse = int(''.join(x for x in d if x.isdigit()))
		subj = ''.join(x for x in d if not x.isdigit())
		row = data3.loc[(data3['crse'] == crse) & (data3['subj'] == subj)].iloc[0]
		start = subj + "      " + str(crse) +"      " + row["title"]
		endList = list(typeSets[ds][row["title"]])
		end = ""
		for i in endList[:-1]:
			end += str(i) + ", "
		end += str(endList[-1])
		rowsToPrint[-1].append((credData[ds][row["subj"] + str(row["crse"])], start, end))
		if len(start) > maxStart:
			maxStart = len(start)
		if len(end) > maxEnd:
			maxEnd = len(end)

lenOfLine = maxStart + 5 + maxEnd+14
print("Cred l:h     SUBJ:     CRSE:     Title:" +  " "*(maxStart + 5-26) + "CRIs:")
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
