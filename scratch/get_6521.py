import json

with open(r'C:\Users\Abhinav\.gemini\antigravity\brain\44e72ab9-3bd0-4ded-96fa-40285707e196\.system_generated\logs\transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f):
        if idx == 6521:
            obj = json.loads(line)
            c = str(obj.get('content', ''))
            print('Line 6521 length:', len(c))
            with open('line_6521.txt', 'w', encoding='utf-8') as out:
                out.write(c)
