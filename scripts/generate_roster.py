import zipfile
import xml.etree.ElementTree as ET
import re
import random
import json

random.seed(20261123)  # deterministic reproducible random seed

files_houses = [
    ('1docs/Bheesma (1).xlsx', 'BHEESHMA', 'Bheeshma'),
    ('1docs/Gurudrona (1).xlsx', 'GURUDRONA', 'Gurudrona'),
    ('1docs/Hanuman.xlsx', 'HANUMAN', 'Hanuman'),
    ('1docs/Karan.xlsx', 'KARNA', 'Karna'),
    ('1docs/Vasista.xlsx', 'VASISTHA', 'Vasistha'),
    ('1docs/Viswamitra (1).xlsx', 'VISHWAMITHRA', 'Vishwamithra')
]

# Section header cleaners
IGNORED_NAMES = {
    "", "boys", "girls", "name", "names", "section", "sections", "total",
    "class", "satish dhawan", "aryabhatta", "vikram sarabhai", "kalpana chawla",
    "apj abdul kalam", "vsb", "ab", "sd", "kc", "apj", "kc section", "apj section",
    "`", "chatrapathi shivaji", "maha raana pratap", "jhansi laxmi bai", "ashoka chakravarthi",
    "cs", "mrp", "jlb", "ac"
}

def clean_str(s):
    if s is None:
        return ""
    return re.sub(r"\s+", " ", str(s).strip())

def parse_all_houses():
    all_students = []
    
    for path, house_code, house_name in files_houses:
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
            
            for sheet_name in sheets:
                if 'total' in sheet_name.lower():
                    continue
                c_match = re.search(r'(\d+)', sheet_name)
                class_num = c_match.group(1) if c_match else sheet_name
                
                sheet_idx = sheets.index(sheet_name) + 1
                sheet_file = f'xl/worksheets/sheet{sheet_idx}.xml'
                if sheet_file not in z.namelist():
                    continue
                
                s_xml = z.read(sheet_file)
                s_tree = ET.fromstring(s_xml)
                
                row_data = {}
                for r in s_tree.findall('.//main:row', ns):
                    r_num = int(r.attrib['r'])
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
                    row_data[r_num] = cells
                
                # Determine girl column
                # Col A: Boy Name
                # Col B or C or D: Boy Sec
                # Col D or E or F: Girl Name
                # Col F or G or H: Girl Sec
                current_b_sec = ""
                current_g_sec = ""
                
                for r_num in sorted(row_data.keys()):
                    cells = row_data[r_num]
                    row_str = " ".join(cells.values()).lower()
                    if r_num <= 2 and any(w in row_str for w in ['boys', 'girls', 'names', 'name', 'section', 'sections']):
                        continue
                    if 'total' in row_str and ('class' in row_str or 'boys' in row_str):
                        continue
                    
                    # Col A is boy name
                    boy_name = (cells.get('A') or '').strip()
                    # boy section
                    b_sec = cells.get('B') or cells.get('C') or cells.get('D') or ''
                    b_sec = (b_sec or '').strip().upper()
                    if b_sec and len(b_sec) <= 4 and b_sec.isalnum() and not '.' in b_sec:
                        current_b_sec = b_sec
                    elif not b_sec:
                        b_sec = current_b_sec
                        
                    # Girl name
                    girl_name = cells.get('D') if ('E' not in cells and 'F' not in cells) else (cells.get('E') or cells.get('F') or '')
                    girl_name = (girl_name or '').strip()
                    g_sec = cells.get('F') or cells.get('G') or cells.get('H') or ''
                    g_sec = (g_sec or '').strip().upper()
                    if g_sec and len(g_sec) <= 4 and g_sec.isalnum() and not '.' in g_sec:
                        current_g_sec = g_sec
                    elif not g_sec:
                        g_sec = current_g_sec
                    
                    # Clean up
                    if boy_name and boy_name.lower() not in IGNORED_NAMES and len(boy_name) > 2:
                        all_students.append({
                            "fullName": boy_name,
                            "gender": "Boy",
                            "className": class_num,
                            "section": b_sec if b_sec else "A",
                            "houseCode": house_code,
                            "houseName": house_name
                        })
                    if girl_name and girl_name.lower() not in IGNORED_NAMES and len(girl_name) > 2:
                        all_students.append({
                            "fullName": girl_name,
                            "gender": "Girl",
                            "className": class_num,
                            "section": g_sec if g_sec else "A",
                            "houseCode": house_code,
                            "houseName": house_name
                        })
    return all_students

students = parse_all_houses()
print(f"Total students parsed: {len(students)}")

# Candidate matching: load candidates from Houses/admin/data.js
with open('Houses/admin/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'"candidates":\s*(\[\s*\{[\s\S]*?\}\s*\])\s*,\s*"', text)
candidates = []
if m:
    candidates = json.loads(m.group(1))
    print(f"Total existing candidates loaded: {len(candidates)}")

def norm_name(n):
    return re.sub(r'[^a-zA-Z]', '', n).lower()

cand_map = {}
for c in candidates:
    key = (norm_name(c.get('fullName', '')), c.get('houseCode', ''))
    cand_map[key] = c

# Generate unique IDs: [ClassDigit][SectionLetter][4RandomDigits]
# Class 10 -> '1'
# Class 6 -> '6', Class 7 -> '7', Class 8 -> '8', Class 9 -> '9'
used_ids = set()
# Preserve demo id 1C8492
used_ids.add("1C8492")

for s in students:
    cl = s['className']
    class_digit = "1" if cl == "10" else str(cl)
    
    sec = s['section']
    # Pick first alphabetical character from section, fallback to 'S'
    sec_letter = "S"
    for ch in sec:
        if ch.isalpha():
            sec_letter = ch.upper()
            break
            
    # Generate unique 4 random digits
    while True:
        r_digits = f"{random.randint(1000, 9999)}"
        cand_id = f"{class_digit}{sec_letter}{r_digits}"
        if cand_id not in used_ids:
            used_ids.add(cand_id)
            s['admissionNo'] = cand_id
            break
            
    # Check candidate matching
    n_key = (norm_name(s['fullName']), s['houseCode'])
    if n_key in cand_map:
        c_obj = cand_map[n_key]
        s['isCandidate'] = True
        s['positionName'] = c_obj.get('positionName', '')
        s['positionId'] = c_obj.get('positionId', '')
        if c_obj.get('photoUrl'):
            s['photoUrl'] = c_obj.get('photoUrl')
    else:
        s['isCandidate'] = False

print(f"Generated {len(students)} student IDs.")
sample = students[:5] + students[500:505] + students[-5:]
for s in sample:
    print(f"{s['admissionNo']}: {s['fullName']} | Class {s['className']}-{s['section']} | House: {s['houseCode']} | Cand: {s['isCandidate']}")

# Save parsed students to JSON for import
with open('new_students_roster.json', 'w', encoding='utf-8') as f:
    json.dump(students, f, indent=2)

print("Saved new_students_roster.json successfully!")
