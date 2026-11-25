with open('Houses/admin/supabase-config.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('async getSnapshot()')
idx2 = text.find('candidates:', idx)
print(text[idx2-100:idx2+400])
