with open('C:/Users/Abhinav/.gemini/antigravity/brain/44e72ab9-3bd0-4ded-96fa-40285707e196/.system_generated/logs/transcript.jsonl', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'function renderDrilldown\(snap\)', text)]
idx = matches[-1]
snippet = text[idx:idx+8000].replace('\\r\\n', '\n').replace('\\n', '\n').replace('\\"', '"').replace('\\t', '  ')
end_idx = snippet.find('function renderOverview(snap)')
print(snippet[:end_idx])
