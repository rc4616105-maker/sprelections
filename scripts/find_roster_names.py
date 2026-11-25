import json

with open('Houses/admin/data.js', 'r', encoding='utf-8') as f:
    c = f.read()
eq = c.find('=')
data = json.loads(c[eq+1:].strip().rstrip(';'))

students = data.get('students', [])

for name in ['Rithvik', 'Vaishnavi', 'Harini', 'Janaki', 'Srinith', 'Malala', 'Bhagya', 'Balla', 'Harsha', 'Indu', 'Trusha', 'Kowshik', 'Enriqe', 'Vivekananda', 'Srunith']:
    matches = [s for s in students if name.lower() in s.get('fullName', '').lower()]
    print(f"Query '{name}': {len(matches)} matches")
    for m in matches[:3]:
        print(f"   Adm: {m.get('admissionNo')} | Name: {m.get('fullName')} | House: {m.get('houseCode')} | Class: {m.get('className')}-{m.get('section')}")
