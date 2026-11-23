import sys, os, json, re
sys.path.insert(0, os.path.abspath("."))

with open('Houses/assets/all-candidates.js', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'window\.ALL_CONTESTING_CANDIDATES = (\[.*?\]);', text, re.DOTALL)
existing = json.loads(m.group(1))

from scripts.test_clean_names_all import get_clean_name

no_initial_list = []
for i, c in enumerate(existing):
    clean = get_clean_name(c)
    has_init = bool(re.match(r'^[A-Za-z]{1,3}\.', clean))
    if not has_init:
        no_initial_list.append((i+1, c['houseCode'], clean, c['photoPath']))

print(f"Names WITHOUT dot initial: {len(no_initial_list)}")
for idx, h, name, photo in no_initial_list:
    print(f"  {idx}. [{h}] {name} (Photo: {photo})")
