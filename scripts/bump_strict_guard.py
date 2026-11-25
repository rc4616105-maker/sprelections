import re

for h in ['bheeshma', 'gurudrona', 'hanuman', 'karna', 'vasistha', 'vishwamithra', 'teachers', 'central']:
    p = f'Houses/{h}/index.html'
    with open(p, 'r', encoding='utf-8') as f:
        c = f.read()
    c = re.sub(r'app\.js\?v=[^"]+', 'app.js?v=20261125_STRICT_SELECTION_GUARD', c)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(c)
    print(f"Busted cache for {h}")
