with open('Houses/teachers/app.js', 'r', encoding='utf-8') as f:
    t_app = f.read()

import re
matches = re.findall(r'.{0,50}(?:castVote|submitVote|submitBallot|recordVote|finalSubmit|confirmVote).{0,50}', t_app, re.I)
print(f"Found {len(matches)} matches in teachers/app.js:")
for m in matches[:10]:
    print(' ', m.strip().replace('\n', ' '))
