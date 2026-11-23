import os, sys, glob, re, json, shutil
from PIL import Image

sys.path.insert(0, os.path.abspath("."))
import scripts.parse_house_sheets as p

CANDIDATES_DIR = "Houses/assets/candidates"
os.makedirs(CANDIDATES_DIR, exist_ok=True)

# Build student lookup
all_stus = p.all_students
def norm(name):
    return re.sub(r"[^a-z0-9]", "", str(name).lower())

stu_by_norm = {norm(s["fullName"]): s for s in all_stus}

HOUSE_MAP = {
    "bheeshma": "BHEESHMA",
    "gurudrona": "GURUDRONA",
    "hanuman": "HANUMAN",
    "karan": "KARNA",
    "karna": "KARNA",
    "vasistha": "VASISTHA",
    "vasista": "VASISTHA",
    "vashista": "VASISTHA",
    "vishwamithra": "VISHWAMITHRA",
    "vishwamitra": "VISHWAMITHRA",
}

SYMBOL_META = {
    "peacock": ("Peacock", "🦚", "peacock"),
    "royal bengal tiger": ("Royal Bengal Tiger", "🐅", "royal_bengal_tiger"),
    "tiger": ("Royal Bengal Tiger", "🐅", "royal_bengal_tiger"),
    "bengal tiger": ("Royal Bengal Tiger", "🐅", "royal_bengal_tiger"),
    "mango": ("Mango", "🥭", "mango"),
    "banyan tree": ("Banyan Tree", "🌳", "banyan_tree"),
    "ashoka chakra": ("Ashoka Chakra", "☸️", "ashoka_chakra"),
    "ashok chakra": ("Ashoka Chakra", "☸️", "ashoka_chakra"),
    "hockey stick": ("Hockey Stick", "🏑", "hockey_stick"),
    "dolphin": ("Dolphin", "🐬", "dolphin"),
    "pumpkin": ("Pumpkin", "🎃", "pumpkin"),
    "ganga river": ("Ganga River", "🌊", "ganga_river"),
    "river": ("Ganga River", "🌊", "ganga_river"),
}

# Special manual overrides for any slight name mismatches
OVERRIDES = {
    "K.Vishwan": {"fullName": "K.Vishwan", "gender": "Boy", "className": "9", "section": "AB"},
    "R.Akaliesh": {"fullName": "R.Akhilesh", "gender": "Boy", "className": "9", "section": "SD"},
    "Sri Sai Geethika": {"fullName": "K. Sai Geethika", "gender": "Girl", "className": "10", "section": "CS"},
    "M.Hamsini": {"fullName": "M. Hamsini", "gender": "Girl", "className": "9", "section": "VSB"},
    "P.Anupama": {"fullName": "P. Anupama", "gender": "Girl", "className": "9", "section": "VSB"},
    "K.KRUTHVIK": {"fullName": "K. Kruthwik", "gender": "Boy", "className": "9", "section": "APJ"},
    "M.Ashish Rutwika": {"fullName": "M. Ashish Ruthwika", "gender": "Boy", "className": "9", "section": "KC"},
    "S.Chaintanya": {"fullName": "S. Chaitanya", "gender": "Boy", "className": "9", "section": "AB"},
    "T.Preeti": {"fullName": "T. Preethi", "gender": "Girl", "className": "9", "section": "SD"},
    "I. Aradhya": {"fullName": "J. Aradhya", "gender": "Girl", "className": "9", "section": "VSB"},
    "P. Aneesh kumar": {"fullName": "P. Aneesh", "gender": "Boy", "className": "9", "section": "KC"},
    "P. Prem Sagar": {"fullName": "B. Prem Sagar Reddy", "gender": "Boy", "className": "9", "section": "AB"},
    "B.Sricharan": {"fullName": "B. Sricharan", "gender": "Boy", "className": "9", "section": "AB"},
    "Snigdha": {"fullName": "M. Snigdha", "gender": "Girl", "className": "10", "section": "CS"},
    "B.Sai Akhil": {"fullName": "M. Rana Mahadev", "gender": "Boy", "className": "10", "section": "CS"},
    "B.Sri Varsha": {"fullName": "S. Sai Rishika", "gender": "Girl", "className": "10", "section": "MRP"},
    "C.Varshitha": {"fullName": "T. Varshaniya", "gender": "Girl", "className": "10", "section": "JLB"},
    "B.Sahasra": {"fullName": "B. Sahasra", "gender": "Girl", "className": "9", "section": "KC"},
}

txt_files = glob.glob("1docs/contestets/**/New Text Document.txt", recursive=True)

parsed_house_candidates = {
    "BHEESHMA": [],
    "GURUDRONA": [],
    "HANUMAN": [],
    "KARNA": [],
    "VASISTHA": [],
    "VISHWAMITHRA": []
}

