# -*- coding: utf-8 -*-
import os
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import Counter, defaultdict

FOLDER = Path("1docs")
ns = {
    "s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

def col_idx(ref: str) -> int:
    letters = "".join(ch for ch in ref if ch.isalpha())
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch.upper()) - 64)
    return n - 1

def read_xlsx(path: Path):
    sheets_data = {}
    with zipfile.ZipFile(path) as z:
        wb = ET.fromstring(z.read("xl/workbook.xml"))
        sheets = [
            (
                el.attrib["name"],
                el.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"],
            )
            for el in wb.findall(".//s:sheet", ns)
        ]
        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        rel_map = {r.attrib["Id"]: r.attrib["Target"] for r in rels}
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            ss = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in ss.findall("s:si", ns):
                shared.append("".join(t.text or "" for t in si.findall(".//s:t", ns)))

        for sheet_name, rid in sheets:
            target = "xl/" + rel_map[rid].lstrip("/")
            if target.startswith("xl/xl/"):
                target = target[3:]
            root = ET.fromstring(z.read(target))
            rows_list = []
            for row in root.findall(".//s:sheetData/s:row", ns):
                row_idx = int(row.attrib.get("r", len(rows_list) + 1))
                row_dict = {}
                for c in row.findall("s:c", ns):
                    ref = c.attrib.get("r", "")
                    c_idx = col_idx(ref) if ref else len(row_dict)
                    t = c.attrib.get("t")
                    v = c.find("s:v", ns)
                    val = v.text if v is not None else None
                    if t == "s" and val is not None:
                        val = shared[int(val)] if int(val) < len(shared) else val
                    elif t == "inlineStr":
                        t_el = c.find(".//s:t", ns)
                        val = t_el.text if t_el is not None else ""
                    if val is not None:
                        row_dict[c_idx] = str(val).strip()
                if row_dict:
                    max_c = max(row_dict.keys())
                    dense = [row_dict.get(i, "") for i in range(max_c + 1)]
                    rows_list.append((row_idx, dense))
            sheets_data[sheet_name] = rows_list
    return sheets_data

print("Scanning folder:", FOLDER.resolve())
for fname in sorted(os.listdir(FOLDER)):
    if not fname.endswith(".xlsx") or fname.startswith("~$"):
        continue
    fpath = FOLDER / fname
    print("\n" + "=" * 60)
    print(f"FILE: {fname}")
    try:
        data = read_xlsx(fpath)
        for sname, rows in data.items():
            print(f"  --- Sheet: [{sname}] (Total non-empty rows: {len(rows)}) ---")
            for r_idx, r_vals in rows[:8]:
                print(f"    Row {r_idx}: {r_vals[:12]}")
    except Exception as e:
        print(f"  Error reading {fname}: {e}")
