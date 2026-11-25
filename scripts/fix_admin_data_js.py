import re
import json

with open('Houses/admin/data.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's search for patterns like:
#     "isApproved": true
#   },
#   "photoUrl": ...
#   "isApproved": true
# },

pattern = r'(\s*\"isApproved\":\s*true\s*\n\s*\},)\s*\"photoUrl\":[^\n]*\n\s*\"photoPath\":[^\n]*\n\s*\"isApproved\":\s*true\s*\n\s*\},'

matches = list(re.finditer(pattern, content))
print(f"Found {len(matches)} duplicate photo blocks in admin/data.js")

cleaned = re.sub(pattern, r'\1', content)

# Check if JSON parses now
match = re.search(r'=\s*(\{.*\}|\[.*\])\s*;?\s*$', cleaned, re.DOTALL)
if match:
    try:
        data = json.loads(match.group(1).strip())
        print("SUCCESS! admin/data.js parses perfectly as JSON!")
        with open('Houses/admin/data.js', 'w', encoding='utf-8') as f:
            f.write(cleaned)
        print("Updated Houses/admin/data.js successfully!")
    except json.JSONDecodeError as e:
        print(f"Still JSON error: {e}")
        # print around the error
        err_char = e.pos
        start = max(0, err_char - 200)
        end = min(len(match.group(1)), err_char + 200)
        print("Context around error:")
        print(match.group(1)[start:end])
