with open('Houses/vasistha/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('function analyzeCameraFrame')
print(text[idx:idx+3500])
