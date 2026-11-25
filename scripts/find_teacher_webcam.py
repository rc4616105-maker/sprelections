with open('Houses/teachers/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('getUserMedia')
if idx != -1:
    print(text[idx-50:idx+800])
else:
    print("Not found getUserMedia")
