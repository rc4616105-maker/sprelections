with open('Houses/admin/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('activeKpi === "accepted"')
print(text[idx-50:idx+1500])
