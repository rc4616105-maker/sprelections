import re

with open('Houses/central/data.js', 'r', encoding='utf-8') as f:
    c = f.read()

cands = re.findall(r'"id":\s*"(CAND_CENTRAL_[^"]+)"', c)
print('Central candidates count in central/data.js:', len(cands))
admissions = re.findall(r'"admissionNo":\s*"([^"]+)"', c)
print('Admissions in central/data.js:', len(admissions), admissions[:15])

with open('Houses/assets/all-candidates.js', 'r', encoding='utf-8') as f:
    c_all = f.read()
cab_cands = re.findall(r'CAND_CENTRAL_[A-Z_0-9]+', c_all)
print('Central candidates count in all-candidates.js:', len(set(cab_cands)))
