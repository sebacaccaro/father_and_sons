from tqdm import tqdm
import json
from itertools import combinations, chain
from Levenshtein import distance  # 2https://github.com/ztane/python-Levenshtein/


def normalize(word):
    discardSet = [
        "@",
        "^",
        "ß",
        "•",
        "°",
        '̀',
        '̆',
        '̌'
    ]

    symbols = [
        "+",
        "%",
        "*",
        "#",
        "!",
        "(",
        "&",
        ")",
        "«",
        "»",
        "“",
        "”",
        "/",
        ":",
        ";",
        "=",
        "?",
    ]

    morph = {
        '′': "'",
        "ḥ": "h",
        "−": "-",
        "–": "-",
        "—": "-",
        "`": "'",
        "ª": "a",
        "à": "à",
        "á": "à",
        "ā": "à",
        "â": "à",
        "ä": "à",
        "è": "è",
        "é": "è",
        "ê": "è",
        "ë": "è",
        "ì": "ì",
        "í": "ì",
        "î": "i",
        "ï": "i",
        "ñ": "n",
        "ò": "o",
        "ó": "o",
        "ô": "o",
        "ö": "o",
        "ø": "o",
        "ù": "u",
        "ú": "u",
        "û": "u",
        "ü": "u",
        "ū": "u",
        "č": "c",
        "ç": "c",
        "‘": "'",
        "’": "'",
        "ğ": "g",
        "š": "s",
        "ž": "z"}
    word = list(word)
    for i in range(len(word)):
        # Changing all numers to zeros
        if word[i] in morph:
            word[i] = morph[word[i]]
        if word[i].isdigit():
            word[i] = "1"
        if word[i] in symbols:
            word[i] = "2"
    word = [w for w in word if w not in discardSet]
    return "".join(word)


with open("parole_uniche.json") as f:
    dictionary = json.load(f)
    dictionary = list(set([normalize(w.lower()) for w in dictionary]))

charSet = []
for word in dictionary:
    for char in set(word):
        if char.lower() not in charSet:
            charSet.append(char.lower())

charSet.sort()


# Empircally set number used in bad hash
HASH_N = 5


def badHash(word):
    chars = list(set(word))
    return sum([ord(char)**5 for char in chars])

# Building the Alphabet


def alphabetFromCharSet(charSet):
    alphabet = {}
    for i in range(1, 4):
        iAVs = ["".join(sorted(list(chain.from_iterable(c))))
                for c in list(combinations(charSet, i))]
        iAvs = {badHash(av): av for av in iAVs}
        alphabet = {**alphabet, **iAvs}
    return alphabet


def buildLexicon(dictionary):
    lexicon = {}
    for word in dictionary:
        bh = badHash(word)
        if bh in lexicon:
            lexicon[bh].append(word)
        else:
            lexicon[bh] = [word]
    return lexicon


def focuswordAlphabet(word):
    return alphabetFromCharSet(list(set(word))).keys()


# print(alphabetFromCharSet(charSet))
alphabet = alphabetFromCharSet(charSet)
lexicon = buildLexicon(dictionary)

with open("./freq_dict.json") as f:
    frequencies = json.load(f)

StdLDlimit = 3

# PRE alphabet
# PRE focusWord


def TICCL(focusWord, alphabet):
    focusWord = normalize(focusWord)
    results = []
    for counter1 in (1, 2):
        for counter2 in (1, 2):
            for alphabetValue in (alphabet):
                for focuswordAlphabetValue in focuswordAlphabet(focusWord):
                    newValue = badHash(focusWord) - (focuswordAlphabetValue *
                                                     counter1) + (alphabetValue * counter2)
                    if newValue in lexicon:
                        variants = lexicon[newValue]
                        LDlimit = 0
                        # if counter1 == 2 or counter2 == 2 and len(focusWord) > 9: Controllo, non si capisce a cosa serve
                        if len(focusWord) < 7:
                            LDlimit = 2
                        else:
                            LDlimit = 3
                        for variant in variants:
                            if distance(focusWord, variant) <= LDlimit:
                                results.append(variant)
    results = list(set(results))
    results = [{"res": r, "distance": distance(r, focusWord)} for r in results]
    #results = sorted(results, key=lambda x: x["distance"])
    return results


def TICCL_use(focusWord):
    res = TICCL(focusWord, alphabet)
    res = [{"res": r["res"], "distance": frequencies.get(
        r["res"], 0)*(10**-r["distance"])} for r in res]
    res.sort(key=lambda w: -w["distance"])
    return focusWord if len(res) == 0 else res[0]["res"]
#res = TICCL("0sservazioni", alphabet)
# print(res)
