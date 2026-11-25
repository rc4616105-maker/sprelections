with open('Houses/vasistha/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('facefinder')
print(text[idx-50:idx+350])
