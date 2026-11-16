with open('C:/Users/Abhinav/.gemini/antigravity/brain/44e72ab9-3bd0-4ded-96fa-40285707e196/.system_generated/logs/transcript.jsonl', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'function renderDrilldown\(', text)]
print('Matches with (:', len(matches))
for m in matches[-3:]:
    print("---")
    print(text[m:m+1200].replace('\\n', '\n'))
