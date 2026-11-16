import json

with open(r'C:\Users\Abhinav\.gemini\antigravity\brain\44e72ab9-3bd0-4ded-96fa-40285707e196\.system_generated\logs\transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f):
        if idx == 6704:
            obj = json.loads(line)
            # Find in obj where Cancelled Ballots appears
            def find_text(val):
                if isinstance(val, str) and 'Cancelled Ballots' in val:
                    return val
                elif isinstance(val, dict):
                    for v in val.values():
                        res = find_text(v)
                        if res: return res
                elif isinstance(val, list):
                    for item in val:
                        res = find_text(item)
                        if res: return res
                return None
            res = find_text(obj)
            if res:
                with open('cancelled_res.txt', 'w', encoding='utf-8') as out:
                    out.write(res)
                print('Saved to cancelled_res.txt! Length:', len(res))
