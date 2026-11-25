import json
import re

files_to_check = [
    'Houses/admin/data.js',
    'Houses/teachers/data.js',
    'Houses/assets/all-candidates.js',
    'Houses/bheeshma/data.js',
    'Houses/gurudrona/data.js',
    'Houses/hanuman/data.js',
    'Houses/karna/data.js',
    'Houses/vasistha/data.js',
    'Houses/vishwamithra/data.js',
    'Houses/central/data.js'
]

def check_file(path):
    print(f"\n--- Checking {path} ---")
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Try to find JS object assignment
    # e.g., window.ADMIN_DATA = { ... }; or const ALL_CANDIDATES = [ ... ];
    match = re.search(r'=\s*(\{.*\}|\[.*\])\s*;?\s*$', content, re.DOTALL)
    if not match:
        print("Could not find assignment in", path)
        return False
    
    js_text = match.group(1).strip()
    try:
        data = json.loads(js_text)
        print("VALID JSON in", path)
        return True
    except json.JSONDecodeError as e:
        print(f"ERROR in {path}: {e}")
        return False

for p in files_to_check:
    check_file(p)
