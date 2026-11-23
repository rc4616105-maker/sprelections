import zipfile, xml.etree.ElementTree as ET, re, random, json, urllib.request, time

random.seed(20261123)

SHEET_COLS = {
    ("BHEESHMA", "6"): ("A", "B", "E", "F"),
    ("BHEESHMA", "7"): ("A", "B", "D", "F"),
    ("BHEESHMA", "8"): ("A", "B", "E", "F"),
    ("BHEESHMA", "9"): ("A", "D", "E", "H"),
    ("BHEESHMA", "10"): ("A", "D", "E", "H"),
    
    ("GURUDRONA", "6"): ("A", "D", "F", "G"),
    ("GURUDRONA", "7"): ("A", "D", "F", "G"),
    ("GURUDRONA", "8"): ("A", "B", "E", "F"),
    ("GURUDRONA", "9"): ("A", "D", "E", "H"),
    ("GURUDRONA", "10"): ("A", "D", "E", "H"),
    
    ("HANUMAN", "6"): ("A", "D", "E", "H"),
    ("HANUMAN", "7"): ("A", "B", "E", "F"),
    ("HANUMAN", "8"): ("A", "B", "E", "F"),
    ("HANUMAN", "9"): ("A", "D", "E", "H"),
    ("HANUMAN", "10"): ("A", "D", "E", "H"),
    
    ("KARNA", "6"): ("A", "B", "E", "F"),
    ("KARNA", "7"): ("A", "B", "F", "G"),
    ("KARNA", "8"): ("A", "B", "E", "F"),
    ("KARNA", "9"): ("A", "D", "E", "H"),
    ("KARNA", "10"): ("A", "D", "E", "H"),
    
    ("VASISTHA", "6"): ("A", "D", "E", "H"),
    ("VASISTHA", "7"): ("A", "B", "E", "F"),
    ("VASISTHA", "8"): ("A", "B", "E", "F"),
    ("VASISTHA", "9"): ("A", "D", "E", "H"),
    ("VASISTHA", "10"): ("A", "D", "E", "H"),
    
    ("VISHWAMITHRA", "6"): ("A", "D", "E", "H"),
    ("VISHWAMITHRA", "7"): ("A", "B", "E", "F"),
    ("VISHWAMITHRA", "8"): ("A", "B", "E", "F"),
    ("VISHWAMITHRA", "9"): ("A", "D", "E", "H"),
    ("VISHWAMITHRA", "10"): ("A", "D", "E", "H"),
}

files_houses = [
    ('1docs/Bheesma (1).xlsx', 'BHEESHMA', 'Bheeshma'),
    ('1docs/Gurudrona (1).xlsx', 'GURUDRONA', 'Gurudrona'),
    ('1docs/Hanuman.xlsx', 'HANUMAN', 'Hanuman'),
    ('1docs/Karan.xlsx', 'KARNA', 'Karna'),
    ('1docs/Vasista.xlsx', 'VASISTHA', 'Vasistha'),
    ('1docs/Viswamitra (1).xlsx', 'VISHWAMITHRA', 'Vishwamithra')
]

IGNORED_NAMES = {
    "", "boys", "girls", "name", "names", "section", "sections", "total",
    "class", "satish dhawan", "aryabhatta", "vikram sarabhai", "kalpana chawla",
    "apj abdul kalam", "vsb", "ab", "sd", "kc", "apj", "kc section", "apj section",
    "`", "chatrapathi shivaji", "maha raana pratap", "jhansi laxmi bai", "ashoka chakravarthi",
    "cs", "mrp", "jlb", "ac"
}

def clean_sec(s):
    if not s:
        return ""
    val = re.sub(r'\s+', ' ', str(s).strip()).upper()
    if "AMBEDKAR" in val or "DR BR" in val:
        return "AMBEDKAR"
    if val in ("SATISH DHAWAN", "SATISH DHAWAN \t", "SD"):
        return "SD"
    if val in ("ARYABHATTA", "AB"):
        return "AB"
    if val in ("VIKRAM SARABHAI", "VSB"):
        return "VSB"
    if val in ("KALPANA CHAWLA", "KC"):
        return "KC"
    if val in ("APJ ABDUL KALAM", "APJ SECTION", "APJ"):
        return "APJ"
    if val in ("CHATHRAPATHI SHIVAJI", "CHATRAPATHI SHIVAJI", "CS"):
        return "CS"
    if val in ("MAHA RAANA PRATAP", "MAHARANA PRATAP", "MRP"):
        return "MRP"
    if val in ("JHANSI LAXMI BAI", "JHANSI LAKSHMI BAI", "JLB"):
        return "JLB"
    if val in ("ASHOKA CHAKRAVARTHI", "ASHOKA CHAKRAVARTHY", "AC"):
        return "AC"
    return val

all_students = []

