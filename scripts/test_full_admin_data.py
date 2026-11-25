with open('Houses/admin/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Verify that text starts with window.ADMIN_DATA =
assert text.strip().startswith('window.ADMIN_DATA =')
assert text.strip().endswith('};')

import json
js_obj = text[text.find('window.ADMIN_DATA =') + len('window.ADMIN_DATA ='):].strip()
if js_obj.endswith(';'):
    js_obj = js_obj[:-1].strip()

data = json.loads(js_obj)
print("Data loaded successfully!")
print("Houses in data:", len(data['houses']))
for h in data['houses']:
    print(f"  Code: {h['code']}, Name: {h['name']}, Accent: {h.get('accent')}")
print("Students in data:", len(data['students']))
print("Candidates in data:", len(data['candidates']))
