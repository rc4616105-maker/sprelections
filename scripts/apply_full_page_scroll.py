css_files = [
    'Houses/bheeshma/styles.css',
    'Houses/gurudrona/styles.css',
    'Houses/hanuman/styles.css',
    'Houses/karna/styles.css',
    'Houses/vasistha/styles.css',
    'Houses/vishwamithra/styles.css',
    'Houses/teachers/styles.css',
]

full_page_scroll_css = """/* ==========================================================================
   FULL PAGE NATURAL SCROLLING (NO INNER SCROLL BOXES)
   ========================================================================== */
html, body {
  height: auto !important;
  min-height: 100% !important;
  overflow-y: auto !important;
  overflow-x: hidden !important;
  scroll-behavior: smooth;
}

.page-shell,
.page-shell.evm-active {
  height: auto !important;
  min-height: 100vh !important;
  max-width: 1180px;
  width: 100%;
  display: flex !important;
  flex-direction: column !important;
  justify-content: flex-start !important;
  overflow: visible !important;
  padding: 1.25rem 1.5rem 3.5rem !important;
}

.page-shell.evm-active .booth-main {
  flex: none !important;
  height: auto !important;
  min-height: auto !important;
  overflow: visible !important;
  display: block !important;
}

.page-shell.evm-active .booth-card {
  flex: none !important;
  height: auto !important;
  min-height: auto !important;
  overflow: visible !important;
  padding: clamp(1.25rem, 2.5vw, 1.85rem) !important;
}

.evm-ballot-view,
.evm-review-view {
  flex: none !important;
  height: auto !important;
  min-height: auto !important;
  overflow: visible !important;
  display: flex !important;
  flex-direction: column !important;
}

/* All Candidates are naturally rendered without inner scroll boxes */
.evm-candidate-list {
  flex: none !important;
  height: auto !important;
  min-height: auto !important;
  max-height: none !important;
  overflow: visible !important;
  overflow-y: visible !important;
  overflow-x: visible !important;
  padding-right: 0 !important;
  padding-bottom: 0 !important;
  display: flex !important;
  flex-direction: column !important;
  gap: 0.85rem !important;
  margin: 1rem 0 1.5rem !important;
}

.evm-candidate-list::-webkit-scrollbar {
  display: none !important;
  width: 0 !important;
}

.evm-candidate-row {
  flex: none !important;
  flex-shrink: 0 !important;
  min-height: 88px !important;
  max-height: none !important;
  height: auto !important;
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  padding: 0.95rem 1.6rem !important;
  background: var(--bg-card);
  border: 2px solid var(--border-default);
  border-radius: 16px;
  cursor: pointer;
  user-select: none;
  transition: background-color 140ms ease, border-color 140ms ease, box-shadow 140ms ease, transform 120ms ease;
}

.evm-review-grid {
  display: grid !important;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)) !important;
  gap: 0.85rem !important;
  margin: 1rem 0 1.5rem !important;
  flex: none !important;
  height: auto !important;
  max-height: none !important;
  overflow: visible !important;
  padding-right: 0 !important;
}

.evm-review-grid::-webkit-scrollbar {
  display: none !important;
  width: 0 !important;
}

/* Fixed/Sticky Bottom Kiosk Action Bar so 'Next Post' is always immediately accessible as page scrolls */
.evm-kiosk-footer {
  position: sticky !important;
  bottom: 0.75rem !important;
  background: var(--bg-card) !important;
  border: 1.5px solid var(--border-default) !important;
  border-radius: var(--radius-lg) !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08) !important;
  padding: 0.85rem 1.25rem !important;
  margin-top: 1rem !important;
  z-index: 20 !important;
}

.cloud-status-note {
  margin-top: 0.85rem;
  font-size: 0.82rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  text-align: center;
  line-height: 1.4;
  transition: color 200ms ease;
}

.cloud-status-note.is-connected {
  color: #15803d;
}

.cloud-status-note.is-disconnected {
  color: #b91c1c;
}
"""

marker = '/* ==========================================================================\n   SCROLLING & VIEWPORT ADAPTABILITY ENHANCEMENTS'

for cf in css_files:
    with open(cf, 'r', encoding='utf-8') as f:
        text = f.read()
    
    idx = text.find(marker)
    if idx != -1:
        text = text[:idx] + full_page_scroll_css
    else:
        alt_marker = '/* ==========================================================================\n   FULL PAGE NATURAL SCROLLING'
        alt_idx = text.find(alt_marker)
        if alt_idx != -1:
            text = text[:alt_idx] + full_page_scroll_css
        else:
            text = text + "\n\n" + full_page_scroll_css
            
    with open(cf, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"Updated full-page scrolling in {cf}")
