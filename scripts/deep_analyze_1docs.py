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

HEADER_WORDS = {
    "boys", "girls", "name", "names", "section", "sections", "sec",
    "total", "class", "sl no", "s.no", "sno", "b", "g"
}

def clean_val(v):
    if v is None:
        return ""
    return str(v).strip()

def is_header_val(v):
    return clean_val(v).lower() in HEADER_WORDS

def parse_sheet_students(sheet_name, rows):
    """
    Parses a class sheet into list of dicts:
    [{'name': str, 'gender': 'Boy'|'Girl', 'section_raw': str, 'class': str, 'row': int}]
    """
    students = []
    issues = []
    
    # Identify column layout by looking at first 3 rows
    # Generally: Boys on the left, Girls on the right
    # Let's inspect rows to find where boys names/sections and girls names/sections are
    
    # We can detect columns dynamically:
    # Look for 'Boys' and 'Girls' in header rows
    boys_name_col = None
    boys_sec_col = None
    girls_name_col = None
    girls_sec_col = None
    
    start_row_idx = 0
    for idx, (r_num, r_vals) in enumerate(rows[:5]):
        row_lower = [clean_val(c).lower() for c in r_vals]
        if "boys" in row_lower or "girls" in row_lower:
            start_row_idx = max(start_row_idx, idx + 1)
        if "name" in row_lower or "names" in row_lower or "section" in row_lower or "sections" in row_lower:
            start_row_idx = max(start_row_idx, idx + 1)

    # Let's see what columns have data in rows starting from start_row_idx
    data_rows = rows[start_row_idx:]
    if not data_rows:
        return students, issues

    # To determine column structure accurately:
    # In almost all sheets:
    # Left side (Boys): Name is at Col 0. Section is at Col 1 or Col 3.
    # Right side (Girls): Name is around Col 3, 4 or 5. Section is after name.
    
    # Let's inspect which column contains the girls names
    # In rows[0] or rows[1], let's see where 'Girls' was placed
    girls_start_col = None
    for idx, (r_num, r_vals) in enumerate(rows[:3]):
        for c_idx, val in enumerate(r_vals):
            if "girl" in clean_val(val).lower():
                girls_start_col = c_idx
                break
        if girls_start_col is not None:
            break
            
    if girls_start_col is None:
        # Default heuristic based on sheet width
        girls_start_col = 4

    for r_num, r_vals in data_rows:
        # Check if this row is a total/summary row
        row_text = " ".join(clean_val(c).lower() for c in r_vals)
        if "total" in row_text or "class" in row_text:
            continue

        # Split into left (boys) and right (girls)
        left_part = r_vals[:girls_start_col] if girls_start_col < len(r_vals) else r_vals
        right_part = r_vals[girls_start_col:] if girls_start_col < len(r_vals) else []

        # Find boy name & section in left_part
        # non-empty cells
        left_non_empty = [(i, clean_val(val)) for i, val in enumerate(left_part) if clean_val(val)]
        # filter out header words
        left_non_empty = [(i, val) for i, val in left_non_empty if not is_header_val(val)]
        
        if len(left_non_empty) == 1:
            # Just a name or just a section?
            c_idx, val = left_non_empty[0]
            if len(val) <= 4 and val.isupper() and not "." in val:
                issues.append(f"Row {r_num}: Boy has section '{val}' but missing name")
            else:
                students.append({
                    "name": val,
                    "gender": "Boy",
                    "section_raw": "",
                    "row": r_num,
                    "class": sheet_name
                })
                issues.append(f"Row {r_num}: Boy '{val}' has empty section")
        elif len(left_non_empty) >= 2:
            # First is typically name, second is section
            # Check which is name and which is section
            val1 = left_non_empty[0][1]
            val2 = left_non_empty[1][1]
            # If val1 looks like section and val2 is name:
            if len(val1) <= 3 and len(val2) > 3 and not "." in val1:
                b_sec, b_name = val1, val2
            else:
                b_name, b_sec = val1, val2
            students.append({
                "name": b_name,
                "gender": "Boy",
                "section_raw": b_sec,
                "row": r_num,
                "class": sheet_name
            })

        # Find girl name & section in right_part
        right_non_empty = [(i + girls_start_col, clean_val(val)) for i, val in enumerate(right_part) if clean_val(val)]
        right_non_empty = [(i, val) for i, val in right_non_empty if not is_header_val(val)]
        
        if len(right_non_empty) == 1:
            c_idx, val = right_non_empty[0]
            if len(val) <= 4 and val.isupper() and not "." in val:
                issues.append(f"Row {r_num}: Girl has section '{val}' but missing name")
            else:
                students.append({
                    "name": val,
                    "gender": "Girl",
                    "section_raw": "",
                    "row": r_num,
                    "class": sheet_name
                })
                issues.append(f"Row {r_num}: Girl '{val}' has empty section")
        elif len(right_non_empty) >= 2:
            val1 = right_non_empty[0][1]
            val2 = right_non_empty[1][1]
            if len(val1) <= 3 and len(val2) > 3 and not "." in val1:
                g_sec, g_name = val1, val2
            else:
                g_name, g_sec = val1, val2
            students.append({
                "name": g_name,
                "gender": "Girl",
                "section_raw": g_sec,
                "row": r_num,
                "class": sheet_name
            })

    return students, issues

