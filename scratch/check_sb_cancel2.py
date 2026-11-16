with open('Houses/admin/supabase-config.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('async cancelBallot(')
idx2 = text.find('async updateBallotChoice(', idx)
print(text[idx:idx2])
