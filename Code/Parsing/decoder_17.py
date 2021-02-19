import json
import functools
import itertools
import re
from tqdm.auto import tqdm

root = "../Debates/"
files = [
    "I_legislature_italian_republic.json",
    "XVIII_legislature_italian_republic.json",
    "XVII_legislature_italian_republic.json"
]

with open(root+files[2]) as f:
    data = json.load(f)

with open("deputati_17.json") as f:
    deputati = json.load(f)

name_sur = [d["name"]+d["surname"] for d in deputati]
name_sur = [d.replace(" ", "").lower() for d in name_sur]

name_sur_rev = [d["surname"]+d["name"] for d in deputati]
name_sur_rev = [d.replace(" ", "").lower() for d in name_sur_rev]


def inLines(textField):
    return textField.split('\n')


def confine_index(textLines):
    try:
        start, end = -1, -1
        lineNum = 0
        while (start == -1):
            if "I N D I C E" in textLines[lineNum]:
                start = lineNum
            lineNum += 1
        while (end == -1):
            if "— 1 —" in textLines[lineNum]:
                end = lineNum
            lineNum += 1
        return start, end
    except IndexError:
        return False, False


def printPretty(line, end, start=0):
    for i in range(start, end):
        print(str(i) + ">> " + line[i])


def extractSpeakers(doc):
    start, end = confine_index(doc["text"])
    currentBuffer = []
    entries = []
    for i in range(start, end):
        line = doc["text"][i].lower()
        line = line.replace(" ", "")
        i = 0
        for d in name_sur:
            if d in line:
                entries.append(d)
                entries.append(name_sur_rev[i])
            i += 1
        i = 0
        for d in name_sur_rev:
            if d in line:
                entries.append(d)
                entries.append(name_sur[i])
            i += 1
    entries = list(set(entries))
    entries.append("presidente")
    return entries


def cleanBraketes(textLines):
    newLines = []


def matchRotation(s1, s2):
    name_permutation = [" ".join(x) for x in list(
        itertools.permutations(s1.split()))]
    # print(name_permutation)
    return s2 in name_permutation


nameRegex = "^(([A-Z]*\s*)*)"


def breakIntoSpeeches(doc):
    speeches = []
    for i in range(confine_index(doc["text"])[1], len(doc["text"])):
        res = re.findall(nameRegex, doc["text"][i])[0][0]
        spk = res
        res = res.lower().replace(" ", "")
        if len(res) > 1 and res in doc["speakers"]:
            # print(str(i) + " >> " + res)
            speeches.append({"speaker": spk, "index": i})

    def getFileEnd(textLines):
        end = len(textLines)
        for i in range(end):
            if "La seduta termina alle " in textLines[i]:
                end = i
        return end

    segments = []
    for i in range(len(speeches)):
        s = speeches[i]
        start = s["index"]
        end = speeches[i+1]["index"] if i + \
            1 < len(speeches) else getFileEnd(doc["text"])
        segments.append(
            {"speaker": s["speaker"], "segment": doc["text"][start:end]})

    return segments


def cleanSegment(segment, speaker):
    # Remove page start line and other stuff
    blacklist = ["XVIII LEGISLATURA — DISCUSSIONI", "XVII LEGISLATURA — DISCUSSIONI",
                 "Atti Parlamentari —", "XVII LEGISLATURA — DISCUSSIONI"]

    def notInBlackList(x): return not any([b in x for b in blacklist])
    segment = [line for line in segment if notInBlackList(line)]

    # Since it flattens the text, it needs to be one of the last op
    def removeParenthesis(segment):
        tempSeg = []
        for line in segment:
            if len(tempSeg) > 0 and tempSeg[-1][-1] == "-":
                tempSeg[-1] = tempSeg[-1][:-1]
                tempSeg[-1] += line
            else:
                tempSeg.append(line)
        segment = tempSeg
        segment = " ".join(segment)
        segment = re.sub("[\(\[].*?[\)\]]", "", segment)
        lonelyPar = segment.find("(")
        if lonelyPar != -1:
            segment = segment[: lonelyPar]
        return segment

    def removeSpeaker(segment, speaker):
        segment = segment[len(speaker):]
        while len(segment) > 1 and segment[0] in [".", " ", ","]:
            segment = segment[1:]
        return segment

    segment = removeParenthesis(segment)
    segment = removeSpeaker(segment, speaker)
    return segment


data2 = []
#print("**Filtering Empty documents")
for d in data:
    start, end = confine_index(inLines(d["text"]))
    if end != False:
        data2.append(d)

data = data2

for d in tqdm(data, desc="Parsing 17th legislature (1/2)"):
    d["text"] = inLines(d["text"])
    d["speakers"] = [e.lower() for e in extractSpeakers(d)]

# for line in data[0]["text"]:
#    print(line)

documentIntoSpeeches = list(itertools.chain.from_iterable(
    [breakIntoSpeeches(x) for x in tqdm(data, desc="Parsing 17th legislature (2/2)")]))


print("** Removing stupid shit")
documentIntoSpeeches = [{"speaker": item["speaker"], "segment": cleanSegment(
    item["segment"], item["speaker"])} for item in documentIntoSpeeches]

with open('parsed_17.json', 'w') as outfile:
    json.dump(documentIntoSpeeches, outfile, indent=4)

""" segments = documentIntoSpeeches
for s in segments:
    print("----------{}---------".format(s["speaker"]))
    for line in s["segment"]:
        print(line)
 """
