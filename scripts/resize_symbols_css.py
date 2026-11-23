import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOUSES = ["bheeshma", "gurudrona", "hanuman", "karna", "vasistha", "vishwamithra", "central", "teachers"]

CSS_BLOCK = """/* EVM Candidate Symbol Box (Between Candidate Photo and Candidate Name) */
.evm-cand-symbol {
  width: 96px;
  height: 96px;
  border-radius: 14px;
  background: #ffffff;
  border: 2px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  margin-right: 1.35rem;
  flex-shrink: 0;
  padding: 4px;
  box-sizing: border-box;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.06);
}

.evm-cand-symbol .evm-symbol-img {
  width: 70px;
  height: 70px;
  object-fit: cover;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.12);
}

.evm-cand-symbol .evm-symbol-fallback {
  font-size: 2.2rem;
  line-height: 1;
}

.evm-cand-symbol .evm-symbol-caption {
  font-size: 0.58rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 88px;
  line-height: 1.1;
  margin-top: 1px;
}

.evm-candidate-row.is-selected .evm-cand-symbol {
  background: #ffffff;
  border-color: #86efac;
  box-shadow: 0 3px 8px rgba(34, 197, 94, 0.15);
}

.evm-review-cand-symbol {
  width: 58px;
  height: 58px;
  border-radius: 12px;
  background: #ffffff;
  border: 1.5px solid #e2e8f0;
  display: grid;
  place-items: center;
  flex-shrink: 0;
  padding: 3px;
  box-sizing: border-box;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

.evm-review-cand-symbol .evm-symbol-img-sm {
  width: 50px;
  height: 50px;
  object-fit: cover;
  border-radius: 6px;
}"""

for h in HOUSES:
    css_file = ROOT / "Houses" / h / "styles.css"
    if css_file.exists():
        content = css_file.read_text(encoding="utf-8")
        pattern = r"/\*\s*EVM Candidate Symbol Box[\s\S]*?\.evm-review-cand-symbol \.evm-symbol-img-sm\s*\{[^}]*\}"
        if re.search(pattern, content):
            new_content = re.sub(pattern, CSS_BLOCK.strip(), content)
            css_file.write_text(new_content, encoding="utf-8")
            print(f"Updated {h} styles.css")
        else:
            print(f"Pattern not found in {h} styles.css")
    
    # Bump html cachebuster
    html_file = ROOT / "Houses" / h / "index.html"
    if html_file.exists():
        html = html_file.read_text(encoding="utf-8")
        html = re.sub(r'href="\./styles\.css(\?v=[^"]*)?"', 'href="./styles.css?v=20261122c"', html)
        html_file.write_text(html, encoding="utf-8")
        print(f"Bumped {h} index.html to v=20261122c")

print("All houses updated successfully!")
