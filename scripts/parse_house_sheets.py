# -*- coding: utf-8 -*-
import os, sys, re
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from inspect_new_1docs import read_xlsx, FOLDER

house_files = {
    "BHEESHMA": "Bheesma.xlsx",
    "GURUDRONA": "Gurudrona.xlsx",
    "HANUMAN": "Hanuman.xlsx",
    "KARNA": "Karan.xlsx",
    "VASISTHA": "Vasista.xlsx",
    "VISHWAMITHRA": "Viswamitra.xlsx",
}

# Standardized section mapping
# Short code -> Full Section Name
SECTION_MAP = {
    # Class 10
    "CS": "Chatrapathi Shivaji (10-CS)",
    "MRP": "Maha Raana Pratap (10-MP)",
    "JLB": "Jhansi Laxmi Bai (10-JL)",
    "AC": "Ashoka Chakravarthi (10-AC)",

    # Class 9
    "SD": "Satish Dhawan (9-SD)",
    "AB": "Aryabhatta (9-AB)",
    "VSB": "Vikram Sarabhai (9-VS)",
    "VS": "Vikram Sarabhai (9-VS)",
    "KC": "Kalpana Chawla (9-KC)",
    "APJ": "APJ Abdul Kalam (9-AK)",
    "AK": "APJ Abdul Kalam (9-AK)",

    # Class 8
    "SG": "Sri Guruji (8-SG)",
    "DS": "Dayananda Saraswathi (8-DS)",
    "CK": "Chanakya (8-CH)",
    "CH": "Chanakya (8-CH)",
    "HG": "Hedgewar (8-HW)",
    "HW": "Hedgewar (8-HW)",
    "SV": "Swamy Vivekananda (8-SV)",

    # Class 7
    "SCB": "Subhash Chandra Bose (7-SB)",
    "ASR": "Alluri Sitaramaraju (7-AS)",
    "CSA": "Chandra Shekar Azad (7-CA)",
    "BS": "Bhagath Singh (7-BS)",
    "RG": "Rajguru (7-RG)",
    "RJ": "Rajguru (7-RG)",

    # Class 6
    "LLR": "Lala Lajpat Rai (6-LLR)",
    "BGT": "Bhagat Singh (6-BGT)",
    "BCP": "Bipin Chandra Pal (6-BCP)",
    "DR BR AMBEDKAR": "Dr BR Ambedkar (6-AMB)",
    "AMB": "Dr BR Ambedkar (6-AMB)",
}

def clean_str(s):
    if s is None:
        return ""
    return re.sub(r"\s+", " ", str(s).strip())

FULL_SECTION_NAMES_CLEAN = {
    "satishdhawan", "aryabhatta", "vikramsarabhai", "kalpanachawla",
    "apjabdulkalam", "chatrapathishivaji", "maharaanapratap",
    "jhansilaxmibai", "ashokachakravarthi", "subhashchandrabose",
    "allurisitaramaraju", "chandrashekarazad", "bhagathsingh", "rajguru",
    "sriguruji", "dayanandasaraswathi", "chanakya", "hedgewar",
    "swamyvivekananda", "lalalajpatrai", "bipinchandrapal", "drbrambedkar"
}

def is_full_section_name(v, class_num=None):
    cleaned = re.sub(r"[^a-z]", "", clean_str(v).lower())
    if class_num == "6" and cleaned == "drbrambedkar":
        return False
    return cleaned in FULL_SECTION_NAMES_CLEAN

def is_banner_header(v):
    cleaned = re.sub(r"[^a-z0-9]", "", clean_str(v).lower())
    return is_full_section_name(v) or "section" in cleaned or cleaned.upper() in SECTION_MAP

def normalize_sec(raw_sec, class_num):
    s = clean_str(raw_sec).upper()
    c_clean = re.sub(r"[^a-z]", "", clean_str(raw_sec).lower())
    if c_clean == "drbrambedkar" or s == "DR BR AMBEDKAR":
        return "AMB"
    if s == "VS" and class_num == "9":
        return "VSB"
    if s == "RJ" and class_num == "7":
        return "RG"
    if s == "CH" and class_num == "8":
        return "CK"
    if s == "HW" and class_num == "8":
        return "HG"
    if s == "AK" and class_num == "9":
        return "APJ"
    return s

