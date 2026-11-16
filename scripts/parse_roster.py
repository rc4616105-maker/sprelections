from pathlib import Path
from collections import Counter
import json
import re
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parent.parent
XLSX_PATH = ROOT / "ELECTIONS HOUSES (1).xlsx"

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

    # Universal demo user (`0000`) for testing across all booths
    if "0000" not in seen_ids:
        seen_ids.add("0000")
        students.insert(
            0,
            {
                "admissionNo": "0000",
                "fullName": "Demo User",
                "gender": "—",
                "fatherName": "Demo Record",
                "className": "Demo",
                "section": "All",
                "houseCode": "ALL",
                "isActive": True,
                "isCandidate": False,
                "positionName": None,
            },
        )

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


def build_central_demo_candidates():
    candidates = []
    positions = get_central_positions()
    for pos in positions:
        tag_short = pos["id"][:4]
        for letter in ("A", "B", "C"):
            candidates.append(
                {
                    "id": f"CAND_CENTRAL_{pos['id']}_{letter}",
                    "admissionNo": f"DEMO-{tag_short}-{letter}",
                    "fullName": f"Candidate {letter}",
                    "className": pos["className"],
                    "section": f"{pos['subtitle']} · Option {letter}",
                    "houseCode": "CENTRAL",
                    "positionId": pos["id"],
                    "positionName": f"{pos['title']} ({pos['subtitle']})",
                    "tagline": f"Demo {pos['title']} Candidate {letter} · School Cabinet",
                    "isApproved": True,
                }
            )
    return candidates


def build_demo_candidates():
    candidates = []
    positions = get_positions()
    for h in HOUSES:
        for pos in positions:
            tag_short = f"{pos['className']}{pos['gender'][0]}"
            for letter in ("A", "B", "C"):
                candidates.append(
                    {
                        "id": f"CAND_{h['code']}_{pos['id']}_{letter}",
                        "admissionNo": f"DEMO-{tag_short}-{letter}",
                        "fullName": f"Candidate {letter}",
                        "className": pos["className"],
                        "section": f"{pos['subtitle']} · Option {letter}",
                        "houseCode": h["code"],
                        "positionId": pos["id"],
                        "positionName": f"{pos['title']} ({pos['subtitle']})",
                        "tagline": f"Demo {pos['title']} Candidate {letter} · {h['name']} House",
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

    (ROOT / "admin" / "data.js").write_text(build_admin_data_js(students, candidates), encoding="utf-8")
    (ROOT / "1docs" / "UNASSIGNED_HOUSE_STUDENTS.md").write_text(
        build_unassigned_markdown(blank_house), encoding="utf-8"
    )

    print(f"Exported admin/data.js with {len(students)} valid students and {len(candidates)} demo candidates.")
    print("House counts:", dict(counts))
    print(f"Saved {len(blank_house)} blank-house students to 1docs/UNASSIGNED_HOUSE_STUDENTS.md")


if __name__ == "__main__":
    main()
