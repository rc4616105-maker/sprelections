import json, os, re

from reconcile_and_copy_all_photos import final_roster

# 1. Update Houses/assets/all-candidates.js
header = """// Official SPR School Elections 2026 — Master Contesting Candidates Roster
// 140 Verified Candidates across 6 Houses and Central Cabinet
// Photos, names, and symbols reconciled from 1docs/contestets
window.ALL_CONTESTING_CANDIDATES = """

js_content = header + json.dumps(final_roster, indent=2) + ";\n"

with open("Houses/assets/all-candidates.js", "w", encoding="utf-8") as f:
    f.write(js_content)
print("Updated Houses/assets/all-candidates.js")

# 2. Update Result declaration/js/candidates-data.js
# Read the bottom helper from candidates-data.js
with open("Result declaration/js/candidates-data.js", "r", encoding="utf-8") as f:
    old_cdata = f.read()

find_meta_idx = old_cdata.find("window.findCandidateMeta = function")
helper_part = old_cdata[find_meta_idx:] if find_meta_idx != -1 else ""

cdata_content = header + json.dumps(final_roster, indent=2) + ";\n\n" + helper_part
with open("Result declaration/js/candidates-data.js", "w", encoding="utf-8") as f:
    f.write(cdata_content)
print("Updated Result declaration/js/candidates-data.js")
