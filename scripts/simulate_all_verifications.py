import json, urllib.request

with open('new_students_roster.json', 'r', encoding='utf-8') as f:
    stus = json.load(f)

SUPABASE_URL = 'https://rziptxcknaeuorekxwrl.supabase.co'
SECRET_KEY = 'sb_secret_FtxzxZKea9lg5fhHm10sEA_WZcgFcs8'

houses = ["BHEESHMA", "GURUDRONA", "HANUMAN", "KARNA", "VASISTHA", "VISHWAMITHRA"]

print("="*60)
print("TESTING VERIFICATION ACROSS ALL 6 HOUSE KIOSKS:")
print("="*60)

for hc in houses:
    folder = hc.lower()
    # Read house data.js
    with open(f'Houses/{folder}/data.js', 'r', encoding='utf-8') as f:
        txt = f.read()
    
    # Pick a student from this house
    h_stus = [s for s in stus if s['houseCode'] == hc]
    test_stu = h_stus[0]
    adm = test_stu['admissionNo']
    
    # 1. Check local data.js
    found_in_local = f'"{adm}"' in txt
    
    # 2. Check Supabase
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/voters?admission_no=eq.{adm}&select=admission_no,full_name,house_code,final_status",
        headers={
            'apikey': SECRET_KEY,
            'Authorization': f'Bearer {SECRET_KEY}'
        }
    )
    with urllib.request.urlopen(req) as resp:
        sb_res = json.loads(resp.read().decode('utf-8'))
        found_in_sb = len(sb_res) > 0 and sb_res[0]['house_code'] == hc
    
    print(f"Booth {hc:12} | Test Voter ID: {adm} ({test_stu['fullName']})")
    print(f"  Local data.js: {'PASS' if found_in_local else 'FAIL'} | Supabase: {'PASS' if found_in_sb else 'FAIL'}")

# Verify Teachers and Demo accounts
print("\nVerifying Universal Voters:")
for adm in ['1C8492', '0000', '6001']:
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/voters?admission_no=eq.{adm}&select=admission_no,full_name,house_code",
        headers={
            'apikey': SECRET_KEY,
            'Authorization': f'Bearer {SECRET_KEY}'
        }
    )
    with urllib.request.urlopen(req) as resp:
        sb_res = json.loads(resp.read().decode('utf-8'))
        print(f"  Universal ID {adm}: {'PASS (' + sb_res[0]['full_name'] + ')' if sb_res else 'FAIL'}")
