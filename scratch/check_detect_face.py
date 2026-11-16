with open('Houses/hanuman/app.js', 'r', encoding='utf-8') as f:
    c = f.read()

idx = c.find('async function detectHumanFace')
print(c[idx:idx+2500])
