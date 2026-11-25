import urllib.request
import json

headers = {
    'apikey': 'sb_publishable_jcyjkISfyHxcKPwVUloYYQ_4BfL3pUZ',
    'Authorization': 'Bearer sb_publishable_jcyjkISfyHxcKPwVUloYYQ_4BfL3pUZ'
}

def sb_fetch_all(table_query):
    rows = []
    offset = 0
    limit = 1000
    sep = '&' if '?' in table_query else '?'
    while True:
        url = f'https://rziptxcknaeuorekxwrl.supabase.co/rest/v1/{table_query}{sep}limit={limit}&offset={offset}'
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            batch = json.loads(resp.read().decode('utf-8'))
            if not isinstance(batch, list): break
            rows.extend(batch)
            if len(batch) < limit: break
            offset += limit
    return rows

voters = sb_fetch_all('voters?select=*')
print('Total voters:', len(voters))

ballots = sb_fetch_all('ballots?select=*&order=cast_at.desc')
print('Total ballots:', len(ballots))
accepted = [b for b in ballots if b.get('status') == 'accepted']
print('Accepted ballots:', len(accepted))
accepted_admissions = set(b.get('admission_no') for b in accepted)
print('Unique accepted voter admissions:', len(accepted_admissions))
