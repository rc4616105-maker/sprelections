import json

with open('Houses/gurudrona/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

data = json.loads(text[text.find('{'):text.rfind('}')+1])
cands = data.get('houseCandidates', [])
print(f'Total candidates in Gurudrona: {len(cands)}')
for c in cands:
    print(c.get('fullName'), '|', c.get('positionId'), '|', c.get('positionName'), '|', c.get('symbolObj', {}).get('name'))
