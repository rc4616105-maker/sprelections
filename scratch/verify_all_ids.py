import re

with open('Houses/admin/app.js', 'r', encoding='utf-8') as f:
    app_text = f.read()

with open('Houses/admin/index.html', 'r', encoding='utf-8') as f:
    html_text = f.read()

# Find all getElementById in app.js
ids = re.findall(r'getElementById\(["\']([^"\']+)["\']\)', app_text)
print(f'Total getElementById calls in app.js: {len(ids)}')

missing = []
for i in set(ids):
    if f'id="{i}"' not in html_text and f"id='{i}'" not in html_text:
        missing.append(i)

print('Missing IDs in index.html:', missing)
