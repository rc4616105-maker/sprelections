import os
import sys
import json
import re
import urllib.request

sys.path.insert(0, os.path.abspath("."))
from scripts.test_clean_names_all import get_clean_name

SUPABASE_URL = "https://rziptxcknaeuorekxwrl.supabase.co"
SECRET_KEY = "sb_secret_FtxzxZKea9lg5fhHm10sEA_WZcgFcs8"

# 1. Update Houses/assets/all-candidates.js & Result declaration/js/candidates-data.js
with open('Houses/assets/all-candidates.js', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'window\.ALL_CONTESTING_CANDIDATES = (\[.*?\]);', text, re.DOTALL)
all_candidates = json.loads(m.group(1))

name_replacements = {}
for c in all_candidates:
    old_name = c['fullName']
    new_name = get_clean_name(c)
    if old_name != new_name:
        name_replacements[old_name] = new_name
    c['fullName'] = new_name
    # Update tagline if it contains old name
    if 'tagline' in c and old_name in c['tagline']:
        c['tagline'] = c['tagline'].replace(old_name, new_name)

print(f"Total candidate names to update: {len(name_replacements)}")

# Write all-candidates.js
cand_js_content = f"// Official SPR School Elections 2026 — Master Contesting Candidates Roster\n// 140 Verified Candidates across 6 Houses and Central Cabinet\nwindow.ALL_CONTESTING_CANDIDATES = {json.dumps(all_candidates, indent=2, ensure_ascii=False)};\n"
with open('Houses/assets/all-candidates.js', 'w', encoding='utf-8') as f:
    f.write(cand_js_content)
print("✓ Updated Houses/assets/all-candidates.js")

# Write Result declaration/js/candidates-data.js
# Include findCandidateMeta
with open('Result declaration/js/candidates-data.js', 'r', encoding='utf-8') as f:
    r_text = f.read()
m_helper = re.search(r'window\.findCandidateMeta = function.*', r_text, re.DOTALL)
helper_code = m_helper.group(0) if m_helper else ""

with open('Result declaration/js/candidates-data.js', 'w', encoding='utf-8') as f:
    f.write(cand_js_content + "\n" + helper_code)
print("✓ Updated Result declaration/js/candidates-data.js")

# 2. Update all booth data.js files
booth_data_files = [
    'Houses/bheeshma/data.js',
    'Houses/gurudrona/data.js',
    'Houses/hanuman/data.js',
    'Houses/karna/data.js',
    'Houses/vasistha/data.js',
    'Houses/vishwamithra/data.js',
    'Houses/central/data.js'
]

for bdf in booth_data_files:
    if os.path.exists(bdf):
        with open(bdf, 'r', encoding='utf-8') as f:
            b_txt = f.read()
        for old_n, new_n in name_replacements.items():
            b_txt = b_txt.replace(f'"{old_n}"', f'"{new_n}"')
        with open(bdf, 'w', encoding='utf-8') as f:
            f.write(b_txt)
        print(f"✓ Updated names in {bdf}")

# 3. Update Result declaration/js/data.js
with open('Result declaration/js/data.js', 'r', encoding='utf-8') as f:
    dec_txt = f.read()
for old_n, new_n in name_replacements.items():
    dec_txt = dec_txt.replace(f'"{old_n}"', f'"{new_n}"')
with open('Result declaration/js/data.js', 'w', encoding='utf-8') as f:
    f.write(dec_txt)
print("✓ Updated names in Result declaration/js/data.js")

# 4. Sync updated names to Supabase public.candidates table
print("Updating Supabase public.candidates...")
try:
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/candidates?select=id,full_name",
        headers={'apikey': SECRET_KEY, 'Authorization': f'Bearer {SECRET_KEY}'}
    )
    with urllib.request.urlopen(req) as resp:
        sb_cands = json.loads(resp.read().decode('utf-8'))
    
    updated_sb_count = 0
    for sbc in sb_cands:
        cur_fn = sbc.get('full_name', '')
        if cur_fn in name_replacements:
            target_fn = name_replacements[cur_fn]
            patch_req = urllib.request.Request(
                f"{SUPABASE_URL}/rest/v1/candidates?id=eq.{sbc['id']}",
                data=json.dumps({"full_name": target_fn}).encode('utf-8'),
                headers={
                    'apikey': SECRET_KEY,
                    'Authorization': f'Bearer {SECRET_KEY}',
                    'Content-Type': 'application/json'
                },
                method="PATCH"
            )
            with urllib.request.urlopen(patch_req) as p_resp:
                if p_resp.status in (200, 204):
                    updated_sb_count += 1
    print(f"✓ Updated {updated_sb_count} candidate names in Supabase!")
except Exception as e:
    print("Note on Supabase sync:", e)

# 5. Bump cachebusters
import scripts.bump_cachebusters as bb
print("All candidate initials updated and synced successfully!")
