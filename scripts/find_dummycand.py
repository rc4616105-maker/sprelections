import os

configs = []
for root, _, files in os.walk('Houses'):
    for f in files:
        if f == 'supabase-config.js':
            p = os.path.join(root, f)
            configs.append(p)

print("Found configs:", configs)
for p in configs:
    with open(p, 'r', encoding='utf-8') as f:
        c = f.read()
    print(p, 'has isDummyCand:', 'isDummyCand' in c)
