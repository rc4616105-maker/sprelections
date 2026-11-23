import os, json, re, shutil, hashlib

BASE_1DOCS = "1docs/contestets"
HOUSES_DIR = "Houses/assets/candidates"
RESULT_DIR = "Result declaration/assets/candidates"

os.makedirs(HOUSES_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)

# Helper to normalize string
def norm(s):
    return re.sub(r'[^a-zA-Z0-9]', '', s).lower()

parsed_candidates = []

# Scan 1docs/contestets
for root, dirs, files in os.walk(BASE_1DOCS):
    # Skip root
    if root == BASE_1DOCS:
        continue
    rel = os.path.relpath(root, BASE_1DOCS)
    parts = rel.split(os.sep)
    
    # Check if this folder has an image or txt
    imgs = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png')) and not f.startswith('symbol')]
    txts = [f for f in files if f.endswith('.txt')]
    
    if not imgs and not txts:
        continue
    
    # Determine house and post
    house_raw = parts[0]
    folder_name = parts[-1]
    subfolder = parts[1] if len(parts) > 2 else ""
    
    txt_content = ""
    if txts:
        with open(os.path.join(root, txts[0]), 'r', encoding='utf-8', errors='ignore') as fp:
            txt_content = fp.read().strip()
            
    parsed_candidates.append({
        "rel": rel,
        "parts": parts,
        "house_raw": house_raw,
        "subfolder": subfolder,
        "folder_name": folder_name,
        "img": imgs[0] if imgs else None,
        "img_path": os.path.join(root, imgs[0]) if imgs else None,
        "txt": txt_content
    })

print(f"Total candidates scanned from 1docs: {len(parsed_candidates)}")

# Print summary
for c in parsed_candidates[:15]:
    print(f"[{c['house_raw']}] Folder: {c['folder_name']} | Img: {c['img']} | Txt: {c['txt'][:40]}")
