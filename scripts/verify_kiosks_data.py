import json

houses = ['bheeshma', 'gurudrona', 'hanuman', 'karna', 'vasistha', 'vishwamithra']

for h in houses:
    path = f'Houses/{h}/data.js'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    start_idx = content.find('{')
    end_idx = content.rfind('}')
    data = json.loads(content[start_idx:end_idx+1])
    
    cfg = data.get('houseConfig', {})
    hc = data.get('houseCandidates', [])
    students = data.get('houseStudents', [])
    all_students = data.get('allStudents', [])
    all_cand = data.get('allCandidates', [])
    
    dummy_names = {'Arjun Verma', 'Tushar Singhania', 'Karthik Menon', 'Priya Sharma', 'Ananya Iyer', 'Sneha Reddy', 'Rohan Mehra', 'Kabir Joshi', 'Kavya Nair', 'Riya Sen'}
    dummies_in_hc = [c['fullName'] for c in hc if c.get('fullName') in dummy_names]
    dummies_in_all = [c['fullName'] for c in all_cand if c.get('fullName') in dummy_names]
    
    print(f"=== {h.upper()} ===")
    print(f"  Config Name: {cfg.get('name')}, Code: {cfg.get('code')}, Slug: {cfg.get('slug')}")
    print(f"  House Candidates: {len(hc)}")
    for c in hc:
        print(f"    - [{c.get('postName')}] {c.get('fullName')} (Adm: {c.get('admissionNo')}, Symbol: {c.get('symbolName')})")
    print(f"  House Students: {len(students)}, All Students: {len(all_students)}, All Candidates: {len(all_cand)}")
    print(f"  Dummy check: houseCandidates dummies={dummies_in_hc}, allCandidates dummies={dummies_in_all}")
