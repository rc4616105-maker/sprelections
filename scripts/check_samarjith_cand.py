import json, re

with open("Result declaration/js/candidates-data.js", "r", encoding="utf-8") as f:
    text = f.read()

m = re.search(r'window\.ALL_CONTESTING_CANDIDATES\s*=\s*(\[[\s\S]*?\]);', text)
cands = json.loads(m.group(1))

for c in cands:
    if "samarjith" in c['fullName'].lower():
        print(json.dumps(c, indent=2))
