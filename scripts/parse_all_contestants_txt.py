import os
import re
import json

base_dir = '1docs/contestets'

houses_map = {
    'Bheeshma': 'bheeshma',
    'Gurudrona': 'gurudrona',
    'Hanuman house': 'hanuman',
    'KAran house': 'karna',
    'Vasistha house': 'vasistha',
    'Vishwamithra': 'vishwamithra',
}

def parse_txt(txt):
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    full_text = " ".join(lines).lower()
    
    # check role
    is_vc = 'vice' in full_text
    is_capt = not is_vc and 'captain' in full_text
    role = 'VICE_CAPTAIN' if is_vc else ('CAPTAIN' if is_capt else 'UNKNOWN')
    
    # check symbol
    symbol = 'Unknown'
    if 'peacock' in full_text: symbol = 'Peacock'
    elif 'mango' in full_text: symbol = 'Mango'
    elif 'ashok' in full_text: symbol = 'Ashoka Chakra'
    elif 'tiger' in full_text: symbol = 'Royal Bengal Tiger'
    elif 'banyan' in full_text: symbol = 'Banyan Tree'
    elif 'hockey' in full_text: symbol = 'Hockey Stick'
    elif 'dolphin' in full_text: symbol = 'Dolphin'
    elif 'pumpkin' in full_text: symbol = 'Pumpkin'
    elif 'ganga' in full_text: symbol = 'Ganga River'
    elif 'star' in full_text: symbol = 'Star'
    
    return role, symbol

summary = {}
for f_name, slug in houses_map.items():
    h_dir = os.path.join(base_dir, f_name)
    summary[slug] = []
    for c_name in sorted(os.listdir(h_dir)):
        c_dir = os.path.join(h_dir, c_name)
        if not os.path.isdir(c_dir): continue
        
        # files
        files = os.listdir(c_dir)
        txts = [f for f in files if f.endswith('.txt')]
        imgs = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png')) and not f.lower().startswith('symbol')]
        
        txt_str = ""
        for tf in txts:
            with open(os.path.join(c_dir, tf), 'r', encoding='utf-8', errors='ignore') as fp:
                txt_str += fp.read() + "\n"
                
        role, sym = parse_txt(txt_str)
        img_name = imgs[0] if imgs else None
        summary[slug].append({
            'folder': c_name,
            'role': role,
            'symbol': sym,
            'image': img_name,
            'raw_txt': txt_str.strip().replace('\n', ' | ')
        })

for slug, cands in summary.items():
    print(f"\n=================== {slug.upper()} ({len(cands)} contestants) ===================")
    for c in cands:
        print(f"  {c['folder']:20} | Role: {c['role']:12} | Symbol: {c['symbol']:18} | Img: {str(c['image'])[:20]}")
