import json

with open('Houses/admin/data.js', 'r', encoding='utf-8') as f:
    c = f.read()
eq = c.find('=')
data = json.loads(c[eq+1:].strip().rstrip(';'))

students = data.get('students', [])
candidates = [c for c in data.get('candidates', []) if c['houseCode'] == 'CENTRAL']

for cand in candidates:
    adm = str(cand.get('admissionNo', '')).strip().upper()
    cname = cand.get('fullName', '').strip().lower()
    
    # Try exact admission match
    m = next((s for s in students if str(s.get('admissionNo', '')).strip().upper() == adm), None)
    if not m:
        # Try match by name
        m = next((s for s in students if s.get('fullName', '').strip().lower() == cname), None)
    if not m:
        # Try partial name
        m = next((s for s in students if cname in s.get('fullName', '').strip().lower() or s.get('fullName', '').strip().lower() in cname), None)
        
    print(f"Cand: {cand['fullName']} ({cand['admissionNo']}) -> Matched House: {m.get('houseCode') if m else 'NOT FOUND'} (Adm in roster: {m.get('admissionNo') if m else 'N/A'}, Name in roster: {m.get('fullName') if m else 'N/A'})")
