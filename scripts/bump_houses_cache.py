import re

for h in ['vasistha', 'bheeshma', 'gurudrona', 'hanuman', 'karna', 'vishwamithra']:
    p = f'Houses/{h}/index.html'
    with open(p, 'r', encoding='utf-8') as f:
        c = f.read()
    c = re.sub(r'data\.js\?v=[^"]+', 'data.js?v=20261125_KONARK', c)
    c = re.sub(r'app\.js\?v=[^"]+', 'app.js?v=20261125_KONARK', c)
    c = re.sub(r'supabase-config\.js\?v=[^"]+', 'supabase-config.js?v=20261125_KONARK', c)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(c)
    print(f'Busted cache for {h}')
