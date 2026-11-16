with open('Houses/admin/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('activeKpi === "cancelled"')
if idx == -1: idx = text.find('"cancelled"')
print(text[idx-50:idx+2500])
