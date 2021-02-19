import json
from difflib import SequenceMatcher

print(f"Grouping speeches by leader ({1} legislature)")

with open("parsed_1.json") as f:
    speeches = json.load(f)

interested_in = ["MORO",
                 "SCALFARO",
                 "DE GASPERI",
                 "FANFANI",
                 "GRONCHI",
                 "SEGNI",
                 "LEONE",
                 "RUMOR",
                 "ANDREOTTI",
                 "TOGLIATTI",
                 "AMENDOLA",
                 "DI VITTORIO",
                 "GIOLITTI",
                 "INGRAO",
                 "IOTTI",
                 "PAJETTA",
                 "LONGO",
                 "NENNI",
                 "MATTEOTTI",
                 "BASSO",
                 "MANCINI",
                 "DE MARTINO",
                 "CALAMANDREI",
                 "SARAGAT",
                 "MARTINO",
                 "LA MALFA",
                 "PACCIARDI",
                 "ALMIRANTE",
                 "RUSSO",
                 "COVELLI",
                 "AMENDOLA GIORGIO",
                 "DE MARTINO FRANCESCO",
                 "MARTINO GAETANO",
                 "MATTEOTTI CARLO",
                 "MORO ALDO",
                 "NENNI PIETRO",
                 "PAJETTA GIANCARLO",
                 "RUSSO PEREZ"]


leaders_speeches = list(set([s["speaker"] for s in speeches]))
leaders_speeches = {
    l: [s["text"] for s in speeches if s["speaker"] == l] for l in interested_in}


# Pulizia ad hoc per i deputati LEONE, E RUSSO
leaders_speeches["LEONE"] = [l for l in leaders_speeches["LEONE"]
                             if SequenceMatcher(None, l[:22], "MARCHESANO").ratio() < 0.3]
leaders_speeches["RUSSO PEREZ"] = [
    *leaders_speeches["RUSSO PEREZ"]], *leaders_speeches["RUSSO"]
del(leaders_speeches["RUSSO"])
leaders_speeches["RUSSO PEREZ"] = [l for l in leaders_speeches["RUSSO PEREZ"]
                                   if SequenceMatcher(None, l[5:25], "PEREZ").ratio() > 0.2]
count = sorted([{"speaker": l, "count": len(leaders_speeches[l])}
                for l in leaders_speeches.keys()], key=lambda l: l["count"])

with open("leader_grouped_1.json", "w") as f:
    json.dump(leaders_speeches, f, indent=2)
