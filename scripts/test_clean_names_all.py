import os
import glob
import re
import json

base = "1docs/contestets"

def norm(s):
    return re.sub(r'[^a-zA-Z0-9]', '', str(s).lower())

# Build folder map
HOUSE_DIRS = {
    "bheeshma": "BHEESHMA",
    "gurudrona": "GURUDRONA",
    "hanuman": "HANUMAN",
    "hanuman house": "HANUMAN",
    "karan house": "KARNA",
    "karna": "KARNA",
    "vasistha house": "VASISTHA",
    "vasistha": "VASISTHA",
    "vishwamithra": "VISHWAMITHRA"
}

folder_map = []
for hdir in sorted(os.listdir(base)):
    hpath = os.path.join(base, hdir)
    if not os.path.isdir(hpath) or hdir == "School Cabinet":
        continue
    h_code = None
    for k, v in HOUSE_DIRS.items():
        if k in hdir.lower():
            h_code = v
            break
    for cfolder in sorted(os.listdir(hpath)):
        cpath = os.path.join(hpath, cfolder)
        if os.path.isdir(cpath):
            folder_map.append({
                'house': h_code,
                'folder': cfolder,
                'path': cpath
            })

cab_base = os.path.join(base, "School Cabinet")
if os.path.isdir(cab_base):
    for rdir in sorted(os.listdir(cab_base)):
        rpath = os.path.join(cab_base, rdir)
        if os.path.isdir(rpath):
            for cfolder in sorted(os.listdir(rpath)):
                cpath = os.path.join(rpath, cfolder)
                if os.path.isdir(cpath):
                    folder_map.append({
                        'house': 'CENTRAL',
                        'folder': cfolder,
                        'path': cpath
                    })

with open('Houses/assets/all-candidates.js', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'window\.ALL_CONTESTING_CANDIDATES = (\[.*?\]);', text, re.DOTALL)
existing = json.loads(m.group(1))

