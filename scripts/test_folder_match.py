import os
import glob
import re
import json

base = "1docs/contestets"

folder_list = []

def norm(s):
    return re.sub(r'[^a-zA-Z0-9]', '', str(s).lower())

# 1. House Folders
HOUSE_DIRS = {
    "bheeshma": "BHEESHMA",
    "gurudrona": "GURUDRONA",
    "hanuman": "HANUMAN",
    "hanuman house": "HANUMAN",
    "karan house": "KARNA",
    "karna": "KARNA",
    "vasistha house": "VASISTHA",
    "vasistha": "VASISTHA",
    "vishwamithra": "VISHWAMITHRA"
}

for hdir in sorted(os.listdir(base)):
    hpath = os.path.join(base, hdir)
    if not os.path.isdir(hpath) or hdir == "School Cabinet":
        continue
    h_code = None
    for k, v in HOUSE_DIRS.items():
        if k in hdir.lower():
            h_code = v
            break
    if not h_code:
        continue
    for cfolder in sorted(os.listdir(hpath)):
        cpath = os.path.join(hpath, cfolder)
        if os.path.isdir(cpath):
            folder_list.append({
                'house': h_code,
                'folder_name': cfolder,
                'path': cpath,
                'category': 'House',
                'clean_fn': f"{h_code.lower()}_{norm(cfolder)}.jpg"
            })

# 2. Cabinet Folders
CABINET_ROLES = {
    "president": ("PRESIDENT", "School President"),
    "vice president": ("VICE_PRESIDENT", "School Vice President"),
    "literary secretary": ("LITERARY_SECRETARY", "Literary Secretary"),
    "sports secretary": ("SPORTS_SECRETARY", "Sports Secretary"),
    "social and cultural secretary": ("SOCIAL_CULTURAL_SECRETARY", "Social & Cultural Secretary")
}

cab_base = os.path.join(base, "School Cabinet")
if os.path.isdir(cab_base):
    for rdir in sorted(os.listdir(cab_base)):
        rpath = os.path.join(cab_base, rdir)
        if os.path.isdir(rpath):
            r_info = None
            for k, v in CABINET_ROLES.items():
                if k in rdir.lower():
                    r_info = v
                    break
            if not r_info:
                continue
            for cfolder in sorted(os.listdir(rpath)):
                cpath = os.path.join(rpath, cfolder)
                if os.path.isdir(cpath):
                    folder_list.append({
                        'house': 'CENTRAL',
                        'positionId': r_info[0],
                        'positionName': r_info[1],
                        'folder_name': cfolder,
                        'path': cpath,
                        'category': 'Cabinet',
                        'clean_fn': f"central_{r_info[0].lower()}_{norm(cfolder)}.jpg"
                    })

print(f"Total folders loaded: {len(folder_list)}")

# Load all-candidates.js
with open('Houses/assets/all-candidates.js', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'window\.ALL_CONTESTING_CANDIDATES = (\[.*?\]);', text, re.DOTALL)
existing = json.loads(m.group(1))

print(f"Total existing candidates: {len(existing)}")

# Match each existing candidate to its folder
matched = 0
unmatched = []

for c in existing:
    c_photo = c.get('photoPath', '').replace('../assets/candidates/', '')
    c_h = c.get('houseCode', '')
    c_pos = c.get('positionId', '')
    c_fn = c['fullName']
    
    # Try match by photo filename
    f_match = None
    for f in folder_list:
        if f['house'] == c_h:
            # check if photo matches
            if norm(f['folder_name']) in norm(c_photo) or norm(c_photo) in norm(f['folder_name']):
                f_match = f
                break
            # check if name matches
            if norm(f['folder_name']) == norm(c_fn) or norm(f['folder_name']) in norm(c_fn) or norm(c_fn) in norm(f['folder_name']):
                f_match = f
                break
                
    if f_match:
        matched += 1
        c['target_folder_name'] = f_match['folder_name']
    else:
        unmatched.append((c_h, c_fn, c_photo))

print(f"Matched: {matched}/{len(existing)}")
if unmatched:
    print("Unmatched:")
    for u in unmatched:
        print(" ", u)
