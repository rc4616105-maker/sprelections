import os
import glob
import re

base_dir = '1docs/contestets'
houses = os.listdir(base_dir)

all_candidates_parsed = []

for h in houses:
    h_path = os.path.join(base_dir, h)
    if not os.path.isdir(h_path):
        continue
    
    cand_folders = os.listdir(h_path)
    print(f"\n==================== HOUSE: {h} ({len(cand_folders)} folders) ====================")
    
    for cf in cand_folders:
        cf_path = os.path.join(h_path, cf)
        if not os.path.isdir(cf_path):
            continue
        
        # Look for txt file and image files
        sub_files = os.listdir(cf_path)
        txt_files = [f for f in sub_files if f.lower().endswith('.txt')]
        img_files = [f for f in sub_files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
        
        txt_content = ""
        for tf in txt_files:
            with open(os.path.join(cf_path, tf), 'r', encoding='utf-8', errors='ignore') as fp:
                txt_content += fp.read() + " "
        
        # Clean text
        print(f"Folder: {cf}")
        print(f"   Images: {img_files}")
        print(f"   TXT: {repr(txt_content.strip())}")
