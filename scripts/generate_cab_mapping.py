import json
import openpyxl

wb = openpyxl.load_workbook('1docs/OFFICIAL_STUDENT_VOTER_IDS_2026.xlsx', data_only=True)
sheet = wb.active

roster = []
for r in range(2, sheet.max_row + 1):
    vid = str(sheet.cell(r, 2).value or '').strip()
    name = str(sheet.cell(r, 3).value or '').strip()
    cls = str(sheet.cell(r, 4).value or '').strip()
    sec = str(sheet.cell(r, 5).value or '').strip()
    gender = str(sheet.cell(r, 6).value or '').strip()
    house = str(sheet.cell(r, 7).value or '').strip().upper()
    if vid and name:
        roster.append({
            'vid': vid,
            'name': name,
            'cls': cls,
            'sec': sec,
            'gender': gender,
            'house': house
        })

with open('Houses/admin/data.js', 'r', encoding='utf-8') as f:
    c = f.read()
eq = c.find('=')
data = json.loads(c[eq+1:].strip().rstrip(';'))

cab_cands = [x for x in data.get('candidates', []) if x['houseCode'] == 'CENTRAL']

print(f"Loaded {len(roster)} roster students and {len(cab_cands)} cabinet candidates.")

mapping = []
for c in cab_cands:
    adm = str(c.get('admissionNo', '')).strip().upper()
    name = c.get('fullName', '').strip()
    role = c.get('positionName', c.get('positionId', ''))
    
    # Match in roster
    m = next((r for r in roster if r['vid'].upper() == adm), None)
    if not m:
        # Match by name
        m = next((r for r in roster if r['name'].lower() == name.lower()), None)
    if not m:
        # Match by partial name
        # token matching
        tokens = [t.lower().replace('.', '') for t in name.split() if len(t.replace('.', '')) > 2]
        best_match = None
        best_score = 0
        for r in roster:
            r_tokens = [t.lower().replace('.', '') for t in r['name'].split() if len(t.replace('.', '')) > 2]
            common = set(tokens).intersection(set(r_tokens))
            if len(common) > best_score:
                best_score = len(common)
                best_match = r
        if best_score >= 1:
            m = best_match

    matched_house = m['house'] if m else 'ALL'
    matched_vid = m['vid'] if m else adm
    matched_name = m['name'] if m else name
    cls_sec = f"{m['cls']} - {m['sec']}" if m else c.get('section', '')
    
    mapping.append({
        'candidateId': c['id'],
        'candidateAdm': adm,
        'voterId': matched_vid,
        'candidateName': name,
        'rosterName': matched_name,
        'houseCode': matched_house,
        'classSec': cls_sec,
        'role': role
    })

print(f"Generated mapping for {len(mapping)} candidates.")
with open('scripts/cab_mapping.json', 'w', encoding='utf-8') as f:
    json.dump(mapping, f, indent=2)

for item in mapping:
    print(f"[{item['houseCode']}] {item['candidateName']} | CandAdm: {item['candidateAdm']} | VoterID: {item['voterId']} | Role: {item['role']}")
