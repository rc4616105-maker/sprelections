/**
 * Master Application Controller
 * Handles view transitions, state management, Chrome Back Button integration,
 * fresh-on-reload behavior, elimination logic, and grand finale.
 */

class ElectionApp {
  constructor() {
    this.customDataKey = "SCHOOL_ELECTION_2026_CUSTOM_DATA_V4";

    // Load custom names if edited in Admin, otherwise use defaults
    this.houses = this.loadCustomData() || JSON.parse(JSON.stringify(DEFAULT_HOUSES));
    
    // Always start fresh on page reload with all 6 houses
    this.revealedHouseIds = [];
    this.currentHouse = null;
    this.revealedPostsInCurrent = [];

    // DOM Elements
    this.views = {
      wheel: document.getElementById("wheelView"),
      scratch: document.getElementById("scratchView"),
      finale: document.getElementById("finaleView")
    };

    this.wheelInstance = null;
    this.scratchManager = null;
    this.adminManager = null;

    this.init();
  }

  init() {
    // 1. Setup & render Wheel IMMEDIATELY on frame 1 (instant zero-delay render)
    this.wheelInstance = new SpinWheel("wheelCanvas", {
      onSelect: (selectedHouse) => this.onWheelLanded(selectedHouse)
    });
    this.updateWheelHouses();

    // 2. Setup Admin Panel
    this.adminManager = new AdminManager(this);

    // 3. Setup Global Navigation & Event Listeners
    this.attachEvents();
    this.initHistoryNavigation();

    // 4. Start clean at the wheel
    this.showView("wheel");

    // 5. Fetch live Supabase tallies asynchronously in the background without blocking the UI
    if (window.SupabaseResultsSync) {
      window.SupabaseResultsSync.fetchLiveResults(this.houses)
        .then((liveHouses) => {
          if (liveHouses && Array.isArray(liveHouses) && liveHouses.length > 0) {
            this.houses = liveHouses;
            this.updateWheelHouses();
          }
        })
        .catch((err) => {
          console.warn("Background Supabase live tally fetch error:", err);
        });
    }
  }

  initHistoryNavigation() {
    // Replace initial state
    try {
      window.history.replaceState({ stage: "wheel" }, "");
    } catch (e) {
      // ignore
    }

    // Chrome Back Button Handler
    window.addEventListener("popstate", (e) => {
      const spotlightModal = document.getElementById("scratchSpotlightModal");
      const houseModal = document.getElementById("selectedHouseModal");

      // 1. If spotlight card is open, Chrome Back closes it and returns to the 4 cards
      if (spotlightModal && spotlightModal.classList.contains("active")) {
        if (this.scratchManager) {
          this.scratchManager.closeSpotlight(false);
        }
        return;
      }

      // 2. If House Selected popup is open, Chrome Back dismisses it
      if (houseModal && houseModal.classList.contains("active")) {
        houseModal.classList.remove("active");
        this.currentHouse = null;
        return;
      }

      // 3. If in Scratch Arena, Chrome Back returns to the Wheel stage
      if (this.views.scratch && this.views.scratch.classList.contains("active")) {
        if (this.scratchManager) {
          this.scratchManager.destroy();
          this.scratchManager = null;
        }
        this.currentHouse = null;
        this.showView("wheel");
        this.updateWheelHouses();
        return;
      }

      // 4. If in Finale or Completed Stage, Chrome Back returns to Wheel
      if (this.views.finale && this.views.finale.classList.contains("active")) {
        this.showView("wheel");
        this.updateWheelHouses();
        return;
      }

      const state = e.state;
      if (state && state.stage) {
        if (state.stage === "wheel") {
          this.showView("wheel");
          this.updateWheelHouses();
        }
      }
    });
  }

