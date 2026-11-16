import json

with open(r'C:\Users\Abhinav\.gemini\antigravity\brain\44e72ab9-3bd0-4ded-96fa-40285707e196\.system_generated\logs\transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f):
        if idx in range(6220, 6275):
            obj = json.loads(line)
            c = str(obj.get('content', ''))
            if 'populateBoothFilter' in c:
                print('Found in step', idx, 'length:', len(c))
                with open('recovered_app_part.txt', 'w', encoding='utf-8') as out:
                    out.write(c)
                print('Saved to recovered_app_part.txt!')
