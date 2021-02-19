import sys
import json
from os import error
import re
regex = re.compile('[^a-zA-Z]')

leg_num = int(sys.argv[1])

try:
    if len(sys.argv) < 2:
        raise(ValueError("Devi inseire il numero di legislatura come argomento"))
    leg_num = int(sys.argv[1])
    if leg_num not in [1, 12, 17, 18]:
        raise(ValueError("La legislatura deve essere fra 1,12,17,18"))
except ValueError as ve:
    print(f"{ve.__class__}: {ve}")
except Exception as e:
    print(f"C'è stato un errore negli argomenti: {e}")


def normalize(dp): return regex.sub('', str.lower(dp).replace(" ", ""))


def invertedDict(diz):
    newDict = {}
    for key in diz:
        for value in diz[key]:
            newDict[value] = key
    return newDict


with open(f"./deputies_tokenized_{leg_num}.json") as f:
    depTokenized = json.load(f)


with open(f"./dep_parties_{leg_num}.json") as f:
    partyDep = json.load(f)
    parties = partyDep.keys()
    for key in partyDep:
        partyDep[key] = [normalize(d) for d in partyDep[key]]
    partyDep = invertedDict(partyDep)

output = {p: {} for p in parties}

for dep in depTokenized.keys():
    dp = normalize(dep)
    if dp in partyDep:
        output[partyDep[dp]][dep] = depTokenized[dep]

output = {k: output[k] for k in output.keys() if len(output[k]) > 0}


with open(f"parties_tokenized_{leg_num}.json", "w") as f:
    json.dump(output, f, indent=2)
