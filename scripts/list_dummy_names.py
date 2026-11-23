import re

with open('scripts/parse_roster.py', 'r', encoding='utf-8') as f:
    text = f.read()

names = re.findall(r'\("([^"]+)",\s*"\d+",\s*"Class[^"]*"', text)
print(f'Total dummy candidate profiles ({len(names)}):')
for n in names:
    print(f'  "{n}",')
