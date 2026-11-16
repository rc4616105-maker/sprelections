import urllib.request

houses = ['bheeshma', 'central', 'gurudrona', 'hanuman', 'karna', 'vasistha', 'vishwamithra']
base = "http://127.0.0.1:5500/Houses"

for h in houses:
    print(f"=== Testing {h} ===")
    for asset in ['index.html', 'app.js', 'pico.js', 'facefinder', 'supabase-config.js', 'data.js', 'styles.css']:
        url = f"{base}/{h}/{asset}"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=3) as res:
                content = res.read()
                print(f"  {asset}: {res.status} OK ({len(content)} bytes)")
        except Exception as e:
            print(f"  {asset}: FAILED! {e}")
