import json

with open('new_students_roster.json', 'r', encoding='utf-8') as f:
    new_students = json.load(f)

def make_stu_dict(s):
    d = {
        "admissionNo": s["admissionNo"],
        "fullName": s["fullName"],
        "gender": s.get("gender", "Boy"),
        "fatherName": s.get("fatherName", ""),
        "className": str(s["className"]),
        "section": s.get("section", "A"),
        "houseCode": s["houseCode"],
        "isActive": True,
        "isCandidate": s.get("isCandidate", False),
        "positionName": s.get("positionName", "")
    }
    if s.get("photoUrl"):
        d["photoUrl"] = s.get("photoUrl")
    return d

new_stu_objs = [make_stu_dict(s) for s in new_students]

demo_stu = {
    "admissionNo": "1C8492",
    "fullName": "Aditya Vikram",
    "gender": "Boy",
    "fatherName": "R. K. Vikram",
    "className": "10",
    "section": "Chatrapathi Shivaji (10-CS)",
    "houseCode": "BHEESHMA",
    "isActive": True,
    "isCandidate": False,
    "positionName": "",
    "photoUrl": "../assets/candidates/student_demo.jpg",
    "isUniversal": True
}

all_stus_list = [demo_stu] + new_stu_objs
all_stus_json = json.dumps(all_stus_list, indent=4)

# 1. Update Houses/admin/data.js
print("Updating Houses/admin/data.js...")
with open('Houses/admin/data.js', 'r', encoding='utf-8') as f:
    admin_text = f.read()

start_idx = admin_text.find('"students":')
end_idx = admin_text.find('"candidates":')

if start_idx != -1 and end_idx != -1:
    new_admin_text = admin_text[:start_idx] + f'"students": {all_stus_json},\n  ' + admin_text[end_idx:]
    with open('Houses/admin/data.js', 'w', encoding='utf-8') as f:
        f.write(new_admin_text)
    print("  Admin data.js updated successfully!")
else:
    print("  Error: could not find students/candidates in Houses/admin/data.js")

# 2. Update each of the 6 houses
houses_map = {
    "bheeshma": "BHEESHMA",
    "gurudrona": "GURUDRONA",
    "hanuman": "HANUMAN",
    "karna": "KARNA",
    "vasistha": "VASISTHA",
    "vishwamithra": "VISHWAMITHRA"
}

for folder, hcode in houses_map.items():
    file_path = f'Houses/{folder}/data.js'
    print(f"Updating {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        h_text = f.read()
    
    # 1. Update houseStudents
    h_start = h_text.find('"houseStudents":')
    h_end = h_text.find('"houseCandidates":')
    if h_start == -1 or h_end == -1:
        print(f"  ERROR: could not find houseStudents/houseCandidates in {file_path}")
        continue
        
    house_stus = [demo_stu] + [s for s in new_stu_objs if s["houseCode"] == hcode]
    house_stus_json = json.dumps(house_stus, indent=4)
    
    h_text = h_text[:h_start] + f'"houseStudents": {house_stus_json},\n  ' + h_text[h_end:]
    
    # 2. Update allStudents
    a_start = h_text.find('"allStudents":')
    a_end = h_text.find('"allCandidates":')
    if a_start != -1 and a_end != -1:
        h_text = h_text[:a_start] + f'"allStudents": {all_stus_json},\n  ' + h_text[a_end:]
    else:
        print(f"  Note: allStudents or allCandidates not found in {file_path}")
        
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(h_text)
    print(f"  {file_path} updated with {len(house_stus)} houseStudents and {len(all_stus_list)} allStudents!")

print("\nAll house data.js files updated successfully!")
