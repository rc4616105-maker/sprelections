houses = ['bheeshma', 'central', 'gurudrona', 'hanuman', 'karna', 'vasistha', 'vishwamithra']
for h in houses:
    with open(f'Houses/{h}/index.html', 'r', encoding='utf-8') as f:
        html = f.read()
    with open(f'Houses/{h}/app.js', 'r', encoding='utf-8') as f:
        js = f.read()
    
    # check for camera text or element in index.html
    import re
    matches_html = re.findall(r'camera|photo|verification', html, re.I)
    print(f"=== {h} index.html ===")
    for line in html.splitlines():
        if any(w in line.lower() for w in ['verification photo', 'camera ready', 'face-guard', 'camera-video']):
            print(f"  {line.strip()[:100]}")
