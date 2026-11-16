import json

with open(r'C:\Users\Abhinav\.gemini\antigravity\brain\44e72ab9-3bd0-4ded-96fa-40285707e196\.system_generated\logs\transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f):
        if idx in (6224, 6264, 6404, 6469):
            obj = json.loads(line)
            # Find the file content if this was a read_file response in next step
            print('Idx:', idx)
