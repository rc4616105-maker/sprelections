with open('Houses/admin/supabase-config.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('auditLogs: auditRows.map')
print(text[idx-400:idx])
