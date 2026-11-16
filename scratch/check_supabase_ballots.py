import urllib.request
import json

SUPABASE_URL = "https://ihdkmopupuyommsffuod.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImloZGttb3B1cHV5b21tc2ZmdW9kIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzg1MTI1MTAsImV4cCI6MjA1NDA4ODUxMH0.a4t8tC1X0T9g0T8v0t1b2c3d4e5f6g7h8i9j0k1l2m" # let's find the real anon key

# Read the anon key from supabase-config.js
with open('Houses/hanuman/supabase-config.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
url_m = re.search(r'SUPABASE_URL\s*=\s*["\']([^"\']+)["\']', text)
key_m = re.search(r'SUPABASE_ANON_KEY\s*=\s*["\']([^"\']+)["\']', text)

if url_m and key_m:
    url = url_m.group(1)
    key = key_m.group(1)
    print("Found url:", url)
    req = urllib.request.Request(
        f"{url}/rest/v1/ballots?select=*&order=created_at.desc&limit=15",
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}"
        }
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            print(f"Total ballots found: {len(data)}")
            for b in data:
                photo_val = b.get('photo_url') or b.get('verification_photo_url') or b.get('photo')
                photo_len = len(str(photo_val)) if photo_val else 0
                photo_preview = str(photo_val)[:60] if photo_val else "None"
                print(f"ID: {b.get('id')}, Voter: {b.get('admission_no')}, House: {b.get('house')}, Booth: {b.get('booth_name')}, Photo: len={photo_len}, preview={photo_preview}, Cancelled: {b.get('is_cancelled')}")
    except Exception as e:
        print("Error:", e)
