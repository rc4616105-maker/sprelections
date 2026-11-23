"""
Complete Synchronization Script for Candidate Raw Data, AI Portraits & Demo Voter Profiles
Updates:
- Houses/<house>/data.js across all 6 houses
- Houses/teachers/data.js
- Houses/admin/data.js
- Result declaration/js/data.js
- DEMO_ACCOUNTS across all supabase-config.js files
- scripts/generate_voter_card_images.py and sample demo card
"""

import sys
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from parse_roster import (
    parse_xlsx,
    XLSX_PATH,
    HOUSES,
    CENTRAL_HOUSE,
    get_positions,
    get_central_positions,
    build_demo_candidates,
    build_admin_data_js,
)

DEMO_ACCOUNTS_JS = """  const DEMO_ACCOUNTS = {
    "1C8492": { admissionNo: "1C8492", fullName: "Aditya Vikram", fatherName: "R. K. Vikram", className: "10", section: "Chatrapathi Shivaji (10-CS)", houseCode: "BHEESHMA", isStaff: false, isUniversal: true, isActive: true, photoUrl: "../assets/candidates/student_demo.jpg", isDemoAccount: true },
    "0000": { admissionNo: "0000", fullName: "Aditya Vikram", fatherName: "R. K. Vikram", className: "10", section: "Chatrapathi Shivaji (10-CS)", houseCode: "BHEESHMA", isStaff: false, isUniversal: true, isActive: true, photoUrl: "../assets/candidates/student_demo.jpg", isDemoAccount: true },
    "0001": { admissionNo: "0001", fullName: "Arnav Saxena", fatherName: "S. Saxena", className: "10", section: "A", houseCode: "BHEESHMA", isStaff: false, isUniversal: false, isActive: true, photoUrl: "../assets/candidates/student_boy_1.jpg" },
    "0002": { admissionNo: "0002", fullName: "Rohan Kulkarni", fatherName: "V. Kulkarni", className: "10", section: "B", houseCode: "GURUDRONA", isStaff: false, isUniversal: false, isActive: true, photoUrl: "../assets/candidates/student_boy_3.jpg" },
    "0003": { admissionNo: "0003", fullName: "Siddharth Rao", fatherName: "M. Rao", className: "10", section: "C", houseCode: "HANUMAN", isStaff: false, isUniversal: false, isActive: true, photoUrl: "../assets/candidates/student_boy_4.jpg" },
    "0004": { admissionNo: "0004", fullName: "Karan Malhotra", fatherName: "P. Malhotra", className: "10", section: "D", houseCode: "KARNA", isStaff: false, isUniversal: false, isActive: true, photoUrl: "../assets/candidates/student_boy_1.jpg" },
    "0005": { admissionNo: "0005", fullName: "Pranav Nambiar", fatherName: "K. Nambiar", className: "10", section: "A", houseCode: "VASISTHA", isStaff: false, isUniversal: false, isActive: true, photoUrl: "../assets/candidates/student_boy_2.jpg" },
    "0006": { admissionNo: "0006", fullName: "Dhruv Sen", fatherName: "A. Sen", className: "10", section: "B", houseCode: "VISHWAMITHRA", isStaff: false, isUniversal: false, isActive: true, photoUrl: "../assets/candidates/student_boy_4.jpg" },
  };"""

NEW_GET_CANDIDATES_JS = '''    async getHouseCandidates(houseCode) {
      const localCands = window.HOUSE_DATA?.houseCandidates || [];
      const localMap = new Map(localCands.map((c) => [c.id, c]));

      if (this.mode === "supabase") {
        try {
          const rows = await sbRest(
            "GET",
            `/rest/v1/candidates?house_code=eq.${encodeURIComponent(houseCode)}&is_approved=eq.true&select=*`
          );
          if (Array.isArray(rows) && rows.length > 0) {
            return rows.map((c) => {
              const loc = localMap.get(c.id) || {};
              const isGeneric = !c.full_name || c.full_name.startsWith("Candidate ");
              return {
                id: c.id,
                admissionNo: c.admission_no || loc.admissionNo,
                fullName: isGeneric && loc.fullName ? loc.fullName : c.full_name,
                className: c.class_name || loc.className,
                section: c.section || loc.section,
                houseCode: c.house_code || loc.houseCode,
                positionId: c.position_id || loc.positionId || "CAPTAIN_BOY",
                positionName: c.position_name || loc.positionName || "Boys Captain",
                tagline: (!c.tagline || isGeneric) && loc.tagline ? loc.tagline : (c.tagline || ""),
                symbolObj: loc.symbolObj || (c.symbol_name ? { name: c.symbol_name, icon: c.symbol_icon, image: `../assets/symbols/${(c.symbol_name||'star').toLowerCase().replace(/[\s-]+/g, '_')}.png`, imagePath: `../assets/symbols/${(c.symbol_name||'star').toLowerCase().replace(/[\s-]+/g, '_')}.png` } : null),
                photoUrl: loc.photoUrl || c.photo_url || "",
                photoPath: loc.photoPath || c.photo_url || "",
                isApproved: c.is_approved !== false,
              };
            });
          }
        } catch (_) {}
      }
      return localCands;
    },'''

