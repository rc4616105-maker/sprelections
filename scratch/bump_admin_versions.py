import re

for path in ['Houses/admin/index.html', 'Houses/admin/edit-votes.html']:
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    html = re.sub(r'app\.js\?v=\d+', 'app.js?v=997', html)
    html = re.sub(r'edit-votes\.js\?v=\d+', 'edit-votes.js?v=997', html)
    html = re.sub(r'supabase-config\.js\?v=\d+', 'supabase-config.js?v=997', html)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Bumped version strings in {path} to ?v=997")
