import json, re

with open("Houses/assets/all-candidates.js", "r", encoding="utf-8") as f:
    text = f.read()

m = re.search(r'window\.ALL_CONTESTING_CANDIDATES\s*=\s*(\[[\s\S]*?\]);', text)
master = json.loads(m.group(1))

# Helper to find meta
def find_c(name, house_code=None):
    from compare_cands_normalized import norm_name, norm_house
    nn = norm_name(name)
    nh = norm_house(house_code) if house_code else None
    for c in master:
        if norm_name(c['fullName']) == nn:
            if nh and norm_house(c['houseCode']) != nh:
                continue
            return c
    for c in master:
        if nn in norm_name(c['fullName']) or norm_name(c['fullName']) in nn:
            if nh and norm_house(c['houseCode']) != nh:
                continue
            return c
    return None

with open("Result declaration/js/data.js", "r", encoding="utf-8") as f:
    data_js = f.read()

# Load DEFAULT_HOUSES
m = re.search(r'const DEFAULT_HOUSES = (\[[\s\S]*?\]);', data_js)
houses = json.loads(m.group(1))

for h in houses:
    for post, cand in h.get("candidates", {}).items():
        found = find_c(cand["name"], h["id"])
        if found:
            cand["photo"] = found["photoPath"].replace("../", "")
            cand["symbol"] = {
                "name": found["symbolObj"]["name"],
                "icon": found["symbolObj"]["icon"],
                "imagePath": found["symbolObj"]["imagePath"].replace("../", "")
            }
            cand["symbolName"] = found["symbolObj"]["name"]
            cand["symbolIcon"] = found["symbolObj"]["icon"]
            cand["symbolImagePath"] = found["symbolObj"]["imagePath"].replace("../", "")
        else:
            print("Not found in master:", cand["name"], h["id"])

# Load DEFAULT_CABINET_POSTS
m2 = re.search(r'const DEFAULT_CABINET_POSTS = (\[[\s\S]*?\]);', data_js)
cab = json.loads(m2.group(1))

for cp in cab:
    cand = cp.get("candidate", {})
    found = find_c(cand.get("name", ""), "CENTRAL")
    if found:
        cand["photo"] = found["photoPath"].replace("../", "")
        cand["symbol"] = {
            "name": found["symbolObj"]["name"],
            "icon": found["symbolObj"]["icon"],
            "imagePath": found["symbolObj"]["imagePath"].replace("../", "")
        }
        cand["symbolName"] = found["symbolObj"]["name"]
        cand["symbolIcon"] = found["symbolObj"]["icon"]
        cand["symbolImagePath"] = found["symbolObj"]["imagePath"].replace("../", "")
    else:
        print("Cabinet not found:", cand.get("name"))

new_data_js = data_js[:m.start(1)] + json.dumps(houses, indent=2) + data_js[m.end(1):]
m2_new = re.search(r'const DEFAULT_CABINET_POSTS = (\[[\s\S]*?\]);', new_data_js)
new_data_js = new_data_js[:m2_new.start(1)] + json.dumps(cab, indent=2) + new_data_js[m2_new.end(1):]

with open("Result declaration/js/data.js", "w", encoding="utf-8") as f:
    f.write(new_data_js)

print("Updated Result declaration/js/data.js successfully!")
