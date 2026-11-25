import glob, os

target_files = [
    'Houses/admin/data.js',
    'Houses/assets/all-candidates.js',
    'Houses/bheeshma/data.js',
    'Houses/gurudrona/data.js',
    'Houses/hanuman/data.js',
    'Houses/karna/data.js',
    'Houses/teachers/data.js',
    'Houses/vasistha/data.js',
    'Houses/vishwamithra/data.js',
    'Houses/central/data.js',
    'Result declaration/js/candidates-data.js',
    'Result declaration/js/data.js'
]

for fp in target_files:
    if not os.path.exists(fp):
        print('Skipping non-existent:', fp)
        continue
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()

    orig = content

    # Replace 'Ashoka Chakra' with 'Konark Wheel'
    content = content.replace('"Ashoka Chakra"', '"Konark Wheel"')
    content = content.replace("'Ashoka Chakra'", "'Konark Wheel'")
    content = content.replace('ashoka_chakra.png', 'konark_wheel.png')
    content = content.replace('"ashoka_chakra"', '"konark_wheel"')
    content = content.replace("'ashoka_chakra'", "'konark_wheel'")

    # Replace Sec in shortTitle
    content = content.replace('"shortTitle": "Literary Sec"', '"shortTitle": "Literary"')
    content = content.replace('"shortTitle": "Sports Sec"', '"shortTitle": "Sports"')
    content = content.replace('"shortTitle": "Social & Cultural Sec"', '"shortTitle": "Social & Cultural"')

    if content != orig:
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Updated: {fp}')
    else:
        print(f'No changes needed: {fp}')
