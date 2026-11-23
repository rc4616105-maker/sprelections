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

for folder_name, slug in houses_map.items():
    h_path = os.path.join(base_dir, folder_name)
    cand_folders = os.listdir(h_path)
    
    with open(f'Houses/{slug}/data.js', 'r', encoding='utf-8') as f:
        text = f.read()
    data = json.loads(text[text.find('{'):text.rfind('}')+1])
    cands_in_data = {c['fullName'].lower().replace(' ', '').replace('.', ''): c for c in data['houseCandidates']}
    
    print(f"\n=== HOUSE: {slug.upper()} ===")
    for cf in cand_folders:
        cf_path = os.path.join(h_path, cf)
        if not os.path.isdir(cf_path): continue
        
        # read txt
        txts = [f for f in os.listdir(cf_path) if f.lower().endswith('.txt')]
        txt_content = ""
        for tf in txts:
            with open(os.path.join(cf_path, tf), 'r', encoding='utf-8', errors='ignore') as fp:
                txt_content += fp.read() + " "
        
        # clean key
        clean_name = cf.lower().replace(' ', '').replace('.', '')
        match = cands_in_data.get(clean_name)
        
        # Determine from txt
        is_vc = 'vice' in txt_content.lower()
        is_capt = not is_vc and 'captain' in txt_content.lower()
        txt_role = 'VICE CAPTAIN' if is_vc else ('CAPTAIN' if is_capt else 'UNKNOWN')
        
        if match:
            print(f"  [OK] {cf:20} -> Data Post: {match.get('positionId'):18} | Txt: {txt_role:12} | Symbol: {match.get('symbolObj', {}).get('name')}")
        else:
            print(f"  [MISSING in data.js!] {cf:20} -> Txt: {txt_role}")
