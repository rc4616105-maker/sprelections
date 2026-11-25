with open('Houses/admin/supabase-config.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('const baseRoster =')
print(text[idx-400:idx])
