with open('Houses/admin/supabase-config.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('async getSnapshot()')
# find return statement of supabase mode
idx_ret = text.find('return {', idx)
print(text[idx_ret:idx_ret+800])
