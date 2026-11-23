import shutil

# 1. Update bheeshma/app.js
with open('Houses/bheeshma/app.js', 'r', encoding='utf-8') as f:
    app_text = f.read()

old_cand_html = '''              <div class="evm-review-card-left">
                <div class="evm-cand-avatar">${photoHtml}</div>
                ${symReviewHtml}
                <div>
                  <p class="evm-review-role-title">${pos.title}</p>
                  <h4 class="evm-review-cand-name" style="${!picked ? 'color:#dc2626;' : ''}">${picked ? picked.fullName : 'Not Selected'}</h4>
                  <p class="evm-review-cand-sub">${subText}</p>
                </div>
              </div>'''

new_cand_html = '''              <div class="evm-review-card-left">
                <div class="evm-cand-avatar">${photoHtml}</div>
                ${symReviewHtml}
                <div class="evm-review-cand-info">
                  <p class="evm-review-role-title">${pos.title}</p>
                  <h4 class="evm-review-cand-name" style="${!picked ? 'color:#dc2626;' : ''}">${picked ? picked.fullName : 'Not Selected'}</h4>
                  <p class="evm-review-cand-sub">${subText}</p>
                </div>
              </div>'''

if old_cand_html in app_text:
    app_text = app_text.replace(old_cand_html, new_cand_html)
    with open('Houses/bheeshma/app.js', 'w', encoding='utf-8') as f:
        f.write(app_text)
    print("Updated Houses/bheeshma/app.js with evm-review-cand-info!")
else:
    print("Warning: old_cand_html not found in Houses/bheeshma/app.js")

# Copy bheeshma/app.js to all other houses
for h in ['gurudrona', 'hanuman', 'karna', 'vasistha', 'vishwamithra']:
    target = f'Houses/{h}/app.js'
    shutil.copyfile('Houses/bheeshma/app.js', target)
    print(f"Synced app.js to {target}")

# 2. Update all styles.css files
css_files = [
    'Houses/bheeshma/styles.css',
    'Houses/gurudrona/styles.css',
    'Houses/hanuman/styles.css',
    'Houses/karna/styles.css',
    'Houses/vasistha/styles.css',
    'Houses/vishwamithra/styles.css',
    'Houses/teachers/styles.css',
]

review_css_patch = """
/* Review & Confirm 2-Column Balanced Grid & Non-Overlapping Change Button */
.evm-review-grid {
  display: grid !important;
  grid-template-columns: repeat(2, 1fr) !important;
  gap: 1.25rem !important;
  margin: 1.25rem 0 2rem !important;
  flex: none !important;
  height: auto !important;
  max-height: none !important;
  overflow: visible !important;
  padding-right: 0 !important;
}

@media (max-width: 820px) {
  .evm-review-grid {
    grid-template-columns: 1fr !important;
  }
}

.evm-review-grid::-webkit-scrollbar {
  display: none !important;
  width: 0 !important;
}

.evm-review-card {
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  padding: 1.1rem 1.35rem !important;
  background: var(--bg-surface) !important;
  border: 2px solid var(--border-default) !important;
  border-radius: var(--radius-xl) !important;
  gap: 1.25rem !important;
  position: relative !important;
  min-width: 0 !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03) !important;
  transition: border-color 140ms ease, box-shadow 140ms ease !important;
}

.evm-review-card:hover {
  border-color: var(--house-border-glow) !important;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06) !important;
}

.evm-review-card-left {
  display: flex !important;
  align-items: center !important;
  gap: 0.95rem !important;
  flex: 1 1 auto !important;
  min-width: 0 !important;
  overflow: hidden !important;
}

.evm-review-cand-info {
  flex: 1 1 auto !important;
  min-width: 0 !important;
  overflow: hidden !important;
}

.evm-review-role-title {
  font-size: 0.76rem !important;
  text-transform: uppercase !important;
  font-weight: 800 !important;
  letter-spacing: 0.06em !important;
  color: var(--text-muted) !important;
  margin: 0 0 0.2rem !important;
}

.evm-review-cand-name {
  font-size: 1.2rem !important;
  font-weight: 800 !important;
  color: var(--text-primary) !important;
  margin: 0 !important;
  white-space: normal !important;
  word-break: break-word !important;
  line-height: 1.25 !important;
}

.evm-review-cand-sub {
  font-size: 0.85rem !important;
  color: var(--text-secondary) !important;
  margin: 0.2rem 0 0 !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

.evm-review-change-btn {
  flex-shrink: 0 !important;
  margin-left: auto !important;
  background: #ffffff !important;
  border: 1.5px solid var(--border-default) !important;
  border-radius: var(--radius-full) !important;
  padding: 0.45rem 1.15rem !important;
  font-family: inherit !important;
  font-size: 0.82rem !important;
  font-weight: 700 !important;
  color: var(--house-accent-text, #925c04) !important;
  cursor: pointer !important;
  white-space: nowrap !important;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05) !important;
  transition: all 140ms ease !important;
}

.evm-review-change-btn:hover {
  background: var(--house-subtle) !important;
  border-color: var(--house-accent) !important;
  transform: translateY(-1px) scale(1.02) !important;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08) !important;
}
"""

for cf in css_files:
    with open(cf, 'r', encoding='utf-8') as f:
        c_text = f.read()
    
    # replace existing .evm-review-grid definition in bottom section if present
    marker = '/* Review & Confirm 2-Column Balanced Grid'
    idx = c_text.find(marker)
    if idx != -1:
        c_text = c_text[:idx] + review_css_patch.strip()
    else:
        c_text = c_text + "\n\n" + review_css_patch.strip()
        
    with open(cf, 'w', encoding='utf-8') as f:
        f.write(c_text)
    print(f"Applied review card layout fix to {cf}")
