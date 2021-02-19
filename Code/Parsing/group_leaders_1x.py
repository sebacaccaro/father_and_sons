import json
import sys

leg_num = int(sys.argv[1])
text_field_name = "text" if leg_num < 15 else "segment"

print(f"Grouping speeches by leader ({leg_num} legislature)")

with open(f"parsed_{leg_num}.json") as f:
    speeches = json.load(f)

leaders_speeches = list(set([s["speaker"] for s in speeches]))
leaders_speeches = {
    l: [s[text_field_name] for s in speeches if s["speaker"] == l] for l in leaders_speeches}


count = sorted([{"speaker": l, "count": len(leaders_speeches[l])}
                for l in leaders_speeches.keys()], key=lambda l: l["count"])

with open(f"leader_grouped_{leg_num}.json", "w") as f:
    json.dump(leaders_speeches, f, indent=2)
