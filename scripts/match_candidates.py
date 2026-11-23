import os, sys, glob, re
sys.path.insert(0, os.path.abspath("."))
import scripts.parse_house_sheets as p

def norm(name):
    return re.sub(r"[^a-z0-9]", "", str(name).lower())

all_stus = p.all_students
stu_by_norm = {norm(s["fullName"]): s for s in all_stus}

txts = glob.glob("1docs/contestets/**/New Text Document.txt", recursive=True)

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

print(f"Total txt files: {len(txts)}")

unmatched = []
matched_candidates = []

for t in txts:
    folder = os.path.basename(os.path.dirname(t))
    pdir = os.path.basename(os.path.dirname(os.path.dirname(t)))
    is_cabinet = "cabinet" in t.lower()
    
    h_code = None
    for k, v in HOUSE_MAP.items():
        if k in pdir.lower() or k in t.lower():
            h_code = v
            break
            
    raw = open(t, encoding="utf-8", errors="ignore").read().strip().replace("\n", " ")
    raw_l = raw.lower()
    
    # Position
    pos = "UNKNOWN"
    if "vice" in raw_l:
        pos = "VICE CAPTAIN"
    elif "captain" in raw_l:
        pos = "CAPTAIN"
        
    f_norm = norm(folder)
    
    # Try finding in students
    matched_student = None
    if f_norm in stu_by_norm:
        matched_student = stu_by_norm[f_norm]
    else:
        # Try within house or all students
        candidates = [s for s in all_stus if (not h_code or s["houseCode"] == h_code)]
        for s in candidates:
            s_n = norm(s["fullName"])
            if f_norm in s_n or s_n in f_norm:
                matched_student = s
                break
        if not matched_student:
            for s in all_stus:
                s_n = norm(s["fullName"])
                if f_norm in s_n or s_n in f_norm:
                    matched_student = s
                    break

    # Determine gender & class
    if matched_student:
        gender = matched_student["gender"]
        c_name = matched_student["className"]
        actual_house = matched_student["houseCode"]
    else:
        gender = "Unknown"
        c_name = "10" if pos == "CAPTAIN" else "9"
        actual_house = h_code
        unmatched.append((folder, h_code, pos, raw))
        
    # Map to position ID
    if pos == "CAPTAIN":
        pos_id = "CAPTAIN_BOY" if gender == "Boy" else "CAPTAIN_GIRL"
    elif pos == "VICE CAPTAIN":
        pos_id = "VICE_CAPTAIN_BOY" if gender == "Boy" else "VICE_CAPTAIN_GIRL"
    else:
        pos_id = "CABINET"

    # Image
    fdir = os.path.dirname(t)
    imgs = [f for f in os.listdir(fdir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    img_src = os.path.join(fdir, imgs[0]) if imgs else None

    matched_candidates.append({
        "folder": folder,
        "house": h_code or actual_house,
        "is_cabinet": is_cabinet,
        "pos": pos,
        "pos_id": pos_id,
        "gender": gender,
        "class": c_name,
        "matched_student": matched_student["fullName"] if matched_student else folder,
        "raw": raw,
        "img_src": img_src
    })

print(f"\nSuccessfully processed {len(matched_candidates)} candidates.")
print(f"Unmatched count: {len(unmatched)}")
if unmatched:
    print("Sample unmatched:")
    for u in unmatched[:10]:
        print("  ", u)
