import os, re, json

base = "1docs/contestets"

houses = ["Bheeshma", "Gurudrona", "Hanuman house", "KAran house", "Vasistha house", "Vishwamithra", "School Cabinet"]

all_extracted = []

def parse_txt(txt, folder_name, house_name, subfolder=""):
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    full_text = " | ".join(lines)
    
    # Try parsing key: value
    data = {}
    for l in lines:
        if ":" in l:
            k, v = l.split(":", 1)
            data[k.strip().lower()] = v.strip()
    
    name = data.get("name")
    symbol = data.get("symbol")
    post = data.get("contesting as") or data.get("post") or data.get("contesting post")
    
    # If not in key:value, parse comma or pipe
    if not name:
        parts = [p.strip() for p in re.split(r'[,|]', full_text) if p.strip()]
        # Typically: House, Name, Symbol, Post
        if len(parts) >= 2:
            # check if part 0 is house
            if any(h.lower() in parts[0].lower() for h in ["bheeshma", "guru", "hanuman", "karan", "karna", "vasistha", "vishwa", "cabinet"]):
                name = parts[1]
                if len(parts) >= 3: symbol = parts[2]
                if len(parts) >= 4: post = parts[3]
            else:
                name = parts[0]
                if len(parts) >= 2: symbol = parts[1]
                if len(parts) >= 3: post = parts[2]
    
    if not name:
        name = folder_name
        
    return {
        "raw_text": full_text,
        "name": name,
        "symbol": symbol,
        "post": post
    }

for h in houses:
    hpath = os.path.join(base, h)
    if not os.path.exists(hpath): continue
    
    if h == "School Cabinet":
        for sub in os.listdir(hpath):
            subpath = os.path.join(hpath, sub)
            if not os.path.isdir(subpath): continue
            for cand in os.listdir(subpath):
                cp = os.path.join(subpath, cand)
                if not os.path.isdir(cp): continue
                imgs = [f for f in os.listdir(cp) if f.lower().endswith(('.jpg', '.jpeg', '.png')) and not f.startswith('symbol')]
                txts = [f for f in os.listdir(cp) if f.endswith('.txt')]
                raw_txt = ""
                if txts:
                    with open(os.path.join(cp, txts[0]), 'r', encoding='utf-8', errors='ignore') as fp:
                        raw_txt = fp.read().strip()
                parsed = parse_txt(raw_txt, cand, h, sub)
                all_extracted.append({
                    "house": "School Cabinet",
                    "subfolder": sub,
                    "folder": cand,
                    "parsed": parsed,
                    "img": imgs[0] if imgs else None,
                    "img_path": os.path.join(cp, imgs[0]) if imgs else None
                })
    else:
        for cand in os.listdir(hpath):
            cp = os.path.join(hpath, cand)
            if not os.path.isdir(cp): continue
            imgs = [f for f in os.listdir(cp) if f.lower().endswith(('.jpg', '.jpeg', '.png')) and not f.startswith('symbol')]
            txts = [f for f in os.listdir(cp) if f.endswith('.txt')]
            raw_txt = ""
            if txts:
                with open(os.path.join(cp, txts[0]), 'r', encoding='utf-8', errors='ignore') as fp:
                    raw_txt = fp.read().strip()
            parsed = parse_txt(raw_txt, cand, h)
            all_extracted.append({
                "house": h,
                "subfolder": "",
                "folder": cand,
                "parsed": parsed,
                "img": imgs[0] if imgs else None,
                "img_path": os.path.join(cp, imgs[0]) if imgs else None
            })

print(f"Total extracted from 1docs: {len(all_extracted)}")
with open("scripts/extracted_contestants.json", "w", encoding="utf-8") as fp:
    json.dump(all_extracted, fp, indent=2)

print("Saved to scripts/extracted_contestants.json")
