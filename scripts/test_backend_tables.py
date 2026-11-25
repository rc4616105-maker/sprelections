import urllib.request
import json

headers = {
    'apikey': 'sb_publishable_jcyjkISfyHxcKPwVUloYYQ_4BfL3pUZ',
    'Authorization': 'Bearer sb_publishable_jcyjkISfyHxcKPwVUloYYQ_4BfL3pUZ'
}

def fetch_table(t):
    url = f'https://rziptxcknaeuorekxwrl.supabase.co/rest/v1/{t}'
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

try:
    voters = fetch_table('voters?select=admission_no&limit=10')
    print('voters count:', len(voters))
except Exception as e:
    print('voters error:', e)

try:
    ballots = fetch_table('ballots?select=admission_no,status&limit=10')
    print('ballots count:', len(ballots))
except Exception as e:
    print('ballots error:', e)

try:
    audit = fetch_table('audit_logs?select=id&limit=10')
    print('audit count:', len(audit))
except Exception as e:
    print('audit error:', e)
