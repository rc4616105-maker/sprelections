import openpyxl

wb = openpyxl.load_workbook('1docs/OFFICIAL_STUDENT_VOTER_IDS_2026.xlsx', data_only=True)
sheet = wb.active

for r in range(2, sheet.max_row + 1):
    vid = str(sheet.cell(r, 2).value or '').strip()
    name = str(sheet.cell(r, 3).value or '').strip()
    cls = str(sheet.cell(r, 4).value or '').strip()
    sec = str(sheet.cell(r, 5).value or '').strip()
    house = str(sheet.cell(r, 7).value or '').strip()
    
    if 'class 10' in cls.lower():
        if name.startswith('M.') or 'rithvik' in name.lower() or 'rithwik' in name.lower() or 'ritvik' in name.lower():
            print(f"Class 10 candidate: {vid} | {name} | {house} | {sec}")