all_house_data = {}
all_sections_by_class = defaultdict(Counter)

for house_code, fname in house_files.items():
    fpath = FOLDER / fname
    wb_data = read_xlsx(fpath)
    house_students = []
    house_issues = []
    total_sheet_summary = None

    for sname, rows in wb_data.items():
        if sname.lower() == "total":
            total_sheet_summary = rows
            continue
        stus, iss = parse_sheet_students(sname, rows)
        house_students.extend(stus)
        for is_item in iss:
            house_issues.append(f"[{sname}] {is_item}")
        for s in stus:
            all_sections_by_class[s["class"]][s["section_raw"]] += 1

    all_house_data[house_code] = {
        "file": fname,
        "students": house_students,
        "issues": house_issues,
        "total_sheet": total_sheet_summary
    }

print("\n" + "=" * 80)
print("HOUSE-BY-HOUSE STUDENT COUNTS")
print("=" * 80)

grand_boys = 0
grand_girls = 0
grand_total = 0

for house_code in ["BHEESHMA", "GURUDRONA", "HANUMAN", "KARNA", "VASISTHA", "VISHWAMITHRA"]:
    info = all_house_data[house_code]
    stus = info["students"]
    boys = [s for s in stus if s["gender"] == "Boy"]
    girls = [s for s in stus if s["gender"] == "Girl"]
    
    grand_boys += len(boys)
    grand_girls += len(girls)
    grand_total += len(stus)
    
    print(f"\n🏠 {house_code} ({info['file']}):")
    print(f"   Total Students: {len(stus)} (Boys: {len(boys)}, Girls: {len(girls)})")
    
    # Class breakdown
    class_counter = Counter(s["class"] for s in stus)
    for cname in sorted(class_counter.keys()):
        c_boys = sum(1 for s in stus if s["class"] == cname and s["gender"] == "Boy")
        c_girls = sum(1 for s in stus if s["class"] == cname and s["gender"] == "Girl")
        print(f"     - {cname}: {class_counter[cname]} (Boys: {c_boys}, Girls: {c_girls})")
        
    if info["total_sheet"]:
        print("   Excel 'Total' sheet summary:")
        for r_num, r_vals in info["total_sheet"]:
            row_str = " | ".join(clean_val(c) for c in r_vals if clean_val(c))
            if row_str:
                print(f"       {row_str}")

    if info["issues"]:
        print(f"   ⚠️ Potential data issues detected ({len(info['issues'])}):")
        for iss in info["issues"][:8]:
            print(f"       * {iss}")
        if len(info["issues"]) > 8:
            print(f"       ... and {len(info['issues']) - 8} more issues")

print("\n" + "=" * 80)
print(f"GRAND TOTAL STUDENTS ACROSS ALL 6 HOUSES: {grand_total}")
print(f"Boys: {grand_boys} | Girls: {grand_girls}")
print("=" * 80)

print("\nSECTIONS FOUND PER CLASS:")
for cname, sec_counts in sorted(all_sections_by_class.items()):
    print(f"\nClass: {cname}")
    for sec, count in sorted(sec_counts.items(), key=lambda x: -x[1]):
        print(f"  {repr(sec)}: {count} students")
