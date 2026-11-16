with open('Houses/admin/edit-votes.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('loadStudentEditor')
print(text[idx:idx+1500])
