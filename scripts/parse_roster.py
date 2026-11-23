from pathlib import Path
from collections import Counter
import json
import re
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parent.parent
XLSX_PATH = ROOT / "ELECTIONS HOUSES (1).xlsx"
if not XLSX_PATH.exists() and (ROOT / "1docs" / "ELECTIONS HOUSES (1).xlsx").exists():
    XLSX_PATH = ROOT / "1docs" / "ELECTIONS HOUSES (1).xlsx"

HOUSES = [
    {
        "slug": "bheeshma",
        "code": "BHEESHMA",
        "name": "Bheeshma",
        "accent": "#eab308",
        "accentHover": "#facc15",
        "accentText": "#925c04",
        "onAccent": "#141413",
        "accentRgb": "234, 179, 8",
        "motto": "Wisdom, Duty & Resolve",
    },
    {
        "slug": "gurudrona",
        "code": "GURUDRONA",
        "name": "Gurudrona",
        "accent": "#2563eb",
        "accentHover": "#1d4ed8",
        "accentText": "#1d4ed8",
        "onAccent": "#fffdf9",
        "accentRgb": "37, 99, 235",
        "motto": "Knowledge, Focus & Discipline",
    },
    {
        "slug": "hanuman",
        "code": "HANUMAN",
        "name": "Hanuman",
        "accent": "#f97316",
        "accentHover": "#fb923c",
        "accentText": "#ea580c",
        "onAccent": "#141413",
        "accentRgb": "249, 115, 22",
        "motto": "Strength, Courage & Service",
    },
    {
        "slug": "karna",
        "code": "KARNA",
        "name": "Karna",
        "accent": "#b91c1c",
        "accentHover": "#991b1b",
        "accentText": "#991b1b",
        "onAccent": "#fffdf9",
        "accentRgb": "185, 28, 28",
        "motto": "Generosity, Grit & Honor",
    },
    {
        "slug": "vasistha",
        "code": "VASISTHA",
        "name": "Vasistha",
        "accent": "#db2777",
        "accentHover": "#be185d",
        "accentText": "#be185d",
        "onAccent": "#fffdf9",
        "accentRgb": "219, 39, 119",
        "motto": "Harmony, Clarity & Grace",
    },
    {
        "slug": "vishwamithra",
        "code": "VISHWAMITHRA",
        "name": "Vishwamithra",
        "accent": "#7c3aed",
        "accentHover": "#6d28d9",
        "accentText": "#6d28d9",
        "onAccent": "#fffdf9",
        "accentRgb": "124, 58, 237",
        "motto": "Vision, Determination & Growth",
    },
]

HOUSE_ALIAS = {
    "BHEESHMA": "BHEESHMA",
    "BISHMA": "BHEESHMA",
    "BHISHMA": "BHEESHMA",
    "GURUDRONA": "GURUDRONA",
    "HANUMAN": "HANUMAN",
    "KARAN": "KARNA",
    "KARNA": "KARNA",
    "VASHISHTA": "VASISTHA",
    "VASISHTA": "VASISTHA",
    "VISHWAMITRA": "VISHWAMITHRA",
    "VISHWAMITHRA": "VISHWAMITHRA",
}


def col_idx(ref: str) -> int:
    letters = "".join(ch for ch in ref if ch.isalpha())
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch.upper()) - 64)
    return n - 1


