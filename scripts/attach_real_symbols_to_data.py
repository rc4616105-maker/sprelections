import json
import re

with open('Result declaration/js/candidates-data.js', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'window\.ALL_CONTESTING_CANDIDATES = (\[.*?\]);', text, re.DOTALL)
all_candidates = json.loads(m.group(1))

# Build lookup by normalized name
cands_by_name = {}
for c in all_candidates:
    fn = c['fullName'].strip().lower()
    cands_by_name[fn] = c
    simplified = re.sub(r'[\.\s]+', '', fn)
    cands_by_name[simplified] = c

with open('Result declaration/js/data.js', 'r', encoding='utf-8') as f:
    data_js = f.read()

m_houses = re.search(r'const DEFAULT_HOUSES = (\[.*?\]);\s*const DEFAULT_CABINET_POSTS = (\[.*?\]);', data_js, re.DOTALL)
houses = json.loads(m_houses.group(1))
cabinet = json.loads(m_houses.group(2))

def attach_symbol_and_photo(cand, house_code=None):
    name = cand.get('name', '').strip()
    fn = name.lower()
    simplified = re.sub(r'[\.\s]+', '', fn)
    
    match = cands_by_name.get(fn) or cands_by_name.get(simplified)
    if not match:
        for k, v in cands_by_name.items():
            if (fn in k or k in fn) and (not house_code or v.get('houseCode', '').upper() == house_code.upper()):
                match = v
                break
                
    if match:
        sym = match.get('symbolObj', {})
        cand['symbolName'] = sym.get('name', '')
        cand['symbolIcon'] = sym.get('icon', '🗳️')
        cand['symbolImagePath'] = sym.get('imagePath', '').replace('../', '')
        cand['symbol'] = {
            'name': sym.get('name', ''),
            'icon': sym.get('icon', '🗳️'),
            'imagePath': sym.get('imagePath', '').replace('../', '')
        }
        if match.get('photoPath'):
            cand['photo'] = match['photoPath'].replace('../', '')
        print(f"Matched {name} -> {cand['symbolName']} ({cand['symbolIcon']}) | Photo: {cand['photo']}")
    else:
        print(f"NO MATCH for {name} ({house_code})")

for h in houses:
    for k, cand in h['candidates'].items():
        attach_symbol_and_photo(cand, h['id'])

for p in cabinet:
    cand = p.get('candidate', {})
    attach_symbol_and_photo(cand, 'CENTRAL')

# Re-write Result declaration/js/data.js cleanly
houses_json = json.dumps(houses, indent=2, ensure_ascii=False)
cabinet_json = json.dumps(cabinet, indent=2, ensure_ascii=False)

prefix = data_js[:m_houses.start()]
suffix = data_js[m_houses.end():]

new_data_js = f"{prefix}const DEFAULT_HOUSES = {houses_json};\n\nconst DEFAULT_CABINET_POSTS = {cabinet_json};{suffix}"

with open('Result declaration/js/data.js', 'w', encoding='utf-8') as f:
    f.write(new_data_js)

print("Updated Result declaration/js/data.js with real symbols & photos successfully!")
