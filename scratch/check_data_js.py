houses = ['bheeshma', 'central', 'gurudrona', 'hanuman', 'karna', 'vasistha', 'vishwamithra']
for h in houses:
    with open(f'Houses/{h}/data.js', 'r', encoding='utf-8') as f:
        c = f.read()
    import re
    pos = re.findall(r'id:\s*["\']([^"\']+)["\']', c)
    print(f"{h}: {pos[:6]}")
