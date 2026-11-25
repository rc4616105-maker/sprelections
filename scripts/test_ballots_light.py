import urllib.request
import json

url = 'https://rziptxcknaeuorekxwrl.supabase.co/rest/v1/ballots?select=admission_no,status&status=eq.accepted'
headers = {
    'apikey': 'sb_publishable_jcyjkISfyHxcKPwVUloYYQ_4BfL3pUZ',
    'Authorization': 'Bearer sb_publishable_jcyjkISfyHxcKPwVUloYYQ_4BfL3pUZ'
}

req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    print(f"Accepted ballots in Supabase: {len(data)}")
    print("Sample:", data[:3])
