import urllib.request
import json

url = 'https://rziptxcknaeuorekxwrl.supabase.co/rest/v1/candidates?house_code=eq.VASISTHA&is_approved=eq.true&select=*'
headers = {
    'apikey': 'sb_publishable_jcyjkISfyHxcKPwVUloYYQ_4BfL3pUZ',
    'Authorization': 'Bearer sb_publishable_jcyjkISfyHxcKPwVUloYYQ_4BfL3pUZ'
}

req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    print(f"Approved candidates in Supabase for VASISTHA ({len(data)}):")
    for r in data:
        print(f"[{r.get('position_id')}] {r.get('full_name')} ({r.get('id')})")
