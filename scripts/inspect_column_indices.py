# -*- coding: utf-8 -*-
import os, sys
from pathlib import Path

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

for house_code, fname in house_files.items():
    fpath = FOLDER / fname
    print("=" * 60)
    print(f"FILE: {fname} ({house_code})")
    data = read_xlsx(fpath)
    for sname, rows in data.items():
        if sname.lower() == "total":
            print(f"  --- {sname} summary table ---")
            for r in rows:
                print("   ", r[1])
            continue
        print(f"\n  --- Sheet: [{sname}] (rows: {len(rows)}) ---")
        # Print first 5 rows with indices
        for r_idx, r in rows[:5]:
            print(f"    r{r_idx}: {list(enumerate(r))}")
