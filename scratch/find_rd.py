with open('C:/Users/Abhinav/.gemini/antigravity/brain/44e72ab9-3bd0-4ded-96fa-40285707e196/.system_generated/steps/7268/output.txt', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('renderDrilldown')
while idx != -1:
    print("Found renderDrilldown at", idx)
    print(text[max(0, idx-50):idx+200])
    idx = text.find('renderDrilldown', idx+1)