  attachEvents() {
    // "Show Results" button from wheel modal
    const btnProceedToResults = document.getElementById("btnProceedToResults");
    if (btnProceedToResults) {
      btnProceedToResults.addEventListener("click", () => {
        const modal = document.getElementById("selectedHouseModal");
        if (modal) modal.classList.remove("active");
        if (this.currentHouse) {
          this.enterScratchArena(this.currentHouse);
        }
      });
    }

    // "Next House" button from scratch view
    const btnNextHouse = document.getElementById("btnNextHouse");
    if (btnNextHouse) {
      btnNextHouse.addEventListener("click", () => {
        this.completeCurrentHouseAndReturn();
      });
    }

    // Finale "Go to Home" Button
    const btnGoHome = document.getElementById("btnGoHome");
    if (btnGoHome) {
      btnGoHome.addEventListener("click", () => {
        this.showHomeCompleted();
      });
    }

    // Home Completed "View Elected Cabinet" Button
    const btnViewResultsHome = document.getElementById("btnViewResultsHome");
    if (btnViewResultsHome) {
      btnViewResultsHome.addEventListener("click", () => {
        this.showView("finale");
        this.renderFinale();
        try {
          window.history.pushState({ stage: "finale" }, "");
        } catch (e) {}
      });
    }

    // Home Completed "Restart" Button
    const btnRestartFromHome = document.getElementById("btnRestartFromHome");
    if (btnRestartFromHome) {
      btnRestartFromHome.addEventListener("click", () => {
        if (confirm("Restart election declaration from the beginning?")) {
          this.resetProgress();
        }
      });
    }

    // Finale Print Button
    const btnPrint = document.getElementById("btnPrintFinale");
    if (btnPrint) {
      btnPrint.addEventListener("click", () => window.print());
    }

    // Finale Restart Button
    const btnRestart = document.getElementById("btnRestartElection");
    if (btnRestart) {
      btnRestart.addEventListener("click", () => {
        if (confirm("Restart election declaration from the beginning?")) {
          this.resetProgress();
        }
      });
    }

    // Secret Admin shortcut: Press 'Ctrl+Alt+E' to open edit modal
    window.addEventListener("keydown", (e) => {
      if ((e.key === "e" || e.key === "E") && (e.ctrlKey || e.altKey)) {
        e.preventDefault();
        if (this.adminManager) this.adminManager.open();
      }
    });
  }

  showView(viewName) {
    Object.keys(this.views).forEach(key => {
      if (this.views[key]) this.views[key].classList.remove("active");
    });
    if (this.views[viewName]) {
      this.views[viewName].classList.add("active");
    }
  }

  showHomeCompleted() {
    this.showView("wheel");
    const activeStage = document.getElementById("wheelActiveStage");
    const completedStage = document.getElementById("wheelCompletedStage");

    if (activeStage) activeStage.style.display = "none";
    if (completedStage) completedStage.style.display = "flex";

    try {
      window.history.pushState({ stage: "home_completed" }, "");
    } catch (e) {}
  }

  getActiveHouses() {
    return this.houses.filter(h => !this.revealedHouseIds.includes(h.id));
  }

  updateWheelHouses() {
    const active = this.getActiveHouses();
    this.wheelInstance.setHouses(active);

    const activeStage = document.getElementById("wheelActiveStage");
    const completedStage = document.getElementById("wheelCompletedStage");
    const centerBtn = document.getElementById("btnCenterSpin");
    const countLabel = document.getElementById("remainingCountLabel");

    if (activeStage) activeStage.style.display = "flex";
    if (completedStage) completedStage.style.display = "none";

    if (countLabel) {
      countLabel.textContent = `${active.length} of ${this.houses.length} Remaining`;
    }

    if (active.length === 0) {
      if (centerBtn) {
        centerBtn.disabled = true;
        const textSpan = centerBtn.querySelector('.spin-text');
        if (textSpan) textSpan.textContent = "DONE";
      }
      this.showHomeCompleted();
    } else {
      if (centerBtn) {
        centerBtn.disabled = false;
        const textSpan = centerBtn.querySelector('.spin-text');
        if (textSpan) textSpan.textContent = "SPIN";
      }
    }
  }

  onWheelLanded(selectedHouse) {
    this.currentHouse = selectedHouse;
    this.revealedPostsInCurrent = [];

    const modal = document.getElementById("selectedHouseModal");
    const banner = document.getElementById("selectedHouseBanner");
    const title = document.getElementById("selectedHouseTitle");
    const preLabel = document.getElementById("modalPreLabel");

    if (preLabel) {
      preLabel.textContent = "HOUSE SELECTED";
    }
    if (banner) {
      banner.style.borderTop = `8px solid ${selectedHouse.color}`;
    }
    if (title) {
      title.textContent = selectedHouse.fullName || `${selectedHouse.name} House`;
      title.style.color = selectedHouse.color;
    }

    modal.classList.add("active");

    try {
      window.history.pushState({ stage: "house_modal", houseId: selectedHouse.id }, "");
    } catch (e) {}
  }

