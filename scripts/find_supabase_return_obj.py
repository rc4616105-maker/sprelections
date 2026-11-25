with open('Houses/admin/supabase-config.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('async getSnapshot()')
idx_else = text.find('} else {', idx)
print(text[idx_else-500:idx_else+100])
