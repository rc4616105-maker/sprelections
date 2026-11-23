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
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Update Tabs: make scan mode inactive, manual mode active
    # For house booths using voter-tab-btn:
    html = re.sub(
        r'<button([^>]*id="tab-scan-mode"[^>]*)class="([^"]*)\bis-active\b([^"]*)"',
        r'<button\1class="\2\3"',
        html
    )
    html = re.sub(
        r'<button([^>]*id="tab-scan-mode"[^>]*)aria-selected="true"',
        r'<button\1aria-selected="false"',
        html
    )
    # If tab-manual-mode doesn't have is-active or active:
    def activate_manual(m):
        btn = m.group(0)
        btn = re.sub(r'aria-selected="false"', 'aria-selected="true"', btn)
        if 'voter-tab-btn' in btn and 'is-active' not in btn:
            btn = btn.replace('class="voter-tab-btn', 'class="voter-tab-btn is-active')
        elif 'auth-tab' in btn and 'active' not in btn:
            btn = btn.replace('class="auth-tab', 'class="auth-tab active')
        return btn
    html = re.sub(r'<button[^>]*id="tab-manual-mode"[^>]*>', activate_manual, html)

    # For teachers/central using auth-tab:
    html = re.sub(
        r'<button([^>]*id="tab-scan-mode"[^>]*)class="([^"]*)\bactive\b([^"]*)"',
        r'<button\1class="\2\3"',
        html
    )

    # 2. Update Panes: pane-barcode-scan hidden, pane-manual-entry visible & active
    def fix_barcode_pane(m):
        tag = m.group(0)
        if 'hidden' not in tag:
            tag = tag.rstrip('>') + ' hidden>'
        tag = tag.replace('is-active', '').replace('  ', ' ')
        return tag
    html = re.sub(r'<div[^>]*id="pane-barcode-scan"[^>]*>', fix_barcode_pane, html)

    def fix_manual_pane(m):
        tag = m.group(0)
        tag = re.sub(r'\bhidden\b', '', tag)
        if 'is-active' not in tag:
            tag = tag.replace('class="auth-pane', 'class="auth-pane is-active')
        tag = re.sub(r'\s+', ' ', tag).replace(' >', '>')
        return tag
    html = re.sub(r'<div[^>]*id="pane-manual-entry"[^>]*>', fix_manual_pane, html)

    # 3. Label & Placeholder strictly 'Enter Voter ID'
    html = re.sub(
        r'<label for="admission-input"[^>]*>.*?</label>',
        '<label for="admission-input" class="form-label">\n                  <span>Enter Voter ID</span>\n                </label>',
        html,
        flags=re.DOTALL
    )
    html = re.sub(
        r'(<input[^>]*id="admission-input"[^>]*?)placeholder="[^"]*"',
        r'\1placeholder="Enter Voter ID"',
        html
    )

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Updated {html_path}")

print("All booths updated successfully.")
