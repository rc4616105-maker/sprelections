"""
Script to remove all '(Demo Voter)' / '(Demo)' text for Aditya Vikram (1C8492 & 0000),
ensure student status (isStaff: false, Eligible Voter badge, Class 10 metadata),
and record 1C8492 as a tracked demo account for future removal.
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent

# 1. Update scripts/parse_roster.py
parse_roster_path = ROOT / "scripts" / "parse_roster.py"
pr_text = parse_roster_path.read_text(encoding="utf-8")
pr_text = pr_text.replace('"fullName": "Aditya Vikram (Demo Voter)"', '"fullName": "Aditya Vikram"')
pr_text = pr_text.replace('"fatherName": "R. K. Vikram (Demo)"', '"fatherName": "R. K. Vikram"')
parse_roster_path.write_text(pr_text, encoding="utf-8")
print("1. Updated scripts/parse_roster.py")

# 2. Update scripts/update_candidates_and_demo.py
up_path = ROOT / "scripts" / "update_candidates_and_demo.py"
up_text = up_path.read_text(encoding="utf-8")
up_text = re.sub(r'fullName":\s*"Aditya Vikram \([^"]+\)"', 'fullName": "Aditya Vikram"', up_text)
up_text = re.sub(r'fatherName":\s*"R\. K\. Vikram \([^"]+\)"', 'fatherName": "R. K. Vikram"', up_text)
# Ensure isStaff: false for 1C8492 and 0000 in DEMO_ACCOUNTS_JS
up_text = up_text.replace(
    '"1C8492": { admissionNo: "1C8492", fullName: "Aditya Vikram", fatherName: "R. K. Vikram", className: "10", section: "Chatrapathi Shivaji (10-CS)", houseCode: "ALL", isStaff: true,',
    '"1C8492": { admissionNo: "1C8492", fullName: "Aditya Vikram", fatherName: "R. K. Vikram", className: "10", section: "Chatrapathi Shivaji (10-CS)", houseCode: "BHEESHMA", isStaff: false, isDemoAccount: true,'
)
up_text = up_text.replace(
    '"0000": { admissionNo: "0000", fullName: "Aditya Vikram", fatherName: "R. K. Vikram", className: "10", section: "Chatrapathi Shivaji (10-CS)", houseCode: "ALL", isStaff: true,',
    '"0000": { admissionNo: "0000", fullName: "Aditya Vikram", fatherName: "R. K. Vikram", className: "10", section: "Chatrapathi Shivaji (10-CS)", houseCode: "BHEESHMA", isStaff: false, isDemoAccount: true,'
)
up_path.write_text(up_text, encoding="utf-8")
print("2. Updated scripts/update_candidates_and_demo.py")

# 3. Update all Houses/*/app.js files: isTeacher logic and Step 2 text
for slug in ['bheeshma', 'gurudrona', 'hanuman', 'karna', 'vasistha', 'vishwamithra', 'central']:
    app_path = ROOT / "Houses" / slug / "app.js"
    if not app_path.exists():
        continue
    a_text = app_path.read_text(encoding="utf-8")
    
    # Replace isTeacher logic
    old_teacher_check = 'const isTeacher = result.student.isStaff === true || result.student.houseCode === "ALL" || result.student.admissionNo === "0000";'
    new_teacher_check = 'const isTeacher = result.student.isStaff === true && result.student.className !== "10" && result.student.className !== "9" && result.student.className !== "8" && result.student.className !== "7" && result.student.admissionNo !== "1C8492" && result.student.admissionNo !== "0000";'
    if old_teacher_check in a_text:
        a_text = a_text.replace(old_teacher_check, new_teacher_check)
        print(f" -> Updated isTeacher logic in Houses/{slug}/app.js")
        
    app_path.write_text(a_text, encoding="utf-8")

# 4. Update all Houses/*/supabase-config.js files: DEMO_ACCOUNTS clean name and isStaff: false
for slug in ['bheeshma', 'gurudrona', 'hanuman', 'karna', 'vasistha', 'vishwamithra', 'central']:
    sb_path = ROOT / "Houses" / slug / "supabase-config.js"
    if not sb_path.exists():
        continue
    sb_text = sb_path.read_text(encoding="utf-8")
    
    sb_text = re.sub(
        r'"1C8492":\s*\{[^}]*\}',
        '"1C8492": { admissionNo: "1C8492", fullName: "Aditya Vikram", fatherName: "R. K. Vikram", className: "10", section: "Chatrapathi Shivaji (10-CS)", houseCode: "BHEESHMA", isStaff: false, isUniversal: true, isActive: true, photoUrl: "../assets/candidates/student_demo.jpg", isDemoAccount: true }',
        sb_text
    )
    sb_text = re.sub(
        r'"0000":\s*\{[^}]*\}',
        '"0000": { admissionNo: "0000", fullName: "Aditya Vikram", fatherName: "R. K. Vikram", className: "10", section: "Chatrapathi Shivaji (10-CS)", houseCode: "BHEESHMA", isStaff: false, isUniversal: true, isActive: true, photoUrl: "../assets/candidates/student_demo.jpg", isDemoAccount: true }',
        sb_text
    )
    sb_path.write_text(sb_text, encoding="utf-8")
    print(f" -> Updated DEMO_ACCOUNTS in Houses/{slug}/supabase-config.js")

# 5. Update scripts/generate_voter_card_images.py
gv_path = ROOT / "scripts" / "generate_voter_card_images.py"
gv_text = gv_path.read_text(encoding="utf-8")

# Update render_voter_card so 1C8492 is NOT treated as generic demo text
gv_text = gv_text.replace(
    'is_demo = str(person.get("admissionNo")) == "0000" or (house_code == "ALL" and not is_staff)',
    'is_demo = False  # Render full authentic student identity on all cards'
)
gv_text = gv_text.replace('"fullName": "Aditya Vikram (Demo)"', '"fullName": "Aditya Vikram"')
gv_text = gv_text.replace('"houseCode": "ALL"', '"houseCode": "BHEESHMA"')
gv_path.write_text(gv_text, encoding="utf-8")
print("5. Updated scripts/generate_voter_card_images.py")

# 6. Bump cachebusters to ?v=1060
html_files = [
    ROOT / "Houses" / "bheeshma" / "index.html",
    ROOT / "Houses" / "gurudrona" / "index.html",
    ROOT / "Houses" / "hanuman" / "index.html",
    ROOT / "Houses" / "karna" / "index.html",
    ROOT / "Houses" / "vasistha" / "index.html",
    ROOT / "Houses" / "vishwamithra" / "index.html",
    ROOT / "Houses" / "central" / "index.html",
    ROOT / "Houses" / "teachers" / "index.html",
]
for hp in html_files:
    if not hp.exists():
        continue
    c = hp.read_text(encoding="utf-8")
    c = re.sub(r'(\.js|\.css)\?v=\d+', r'\1?v=1060', c)
    hp.write_text(c, encoding="utf-8")
    print(f" -> Bumped cachebuster to ?v=1060 in {hp.relative_to(ROOT)}")

print("\n--- All demo text removed and student status restored! ---")