  // When only 1 house remains, guide directly to its scratch without wheel spin
  onLastHouseAutoSelected(lastHouse) {
    this.currentHouse = lastHouse;
    this.revealedPostsInCurrent = [];

    const modal = document.getElementById("selectedHouseModal");
    const banner = document.getElementById("selectedHouseBanner");
    const title = document.getElementById("selectedHouseTitle");
    const preLabel = document.getElementById("modalPreLabel");

    if (preLabel) {
      preLabel.textContent = "FINAL HOUSE";
    }
    if (banner) {
      banner.style.borderTop = `8px solid ${lastHouse.color}`;
    }
    if (title) {
      title.textContent = lastHouse.fullName || `${lastHouse.name} House`;
      title.style.color = lastHouse.color;
    }

    this.showView("wheel");
    modal.classList.add("active");

    window.soundEngine.playFanfare();
    window.confettiEngine.burst(window.innerWidth / 2, window.innerHeight * 0.45, 65, [lastHouse.color, "#EAB308", "#111827", "#FFFFFF"]);

    try {
      window.history.pushState({ stage: "house_modal", houseId: lastHouse.id }, "");
    } catch (e) {}
  }

  enterScratchArena(house) {
    this.showView("scratch");

    const scratchHeader = document.getElementById("scratchHouseHeader");
    const scratchTitle = document.getElementById("scratchHouseTitle");
    const nextBtn = document.getElementById("btnNextHouse");

    if (scratchHeader) {
      scratchHeader.style.borderTop = `6px solid ${house.color}`;
    }
    if (scratchTitle) {
      scratchTitle.textContent = house.fullName || `${house.name} House`;
      scratchTitle.style.color = house.color;
    }

    if (nextBtn) {
      nextBtn.disabled = true;
      nextBtn.classList.remove("unlocked");
      nextBtn.innerHTML = `<span>Reveal All 4 Posts</span>`;
    }

    if (this.scratchManager) {
      this.scratchManager.destroy();
    }

    this.scratchManager = new ScratchArenaManager(
      "scratchArenaContainer",
      "scratchSpotlightModal",
      house,
      {
        onPostRevealed: (postKey) => this.onPostCardRevealed(postKey),
        onAllRevealed: () => this.onHouseFullyRevealed()
      }
    );

    try {
      window.history.pushState({ stage: "scratch", houseId: house.id }, "");
    } catch (e) {}
  }

  onPostCardRevealed(postKey) {
    if (!this.revealedPostsInCurrent.includes(postKey)) {
      this.revealedPostsInCurrent.push(postKey);
    }
  }

  onHouseFullyRevealed() {
    const nextBtn = document.getElementById("btnNextHouse");
    const remaining = this.getActiveHouses().filter(h => h.id !== this.currentHouse.id);

    if (nextBtn) {
      nextBtn.disabled = false;
      nextBtn.classList.add("unlocked");
      if (remaining.length === 0) {
        nextBtn.innerHTML = `<span>View Final Cabinet ➔</span>`;
      } else {
        nextBtn.innerHTML = `<span>Next House ➔</span>`;
      }
    }

    // Stage cannons without duplicate fanfare
    window.confettiEngine.stageCannons([this.currentHouse.color, "#EAB308", "#111827", "#FFFFFF"]);
  }

  completeCurrentHouseAndReturn() {
    if (this.currentHouse && !this.revealedHouseIds.includes(this.currentHouse.id)) {
      this.revealedHouseIds.push(this.currentHouse.id);
    }

    if (this.scratchManager) {
      this.scratchManager.destroy();
      this.scratchManager = null;
    }

    this.currentHouse = null;
    this.revealedPostsInCurrent = [];

    const remaining = this.getActiveHouses();

    if (remaining.length === 0) {
      // All 6 houses declared! Go to Finale View
      this.showView("finale");
      this.renderFinale();
      try {
        window.history.pushState({ stage: "finale" }, "");
      } catch (e) {}
    } else {
      // 1 or more houses left: always return to wheel so it can be spun with true random selection
      this.showView("wheel");
      this.updateWheelHouses();
      try {
        window.history.pushState({ stage: "wheel" }, "");
      } catch (e) {}
    }
  }

