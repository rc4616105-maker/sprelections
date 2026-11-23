# -*- coding: utf-8 -*-
import json, re, sys
from pathlib import Path
from collections import Counter

# Load existing students from data.js
with open("Houses/admin/data.js", "r", encoding="utf-8") as f:
    text = f.read()

# Extract window.ADMIN_DATA
m = re.search(r"window\.ADMIN_DATA\s*=\s*(\{.*?\});\s*(?:window\.TEACHERS_DATA|$)", text, re.DOTALL)
if not m:
    print("Could not find ADMIN_DATA in data.js")
    sys.exit(1)

admin_data = json.loads(m.group(1))
existing_students = admin_data.get("students", [])
print(f"Existing students in data.js: {len(existing_students)}")

classes_existing = Counter(s.get("className") for s in existing_students)
print("Existing by class:", classes_existing)

houses_existing = Counter(s.get("houseCode") for s in existing_students)
print("Existing by house:", houses_existing)
