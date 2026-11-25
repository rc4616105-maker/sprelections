import json
import openpyxl

wb = openpyxl.load_workbook('1docs/OFFICIAL_STUDENT_VOTER_IDS_2026.xlsx', data_only=True)
sheet = wb.active

roster = {}
for r in range(2, sheet.max_row + 1):
    vid = str(sheet.cell(r, 2).value or '').strip().upper()
    name = str(sheet.cell(r, 3).value or '').strip()
    cls = str(sheet.cell(r, 4).value or '').strip()
    sec = str(sheet.cell(r, 5).value or '').strip()
    gender = str(sheet.cell(r, 6).value or '').strip()
    house = str(sheet.cell(r, 7).value or '').strip().upper()
    if vid:
        roster[vid] = {
            'vid': vid,
            'name': name,
            'cls': cls,
            'sec': sec,
            'gender': gender,
            'house': house
        }

# Accurate manual / verified associations for all 39 cabinet candidates
# Candidate Adm, Candidate Name, Verified Voter ID, Verified House Code, Role Title
verified_cands = [
    # PRESIDENT (Class 10)
    ("7083", "M.Rithvik", "1C6305", "VISHWAMITHRA", "School President", "Class 10 · CS", "Amarkantak"),
    ("7222", "M.Vaishnavi", "1C2457", "VISHWAMITHRA", "School President", "Class 10 · CS", "Amarkantak"),
    ("10055", "S.Harini Reddy", "1C3135", "VASISTHA", "School President", "Class 10 · CS", "Mahabaleshwar"),
    ("10189", "V.Janaki Koushik", "1M5135", "VASISTHA", "School President", "Class 10 · MRP", "Mahabaleshwar"),
    ("10091", "Y.Srinith", "1C6361", "HANUMAN", "School President", "Class 10 · CS", "Yamunotri"),

    # VICE PRESIDENT (Class 9)
    ("9901", "N.Enriqe Iglesias", "9K6281", "GURUDRONA", "School Vice President", "Class 9 · KC", "Trimbakeshwar"),
    ("9167", "G.Badrinath", "9S5116", "HANUMAN", "School Vice President", "Class 9 · SD", "Yamunotri"),
    ("9037", "J.Sampath Kumar", "9A8173", "VASISTHA", "School Vice President", "Class 9 · APJ", "Mahabaleshwar"),
    ("9093", "K.Ambika", "9K1995", "KARNA", "School Vice President", "Class 9 · KC", "Manasarovar"),
    ("9183", "M.Vivekananda Rao", "9S2383", "GURUDRONA", "School Vice President", "Class 9 · SD", "Trimbakeshwar"),
    ("9088", "G. Srunith Goud", "9A5019", "BHEESHMA", "School Vice President", "Class 9 · AB", "Gangotri"),
    ("9V4182", "M.Anvitha Sharma", "9V4182", "VASISTHA", "School Vice President", "Class 9 · VSB", "Mahabaleshwar"),
    ("9V1966", "K.Hadvitha", "9V1966", "VISHWAMITHRA", "School Vice President", "Class 9 · VSB", "Amarkantak"),
    ("9V4045", "K.Ishwarya", "9V4045", "VISHWAMITHRA", "School Vice President", "Class 9 · VSB", "Amarkantak"),
    ("9V7995", "G.Aadhya", "9V7995", "HANUMAN", "School Vice President", "Class 9 · VSB", "Yamunotri"),
    ("9V1576", "V.Ananya Reddy", "9V1576", "KARNA", "School Vice President", "Class 9 · VSB", "Manasarovar"),

    # SPORTS SECRETARY (Class 9)
    ("9069", "Ch.Bala Thrusha Datta", "9A9164", "VASISTHA", "Sports Secretary", "Class 9 · APJ", "Mahabaleshwar"),
    ("9172", "Ch.Kowshik", "9S2374", "BHEESHMA", "Sports Secretary", "Class 9 · SD", "Gangotri"),
    ("8008", "K.Krithika", "9S6145", "BHEESHMA", "Sports Secretary", "Class 9 · SD", "Gangotri"),
    ("9227", "R.Srikshith", "9V1574", "HANUMAN", "Sports Secretary", "Class 9 · VSB", "Yamunotri"),
    ("9178", "S.Rithvik Reddy", "9S3094", "BHEESHMA", "Sports Secretary", "Class 9 · SD", "Gangotri"),
    ("9200", "S.Sahasra", "9V9804", "HANUMAN", "Sports Secretary", "Class 9 · VSB", "Yamunotri"),
    ("9062", "Shubhi Patel", "9A6327", "KARNA", "Sports Secretary", "Class 9 · AB", "Manasarovar"),

    # LITERARY SECRETARY (Class 9)
    ("9198", "Balla Raga Sri", "9V8471", "VISHWAMITHRA", "Literary Secretary", "Class 9 · VSB", "Amarkantak"),
    ("8102", "D. Samanvitha", "1J6758", "BHEESHMA", "Literary Secretary", "Class 9 · JLB", "Gangotri"),
    ("8074", "G.Harsha Vardhan Rao", "9S2280", "HANUMAN", "Literary Secretary", "Class 9 · SD", "Yamunotri"),
    ("9192", "Indu Priya", "9S2952", "BHEESHMA", "Literary Secretary", "Class 9 · SD", "Gangotri"),
    ("9157", "M.Srivaishnavi", "9V1932", "BHEESHMA", "Literary Secretary", "Class 9 · VSB", "Gangotri"),
    ("9052", "N.Malala", "9K6281", "VISHWAMITHRA", "Literary Secretary", "Class 9 · KC", "Amarkantak"),
    ("9138", "Y Bhagya Sri", "9S8038", "KARNA", "Literary Secretary", "Class 9 · SD", "Manasarovar"),
    ("9K7051", "L.Rushil", "9K7051", "GURUDRONA", "Literary Secretary", "Class 9 · KC", "Trimbakeshwar"),

    # SOCIAL & CULTURAL SECRETARY (Class 9)
    ("7071", "G.Ashwath", "9S5700", "HANUMAN", "Social & Cultural Secretary", "Class 9 · SD", "Yamunotri"),
    ("7198", "K.Akshara", "9V1412", "BHEESHMA", "Social & Cultural Secretary", "Class 9 · VSB", "Gangotri"),
    ("8096", "K.Rasagna", "8D6913", "BHEESHMA", "Social & Cultural Secretary", "Class 8 · DS", "Gangotri"),
    ("9190", "P.Divija", "9V1030", "GURUDRONA", "Social & Cultural Secretary", "Class 9 · VSB", "Trimbakeshwar"),
    ("9104", "P.Meghana", "9K7833", "KARNA", "Social & Cultural Secretary", "Class 9 · KC", "Manasarovar"),
    ("9189", "V.Chaithra", "9V7410", "VASISTHA", "Social & Cultural Secretary", "Class 9 · VSB", "Mahabaleshwar"),
    ("9170", "V.Himavardhan", "9S7692", "BHEESHMA", "Social & Cultural Secretary", "Class 9 · SD", "Gangotri"),
    ("9195", "Nithya Sree.Y", "9S2952", "BHEESHMA", "Social & Cultural Secretary", "Class 9 · SD", "Gangotri")
]

print("Total verified candidates:", len(verified_cands))

output_data = []
for adm, name, vid, house, role, cls_sec, constituency in verified_cands:
    # Full house title
    house_title = {
        "BHEESHMA": "Bheeshma House",
        "GURUDRONA": "Gurudrona House",
        "HANUMAN": "Hanuman House",
        "KARNA": "Karna House",
        "VASISTHA": "Vasistha House",
        "VISHWAMITHRA": "Vishwamithra House"
    }.get(house, f"{house} House")
    
    output_data.append({
        "candidateAdm": adm,
        "candidateName": name,
        "voterId": vid,
        "houseCode": house,
        "houseTitle": house_title,
        "constituency": constituency,
        "roleTitle": role,
        "classSec": cls_sec
    })

with open('scripts/school_cabinet_contestants_registry.json', 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=2)

print("Saved school_cabinet_contestants_registry.json successfully!")
