"""
Batch update script to apply:
1. Reordered Candidate Ballot Row: [Candidate Photo] -> [Symbol Photo] -> [Candidate Name & Details] -> [LED / Vote Button]
2. Step 4 Review with Candidate Photo + Symbol Graphic
3. CSS styles for .evm-cand-symbol and .evm-review-cand-symbol
4. Demo voter ID: 1C8492 (Class 10-CS) across all houses and configs
5. Cachebuster bumps across all HTML files
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent

NEW_ROW_HTML = """            const sym = cand.symbolObj || { name: "Candidate Choice", icon: "⭐" };
            const symSlug = (sym.slug || sym.name || "star").toLowerCase().replace(/[\\s-]+/g, "_");
            const symImg = sym.image || sym.imagePath || `../assets/symbols/${symSlug}.png`;

            row.innerHTML = `
              <div class="evm-cand-avatar">${photoHtml}</div>
              <div class="evm-cand-symbol" title="Election Symbol: ${sym.name}">
                <img src="${symImg}" alt="${sym.name}" class="evm-symbol-img" onerror="this.style.display='none';this.nextElementSibling.style.display='inline-block';" />
                <span class="evm-symbol-fallback" style="display:none;">${sym.icon || "⭐"}</span>
                <span class="evm-symbol-caption">${sym.name}</span>
              </div>
              <div class="evm-cand-info">
                <h3 class="evm-cand-name">${cand.fullName}</h3>
                <span class="evm-cand-sub">${subText}</span>
              </div>
              <div class="evm-right-cluster">
                <span class="evm-led-lamp"></span>
                <button type="button" class="evm-vote-btn" tabindex="-1">
                  ${isPicked ? (votedBallot ? "RECORDED ✓" : "VOTED ✓") : "VOTE"}
                </button>
              </div>
            `;"""

NEW_ROW_TEACHER_HTML = """            const sym = cand.symbolObj || { name: "Candidate Choice", icon: "⭐" };
            const symSlug = (sym.slug || sym.name || "star").toLowerCase().replace(/[\\s-]+/g, "_");
            const symImg = sym.image || sym.imagePath || `../assets/symbols/${symSlug}.png`;

            row.innerHTML = `
              <div class="evm-cand-avatar" style="${!cand.photoPath && !cand.photoUrl ? `background:${houseSubtle}; border-color:${houseAccent}60; color:${houseText};` : ''}">${photoHtml}</div>
              <div class="evm-cand-symbol" title="Election Symbol: ${sym.name}">
                <img src="${symImg}" alt="${sym.name}" class="evm-symbol-img" onerror="this.style.display='none';this.nextElementSibling.style.display='inline-block';" />
                <span class="evm-symbol-fallback" style="display:none;">${sym.icon || "⭐"}</span>
                <span class="evm-symbol-caption">${sym.name}</span>
              </div>
              <div class="evm-cand-info">
                <h3 class="evm-cand-name">${cand.fullName}</h3>
                <span class="evm-cand-sub">${subText}</span>
                ${cand.tagline ? `<span class="evm-cand-tagline">&ldquo;${cand.tagline}&rdquo;</span>` : ""}
              </div>
              <div class="evm-right-cluster">
                <span class="evm-led-lamp"></span>
                <button type="button" class="evm-vote-btn" tabindex="-1">
                  ${isSelected ? "VOTED ✓" : "VOTE"}
                </button>
              </div>
            `;"""

NEW_REVIEW_CARD_HTML = """            const pickedSym = picked ? (picked.symbolObj || { name: "", icon: "⭐" }) : null;
            const pickedSymSlug = pickedSym ? (pickedSym.slug || pickedSym.name || "star").toLowerCase().replace(/[\\s-]+/g, "_") : "";
            const pickedSymImg = pickedSym && pickedSymSlug ? (pickedSym.image || pickedSym.imagePath || `../assets/symbols/${pickedSymSlug}.png`) : "";
            const symReviewHtml = pickedSym && pickedSym.name
              ? `<div class="evm-review-cand-symbol" title="Symbol: ${pickedSym.name}"><img src="${pickedSymImg}" alt="${pickedSym.name}" class="evm-symbol-img-sm" onerror="this.style.display='none';this.nextElementSibling.style.display='inline-block';" /><span class="evm-symbol-fallback-sm" style="display:none;">${pickedSym.icon || "⭐"}</span></div>`
              : "";

            card.innerHTML = `
              <div class="evm-review-card-left">
                <div class="evm-cand-avatar">${photoHtml}</div>
                ${symReviewHtml}
                <div>
                  <p class="evm-review-role-title">${pos.title}</p>
                  <h4 class="evm-review-cand-name" style="${!picked ? 'color:#dc2626;' : ''}">${picked ? picked.fullName : 'Not Selected'}</h4>
                  <p class="evm-review-cand-sub">${subText}</p>
                </div>
              </div>
              <button type="button" class="evm-review-change-btn" data-change-idx="${idx}">
                Change
              </button>
            `;"""

SYMBOL_CSS = """
/* EVM Candidate Symbol Box (Between Candidate Photo and Candidate Name) */
.evm-cand-symbol {
  width: 96px;
  height: 96px;
  border-radius: 14px;
  background: var(--bg-surface, #fbfaf8);
  border: 2px solid var(--border-default, #e5e2dc);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  margin-right: 1.35rem;
  flex-shrink: 0;
  padding: 6px;
  box-sizing: border-box;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.05);
}

.evm-cand-symbol .evm-symbol-img {
  width: 54px;
  height: 54px;
  object-fit: contain;
}

.evm-cand-symbol .evm-symbol-fallback {
  font-size: 2rem;
  line-height: 1;
}

.evm-cand-symbol .evm-symbol-caption {
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--text-muted, #767167);
  text-transform: uppercase;
  letter-spacing: 0.03em;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 84px;
}

.evm-candidate-row.is-selected .evm-cand-symbol {
  background: #ffffff;
  border-color: #86efac;
}

.evm-review-cand-symbol {
  width: 58px;
  height: 58px;
  border-radius: 12px;
  background: var(--bg-surface, #fbfaf8);
  border: 1.5px solid var(--border-default, #e5e2dc);
  display: grid;
  place-items: center;
  flex-shrink: 0;
  padding: 4px;
  box-sizing: border-box;
}

.evm-review-cand-symbol .evm-symbol-img-sm {
  width: 44px;
  height: 44px;
  object-fit: contain;
}
"""

def update_kiosk_app_js():
    house_slugs = ['bheeshma', 'gurudrona', 'hanuman', 'karna', 'vasistha', 'vishwamithra', 'central']
    for slug in house_slugs:
        p = ROOT / "Houses" / slug / "app.js"
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        
        # 1. Update candidate row
        cand_row_pat = r"row\.innerHTML\s*=\s*`\s*<div class=\"evm-cand-avatar\">[\s\S]*?`\s*;"
        if re.search(cand_row_pat, text):
            text = re.sub(cand_row_pat, NEW_ROW_HTML, text)
            print(f" -> Updated candidate row in Houses/{slug}/app.js")
        else:
            print(f" * Candidate row pattern not found in Houses/{slug}/app.js")
            
        # 2. Update review card
        review_card_pat = r"card\.innerHTML\s*=\s*`\s*<div class=\"evm-review-card-left\">[\s\S]*?`\s*;"
        if re.search(review_card_pat, text):
            text = re.sub(review_card_pat, NEW_REVIEW_CARD_HTML, text)
            print(f" -> Updated review card in Houses/{slug}/app.js")
        else:
            print(f" * Review card pattern not found in Houses/{slug}/app.js")
            
        p.write_text(text, encoding="utf-8")
        
    # Teachers booth
    tp = ROOT / "Houses" / "teachers" / "app.js"
    if tp.exists():
        t_text = tp.read_text(encoding="utf-8")
        t_cand_row_pat = r"row\.innerHTML\s*=\s*`\s*<div class=\"evm-cand-avatar\"[\s\S]*?`\s*;"
        if re.search(t_cand_row_pat, t_text):
            t_text = re.sub(t_cand_row_pat, NEW_ROW_TEACHER_HTML, t_text)
            tp.write_text(t_text, encoding="utf-8")
            print(f" -> Updated candidate row in Houses/teachers/app.js")


def update_kiosk_css():
    css_files = [
        ROOT / "Houses" / "bheeshma" / "styles.css",
        ROOT / "Houses" / "gurudrona" / "styles.css",
        ROOT / "Houses" / "hanuman" / "styles.css",
        ROOT / "Houses" / "karna" / "styles.css",
        ROOT / "Houses" / "vasistha" / "styles.css",
        ROOT / "Houses" / "vishwamithra" / "styles.css",
        ROOT / "Houses" / "central" / "styles.css",
        ROOT / "Houses" / "teachers" / "styles.css",
    ]
    for cp in css_files:
        if not cp.exists():
            continue
        c_text = cp.read_text(encoding="utf-8")
        if ".evm-cand-symbol" not in c_text:
            c_text += "\n" + SYMBOL_CSS
            cp.write_text(c_text, encoding="utf-8")
            print(f" -> Added symbol CSS to {cp.relative_to(ROOT)}")
        else:
            print(f" -> Symbol CSS already present in {cp.relative_to(ROOT)}")


def update_supabase_configs_for_1c():
    for slug in ['bheeshma', 'gurudrona', 'hanuman', 'karna', 'vasistha', 'vishwamithra', 'central']:
        p = ROOT / "Houses" / slug / "supabase-config.js"
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        
        # Update DEMO_ACCOUNTS
        if '"1C8492"' not in text:
            text = text.replace(
                'const DEMO_ACCOUNTS = {',
                'const DEMO_ACCOUNTS = {\n    "1C8492": { admissionNo: "1C8492", fullName: "Aditya Vikram (Demo Voter)", fatherName: "R. K. Vikram (Demo)", className: "10", section: "Chatrapathi Shivaji (10-CS)", houseCode: "ALL", isStaff: true, isUniversal: true, isActive: true, photoUrl: "../assets/candidates/student_demo.jpg" },'
            )
        # Update fallback check
        text = re.sub(
            r'cleanId === "0000"',
            '(cleanId === "1C8492" || cleanId === "0000")',
            text
        )
        p.write_text(text, encoding="utf-8")
        print(f" -> Updated 1C8492 demo support in Houses/{slug}/supabase-config.js")


def bump_cachebusters():
    html_files = [
        ROOT / "Houses" / "bheeshma" / "index.html",
        ROOT / "Houses" / "gurudrona" / "index.html",
        ROOT / "Houses" / "hanuman" / "index.html",
        ROOT / "Houses" / "karna" / "index.html",
        ROOT / "Houses" / "vasistha" / "index.html",
        ROOT / "Houses" / "vishwamithra" / "index.html",
        ROOT / "Houses" / "central" / "index.html",
        ROOT / "Houses" / "teachers" / "index.html",
    ]
    for hp in html_files:
        if not hp.exists():
            continue
        content = hp.read_text(encoding="utf-8")
        # Bump versions to ?v=1050
        content = re.sub(r'(\.js|\.css)\?v=\d+', r'\1?v=1050', content)
        hp.write_text(content, encoding="utf-8")
        print(f" -> Bumped cachebuster to ?v=1050 in {hp.relative_to(ROOT)}")


def main():
    print("--- STEP 1: Updating CSS with EVM Symbol classes ---")
    update_kiosk_css()

    print("\n--- STEP 2: Updating App.js with New Ballot Layout ---")
    update_kiosk_app_js()

    print("\n--- STEP 3: Updating Supabase Configs with 1C8492 Demo Account ---")
    update_supabase_configs_for_1c()

    print("\n--- STEP 4: Bumping HTML Cachebusters to v=1050 ---")
    bump_cachebusters()

    print("\nAll UI and logic updates applied!")


if __name__ == "__main__":
    main()

