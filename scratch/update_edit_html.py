with open('Houses/admin/edit-votes.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Update table header
html = html.replace('<th style="width: 17%;">Voted For</th>', '<th style="width: 17%;">Voted Status</th>')

# Bump version string to ?v=996
import re
html = re.sub(r'supabase-config\.js\?v=\d+', 'supabase-config.js?v=996', html)
html = re.sub(r'edit-votes\.js\?v=\d+', 'edit-votes.js?v=996', html)

with open('Houses/admin/edit-votes.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated Houses/admin/edit-votes.html successfully!")
