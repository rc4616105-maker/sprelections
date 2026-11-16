with open('Houses/admin/edit-votes.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('ballots-table')
print(text[idx-50:idx+800])
