import os, re, json

with open("scripts/new_candidates_clean.json", "r", encoding="utf-8") as f:
    cand_by_house = json.load(f)

house_files = {
    "BHEESHMA": "Houses/bheeshma/data.js",
    "GURUDRONA": "Houses/gurudrona/data.js",
    "HANUMAN": "Houses/hanuman/data.js",
    "KARNA": "Houses/karna/data.js",
    "VASISTHA": "Houses/vasistha/data.js",
    "VISHWAMITHRA": "Houses/vishwamithra/data.js",
}

all_admin_candidates = []

for h_code, file_path in house_files.items():
    cands = cand_by_house[h_code]
    all_admin_candidates.extend(cands)
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Format cands as clean JS
    cands_json = json.dumps(cands, indent=4)
    # Replace the houseCandidates array
    # Regex find "houseCandidates": \[ ... \]
    pattern = r'"houseCandidates":\s*\[[\s\S]*?\n\s*\]'
    replacement = f'"houseCandidates": {cands_json}'
    
    new_content, count = re.subn(pattern, lambda m: replacement, content)
    if count == 0:
        print(f"Warning: houseCandidates not found in {file_path}")
    else:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated {file_path} with {len(cands)} real candidates.")

# Now update Houses/admin/data.js
admin_file = "Houses/admin/data.js"
with open(admin_file, "r", encoding="utf-8") as f:
    admin_content = f.read()

all_cands_json = json.dumps(all_admin_candidates, indent=4)
pattern = r'"candidates":\s*\[[\s\S]*?\n\s*\]'
replacement = f'"candidates": {all_cands_json}'

new_admin, a_count = re.subn(pattern, lambda m: replacement, admin_content)
if a_count == 0:
    print(f"Warning: candidates array not found in {admin_file}")
else:
    with open(admin_file, "w", encoding="utf-8") as f:
        f.write(new_admin)
    print(f"Updated {admin_file} with {len(all_admin_candidates)} real candidates across all 6 houses.")

print("\nSUCCESS: All house kiosks and admin console have been updated with real candidates!")
