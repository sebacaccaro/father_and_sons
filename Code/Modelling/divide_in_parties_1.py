import json

with open("./deputies_tokenized_1.json") as f:
    dep_tok = json.load(f)

parties = {"DC": ["DE GASPERI", "MORO ALDO", "SCALFARO", "FANFANI", "GRONCHI", "SEGNI", "LEONE", "RUMOR", "ANDREOTTI"],
           "PCI": ["TOGLIATTI", "AMENDOLA GIORGIO", "DI VITTORIO", "GIOLITTI", "INGRAO", "IOTTI", "PAJETTA GIANCARLO", "LONGO"],
           "PSI": ["NENNI PIETRO", "MATTEOTTI CARLO", "BASSO", "MANCINI", "DE MARTINO FRANCESCO"],
           "PSDI": ["CALAMANDREI", "SARAGAT"],
           "PRI": ["LA MALFA", "PACCIARDI"],
           "PLI": ["MARTINO GAETANO"],
           "MISTO": ["RUSSO PEREZ", "ALMIRANTE"],
           "MONARCHICO": ["COVELLI"]}


parties = {party: {dep: dep_tok[dep] for dep in parties[party]}
           for party in parties.keys()}

with open("parties_tokenized_1.json", "w") as f:
    json.dump(parties, f, indent=2)