# Explicit accurate overrides based on official sheets + folder names
EXACT_NAME_FIXES = {
    # Bheeshma
    "Nikshita": "A.Nikshitha",
    "Leena Rugvedh": "B.Leena Rugvedh",
    "Bharath Yadav": "G.Bharath Yadav",
    "J .Parnika": "J.Parnika",
    "Hanshith": "M.Hanshith",
    "M.Hitharth Shourya": "M.Hitharth",
    "MD.Yasar": "Md.Yasar",
    "Niroop": "B.Niroop",
    "Sreeni": "P.Sreeni Goud",
    "Sai Geethika": "K.Sri Sai Geethika",
    "Ashwitha": "V.Ashwitha",
    "R.Akhilesh": "R.Akhilesh",
    
    # Gurudrona
    "CH.Ananya": "Ch.Ananya",
    "D. Ashwath": "D.Ashwath",
    "J.Rishi teja": "J.Rishi Teja",
    "M Hamsini": "M.Hamsini",
    "Y. Nitish pritam": "Y.Nitish Pritam",

    # Hanuman
    "A. Vignaneshwar": "A.Vignaneshwar",
    "B. Ranadheer": "B.Ranadheer",
    "Ch. Ruthvik": "Ch.Ruthvik",
    "D. Gunasri": "D.Gunasri",
    "K.Kruthvik": "K.Kruthvik",
    "K. Samarjith Reddy": "K.Samarjith Reddy",
    "K. Vignesh Yadav": "K.Vignesh Yadav",
    "M. Ashish Rutwika": "M.Ashish Rutwika",
    "M. Lasya": "M.Lasya",
    "P. Aishwarya": "P.Aishwarya",
    "P. Rishikesh": "P.Rishikesh",
    "P. Vishruth Reddy": "P.Vishruth Reddy",
    "S. Chaintanya": "S.Chaitanya",
    ".SNIGDHA": "M.Snigdha",
    "T. Preeti": "T.Preeti",
    "T. Sragvi": "T.Sragvi",

    # Karna
    "B. Amulya": "B.Amulya",
    "B. Pragna Priya": "B.Pragna Priya",
    "G. Goutham krishna": "G.Goutham Krishna",
    "G. Rishwith": "G.Rishwith",
    "I. Aradhya": "I.Aradhya",
    "K. Aaradhya": "K.Aaradhya",
    "K. Guna Ashmith": "K.Guna Ashmith",
    "K. Kushal Raj": "K.Kushal Raj",
    "K. Sri Theja": "K.Sri Theja",
    "K. Varshith": "K.Varshith",
    "K. Veeksha": "K.Veeksha",
    "M.Aarush": "M.Aarush",
    "P. Aneesh kumar": "P.Aneesh Kumar",
    "P. Pravasthi": "P.Pravasthi",
    "P. Prem Sagar": "P.Prem Sagar",
    "R. Anjana priya": "R.Anjana Priya",
    "V. Amrutha": "V.Amrutha",

    # Vasistha
    "A. Anwitha": "A.Anwitha",
    "B. Sahasra": "B.Sahasra",
    "B. Snigdatha reddy": "B.Snigdatha Reddy",
    "CH. Karthikeya": "Ch.Karthikeya",
    "CH. Ruthvish": "Ch.Ruthvish",
    "D. Partha Ishani": "D.Partha Ishani",
    "G. Greeshma": "G.Greeshma",
    "K. Rasagna": "K.Rasagna",
    "M. Krishnika": "M.Krishnika",
    "M. Vaibhav": "M.Vaibhav",
    "N. Sriteja": "N.Sriteja",
    "N. Sushen": "N.Sushen",
    "S. Shreyas goud": "S.Shreyas Goud",
    "K. Namratha": "K.Namratha",

    # Vishwamithra
    "Nandan.B": "B.Nandan",
    "G.sharanya Raj": "G.Sharanya Raj",
    "P.yashasvi Reddy": "P.Yashasvi Reddy",
    "J. Harshith": "J.Harshith",
    "D.Sree manoharini": "D.Sree Manoharini",
    "A.Adwitha reddy": "A.Adwitha Reddy",

    # Central (Cabinet)
    "Indu priya": "P.Indu Priya",
    "Srunith Goud": "G.Srunith Goud",
    "Shubhi Patel": "S.Shubhi Patel",
    "G.Harsha vardhan Rao": "G.Harshavardhan Rao",
    "Y.Bhavya sri": "Y.Bhavya Sri",
    "Y.Nithya sri": "Y.Nithya Sri",
    "S Rithvik Reddy": "S.Rithvik Reddy",
}

def get_clean_name(cand):
    old = cand['fullName'].strip()
    if old in EXACT_NAME_FIXES:
        return EXACT_NAME_FIXES[old]
    
    # Check folder match
    c_photo = cand.get('photoPath', '').replace('../assets/candidates/', '')
    c_h = cand.get('houseCode', '')
    for f in folder_map:
        if f['house'] == c_h:
            fn = f['folder'].strip()
            if norm(fn) in norm(c_photo) or norm(c_photo) in norm(fn) or norm(fn) == norm(old):
                # Clean up initial format: e.g. "B.Karthikeya" -> keep as is
                # "k.Namratha" -> "K.Namratha"
                # "Ch.kowshik" -> "Ch.Kowshik"
                if re.match(r'^[a-zA-Z]{1,2}\.', fn):
                    parts = fn.split('.', 1)
                    init = parts[0].upper()
                    if init.lower() in ['ch', 'md']:
                        init = init.capitalize()
                    name = parts[1].strip()
                    # capitalize words
                    name = " ".join([w[0].upper() + w[1:] if len(w) > 1 else w.upper() for w in name.split()])
                    return f"{init}.{name}"
                return fn
    return old

updated_count = 0
for c in existing:
    clean = get_clean_name(c)
    if clean != c['fullName']:
        print(f"[{c['houseCode']}] '{c['fullName']}' -> '{clean}'")
        c['fullName'] = clean
        updated_count += 1

print(f"\nTotal names updated: {updated_count}/140")
