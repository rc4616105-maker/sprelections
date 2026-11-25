import glob, re

for path in glob.glob('Houses/**/*.js', recursive=True):
    if '.git' in path: continue
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    found = []
    for line_no, line in enumerate(text.splitlines(), 1):
        if any(k in line for k in ['evm-symbol-caption', 'symbol-caption', 'symbol-name', 'sym.name', 'symbolObj.name', 'candidate-symbol-caption']):
            found.append((line_no, line.strip()))
    if found:
        print(f"=== {path} ===")
        for lno, l in found[:10]:
            print(f"  {lno}: {l}")