def parse_class_sheet(house_code, sheet_name, rows):
    c_match = re.search(r"\d+", sheet_name)
    class_num = c_match.group(0) if c_match else sheet_name
    
    students = []
    warnings = []

    # Find where girls columns start
    g_col_start = None
    for r_idx, r in rows[:4]:
        for c_idx, val in enumerate(r):
            if "girl" in clean_str(val).lower():
                g_col_start = c_idx
                break
        if g_col_start is not None:
            break
    if g_col_start is None:
        g_col_start = 4

    current_b_sec = ""
    current_g_sec = ""

    for r_idx, r in rows:
        row_str = " ".join(clean_str(c).lower() for c in r)
        # Skip top headers
        if r_idx in (1, 2) and ("boys" in row_str or "names" in row_str or "section" in row_str):
            continue
        if "total" in row_str and ("class" in row_str or "boys" in row_str):
            continue

        # Split left (boys) and right (girls)
        left_cells = [(i, clean_str(r[i])) for i in range(min(g_col_start, len(r))) if clean_str(r[i])]
        right_cells = [(i, clean_str(r[i])) for i in range(g_col_start, len(r)) if clean_str(r[i])]

        # Process Boy
        # Check if row is a single banner across (e.g. ['AB'] or ['vsb'] or ['kc section'])
        if len(left_cells) == 1 and not right_cells:
            val = left_cells[0][1]
            if len(val) <= 12 and (val.upper() in SECTION_MAP or is_banner_header(val)):
                sec_code = val.replace("section", "").strip().upper()
                if sec_code:
                    current_b_sec = sec_code
                    current_g_sec = sec_code
                continue

        # Left cells: find boy name and section
        boy_name = ""
        boy_sec = ""
        for i, val in left_cells:
            if is_full_section_name(val, class_num):
                continue
            # Check if this cell is a section code
            val_clean = val.replace("section", "").strip().upper()
            if val_clean in SECTION_MAP or (len(val) <= 4 and val.isupper() and not "." in val):
                boy_sec = val_clean
            elif len(val) > 1 and val != "`":
                boy_name = val

        if boy_sec:
            current_b_sec = boy_sec
        elif current_b_sec and boy_name:
            boy_sec = current_b_sec

        if boy_name:
            norm_s = normalize_sec(boy_sec, class_num)
            students.append({
                "fullName": boy_name,
                "gender": "Boy",
                "className": class_num,
                "section": norm_s,
                "houseCode": house_code,
                "row": r_idx
            })
            if not norm_s:
                warnings.append(f"Row {r_idx}: Boy '{boy_name}' missing section")

        # Right cells: find girl name and section
        girl_name = ""
        girl_sec = ""
        for i, val in right_cells:
            if is_full_section_name(val, class_num):
                continue
            val_clean = val.replace("section", "").strip().upper()
            if val_clean in SECTION_MAP or (len(val) <= 4 and val.isupper() and not "." in val):
                girl_sec = val_clean
            elif len(val) > 1 and val != "`":
                girl_name = val

        if girl_sec:
            current_g_sec = girl_sec
        elif current_g_sec and girl_name:
            girl_sec = current_g_sec

        if girl_name:
            norm_s = normalize_sec(girl_sec, class_num)
            students.append({
                "fullName": girl_name,
                "gender": "Girl",
                "className": class_num,
                "section": norm_s,
                "houseCode": house_code,
                "row": r_idx
            })
            if not norm_s:
                warnings.append(f"Row {r_idx}: Girl '{girl_name}' missing section")

    return students, warnings

# Run on all files
all_students = []
house_results = {}

for house_code, fname in house_files.items():
    data = read_xlsx(FOLDER / fname)
    stus = []
    warns = []
    total_table = None

    for sname in sorted(data.keys()):
        if sname.lower() == "total":
            total_table = data[sname]
            continue
        s_stus, s_warns = parse_class_sheet(house_code, sname, data[sname])
        stus.extend(s_stus)
        for w in s_warns:
            warns.append(f"[{sname}] {w}")

    all_students.extend(stus)
    house_results[house_code] = {
        "file": fname,
        "students": stus,
        "total": len(stus),
        "boys": sum(1 for s in stus if s["gender"] == "Boy"),
        "girls": sum(1 for s in stus if s["gender"] == "Girl"),
        "by_class": Counter(s["className"] for s in stus),
        "by_class_gender": Counter((s["className"], s["gender"]) for s in stus),
        "sections": Counter(s["section"] for s in stus),
        "warnings": warns,
        "total_table": total_table
    }

print("\n" + "=" * 80)
print("ACCURATE NEW STUDENT ENROLLMENT REPORT PER HOUSE")
print("=" * 80)

for hc in ["BHEESHMA", "GURUDRONA", "HANUMAN", "KARNA", "VASISTHA", "VISHWAMITHRA"]:
    r = house_results[hc]
    print(f"\n🏠 {hc} ({r['file']}):")
    print(f"   ► TOTAL MEMBERS: {r['total']} Students (👦 Boys: {r['boys']}, 👧 Girls: {r['girls']})")
    for cl in ["6", "7", "8", "9", "10"]:
        tot = r["by_class"].get(cl, 0)
        b = r["by_class_gender"].get((cl, "Boy"), 0)
        g = r["by_class_gender"].get((cl, "Girl"), 0)
        print(f"       Class {cl:2s}: {tot:2d} students  (Boys: {b:2d}, Girls: {g:2d})")
    
    # Check discrepancy with Total sheet in Excel if present
    if r["total_table"]:
        print("   Excel 'Total' Sheet comparison:")
        for _, row in r["total_table"]:
            clean_row = [clean_str(c) for c in row if clean_str(c)]
            if clean_row:
                print("      ", " | ".join(clean_row))

    if r["warnings"]:
        print(f"   ⚠️ Warnings ({len(r['warnings'])}):")
        for w in r["warnings"]:
            print(f"       * {w}")

print("\n" + "=" * 80)
print(f"GRAND TOTAL ENROLLED STUDENTS ACROSS ALL 6 HOUSES: {len(all_students)}")
print(f"Total Boys: {sum(1 for s in all_students if s['gender'] == 'Boy')} | Total Girls: {sum(1 for s in all_students if s['gender'] == 'Girl')}")
print("=" * 80)
