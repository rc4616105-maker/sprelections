import urllib.request
import json
import time

SUPABASE_URL = 'https://rziptxcknaeuorekxwrl.supabase.co'
SECRET_KEY = 'sb_secret_FtxzxZKea9lg5fhHm10sEA_WZcgFcs8'

# 1. Delete old students
print("Clearing old students from Supabase (where house_code != 'ALL')...")
req = urllib.request.Request(
    f"{SUPABASE_URL}/rest/v1/voters?house_code=neq.ALL",
    method="DELETE",
    headers={
        'apikey': SECRET_KEY,
        'Authorization': f'Bearer {SECRET_KEY}',
        'Content-Type': 'application/json'
    }
)

with urllib.request.urlopen(req) as resp:
    print(f"Delete response: {resp.status}")

# 2. Load new students
with open('new_students_roster.json', 'r', encoding='utf-8') as f:
    students = json.load(f)

print(f"Preparing to insert {len(students)} new students...")

# Format for Supabase
rows = []
for s in students:
    rows.append({
        "admission_no": s["admissionNo"],
        "full_name": s["fullName"],
        "class_name": str(s["className"]),
        "section": s["section"],
        "house_code": s["houseCode"],
        "house_name": s["houseName"],
        "final_status": "Not Voted",
        "voted_for": "",
        "vote_10_boy": "",
        "vote_10_girl": "",
        "vote_9_boy": "",
        "vote_9_girl": "",
        "position_name": "House Captains & Vice Captains",
        "is_active": True
    })

# Batch insert in chunks of 100
chunk_size = 100
total_inserted = 0

for i in range(0, len(rows), chunk_size):
    chunk = rows[i:i + chunk_size]
    payload = json.dumps(chunk).encode('utf-8')
    
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/voters",
        data=payload,
        method="POST",
        headers={
            'apikey': SECRET_KEY,
            'Authorization': f'Bearer {SECRET_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }
    )
    
    with urllib.request.urlopen(req) as resp:
        if resp.status in (200, 201):
            total_inserted += len(chunk)
            print(f"  Inserted chunk {i // chunk_size + 1}: {len(chunk)} rows (Total: {total_inserted}/{len(rows)})")
        else:
            print(f"  Error inserting chunk: status {resp.status}")
    time.sleep(0.1)

print(f"\nSuccessfully inserted {total_inserted} new student voters into Supabase!")