for path, hcode, hname in files_houses:
    with zipfile.ZipFile(path, 'r') as z:
        wb_xml = z.read('xl/workbook.xml')
        wb_tree = ET.fromstring(wb_xml)
        ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        sheets = [s.attrib['name'] for s in wb_tree.findall('.//main:sheet', ns)]
        
        shared_strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            ss_xml = z.read('xl/sharedStrings.xml')
            ss_tree = ET.fromstring(ss_xml)
            for si in ss_tree.findall('.//main:si', ns):
                text = "".join([t.text or "" for t in si.findall('.//main:t', ns)])
                shared_strings.append(text)
                
        for sname in sheets:
            if 'total' in sname.lower():
                continue
            c_match = re.search(r'(\d+)', sname)
            class_num = c_match.group(1) if c_match else sname
            
            b_col, bs_col, g_col, gs_col = SHEET_COLS[(hcode, class_num)]
            
            sidx = sheets.index(sname) + 1
            sxml = z.read(f'xl/worksheets/sheet{sidx}.xml')
            stree = ET.fromstring(sxml)
            
            current_b_sec = ""
            current_g_sec = ""
            
            for r in stree.findall('.//main:row', ns):
                rnum = int(r.attrib.get('r'))
                cells = {}
                for c in r.findall('.//main:c', ns):
                    ref = c.attrib.get('r', '')
                    col = re.sub(r'\d+', '', ref)
                    t_type = c.attrib.get('t')
                    v = c.find('.//main:v', ns)
                    val = v.text if v is not None else ''
                    if t_type == 's' and val.isdigit():
                        val = shared_strings[int(val)]
                    cells[col] = val.strip()
                    
                row_str = " ".join(cells.values()).lower()
                if rnum <= 2 and any(w in row_str for w in ['boys', 'girls', 'names', 'name', 'section', 'sections']):
                    continue
                if 'total' in row_str and ('class' in row_str or 'boys' in row_str):
                    continue
                    
                b_name = (cells.get(b_col) or '').strip()
                b_sec = clean_sec(cells.get(bs_col) or '')
                if b_sec:
                    current_b_sec = b_sec
                else:
                    b_sec = current_b_sec
                    
                g_name = (cells.get(g_col) or '').strip()
                g_sec = clean_sec(cells.get(gs_col) or '')
                if g_sec:
                    current_g_sec = g_sec
                else:
                    g_sec = current_g_sec
                    
                if b_name and b_name.lower() not in IGNORED_NAMES and len(b_name) > 2:
                    all_students.append({
                        "fullName": b_name,
                        "gender": "Boy",
                        "className": class_num,
                        "section": b_sec if b_sec else "A",
                        "houseCode": hcode,
                        "houseName": hname
                    })
                    
                if g_name and g_name.lower() not in IGNORED_NAMES and len(g_name) > 2:
                    all_students.append({
                        "fullName": g_name,
                        "gender": "Girl",
                        "className": class_num,
                        "section": g_sec if g_sec else "A",
                        "houseCode": hcode,
                        "houseName": hname
                    })

print(f"Total students parsed cleanly: {len(all_students)}")