  renderFinale() {
    window.soundEngine.playFinaleChime();
    window.confettiEngine.stageCannons();

    const finaleGrid = document.getElementById("finaleCabinetGrid");
    if (!finaleGrid) return;

    finaleGrid.innerHTML = "";

    // If Central (School Cabinet) winners exist from Supabase, display full-width header card
    if (window.SupabaseResultsSync && Array.isArray(window.SupabaseResultsSync.centralWinners) && window.SupabaseResultsSync.centralWinners.length > 0) {
      const centralCard = document.createElement("div");
      centralCard.className = "finale-house-panel finale-central-panel";
      centralCard.style.borderTop = "7px solid #059669";
      let centralHtml = "";
      window.SupabaseResultsSync.centralWinners.forEach(cw => {
        centralHtml += `
          <div class="finale-leader-row">
            <div class="finale-post-col" style="color: #065f46; font-weight: 700;">${cw.postTitle}</div>
            <div class="finale-name-col">${cw.winnerName}</div>
            <div class="finale-grade-col"><span class="finale-grade-badge" style="background:#ecfdf5; color:#065f46; border:1px solid rgba(5,150,105,0.3); font-weight: 700;">${cw.grade}</span></div>
          </div>
        `;
      });
      centralCard.innerHTML = `
        <div class="finale-house-header" style="display:flex; justify-content:space-between; align-items:center;">
          <h3 style="color: #059669; font-size: 1.35rem; font-weight: 800;">🏛️ School Cabinet (Central Council)</h3>
          <span style="font-size: 0.75rem; font-weight: 700; color: #047857; background: #ecfdf5; padding: 0.25rem 0.65rem; border-radius: 999px; border: 1px solid rgba(5,150,105,0.3);">Apex Leadership</span>
        </div>
        <div class="finale-leaders-list" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 0.5rem 1.75rem;">
          ${centralHtml}
        </div>
      `;
      finaleGrid.appendChild(centralCard);
    }

    this.houses.forEach(house => {
      const houseCard = document.createElement("div");
      houseCard.className = "finale-house-panel";
      houseCard.style.borderTop = `7px solid ${house.color}`;

      let candidatesHtml = "";
      POST_KEYS.forEach(pk => {
        const c = house.candidates[pk];
        const meta = POST_METADATA[pk];
        candidatesHtml += `
          <div class="finale-leader-row">
            <div class="finale-post-col">${meta.title}</div>
            <div class="finale-name-col">${c.name}</div>
            <div class="finale-grade-col"><span class="finale-grade-badge">${c.grade}</span></div>
          </div>
        `;
      });

      houseCard.innerHTML = `
        <div class="finale-house-header">
          <h3 style="color: ${house.color};">${house.fullName || house.name + ' House'}</h3>
        </div>
        <div class="finale-leaders-list">
          ${candidatesHtml}
        </div>
      `;
      finaleGrid.appendChild(houseCard);
    });
  }

  resetProgress() {
    this.revealedHouseIds = [];
    this.currentHouse = null;
    this.revealedPostsInCurrent = [];
    this.updateWheelHouses();
    this.showView("wheel");
    try {
      window.history.pushState({ stage: "wheel" }, "");
    } catch (e) {}
  }

  saveCustomData() {
    try {
      localStorage.setItem(this.customDataKey, JSON.stringify(this.houses));
      this.updateWheelHouses();
    } catch (e) {
      // ignore
    }
  }

  loadCustomData() {
    try {
      const saved = localStorage.getItem(this.customDataKey);
      if (saved) {
        return JSON.parse(saved);
      }
    } catch (e) {
      // ignore
    }
    return null;
  }

  resetAllDataToDefaults() {
    localStorage.removeItem(this.customDataKey);
    this.houses = JSON.parse(JSON.stringify(DEFAULT_HOUSES));
    this.resetProgress();
  }
}

window.addEventListener("DOMContentLoaded", () => {
  window.app = new ElectionApp();
});
