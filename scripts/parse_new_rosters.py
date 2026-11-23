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

SECTION_HEADERS = {
    "sd", "satish dhawan", "ab", "aryabhatta", "vsb", "vikram sarabhai",
    "kc", "kalpana chawla", "kc section", "apj", "apj section",
    "apj abdul kalam", "cs", "chatrapathi shivaji", "mrp", "maha raana pratap",
    "jlb", "jhansi laxmi bai", "ac", "ashoka chakravarthi", "section", "sections"
}

IGNORED_NAMES = {
    "", "boys", "girls", "name", "names", "section", "sections", "total",
    "class", "satish dhawan", "aryabhatta", "vikram sarabhai", "kalpana chawla",
    "apj abdul kalam", "vsb", "ab", "sd", "kc", "apj", "kc section", "apj section",
    "`"
}

def clean_str(s):
    if s is None:
        return ""
    return re.sub(r"\s+", " ", str(s).strip())

def parse_class_sheet(house_code, sheet_name, rows):
    """
    Parses a single sheet into clean student records.
    Returns: list of dicts, list of warnings
    """
    students = []
    warnings = []

    # Detect class number from sheet name: e.g. "Class 6" -> "6"
    c_match = re.search(r"\d+", sheet_name)
    class_num = c_match.group(0) if c_match else sheet_name

    # Determine girl columns starting point
    # Usually Col 0 is Boy Name.
    # In some sheets, Col 1 is Boy Section, Col 4 is Girl Name, Col 5 is Girl Section.
    # In other sheets, Col 0 is Boy Name, Col 3 is Boy Section, Col 4 is Girl Name, Col 7 is Girl Section.
    
    # Let's inspect rows to find the exact structure
    # Look at row 1 or 2
    b_name_col = 0
    b_sec_col = None
    g_name_col = None
    g_sec_col = None

    for r_idx, r in rows[:4]:
        for c_idx, val in enumerate(r):
            v = clean_str(val).lower()
            if "girl" in v and g_name_col is None:
                g_name_col = c_idx
            if "section" in v:
                if g_name_col is None:
                    b_sec_col = c_idx
                else:
                    g_sec_col = c_idx

    # If g_name_col couldn't be determined from headers, check data columns
    if g_name_col is None:
        # Check where the second name column is
        g_name_col = 4
    if b_sec_col is None:
        # If g_name_col is 4, b_sec is usually 1 or 3
        # Check first data row
        b_sec_col = 1
    if g_sec_col is None:
        g_sec_col = g_name_col + 1

    # Now let's iterate rows from row 3 (or 2)
    current_b_sec = ""
    current_g_sec = ""

    for r_idx, r in rows:
        # Skip header rows
        row_joined = " ".join(clean_str(x).lower() for x in r)
        if "total" in row_joined and ("class" in row_joined or "boys" in row_joined):
            continue
        if r_idx in (1, 2) and ("boys" in row_joined or "name" in row_joined):
            continue

        # Extract boy cell and section
        boy_name = ""
        boy_sec = ""
        girl_name = ""
        girl_sec = ""

        # Let's inspect all cells to the left of g_name_col for boy
        left_cells = [(i, clean_str(r[i])) for i in range(min(g_name_col, len(r))) if clean_str(r[i])]
        # filter out ignored
        left_candidates = [(i, v) for i, v in left_cells if v.lower() not in IGNORED_NAMES]

        if left_candidates:
            # If a candidate is just a known section name or section header like "vsb", update current_b_sec
            if len(left_candidates) == 1 and left_candidates[0][1].lower() in SECTION_HEADERS:
                current_b_sec = left_candidates[0][1].upper()
            else:
                # Find name and section
                # If there's a cell with section code (<= 4 chars, or known section)
                name_cands = []
                sec_cands = []
                for i, v in left_candidates:
                    if len(v) <= 4 and (v.isupper() or v.isalnum()) and not "." in v and not " " in v:
                        sec_cands.append(v)
                    else:
                        name_cands.append(v)
                
                if name_cands:
                    boy_name = name_cands[0]
                    boy_sec = sec_cands[0] if sec_cands else current_b_sec
                elif sec_cands:
                    current_b_sec = sec_cands[0].upper()

        # Extract girl cell and section to the right of g_name_col
        right_cells = [(i, clean_str(r[i])) for i in range(g_name_col, len(r)) if clean_str(r[i])]
        right_candidates = [(i, v) for i, v in right_cells if v.lower() not in IGNORED_NAMES]

        if right_candidates:
            if len(right_candidates) == 1 and right_candidates[0][1].lower() in SECTION_HEADERS:
                current_g_sec = right_candidates[0][1].upper()
            else:
                name_cands = []
                sec_cands = []
                for i, v in right_candidates:
                    # Ignore full section name headers like 'Satish Dhawan', 'Aryabhatta', 'Vikram Sarabhai'
                    if v.lower() in {"satish dhawan", "aryabhatta", "vikram sarabhai", "kalpana chawla", "apj abdul kalam"}:
                        continue
                    if len(v) <= 4 and (v.isupper() or v.isalnum()) and not "." in v and not " " in v:
                        sec_cands.append(v)
                    else:
                        name_cands.append(v)
                
                if name_cands:
                    girl_name = name_cands[0]
                    girl_sec = sec_cands[0] if sec_cands else current_g_sec
                elif sec_cands:
                    current_g_sec = sec_cands[0].upper()

        if boy_name and boy_name.lower() not in IGNORED_NAMES:
            students.append({
                "fullName": boy_name,
                "gender": "Boy",
                "className": class_num,
                "section": boy_sec,
                "houseCode": house_code,
                "sourceRow": r_idx
            })
            if not boy_sec:
                warnings.append(f"Row {r_idx}: Boy '{boy_name}' has no section")

        if girl_name and girl_name.lower() not in IGNORED_NAMES:
            students.append({
                "fullName": girl_name,
                "gender": "Girl",
                "className": class_num,
                "section": girl_sec,
                "houseCode": house_code,
                "sourceRow": r_idx
            })
            if not girl_sec:
                warnings.append(f"Row {r_idx}: Girl '{girl_name}' has no section")

    return students, warnings

