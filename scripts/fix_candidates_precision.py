import os, glob, re, json

with open("scripts/new_candidates.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Let's fix the specific corrections:
# 1. Vishwamithra: K.Rithwik is Boy (VICE_CAPTAIN_BOY)
for c in data["VISHWAMITHRA"]:
    if "rithwik" in c["id"].lower():
        c["fullName"] = "K. Ruthwik"
        c["positionId"] = "VICE_CAPTAIN_BOY"
        c["positionName"] = "Boys Vice Captain (Class 9 Boy)"
        c["tagline"] = "Contesting for Boys Vice Captain · Vishwamithra House"

# 2. Vasistha: Ch.Ruthvish is Boy (VICE_CAPTAIN_BOY)
for c in data["VASISTHA"]:
    if "ruthvish" in c["id"].lower():
        c["fullName"] = "CH. Ruthvish"
        c["positionId"] = "VICE_CAPTAIN_BOY"
        c["positionName"] = "Boys Vice Captain (Class 9 Boy)"
        c["tagline"] = "Contesting for Boys Vice Captain · Vasistha House"

# 3. Vasistha: Remove duplicate H.Rishika (belongs to Gurudrona)
data["VASISTHA"] = [c for c in data["VASISTHA"] if not ("rishika" in c["fullName"].lower() and "H." in c["fullName"])]

# 4. Hanuman: R.Srikshith is Class 9 Vice Captain Boy
for c in data["HANUMAN"]:
    if "srikshith" in c["id"].lower():
        c["positionId"] = "VICE_CAPTAIN_BOY"
        c["positionName"] = "Boys Vice Captain (Class 9 Boy)"
        c["className"] = "9"
        c["tagline"] = "Contesting for Boys Vice Captain · Hanuman House"

# 5. Gurudrona: Remove duplicate H.Rishika if there are 2
seen_guru = set()
clean_guru = []
for c in data["GURUDRONA"]:
    if c["fullName"] not in seen_guru:
        seen_guru.add(c["fullName"])
        clean_guru.append(c)
data["GURUDRONA"] = clean_guru

print("=== FINAL VERIFIED CANDIDATE ROSTER PER HOUSE ===")
for h, clist in data.items():
    print(f"\n🏠 {h} (Total: {len(clist)})")
    for pid in ["CAPTAIN_BOY", "CAPTAIN_GIRL", "VICE_CAPTAIN_BOY", "VICE_CAPTAIN_GIRL"]:
        sub = [c for c in clist if c["positionId"] == pid]
        print(f"  [{pid}] ({len(sub)}):")
        for sc in sub:
            print(f"     • {sc['fullName']} | Symbol: {sc['symbolObj']['name']} ({sc['symbolObj']['icon']}) | Photo: {sc['photoUrl']}")

with open("scripts/new_candidates_clean.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
