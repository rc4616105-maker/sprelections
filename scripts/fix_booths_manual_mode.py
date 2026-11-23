import os
import re

app_files = [
    'Houses/bheeshma/app.js',
    'Houses/gurudrona/app.js',
    'Houses/hanuman/app.js',
    'Houses/karna/app.js',
    'Houses/vasistha/app.js',
    'Houses/vishwamithra/app.js',
    'Houses/central/app.js'
]

for p in app_files:
    with open(p, 'r', encoding='utf-8') as f:
        js = f.read()

    # Change scannerState initial mode to "manual"
    js = re.sub(
        r'mode:\s*localStorage\.getItem\("election_voter_input_mode"\)\s*\|\|\s*"(?:scan|manual)"',
        'mode: "manual"',
        js
    )
    # Ensure setInputMode defaults to manual on load
    js = re.sub(
        r'setInputMode\(scannerState\.mode\s*\|\|\s*"scan"\)',
        'setInputMode("manual")',
        js
    )
    with open(p, 'w', encoding='utf-8') as f:
        f.write(js)
    print(f"Updated {p}")

# Also update teachers/app.js
teachers_app = 'Houses/teachers/app.js'
with open(teachers_app, 'r', encoding='utf-8') as f:
    tjs = f.read()

# Make sure teachers/app.js activates manual entry in initEvents and resetToNewVoter
if 'el.tabManualMode?.classList.add("is-active")' not in tjs:
    tjs = tjs.replace(
        'setStep(1);',
        'if (el.tabManualMode && el.tabScanMode && el.paneBarcodeScan && el.paneManualEntry) {\n      el.tabManualMode.classList.add("is-active");\n      el.tabScanMode.classList.remove("is-active");\n      el.paneBarcodeScan.hidden = true;\n      el.paneManualEntry.hidden = false;\n    }\n    setStep(1);'
    )
    with open(teachers_app, 'w', encoding='utf-8') as f:
        f.write(tjs)
    print(f"Updated {teachers_app}")
