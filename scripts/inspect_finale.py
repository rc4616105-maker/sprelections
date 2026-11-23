with open("Result declaration/index.html", "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find('id="finaleView"')
if idx != -1:
    print(text[idx:idx+2500])
else:
    print("finaleView not found")
