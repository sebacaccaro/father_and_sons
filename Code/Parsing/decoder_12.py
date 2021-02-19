import sys
from itertools import tee
import math
import json
import functools
import itertools
import re
from difflib import SequenceMatcher
from tqdm.auto import tqdm

root = "../Debates/"
files = [
    "XII_legislature_italian_republic.json"
]

with open(root+files[0]) as f:
    data = json.load(f)

with open("deputati_12.json") as f:
    deputati = json.load(f)

dep_surnames = [f'{dep["name"]} {dep["surname"]}'.upper() for dep in deputati]
dep_surnames.append("PRESIDENTE")


def distance(s1, s2):
    s1l = s1.lower()
    s2l = s2.lower()
    return sum([0 if s1l[i] == s2l[i] else 1 for i in range(len(s1))])


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def containsSimilar(longStr, shortStr, minRatio):
    for i in range(0, len(longStr)-len(shortStr)):
        if similar(longStr[i:i+len(shortStr)].lower(), shortStr.lower()) > minRatio:
            return True
    return False


def remove_returns(doc):
    returns_split = re.finditer("[a-zA-Z]- \n[a-zA-Z]", doc)
    i = 0
    for rs in returns_split:
        i += 1
        # print("*************")
        # print(doc[rs.start(0)-15:rs.end(0)+15])
    return "??????????"


def removeFromBlackList(doc):
    newLines = []
    for line in doc:
        line2 = line.replace(" ", "")
        if containsSimilar(line2, "AttiParlamentari", 0.7) or \
                (containsSimilar(line2, "Discussioni", 0.7) and containsSimilar(line2, "Seduta", 0.7)):
            # print(line)
            pass
        else:
            newLines.append(line)
    # print(len(doc)-len(newLines))
    return newLines


def cutIndex(doc, indexStr="lasedutacomincia"):
    cut = -1
    i = 0
    lineIter = iter(doc)
    while cut == -1 and i < len(doc):
        line = next(lineIter).replace(" ", "")
        if similar(line[:len(indexStr)], indexStr) > 0.7:
            cut = i
        i += 1
    if i == len(doc):
        if indexStr == "lasedutacomincia":
            return cutIndex(doc, "nehalafacoltà")
        else:
            raise Exception("Cannot cut index")
    return doc[cut+1:]


def cutQueue(doc):
    endStr = "lasedutatermina"
    cut = -1
    i = len(doc)-1
    while cut == -1 and i > 0:
        line = doc[i].replace(" ", "")
        if similar(line[:len(endStr)], endStr) > 0.7:
            cut = i
        i -= 1
    if i == 0:
        return doc
    return doc[:cut]


def isLineSpeechStart(line):
    lineSpls = re.sub('[^a-zA-Z]+', '', line)
    numUpper = sum([1 for char in lineSpls if char.isupper()])
    if numUpper == 0 or len(lineSpls) == 0:
        return False
    upperRatio = numUpper/len(lineSpls)
    if not upperRatio > 0.05:
        return False
    return True


def expFun(x):
    return 1/(1+math.exp(10*x-10))


seq = [expFun(x/6) for x in range(6, 0, -1)]
for i in range(600):
    seq.append(seq[-1]/(5+i))


def isLineSpeechStart2(line):
    lineSpls = re.sub('[^a-zA-Z]+', '', line)
    probName = sum([0 if lineSpls[i].islower() else seq[i]
                    for i in range(len(lineSpls))])
    return probName
    if (probName > 1500):
        return True
    else:
        return False


def removeCites(lines):
    return [line for line in lines if "((" not in line and "))" not in line]


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def cutIntoLinesSpeeches(lines):
    indexes = []
    i = 0
    for line in lines:
        if isLineSpeechStart2(line) > 3:
            similar_dep = sorted([{"dep": dep, "value": similar(line[:len(dep)], dep)}
                                  for dep in dep_surnames], key=lambda i: -i["value"])
            if(similar_dep[0]["value"] > 0.6):
                indexes.append(
                    {"startPos": i, "speaker": similar_dep[0]["dep"]})
        i += 1
    indexes.append({"startPos": len(lines), "speaker": "DUMMY"})
    speeches = [{"speaker": a["speaker"], "text":lines[a["startPos"]                                                       :b["startPos"]]} for a, b in pairwise(indexes)]
    return speeches


def joinWords(l1, l2):
    if len(l1) > 2 and l1[-2:] == "- ":
        l1 = l1[:-2]
        return [l1+l2]
    elif len(l1) > 1 and l1[-1] == "-":
        l1 = l1[:-1]
        return [l1+l2]
    return [l1, l2]


def joinReturns(lines):
    done_lines = [lines[0]]
    for line in lines[1:]:
        to_append = joinWords(done_lines.pop(), line)
        done_lines = [*done_lines, *to_append]
    return done_lines


def removeStupidSpeeches(speeches):
    return [s for s in speeches if len(s["text"]) > 2]


def getDocSpeeches(doc):
    lines = doc.split("\n")
    lines = removeFromBlackList(lines)
    lines = cutIndex(lines)
    lines = cutQueue(lines)
    lines = removeCites(lines)
    speeches = cutIntoLinesSpeeches(lines)
    speeches = removeStupidSpeeches(speeches)
    for s in speeches:
        s["text"] = joinReturns(s["text"])
        s["text"] = "".join(s["text"])
    return speeches


lst_from = 0
lst_to = len(data)

i = 0
speeches = []
for doc in tqdm(data[lst_from:lst_to], desc="Parsing 12th legislature"):
    speeches = [*speeches, *getDocSpeeches(doc["text"])]

with open('parsed_12.json'.format(lst_from, lst_to), 'w') as outfile:
    json.dump(speeches, outfile, indent=4)
