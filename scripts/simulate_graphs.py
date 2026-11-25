import json

with open('Houses/admin/data.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('"houses":')
idx2 = text.find('"students":', idx)
idx3 = text.find('"candidates":', idx2)

houses = json.loads(text[idx + len('"houses":'):idx2].strip().rstrip(','))
students = json.loads(text[idx2 + len('"students":'):idx3].strip().rstrip(','))

sixHouses = [h for h in houses if h['code'] not in ['ALL', 'CENTRAL']]
sixHouseCodes = set(h['code'] for h in sixHouses)
print("sixHouseCodes:", sixHouseCodes)

def isBoyStudent(s):
    g = str(s.get('gender') or '').strip().upper()
    return g in ['M', 'BOY', 'MALE']

def isGirlStudent(s):
    g = str(s.get('gender') or '').strip().upper()
    return g in ['F', 'GIRL', 'FEMALE']

activeStudents = [s for s in students if s.get('isActive') and s.get('admissionNo') != '0000' and not s.get('isStaff') and s.get('houseCode') in sixHouseCodes]
print("activeStudents:", len(activeStudents))

boysEligible = sum(1 for s in activeStudents if isBoyStudent(s))
girlsEligible = sum(1 for s in activeStudents if isGirlStudent(s))
print(f"boysEligible: {boysEligible}, girlsEligible: {girlsEligible}")
