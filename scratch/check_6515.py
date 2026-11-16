import json

with open(r'C:\Users\Abhinav\.gemini\antigravity\brain\44e72ab9-3bd0-4ded-96fa-40285707e196\.system_generated\logs\transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for idx in (6515, 6517):
        f.seek(0)
        for i, line in enumerate(f):
            if i == idx:
                obj = json.loads(line)
                print(f'=== Step {idx} ===')
                print(obj.get('content', '')[:1000])
