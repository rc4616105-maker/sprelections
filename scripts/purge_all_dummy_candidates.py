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

for h_code, file_path in house_files.items():
    cands = cand_by_house[h_code]
    cands_json = json.dumps(cands, indent=4)
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Replace allCandidates if present
    content = re.sub(r'"allCandidates":\s*\[[\s\S]*?\n\s*\]', lambda m: f'"allCandidates": {cands_json}', content)
    # Replace houseCandidates if present
    content = re.sub(r'"houseCandidates":\s*\[[\s\S]*?\n\s*\]', lambda m: f'"houseCandidates": {cands_json}', content)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"Purged dummy candidates from {file_path}")

# Check all house files
for h_code, file_path in house_files.items():
    content = open(file_path, encoding="utf-8").read()
    if "Arjun Verma" in content:
        print(f"ERROR: Arjun Verma still found in {file_path}")
    else:
        print(f"CONFIRMED CLEAN: {file_path}")