def parse_xlsx(path: Path):
    ns = {
        "s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
        "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    }
    students = []
    blank_house = []
    seen_ids = set()
    house_counts = Counter()

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

        for name, rid in sheets:
            # CLASS9 only extracts blank-house rows already present in Sheet 9
            if name.upper() == "CLASS9":
                continue
            target = "xl/" + rel_map[rid].lstrip("/")
            if target.startswith("xl/xl/"):
                target = target[3:]
            root = ET.fromstring(z.read(target))
            for row in root.findall(".//s:sheetData/s:row", ns):
                vals = {}
                for c in row.findall("s:c", ns):
                    idx = col_idx(c.attrib["r"])
                    t = c.attrib.get("t")
                    v = c.find("s:v", ns)
                    isel = c.find("s:is", ns)
                    txt = ""
                    if t == "s" and v is not None:
                        txt = shared[int(v.text)]
                    elif t == "inlineStr" and isel is not None:
                        txt = "".join(x.text or "" for x in isel.findall(".//s:t", ns))
                    elif v is not None:
                        txt = v.text or ""
                    vals[idx] = re.sub(r"\s+", " ", txt).strip()

                if not vals or not vals.get(0, "").isdigit():
                    continue

                sno = int(vals[0])
                full_name = vals.get(1, "").strip()
                gender = vals.get(2, "").strip()
                father_name = vals.get(3, "").strip()
                cls = vals.get(5, "").strip() or name.strip()
                sec = vals.get(6, "").strip() or "—"
                raw_house = vals.get(7, "").strip().upper()
                adm_no = str(int(cls) * 1000 + sno)

                if not raw_house:
                    blank_house.append(
                        {
                            "sheet": name,
                            "sno": sno,
                            "tempId": adm_no,
                            "fullName": full_name,
                            "gender": gender,
                            "fatherName": father_name,
                            "className": cls,
                            "section": sec,
                        }
                    )
                    continue

                house_code = HOUSE_ALIAS.get(raw_house)
                if not house_code:
                    raise ValueError(f"Unknown house name '{raw_house}' for {full_name}")
                if adm_no in seen_ids:
                    raise ValueError(f"Duplicate generated ID '{adm_no}'")
                seen_ids.add(adm_no)
                house_counts[house_code] += 1
                students.append(
                    {
                        "admissionNo": adm_no,
                        "fullName": full_name,
                        "gender": gender,
                        "fatherName": father_name,
                        "className": cls,
                        "section": sec,
                        "houseCode": house_code,
                        "isActive": True,
                        "isCandidate": False,
                        "positionName": None,
                    }
                )

    # Universal demo users for testing across all booths
    demo_profiles = [
        {
            "admissionNo": "1C8492",
            "fullName": "Aditya Vikram",
            "gender": "Boy",
            "fatherName": "R. K. Vikram",
            "className": "10",
            "section": "Chatrapathi Shivaji (10-CS)",
            "houseCode": "ALL",
            "isActive": True,
            "isCandidate": False,
            "positionName": None,
            "photoUrl": "../assets/candidates/student_demo.jpg",
        },
        {
            "admissionNo": "0000",
            "fullName": "Aditya Vikram",
            "gender": "Boy",
            "fatherName": "R. K. Vikram",
            "className": "10",
            "section": "Chatrapathi Shivaji (10-CS)",
            "houseCode": "ALL",
            "isActive": True,
            "isCandidate": False,
            "positionName": None,
            "photoUrl": "../assets/candidates/student_demo.jpg",
        },
    ]
    for dp in demo_profiles:
        if dp["admissionNo"] not in seen_ids:
            seen_ids.add(dp["admissionNo"])
            students.insert(0 if dp["admissionNo"] == "1C8492" else 1, dp)

    return students, blank_house, house_counts


def get_positions():
    return [
        {
            "id": "CAPTAIN_BOY",
            "code": "Vote_10_Boy",
            "title": "Boys Captain",
            "shortTitle": "Boys Captain",
            "subtitle": "Class 10 Boy",
            "className": "10",
            "gender": "Boy",
        },
        {
            "id": "CAPTAIN_GIRL",
            "code": "Vote_10_Girl",
            "title": "Girls Captain",
            "shortTitle": "Girls Captain",
            "subtitle": "Class 10 Girl",
            "className": "10",
            "gender": "Girl",
        },
        {
            "id": "VICE_CAPTAIN_BOY",
            "code": "Vote_9_Boy",
            "title": "Boys Vice Captain",
            "shortTitle": "Boys Vice Captain",
            "subtitle": "Class 9 Boy",
            "className": "9",
            "gender": "Boy",
        },
        {
            "id": "VICE_CAPTAIN_GIRL",
            "code": "Vote_9_Girl",
            "title": "Girls Vice Captain",
            "shortTitle": "Girls Vice Captain",
            "subtitle": "Class 9 Girl",
            "className": "9",
            "gender": "Girl",
        },
    ]


def get_central_positions():
    return [
        {
            "id": "PRESIDENT",
            "code": "Vote_President",
            "title": "School President",
            "shortTitle": "President",
            "subtitle": "Class 10 · Central Cabinet",
            "className": "10",
            "gender": "Any",
        },
        {
            "id": "VICE_PRESIDENT",
            "code": "Vote_Vice_President",
            "title": "School Vice President",
            "shortTitle": "Vice President",
            "subtitle": "Class 9 · Central Cabinet",
            "className": "9",
            "gender": "Any",
        },
        {
            "id": "LITERARY_SECRETARY",
            "code": "Vote_Literary_Sec",
            "title": "Literary Secretary",
            "shortTitle": "Literary Sec",
            "subtitle": "Class 9 · Central Cabinet",
            "className": "9",
            "gender": "Any",
        },
        {
            "id": "SPORTS_SECRETARY",
            "code": "Vote_Sports_Sec",
            "title": "Sports Secretary",
            "shortTitle": "Sports Sec",
            "subtitle": "Class 9 · Central Cabinet",
            "className": "9",
            "gender": "Any",
        },
        {
            "id": "SOCIAL_CULTURAL_SECRETARY",
            "code": "Vote_Social_Cultural_Sec",
            "title": "Social & Cultural Secretary",
            "shortTitle": "Social & Cultural Sec",
            "subtitle": "Class 9 · Central Cabinet",
            "className": "9",
            "gender": "Any",
        },
    ]


CENTRAL_HOUSE = {
    "slug": "central",
    "code": "CENTRAL",
    "name": "School Cabinet",
    "shortName": "Cabinet",
    "accent": "#059669",
    "accentHover": "#047857",
    "accentText": "#065f46",
    "onAccent": "#fffdf9",
    "accentRgb": "5, 150, 105",
    "motto": "Leadership, Service & Integrity",
    "eyebrow": "School Cabinet Elections 2026",
}


CANDIDATE_PROFILES = {
    "BHEESHMA": {
        "CAPTAIN_BOY": [
            ("Arjun Verma", "10", "Class 10-A · Option A", "Unwavering resolve, decisive leadership", {"name": "Torch", "icon": "🔦"}, "../assets/candidates/student_boy_1.jpg"),
            ("Tushar Singhania", "10", "Class 10-B · Option B", "Action and accountability for all", {"name": "Shield", "icon": "🛡️"}, "../assets/candidates/student_boy_3.jpg"),
            ("Karthik Menon", "10", "Class 10-C · Option C", "Leading by example with integrity", {"name": "Rising Sun", "icon": "🌅"}, "../assets/candidates/student_boy_4.jpg"),
        ],
        "CAPTAIN_GIRL": [
            ("Ananya Iyer", "10", "Class 10-B · Option A", "Together we strive, together we thrive", {"name": "Book", "icon": "📖"}, "../assets/candidates/student_girl_1.jpg"),
            ("Shruti Deshpande", "10", "Class 10-A · Option B", "Dedicated service, fearless spirit", {"name": "Star", "icon": "⭐"}, "../assets/candidates/student_girl_3.jpg"),
            ("Pallavi Rao", "10", "Class 10-C · Option C", "Empowering every student voice", {"name": "Rocket", "icon": "🚀"}, "../assets/candidates/student_girl_4.jpg"),
        ],
        "VICE_CAPTAIN_BOY": [
            ("Rohan Nair", "9", "Class 9-A · Option A", "Service with humility and courage", {"name": "Compass", "icon": "🧭"}, "../assets/candidates/student_boy_2.jpg"),
            ("Aryan Gupta", "9", "Class 9-B · Option B", "Building strong foundations", {"name": "Tree", "icon": "🌳"}, "../assets/candidates/student_boy_4.jpg"),
            ("Prateek Joshi", "9", "Class 9-C · Option C", "Always ready to assist and lead", {"name": "Bell", "icon": "🔔"}, "../assets/candidates/student_boy_1.jpg"),
        ],
        "VICE_CAPTAIN_GIRL": [
            ("Sneha Reddy", "9", "Class 9-C · Option A", "Empowering every student voice", {"name": "Bell", "icon": "🔔"}, "../assets/candidates/student_girl_2.jpg"),
            ("Ishani Sen", "9", "Class 9-A · Option B", "Harmony, discipline, and progress", {"name": "Book", "icon": "📖"}, "../assets/candidates/student_girl_4.jpg"),
            ("Kritika Bhat", "9", "Class 9-B · Option C", "Energetic and accessible representation", {"name": "Star", "icon": "⭐"}, "../assets/candidates/student_girl_1.jpg"),
        ],
    },
    "GURUDRONA": {
        "CAPTAIN_BOY": [
            ("Devrath Singh", "10", "Class 10-B · Option A", "Aim high, strike true", {"name": "Torch", "icon": "🔦"}, "../assets/candidates/student_boy_3.jpg"),
            ("Harshavardhan Rao", "10", "Class 10-A · Option B", "Discipline, mastery, and focus", {"name": "Shield", "icon": "🛡️"}, "../assets/candidates/student_boy_1.jpg"),
            ("Manish Pandey", "10", "Class 10-C · Option C", "Unyielding pursuit of excellence", {"name": "Compass", "icon": "🧭"}, "../assets/candidates/student_boy_4.jpg"),
        ],
        "CAPTAIN_GIRL": [
            ("Kavya Menon", "10", "Class 10-C · Option A", "Excellence through relentless practice", {"name": "Book", "icon": "📖"}, "../assets/candidates/student_girl_3.jpg"),
            ("Sanya Malhotra", "10", "Class 10-A · Option B", "Courage, compassion, and commitment", {"name": "Star", "icon": "⭐"}, "../assets/candidates/student_girl_1.jpg"),
            ("Deepika Nair", "10", "Class 10-B · Option C", "Inspiring strength through knowledge", {"name": "Rocket", "icon": "🚀"}, "../assets/candidates/student_girl_2.jpg"),
        ],
        "VICE_CAPTAIN_BOY": [
            ("Kunal Joshi", "9", "Class 9-B · Option A", "Steadfast guidance for every teammate", {"name": "Rising Sun", "icon": "🌅"}, "../assets/candidates/student_boy_2.jpg"),
            ("Nikhil Saxena", "9", "Class 9-A · Option B", "Dedication and teamwork", {"name": "Tree", "icon": "🌳"}, "../assets/candidates/student_boy_4.jpg"),
            ("Tanmay Kulkarni", "9", "Class 9-C · Option C", "Committed to house glory", {"name": "Shield", "icon": "🛡️"}, "../assets/candidates/student_boy_1.jpg"),
        ],
        "VICE_CAPTAIN_GIRL": [
            ("Meera Sen", "9", "Class 9-A · Option A", "Inspiring strength through knowledge", {"name": "Star", "icon": "⭐"}, "../assets/candidates/student_girl_4.jpg"),
            ("Rhea Pillai", "9", "Class 9-B · Option B", "Focus, determination, and unity", {"name": "Torch", "icon": "🔦"}, "../assets/candidates/student_girl_2.jpg"),
            ("Anushka Varma", "9", "Class 9-C · Option C", "Your voice, our shared mission", {"name": "Bell", "icon": "🔔"}, "../assets/candidates/student_girl_3.jpg"),
        ],
    },
    "HANUMAN": {
        "CAPTAIN_BOY": [
            ("Tejas Chawla", "10", "Class 10-B · Option A", "No peak is too high to conquer", {"name": "Torch", "icon": "🔦"}, "../assets/candidates/student_boy_4.jpg"),
            ("Yuvraj Sharma", "10", "Class 10-A · Option B", "Courage, loyalty, and unstoppable might", {"name": "Shield", "icon": "🛡️"}, "../assets/candidates/student_boy_1.jpg"),
            ("Samar Chauhan", "10", "Class 10-C · Option C", "Relentless energy and determination", {"name": "Rocket", "icon": "🚀"}, "../assets/candidates/student_boy_3.jpg"),
        ],
        "CAPTAIN_GIRL": [
            ("Ishita Pillai", "10", "Class 10-C · Option A", "Boundless energy, limitless devotion", {"name": "Rising Sun", "icon": "🌅"}, "../assets/candidates/student_girl_1.jpg"),
            ("Tara Nambiar", "10", "Class 10-A · Option B", "Leading with heart and strength", {"name": "Star", "icon": "⭐"}, "../assets/candidates/student_girl_3.jpg"),
            ("Garima Saxena", "10", "Class 10-B · Option C", "Bold decisions, humble execution", {"name": "Book", "icon": "📖"}, "../assets/candidates/student_girl_4.jpg"),
        ],
        "VICE_CAPTAIN_BOY": [
            ("Dhruv Kapoor", "9", "Class 9-B · Option A", "Courage is contagious", {"name": "Compass", "icon": "🧭"}, "../assets/candidates/student_boy_2.jpg"),
            ("Akshay Mehra", "9", "Class 9-A · Option B", "Loyalty and active participation", {"name": "Tree", "icon": "🌳"}, "../assets/candidates/student_boy_1.jpg"),
            ("Naveen Reddy", "9", "Class 9-C · Option C", "Standing tall for our house", {"name": "Bell", "icon": "🔔"}, "../assets/candidates/student_boy_3.jpg"),
        ],
        "VICE_CAPTAIN_GIRL": [
            ("Avni Sharma", "9", "Class 9-A · Option A", "Strength begins with unity", {"name": "Star", "icon": "⭐"}, "../assets/candidates/student_girl_2.jpg"),
            ("Bhavya Nair", "9", "Class 9-B · Option B", "Energetic and proactive support", {"name": "Torch", "icon": "🔦"}, "../assets/candidates/student_girl_4.jpg"),
            ("Kareena Joseph", "9", "Class 9-C · Option C", "United we rise, together we win", {"name": "Shield", "icon": "🛡️"}, "../assets/candidates/student_girl_1.jpg"),
        ],
    },
    "KARNA": {
        "CAPTAIN_BOY": [
            ("Abhimanyu Das", "10", "Class 10-A · Option A", "Standing firm when the storm rages", {"name": "Shield", "icon": "🛡️"}, "../assets/candidates/student_boy_1.jpg"),
            ("Raghav Vashisht", "10", "Class 10-B · Option B", "Selfless honor, supreme bravery", {"name": "Torch", "icon": "🔦"}, "../assets/candidates/student_boy_3.jpg"),
            ("Surya Prakash", "10", "Class 10-C · Option C", "Valour and dedication in every deed", {"name": "Rising Sun", "icon": "🌅"}, "../assets/candidates/student_boy_4.jpg"),
        ],
        "CAPTAIN_GIRL": [
            ("Tarini Mukherjee", "10", "Class 10-C · Option A", "Honor over glory, duty over triumph", {"name": "Book", "icon": "📖"}, "../assets/candidates/student_girl_3.jpg"),
            ("Priyanka Bose", "10", "Class 10-A · Option B", "Resilience, fairness, and grace", {"name": "Star", "icon": "⭐"}, "../assets/candidates/student_girl_1.jpg"),
            ("Aaradhya Sen", "10", "Class 10-B · Option C", "Steadfast in the face of all trials", {"name": "Compass", "icon": "🧭"}, "../assets/candidates/student_girl_4.jpg"),
        ],
        "VICE_CAPTAIN_BOY": [
            ("Siddharth Jain", "9", "Class 9-A · Option A", "Loyal to the team, faithful to the cause", {"name": "Compass", "icon": "🧭"}, "../assets/candidates/student_boy_2.jpg"),
            ("Jayesh Patel", "9", "Class 9-B · Option B", "Perseverance and team harmony", {"name": "Tree", "icon": "🌳"}, "../assets/candidates/student_boy_4.jpg"),
            ("Chetan Anand", "9", "Class 9-C · Option C", "Always ready to step up and serve", {"name": "Bell", "icon": "🔔"}, "../assets/candidates/student_boy_1.jpg"),
        ],
        "VICE_CAPTAIN_GIRL": [
            ("Roshni Paul", "9", "Class 9-B · Option A", "Unyielding spirit, unwavering heart", {"name": "Torch", "icon": "🔦"}, "../assets/candidates/student_girl_2.jpg"),
            ("Diya Sengupta", "9", "Class 9-A · Option B", "Steadfast resolve and bright ideals", {"name": "Star", "icon": "⭐"}, "../assets/candidates/student_girl_4.jpg"),
            ("Maya Nambiar", "9", "Class 9-C · Option C", "Courage in duty, warmth in spirit", {"name": "Shield", "icon": "🛡️"}, "../assets/candidates/student_girl_3.jpg"),
        ],
    },
    "VASISTHA": {
        "CAPTAIN_BOY": [
            ("Aditya Hegde", "10", "Class 10-A · Option A", "True power lies in quiet conviction", {"name": "Tree", "icon": "🌳"}, "../assets/candidates/student_boy_3.jpg"),
            ("Gautam Menon", "10", "Class 10-B · Option B", "Wisdom, peace, and integrity", {"name": "Torch", "icon": "🔦"}, "../assets/candidates/student_boy_1.jpg"),
            ("Pranav Joshi", "10", "Class 10-C · Option C", "Principled guidance, enduring calm", {"name": "Compass", "icon": "🧭"}, "../assets/candidates/student_boy_4.jpg"),
        ],
        "CAPTAIN_GIRL": [
            ("Pooja Kulkarni", "10", "Class 10-A · Option A", "Compassion and character above all", {"name": "Book", "icon": "📖"}, "../assets/candidates/student_girl_1.jpg"),
            ("Nandita Rao", "10", "Class 10-B · Option B", "Dignity in leadership and speech", {"name": "Star", "icon": "⭐"}, "../assets/candidates/student_girl_3.jpg"),
            ("Malavika Nair", "10", "Class 10-C · Option C", "Harmonious hearts build great houses", {"name": "Rising Sun", "icon": "🌅"}, "../assets/candidates/student_girl_4.jpg"),
        ],
        "VICE_CAPTAIN_BOY": [
            ("Varun Bhat", "9", "Class 9-C · Option A", "Leading by standing beside you", {"name": "Shield", "icon": "🛡️"}, "../assets/candidates/student_boy_2.jpg"),
            ("Naveen Iyer", "9", "Class 9-A · Option B", "Gentle strength, clear direction", {"name": "Compass", "icon": "🧭"}, "../assets/candidates/student_boy_4.jpg"),
            ("Rahul Somani", "9", "Class 9-B · Option C", "Committed to house unity and peace", {"name": "Bell", "icon": "🔔"}, "../assets/candidates/student_boy_1.jpg"),
        ],
        "VICE_CAPTAIN_GIRL": [
            ("Tanvi Saxena", "9", "Class 9-B · Option A", "Harmonious hearts build great houses", {"name": "Star", "icon": "⭐"}, "../assets/candidates/student_girl_4.jpg"),
            ("Divya Kamath", "9", "Class 9-A · Option B", "Graceful action and dependable trust", {"name": "Book", "icon": "📖"}, "../assets/candidates/student_girl_2.jpg"),
            ("Swati Mishra", "9", "Class 9-C · Option C", "Empathetic listening, active service", {"name": "Torch", "icon": "🔦"}, "../assets/candidates/student_girl_3.jpg"),
        ],
    },
    "VISHWAMITHRA": {
        "CAPTAIN_BOY": [
            ("Vikramaditya Roy", "10", "Class 10-C · Option A", "Creating new horizons where none exist", {"name": "Rocket", "icon": "🚀"}, "../assets/candidates/student_boy_4.jpg"),
            ("Shaurya Singhal", "10", "Class 10-A · Option B", "Audacity, innovation, and valor", {"name": "Torch", "icon": "🔦"}, "../assets/candidates/student_boy_1.jpg"),
            ("Anirudh Deshmukh", "10", "Class 10-B · Option C", "Trailblazing with purpose and power", {"name": "Rising Sun", "icon": "🌅"}, "../assets/candidates/student_boy_3.jpg"),
        ],
        "CAPTAIN_GIRL": [
            ("Rhea Deshmukh", "10", "Class 10-B · Option A", "Fearless pursuit of greatness", {"name": "Star", "icon": "⭐"}, "../assets/candidates/student_girl_3.jpg"),
            ("Ayesha Khan", "10", "Class 10-A · Option B", "Bold ideas, unstoppable drive", {"name": "Compass", "icon": "🧭"}, "../assets/candidates/student_girl_1.jpg"),
            ("Tanvi Sengupta", "10", "Class 10-C · Option C", "Inspiring innovation across our house", {"name": "Book", "icon": "📖"}, "../assets/candidates/student_girl_4.jpg"),
        ],
        "VICE_CAPTAIN_BOY": [
            ("Samarth Rao", "9", "Class 9-A · Option A", "Resilience in every challenge", {"name": "Shield", "icon": "🛡️"}, "../assets/candidates/student_boy_2.jpg"),
            ("Vivan Kapoor", "9", "Class 9-B · Option B", "Courageous spirit, disciplined mind", {"name": "Tree", "icon": "🌳"}, "../assets/candidates/student_boy_4.jpg"),
            ("Tejas Nambiar", "9", "Class 9-C · Option C", "Ready to explore, ready to conquer", {"name": "Bell", "icon": "🔔"}, "../assets/candidates/student_boy_1.jpg"),
        ],
        "VICE_CAPTAIN_GIRL": [
            ("Pari Chopra", "9", "Class 9-C · Option A", "Breaking barriers with bold determination", {"name": "Torch", "icon": "🔦"}, "../assets/candidates/student_girl_2.jpg"),
            ("Ananya Roy", "9", "Class 9-A · Option B", "Creative solutions for every student", {"name": "Star", "icon": "⭐"}, "../assets/candidates/student_girl_4.jpg"),
            ("Sana Sheikh", "9", "Class 9-B · Option C", "Dynamic, inclusive, and forward-thinking", {"name": "Rocket", "icon": "🚀"}, "../assets/candidates/student_girl_3.jpg"),
        ],
    },
    "CENTRAL": {
        "PRESIDENT": [
            ("Kabir Mehta", "10", "Class 10-A · Option A", "Visionary leadership, institutional excellence", {"name": "Torch", "icon": "🔦"}, "../assets/candidates/student_boy_1.jpg"),
            ("Ananya Sundaram", "10", "Class 10-B · Option B", "Integrity, inclusivity, and student empowerment", {"name": "Star", "icon": "⭐"}, "../assets/candidates/student_girl_1.jpg"),
            ("Rishabh Tandon", "10", "Class 10-C · Option C", "Bridging administration and student council", {"name": "Shield", "icon": "🛡️"}, "../assets/candidates/student_boy_3.jpg"),
        ],
        "VICE_PRESIDENT": [
            ("Manav Saxena", "9", "Class 9-A · Option A", "Energetic leadership with unwavering dedication", {"name": "Compass", "icon": "🧭"}, "../assets/candidates/student_boy_2.jpg"),
            ("Isha Nair", "9", "Class 9-B · Option B", "Championing student causes with empathy", {"name": "Book", "icon": "📖"}, "../assets/candidates/student_girl_2.jpg"),
            ("Vivaan Goel", "9", "Class 9-C · Option C", "Active communication, transparent progress", {"name": "Rising Sun", "icon": "🌅"}, "../assets/candidates/student_boy_4.jpg"),
        ],
        "LITERARY_SECRETARY": [
            ("Siddharth Varma", "9", "Class 9-B · Option A", "Celebrating expression, eloquence, and literature", {"name": "Book", "icon": "📖"}, "../assets/candidates/student_boy_4.jpg"),
            ("Kavya Ramanathan", "9", "Class 9-A · Option B", "Fostering vibrant debate, journalism, and writing", {"name": "Star", "icon": "⭐"}, "../assets/candidates/student_girl_4.jpg"),
            ("Nirav Shah", "9", "Class 9-C · Option C", "Empowering every student voice through words", {"name": "Bell", "icon": "🔔"}, "../assets/candidates/student_boy_2.jpg"),
        ],
        "SPORTS_SECRETARY": [
            ("Aayush Rawat", "9", "Class 9-C · Option A", "Sportsmanship, grit, and athletic glory", {"name": "Trophy", "icon": "🏆"}, "../assets/candidates/student_boy_3.jpg"),
            ("Tanvi Bhardwaj", "9", "Class 9-A · Option B", "Fitness for all, medals for our school", {"name": "Torch", "icon": "🔦"}, "../assets/candidates/student_girl_3.jpg"),
            ("Arman Gill", "9", "Class 9-B · Option C", "Championing teamwork and competitive spirit", {"name": "Shield", "icon": "🛡️"}, "../assets/candidates/student_boy_1.jpg"),
        ],
        "SOCIAL_CULTURAL_SECRETARY": [
            ("Zoya Akhtar", "9", "Class 9-A · Option A", "Spectacular festivals, unforgettable traditions", {"name": "Rising Sun", "icon": "🌅"}, "../assets/candidates/student_girl_2.jpg"),
            ("Pranav Khandelwal", "9", "Class 9-B · Option B", "Showcasing every talent, uniting all houses", {"name": "Rocket", "icon": "🚀"}, "../assets/candidates/student_boy_2.jpg"),
            ("Rhea Sengupta", "9", "Class 9-C · Option C", "Vibrant cultural arts and festive school spirit", {"name": "Star", "icon": "⭐"}, "../assets/candidates/student_girl_4.jpg"),
        ],
    },
}


SYMBOL_SLUGS = {
    "Torch": "torch",
    "Shield": "shield",
    "Rising Sun": "rising_sun",
    "Book": "book",
    "Star": "star",
    "Trophy": "trophy",
    "Tree": "tree",
    "Bell": "bell",
    "Rocket": "rocket",
    "Compass": "compass",
}


def get_symbol_obj(sym):
    if not isinstance(sym, dict):
        return {
            "name": "Candidate Choice",
            "icon": "⭐",
            "slug": "star",
            "image": "../assets/symbols/star.png",
            "imagePath": "../assets/symbols/star.png",
        }
    name = sym.get("name", "Star")
    slug = SYMBOL_SLUGS.get(name, name.lower().replace(" ", "_"))
    return {
        "name": name,
        "icon": sym.get("icon", "⭐"),
        "slug": slug,
        "image": f"../assets/symbols/{slug}.png",
        "imagePath": f"../assets/symbols/{slug}.png",
    }


def build_central_demo_candidates():
    candidates = []
    positions = get_central_positions()
    for pos in positions:
        pos_id = pos["id"]
        tag_short = pos_id[:4]
        items = CANDIDATE_PROFILES["CENTRAL"].get(pos_id, [])
        for idx, (name, cls, sec, tagline, symbol, photo) in enumerate(items):
            letter = chr(65 + idx)
            sym_obj = get_symbol_obj(symbol)
            candidates.append(
                {
                    "id": f"CAND_CENTRAL_{pos_id}_{letter}",
                    "admissionNo": f"DEMO-{tag_short}-{letter}",
                    "fullName": name,
                    "className": cls,
                    "section": sec,
                    "houseCode": "CENTRAL",
                    "positionId": pos_id,
                    "positionName": f"{pos['title']} ({pos['subtitle']})",
                    "tagline": f"{tagline} · School Cabinet",
                    "symbolObj": sym_obj,
                    "photoUrl": photo,
                    "photoPath": photo,
                    "isApproved": True,
                }
            )
    return candidates


def build_demo_candidates():
    candidates = []
    positions = get_positions()
    for h in HOUSES:
        h_code = h["code"]
        for pos in positions:
            pos_id = pos["id"]
            tag_short = f"{pos['className']}{pos['gender'][0]}"
            items = CANDIDATE_PROFILES.get(h_code, {}).get(pos_id, [])
            for idx, (name, cls, sec, tagline, symbol, photo) in enumerate(items):
                letter = chr(65 + idx)
                sym_obj = get_symbol_obj(symbol)
                candidates.append(
                    {
                        "id": f"CAND_{h_code}_{pos_id}_{letter}",
                        "admissionNo": f"DEMO-{tag_short}-{letter}",
                        "fullName": name,
                        "className": cls,
                        "section": sec,
                        "houseCode": h_code,
                        "positionId": pos_id,
                        "positionName": f"{pos['title']} ({pos['subtitle']})",
                        "tagline": f"{tagline} · {h['name']} House",
                        "symbolObj": sym_obj,
                        "photoUrl": photo,
                        "photoPath": photo,
                        "isApproved": True,
                    }
                )
    candidates.extend(build_central_demo_candidates())
    return candidates



def build_admin_data_js(students, candidates) -> str:
    admin_houses = [
        {k: h[k] for k in ("slug", "code", "name", "accent", "accentText", "accentRgb")}
        for h in HOUSES
    ]
    admin_houses.append({
        "slug": "central",
        "code": "CENTRAL",
        "name": "School Cabinet",
        "accent": "#059669",
        "accentText": "#065f46",
        "accentRgb": "5, 150, 105",
    })
    positions = get_positions()
    central_positions = get_central_positions()
    payload = {
        "electionId": "ELECTION_2026",
        "electionName": "School House Elections 2026",
        "positionId": positions[0]["id"],
        "positionName": "House Captains & Vice Captains",
        "positions": positions,
        "centralPositions": central_positions,
        "houses": admin_houses,
        "students": students,
        "candidates": candidates,
    }
    return (
        "// Admin Console — Official School Voter Roster (from ELECTIONS HOUSES (1).xlsx) & 4-Role Demo Candidates\n"
        f"window.ADMIN_DATA = {json.dumps(payload, indent=2)};\n"
    )


def build_unassigned_markdown(blank_house) -> str:
    lines = [
        "# Students With Blank House Name in `ELECTIONS HOUSES (1).xlsx`",
        "",
        f"Total unassigned students: **{len(blank_house)}** *(excluded from voting rosters until assigned a house; 9 duplicate rows in `CLASS9` sheet were also skipped)*.",
        "",
        "| # | Class | S.NO | Temp Voting ID | Student Name | Section | Father Name | Assigned House (Pending) |",
        "| :---: | :---: | :---: | :---: | :--- | :--- | :--- | :--- |",
    ]
    for idx, b in enumerate(blank_house, 1):
        lines.append(
            f"| {idx} | {b['className']} | {b['sno']} | `{b['tempId']}` | {b['fullName']} | {b['section']} | {b['fatherName']} | |"
        )
    return "\n".join(lines) + "\n"


def main():
    students, blank_house, counts = parse_xlsx(XLSX_PATH)
    candidates = build_demo_candidates()

    admin_path = ROOT / "Houses" / "admin" / "data.js"
    admin_path.parent.mkdir(parents=True, exist_ok=True)
    admin_path.write_text(build_admin_data_js(students, candidates), encoding="utf-8")
    (ROOT / "1docs" / "UNASSIGNED_HOUSE_STUDENTS.md").write_text(
        build_unassigned_markdown(blank_house), encoding="utf-8"
    )

    print(f"Exported admin/data.js with {len(students)} valid students and {len(candidates)} demo candidates.")
    print("House counts:", dict(counts))
    print(f"Saved {len(blank_house)} blank-house students to 1docs/UNASSIGNED_HOUSE_STUDENTS.md")


if __name__ == "__main__":
    main()
