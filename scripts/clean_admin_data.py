import json
import re

with open('Houses/assets/all-candidates.js', 'r', encoding='utf-8') as f:
    ac_text = f.read()

idx = ac_text.find('window.ALL_CONTESTING_CANDIDATES =')
if idx == -1:
    print("Could not find window.ALL_CONTESTING_CANDIDATES")
    exit(1)

js_array = ac_text[idx + len('window.ALL_CONTESTING_CANDIDATES ='):].strip()
if js_array.endswith(';'):
    js_array = js_array[:-1].strip()

candidates_data = json.loads(js_array)
print(f"Loaded {len(candidates_data)} candidates from all-candidates.js")

with open('Houses/admin/data.js', 'r', encoding='utf-8') as f:
    admin_text = f.read()

cand_idx = admin_text.find('"candidates": [')
if cand_idx == -1:
    print("Could not find candidates in admin/data.js")
    exit(1)

prefix = admin_text[:cand_idx + len('"candidates": ')]

# Format candidates JSON nicely
cand_json = json.dumps(candidates_data, indent=2)

new_admin_text = prefix + cand_json + "\n};\n"

# Verify that new_admin_text parses as valid JSON after "window.ADMIN_DATA ="
idx_eq = new_admin_text.find('window.ADMIN_DATA =')
js_to_test = new_admin_text[idx_eq + len('window.ADMIN_DATA ='):].strip()
if js_to_test.endswith(';'):
    js_to_test = js_to_test[:-1].strip()

parsed = json.loads(js_to_test)
print("SUCCESS: Full ADMIN_DATA parses 100% cleanly!")
print("ADMIN_DATA keys:", list(parsed.keys()))
print("Total students:", len(parsed['students']))
print("Total candidates:", len(parsed['candidates']))
print("Total houses:", len(parsed['houses']))

with open('Houses/admin/data.js', 'w', encoding='utf-8') as f:
    f.write(new_admin_text)

print("Saved clean Houses/admin/data.js!")
