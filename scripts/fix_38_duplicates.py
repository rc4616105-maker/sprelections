import re, json

files = [
    'Houses/teachers/data.js',
    'Houses/assets/all-candidates.js',
    'Result declaration/js/candidates-data.js'
]

pattern = re.compile(r'("isApproved":\s*true\s*\},)\s*"photoUrl":\s*"[^"]*",\s*"photoPath":\s*"[^"]*",\s*"isApproved":\s*true\s*\},', re.DOTALL)

for fp in files:
    with open(fp, 'r', encoding='utf-8') as f:
        text = f.read()

    new_text, count = pattern.subn(r'\1', text)
    print(f"{fp}: replaced {count} duplicate blocks")
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(new_text)

    # Now validate JSON!
    idx = new_text.find('= ')
    json_str = new_text[idx + 2:].strip().rstrip(';')
    try:
        obj = json.loads(json_str)
        print(f"  --> {fp}: 100% VALID JSON!")
    except Exception as e:
        print(f"  --> {fp}: FAILED with {e}")
