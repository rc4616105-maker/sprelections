import re

target_files = [
    'Houses/teachers/data.js',
    'Houses/assets/all-candidates.js',
    'Result declaration/js/candidates-data.js'
]

# Pattern:
#     },\n      "photoUrl": "...",\n      "photoPath": "...",\n      "isApproved": true\n    },
pattern = re.compile(r'(\s*},\s*\n\s*"photoUrl":\s*"[^"]*",\s*\n\s*"photoPath":\s*"[^"]*",\s*\n\s*"isApproved":\s*true\s*\n\s*},)', re.MULTILINE)

for fp in target_files:
    with open(fp, 'r', encoding='utf-8') as f:
        text = f.read()

    # Repeatedly remove any occurrences
    count = 0
    while True:
        m = pattern.search(text)
        if not m:
            break
        text = text[:m.start()] + "\n    }," + text[m.end():]
        count += 1
    
    print(f"{fp}: replaced {count} duplicate trailing blocks")
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(text)
