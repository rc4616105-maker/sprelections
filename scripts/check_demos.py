import re

with open("Houses/admin/data.js", "r", encoding="utf-8") as f:
    txt = f.read()

print("--- CANDIDATES CHECK ---")
cand_part = txt.split('"candidates": [', 1)[1].split('],', 1)[0]
for m in re.finditer(r'\{[^{}]*?"fullName":\s*"([^"]+)"[^{}]*?\}', cand_part):
    cand_str = m.group(0)
    if any(w in cand_str.lower() for w in ["demo", "sample", "0000", "test"]):
        print("Candidate with demo/test:", cand_str)

print("--- STUDENTS CHECK ---")
stu_part = txt.split('"students": [', 1)[1].split(']\n};', 1)[0]
for m in re.finditer(r'\{[^{}]*?"fullName":\s*"([^"]+)"[^{}]*?\}', stu_part):
    stu_str = m.group(0)
    if any(w in stu_str.lower() for w in ["demo", "sample", "0000", "test", "staff", "facul"]):
        print("Student with keyword:", stu_str)
