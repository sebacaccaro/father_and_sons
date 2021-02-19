import nltk
import json
from tqdm import tqdm


def create_freq_file(leg_num):
    print(
        f"Creating word frequency for correction ({leg_num} legislature). This may take a while")
    with open(f"../Parsing/parsed_{leg_num}.json") as f:
        speeches = json.load(f)

    with open("./parole_uniche.json") as f:
        words = json.load(f)

    speeches = [s["text"] for s in speeches]

    words_extracted = {}
    for s in tqdm(speeches):
        tokens = nltk.word_tokenize(s)
        for t in tokens:
            tlow = t.lower()
            if not tlow in words_extracted.keys():
                words_extracted[tlow] = 0
            words_extracted[tlow] += 1

    words_not_ok = []
    words_not_ok = [w for w in tqdm(
        words_extracted.keys()) if words_extracted[w] == 1 or w in words_not_ok or w not in words]

    for w in words_not_ok:
        del(words_extracted[w])

    with open("freq_dict.json", "w") as f:
        json.dump(words_extracted, f, indent=2)
