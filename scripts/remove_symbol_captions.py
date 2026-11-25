import glob

house_apps = [
    'Houses/bheeshma/app.js',
    'Houses/gurudrona/app.js',
    'Houses/hanuman/app.js',
    'Houses/karna/app.js',
    'Houses/vasistha/app.js',
    'Houses/vishwamithra/app.js',
    'Houses/teachers/app.js'
]

for fp in house_apps:
    with open(fp, 'r', encoding='utf-8') as f:
        text = f.read()

    orig = text
    # Remove evm-symbol-caption
    text = text.replace('<span class="evm-symbol-caption">${sym.name}</span>', '')
    # Remove evm-symbol-caption-sm
    text = text.replace('<span class="evm-symbol-caption-sm">${pickedSym.name}</span>', '')

    if text != orig:
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Updated {fp}")
    else:
        print(f"No match in {fp}")
