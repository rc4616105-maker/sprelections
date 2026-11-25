import openpyxl

wb = openpyxl.load_workbook('1docs/OFFICIAL_STUDENT_VOTER_IDS_2026.xlsx', data_only=True)
sheet = wb.active
print("Sheet title:", sheet.title)

for r in range(1, 20):
    vals = [sheet.cell(r, c).value for c in range(1, 10)]
    if any(vals):
        print(f"Row {r}: {vals[:6]}")

# search for Rithvik
found = []
for r in range(1, sheet.max_row + 1):
    for c in range(1, 8):
        v = str(sheet.cell(r, c).value or '')
        if 'rithvik' in v.lower() or 'janaki' in v.lower() or 'koushik' in v.lower() or 'enriqe' in v.lower() or 'trusha' in v.lower():
            row_vals = [sheet.cell(r, col).value for col in range(1, 8)]
            found.append(row_vals)

print(f"Found {len(found)} rows:")
for f in found[:10]:
    print("  ", f)
