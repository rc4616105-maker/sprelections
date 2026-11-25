import json

with open('Houses/admin/data.js', 'r', encoding='utf-8') as f:
    c = f.read()
eq = c.find('=')
data = json.loads(c[eq+1:].strip().rstrip(';'))

students = {s['admissionNo']: s for s in data.get('students', [])}
candidates = [c for c in data.get('candidates', []) if c['houseCode'] == 'CENTRAL']

print(f"Total Central Candidates: {len(candidates)}")
for c in candidates:
    st = students.get(c['admissionNo'], {})
    print(f"Adm: {c['admissionNo']} | Name: {c['fullName']} | Role: {c['positionId']} | Student House: {st.get('houseCode', 'N/A')}")
