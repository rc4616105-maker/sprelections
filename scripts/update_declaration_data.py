import json

with open('Houses/assets/all-candidates.js', 'r', encoding='utf-8') as f:
    text = f.read()
idx = text.find('window.ALL_CONTESTING_CANDIDATES = ')
cands = json.loads(text[idx+35:-2])

cand_map = {}
for c in cands:
    cand_map[(c['houseCode'], c['positionId'])] = c

def clean_photo(p):
    if not p: return ""
    return p.replace('../assets/', 'assets/')

def make_cand_obj(c, post_title):
    sym = c.get('symbolObj', {})
    sym_img = sym.get('image', '').replace('../assets/', 'assets/') if sym else ''
    return {
        "postTitle": post_title,
        "name": c.get('fullName', ''),
        "admissionNo": c.get('admissionNo', ''),
        "grade": c.get('section') or f"Class {c.get('className')}",
        "photo": clean_photo(c.get('photoUrl') or c.get('photoPath')),
        "quote": c.get('tagline', 'Dedicated to student excellence and democratic leadership.'),
        "symbol": {
            "name": sym.get('name', 'Symbol'),
            "icon": sym.get('icon', '🗳️'),
            "image": sym_img
        }
    }

HOUSES_CONFIG = [
    {
        "id": "bheeshma",
        "hCode": "BHEESHMA",
        "name": "Bheeshma",
        "fullName": "Bheeshma House",
        "color": "#EAB308",
        "accent": "#CA8A04",
        "textColor": "#111827",
        "motto": "Unwavering Resolve & Duty"
    },
    {
        "id": "gurudrona",
        "hCode": "GURUDRONA",
        "name": "Gurudrona",
        "fullName": "Gurudrona House",
        "color": "#2563EB",
        "accent": "#1D4ED8",
        "textColor": "#FFFFFF",
        "motto": "Discipline, Mastery & Focus"
    },
    {
        "id": "hanuman",
        "hCode": "HANUMAN",
        "name": "Hanuman",
        "fullName": "Hanuman House",
        "color": "#EA580C",
        "accent": "#C2410C",
        "textColor": "#FFFFFF",
        "motto": "Courage, Loyalty & Unstoppable Might"
    },
    {
        "id": "karna",
        "hCode": "KARNA",
        "name": "Karna",
        "fullName": "Karna House",
        "color": "#DC2626",
        "accent": "#B91C1C",
        "textColor": "#FFFFFF",
        "motto": "Selfless Honor & Supreme Bravery"
    },
    {
        "id": "vasistha",
        "hCode": "VASISTHA",
        "name": "Vasistha",
        "fullName": "Vasistha House",
        "color": "#DB2777",
        "accent": "#BE185D",
        "textColor": "#FFFFFF",
        "motto": "Wisdom, Peace & Integrity"
    },
    {
        "id": "vishwamithra",
        "hCode": "VISHWAMITHRA",
        "name": "Vishwamithra",
        "fullName": "Vishwamithra House",
        "color": "#7C3AED",
        "accent": "#6D28D9",
        "textColor": "#FFFFFF",
        "motto": "Determination, Innovation & Vision"
    }
]

default_houses = []
for h in HOUSES_CONFIG:
    hCode = h['hCode']
    cb = cand_map.get((hCode, 'CAPTAIN_BOY'), {})
    cg = cand_map.get((hCode, 'CAPTAIN_GIRL'), {})
    vcb = cand_map.get((hCode, 'VICE_CAPTAIN_BOY'), {})
    vcg = cand_map.get((hCode, 'VICE_CAPTAIN_GIRL'), {})

    default_houses.append({
        "id": h["id"],
        "name": h["name"],
        "fullName": h["fullName"],
        "color": h["color"],
        "accent": h["accent"],
        "textColor": h["textColor"],
        "motto": h["motto"],
        "candidates": {
            "boys_captain": make_cand_obj(cb, "Boys Captain"),
            "girls_captain": make_cand_obj(cg, "Girls Captain"),
            "boys_vc": make_cand_obj(vcb, "Boys Vice-Captain"),
            "girls_vc": make_cand_obj(vcg, "Girls Vice-Captain")
        }
    })

CABINET_CONFIG = [
    { "id": "PRESIDENT", "posId": "PRESIDENT", "code": "Vote_President", "name": "President", "fullName": "School President", "color": "#059669", "accent": "#047857", "textColor": "#FFFFFF" },
    { "id": "VICE_PRESIDENT", "posId": "VICE_PRESIDENT", "code": "Vote_Vice_President", "name": "Vice President", "fullName": "School Vice President", "color": "#0D9488", "accent": "#0F766E", "textColor": "#FFFFFF" },
    { "id": "LITERARY_SECRETARY", "posId": "LITERARY_SECRETARY", "code": "Vote_Literary_Sec", "name": "Literary Sec", "fullName": "Literary Secretary", "color": "#7C3AED", "accent": "#6D28D9", "textColor": "#FFFFFF" },
    { "id": "SPORTS_SECRETARY", "posId": "SPORTS_SECRETARY", "code": "Vote_Sports_Sec", "name": "Sports Sec", "fullName": "Sports Secretary", "color": "#EA580C", "accent": "#C2410C", "textColor": "#FFFFFF" },
    { "id": "SOCIAL_CULTURAL_SECRETARY", "posId": "SOCIAL_CULTURAL_SECRETARY", "code": "Vote_Social_Cultural_Sec", "name": "Cultural Sec", "fullName": "Social & Cultural Secretary", "color": "#D97706", "accent": "#B45309", "textColor": "#FFFFFF" }
]

default_cabinet = []
for c_conf in CABINET_CONFIG:
    c_cand = cand_map.get(('CENTRAL', c_conf['posId']), {})
    cand_obj = make_cand_obj(c_cand, c_conf['fullName'])
    default_cabinet.append({
        "id": c_conf["id"],
        "code": c_conf["code"],
        "name": c_conf["name"],
        "fullName": c_conf["fullName"],
        "color": c_conf["color"],
        "accent": c_conf["accent"],
        "textColor": c_conf["textColor"],
        "grade": cand_obj["grade"],
        "postTitle": c_conf["fullName"],
        "candidate": cand_obj
    })

out_js = """/**
 * Election Configuration & Candidate Data
 * Matching Main Web Theme with 6 Houses & 4 Leadership Posts
 * Contains Real Student Candidates, Photos, and Symbols
 */

const DEFAULT_HOUSES = """ + json.dumps(default_houses, indent=2) + """;

const DEFAULT_CABINET_POSTS = """ + json.dumps(default_cabinet, indent=2) + """;
"""

with open('Result declaration/js/data.js', 'w', encoding='utf-8') as f:
    f.write(out_js)

print("Generated Result declaration/js/data.js with real candidates, photos, and symbols!")
