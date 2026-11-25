with open('Houses/vasistha/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'openFaceGuardModal', text)]
for idx in matches:
    print('--- CALL ---')
    print(text[idx-100:idx+300])
