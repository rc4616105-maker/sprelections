from pathlib import Path

for slug in ['bheeshma', 'gurudrona', 'hanuman', 'karna', 'vasistha', 'vishwamithra', 'central']:
    p = Path('Houses') / slug / 'supabase-config.js'
    text = p.read_text(encoding='utf-8')
    old_snippet = '        if (isTeacher) {\n          const boothDisplayName = housesMeta[requestedHouseCode]?.name'
    new_snippet = '        if (isTeacher && cleanId !== "1C8492" && cleanId !== "0000" && cleanId !== "000000") {\n          const boothDisplayName = housesMeta[requestedHouseCode]?.name'
    if old_snippet in text:
        text = text.replace(old_snippet, new_snippet)
        p.write_text(text, encoding='utf-8')
        print(f'Updated revoting for demo in {slug}')
    else:
        print(f'Pattern already updated in {slug}')
