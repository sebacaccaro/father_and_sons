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

with open(root+files[1]) as f:
    data = json.load(f)


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
        line = doc["text"][i]
        if (not("Atti Parlamentari" in line and "Camera dei Deputati" in line)):
            currentBuffer = [*currentBuffer, line]
            if "...." in line:
                entries = [*entries, currentBuffer]
                currentBuffer = []

    for entry in entries:
        entry = " ".join(entry)

    blacklist = ["ERRATA CORRIGE", "N.B. ", "XVIII  LEGISLATURA  –", "XVIII LEGISLATURA", "XVIII",
                 "SEGNALAZIONI RELATIVE ALLE VOTAZIONI EFFETTUATE NEL CORSO DELLA SEDUTA", "DICHIARAZIONI PROGRAMMATICHE DEL GOVERNO", "XVII LEGISLATURA  –", "XVII LEGISLATURA", "XVII", ]

    def notInBlackList(x): return not any([b in x for b in blacklist])

    entries = [" ".join(entry) for entry in entries]
    entries = [e for e in entries if "RESOCONTO STENOGRAFICO" not in e]
    entries = [e for e in entries if str.split(e)[0].isupper()]
    entries = [e[:e.find("....")] for e in entries]
    entries = [e for e in entries if notInBlackList(e)]
    entries = [e.split(",")[0] for e in entries]
    entries = [e[:e.find("(")] if "(" in e else e for e in entries]
    entries = set(entries)
    entries = [str.strip(e.upper()) for e in entries]
    return entries


def cleanBraketes(textLines):
    newLines = []


def matchRotation(s1, s2):
    name_permutation = [" ".join(x) for x in list(
        itertools.permutations(s1.split()))]
    return s2 in name_permutation


nameRegex = "^(([A-Z]*\s*)*)"


def breakIntoSpeeches(doc):

    speeches = []
    for i in range(confine_index(doc["text"])[1], len(doc["text"])):
        # print(i)
        res = re.findall(nameRegex, doc["text"][i])[0][0]
        if len(res) > 1 and any([matchRotation(x, str.strip(res)) for x in doc["speakers"]]):
            #print(str(i) + " >> " + res)
            speeches.append({"speaker": res, "index": i})

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
        segment = " ".join(segment)
        segment = re.sub("[\(\[].*?[\)\]]", "", segment)
        lonelyPar = segment.find("(")
        if lonelyPar != -1:
            segment = segment[:lonelyPar]
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

for d in tqdm(data, desc="Parsing 18th legislature (1/2)"):
    d["text"] = inLines(d["text"])
    extracted = extractSpeakers(d)
    d["speakers"] = [e.upper() for e in extracted]


documentIntoSpeeches = list(itertools.chain.from_iterable(
    [breakIntoSpeeches(x) for x in tqdm(data, desc="Parsing 18th legislature (2/2)")]))


documentIntoSpeeches = [{"speaker": item["speaker"], "segment":cleanSegment(
    item["segment"], item["speaker"])} for item in documentIntoSpeeches]

with open('parsed_18.json', 'w') as outfile:
    json.dump(documentIntoSpeeches, outfile, indent=4)
