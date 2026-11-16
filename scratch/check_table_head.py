with open('Houses/admin/edit-votes.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if '<table class="ballots-table">' in l:
        print(''.join(lines[max(0, i-5):min(len(lines), i+25)]))
        break
