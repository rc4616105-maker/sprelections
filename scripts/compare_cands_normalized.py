import json, os, re, hashlib, shutil

def norm_house(h):
    h = str(h).lower()
    if 'bheeshma' in h or 'bhishma' in h: return 'bheeshma'
    if 'guru' in h or 'drona' in h: return 'gurudrona'
    if 'hanuman' in h: return 'hanuman'
    if 'karan' in h or 'karna' in h: return 'karna'
    if 'vasis' in h: return 'vasistha'
    if 'vishwa' in h: return 'vishwamithra'
    if 'cabinet' in h or 'central' in h: return 'cabinet'
    return h

def norm_name(s):
    # Remove dots, spaces, special chars
    return re.sub(r'[^a-zA-Z0-9]', '', str(s)).lower()

from reconcile_all_contestants import parsed_candidates

with open('Houses/assets/all-candidates.js', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'window\.ALL_CONTESTING_CANDIDATES\s*=\s*(\[[\s\S]*?\]);', text)
js_cands = json.loads(m.group(1))

mapped = []
unmapped_js = []
unmapped_docs = list(parsed_candidates)

for jc in js_cands:
    jname = norm_name(jc['fullName'])
    jhouse = norm_house(jc['houseCode'])
    
    match = None
    for dc in unmapped_docs:
        dname = norm_name(dc['folder_name'])
        dhouse = norm_house(dc['house_raw'])
        
        if jhouse == dhouse:
            # Check name match
            if jname == dname or jname in dname or dname in jname:
                match = dc
                break
            # Also check text content in doc for candidate name
            dtxt = norm_name(dc['txt'])
            if jname in dtxt:
                match = dc
                break
    
    if match:
        mapped.append((jc, match))
        unmapped_docs.remove(match)
    else:
        unmapped_js.append(jc)

print(f"Total in JS: {len(js_cands)}")
print(f"Successfully matched: {len(mapped)} candidates")
print(f"Unmatched in JS: {len(unmapped_js)}")
for uj in unmapped_js:
    print(f"  JS unmatched: {uj['fullName']} ({uj['houseCode']})")

print(f"\nUnmatched in 1docs: {len(unmapped_docs)}")
for ud in unmapped_docs:
    print(f"  1docs unmatched: {ud['folder_name']} ({ud['house_raw']} / {ud['subfolder']})")
