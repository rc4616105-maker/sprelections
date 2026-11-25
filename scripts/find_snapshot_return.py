with open('Houses/admin/supabase-config.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('async getSnapshot()')
# find return statement at the end of getSnapshot
idx_end = text.find('async ', idx + 50)
print(text[idx_end-800:idx_end])