def update_get_candidates_function():
    for slug in ['bheeshma', 'gurudrona', 'hanuman', 'karna', 'vasistha', 'vishwamithra', 'central']:
        p = ROOT / 'Houses' / slug / 'supabase-config.js'
        if not p.exists():
            continue
        text = p.read_text(encoding='utf-8')
        pattern = r"    async getHouseCandidates\(houseCode\) \{[\s\S]*?^\s*\},"
        if re.search(pattern, text, flags=re.MULTILINE):
            new_text = re.sub(pattern, lambda m: NEW_GET_CANDIDATES_JS, text, flags=re.MULTILINE)
            p.write_text(new_text, encoding='utf-8')
            print(f" -> Updated getHouseCandidates in Houses/{slug}/supabase-config.js")
        else:
            print(f" * getHouseCandidates pattern not found in {slug}")


def build_house_data_js(house: dict, students, candidates):
    positions = get_positions()
    house_students = [s for s in students if s["houseCode"] == house["code"] or s["admissionNo"] in ("0000", "1C8492")]
    house_candidates = [c for c in candidates if c["houseCode"] == house["code"]]
    pos_id = "HOUSE_CAPTAIN"
    pos_name = "House Captain"
    houses_meta = {h["code"]: {"name": h["name"], "slug": h["slug"]} for h in HOUSES}
    houses_meta["CENTRAL"] = {"name": "School Cabinet", "slug": "central"}
    payload = {
        "electionId": "ELECTION_2026",
        "electionName": "School House Elections 2026",
        "positionId": pos_id,
        "positionName": pos_name,
        "positions": positions,
        "houseConfig": house,
        "housesMeta": houses_meta,
        "houseStudents": house_students,
        "houseCandidates": house_candidates,
        "allStudents": students,
        "allCandidates": candidates,
    }
    return f"// {house['name']} — Roster & House Metadata\nwindow.HOUSE_DATA = {json.dumps(payload, indent=2)};\n"

