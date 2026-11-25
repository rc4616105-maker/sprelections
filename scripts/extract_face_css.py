with open('Houses/vasistha/styles.css', 'r', encoding='utf-8') as f:
    text = f.read()

start_idx = text.find('.face-modal-card')
end_idx = text.find('/* --- Responsive', start_idx)
if end_idx == -1:
    end_idx = text.find('@media', start_idx + 1000)

print(text[start_idx:start_idx+3000])
