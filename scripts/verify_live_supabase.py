import urllib.request, json

SUPABASE_URL = 'https://rziptxcknaeuorekxwrl.supabase.co'
SECRET_KEY = 'sb_secret_FtxzxZKea9lg5fhHm10sEA_WZcgFcs8'

# 1. Total voters
req = urllib.request.Request(
    f"{SUPABASE_URL}/rest/v1/voters?select=admission_no",
    headers={
        'apikey': SECRET_KEY,
        'Authorization': f'Bearer {SECRET_KEY}',
        'Range-Unit': 'items',
        'Range': '0-1500'
    }
)
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    print(f"Total voters currently in Supabase: {len(data)}")

# 2. Test sample IDs from each house
with open('new_students_roster.json', 'r', encoding='utf-8') as f:
    stus = json.load(f)

# Pick 1 student from each house
sample_by_house = {}
for s in stus:
    h = s['houseCode']
    if h not in sample_by_house:
        sample_by_house[h] = s

print("\nVerifying sample new student IDs in Supabase:")
for h, s in sample_by_house.items():
    adm = s['admissionNo']
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/voters?admission_no=eq.{adm}&select=admission_no,full_name,class_name,section,house_code,final_status",
        headers={
            'apikey': SECRET_KEY,
            'Authorization': f'Bearer {SECRET_KEY}'
        }
    )
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        if res:
            r = res[0]
            print(f"  [PASS] {h}: {r['admission_no']} -> {r['full_name']} (Class {r['class_name']}-{r['section']}) | Status: {r['final_status']}")
        else:
            print(f"  [FAIL] {h}: {adm} not found!")

# 3. Verify demo account and teacher
for test_id in ['1C8492', '6001', '0000']:
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/voters?admission_no=eq.{test_id}&select=admission_no,full_name,house_code",
        headers={
            'apikey': SECRET_KEY,
            'Authorization': f'Bearer {SECRET_KEY}'
        }
    )
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        if res:
            r = res[0]
            print(f"  [PASS] Special/Teacher: {r['admission_no']} -> {r['full_name']} (House: {r['house_code']})")
        else:
            print(f"  [FAIL] Special: {test_id} not found!")