all_parsed = []
house_stats = {}

for house_code, fname in house_files.items():
    data = read_xlsx(FOLDER / fname)
    h_students = []
    h_warnings = []
    for sname in sorted(data.keys()):
        if sname.lower() == "total":
            continue
        stus, warns = parse_class_sheet(house_code, sname, data[sname])
        h_students.extend(stus)
        for w in warns:
            h_warnings.append(f"[{sname}] {w}")
            
    all_parsed.extend(h_students)
    house_stats[house_code] = {
        "file": fname,
        "total": len(h_students),
        "boys": sum(1 for s in h_students if s["gender"] == "Boy"),
        "girls": sum(1 for s in h_students if s["gender"] == "Girl"),
        "by_class": Counter(s["className"] for s in h_students),
        "by_class_gender": Counter((s["className"], s["gender"]) for s in h_students),
        "warnings": h_warnings,
        "sections": Counter(s["section"] for s in h_students)
    }

print("\n" + "=" * 80)
print("FINAL EXACT PARSED STATS PER HOUSE:")
print("=" * 80)

for hc in ["BHEESHMA", "GURUDRONA", "HANUMAN", "KARNA", "VASISTHA", "VISHWAMITHRA"]:
    st = house_stats[hc]
    print(f"\n🏠 {hc} ({st['file']}):")
    print(f"   Total Members: {st['total']} (Boys: {st['boys']}, Girls: {st['girls']})")
    for cl in ["6", "7", "8", "9", "10"]:
        c_tot = st["by_class"].get(cl, 0)
        c_b = st["by_class_gender"].get((cl, "Boy"), 0)
        c_g = st["by_class_gender"].get((cl, "Girl"), 0)
        print(f"     - Class {cl}: {c_tot:2d} students (Boys: {c_b:2d}, Girls: {c_g:2d})")
    print("   Sections:", dict(st["sections"]))
    if st["warnings"]:
        print(f"   Warnings ({len(st['warnings'])}):")
        for w in st["warnings"]:
            print(f"     * {w}")

print("\n" + "=" * 80)
print(f"TOTAL STUDENTS ACROSS ALL 6 HOUSES: {len(all_parsed)}")
print(f"Boys: {sum(1 for s in all_parsed if s['gender'] == 'Boy')} | Girls: {sum(1 for s in all_parsed if s['gender'] == 'Girl')}")
print("=" * 80)
