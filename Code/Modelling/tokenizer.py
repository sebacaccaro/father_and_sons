import importlib.machinery
from multiprocessing import cpu_count, pool
from sklearn.decomposition import LatentDirichletAllocation
import nltk
import re
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from spellchecker import SpellChecker
import spellchecker
from tqdm import tqdm
import multiprocessing
import json
import sys
from os import path

CORRECTION_ACTIVE = False
leg_num = sys.argv[1]

if CORRECTION_ACTIVE:
    from world_frequency_creator import create_freq_file
    create_freq_file(leg_num)
    from anagram_hash_algorythm import TICCL_use


# Intialization
nltk.download('stopwords')
nltk.download('punkt')
stopwords = set(stopwords.words('italian'))
stemmer = SnowballStemmer('italian')
spell = SpellChecker()
spell.word_frequency.load_text_file("./parole_uniche.json")


def map_fn(token):
    correction = {"key": token, "value": TICCL_use(token)}
    return correction


def tokenize_correct(sentence):
    # Text normalization and stemming
    tokens = nltk.word_tokenize(sentence)
    tokens = [t.lower() for t in tokens]  # All words to lowecase
    #tokens = [t[t.find("'"):] for t in tokens]
    for t in tokens:
        apostrofoPos = t.find("'")
        if apostrofoPos > -1:
            t = t[apostrofoPos:]
    tokens = [re.sub('[^a-z]+', '', t) for t in tokens]
    tokens = [t for t in tokens if len(t) > 0]
    tokens = [t for t in tokens if t not in stopwords]
    if int(leg_num) < 15 and CORRECTION_ACTIVE:
        corrected = [map_fn(x) for x in spell.unknown(tokens)]
        corrected = {x["key"]: x["value"] for x in corrected}
        for i in range(len(tokens)):
            if tokens[i] in corrected.keys():
                tokens[i] = corrected[tokens[i]]
    tokens = [stemmer.stem(x) for x in tokens]
    return tokens


with open(f"../Parsing/leader_grouped_{leg_num}.json") as f:
    data = json.load(f)

processed = {}
if path.exists(f"deputies_tokenized_{leg_num}.json"):
    with open(f"deputies_tokenized_{leg_num}.json") as f:
        processed = json.load(f)

pool1 = multiprocessing.Pool()
deps = list(data.keys())
i = 0
for deputy in tqdm(data, desc=f"Tokenizing speeches ({leg_num} legislature)"):
    if deputy not in processed.keys() and deputy != "PRESIDENTE":
        dep_speeches = pool1.map(tokenize_correct, data[deputy])
        processed[deputy] = dep_speeches
        i += 1
        with open(f"deputies_tokenized_{leg_num}.json", "w") as f:
            json.dump(processed, f, indent=2)
pool1.close()
