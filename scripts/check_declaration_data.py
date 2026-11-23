import json
import re

with open('Result declaration/js/data.js', 'r', encoding='utf-8') as f:
    c = f.read()

m = re.search(r'const DEFAULT_HOUSES = (\[.*?\]);\s*const DEFAULT_CABINET_POSTS', c, re.DOTALL)
if m:
    houses = json.loads(m.group(1))
    print(f"Houses count: {len(houses)}")
    for h in houses:
        print(f"\nHouse: {h['id']} - {h['name']}")
        for k, cand in h['candidates'].items():
            print(f"  {k}: {cand['name']} | photo: {cand.get('photo')} | symbol: {cand.get('symbolName')}")

m2 = re.search(r'const DEFAULT_CABINET_POSTS = (\[.*?\]);', c, re.DOTALL)
if m2:
    posts = json.loads(m2.group(1))
    print(f"\nCabinet posts count: {len(posts)}")
    for p in posts:
        cand = p.get('candidate', {})
        print(f"  {p['id']}: {cand.get('name')} | photo: {cand.get('photo')} | symbol: {cand.get('symbolName')}")
