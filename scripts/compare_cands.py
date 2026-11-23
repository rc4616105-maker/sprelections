import json, os, re, hashlib

def norm(s):
    return re.sub(r'[^a-zA-Z0-9]', '', str(s)).lower()

with open('Houses/assets/all-candidates.js', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'window\.ALL_CONTESTING_CANDIDATES\s*=\s*(\[[\s\S]*?\]);', text)
js_cands = json.loads(m.group(1))
print(f"Loaded {len(js_cands)} from all-candidates.js")

# Let's import parsed 1docs
from reconcile_all_contestants import parsed_candidates

print(f"Loaded {len(parsed_candidates)} from 1docs/contestets")

# Map by name and house
mapped = []
unmapped_js = []
unmapped_docs = list(parsed_candidates)

for jc in js_cands:
    jname = norm(jc['fullName'])
    jhouse = norm(jc['houseCode'])
    if 'cabinet' in jhouse or 'central' in jhouse:
        jhouse = 'cabinet'
    
    match = None
    for dc in unmapped_docs:
        dname = norm(dc['folder_name'])
        dhouse = norm(dc['house_raw'])
        if 'cabinet' in dhouse or 'central' in dhouse:
            dhouse = 'cabinet'
            
        if jhouse == dhouse:
            # Check name match
            if jname == dname or jname in dname or dname in jname:
                match = dc
                break
    
    if match:
        mapped.append((jc, match))
        unmapped_docs.remove(match)
    else:
        unmapped_js.append(jc)

print(f"\nSuccessfully matched: {len(mapped)} candidates")
print(f"Unmatched in JS: {len(unmapped_js)}")
for uj in unmapped_js:
    print(f"  JS unmatched: {uj['fullName']} ({uj['houseCode']})")

print(f"\nUnmatched in 1docs: {len(unmapped_docs)}")
for ud in unmapped_docs:
    print(f"  1docs unmatched: {ud['folder_name']} ({ud['house_raw']} / {ud['subfolder']})")