# Candidate matching
with open('Houses/admin/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('"candidates":')
c_text = text[idx + len('"candidates":'):].strip()
if c_text.endswith('};'):
    c_text = c_text[:-2].strip()
elif c_text.endswith('}'):
    c_text = c_text[:-1].strip()

candidates = json.loads(c_text)

def clean_tokens(s):
    s = re.sub(r'[^a-zA-Z\s]', ' ', s or '').lower()
    return set(w for w in s.split() if len(w) >= 3)

for c in candidates:
    c_name = c.get('fullName', '')
    c_tokens = clean_tokens(c_name)
    c_house = c.get('houseCode', '')
    c_class = str(c.get('className', ''))
    
    for s in all_students:
        s_name = s.get('fullName', '')
        s_tokens = clean_tokens(s_name)
        s_house = s.get('houseCode', '')
        s_class = str(s.get('className', ''))
        
        if c_house != 'CENTRAL' and s_house != c_house:
            continue
        if c_class and s_class and c_class != s_class:
            continue
            
        common = c_tokens.intersection(s_tokens)
        if common:
            s['isCandidate'] = True
            s['positionName'] = c.get('positionName', '')
            s['positionId'] = c.get('positionId', '')
            if c.get('photoUrl'):
                s['photoUrl'] = c.get('photoUrl')
            break

# Generate unique IDs: [ClassDigit][SectionLetter][4RandomDigits]
used_ids = set(["1C8492"])

for s in all_students:
    cl = s['className']
    class_digit = "1" if cl == "10" else str(cl)
    sec = s['section']
    sec_letter = "S"
    for ch in sec:
        if ch.isalpha():
            sec_letter = ch.upper()
            break
            
    while True:
        r_digits = f"{random.randint(1000, 9999)}"
        cand_id = f"{class_digit}{sec_letter}{r_digits}"
        if cand_id not in used_ids:
            used_ids.add(cand_id)
            s['admissionNo'] = cand_id
            break

# Save new_students_roster.json
with open('new_students_roster.json', 'w', encoding='utf-8') as f:
    json.dump(all_students, f, indent=2)

print("Saved clean new_students_roster.json!")

# Demo student
demo_stu = {
    "admissionNo": "1C8492",
    "fullName": "Aditya Vikram",
    "gender": "Boy",
    "fatherName": "R. K. Vikram",
    "className": "10",
    "section": "CS",
    "houseCode": "BHEESHMA",
    "isActive": True,
    "isCandidate": False,
    "positionName": "",
    "photoUrl": "../assets/candidates/student_demo.jpg",
    "isUniversal": True
}

def make_stu_dict(s):
    d = {
        "admissionNo": s["admissionNo"],
        "fullName": s["fullName"],
        "gender": s.get("gender", "Boy"),
        "fatherName": s.get("fatherName", ""),
        "className": str(s["className"]),
        "section": s.get("section", "A"),
        "houseCode": s["houseCode"],
        "isActive": True,
        "isCandidate": s.get("isCandidate", False),
        "positionName": s.get("positionName", "")
    }
    if s.get("photoUrl"):
        d["photoUrl"] = s.get("photoUrl")
    return d

new_stu_objs = [make_stu_dict(s) for s in all_students]
all_stus_list = [demo_stu] + new_stu_objs
all_stus_json = json.dumps(all_stus_list, indent=4)

# 1. Update Houses/admin/data.js
print("Updating Houses/admin/data.js...")
with open('Houses/admin/data.js', 'r', encoding='utf-8') as f:
    admin_text = f.read()

start_idx = admin_text.find('"students":')
end_idx = admin_text.find('"candidates":')
if start_idx != -1 and end_idx != -1:
    new_admin_text = admin_text[:start_idx] + f'"students": {all_stus_json},\n  ' + admin_text[end_idx:]
    with open('Houses/admin/data.js', 'w', encoding='utf-8') as f:
        f.write(new_admin_text)
    print("  Admin data.js updated successfully!")

# 2. Update house data.js files
houses_map = {
    "bheeshma": "BHEESHMA",
    "gurudrona": "GURUDRONA",
    "hanuman": "HANUMAN",
    "karna": "KARNA",
    "vasistha": "VASISTHA",
    "vishwamithra": "VISHWAMITHRA"
}

for folder, hcode in houses_map.items():
    file_path = f'Houses/{folder}/data.js'
    print(f"Updating {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        h_text = f.read()
    
    h_start = h_text.find('"houseStudents":')
    h_end = h_text.find('"houseCandidates":')
    if h_start != -1 and h_end != -1:
        house_stus = [demo_stu] + [s for s in new_stu_objs if s["houseCode"] == hcode]
        house_stus_json = json.dumps(house_stus, indent=4)
        h_text = h_text[:h_start] + f'"houseStudents": {house_stus_json},\n  ' + h_text[h_end:]
        
    a_start = h_text.find('"allStudents":')
    a_end = h_text.find('"allCandidates":')
    if a_start != -1 and a_end != -1:
        h_text = h_text[:a_start] + f'"allStudents": {all_stus_json},\n  ' + h_text[a_end:]
        
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(h_text)
    print(f"  {file_path} updated!")

# 3. Resync Supabase
SUPABASE_URL = 'https://rziptxcknaeuorekxwrl.supabase.co'
SECRET_KEY = 'sb_secret_FtxzxZKea9lg5fhHm10sEA_WZcgFcs8'

print("\nClearing old student voters from Supabase...")
req = urllib.request.Request(
    f"{SUPABASE_URL}/rest/v1/voters?house_code=neq.ALL",
    method="DELETE",
    headers={
        'apikey': SECRET_KEY,
        'Authorization': f'Bearer {SECRET_KEY}',
        'Content-Type': 'application/json'
    }
)
with urllib.request.urlopen(req) as resp:
    print(f"  Delete status: {resp.status}")

print("Inserting clean student voters into Supabase...")
rows = []
for s in all_students:
    rows.append({
        "admission_no": s["admissionNo"],
        "full_name": s["fullName"],
        "class_name": str(s["className"]),
        "section": s["section"],
        "house_code": s["houseCode"],
        "house_name": s["houseName"],
        "final_status": "Not Voted",
        "voted_for": "",
        "vote_10_boy": "",
        "vote_10_girl": "",
        "vote_9_boy": "",
        "vote_9_girl": "",
        "position_name": "House Captains & Vice Captains",
        "is_active": True
    })

chunk_size = 100
total_ins = 0
for i in range(0, len(rows), chunk_size):
    chunk = rows[i:i + chunk_size]
    payload = json.dumps(chunk).encode('utf-8')
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/voters",
        data=payload,
        method="POST",
        headers={
            'apikey': SECRET_KEY,
            'Authorization': f'Bearer {SECRET_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }
    )
    with urllib.request.urlopen(req) as resp:
        if resp.status in (200, 201):
            total_ins += len(chunk)
            print(f"  Inserted {total_ins}/{len(rows)}")
    time.sleep(0.1)

print(f"\nCOMPLETED! All {total_ins} clean students inserted into Supabase.")
