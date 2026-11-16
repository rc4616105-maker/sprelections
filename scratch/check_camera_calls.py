import os

houses = ['bheeshma', 'central', 'gurudrona', 'hanuman', 'karna', 'vasistha', 'vishwamithra']
for h in houses:
    path = f'Houses/{h}/app.js'
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    
    print(f"=== {h} ===")
    lines = c.splitlines()
    for i, line in enumerate(lines):
        if any(term in line for term in ['detectHumanFace', 'warmUpBackgroundCamera', 'openFaceGuardModal', 'pico', 'facefinder', 'submitFinalVote']):
            print(f"  L{i+1}: {line.strip()[:100]}")
