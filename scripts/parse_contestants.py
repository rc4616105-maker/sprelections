import os, glob, re, shutil
from collections import defaultdict

# Symbols mapping and standard icons
SYMBOL_ICONS = {
    "peacock": "🦚",
    "royal bengal tiger": "🐅",
    "tiger": "🐅",
    "mango": "🥭",
    "banyan tree": "🌳",
    "ashoka chakra": "☸️",
    "ashok chakra": "☸️",
    "hockey stick": "🏑",
    "dolphin": "🐬",
    "pumpkin": "🎃",
    "ganga river": "🌊",
    "river": "🌊",
    "torch": "🔦",
    "shield": "🛡️",
    "rising sun": "🌅",
    "star": "⭐",
    "book": "📖",
    "trophy": "🏆",
    "compass": "🧭",
    "rocket": "🚀",
    "bell": "🔔",
}

HOUSE_MAP = {
    "bheeshma": "BHEESHMA",
    "gurudrona": "GURUDRONA",
    "hanuman": "HANUMAN",
    "hanuman house": "HANUMAN",
    "karan": "KARNA",
    "karna": "KARNA",
    "karan house": "KARNA",
    "vasistha": "VASISTHA",
    "vasista": "VASISTHA",
    "vashista": "VASISTHA",
    "vasistha house": "VASISTHA",
    "vishwamithra": "VISHWAMITHRA",
    "vishwamitra": "VISHWAMITHRA",
}

def clean(s):
    return re.sub(r"\s+", " ", str(s or "")).strip()

def extract_contestant_info(txt_path):
    raw_txt = open(txt_path, encoding="utf-8", errors="ignore").read().strip()
    folder_name = os.path.basename(os.path.dirname(txt_path))
    parent_dir = os.path.basename(os.path.dirname(os.path.dirname(txt_path)))
    
    # Identify house
    house_code = None
    for k, v in HOUSE_MAP.items():
        if k in parent_dir.lower() or k in raw_txt.lower():
            house_code = v
            break
            
    is_cabinet = "school cabinet" in txt_path.lower()
    
    # Identify position
    txt_lower = raw_txt.lower()
    position = "UNKNOWN"
    if "vice" in txt_lower:
        position = "VICE CAPTAIN"
    elif "captain" in txt_lower:
        position = "CAPTAIN"
    elif is_cabinet:
        # e.g. President, Vice President, etc.
        pos_dir = os.path.basename(os.path.dirname(os.path.dirname(txt_path)))
        position = pos_dir.upper()
        
    # Identify symbol
    symbol = "Unknown"
    for s_name in ["royal bengal tiger", "ashoka chakra", "ashok chakra", "banyan tree", "hockey stick", 
                   "ganga river", "peacock", "tiger", "mango", "dolphin", "pumpkin", "river"]:
        if s_name in txt_lower:
            symbol = s_name.title()
            if "Ashok" in symbol:
                symbol = "Ashoka Chakra"
            if symbol == "Tiger":
                symbol = "Royal Bengal Tiger"
            break
            
    # Find candidate image
    folder = os.path.dirname(txt_path)
    imgs = [f for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    img_path = os.path.join(folder, imgs[0]) if imgs else None
    
    return {
        "folder": folder_name,
        "raw_txt": raw_txt,
        "house_code": house_code,
        "is_cabinet": is_cabinet,
        "position": position,
        "symbol": symbol,
        "img_path": img_path,
        "txt_path": txt_path
    }

if __name__ == "__main__":
    txt_files = glob.glob("1docs/contestets/**/New Text Document.txt", recursive=True)
    contestants = [extract_contestant_info(t) for t in txt_files]
    
    by_house = defaultdict(list)
    cabinet = []
    
    for c in contestants:
        if c["is_cabinet"]:
            cabinet.append(c)
        elif c["house_code"]:
            by_house[c["house_code"]].append(c)
            
    print(f"Total contestants parsed: {len(contestants)}")
    for h, clist in sorted(by_house.items()):
        print(f"House {h}: {len(clist)} contestants")
        captains = [c['folder'] for c in clist if c['position'] == 'CAPTAIN']
        vices = [c['folder'] for c in clist if c['position'] == 'VICE CAPTAIN']
        print(f"   Captains ({len(captains)}): {captains}")
        print(f"   Vice Captains ({len(vices)}): {vices}")
        
    print(f"\nSchool Cabinet: {len(cabinet)} contestants")
    for c in cabinet:
        print(f"   {c['position']}: {c['folder']} ({c['symbol']})")
