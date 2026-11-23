import json, re

with open("scripts/new_candidates_clean.json", "r", encoding="utf-8") as f:
    cand_by_house = json.load(f)

all_cands = []
for clist in cand_by_house.values():
    all_cands.extend(clist)

t_file = "Houses/teachers/data.js"
content = open(t_file, encoding="utf-8").read()
cands_json = json.dumps(all_cands, indent=4)
pattern = r'"candidates":\s*\[[\s\S]*?\n\s*\]'

new_content, count = re.subn(pattern, lambda m: '"candidates": ' + cands_json, content)
if count > 0:
    with open(t_file, "w", encoding="utf-8") as out:
        out.write(new_content)
    print(f"Successfully updated {t_file} with {len(all_cands)} real candidates!")
else:
    print("Pattern not found in teachers/data.js")
