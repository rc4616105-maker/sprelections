import json

with open('Houses/assets/all-candidates.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('window.ALL_CONTESTING_CANDIDATES = ')
cands = json.loads(text[idx+35:-2])

by_house_pos = {}
for c in cands:
    h = c.get('houseCode')
    p = c.get('positionId')
    by_house_pos.setdefault((h, p), []).append(c)

print("Houses and positions mapped:")
for (h, p), list_c in sorted(by_house_pos.items()):
    print(f"({h}, {p}): {len(list_c)} candidates. Sample: {list_c[0]['fullName']}")
