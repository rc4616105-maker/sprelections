import json

with open(r'C:\Users\Abhinav\.gemini\antigravity\brain\44e72ab9-3bd0-4ded-96fa-40285707e196\.system_generated\logs\transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for idx in (6526, 6527, 6588, 6589, 6650, 6651, 6652, 6653, 6662, 6663):
        f.seek(0)
        for i, line in enumerate(f):
            if i == idx:
                obj = json.loads(line)
                print(idx, obj.get('source'), obj.get('type'))
                if obj.get('tool_calls'):
                    print('  tc:', obj['tool_calls'][0]['name'], obj['tool_calls'][0]['args'])
                elif obj.get('content'):
                    print('  content prefix:', obj['content'][:120])
