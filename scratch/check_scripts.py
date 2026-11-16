import re

houses = ['bheeshma', 'central', 'gurudrona', 'hanuman', 'karna', 'vasistha', 'vishwamithra']
for h in houses:
    with open('Houses/' + h + '/index.html', 'r', encoding='utf-8') as f:
        c = f.read()
    scripts = re.findall(r'<script[^>]*src=["\']([^"\']+)["\']', c)
    print(f"{h}:")
    for s in scripts:
        print(f"  {s}")