def sync_all():
    print("1. Parsing roster and candidate data...")
    students, blank_house, counts = parse_xlsx(XLSX_PATH)
    candidates = build_demo_candidates()
    print(f"Loaded {len(students)} students and {len(candidates)} candidates.")

    # 1. Update 6 House data.js files
    for h in HOUSES:
        slug = h["slug"]
        h_file = ROOT / "Houses" / slug / "data.js"
        content = build_house_data_js(h, students, candidates)
        h_file.write_text(content, encoding="utf-8")
        h_cands = [c for c in candidates if c["houseCode"] == h["code"]]
        print(f" -> Updated Houses/{slug}/data.js ({len(h_cands)} candidates)")

    # 2. Update Houses/admin/data.js
    admin_data_file = ROOT / "Houses" / "admin" / "data.js"
    admin_data_file.write_text(build_admin_data_js(students, candidates), encoding="utf-8")
    print(f" -> Updated Houses/admin/data.js")

    # 3. Update Houses/teachers/data.js
    teachers_data_file = ROOT / "Houses" / "teachers" / "data.js"
    if teachers_data_file.exists():
        raw_t = teachers_data_file.read_text(encoding="utf-8")
        clean_json_str = re.sub(r"^\s*//[^\n]*\n", "", raw_t)
        clean_json_str = re.sub(r"^\s*window\.TEACHER_BOOTH_DATA\s*=\s*", "", clean_json_str)
        clean_json_str = re.sub(r";\s*$", "", clean_json_str.strip())
        t_data = json.loads(clean_json_str)
        t_data["candidates"] = candidates
        
        # Ensure 0000 is present in teachers list
        if "teachers" in t_data:
            has_demo = any(t.get("admissionNo") == "0000" for t in t_data["teachers"])
            if not has_demo:
                t_data["teachers"].insert(0, {
                    "sl": 0,
                    "admissionNo": "0000",
                    "fullName": "Aditya Vikram",
                    "gender": "MALE",
                    "subject": "DEMO FACULTY",
                    "contact": "9999999999",
                    "houseCode": "ALL",
                    "houseName": "All Houses & Cabinet",
                    "className": "Staff",
                    "section": "Faculty",
                    "isStaff": True,
                    "isActive": True
                })
            else:
                for t in t_data["teachers"]:
                    if t.get("admissionNo") in ("0000", "6000"):
                        t["fullName"] = "Dr. Rajesh Sharma"
                        t["subject"] = "SENIOR FACULTY"
                        t["photoUrl"] = "../assets/candidates/teacher_demo.jpg"
                        
        teachers_data_file.write_text(
            f"// Teacher Universal Polling Booth — Full Metadata & Roster\nwindow.TEACHER_BOOTH_DATA = {json.dumps(t_data, indent=2)};\n",
            encoding="utf-8"
        )
        print(f" -> Updated Houses/teachers/data.js ({len(candidates)} candidates)")

    # 4. Update Result declaration/js/data.js
    res_data_file = ROOT / "Result declaration" / "js" / "data.js"
    if res_data_file.exists():
        raw_res = res_data_file.read_text(encoding="utf-8")
        
        # Map of house candidates
        winner_map = {
            "bheeshma": {
                "boys_captain": ("Arjun Verma", "Class 10-A", "assets/candidates/student_boy_1.jpg", "Unwavering resolve, decisive leadership."),
                "girls_captain": ("Ananya Iyer", "Class 10-B", "assets/candidates/student_girl_1.jpg", "Together we strive, together we thrive."),
                "boys_vc": ("Rohan Nair", "Class 9-A", "assets/candidates/student_boy_2.jpg", "Service with humility and courage."),
                "girls_vc": ("Sneha Reddy", "Class 9-C", "assets/candidates/student_girl_2.jpg", "Empowering every student voice."),
            },
            "gurudrona": {
                "boys_captain": ("Devrath Singh", "Class 10-B", "assets/candidates/student_boy_3.jpg", "Aim high, strike true."),
                "girls_captain": ("Kavya Menon", "Class 10-C", "assets/candidates/student_girl_3.jpg", "Excellence through relentless practice."),
                "boys_vc": ("Kunal Joshi", "Class 9-B", "assets/candidates/student_boy_2.jpg", "Steadfast guidance for every teammate."),
                "girls_vc": ("Meera Sen", "Class 9-A", "assets/candidates/student_girl_4.jpg", "Inspiring strength through knowledge."),
            },
            "hanuman": {
                "boys_captain": ("Tejas Chawla", "Class 10-B", "assets/candidates/student_boy_4.jpg", "No peak is too high to conquer."),
                "girls_captain": ("Ishita Pillai", "Class 10-C", "assets/candidates/student_girl_1.jpg", "Boundless energy, limitless devotion."),
                "boys_vc": ("Dhruv Kapoor", "Class 9-B", "assets/candidates/student_boy_2.jpg", "Courage is contagious."),
                "girls_vc": ("Avni Sharma", "Class 9-A", "assets/candidates/student_girl_2.jpg", "Strength begins with unity."),
            },
            "karna": {
                "boys_captain": ("Abhimanyu Das", "Class 10-A", "assets/candidates/student_boy_1.jpg", "Standing firm when the storm rages."),
                "girls_captain": ("Tarini Mukherjee", "Class 10-C", "assets/candidates/student_girl_3.jpg", "Honor over glory, duty over triumph."),
                "boys_vc": ("Siddharth Jain", "Class 9-A", "assets/candidates/student_boy_2.jpg", "Loyal to the team, faithful to the cause."),
                "girls_vc": ("Roshni Paul", "Class 9-B", "assets/candidates/student_girl_2.jpg", "Unyielding spirit, unwavering heart."),
            },
            "vasistha": {
                "boys_captain": ("Aditya Hegde", "Class 10-A", "assets/candidates/student_boy_3.jpg", "True power lies in quiet conviction."),
                "girls_captain": ("Pooja Kulkarni", "Class 10-A", "assets/candidates/student_girl_1.jpg", "Compassion and character above all."),
                "boys_vc": ("Varun Bhat", "Class 9-C", "assets/candidates/student_boy_2.jpg", "Leading by standing beside you."),
                "girls_vc": ("Tanvi Saxena", "Class 9-B", "assets/candidates/student_girl_4.jpg", "Harmonious hearts build great houses."),
            },
            "vishwamithra": {
                "boys_captain": ("Vikramaditya Roy", "Class 10-C", "assets/candidates/student_boy_4.jpg", "Creating new horizons where none exist."),
                "girls_captain": ("Rhea Deshmukh", "Class 10-B", "assets/candidates/student_girl_3.jpg", "Fearless pursuit of greatness."),
                "boys_vc": ("Samarth Rao", "Class 9-A", "assets/candidates/student_boy_2.jpg", "Resilience in every challenge."),
                "girls_vc": ("Pari Chopra", "Class 9-C", "assets/candidates/student_girl_2.jpg", "Breaking barriers with bold determination."),
            },
        }
        
        cabinet_map = {
            "PRESIDENT": ("Kabir Mehta", "Class 10-A", "assets/candidates/student_boy_1.jpg", "Visionary leadership, institutional excellence"),
            "VICE_PRESIDENT": ("Manav Saxena", "Class 9-A", "assets/candidates/student_boy_2.jpg", "Energetic leadership with unwavering dedication"),
            "LITERARY_SECRETARY": ("Siddharth Varma", "Class 9-B", "assets/candidates/student_boy_4.jpg", "Celebrating expression, eloquence, and literature"),
            "SPORTS_SECRETARY": ("Aayush Rawat", "Class 9-C", "assets/candidates/student_boy_3.jpg", "Sportsmanship, grit, and athletic glory"),
            "SOCIAL_CULTURAL_SECRETARY": ("Zoya Akhtar", "Class 9-A", "assets/candidates/student_girl_2.jpg", "Spectacular festivals, unforgettable traditions"),
        }
        
        lines = raw_res.split("\n")
        out_lines = []
        cur_h = None
        cur_role = None
        cur_cab = None
        
        for line in lines:
            hm = re.search(r'id:\s*"(bheeshma|gurudrona|hanuman|karna|vasistha|vishwamithra)"', line)
            if hm:
                cur_h = hm.group(1)
            cm = re.search(r'id:\s*"(PRESIDENT|VICE_PRESIDENT|LITERARY_SECRETARY|SPORTS_SECRETARY|SOCIAL_CULTURAL_SECRETARY)"', line)
            if cm:
                cur_cab = cm.group(1)
                
            rm = re.search(r'(boys_captain|girls_captain|boys_vc|girls_vc):\s*\{', line)
            if rm:
                cur_role = rm.group(1)
                
            if cur_h and cur_role and cur_h in winner_map and cur_role in winner_map[cur_h]:
                name, grade, photo, quote = winner_map[cur_h][cur_role]
                if 'photo:' in line:
                    line = f'        photo: "{photo}",'
                elif 'name:' in line and not 'postTitle:' in line:
                    line = f'        name: "{name}",'
                elif 'grade:' in line:
                    line = f'        grade: "{grade}",'
                elif 'quote:' in line:
                    line = f'        quote: "{quote}"'
            elif cur_cab and cur_cab in cabinet_map:
                name, grade, photo, quote = cabinet_map[cur_cab]
                if 'photo:' in line:
                    line = f'      photo: "{photo}",'
                elif 'name:' in line and not 'postTitle:' in line and not 'fullName:' in line:
                    line = f'      name: "{name}",'
                elif 'grade:' in line:
                    line = f'      grade: "{grade}",'
                elif 'quote:' in line:
                    line = f'      quote: "{quote}"'
                    
            out_lines.append(line)
            
        res_data_file.write_text("\n".join(out_lines), encoding="utf-8")
        print(" -> Updated Result declaration/js/data.js with candidate names and photos.")

    # 5. Update DEMO_ACCOUNTS across all supabase-config.js files
    sb_configs = [
        ROOT / "Houses" / "bheeshma" / "supabase-config.js",
        ROOT / "Houses" / "gurudrona" / "supabase-config.js",
        ROOT / "Houses" / "hanuman" / "supabase-config.js",
        ROOT / "Houses" / "karna" / "supabase-config.js",
        ROOT / "Houses" / "vasistha" / "supabase-config.js",
        ROOT / "Houses" / "vishwamithra" / "supabase-config.js",
        ROOT / "Houses" / "central" / "supabase-config.js",
        ROOT / "Houses" / "teachers" / "supabase-config.js",
        ROOT / "Houses" / "admin" / "supabase-config.js",
    ]
    pattern = r"  const DEMO_ACCOUNTS\s*=\s*\{[\s\S]*?^\s*\};"
    for sp in sb_configs:
        if not sp.exists():
            continue
        stext = sp.read_text(encoding="utf-8")
        if re.search(pattern, stext, flags=re.MULTILINE):
            new_stext = re.sub(pattern, DEMO_ACCOUNTS_JS, stext, flags=re.MULTILINE)
            sp.write_text(new_stext, encoding="utf-8")
            print(f" -> Updated DEMO_ACCOUNTS in {sp.relative_to(ROOT)}")
        else:
            print(f" * Pattern not found in {sp.name}")

    # 6. Update getHouseCandidates to merge and prioritize real candidates
    update_get_candidates_function()

    print("--- Synchronization Complete! ---")

if __name__ == "__main__":
    sync_all()
