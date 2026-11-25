import re

for fp in ['Houses/teachers/data.js', 'Houses/assets/all-candidates.js', 'Result declaration/js/candidates-data.js']:
    with open(fp, 'r', encoding='utf-8') as f:
        text = f.read()
    
    matches = list(re.finditer(r'"isApproved":\s*true\s*\},?\s*"photoUrl"', text))
    print(f"{fp}: {len(matches)} matches")
    for m in matches[:5]:
        print(text[m.start()-40:m.start()+120].replace('\n', ' '))
