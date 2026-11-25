import glob

houses = ['bheeshma', 'gurudrona', 'hanuman', 'karna', 'vasistha', 'vishwamithra', 'teachers']

old_subtext = """          let subText = String(cand.section || "").trim();
          if (!/^class\\s+/i.test(subText)) {
            subText = cand.className ? `Class ${cand.className} · ${subText}` : subText;
          }"""

new_subtext = """          let subText = cand.className ? `Class ${cand.className}` : "Class 10";"""

for h in houses:
    p = f'Houses/{h}/app.js'
    with open(p, 'r', encoding='utf-8') as f:
        c = f.read()
    
    if old_subtext in c:
        c = c.replace(old_subtext, new_subtext)
        with open(p, 'w', encoding='utf-8') as f:
            f.write(c)
        print(f"Updated subText in {h}")
    else:
        print(f"Pattern not found in {h}, searching regex...")
        import re
        c = re.sub(r'let subText = String\(cand\.section.*?\};\s*\}', 'let subText = cand.className ? `Class ${cand.className}` : "Class 10";', c, flags=re.DOTALL)
        with open(p, 'w', encoding='utf-8') as f:
            f.write(c)
        print(f"Regex updated subText in {h}")
