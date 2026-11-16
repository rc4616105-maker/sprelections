with open('Houses/hanuman/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('async function submitFinalVote')
if idx != -1:
    print(text[idx:idx+2500])
