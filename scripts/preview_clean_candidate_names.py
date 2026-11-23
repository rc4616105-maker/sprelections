import os
import glob
import re
import json

base = "1docs/contestets"

def norm(s):
    return re.sub(r'[^a-zA-Z0-9]', '', str(s).lower())

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

folder_list = []
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
            folder_list.append({
                'house': h_code,
                'folder_name': cfolder,
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
                    folder_list.append({
                        'house': 'CENTRAL',
                        'folder_name': cfolder,
                        'path': cpath
                    })

with open('Houses/assets/all-candidates.js', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'window\.ALL_CONTESTING_CANDIDATES = (\[.*?\]);', text, re.DOTALL)
existing = json.loads(m.group(1))

# Format folder name cleanly:
# e.g. "A.Nikshitha" -> "A.Nikshitha"
# "k.Namratha" -> "K.Namratha"
# "Ch.kowshik" -> "Ch.Kowshik"
# ".SNIGDHA" -> "M.Snigdha" or "Snigdha"
def clean_display_name(raw_folder, existing_cand=None):
    s = raw_folder.strip()
    # Remove leading dots if any like .SNIGDHA
    if s.startswith('.'):
        s = s.lstrip('.')
    
    # Fix casing like k.Namratha -> K.Namratha
    # Match pattern: letter(s) + dot + name
    m = re.match(r'^([a-zA-Z]{1,3})\.([a-zA-Z\s]+)$', s)
    if m:
        init = m.group(1).upper()
        if len(init) == 2 and init.lower() in ['ch', 'md']:
            init = init.capitalize()
        name_part = m.group(2).strip()
        # Capitalize words in name_part properly if all uppercase or lowercase
        if name_part.isupper() or name_part.islower():
            name_part = " ".join([w.capitalize() for w in name_part.split()])
        else:
            # Title case words
            name_part = " ".join([w[0].upper() + w[1:] if len(w) > 1 else w.upper() for w in name_part.split()])
        return f"{init}.{name_part}"
    
    # Check if format is "Name.B" like "Nandan.B" -> "B.Nandan"
    m_rev = re.match(r'^([a-zA-Z\s]+)\.([a-zA-Z]{1,2})$', s)
    if m_rev:
        init = m_rev.group(2).upper()
        name_part = m_rev.group(1).strip()
        if name_part.isupper() or name_part.islower():
            name_part = " ".join([w.capitalize() for w in name_part.split()])
        return f"{init}.{name_part}"

    # Multiple initials like "CH. Ruthvik" or "A. Megha Sanjana"
    m_space = re.match(r'^([a-zA-Z]{1,3})\.\s+([a-zA-Z\s]+)$', s)
    if m_space:
        init = m_space.group(1).upper()
        if len(init) == 2 and init.lower() in ['ch', 'md']:
            init = init.capitalize()
        name_part = m_space.group(2).strip()
        name_part = " ".join([w[0].upper() + w[1:] if len(w) > 1 else w.upper() for w in name_part.split()])
        return f"{init}.{name_part}"

    # If it's a name with space like "Bharath Yadav", "Sri Sai Geethika"
    words = s.split()
    clean_words = []
    for w in words:
        if '.' in w:
            parts = w.split('.')
            clean_parts = [p.capitalize() if len(p) > 2 else p.upper() for p in parts if p]
            clean_words.append(".".join(clean_parts) + ".")
        else:
            clean_words.append(w.capitalize() if w.isupper() or w.islower() else w)
    return " ".join(clean_words)

for c in existing:
    c_photo = c.get('photoPath', '').replace('../assets/candidates/', '')
    c_h = c.get('houseCode', '')
    c_fn = c['fullName']
    
    f_match = None
    for f in folder_list:
        if f['house'] == c_h:
            if norm(f['folder_name']) in norm(c_photo) or norm(c_photo) in norm(f['folder_name']):
                f_match = f
                break
            if norm(f['folder_name']) == norm(c_fn) or norm(f['folder_name']) in norm(c_fn) or norm(c_fn) in norm(f['folder_name']):
                f_match = f
                break
                
    old_name = c['fullName']
    folder_raw = f_match['folder_name'] if f_match else old_name
    cleaned_name = clean_display_name(folder_raw, c)
    # Special overrides for exact school names
    if folder_raw == "R.Akaliesh":
        cleaned_name = "R.Akhilesh"
    elif folder_raw == "Snigdha" or folder_raw == ".SNIGDHA":
        cleaned_name = "M.Snigdha" if c.get('className') == "10" else "Snigdha"
    elif folder_raw == "Sri Sai Geethika":
        cleaned_name = "K.Sri Sai Geethika"
    elif folder_raw == "Bharath Yadav":
        cleaned_name = "D.Bharath Yadav"
    elif folder_raw == "Niroop":
        cleaned_name = "B.Niroop"
    elif folder_raw == "Sreeni":
        cleaned_name = "K.Sreeni"
    elif folder_raw == "Shubhi Patel":
        cleaned_name = "Shubhi Patel"
    elif folder_raw == "Enrique Iglesias":
        cleaned_name = "Enrique Iglesias"
    elif folder_raw == "Indu priya":
        cleaned_name = "P.Indu Priya"
    elif folder_raw == "Srunith Goud":
        cleaned_name = "V.Srunith Goud"
    elif folder_raw == "J.Rishi teja":
        cleaned_name = "J.Rishi Teja"
    elif folder_raw == "Y.Nitish Pritam":
        cleaned_name = "Y.Nitish Pritam"
    elif folder_raw == "B.Snigdatha reddy":
        cleaned_name = "B.Snigdatha Reddy"
    elif folder_raw == "P.yashasvi Reddy":
        cleaned_name = "P.Yashasvi Reddy"
    elif folder_raw == "G.sharanya Raj":
        cleaned_name = "G.Sharanya Raj"
    elif folder_raw == "k.Namratha":
        cleaned_name = "K.Namratha"
    elif folder_raw == "A.Adwitha Reddy":
        cleaned_name = "A.Adwitha Reddy"
    elif folder_raw == "D.Sree Manoharini":
        cleaned_name = "D.Sree Manoharini"
    elif folder_raw == "Ch.Shivasri":
        cleaned_name = "Ch.Shivasri"

    c['new_display_name'] = cleaned_name
    if old_name != cleaned_name:
        print(f"[{c_h}] '{old_name}' -> '{cleaned_name}' (from folder: '{folder_raw}')")
