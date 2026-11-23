import os
import re

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
    html_path = os.path.join(b, 'index.html')
    js_path = os.path.join(b, 'app.js')
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    has_manual_active = 'id="tab-manual-mode" class="auth-tab active"' in html or 'id="tab-manual-mode" class="auth-tab is-active"' in html or 'class="auth-tab active" id="tab-manual-mode"' in html
    manual_hidden = 'id="pane-manual-entry" class="auth-pane" hidden' in html
    barcode_hidden = 'id="pane-barcode-scan" class="auth-pane" hidden' in html
    
    print(f"=== {b} ===")
    print(f"  Manual tab active: {has_manual_active}")
    print(f"  Manual pane hidden: {manual_hidden}")
    print(f"  Barcode pane hidden: {barcode_hidden}")
    
    # check input label and placeholder
    m_label = re.search(r'<label for="admission-input"[^>]*>(.*?)</label>', html, re.DOTALL)
    if m_label:
        clean_lbl = re.sub(r'<[^>]+>', ' ', m_label.group(1)).strip()
        print(f"  Label: {clean_lbl}")
    m_inp = re.search(r'<input id="admission-input"[^>]*placeholder="([^"]+)"', html)
    if m_inp:
        print(f"  Placeholder: {m_inp.group(1)}")
    
    with open(js_path, 'r', encoding='utf-8') as f:
        js = f.read()
    mode_scan = 'mode: "scan"' in js or "mode: 'scan'" in js
    mode_manual = 'mode: "manual"' in js or "mode: 'manual'" in js
    print(f"  JS mode scan: {mode_scan}, manual: {mode_manual}")
