import glob

css_rule = "\n\n/* Hide symbol text captions everywhere */\n.evm-symbol-caption,\n.evm-symbol-caption-sm,\n.cand-symbol-label,\n.symbol-name {\n  display: none !important;\n}\n"

for p in glob.glob('Houses/**/*.css', recursive=True):
    with open(p, 'r', encoding='utf-8') as f:
        c = f.read()
    if '.evm-symbol-caption' not in c or 'display: none !important' not in c:
        with open(p, 'a', encoding='utf-8') as f:
            f.write(css_rule)
        print(f"Added rule to {p}")
    else:
        print(f"Already present in {p}")
