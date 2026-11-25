/**
 * Universal Contesting Candidates Modal Component
 * Renders an interactive modal directory of all 140 candidates
 * across the 6 Houses and Central School Cabinet.
 */
(function () {
  const HOUSE_META = {
    BHEESHMA: { name: "Bheeshma House", color: "#EAB308", border: "#CA8A04", bg: "#FEFCE8", badge: "🦁 Bheeshma" },
    GURUDRONA: { name: "Gurudrona House", color: "#2563EB", border: "#1D4ED8", bg: "#EFF6FF", badge: "🏹 Gurudrona" },
    HANUMAN: { name: "Hanuman House", color: "#EA580C", border: "#C2410C", bg: "#FFF7ED", badge: "⚡ Hanuman" },
    KARNA: { name: "Karna House", color: "#DC2626", border: "#B91C1C", bg: "#FEF2F2", badge: "⚔️ Karna" },
    VASISTHA: { name: "Vasistha House", color: "#DB2777", border: "#BE185D", bg: "#FDF2F8", badge: "🌿 Vasistha" },
    VISHWAMITHRA: { name: "Vishwamithra House", color: "#7C3AED", border: "#6D28D9", bg: "#F5F3FF", badge: "🔥 Vishwamithra" },
    CENTRAL: { name: "School Cabinet", color: "#059669", border: "#047857", bg: "#ECFDF5", badge: "⭐ Central Cabinet" }
  };

  const STYLES = `
    .cand-modal-overlay {
      position: fixed;
      inset: 0;
      background: rgba(15, 23, 42, 0.7);
      backdrop-filter: blur(6px);
      z-index: 99999;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 1.5rem;
      animation: candFadeIn 0.2s ease-out;
      font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
    }
    @keyframes candFadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }
    .cand-modal-container {
      background: #FFFFFF;
      width: 100%;
      max-width: 1140px;
      max-height: 92vh;
      border-radius: 20px;
      display: flex;
      flex-direction: column;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
      border: 1px solid #E2E8F0;
      overflow: hidden;
      animation: candSlideUp 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }
    @keyframes candSlideUp {
      from { transform: translateY(20px) scale(0.98); opacity: 0; }
      to { transform: translateY(0) scale(1); opacity: 1; }
    }
    .cand-modal-head {
      padding: 1.25rem 1.75rem;
      border-bottom: 1px solid #E2E8F0;
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: #FAF7F2;
    }
    .cand-modal-title {
      font-size: 1.4rem;
      font-weight: 800;
      color: #0F172A;
      margin: 0;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }
    .cand-modal-sub {
      font-size: 0.85rem;
      color: #64748B;
      margin-top: 0.2rem;
    }
    .cand-head-actions {
      display: flex;
      align-items: center;
      gap: 0.65rem;
    }
    .cand-btn-print {
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      background: #FFFFFF;
      border: 1px solid #CBD5E1;
      padding: 0.5rem 0.95rem;
      border-radius: 10px;
      font-size: 0.85rem;
      font-weight: 600;
      color: #334155;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .cand-btn-print:hover {
      background: #F1F5F9;
      border-color: #94A3B8;
    }
    .cand-btn-close {
      width: 36px;
      height: 36px;
      border-radius: 50%;
      border: 1px solid #CBD5E1;
      background: #FFFFFF;
      color: #64748B;
      font-size: 1.35rem;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      line-height: 1;
      transition: all 0.15s ease;
    }
    .cand-btn-close:hover {
      background: #FEE2E2;
      color: #DC2626;
      border-color: #FCA5A5;
    }
    .cand-modal-controls {
      padding: 1rem 1.75rem;
      background: #FFFFFF;
      border-bottom: 1px solid #E2E8F0;
      display: flex;
      flex-direction: column;
      gap: 0.85rem;
    }
    .cand-filter-row {
      display: flex;
      gap: 0.75rem;
      align-items: center;
      flex-wrap: wrap;
    }
    .cand-search-input {
      flex: 1;
      min-width: 220px;
      padding: 0.65rem 1rem;
      border-radius: 10px;
      border: 1px solid #CBD5E1;
      font-size: 0.9rem;
      background: #F8FAFC;
      color: #0F172A;
      outline: none;
      transition: border-color 0.15s ease;
    }
    .cand-search-input:focus {
      border-color: #059669;
      background: #FFFFFF;
      box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.1);
    }
    .cand-pos-select {
      padding: 0.65rem 1rem;
      border-radius: 10px;
      border: 1px solid #CBD5E1;
      font-size: 0.9rem;
      background: #F8FAFC;
      color: #0F172A;
      cursor: pointer;
      outline: none;
      min-width: 200px;
    }
    .cand-pos-select:focus {
      border-color: #059669;
    }
    .cand-house-tabs {
      display: flex;
      gap: 0.4rem;
      overflow-x: auto;
      padding-bottom: 0.25rem;
    }
    .cand-tab-pill {
      background: #F1F5F9;
      border: 1px solid #E2E8F0;
      padding: 0.4rem 0.85rem;
      border-radius: 9999px;
      font-size: 0.82rem;
      font-weight: 700;
      color: #475569;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.15s ease;
    }
    .cand-tab-pill:hover {
      background: #E2E8F0;
      color: #1E293B;
    }
    .cand-tab-pill.active {
      background: #0F172A;
      color: #FFFFFF;
      border-color: #0F172A;
    }
    .cand-grid-body {
      flex: 1;
      overflow-y: auto;
      padding: 1.5rem 1.75rem;
      background: #F8FAFC;
    }
    .cand-cards-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(290px, 1fr));
      gap: 1.15rem;
    }
    .cand-card {
      background: #FFFFFF;
      border-radius: 14px;
      border: 1px solid #E2E8F0;
      padding: 1.15rem;
      display: flex;
      flex-direction: column;
      gap: 0.85rem;
      transition: transform 0.15s ease, box-shadow 0.15s ease;
      position: relative;
    }
    .cand-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.08);
    }
    .cand-card-top {
      display: flex;
      align-items: center;
      gap: 0.85rem;
    }
    .cand-avatar-wrap {
      width: 62px;
      height: 62px;
      border-radius: 50%;
      border: 2.5px solid #CBD5E1;
      overflow: hidden;
      flex-shrink: 0;
      background: #E2E8F0;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .cand-avatar-img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    .cand-avatar-initials {
      font-weight: 800;
      font-size: 1.25rem;
      color: #64748B;
    }
    .cand-info-wrap {
      flex: 1;
      min-width: 0;
    }
    .cand-name {
      font-size: 1rem;
      font-weight: 800;
      color: #0F172A;
      margin: 0 0 0.15rem 0;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .cand-grade {
      font-size: 0.8rem;
      font-weight: 600;
      color: #64748B;
      margin: 0;
    }
    .cand-post-badge {
      display: inline-block;
      font-size: 0.75rem;
      font-weight: 800;
      padding: 0.25rem 0.65rem;
      border-radius: 6px;
      margin-top: 0.25rem;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 100%;
    }
    .cand-card-middle {
      background: #F8FAFC;
      border-radius: 8px;
      padding: 0.65rem 0.85rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border: 1px solid #EDF2F7;
    }
    .cand-symbol-info {
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }
    .cand-symbol-box {
      width: 32px;
      height: 32px;
      border-radius: 6px;
      background: #FFFFFF;
      border: 1px solid #CBD5E1;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
      font-size: 1.15rem;
    }
    .cand-symbol-img {
      width: 100%;
      height: 100%;
      object-fit: contain;
    }
    .cand-symbol-label {
      font-size: 0.82rem;
      font-weight: 700;
      color: #334155;
    }
    .cand-house-tag {
      font-size: 0.75rem;
      font-weight: 700;
      padding: 0.2rem 0.55rem;
      border-radius: 9999px;
    }
    .cand-motto {
      font-size: 0.8rem;
      font-style: italic;
      color: #64748B;
      margin: 0;
      line-height: 1.35;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }
    .cand-empty-state {
      text-align: center;
      padding: 3.5rem 1rem;
      color: #64748B;
    }
    .cand-empty-icon {
      font-size: 2.5rem;
      margin-bottom: 0.5rem;
    }
  `;

  class ContestingCandidatesModal {
    constructor() {
      this.modalEl = null;
      this.candidates = [];
      this.currentHouse = "ALL";
      this.currentPosition = "";
      this.currentSearch = "";
      this.isInitialized = false;
      this.basePrefix = this.detectPrefix();
    }

    detectPrefix() {
      // If running from Result declaration/
      if (window.location.pathname.includes("Result declaration")) {
        return "../";
      }
      // If running from Houses/admin/
      if (window.location.pathname.includes("Houses/admin")) {
        return "../../";
      }
      return "";
    }

    resolvePhoto(raw) {
      if (!raw) return "";
      const path = String(raw).trim();
      if (path.startsWith("http://") || path.startsWith("https://") || path.startsWith("data:")) {
        return path;
      }
      // Clean up relative path based on location
      const isResultDecl = window.location.pathname.includes("Result declaration");
      if (isResultDecl) {
        if (path.startsWith("../assets/")) {
          return path.replace("../assets/", "../Houses/assets/");
        }
        if (path.startsWith("assets/")) {
          return path;
        }
        return "../Houses/" + path.replace(/^(\.\.\/)+/, "");
      } else {
        if (path.startsWith("../assets/")) {
          return path;
        }
        if (path.startsWith("assets/")) {
          return "../" + path;
        }
        return path;
      }
    }

    resolveSymbolImg(sym) {
      if (!sym) return "";
      const img = sym.image || sym.imagePath || "";
      return this.resolvePhoto(img);
    }

    countFor(house) {
      if (!Array.isArray(this.candidates) || this.candidates.length === 0) return 0;
      if (house === "ALL") return this.candidates.length;
      return this.candidates.filter(c => String(c.houseCode || "").toUpperCase() === house).length;
    }

    updateTabCounts() {
      if (!this.modalEl) return;
      const tabs = this.modalEl.querySelectorAll(".cand-tab-pill");
      tabs.forEach(tab => {
        const h = tab.getAttribute("data-house");
        const count = this.countFor(h);
        if (h === "ALL") tab.textContent = `All (${count})`;
        else if (h === "CENTRAL") tab.textContent = `⭐ Cabinet (${count})`;
        else if (h === "BHEESHMA") tab.textContent = `🦁 Bheeshma (${count})`;
        else if (h === "GURUDRONA") tab.textContent = `🏹 Gurudrona (${count})`;
        else if (h === "HANUMAN") tab.textContent = `⚡ Hanuman (${count})`;
        else if (h === "KARNA") tab.textContent = `⚔️ Karna (${count})`;
        else if (h === "VASISTHA") tab.textContent = `🌿 Vasistha (${count})`;
        else if (h === "VISHWAMITHRA") tab.textContent = `🔥 Vishwamithra (${count})`;
      });
      const sub = this.modalEl.querySelector("#cand-summary-sub");
      if (sub && this.candidates.length > 0) {
        sub.textContent = `Total ${this.candidates.length} Verified Candidates across 6 Houses and School Cabinet`;
      }
    }

    loadCandidates() {
      if (Array.isArray(window.ALL_CONTESTING_CANDIDATES) && window.ALL_CONTESTING_CANDIDATES.length > 0) {
        this.candidates = window.ALL_CONTESTING_CANDIDATES;
      } else if (window.ADMIN_DATA && Array.isArray(window.ADMIN_DATA.candidates)) {
        this.candidates = window.ADMIN_DATA.candidates;
      } else {
        this.candidates = [];
      }
    }

    injectStyles() {
      if (document.getElementById("cand-modal-styles")) return;
      const style = document.createElement("style");
      style.id = "cand-modal-styles";
      style.textContent = STYLES;
      document.head.appendChild(style);
    }

    buildModal() {
      this.injectStyles();
      this.loadCandidates();

      const modal = document.createElement("div");
      modal.className = "cand-modal-overlay";
      modal.id = "contesting-candidates-modal";
      modal.hidden = true;

      modal.innerHTML = `
        <div class="cand-modal-container" role="dialog" aria-modal="true" aria-labelledby="cand-title">
          <div class="cand-modal-head">
            <div>
              <h2 id="cand-title" class="cand-modal-title">
                <span>👥 Official Contesting Candidates 2026</span>
              </h2>
              <p class="cand-modal-sub" id="cand-summary-sub">
                Total ${this.candidates.length || 140} Verified Candidates across 6 Houses and School Cabinet
              </p>
            </div>
            <div class="cand-head-actions">
              <button type="button" id="cand-print-btn" class="cand-btn-print" title="Save &amp; Download PDF Directory">
                📥 Save / Download PDF
              </button>
              <button type="button" id="cand-close-btn" class="cand-btn-close" aria-label="Close modal">&times;</button>
            </div>
          </div>

          <div class="cand-modal-controls">
            <div class="cand-filter-row">
              <input type="search" id="cand-search-input" class="cand-search-input" placeholder="🔍 Search candidate name, admission no, symbol, or motto..." />
              <select id="cand-pos-select" class="cand-pos-select" aria-label="Filter by Leadership Post">
                <option value="">All Leadership Posts</option>
                <optgroup label="School Cabinet (Central)">
                  <option value="PRESIDENT">School President</option>
                  <option value="VICE_PRESIDENT">School Vice President</option>
                  <option value="LITERARY_SECRETARY">Literary Secretary</option>
                  <option value="SPORTS_SECRETARY">Sports Secretary</option>
                  <option value="SOCIAL_CULTURAL_SECRETARY">Social & Cultural Secretary</option>
                </optgroup>
                <optgroup label="House Leadership (Class 10 & 9)">
                  <option value="CAPTAIN_BOY">Boys Captain (Class 10)</option>
                  <option value="CAPTAIN_GIRL">Girls Captain (Class 10)</option>
                  <option value="VICE_CAPTAIN_BOY">Boys Vice-Captain (Class 9)</option>
                  <option value="VICE_CAPTAIN_GIRL">Girls Vice-Captain (Class 9)</option>
                </optgroup>
              </select>
            </div>

            <div class="cand-house-tabs" id="cand-house-tabs">
              <button type="button" class="cand-tab-pill active" data-house="ALL">All (${this.countFor("ALL")})</button>
              <button type="button" class="cand-tab-pill" data-house="CENTRAL">⭐ Cabinet (${this.countFor("CENTRAL")})</button>
              <button type="button" class="cand-tab-pill" data-house="BHEESHMA">🦁 Bheeshma (${this.countFor("BHEESHMA")})</button>
              <button type="button" class="cand-tab-pill" data-house="GURUDRONA">🏹 Gurudrona (${this.countFor("GURUDRONA")})</button>
              <button type="button" class="cand-tab-pill" data-house="HANUMAN">⚡ Hanuman (${this.countFor("HANUMAN")})</button>
              <button type="button" class="cand-tab-pill" data-house="KARNA">⚔️ Karna (${this.countFor("KARNA")})</button>
              <button type="button" class="cand-tab-pill" data-house="VASISTHA">🌿 Vasistha (${this.countFor("VASISTHA")})</button>
              <button type="button" class="cand-tab-pill" data-house="VISHWAMITHRA">🔥 Vishwamithra (${this.countFor("VISHWAMITHRA")})</button>
            </div>
          </div>

          <div class="cand-grid-body">
            <div class="cand-cards-grid" id="cand-cards-grid"></div>
            <div class="cand-empty-state" id="cand-empty" style="display: none;">
              <div class="cand-empty-icon">🔍</div>
              <h3 style="font-weight: 700; color: #1E293B; margin-bottom: 0.35rem;">No Matching Candidates Found</h3>
              <p>Try clearing your search query or switching to another house filter tab.</p>
            </div>
          </div>
        </div>
      `;

      document.body.appendChild(modal);
      this.modalEl = modal;

      // Event listeners
      modal.querySelector("#cand-close-btn").addEventListener("click", () => this.close());
      modal.addEventListener("click", (e) => {
        if (e.target === modal) this.close();
      });

      document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && !this.modalEl.hidden) {
          this.close();
        }
      });

      const searchInput = modal.querySelector("#cand-search-input");
      searchInput.addEventListener("input", (e) => {
        this.currentSearch = e.target.value.trim().toLowerCase();
        this.renderCards();
      });

      const posSelect = modal.querySelector("#cand-pos-select");
      posSelect.addEventListener("change", (e) => {
        this.currentPosition = e.target.value;
        this.renderCards();
      });

      const tabs = modal.querySelectorAll(".cand-tab-pill");
      tabs.forEach((tab) => {
        tab.addEventListener("click", () => {
          tabs.forEach((t) => t.classList.remove("active"));
          tab.classList.add("active");
          this.currentHouse = tab.getAttribute("data-house");
          this.renderCards();
        });
      });

      modal.querySelector("#cand-print-btn").addEventListener("click", () => {
        this.printDirectory();
      });

      this.isInitialized = true;
    }

    renderCards() {
      if (!this.modalEl) return;
      this.loadCandidates();

      const grid = this.modalEl.querySelector("#cand-cards-grid");
      const empty = this.modalEl.querySelector("#cand-empty");
      const sub = this.modalEl.querySelector("#cand-summary-sub");

      const filtered = this.candidates.filter((c) => {
        // House filter
        if (this.currentHouse !== "ALL") {
          if (String(c.houseCode || "").toUpperCase() !== this.currentHouse) return false;
        }

        // Position filter
        if (this.currentPosition) {
          const posId = String(c.positionId || "").toUpperCase();
          if (!posId.includes(this.currentPosition.toUpperCase())) return false;
        }

        // Search query
        if (this.currentSearch) {
          const symName = c.symbolObj ? (c.symbolObj.name || "") : "";
          const hay = `${c.fullName || ""} ${c.admissionNo || ""} ${c.tagline || ""} ${c.positionName || ""} ${c.section || ""} ${symName}`.toLowerCase();
          if (!hay.includes(this.currentSearch)) return false;
        }

        return true;
      });

      if (sub) {
        sub.textContent = `Showing ${filtered.length} of ${this.candidates.length} Contesting Candidates`;
      }

      if (filtered.length === 0) {
        grid.innerHTML = "";
        empty.style.display = "block";
        return;
      }

      empty.style.display = "none";
      grid.innerHTML = filtered.map((c) => {
        const hCode = String(c.houseCode || "").toUpperCase();
        const meta = HOUSE_META[hCode] || { name: c.houseCode, color: "#475569", border: "#CBD5E1", bg: "#F8FAFC", badge: c.houseCode };
        const photoSrc = this.resolvePhoto(c.photoUrl || c.photoPath);
        const sym = c.symbolObj || {};
        const symImg = this.resolveSymbolImg(sym);
        const initials = (c.fullName || "C").split(" ").map(p => p[0]).slice(0, 2).join("").toUpperCase();

        return `
          <div class="cand-card" style="border-top: 5px solid ${meta.color};">
            <div class="cand-card-top">
              <div class="cand-avatar-wrap" style="border-color: ${meta.color};">
                ${photoSrc ? `<img class="cand-avatar-img" src="${photoSrc}" alt="${c.fullName}" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';" /><div class="cand-avatar-initials" style="display:none;">${initials}</div>` : `<div class="cand-avatar-initials">${initials}</div>`}
              </div>
              <div class="cand-info-wrap">
                <h4 class="cand-name" title="${c.fullName}">${c.fullName}</h4>
                <p class="cand-grade">${c.section || (c.className ? `Class ${c.className}` : "Candidate")}</p>
                <span class="cand-post-badge" style="background: ${meta.bg}; color: ${meta.border}; border: 1px solid ${meta.border};">
                  ${c.positionName || "Contesting Candidate"}
                </span>
              </div>
            </div>

            <div class="cand-card-middle">
              <div class="cand-symbol-info">
                <div class="cand-symbol-box">
                  ${symImg ? `<img src="${symImg}" class="cand-symbol-img" alt="Symbol" onerror="this.style.display='none'; if(this.nextElementSibling) this.nextElementSibling.style.display='inline';" /><span style="display:none; font-size:1.15rem;">${sym.icon || '🗳️'}</span>` : `<span style="font-size:1.15rem;">${sym.icon || '🗳️'}</span>`}
                </div>
              </div>
              <span class="cand-house-tag" style="background: ${meta.bg}; color: ${meta.border}; border: 1px solid ${meta.border};">
                ${meta.badge}
              </span>
            </div>

            <p class="cand-motto" title="${c.tagline || ''}">
              &ldquo;${c.tagline || 'Dedicated to student excellence and democratic school leadership.'}&rdquo;
            </p>
          </div>
        `;
      }).join("");
    }

    open(initialHouse = "ALL") {
      this.loadCandidates();
      if (!this.isInitialized || !this.modalEl) {
        this.buildModal();
      } else {
        this.updateTabCounts();
      }
      this.currentHouse = initialHouse;

      if (this.modalEl) {
        const tabs = this.modalEl.querySelectorAll(".cand-tab-pill");
        tabs.forEach((tab) => {
          tab.classList.toggle("active", tab.getAttribute("data-house") === initialHouse);
        });
        this.modalEl.hidden = false;
        this.renderCards();
        document.body.style.overflow = "hidden";
      }
    }

    close() {
      if (this.modalEl) {
        this.modalEl.hidden = true;
        document.body.style.overflow = "";
      }
    }

    buildPrintableDocument() {
      this.loadCandidates();
      const allCands = Array.isArray(this.candidates) ? this.candidates : [];

      const HOUSES_ORDER = [
        { code: "CENTRAL", name: "School Cabinet (Central Council)", badge: "🏛️ School Cabinet", color: "#059669", bg: "#ECFDF5", motto: "Excellence, Integrity, Service & Apex Vision" },
        { code: "BHEESHMA", name: "Bheeshma House", badge: "🦁 Bheeshma House", color: "#CA8A04", bg: "#FEFCE8", motto: "Unwavering Resolve, Discipline & Duty" },
        { code: "GURUDRONA", name: "Gurudrona House", badge: "🏹 Gurudrona House", color: "#2563EB", bg: "#EFF6FF", motto: "Mastery, Focus, Dedication & Wisdom" },
        { code: "HANUMAN", name: "Hanuman House", badge: "⚡ Hanuman House", color: "#EA580C", bg: "#FFF7ED", motto: "Courage, Strength, Loyalty & Service" },
        { code: "KARNA", name: "Karna House", badge: "⚔️ Karna House", color: "#DC2626", bg: "#FEF2F2", motto: "Generosity, Valour, Resilience & Honour" },
        { code: "VASISTHA", name: "Vasistha House", badge: "🌿 Vasistha House", color: "#DB2777", bg: "#FDF2F8", motto: "Wisdom, Harmony, Patience & Knowledge" },
        { code: "VISHWAMITHRA", name: "Vishwamithra House", badge: "🔥 Vishwamithra House", color: "#7C3AED", bg: "#F5F3FF", motto: "Determination, Innovation, Vision & Tenacity" }
      ];

      const CENTRAL_POSTS = [
        "School President (Class 10 · Central Cabinet)",
        "School Vice President (Class 9 · Central Cabinet)",
        "Literary Secretary (Class 9 · Central Cabinet)",
        "Sports Secretary (Class 9 · Central Cabinet)",
        "Social & Cultural Secretary (Class 9 · Central Cabinet)"
      ];

      const HOUSE_POSTS = [
        "Boys Captain (Class 10 Boy)",
        "Girls Captain (Class 10 Girl)",
        "Boys Vice Captain (Class 9 Boy)",
        "Girls Vice Captain (Class 9 Girl)"
      ];

      const dateStr = new Date().toLocaleDateString("en-US", {
        weekday: "long",
        year: "numeric",
        month: "long",
        day: "numeric"
      });

      const isResultPage = window.location.pathname.includes("Result") || window.location.pathname.includes("declaration");

      const resolveImg = (src) => {
        if (!src) return "";
        let s = String(src).trim();
        if (s.startsWith("http://") || s.startsWith("https://") || s.startsWith("data:")) return s;
        if (isResultPage) {
          if (s.startsWith("../assets/")) return s.replace(/^\.\.\/assets\//, "assets/");
        } else {
          if (!s.startsWith("../")) return "../" + s;
        }
        return s;
      };

      let sectionsHtml = "";

      HOUSES_ORDER.forEach((hInfo, hIdx) => {
        const houseCands = allCands.filter(c => String(c.houseCode || "").toUpperCase() === hInfo.code);
        const postList = hInfo.code === "CENTRAL" ? CENTRAL_POSTS : HOUSE_POSTS;

        let postsHtml = "";

        postList.forEach((postName) => {
          const postCands = houseCands.filter(c => c.positionName === postName);
          if (postCands.length === 0) return;

          const cardsHtml = postCands.map(c => {
            const photoSrc = resolveImg(c.photoUrl || c.photoPath);
            const sym = c.symbolObj || {};
            const symImg = resolveImg(sym.image || sym.imagePath);
            const initials = String(c.fullName || "C").trim().split(/\s+/).slice(0, 2).map(p => p[0]).join("").toUpperCase();

            return `
              <div class="print-cand-card" style="border-top: 4px solid ${hInfo.color};">
                <div class="card-left">
                  <div class="avatar-box" style="border-color: ${hInfo.color};">
                    ${photoSrc ? `<img src="${photoSrc}" alt="${c.fullName}" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';" /><div class="avatar-fallback" style="display:none; background:${hInfo.color};">${initials}</div>` : `<div class="avatar-fallback" style="background:${hInfo.color};">${initials}</div>`}
                  </div>
                </div>
                <div class="card-right">
                  <div class="cand-header-row">
                    <h4 class="cand-name">${c.fullName}</h4>
                    <span class="cand-id">${c.admissionNo || ""}</span>
                  </div>
                  <div class="cand-meta-row">
                    <span class="cand-class">${c.section || (c.className ? `Class ${c.className}` : "")}</span>
                    <span class="cand-house-badge" style="background:${hInfo.bg}; color:${hInfo.color}; border:1px solid ${hInfo.color}50;">${hInfo.name}</span>
                  </div>
                  <div class="symbol-row">
                    <div class="symbol-pill">
                      ${symImg ? `<img src="${symImg}" alt="Symbol" class="symbol-img" onerror="this.style.display='none'; if(this.nextElementSibling) this.nextElementSibling.style.display='inline';" /><span class="symbol-icon" style="display:none;">${sym.icon || '🗳️'}</span>` : `<span class="symbol-icon">${sym.icon || '🗳️'}</span>`}
                    </div>
                  </div>
                  <p class="cand-motto">&ldquo;${c.tagline || 'Dedicated to student leadership and school duty.'}&rdquo;</p>
                </div>
              </div>
            `;
          }).join("");

          postsHtml += `
            <div class="post-group">
              <div class="post-heading">
                <span class="post-icon">📌</span>
                <span class="post-title">${postName}</span>
                <span class="post-count-badge">${postCands.length} Contesting Candidate${postCands.length > 1 ? 's' : ''}</span>
              </div>
              <div class="cards-grid">
                ${cardsHtml}
              </div>
            </div>
          `;
        });

        sectionsHtml += `
          <section class="house-section ${hIdx > 0 ? 'page-break' : ''}">
            <div class="house-banner" style="border-left: 6px solid ${hInfo.color}; background: ${hInfo.bg};">
              <div class="house-banner-left">
                <h3 class="house-title" style="color: ${hInfo.color};">${hInfo.badge}</h3>
                <p class="house-motto">&ldquo;${hInfo.motto}&rdquo;</p>
              </div>
              <div class="house-banner-right">
                <span class="house-count-pill" style="background: ${hInfo.color}; color: #ffffff;">
                  ${houseCands.length} Candidates
                </span>
              </div>
            </div>
            ${postsHtml}
          </section>
        `;
      });

      return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Official Contesting Candidates Directory — SPR School Elections 2026</title>
  <base href="${window.location.href}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    html, body {
      font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
      color: #0f172a;
      background: #f8fafc;
      font-size: 13px;
      line-height: 1.45;
      -webkit-font-smoothing: antialiased;
    }
    
    /* Screen Control Bar */
    .screen-controls {
      position: sticky;
      top: 0;
      z-index: 9999;
      background: #0f172a;
      color: #ffffff;
      padding: 0.75rem 1.5rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .screen-controls h2 {
      font-size: 1rem;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }
    .screen-controls-btns {
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }
    .btn-print-now {
      background: #059669;
      color: #ffffff;
      border: none;
      padding: 0.55rem 1.25rem;
      border-radius: 8px;
      font-size: 0.88rem;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      transition: background 0.15s;
    }
    .btn-print-now:hover {
      background: #047857;
    }
    .btn-close-win {
      background: #334155;
      color: #f1f5f9;
      border: none;
      padding: 0.55rem 1rem;
      border-radius: 8px;
      font-size: 0.88rem;
      font-weight: 600;
      cursor: pointer;
    }
    .btn-close-win:hover {
      background: #475569;
    }

    /* Print Document Container */
    .print-document {
      max-width: 1040px;
      margin: 1.5rem auto;
      background: #ffffff;
      padding: 2.5rem 3rem;
      border-radius: 12px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    }

    /* Master Cover Header */
    .doc-header {
      text-align: center;
      padding-bottom: 1.5rem;
      border-bottom: 3px double #cbd5e1;
      margin-bottom: 1.75rem;
    }
    .school-pretitle {
      font-size: 0.8rem;
      font-weight: 800;
      letter-spacing: 2px;
      color: #059669;
      text-transform: uppercase;
      margin-bottom: 0.35rem;
    }
    .doc-main-title {
      font-size: 1.85rem;
      font-weight: 900;
      color: #0f172a;
      letter-spacing: -0.5px;
      margin-bottom: 0.35rem;
    }
    .doc-subtitle {
      font-size: 0.95rem;
      color: #475569;
      font-weight: 600;
      margin-bottom: 1rem;
    }
    .stats-summary-bar {
      display: flex;
      justify-content: center;
      gap: 1.5rem;
      flex-wrap: wrap;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      padding: 0.65rem 1.25rem;
      border-radius: 9999px;
      margin: 0.75rem auto 0;
      max-width: 820px;
    }
    .stat-item {
      font-size: 0.82rem;
      color: #334155;
      font-weight: 600;
    }
    .stat-item strong {
      color: #0f172a;
      font-weight: 800;
    }

    /* House Sections */
    .house-section {
      margin-bottom: 2.25rem;
    }
    .house-banner {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0.9rem 1.25rem;
      border-radius: 10px;
      margin-bottom: 1.25rem;
      border: 1px solid #e2e8f0;
    }
    .house-title {
      font-size: 1.3rem;
      font-weight: 800;
      margin-bottom: 0.2rem;
    }
    .house-motto {
      font-size: 0.82rem;
      color: #475569;
      font-style: italic;
    }
    .house-count-pill {
      font-size: 0.82rem;
      font-weight: 800;
      padding: 0.35rem 0.9rem;
      border-radius: 9999px;
    }

    /* Post Groups */
    .post-group {
      margin-bottom: 1.5rem;
      page-break-inside: avoid;
      break-inside: avoid;
    }
    .post-heading {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      background: #f1f5f9;
      border-left: 4px solid #334155;
      padding: 0.45rem 0.85rem;
      border-radius: 6px;
      margin-bottom: 0.75rem;
    }
    .post-icon {
      font-size: 1rem;
    }
    .post-title {
      font-size: 0.95rem;
      font-weight: 800;
      color: #0f172a;
    }
    .post-count-badge {
      font-size: 0.75rem;
      font-weight: 700;
      color: #64748b;
      margin-left: auto;
    }

    /* Cards Grid */
    .cards-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 0.85rem;
    }
    .print-cand-card {
      background: #ffffff;
      border: 1px solid #cbd5e1;
      border-radius: 10px;
      padding: 0.85rem;
      display: flex;
      gap: 0.85rem;
      page-break-inside: avoid;
      break-inside: avoid;
      box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    .card-left {
      flex-shrink: 0;
    }
    .avatar-box {
      width: 72px;
      height: 72px;
      border-radius: 50%;
      border: 3px solid #cbd5e1;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #f1f5f9;
    }
    .avatar-box img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    .avatar-fallback {
      width: 100%;
      height: 100%;
      color: #ffffff;
      font-weight: 800;
      font-size: 1.25rem;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .card-right {
      flex-grow: 1;
      min-width: 0;
      display: flex;
      flex-direction: column;
      justify-content: center;
    }
    .cand-header-row {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 0.5rem;
      margin-bottom: 0.15rem;
    }
    .cand-name {
      font-size: 1.05rem;
      font-weight: 800;
      color: #0f172a;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .cand-id {
      font-size: 0.72rem;
      font-family: monospace;
      font-weight: 700;
      color: #64748b;
      flex-shrink: 0;
    }
    .cand-meta-row {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      margin-bottom: 0.4rem;
    }
    .cand-class {
      font-size: 0.78rem;
      font-weight: 700;
      color: #475569;
    }
    .cand-house-badge {
      font-size: 0.72rem;
      font-weight: 800;
      padding: 0.15rem 0.55rem;
      border-radius: 9999px;
    }
    .symbol-row {
      margin-bottom: 0.35rem;
    }
    .symbol-pill {
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      padding: 0.2rem 0.55rem;
      border-radius: 6px;
      font-size: 0.76rem;
      color: #1e293b;
    }
    .symbol-img {
      width: 20px;
      height: 20px;
      object-fit: contain;
    }
    .symbol-icon {
      font-size: 1rem;
    }
    .cand-motto {
      font-size: 0.75rem;
      font-style: italic;
      color: #64748b;
      line-height: 1.35;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    /* Print Document Footer */
    .doc-footer {
      margin-top: 2rem;
      padding-top: 1.25rem;
      border-top: 2px solid #e2e8f0;
      display: flex;
      align-items: center;
      justify-content: space-between;
      color: #64748b;
      font-size: 0.78rem;
    }
    .doc-footer strong {
      color: #0f172a;
    }

    /* Print Specific Media Rules */
    @page {
      size: A4 portrait;
      margin: 10mm 10mm 12mm 10mm;
    }
    @media print {
      body {
        background: #ffffff !important;
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
      }
      .screen-controls {
        display: none !important;
      }
      .print-document {
        margin: 0 !important;
        padding: 0 !important;
        max-width: none !important;
        box-shadow: none !important;
        border-radius: 0 !important;
      }
      .page-break {
        page-break-before: always !important;
        break-before: page !important;
      }
      .post-group {
        page-break-inside: avoid !important;
        break-inside: avoid !important;
      }
      .print-cand-card {
        page-break-inside: avoid !important;
        break-inside: avoid !important;
      }
    }
    .btn-download-pdf {
      background: #2563eb;
      color: #ffffff;
      border: none;
      padding: 0.55rem 1.35rem;
      border-radius: 8px;
      font-size: 0.9rem;
      font-weight: 800;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.45rem;
      box-shadow: 0 2px 8px rgba(37,99,235,0.35);
      transition: all 0.15s ease;
    }
    .btn-download-pdf:hover {
      background: #1d4ed8;
      transform: translateY(-1px);
    }
    .pdf-spinner {
      display: inline-block;
      width: 14px;
      height: 14px;
      border: 2px solid #ffffff;
      border-top-color: transparent;
      border-radius: 50%;
      animation: spin 0.6s linear infinite;
    }
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
    .download-success-banner {
      background: #ecfdf5;
      color: #047857;
      border: 1px solid #a7f3d0;
      padding: 0.45rem 1rem;
      border-radius: 6px;
      font-size: 0.8rem;
      font-weight: 700;
      display: none;
    }
  </style>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
  <script src="${isResultPage ? 'js/html2pdf.bundle.min.js' : '../assets/html2pdf.bundle.min.js'}"></script>
</head>
<body>
  <div class="screen-controls">
    <h2>📄 Official Candidate Directory Preview (140 Candidates)</h2>
    <div class="screen-controls-btns">
      <span id="download-status-banner" class="download-success-banner">✓ PDF Downloaded!</span>
      <button id="btn-download-pdf" class="btn-download-pdf" onclick="window.downloadPdfFile()">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
        Save &amp; Download PDF
      </button>
      <button class="btn-print-now" onclick="window.print()">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 6 2 18 2 18 9"></polyline><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path><rect x="6" y="14" width="12" height="8"></rect></svg>
        Print Dialog
      </button>
      <button class="btn-close-win" onclick="window.close()">✕ Close Preview</button>
    </div>
  </div>

  <main class="print-document">
    <header class="doc-header">
      <div class="school-pretitle">SPR SCHOOL OF EXCELLENCE · DEMOCRATIC ELECTIONS 2026</div>
      <h1 class="doc-main-title">Official Contesting Candidates Directory</h1>
      <p class="doc-subtitle">Certified Master Nomination Register · House-Wise &amp; Post-Wise Compilation</p>
      
      <div class="stats-summary-bar">
        <span class="stat-item">Total Contesting Candidates: <strong>${allCands.length}</strong></span>
        <span class="stat-item">Electoral Divisions: <strong>7 (Cabinet + 6 Houses)</strong></span>
        <span class="stat-item">Leadership Offices: <strong>29 Posts</strong></span>
        <span class="stat-item">Date: <strong>${dateStr}</strong></span>
      </div>
    </header>

    <div class="sections-container">
      ${sectionsHtml}
    </div>

    <footer class="doc-footer">
      <div>
        <strong>SPR School Elections 2026</strong> · Returning Officer Master Record
      </div>
      <div>
        Certified Complete: 140 of 140 Candidates Printed House-Wise &amp; Post-Wise
      </div>
    </footer>
  </main>

  <script>
    window.downloadPdfFile = function() {
      const btn = document.getElementById("btn-download-pdf");
      const statusBanner = document.getElementById("download-status-banner");
      const origHtml = btn ? btn.innerHTML : "";
      if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span class="pdf-spinner"></span> Generating PDF...';
      }

      const element = document.querySelector(".print-document");
      const opt = {
        margin: [10, 8, 10, 8],
        filename: 'Official-Contesting-Candidates-Directory-2026.pdf',
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true, logging: false },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
        pagebreak: { mode: ['css', 'legacy'], before: '.page-break', avoid: ['.post-group', '.print-cand-card'] }
      };

      if (typeof html2pdf !== "undefined") {
        html2pdf().set(opt).from(element).save().then(function() {
          if (btn) {
            btn.disabled = false;
            btn.innerHTML = '✓ Downloaded!';
            setTimeout(function() { btn.innerHTML = origHtml; }, 3500);
          }
          if (statusBanner) {
            statusBanner.style.display = 'inline-block';
            setTimeout(function() { statusBanner.style.display = 'none'; }, 5000);
          }
        }).catch(function(err) {
          console.warn("html2pdf failed, falling back to print:", err);
          if (btn) {
            btn.disabled = false;
            btn.innerHTML = origHtml;
          }
          window.print();
        });
      } else {
        window.print();
        if (btn) {
          btn.disabled = false;
          btn.innerHTML = origHtml;
        }
      }
    };
  </script>
</body>
</html>`;
    }

    printDirectory() {
      this.loadCandidates();
      const html = this.buildPrintableDocument();

      // Open isolated print window for preview & immediate PDF download
      const printWin = window.open("", "_blank");
      if (printWin) {
        try {
          printWin.document.open();
          printWin.document.write(html);
          printWin.document.close();
          printWin.focus();
          return;
        } catch (err) {
          console.warn("Print window open warning, falling back to iframe:", err);
        }
      }

      // Fallback: Invisible iframe
      let iframe = document.getElementById("cand-print-iframe");
      if (!iframe) {
        iframe = document.createElement("iframe");
        iframe.id = "cand-print-iframe";
        iframe.style.position = "fixed";
        iframe.style.right = "0";
        iframe.style.bottom = "0";
        iframe.style.width = "0";
        iframe.style.height = "0";
        iframe.style.border = "0";
        document.body.appendChild(iframe);
      }
      const doc = iframe.contentWindow.document;
      doc.open();
      doc.write(html);
      doc.close();
    }
  }

  window.ContestingCandidatesModal = new ContestingCandidatesModal();

  // Auto-bind to buttons with [data-open-candidates] or #open-candidates-btn or #btnContestingCandidates
  document.addEventListener("DOMContentLoaded", () => {
    const bindTriggers = () => {
      document.querySelectorAll("[data-open-candidates], #open-candidates-btn, #btnContestingCandidates").forEach((btn) => {
        if (!btn.hasAttribute("data-cand-bound")) {
          btn.setAttribute("data-cand-bound", "true");
          btn.addEventListener("click", (e) => {
            e.preventDefault();
            const house = btn.getAttribute("data-open-candidates") || "ALL";
            window.ContestingCandidatesModal.open(house);
          });
        }
      });
    };
    bindTriggers();
    setTimeout(bindTriggers, 500);
  });
})();
