import os
import glob
import json
import re

with open('Houses/assets/all-candidates.js', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'window\.ALL_CONTESTING_CANDIDATES = (\[.*?\]);', text, re.DOTALL)
existing = json.loads(m.group(1))

print(f"Total candidates in all-candidates.js: {len(existing)}")

# Map existing by photo filename or normalized name
cand_map = {}
for c in existing:
    cand_map[c['id']] = c

# Scan 1docs/contestets
base = "1docs/contestets"

folder_candidates = []

# 1. Houses
for house_dir in sorted(os.listdir(base)):
    hpath = os.path.join(base, house_dir)
    if not os.path.isdir(hpath) or house_dir == "School Cabinet":
        continue
    for cand_folder in sorted(os.listdir(hpath)):
        cpath = os.path.join(hpath, cand_folder)
        if os.path.isdir(cpath):
            folder_candidates.append({
                'category': 'House',
                'house': house_dir,
                'folder_name': cand_folder,
                'path': cpath
            })

# 2. School Cabinet
cab_base = os.path.join(base, "School Cabinet")
if os.path.isdir(cab_base):
    for role_dir in sorted(os.listdir(cab_base)):
        rpath = os.path.join(cab_base, role_dir)
        if os.path.isdir(rpath):
            for cand_folder in sorted(os.listdir(rpath)):
                cpath = os.path.join(rpath, cand_folder)
                if os.path.isdir(cpath):
                    folder_candidates.append({
                        'category': 'Cabinet',
                        'role': role_dir,
                        'folder_name': cand_folder,
                        'path': cpath
                    })

print(f"Total candidate folders in 1docs/contestets: {len(folder_candidates)}")

# Print comparisons
for fc in folder_candidates[:25]:
    fname = fc['folder_name']
    cat = fc.get('house') or fc.get('role')
    # Find in existing
    match = None
    for c in existing:
        # Check if folder name matches or photo matches
        en = c['fullName']
        if en.lower() == fname.lower() or fname.lower().endswith(en.lower()) or en.lower().endswith(fname.lower()):
            match = c
            break
        # also check without initials / dots
        en_clean = re.sub(r'[\.\s]+', '', en.lower())
        fn_clean = re.sub(r'[\.\s]+', '', fname.lower())
        if en_clean == fn_clean or en_clean in fn_clean or fn_clean in en_clean:
            match = c
            break
    print(f"[{cat}] Folder: '{fname}' => Current JS: '{match['fullName'] if match else 'NO MATCH'}'")
