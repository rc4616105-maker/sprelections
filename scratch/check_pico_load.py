with open('Houses/hanuman/app.js', 'r', encoding='utf-8') as f:
    c = f.read()

idx = c.find('let picoClassifier')
print(c[idx:idx+1500])
