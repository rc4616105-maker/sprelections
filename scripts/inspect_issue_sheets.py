# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from inspect_new_1docs import read_xlsx, FOLDER

def inspect_sheet_rows(fname, sname):
    print(f"\n==================== {fname} -> [{sname}] ====================")
    data = read_xlsx(FOLDER / fname)
    rows = data.get(sname, [])
    for r_idx, r in rows:
        print(f"Row {r_idx:2d}: {r}")

inspect_sheet_rows("Gurudrona.xlsx", "Class 9")
inspect_sheet_rows("Karan.xlsx", "Class 9")
inspect_sheet_rows("Vasista.xlsx", "Class 9")
inspect_sheet_rows("Hanuman.xlsx", "Class 8")
