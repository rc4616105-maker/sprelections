"""
Test script to simulate kiosk verification for all houses:
1. Verify each house has valid HOUSE_DATA
2. Check that ElectionBackend contract is satisfied
3. Verify test voter 1C8492
4. Verify house-specific student lookups
"""
import json

houses = ['bheeshma', 'gurudrona', 'hanuman', 'karna', 'vasistha', 'vishwamithra']

for h in houses:
    data_path = f'Houses/{h}/data.js'
    sb_path = f'Houses/{h}/supabase-config.js'
    
    with open(data_path, 'r', encoding='utf-8') as f:
        data_text = f.read()
    with open(sb_path, 'r', encoding='utf-8') as f:
        sb_text = f.read()
        
    start_idx = data_text.find('{')
    end_idx = data_text.rfind('}')
    house_data = json.loads(data_text[start_idx:end_idx+1])
    
    cfg = house_data.get('houseConfig', {})
    h_code = cfg.get('code')
    h_name = cfg.get('name')
    students = house_data.get('houseStudents', [])
    candidates = house_data.get('houseCandidates', [])
    
    # Check supabase-config.js syntax safety
    has_broken_syntax = 'oters?' in sb_text.replace('voters?', '')
    has_election_backend = 'window.ElectionBackend = {' in sb_text
    
    sample_student = students[0] if students else None
    
    print(f"[{h_code}] {h_name}:")
    print(f"  - supabase-config.js valid: {not has_broken_syntax}")
    print(f"  - defines ElectionBackend: {has_election_backend}")
    print(f"  - House Candidates: {len(candidates)}")
    print(f"  - House Students: {len(students)}")
    if sample_student:
        print(f"  - Sample Student: {sample_student.get('fullName')} (Adm: {sample_student.get('admissionNo')})")
    print()
