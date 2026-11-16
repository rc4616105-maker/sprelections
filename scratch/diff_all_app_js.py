import difflib

houses = ['bheeshma', 'central', 'gurudrona', 'karna', 'vasistha', 'vishwamithra']
with open('Houses/hanuman/app.js', 'r', encoding='utf-8') as f:
    hanuman_lines = f.readlines()

for h in houses:
    path = f'Houses/{h}/app.js'
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    diff = list(difflib.unified_diff(hanuman_lines, lines, lineterm=''))
    print(f"Diff hanuman vs {h}: {len(diff)} diff lines")
    for d in diff:
        print(f"  {d}")
