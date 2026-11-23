import json, os, re

# Load master
with open("Houses/assets/all-candidates.js", "r", encoding="utf-8") as f:
    text = f.read()

m = re.search(r'window\.ALL_CONTESTING_CANDIDATES\s*=\s*(\[[\s\S]*?\]);', text)
master = json.loads(m.group(1))

from compare_cands_normalized import norm_name, norm_house

lookup = {}
for c in master:
    k = (norm_name(c['fullName']), norm_house(c['houseCode']))
    lookup[k] = c
    lookup[norm_name(c['fullName'])] = c

def update_candidate_obj(cand, default_house=""):
    fn = cand.get("fullName", "")
    nh = norm_house(cand.get("houseCode", default_house))
    meta = lookup.get((norm_name(fn), nh)) or lookup.get(norm_name(fn))
    if meta:
        cand["photoUrl"] = meta["photoUrl"]
        cand["photoPath"] = meta["photoPath"]
        cand["symbolObj"] = meta["symbolObj"]
        if "tagline" in cand and "tagline" in meta:
            cand["tagline"] = meta["tagline"]
        return True
    return False

def update_student_obj(stu, default_house=""):
    if stu.get("isCandidate"):
        fn = stu.get("fullName", "")
        nh = norm_house(stu.get("houseCode", default_house))
        meta = lookup.get((norm_name(fn), nh)) or lookup.get(norm_name(fn))
        if meta:
            stu["photoUrl"] = meta["photoUrl"]
            return True
    return False

house_slugs = ["bheeshma", "gurudrona", "hanuman", "karna", "vasistha", "vishwamithra"]

for slug in house_slugs:
    p = f"Houses/{slug}/data.js"
    with open(p, "r", encoding="utf-8") as f:
        c = f.read()
    
    m_h = re.search(r'window\.HOUSE_DATA\s*=\s*(\{[\s\S]*\});?\s*$', c)
    if not m_h:
        print(f"Failed to find HOUSE_DATA in {p}")
        continue
    
    data = json.loads(m_h.group(1))
    c_up = 0
    s_up = 0
    
    for cand in data.get("houseCandidates", []):
        if update_candidate_obj(cand, slug): c_up += 1
    for cand in data.get("allCandidates", []):
        if update_candidate_obj(cand, slug): c_up += 1
    for stu in data.get("houseStudents", []):
        if update_student_obj(stu, slug): s_up += 1
    for stu in data.get("allStudents", []):
        if update_student_obj(stu, slug): s_up += 1
        
    out = "// " + slug.capitalize() + " — Roster & House Metadata\nwindow.HOUSE_DATA = " + json.dumps(data, indent=2) + ";\n"
    with open(p, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"Updated {p}: {c_up} candidates, {s_up} student candidates.")

# Also update central (School Cabinet)
p_cent = "Houses/central/data.js"
with open(p_cent, "r", encoding="utf-8") as f:
    cent_text = f.read()

# Replace any photoUrl or symbolObj in central/data.js for all master candidates
cent_updated = cent_text
for c in master:
    if norm_house(c["houseCode"]) == "cabinet":
        fn = c["fullName"]
        photo = c["photoPath"]
        sym_name = c["symbolObj"]["name"]
        sym_img = c["symbolObj"]["imagePath"]
        # Match candidate block for fn
        # Let's replace photoUrl
        pattern = re.compile(rf'("fullName":\s*"{re.escape(fn)}"[\s\S]*?"photoUrl":\s*")[^"]+(")', re.MULTILINE)
        cent_updated = pattern.sub(rf'\g<1>{photo}\g<2>', cent_updated)
        pattern_sym = re.compile(rf'("fullName":\s*"{re.escape(fn)}"[\s\S]*?"name":\s*")[^"]+(")', re.MULTILINE)
        # Also replace in symbolObj

with open(p_cent, "w", encoding="utf-8") as f:
    f.write(cent_updated)
print("Updated Houses/central/data.js")

# Also update admin data.js
p_admin = "Houses/admin/data.js"
with open(p_admin, "r", encoding="utf-8") as f:
    adm_text = f.read()

m_adm = re.search(r'window\.ADMIN_DATA\s*=\s*(\{[\s\S]*\});?\s*$', adm_text)
if m_adm:
    data_adm = json.loads(m_adm.group(1))
    adm_c = 0
    adm_s = 0
    for cand in data_adm.get("candidates", []):
        if update_candidate_obj(cand): adm_c += 1
    for stu in data_adm.get("allStudents", []):
        if update_student_obj(stu): adm_s += 1
    out_adm = "window.ADMIN_DATA = " + json.dumps(data_adm, indent=2) + ";\n"
    with open(p_admin, "w", encoding="utf-8") as f:
        f.write(out_adm)
    print(f"Updated Houses/admin/data.js: {adm_c} candidates, {adm_s} student candidates.")
