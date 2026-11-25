import os
import re

# 1. Inspect Vasistha data.js
with open('Houses/vasistha/data.js', 'r', encoding='utf-8') as f:
    v_data = f.read()

print('=== VASISTHA DATA ===')
for m in re.finditer(r'(Boys Captain|Girls Captain|Boys Vice Captain|Girls Vice Captain)', v_data):
    pos = m.group(1)
    sub = v_data[m.start():m.start()+2500]
    names = re.findall(r'name:\s*["\']([^"\']+)["\']', sub)
    print(pos, ':', names[:6])

# 2. Check Ashoka chakra in all files
print('\n=== ASHOKA CHAKRA SEARCH ===')
for root, _, files in os.walk('Houses'):
    for file in files:
        if file.endswith(('.js', '.html', '.json')):
            p = os.path.join(root, file)
            with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                c = f.read()
                if 'ashoka' in c.lower():
                    print('Ashoka found in:', p)

# 3. Check teachers/data.js
print('\n=== TEACHERS DATA ===')
with open('Houses/teachers/data.js', 'r', encoding='utf-8') as f:
    t_data = f.read()
print('Teachers Literary Sec in data.js:', 'Literary Sec' in t_data)
print('Teachers quotes in data.js:', 'Visionary leadership' in t_data)
sections = re.findall(r'Class 10\s*·\s*[^",\n\r]+', t_data)
print('Found section names in data.js:', len(sections), sections[:3])

# 4. Check teachers/index.html and teachers/app.js for Sec, quotes, and sections
with open('Houses/teachers/index.html', 'r', encoding='utf-8') as f:
    t_html = f.read()
print('\n=== TEACHERS INDEX.HTML ===')
print('Literary Sec in index.html:', 'Literary Sec' in t_html)
print('Sports Sec in index.html:', 'Sports Sec' in t_html)
print('Social & Cultural Sec in index.html:', 'Social & Cultural Sec' in t_html)

# 5. Check teachers candidate cards rendering
print('\n=== TEACHERS APP.JS ===')
with open('Houses/teachers/app.js', 'r', encoding='utf-8') as f:
    t_app = f.read()
print('teachers/app.js size:', len(t_app))
