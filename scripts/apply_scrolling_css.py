import re

css_files = [
    'Houses/bheeshma/styles.css',
    'Houses/gurudrona/styles.css',
    'Houses/hanuman/styles.css',
    'Houses/karna/styles.css',
    'Houses/vasistha/styles.css',
    'Houses/vishwamithra/styles.css',
    'Houses/teachers/styles.css',
]

scroll_improvements = """
/* ==========================================================================
   SCROLLING & VIEWPORT ADAPTABILITY ENHANCEMENTS (All Kiosks)
   ========================================================================== */
.page-shell.evm-active {
  max-width: 1180px;
  width: 100%;
  min-height: 100svh;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 0.85rem 1.5rem 1rem;
}

.page-shell.evm-active .booth-card {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 0.95rem 1.65rem 0.95rem;
  overflow: visible;
}

/* EVM Candidate List (Smooth vertical scroll for any number of candidates) */
.evm-candidate-list {
  flex: 1;
  min-height: 0;
  max-height: 60vh;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  gap: 0.75rem;
  margin: 0.65rem 0;
  overflow-y: auto !important;
  overflow-x: hidden;
  padding-right: 0.45rem;
  padding-bottom: 0.5rem;
  -webkit-overflow-scrolling: touch;
  scroll-behavior: smooth;
  scrollbar-width: thin;
  scrollbar-color: var(--house-accent, #2563eb) rgba(0, 0, 0, 0.08);
}

.evm-candidate-list::-webkit-scrollbar {
  width: 8px;
}
.evm-candidate-list::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.04);
  border-radius: 6px;
}
.evm-candidate-list::-webkit-scrollbar-thumb {
  background: var(--house-accent, #2563eb);
  border-radius: 6px;
}

.evm-candidate-row {
  flex-shrink: 0;
  min-height: 88px;
  max-height: 140px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.85rem 1.6rem;
  background: var(--bg-card);
  border: 2px solid var(--border-default);
  border-radius: 16px;
  cursor: pointer;
  user-select: none;
  transition: background-color 140ms ease, border-color 140ms ease, box-shadow 140ms ease, transform 120ms ease;
}

.evm-review-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 0.85rem;
  margin: 0.85rem 0;
  flex: 1;
  max-height: 58vh;
  overflow-y: auto !important;
  padding-right: 0.35rem;
  scrollbar-width: thin;
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

for cf in css_files:
    with open(cf, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if scroll_improvements already appended
    if 'SCROLLING & VIEWPORT ADAPTABILITY ENHANCEMENTS' not in content:
        content = content + "\n\n" + scroll_improvements
        with open(cf, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Appended scrolling rules to {cf}")
    else:
        print(f"Already updated {cf}")
