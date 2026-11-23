import os
import re
import json

errors = []

# 1. Check edit-votes.html
with open('Houses/admin/edit-votes.html', 'r', encoding='utf-8') as f:
    ev_html = f.read()

if '<option value="6">Class 6</option>' not in ev_html:
    errors.append("Class 6 missing in edit-votes.html")

if 'type-btn-faculty' not in ev_html or 'type-btn-student' not in ev_html:
    errors.append("Faculty switcher buttons missing in edit-votes.html")

# 2. Check edit-votes.js
with open('Houses/admin/edit-votes.js', 'r', encoding='utf-8') as f:
    ev_js = f.read()

if 'generateUniqueFacultyVoterId' not in ev_js:
    errors.append("generateUniqueFacultyVoterId missing in edit-votes.js")

if 'SPR' not in ev_js:
    errors.append("SPR prefix logic missing in edit-votes.js")

# 3. Check all 8 booths
booths = [
    'Houses/bheeshma',
    'Houses/gurudrona',
    'Houses/hanuman',
    'Houses/karna',
    'Houses/vasistha',
    'Houses/vishwamithra',
    'Houses/central',
    'Houses/teachers'
]

for b in booths:
    hpath = os.path.join(b, 'index.html')
    with open(hpath, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Check manual tab is active
    if 'id="tab-manual-mode"' not in html:
        errors.append(f"{b}: tab-manual-mode not found")
    elif 'class="voter-tab-btn is-active"' not in html and 'class="auth-tab active"' not in html:
        errors.append(f"{b}: tab-manual-mode is not active")
        
    # Check barcode pane is hidden
    if not re.search(r'<div[^>]*id="pane-barcode-scan"[^>]*\bhidden\b', html):
        errors.append(f"{b}: pane-barcode-scan is not hidden")
        
    # Check manual pane is NOT hidden
    if re.search(r'<div[^>]*id="pane-manual-entry"[^>]*\bhidden\b', html):
        errors.append(f"{b}: pane-manual-entry is hidden")
        
    # Check placeholder strictly Enter Voter ID
    if 'placeholder="Enter Voter ID"' not in html:
        errors.append(f"{b}: placeholder is not 'Enter Voter ID'")

# 4. Check Result declaration
with open('Result declaration/index.html', 'r', encoding='utf-8') as f:
    dec_html = f.read()

if 'wheel-mode-switcher' in dec_html:
    errors.append("Result declaration/index.html still has wheel-mode-switcher")

if 'nav-back-arrow' not in dec_html:
    errors.append("Back arrow missing in Result declaration/index.html")

with open('Result declaration/js/data.js', 'r', encoding='utf-8') as f:
    dec_data = f.read()

m_h = re.search(r'const DEFAULT_HOUSES = (\[.*?\]);\s*const DEFAULT_CABINET_POSTS = (\[.*?\]);', dec_data, re.DOTALL)
if m_h:
    h_list = json.loads(m_h.group(1))
    c_list = json.loads(m_h.group(2))
    for h in h_list:
        for k, cand in h['candidates'].items():
            if not cand.get('symbolName'):
                errors.append(f"House {h['id']} {k} missing symbolName")
            if not cand.get('photo') or 'student_boy' in cand['photo']:
                errors.append(f"House {h['id']} {k} has generic photo")
    for p in c_list:
        cand = p.get('candidate', {})
        if not cand.get('symbolName'):
            errors.append(f"Cabinet {p['id']} missing symbolName")
        if not cand.get('photo') or 'student_boy' in cand.get('photo', ''):
            errors.append(f"Cabinet {p['id']} has generic photo")
else:
    errors.append("Could not parse DEFAULT_HOUSES in Result declaration/js/data.js")

# 5. Check teachers data has SPRCOM820
with open('Houses/teachers/data.js', 'r', encoding='utf-8') as f:
    t_data = f.read()

if 'SPRCOM820' not in t_data:
    errors.append("SPRCOM820 missing in Houses/teachers/data.js")

if not errors:
    print("ALL VERIFICATION CHECKS PASSED PERFECTLY! 100% CLEAN.")
else:
    print(f"FAILED CHECKS ({len(errors)}):")
    for e in errors:
        print("  -", e)
