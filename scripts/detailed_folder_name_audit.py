import os
import glob
import re
import json

base = "1docs/contestets"

all_folders = []

# Scan House folders
for h in sorted(os.listdir(base)):
    hpath = os.path.join(base, h)
    if not os.path.isdir(hpath) or h == "School Cabinet":
        continue
    for cfolder in sorted(os.listdir(hpath)):
        cpath = os.path.join(hpath, cfolder)
        if os.path.isdir(cpath):
            img_files = [f for f in os.listdir(cpath) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            txt_files = [f for f in os.listdir(cpath) if f.lower().endswith('.txt')]
            txt_content = ""
            if txt_files:
                try:
                    with open(os.path.join(cpath, txt_files[0]), 'r', encoding='utf-8', errors='ignore') as f:
                        txt_content = f.read().strip()
                except:
                    pass
            all_folders.append({
                'category': 'House',
                'house': h,
                'folder_name': cfolder,
                'path': cpath,
                'images': img_files,
                'txt': txt_content
            })

# Scan School Cabinet folders
cab_base = os.path.join(base, "School Cabinet")
if os.path.isdir(cab_base):
    for r in sorted(os.listdir(cab_base)):
        rpath = os.path.join(cab_base, r)
        if os.path.isdir(rpath):
            for cfolder in sorted(os.listdir(rpath)):
                cpath = os.path.join(rpath, cfolder)
                if os.path.isdir(cpath):
                    img_files = [f for f in os.listdir(cpath) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                    txt_files = [f for f in os.listdir(cpath) if f.lower().endswith('.txt')]
                    txt_content = ""
                    if txt_files:
                        try:
                            with open(os.path.join(cpath, txt_files[0]), 'r', encoding='utf-8', errors='ignore') as f:
                                txt_content = f.read().strip()
                        except:
                            pass
                    all_folders.append({
                        'category': 'Cabinet',
                        'role': r,
                        'folder_name': cfolder,
                        'path': cpath,
                        'images': img_files,
                        'txt': txt_content
                    })

print(f"Total folders found: {len(all_folders)}")

# Now let's see how each folder name maps to candidates in all-candidates.js
with open('Houses/assets/all-candidates.js', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'window\.ALL_CONTESTING_CANDIDATES = (\[.*?\]);', text, re.DOTALL)
existing = json.loads(m.group(1))

# Check how many of existing match folder_name exactly
perfect_matches = 0
differing_names = []
for c in existing:
    c_name = c['fullName'].strip()
    c_photo = c.get('photoPath', '')
    c_house = c.get('houseCode', '')
    
    # Try to find folder
    found = None
    for f in all_folders:
        # Match by photo or by name
        f_name = f['folder_name'].strip()
        # Does photo match?
        photo_match = False
        if f['images']:
            for img in f['images']:
                # The photo in assets was renamed like bheeshma_anikshitha.jpg
                # But let's check folder_name similarity
                pass
        
        # Check normalized name
        norm_c = re.sub(r'[^a-zA-Z0-9]', '', c_name.lower())
        norm_f = re.sub(r'[^a-zA-Z0-9]', '', f_name.lower())
        
        # Check house match
        h_match = False
        if f['category'] == 'Cabinet' and c_house == 'CENTRAL':
            h_match = True
        elif f['category'] == 'House' and c_house.upper() in f['house'].upper().replace('HOUSE', ''):
            h_match = True
            
        if h_match and (norm_c == norm_f or norm_c in norm_f or norm_f in norm_c):
            found = f
            break
            
    if found:
        f_name = found['folder_name'].strip()
        if f_name == c_name:
            perfect_matches += 1
        else:
            differing_names.append((c_name, f_name, c_house, c['positionId']))
    else:
        differing_names.append((c_name, "NOT FOUND IN FOLDERS", c_house, c['positionId']))

print(f"Perfect matches: {perfect_matches}")
print(f"Differing names count: {len(differing_names)}")
print("\nSample differing names (Current in JS -> Folder Name):")
for cur, fld, h, pos in differing_names:
    print(f"  [{h}] '{cur}' => '{fld}' ({pos})")