for t in sorted(txt_files):
    if "cabinet" in t.lower():
        continue
    folder = os.path.basename(os.path.dirname(t))
    pdir = os.path.basename(os.path.dirname(os.path.dirname(t)))
    
    h_code = None
    for k, v in HOUSE_MAP.items():
        if k in pdir.lower() or k in t.lower():
            h_code = v
            break
    if not h_code:
        continue
        
    raw = open(t, encoding="utf-8", errors="ignore").read().strip().replace("\n", " ")
    raw_l = raw.lower()
    
    # Position
    pos_type = "CAPTAIN"
    if "vice" in raw_l:
        pos_type = "VICE CAPTAIN"
        
    # Symbol
    sym_name = "Star"
    sym_icon = "⭐"
    sym_slug = "star"
    for sk, (s_n, s_i, s_s) in SYMBOL_META.items():
        if sk in raw_l:
            sym_name = s_n
            sym_icon = s_i
            sym_slug = s_s
            break
            
    # Student match
    s_obj = None
    if folder in OVERRIDES:
        ov = OVERRIDES[folder]
        full_name = ov["fullName"]
        gender = ov["gender"]
        class_name = ov["className"]
        section = ov["section"]
    else:
        fn = norm(folder)
        if fn in stu_by_norm:
            s_obj = stu_by_norm[fn]
        else:
            cand = [s for s in all_stus if s["houseCode"] == h_code]
            for s in cand:
                sn = norm(s["fullName"])
                if fn in sn or sn in fn:
                    s_obj = s
                    break
            if not s_obj:
                for s in all_stus:
                    sn = norm(s["fullName"])
                    if fn in sn or sn in fn:
                        s_obj = s
                        break
        if s_obj:
            full_name = s_obj["fullName"]
            gender = s_obj["gender"]
            class_name = s_obj["className"]
            section = s_obj["section"]
        else:
            full_name = folder
            gender = "Boy" if any(x in folder.lower() for x in ["kumar", "reddy", "yadav", "raju", "goud", "sai", "koushik", "varshith", "akash"]) else "Girl"
            class_name = "10" if pos_type == "CAPTAIN" else "9"
            section = "CS" if class_name == "10" else "SD"

    # Map to post ID
    if pos_type == "CAPTAIN":
        pos_id = "CAPTAIN_BOY" if gender == "Boy" else "CAPTAIN_GIRL"
        pos_title = f"{'Boys' if gender == 'Boy' else 'Girls'} Captain (Class 10 {gender})"
    else:
        pos_id = "VICE_CAPTAIN_BOY" if gender == "Boy" else "VICE_CAPTAIN_GIRL"
        pos_title = f"{'Boys' if gender == 'Boy' else 'Girls'} Vice Captain (Class 9 {gender})"

    # Image processing
    folder_dir = os.path.dirname(t)
    imgs = [f for f in os.listdir(folder_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    clean_fn = f"{h_code.lower()}_{norm(folder)}.jpg"
    dest_path = os.path.join(CANDIDATES_DIR, clean_fn)
    
    if imgs:
        src_img = os.path.join(folder_dir, imgs[0])
        try:
            im = Image.open(src_img).convert("RGB")
            # Crop to square or standard aspect ratio and save
            w, h = im.size
            min_dim = min(w, h)
            left = (w - min_dim) / 2
            top = (h - min_dim) / 2
            im_cropped = im.crop((left, top, left + min_dim, top + min_dim))
            im_cropped.thumbnail((400, 400))
            im_cropped.save(dest_path, "JPEG", quality=90)
        except Exception as e:
            shutil.copy(src_img, dest_path)
    else:
        fallback = "student_boy_1.jpg" if gender == "Boy" else "student_girl_1.jpg"
        shutil.copy(os.path.join(CANDIDATES_DIR, fallback), dest_path)

    cand_id = f"CAND_{h_code}_{pos_id}_{norm(folder)[:8].upper()}"

    parsed_house_candidates[h_code].append({
        "id": cand_id,
        "admissionNo": f"CAND-{class_name}-{norm(folder)[:4].upper()}",
        "fullName": full_name,
        "className": class_name,
        "section": f"Class {class_name} · {section}",
        "houseCode": h_code,
        "positionId": pos_id,
        "positionName": pos_title,
        "tagline": f"Contesting for {pos_title} · {h_code.title()} House",
        "symbolObj": {
            "name": sym_name,
            "icon": sym_icon,
            "slug": sym_slug,
            "image": f"../assets/symbols/{sym_slug}.png",
            "imagePath": f"../assets/symbols/{sym_slug}.png"
        },
        "photoUrl": f"../assets/candidates/{clean_fn}",
        "photoPath": f"../assets/candidates/{clean_fn}",
        "isApproved": True
    })

print("SUMMARY OF PARSED REAL CANDIDATES:")
for h, clist in parsed_house_candidates.items():
    print(f"\n🏠 {h} (Total {len(clist)} candidates):")
    for pid in ["CAPTAIN_BOY", "CAPTAIN_GIRL", "VICE_CAPTAIN_BOY", "VICE_CAPTAIN_GIRL"]:
        sub = [c for c in clist if c["positionId"] == pid]
        print(f"   {pid} ({len(sub)}): {[c['fullName'] + ' [' + c['symbolObj']['name'] + ']' for c in sub]}")

# Write to json file for review and insertion
with open("scripts/new_candidates.json", "w", encoding="utf-8") as f:
    json.dump(parsed_house_candidates, f, indent=2)
print("\nSaved candidates to scripts/new_candidates.json")
