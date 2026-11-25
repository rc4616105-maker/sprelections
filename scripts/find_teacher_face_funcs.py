with open('Houses/teachers/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'faceGuard|openFace|detectHumanFace|warmUpBackgroundCamera', text)]
print(f"Found {len(matches)} matches in teachers/app.js:")
for idx in matches:
    print('--- MATCH ---')
    print(text[idx-50:idx+250])
