import os
import re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent

# 1. Verify all 10 real symbol images
SYMBOLS = ["torch", "shield", "rising_sun", "book", "star", "trophy", "tree", "bell", "compass", "rocket"]
SYM_DIR = ROOT / "Houses" / "assets" / "symbols"
print(f"Checking symbols in {SYM_DIR}...")
for s in SYMBOLS:
    p = SYM_DIR / f"{s}.png"
    if not p.exists():
        print(f"MISSING: {p}")
    else:
        im = Image.open(p)
        print(f"  OK: {s}.png ({im.size}, {p.stat().st_size // 1024} KB)")

# Also copy to Result declaration/assets/symbols
RES_SYM_DIR = ROOT / "Result declaration" / "assets" / "symbols"
RES_SYM_DIR.mkdir(parents=True, exist_ok=True)
for s in SYMBOLS:
    p = SYM_DIR / f"{s}.png"
    if p.exists():
        dest = RES_SYM_DIR / f"{s}.png"
        dest.write_bytes(p.read_bytes())
        dest_jpg = RES_SYM_DIR / f"{s}.jpg"
        src_jpg = SYM_DIR / f"{s}.jpg"
        if src_jpg.exists():
            dest_jpg.write_bytes(src_jpg.read_bytes())

# 2. Update CSS in all House styles.css
HOUSES = ["bheeshma", "gurudrona", "hanuman", "karna", "vasistha", "vishwamithra", "central", "teachers"]

CSS_BLOCK = """
/* EVM Candidate Symbol Box (Between Candidate Photo and Candidate Name) */
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
  gap: 4px;
  margin-right: 1.35rem;
  flex-shrink: 0;
  padding: 6px;
  box-sizing: border-box;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.06);
}

.evm-cand-symbol .evm-symbol-img {
  width: 58px;
  height: 58px;
  object-fit: cover;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.12);
}

.evm-cand-symbol .evm-symbol-fallback {
  font-size: 2rem;
  line-height: 1;
}

.evm-cand-symbol .evm-symbol-caption {
  font-size: 0.70rem;
  font-weight: 800;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 84px;
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
  padding: 4px;
  box-sizing: border-box;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

.evm-review-cand-symbol .evm-symbol-img-sm {
  width: 46px;
  height: 46px;
  object-fit: cover;
  border-radius: 6px;
}
"""

for h in HOUSES:
    css_file = ROOT / "Houses" / h / "styles.css"
    if not css_file.exists():
        continue
    content = css_file.read_text(encoding="utf-8")
    
    # Replace existing .evm-cand-symbol section or append
    if ".evm-cand-symbol {" in content:
        # Replace the block from /* EVM Candidate Symbol Box to .evm-review-cand-symbol .evm-symbol-img-sm { ... }
        pattern = r"/\*\s*EVM Candidate Symbol Box[\s\S]*?\.evm-review-cand-symbol \.evm-symbol-img-sm\s*\{[^}]*\}"
        if re.search(pattern, content):
            new_content = re.sub(pattern, CSS_BLOCK.strip(), content)
            css_file.write_text(new_content, encoding="utf-8")
            print(f"Updated CSS in {css_file.relative_to(ROOT)}")
        else:
            # Fallback replace
            sub_pat = r"\.evm-cand-symbol\s*\{[\s\S]*?\.evm-review-cand-symbol \.evm-symbol-img-sm\s*\{[^}]*\}"
            if re.search(sub_pat, content):
                new_content = re.sub(sub_pat, CSS_BLOCK.strip(), content)
                css_file.write_text(new_content, encoding="utf-8")
                print(f"Updated CSS (sub-pat) in {css_file.relative_to(ROOT)}")
            else:
                css_file.write_text(content + "\n" + CSS_BLOCK, encoding="utf-8")
                print(f"Appended CSS in {css_file.relative_to(ROOT)}")
    else:
        css_file.write_text(content + "\n" + CSS_BLOCK, encoding="utf-8")
        print(f"Appended CSS in {css_file.relative_to(ROOT)}")

# 3. Update app.js across houses to append cachebuster to symbol image URLs
for h in HOUSES:
    app_file = ROOT / "Houses" / h / "app.js"
    if not app_file.exists():
        continue
    code = app_file.read_text(encoding="utf-8")
    
    # 1: symImg cachebuster
    old_sym_img = "const symImg = sym.image || sym.imagePath || `../assets/symbols/${symSlug}.png`;"
    new_sym_img = "const symImg = (sym.image || sym.imagePath || `../assets/symbols/${symSlug}.png`) + '?v=20261122b';"
    if old_sym_img in code:
        code = code.replace(old_sym_img, new_sym_img)
    elif "const symImg =" in code and "?v=20261122b" not in code:
        code = re.sub(r"const symImg = [^;\n]+;", new_sym_img, code)

    # 2: pickedSymImg cachebuster in review
    old_picked = 'const pickedSymImg = pickedSym && pickedSymSlug ? (pickedSym.image || pickedSym.imagePath || `../assets/symbols/${pickedSymSlug}.png`) : "";'
    new_picked = 'const pickedSymImg = pickedSym && pickedSymSlug ? ((pickedSym.image || pickedSym.imagePath || `../assets/symbols/${pickedSymSlug}.png`) + "?v=20261122b") : "";'
    if old_picked in code:
        code = code.replace(old_picked, new_picked)
    elif "const pickedSymImg =" in code and "?v=20261122b" not in code:
        code = re.sub(r"const pickedSymImg = [^;\n]+;", new_picked, code)

    app_file.write_text(code, encoding="utf-8")
    print(f"Updated app.js cachebusters in {app_file.relative_to(ROOT)}")

# 4. Bump cachebuster query params in all index.html files
for h in HOUSES:
    html_file = ROOT / "Houses" / h / "index.html"
    if not html_file.exists():
        continue
    html = html_file.read_text(encoding="utf-8")
    
    # styles.css
    html = re.sub(r'href="\./styles\.css(\?v=[^"]*)?"', 'href="./styles.css?v=20261122b"', html)
    # data.js
    html = re.sub(r'src="\./data\.js(\?v=[^"]*)?"', 'src="./data.js?v=20261122b"', html)
    # supabase-config.js
    html = re.sub(r'src="\./supabase-config\.js(\?v=[^"]*)?"', 'src="./supabase-config.js?v=20261122b"', html)
    # app.js
    html = re.sub(r'src="\./app\.js(\?v=[^"]*)?"', 'src="./app.js?v=20261122b"', html)
    
    html_file.write_text(html, encoding="utf-8")
    print(f"Bumped version to v=20261122b in {html_file.relative_to(ROOT)}")

print("\nDone! All real symbol assets, CSS, and cachebusters applied successfully.")
