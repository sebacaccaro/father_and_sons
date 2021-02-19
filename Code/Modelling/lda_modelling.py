import numpy as np
import pandas as pd
from tqdm import tqdm
import json
import nltk
from nltk.corpus import stopwords
from sklearn.decomposition import LatentDirichletAllocation
from collections import defaultdict
from itertools import chain
from spellchecker import SpellChecker
from nltk.stem.snowball import SnowballStemmer
import random
import sys
##########################
N_GRAM_SIZE = 1
TRAIN_PERCENTAGE = 0.85
#########################
NUM_TOPICS = int(sys.argv[1])

spell = SpellChecker()
spell.word_frequency.load_text_file("./parole_uniche_stemmed.json")


results = {}

print(f"NUM = {NUM_TOPICS}")


def n_grams(word_list, n):
    return ["_".join([word_list[j] for j in range(i, i+n)]) for i in range(len(word_list)-n+1)] if len(word_list) >= n else []


def lda_model(tokenized_speeches, party_name):
    I = defaultdict(lambda: defaultdict(lambda: 0))
    I_test = defaultdict(lambda: defaultdict(lambda: 0))
    # filter out unary words
    random.shuffle(tokenized_speeches)
    for i in range(len(tokenized_speeches)):
        tokenized_speeches[i] = [
            t for t in tokenized_speeches[i] if len(t) > 1]
        tokenized_speeches[i] = n_grams(tokenized_speeches[i], N_GRAM_SIZE)

    train_split = int(len(tokenized_speeches) * TRAIN_PERCENTAGE)
    test_split = len(tokenized_speeches) - train_split
    #print(train_split, test_split)

    # Vectorizing train_set & test_set
    for doc, tokens in enumerate(tokenized_speeches):
        for token in tokens:
            I[doc][token] += 1

    X = pd.DataFrame(I)
    X.fillna(0, inplace=True)

    X_test = X.iloc[:, train_split:]
    X = X.iloc[:, :train_split]
    X = X.T
    X_test = X_test.T

    #X_test.fillna(0, inplace=True)

    lda = LatentDirichletAllocation(n_components=NUM_TOPICS)
    theta = lda.fit_transform(X)
    perplexity = lda.perplexity(X)

    test_theta = lda.transform(X_test)
    test_perplexity = lda.perplexity(X_test)

    phi = lda.components_ / lda.components_.sum(axis=1)[:, np.newaxis]

    # print(
    #    f"Train perplexity: {perplexity}\n Test perplexity: {test_perplexity} \n **********")

    out = {"topic-docs": {}, "topic-words": {},
           "train_perplexity": perplexity, "test_perplexity": test_perplexity}

    for topic in range(NUM_TOPICS):
        out["topic-docs"][topic] = {}
        for i, x in sorted(enumerate(theta[:, topic]), key=lambda y: -y[1]):
            out["topic-docs"][topic][i] = x
            #print(i, x)
            # print(documents[docs[i]], '\n')

    for topic in range(NUM_TOPICS):
        #print(f"****  TOPIC {topic} *******")
        out["topic-words"][topic] = {}
        for i, x in sorted(enumerate(phi[topic, :]), key=lambda y: -y[1])[:20]:
            # print(i, x)
            out["topic-words"][topic][X.columns[i]] = x
            #print(f"{X.columns[i]} -- {x}")
        # print("\n")

    results[party_name] = out

    with open("lda_results.json", "w") as f:
        json.dump(results, f, indent=2)


tokenized_parties = {}
for leg_num in [1, 12, 17, 18]:
    with open(f"./parties_tokenized_{leg_num}.json") as f:
        tp = json.load(f)
    for key in tp:
        tokenized_parties[f"{leg_num}_{key}"] = tp[key]

for party in tokenized_parties:
    tokenized_parties[party] = list(chain(*tokenized_parties[party].values()))

for party in tokenized_parties.keys():
    for i in range(len(tokenized_parties[party])):
        un = spell.unknown(tokenized_parties[party][i])
        tokenized_parties[party][i] = [
            w for w in tokenized_parties[party][i] if w not in un]

for party in tqdm(tokenized_parties.keys(), desc="Modelling parties"):
    lda_model(tokenized_parties[party], party)
