with open('Houses/vasistha/styles.css', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('face-live-view-wrap')
if idx != -1:
    print(text[idx-100:idx+1500])
else:
    print("Not found in styles.css")
