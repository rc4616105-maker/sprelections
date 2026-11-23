import json, os, re

# Load verified master roster
with open("Houses/assets/all-candidates.js", "r", encoding="utf-8") as f:
    text = f.read()

m = re.search(r'window\.ALL_CONTESTING_CANDIDATES\s*=\s*(\[[\s\S]*?\]);', text)
master = json.loads(m.group(1))

from compare_cands_normalized import norm_name, norm_house

# Build lookup by (norm_name, norm_house)
lookup = {}
for c in master:
    k = (norm_name(c['fullName']), norm_house(c['houseCode']))
    lookup[k] = c
    # Also without house for unique names
    lookup[norm_name(c['fullName'])] = c

print(f"Lookup table built with {len(master)} candidates.")

booth_files = [
    "Houses/admin/data.js",
    "Houses/bheeshma/data.js",
    "Houses/gurudrona/data.js",
    "Houses/hanuman/data.js",
    "Houses/karna/data.js",
    "Houses/vasistha/data.js",
    "Houses/vishwamithra/data.js",
    "Houses/central/data.js"
]

for bf in booth_files:
    if not os.path.exists(bf):
        print(f"Skipping {bf} (not found)")
        continue
    
    with open(bf, "r", encoding="utf-8") as f:
        content = f.read()
    
    # We want to replace photoUrl and symbolObj for candidates
    # Let's see: if bf contains window.HOUSE_DATA = { ... }
    m_house = re.search(r'window\.HOUSE_DATA\s*=\s*(\{[\s\S]*\});?\s*$', content)
    if not m_house:
        print(f"Could not parse window.HOUSE_DATA in {bf}")
        continue
        
    try:
        data = json.loads(m_house.group(1))
    except Exception as e:
        print(f"JSON load failed for {bf}: {e}")
        continue
        
    house_slug = data.get("houseConfig", {}).get("slug", "")
    house_code = data.get("houseConfig", {}).get("code", "")
    
    # 1. Update positions candidates
    positions = data.get("positions", [])
    updated_cands = 0
    for pos in positions:
        for cand in pos.get("candidates", []):
            fn = cand.get("fullName", "")
            nh = norm_house(house_code or house_slug)
            meta = lookup.get((norm_name(fn), nh)) or lookup.get(norm_name(fn))
            if meta:
                cand["photoUrl"] = meta["photoUrl"]
                cand["photoPath"] = meta["photoPath"]
                cand["symbolObj"] = meta["symbolObj"]
                updated_cands += 1
                
    # 2. Update voters who are candidates
    voters = data.get("voters", [])
    updated_voters = 0
    for v in voters:
        if v.get("isCandidate"):
            fn = v.get("fullName", "")
            nh = norm_house(v.get("houseCode", house_code))
            meta = lookup.get((norm_name(fn), nh)) or lookup.get(norm_name(fn))
            if meta:
                v["photoUrl"] = meta["photoUrl"]
                updated_voters += 1
                
    # 3. Update candidates array if present at top level
    if "candidates" in data and isinstance(data["candidates"], list):
        for cand in data["candidates"]:
            fn = cand.get("fullName", "")
            nh = norm_house(cand.get("houseCode", house_code))
            meta = lookup.get((norm_name(fn), nh)) or lookup.get(norm_name(fn))
            if meta:
                cand["photoUrl"] = meta["photoUrl"]
                cand["photoPath"] = meta["photoPath"]
                cand["symbolObj"] = meta["symbolObj"]
                updated_cands += 1

    # Write back
    new_content = "// " + data.get("houseConfig", {}).get("name", "House") + " — Roster & House Metadata\nwindow.HOUSE_DATA = " + json.dumps(data, indent=2) + ";\n"
    with open(bf, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Successfully updated {bf}: {updated_cands} candidates, {updated_voters} candidate voters.")

print("All booth data.js files updated successfully!")
