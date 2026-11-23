import json

houses = ['bheeshma', 'gurudrona', 'hanuman', 'karna', 'vasistha', 'vishwamithra']

for h in houses:
    with open(f'Houses/{h}/data.js', 'r', encoding='utf-8') as f:
        text = f.read()
    data = json.loads(text[text.find('{'):text.rfind('}')+1])
    cands = data['houseCandidates']
    print(f"\n====================== {h.upper()} ======================")
    for pos in ['CAPTAIN_BOY', 'CAPTAIN_GIRL', 'VICE_CAPTAIN_BOY', 'VICE_CAPTAIN_GIRL']:
        matched = [c for c in cands if c['positionId'] == pos]
        print(f" {pos} ({len(matched)} candidates):")
        for m in matched:
            sym_name = m.get('symbolObj', {}).get('name', 'None')
            print(f"   - {m['fullName']:20} | Symbol: {sym_name:18} | Photo: {m.get('photoUrl')}")
