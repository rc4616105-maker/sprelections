import openpyxl

wb = openpyxl.load_workbook('1docs/OFFICIAL_STUDENT_VOTER_IDS_2026.xlsx', data_only=True)
sheet = wb.active

for r in range(2, sheet.max_row + 1):
    vid = str(sheet.cell(r, 2).value or '').strip()
    name = str(sheet.cell(r, 3).value or '').strip()
    cls = str(sheet.cell(r, 4).value or '').strip()
    sec = str(sheet.cell(r, 5).value or '').strip()
    gender = str(sheet.cell(r, 6).value or '').strip()
    house = str(sheet.cell(r, 7).value or '').strip()
    
    # check for names
    n_lower = name.lower()
    for q in ['rithvik', 'rithwik', 'ritvik', 'enrique', 'enriqe', 'trusha', 'thrusha', 'shubhi', 'harsha', 'indu', 'balla', 'raga', 'vivek', 'sampath', 'badrinath', 'krithika', 'koushik', 'janaki']:
        if q in n_lower:
            print(f"Matched '{q}': Row {r} | Voter ID: {vid} | Name: {name} | Class: {cls} | Sec: {sec} | House: {house}")
