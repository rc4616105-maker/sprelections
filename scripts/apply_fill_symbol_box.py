import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOUSES = ["bheeshma", "gurudrona", "hanuman", "karna", "vasistha", "vishwamithra", "central", "teachers"]

CSS_BLOCK = """/* EVM Candidate Symbol Box (Between Candidate Photo and Candidate Name) */
.evm-cand-symbol {
  width: 96px;
  height: 96px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;
  margin-right: 1.35rem;
  flex-shrink: 0;
  box-sizing: border-box;
}

.evm-cand-symbol .evm-symbol-box {
  width: 76px;
  height: 76px;
  border-radius: 12px;
  background: #ffffff;
  border: 2px solid #e2e8f0;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
  flex-shrink: 0;
}

.evm-cand-symbol .evm-symbol-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.evm-cand-symbol .evm-symbol-fallback {
  font-size: 2.2rem;
  line-height: 1;
}

.evm-cand-symbol .evm-symbol-caption {
  font-size: 0.58rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 96px;
  line-height: 1.1;
  margin: 0;
  padding: 0 2px;
}

.evm-candidate-row.is-selected .evm-cand-symbol .evm-symbol-box {
  border-color: #86efac;
  box-shadow: 0 3px 8px rgba(34, 197, 94, 0.2);
}

.evm-review-cand-symbol {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  flex-shrink: 0;
  margin-right: 0.5rem;
}

.evm-review-cand-symbol .evm-symbol-box-sm {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  background: #ffffff;
  border: 1.5px solid #e2e8f0;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  box-sizing: border-box;
}

.evm-review-cand-symbol .evm-symbol-img-sm {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.evm-review-cand-symbol .evm-symbol-caption-sm {
  font-size: 0.50rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 58px;
}"""

for h in HOUSES:
    # 1. Update CSS
    css_file = ROOT / "Houses" / h / "styles.css"
    if css_file.exists():
        content = css_file.read_text(encoding="utf-8")
        pattern = r"/\*\s*EVM Candidate Symbol Box[\s\S]*?\.evm-review-cand-symbol \.evm-symbol-img-sm\s*\{[^}]*\}"
        if re.search(pattern, content):
            new_content = re.sub(pattern, CSS_BLOCK.strip(), content)
            css_file.write_text(new_content, encoding="utf-8")
            print(f"Updated {h} styles.css")
        else:
            print(f"CSS pattern not found in {h} styles.css")

    # 2. Update app.js
    app_file = ROOT / "Houses" / h / "app.js"
    if app_file.exists():
        code = app_file.read_text(encoding="utf-8")
        
        # Replace candidate row symbol HTML
        old_row_symbol = re.search(r'<div class="evm-cand-symbol"[^>]*>[\s\S]*?</div>\s*<div class="evm-cand-info">', code)
        if old_row_symbol:
            new_row_symbol_html = """<div class="evm-cand-symbol" title="Election Symbol: ${sym.name}">
                <div class="evm-symbol-box">
                  <img src="${symImg}" alt="${sym.name}" class="evm-symbol-img" onerror="this.style.display='none';this.nextElementSibling.style.display='inline-block';" />
                  <span class="evm-symbol-fallback" style="display:none;">${sym.icon || "⭐"}</span>
                </div>
                <span class="evm-symbol-caption">${sym.name}</span>
              </div>
              <div class="evm-cand-info">"""
            code = code[:old_row_symbol.start()] + new_row_symbol_html + code[old_row_symbol.end():]

        # Replace review card symbol HTML
        old_review_sym = re.search(r'const symReviewHtml = pickedSym && pickedSym\.name\s*\? `[^`]*`\s*: "";', code)
        if old_review_sym:
            new_review_sym_code = """const symReviewHtml = pickedSym && pickedSym.name
              ? `<div class="evm-review-cand-symbol" title="Symbol: ${pickedSym.name}"><div class="evm-symbol-box-sm"><img src="${pickedSymImg}" alt="${pickedSym.name}" class="evm-symbol-img-sm" onerror="this.style.display='none';this.nextElementSibling.style.display='inline-block';" /><span class="evm-symbol-fallback-sm" style="display:none;">${pickedSym.icon || "⭐"}</span></div><span class="evm-symbol-caption-sm">${pickedSym.name}</span></div>`
              : "";"""
            code = code[:old_review_sym.start()] + new_review_sym_code + code[old_review_sym.end():]

        # Ensure cachebuster query param on symImg
        code = re.sub(r'\?v=20261122[a-z]?', '?v=20261122d', code)
        app_file.write_text(code, encoding="utf-8")
        print(f"Updated {h} app.js")

    # 3. Bump HTML version
    html_file = ROOT / "Houses" / h / "index.html"
    if html_file.exists():
        html = html_file.read_text(encoding="utf-8")
        html = re.sub(r'(\./styles\.css\?v=)[^"]*', r'\g<1>20261122d', html)
        html = re.sub(r'(\./app\.js\?v=)[^"]*', r'\g<1>20261122d', html)
        html = re.sub(r'(\./data\.js\?v=)[^"]*', r'\g<1>20261122d', html)
        html = re.sub(r'(\./supabase-config\.js\?v=)[^"]*', r'\g<1>20261122d', html)
        html_file.write_text(html, encoding="utf-8")
        print(f"Bumped {h} index.html to v=20261122d")

print("\nSuccessfully applied white symbol box fill and small caption across all houses!")
