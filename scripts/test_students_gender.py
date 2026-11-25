import json

with open('Houses/admin/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('"students":')
idx2 = text.find('"candidates":', idx)
json_str = text[idx + len('"students":'):idx2].strip().rstrip(',')
students = json.loads(json_str)
print("Total students:", len(students))
boys = [s for s in students if str(s.get('gender')).lower() in ['boy', 'm', 'male']]
girls = [s for s in students if str(s.get('gender')).lower() in ['girl', 'f', 'female']]
print(f"Boys: {len(boys)}, Girls: {len(girls)}")
for s in students[:5]:
    print(s.get('admissionNo'), s.get('fullName'), s.get('gender'), s.get('houseCode'), s.get('isActive'))
