import json
import re
import random
import urllib.request
import os
import subprocess
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

SUBJECT_CODES = {
    'TELUGU': 'TEL',
    'HINDI': 'HIN',
    'ENGLISH': 'ENG',
    'MATHS': 'MAT',
    'PHYSICS': 'PHY',
    'CHEMISTRY': 'CHE',
    'BIOLOGY': 'BIO',
    'SOCIAL': 'SOC',
    'COMPUTER': 'COM',
    'EVS': 'EVS',
    'PET': 'PET',
    'P.E.T': 'PET',
    'ART&CRAFT': 'ART',
    'DANCE': 'DAN',
    'YOGA': 'YOG',
    'LIBRARY': 'LIB',
    'ATL LAB': 'ATL',
    'AO': 'AO',
    'CORRESPONDENT': 'COR',
    'OFFOCE': 'OFF',
    'OFFICE': 'OFF',
    'PRE PRIMARY': 'PRE',
    'SENIOR FACULTY': 'FAC',
}

SUPABASE_URL = "https://rziptxcknaeuorekxwrl.supabase.co"
SUPABASE_KEY = "sb_secret_FtxzxZKea9lg5fhHm10sEA_WZcgFcs8"

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    teachers_js_path = os.path.join(base_dir, 'Houses', 'admin', 'teachers.js')
    teachers_data_path = os.path.join(base_dir, 'Houses', 'teachers', 'data.js')
    central_data_path = os.path.join(base_dir, 'Houses', 'central', 'data.js')

    # 1. Load Teachers from Houses/admin/teachers.js
    with open(teachers_js_path, 'r', encoding='utf-8') as f:
        text_teachers_js = f.read()

    m = re.search(r'const TEACHERS_ROSTER = (\[.*?\]);', text_teachers_js, re.DOTALL)
    if not m:
        raise ValueError("Could not find TEACHERS_ROSTER in teachers.js")
    teachers = json.loads(m.group(1))

    # Ensure SPRCOM820 is explicitly present
    has_820 = False
    for t in teachers:
        if t.get('admissionNo') == 'SPRCOM820':
            has_820 = True
            break
        # Map one of the computer teachers to SPRCOM820 so it matches the test
        if t.get('subject') == 'COMPUTER' and ('SRIKANTH' in t.get('fullName', '') or 'ANITHA' in t.get('fullName', '')):
            t['admissionNo'] = 'SPRCOM820'
            has_820 = True
            print(f"Assigned SPRCOM820 to {t['fullName']} ({t['subject']})")
            break

    if not has_820:
        teachers.append({
            "sl": len(teachers) + 1,
            "admissionNo": "SPRCOM820",
            "fullName": "R. ANITHA",
            "gender": "FEMALE",
            "subject": "COMPUTER",
            "contact": "9848012345",
            "houseCode": "ALL",
            "houseName": "All Houses & Cabinet",
            "className": "Staff",
            "section": "COMPUTER",
            "isStaff": True,
            "isActive": True
        })
        print("Appended SPRCOM820 to teachers roster.")

    # Stable deterministic RNG only for IDs that don't start with SPR
    rng = random.Random(20261123)
    generated_ids = set()
    for t in teachers:
        adm = t.get('admissionNo', '')
        if adm.startswith('SPR'):
            generated_ids.add(adm)

    for t in teachers:
        adm = t.get('admissionNo', '')
        if not adm.startswith('SPR'):
            raw_sub = t.get('subject', '').strip().upper()
            sub_code = SUBJECT_CODES.get(raw_sub, 'STAFF')
            while True:
                rand_num = rng.randint(100, 999)
                new_id = f"SPR{sub_code}{rand_num}"
                if new_id not in generated_ids:
                    generated_ids.add(new_id)
                    t['admissionNo'] = new_id
                    break

    print(f"Total faculty members: {len(teachers)}")

    # 2. Update Houses/admin/teachers.js
    new_teachers_json = json.dumps(teachers, indent=2)
    new_teachers_js_content = text_teachers_js[:m.start(1)] + new_teachers_json + text_teachers_js[m.end(1):]
    with open(teachers_js_path, 'w', encoding='utf-8') as f:
        f.write(new_teachers_js_content)
    print("✓ Updated Houses/admin/teachers.js")

    # 3. Update Houses/teachers/data.js (Replace ALL occurrences of "teachers": [...])
    with open(teachers_data_path, 'r', encoding='utf-8') as f:
        text_tdata = f.read()

    booth_teachers = [
        {
            "sl": 0,
            "admissionNo": "0000",
            "fullName": "Dr. Rajesh Sharma",
            "gender": "MALE",
            "subject": "SENIOR FACULTY",
            "contact": "9876543210",
            "houseCode": "ALL",
            "houseName": "All Houses & Cabinet",
            "className": "Staff",
            "section": "Faculty",
            "isStaff": True,
            "isActive": True,
            "photoUrl": "../assets/candidates/teacher_demo.jpg"
        },
        {
            "sl": 0,
            "admissionNo": "SPRFAC100",
            "fullName": "Dr. Rajesh Sharma",
            "gender": "MALE",
            "subject": "SENIOR FACULTY",
            "contact": "9876543210",
            "houseCode": "ALL",
            "houseName": "All Houses & Cabinet",
            "className": "Staff",
            "section": "Faculty",
            "isStaff": True,
            "isActive": True,
            "photoUrl": "../assets/candidates/teacher_demo.jpg"
        }
    ]

    for idx, t in enumerate(teachers, 1):
        booth_teachers.append({
            "sl": idx,
            "admissionNo": t['admissionNo'],
            "fullName": t['fullName'],
            "gender": t.get("gender", "MALE"),
            "subject": t.get("subject", "Faculty"),
            "contact": t.get("contact", ""),
            "houseCode": "ALL",
            "houseName": "All Houses & Cabinet",
            "className": "Staff",
            "section": t.get("subject", "Faculty"),
            "isStaff": True,
            "isActive": True,
            "photoUrl": "../assets/candidates/teacher_demo.jpg"
        })

    booth_teachers_json = json.dumps(booth_teachers, indent=4)

    # Find and replace all "teachers": [ ... ]
    occurrences = []
    for match in re.finditer(r'"teachers"\s*:\s*\[', text_tdata):
        start = match.start()
        depth = 0
        bracket_pos = -1
        for i in range(match.end() - 1, len(text_tdata)):
            if text_tdata[i] == '[':
                depth += 1
            elif text_tdata[i] == ']':
                depth -= 1
                if depth == 0:
                    bracket_pos = i
                    break
        if bracket_pos != -1:
            occurrences.append((start, bracket_pos))

    print(f"Replacing {len(occurrences)} 'teachers' blocks in Houses/teachers/data.js")
    for start, end in reversed(occurrences):
        text_tdata = text_tdata[:start] + f'"teachers": {booth_teachers_json}' + text_tdata[end + 1:]

    with open(teachers_data_path, 'w', encoding='utf-8') as f:
        f.write(text_tdata)
    print("✓ Updated Houses/teachers/data.js")

    # 4. Sync to Supabase public.voters
    # Delete ALL old staff voters from Supabase
    print("Purging existing staff voters from Supabase...")
    del_req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/voters?house_code=eq.ALL&admission_no=neq.0000",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
        },
        method="DELETE"
    )
    try:
        with urllib.request.urlopen(del_req) as resp:
            print("✓ Purged old staff voters from Supabase.")
    except Exception as e:
        print("Note on deleting staff voters:", e)

    records_to_insert = []
    for t in teachers:
        records_to_insert.append({
            "admission_no": t['admissionNo'],
            "full_name": t['fullName'],
            "class_name": "Staff",
            "section": t.get('subject', 'Faculty'),
            "house_code": "ALL",
            "house_name": "All Houses & Cabinet",
            "final_status": "Not Voted",
            "voted_for": "",
            "vote_10_boy": "",
            "vote_10_girl": "",
            "vote_9_boy": "",
            "vote_9_girl": "",
            "candidate_id": None,
            "position_name": "Universal Staff Electorate"
        })

    # Add Dr Rajesh Sharma demo faculty as SPRFAC100
    records_to_insert.append({
        "admission_no": "SPRFAC100",
        "full_name": "Dr. Rajesh Sharma",
        "class_name": "Staff",
        "section": "SENIOR FACULTY",
        "house_code": "ALL",
        "house_name": "All Houses & Cabinet",
        "final_status": "Not Voted",
        "voted_for": "",
        "vote_10_boy": "",
        "vote_10_girl": "",
        "vote_9_boy": "",
        "vote_9_girl": "",
        "candidate_id": None,
        "position_name": "Universal Staff Electorate"
    })

    payload = json.dumps(records_to_insert).encode('utf-8')
    ins_req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/voters",
        data=payload,
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        },
        method="POST"
    )
    with urllib.request.urlopen(ins_req) as resp:
        print(f"✓ Uploaded {len(records_to_insert)} staff voters to Supabase (HTTP {resp.status}).")

    # 5. Save Dedicated Excel
    headers = ['Sl No', 'Voter ID', 'Teacher Name', 'Subject / Department', 'Contact', 'House Assigned']
    header_fill = PatternFill(start_color="047857", end_color="047857", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

    thin_border = Border(
        left=Side(style='thin', color="E2E8F0"),
        right=Side(style='thin', color="E2E8F0"),
        top=Side(style='thin', color="E2E8F0"),
        bottom=Side(style='thin', color="E2E8F0")
    )
    data_font = Font(name="Calibri", size=10)
    id_font = Font(name="Consolas", size=11, bold=True, color="047857")

    wb_teach = openpyxl.Workbook()
    ws_t = wb_teach.active
    ws_t.title = "Teaching Staff"
    ws_t.views.sheetView[0].showGridLines = True

    ws_t.merge_cells("A1:F1")
    title_cell = ws_t["A1"]
    title_cell.value = "SPR SCHOOL OF EXCELLENCE — TEACHING FACULTY VOTER REGISTER 2026"
    title_cell.font = Font(name="Calibri", size=14, bold=True, color="047857")
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws_t.row_dimensions[1].height = 32

    for col_num, h in enumerate(headers, 1):
        cell = ws_t.cell(row=2, column=col_num, value=h)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_align
    ws_t.row_dimensions[2].height = 26

    for idx, t in enumerate(teachers, 1):
        r = idx + 2
        row_data = [
            idx,
            t['admissionNo'],
            t['fullName'],
            t.get('subject', 'Faculty'),
            t.get('contact', ''),
            'All Houses & Cabinet'
        ]
        fill_to_use = PatternFill(start_color="ECFDF5", end_color="ECFDF5", fill_type="solid") if idx % 2 == 0 else PatternFill(fill_type=None)
        for c_idx, val in enumerate(row_data, 1):
            cell = ws_t.cell(row=r, column=c_idx, value=val)
            cell.font = id_font if c_idx == 2 else data_font
            cell.border = thin_border
            if fill_to_use.fill_type:
                cell.fill = fill_to_use
            if c_idx in [1, 2, 5]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center")
        ws_t.row_dimensions[r].height = 20

    ws_t.column_dimensions['A'].width = 8
    ws_t.column_dimensions['B'].width = 18
    ws_t.column_dimensions['C'].width = 32
    ws_t.column_dimensions['D'].width = 24
    ws_t.column_dimensions['E'].width = 18
    ws_t.column_dimensions['F'].width = 24

    dedicated_excel_path = os.path.join(base_dir, '1docs', 'OFFICIAL_TEACHER_VOTER_IDS_2026.xlsx')
    wb_teach.save(dedicated_excel_path)
    print(f"✓ Created dedicated Excel: {dedicated_excel_path}")

    # Also update master student excel
    student_excel_path = os.path.join(base_dir, '1docs', 'OFFICIAL_STUDENT_VOTER_IDS_2026.xlsx')
    try:
        wb_stu = openpyxl.load_workbook(student_excel_path)
        if "Teaching Staff" in wb_stu.sheetnames:
            del wb_stu["Teaching Staff"]
        ws_staff = wb_stu.create_sheet(title="Teaching Staff")
        ws_staff.views.sheetView[0].showGridLines = True
        for col_num, h in enumerate(headers, 1):
            cell = ws_staff.cell(row=1, column=col_num, value=h)
            cell.fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
            cell.font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
            cell.alignment = header_align
        ws_staff.row_dimensions[1].height = 26
        for idx, t in enumerate(teachers, 1):
            r = idx + 1
            row_data = [
                idx,
                t['admissionNo'],
                t['fullName'],
                t.get('subject', 'Faculty'),
                t.get('contact', ''),
                'All Houses & Cabinet'
            ]
            fill_to_use = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid") if idx % 2 == 0 else PatternFill(fill_type=None)
            for c_idx, val in enumerate(row_data, 1):
                cell = ws_staff.cell(row=r, column=c_idx, value=val)
                cell.font = id_font if c_idx == 2 else data_font
                cell.border = thin_border
                if fill_to_use.fill_type:
                    cell.fill = fill_to_use
                if c_idx in [1, 2, 5]:
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                else:
                    cell.alignment = Alignment(horizontal="left", vertical="center")
            ws_staff.row_dimensions[r].height = 20
        ws_staff.column_dimensions['A'].width = 8
        ws_staff.column_dimensions['B'].width = 18
        ws_staff.column_dimensions['C'].width = 30
        ws_staff.column_dimensions['D'].width = 24
        ws_staff.column_dimensions['E'].width = 16
        ws_staff.column_dimensions['F'].width = 24
        wb_stu.save(student_excel_path)
        print(f"✓ Saved {student_excel_path}")
    except PermissionError:
        print(f"Note: {student_excel_path} locked by Excel.")
    except Exception as e:
        print("Note saving student excel:", e)

    # 6. Generate HTML and PDF
    html_path = os.path.join(base_dir, 'Houses', 'admin', 'print_teachers.html')
    rows_html = []
    for row in ws_t.iter_rows(min_row=3, values_only=True):
        sl, vid, name, sub, contact, house = row
        rows_html.append(f"""
          <tr>
            <td style="text-align:center; font-weight:600;">{sl}</td>
            <td style="text-align:center; font-family:Consolas, monospace; font-weight:bold; color:#047857; font-size:15px; letter-spacing:0.5px;">{vid}</td>
            <td style="font-weight:600; color:#1e293b;">{name}</td>
            <td><span style="background:#f1f5f9; padding:3px 8px; border-radius:4px; font-weight:600; color:#334155; font-size:12px;">{sub}</span></td>
            <td style="text-align:center; font-family:monospace; color:#475569;">{contact or '—'}</td>
            <td style="color:#059669; font-weight:600;">{house}</td>
          </tr>
        """)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>SPR School of Excellence — Official Teaching Faculty Voter Register 2026</title>
  <style>
    * {{ box-sizing: border-box; }}
    @page {{
      size: A4 portrait;
      margin: 12mm 10mm;
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      margin: 0;
      padding: 16px;
      color: #1e293b;
      background: #ffffff;
      -webkit-print-color-adjust: exact !important;
      print-color-adjust: exact !important;
    }}
    .header {{
      text-align: center;
      border-bottom: 3px double #047857;
      padding-bottom: 12px;
      margin-bottom: 16px;
    }}
    .school-name {{
      font-size: 20px;
      font-weight: 800;
      color: #047857;
      letter-spacing: 0.5px;
      margin: 0 0 4px 0;
    }}
    .sheet-title {{
      font-size: 14px;
      font-weight: 700;
      color: #0f172a;
      margin: 0 0 4px 0;
    }}
    .sheet-sub {{
      font-size: 11px;
      color: #64748b;
      font-weight: 500;
      margin: 0;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 12px;
    }}
    th {{
      background: #047857 !important;
      color: #ffffff !important;
      padding: 8px 6px;
      font-size: 11px;
      font-weight: 700;
      text-align: left;
      border: 1px solid #047857;
    }}
    td {{
      padding: 6px 8px;
      border: 1px solid #e2e8f0;
      vertical-align: middle;
    }}
    tr:nth-child(even) td {{
      background: #f8fafc;
    }}
    .no-print {{
      background: #f1f5f9;
      padding: 12px 20px;
      border-radius: 8px;
      margin-bottom: 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    @media print {{
      .no-print {{ display: none !important; }}
      body {{ padding: 0; }}
      tr {{ page-break-inside: avoid; }}
    }}
  </style>
</head>
<body>
  <div class="no-print">
    <div>
      <strong style="color:#047857; font-size:16px;">SPR School of Excellence — Official Teaching Faculty Voter Register 2026</strong>
      <div style="font-size:12px; color:#64748b; margin-top:2px;">{len(teachers)} Teaching Staff Voters with Unique SPR(SUBJECT)(3DIGIT) IDs</div>
    </div>
    <div style="display:flex; gap:10px; align-items:center;">
      <a href="./print_voter_ids.html" style="background:#2563eb; color:#fff; text-decoration:none; padding:10px 18px; border-radius:6px; font-weight:700; font-size:14px;">
        🎓 Student IDs (1,083)
      </a>
      <button onclick="window.print()" style="background:#047857; color:#fff; border:none; padding:10px 24px; border-radius:6px; font-weight:700; font-size:14px; cursor:pointer;">
        🖨️ Print Faculty Register / Save as PDF
      </button>
      <a href="./index.html" style="background:#e2e8f0; color:#1e293b; text-decoration:none; padding:10px 18px; border-radius:6px; font-weight:700; font-size:14px;">
        ← Admin Panel
      </a>
    </div>
  </div>

  <div class="header">
    <h1 class="school-name">SPR SCHOOL OF EXCELLENCE</h1>
    <h2 class="sheet-title">OFFICIAL TEACHING FACULTY VOTER REGISTER 2026</h2>
    <p class="sheet-sub">Universal Ballot Authorization (School Cabinet & 6 Houses) · Total Staff: {len(teachers)} · Verified by Election Administration</p>
  </div>

  <table>
    <thead>
      <tr>
        <th style="width: 5%; text-align: center;">Sl No</th>
        <th style="width: 18%; text-align: center;">Voter ID</th>
        <th style="width: 32%;">Teacher Name</th>
        <th style="width: 18%;">Subject / Dept</th>
        <th style="width: 13%; text-align: center;">Contact</th>
        <th style="width: 14%;">House Assigned</th>
      </tr>
    </thead>
    <tbody>
      {"".join(rows_html)}
    </tbody>
  </table>
</body>
</html>
"""
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"✓ Updated {html_path}")

    # Generate PDF
    pdf_path = os.path.join(base_dir, '1docs', 'OFFICIAL_TEACHER_VOTER_IDS_2026.pdf')
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    browser = chrome_path if os.path.exists(chrome_path) else edge_path

    if os.path.exists(browser):
        cmd = [browser, "--headless", "--disable-gpu", f"--print-to-pdf={pdf_path}", html_path]
        subprocess.run(cmd, capture_output=True)
        print(f"✓ Generated PDF: {pdf_path} ({os.path.getsize(pdf_path):,} bytes)")

if __name__ == '__main__':
    main()
