with open('Houses/admin/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('if (activeKpi === "cancelled")')
idx_end = text.find('el.closeDrilldownBtn.addEventListener', idx)
print(text[idx:idx_end])
