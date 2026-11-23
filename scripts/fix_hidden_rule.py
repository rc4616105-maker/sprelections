css_files = [
    'Houses/bheeshma/styles.css',
    'Houses/gurudrona/styles.css',
    'Houses/hanuman/styles.css',
    'Houses/karna/styles.css',
    'Houses/vasistha/styles.css',
    'Houses/vishwamithra/styles.css',
    'Houses/teachers/styles.css',
]

old_rule = """.evm-ballot-view,
.evm-review-view {
  flex: none !important;
  height: auto !important;
  min-height: auto !important;
  overflow: visible !important;
  display: flex !important;
  flex-direction: column !important;
}"""

new_rule = """/* Strictly enforce hidden state for step panels and EVM views */
[hidden],
.evm-ballot-view[hidden],
.evm-review-view[hidden],
.step-panel[hidden] {
  display: none !important;
}

.evm-ballot-view:not([hidden]),
.evm-review-view:not([hidden]) {
  flex: none !important;
  height: auto !important;
  min-height: auto !important;
  overflow: visible !important;
  display: flex !important;
  flex-direction: column !important;
}"""

for cf in css_files:
    with open(cf, 'r', encoding='utf-8') as f:
        text = f.read()
    
    if old_rule in text:
        text = text.replace(old_rule, new_rule)
        with open(cf, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Fixed hidden enforcement in {cf}")
    else:
        print(f"Warning: old_rule not found in {cf}")
