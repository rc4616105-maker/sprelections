/**
 * Master Application Controller
 * Handles two-phase ceremony (House Councils -> School Cabinet),
 * view transitions, elimination logic, zero-scroll direct navigation on the 6th house
 * and 5th cabinet post, and the complete Grand Finale.
 */

class ElectionApp {
  constructor() {
    this.customDataKey = "SCHOOL_ELECTION_2026_CUSTOM_DATA_V4";

    // 1. House Data
    this.houses = this.loadCustomData() || JSON.parse(JSON.stringify(DEFAULT_HOUSES));
    this.revealedHouseIds = [];
    this.currentHouse = null;
    this.revealedPostsInCurrent = [];

    // 2. School Cabinet (Central Council) Data & Phase
    this.ceremonyPhase = "houses"; // "houses" | "cabinet"
    this.cabinetPosts = (typeof DEFAULT_CABINET_POSTS !== "undefined")
      ? JSON.parse(JSON.stringify(DEFAULT_CABINET_POSTS))
      : [];
    this.revealedCabinetPostIds = [];
    this.currentCabinetPost = null;

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
      onSelect: (selectedItem) => {
        if (this.ceremonyPhase === "cabinet") {
          this.onCabinetWheelLanded(selectedItem);
        } else {
          this.onWheelLanded(selectedItem);
        }
      }
    });
    this.updateWheel();

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
          }
          if (window.SupabaseResultsSync.centralWinners && window.SupabaseResultsSync.centralWinners.length > 0) {
            this.cabinetPosts = window.SupabaseResultsSync.centralWinners;
          }
          this.updateWheel();
        })
        .catch((err) => {
          console.warn("Background Supabase live tally fetch error:", err);
        });
    }
  }

  initHistoryNavigation() {
    try {
      window.history.replaceState({ stage: "wheel" }, "");
    } catch (e) {}

    window.addEventListener("popstate", (e) => {
      const spotlightModal = document.getElementById("scratchSpotlightModal");
      const houseModal = document.getElementById("selectedHouseModal");

      // 1. If spotlight card is open, Chrome Back closes it and returns to scratch arena
      if (spotlightModal && spotlightModal.classList.contains("active")) {
        if (this.scratchManager) {
          this.scratchManager.closeSpotlight();
        }
        return;
      }

      // 2. If Selection popup is open, Chrome Back dismisses it
      if (houseModal && houseModal.classList.contains("active")) {
        houseModal.classList.remove("active");
        this.currentHouse = null;
        this.currentCabinetPost = null;
        return;
      }

      // 3. If in Scratch Arena, Chrome Back returns to the Wheel stage
      if (this.views.scratch && this.views.scratch.classList.contains("active")) {
        if (this.scratchManager) {
          this.scratchManager.destroy();
          this.scratchManager = null;
        }
        this.currentHouse = null;
        this.currentCabinetPost = null;
        this.showView("wheel");
        this.updateWheel();
        return;
      }

      // 4. If in Finale or Completed Stage, Chrome Back returns to Wheel
      if (this.views.finale && this.views.finale.classList.contains("active")) {
        this.showView("wheel");
        this.updateWheel();
        return;
      }

      const state = e.state;
      if (state && state.stage) {
        if (state.stage === "wheel") {
          this.showView("wheel");
          this.updateWheel();
        }
      }
    });
  }

  attachEvents() {
    // "Show Results / Reveal Winner" button from selection modal
    const btnProceedToResults = document.getElementById("btnProceedToResults");
    if (btnProceedToResults) {
      btnProceedToResults.addEventListener("click", () => {
        const modal = document.getElementById("selectedHouseModal");
        if (modal) modal.classList.remove("active");
        if (this.ceremonyPhase === "cabinet" && this.currentCabinetPost) {
          this.enterCabinetScratchArena(this.currentCabinetPost);
        } else if (this.currentHouse) {
          this.enterScratchArena(this.currentHouse);
        }
      });
    }

    // "Next House / Next Post" button from scratch view
    const btnNextHouse = document.getElementById("btnNextHouse");
    if (btnNextHouse) {
      btnNextHouse.addEventListener("click", () => {
        if (this.ceremonyPhase === "cabinet") {
          this.completeCurrentCabinetPostAndProceed();
        } else {
          this.completeCurrentHouseAndReturn();
        }
      });
    }

    // "Reveal School Cabinet Posts ➔" button on Finale view
    const btnLaunchCabinetPhase = document.getElementById("btnLaunchCabinetPhase");
    if (btnLaunchCabinetPhase) {
      btnLaunchCabinetPhase.addEventListener("click", () => {
        this.startCabinetPhase();
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

  getActiveCabinetPosts() {
    return this.cabinetPosts.filter(p => !this.revealedCabinetPostIds.includes(p.id));
  }

  updateWheel() {
    if (this.ceremonyPhase === "cabinet") {
      this.updateCabinetWheel();
    } else {
      this.updateWheelHouses();
    }
  }

  updateWheelHouses() {
    const active = this.getActiveHouses();
    this.wheelInstance.setHouses(active);

    const activeStage = document.getElementById("wheelActiveStage");
    const completedStage = document.getElementById("wheelCompletedStage");
    const centerBtn = document.getElementById("btnCenterSpin");
    const stageTitle = document.getElementById("wheelStageTitle");
    const countLabel = document.getElementById("remainingCountLabel");

    if (activeStage) activeStage.style.display = "flex";
    if (completedStage) completedStage.style.display = "none";

    if (stageTitle) {
      stageTitle.textContent = "House Selection Wheel";
    }

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

  updateCabinetWheel() {
    const active = this.getActiveCabinetPosts();
    this.wheelInstance.setHouses(active);

    const activeStage = document.getElementById("wheelActiveStage");
    const completedStage = document.getElementById("wheelCompletedStage");
    const centerBtn = document.getElementById("btnCenterSpin");
    const stageTitle = document.getElementById("wheelStageTitle");
    const countLabel = document.getElementById("remainingCountLabel");

    if (activeStage) activeStage.style.display = "flex";
    if (completedStage) completedStage.style.display = "none";

    if (stageTitle) {
      stageTitle.textContent = "School Cabinet Selection Wheel";
    }

    if (countLabel) {
      countLabel.textContent = `${active.length} of ${this.cabinetPosts.length} Remaining`;
    }

    if (active.length === 0) {
      if (centerBtn) {
        centerBtn.disabled = true;
        const textSpan = centerBtn.querySelector('.spin-text');
        if (textSpan) textSpan.textContent = "DONE";
      }
      this.showView("finale");
      this.renderFinale();
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
    const btnProceed = document.getElementById("btnProceedToResults");

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
    if (btnProceed) {
      btnProceed.innerHTML = `<span>Show Results ➔</span>`;
    }

    modal.classList.add("active");

    try {
      window.history.pushState({ stage: "house_modal", houseId: selectedHouse.id }, "");
    } catch (e) {}
  }

  enterScratchArena(house) {
    this.showView("scratch");

    const scratchHeader = document.getElementById("scratchHouseHeader");
    const scratchTitle = document.getElementById("scratchHouseTitle");
    const preLabel = scratchHeader ? scratchHeader.querySelector(".house-pre-label") : null;
    const nextBtn = document.getElementById("btnNextHouse");

    if (preLabel) {
      preLabel.textContent = "HOUSE RESULTS";
    }
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
        isCabinet: false,
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
        nextBtn.innerHTML = `<span>View House Leadership Finale ➔</span>`;
      } else if (remaining.length === 1) {
        nextBtn.innerHTML = `<span>Final House: ${remaining[0].name} ➔</span>`;
      } else {
        nextBtn.innerHTML = `<span>Next House ➔</span>`;
      }
    }

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
      // All 6 houses declared! Go to House Leadership Finale
      this.showView("finale");
      this.renderFinale();
      try {
        window.history.pushState({ stage: "finale" }, "");
      } catch (e) {}
    } else if (remaining.length === 1) {
      // Exactly 1 house remains: skip wheel scrolling/spinning and show final house scratch cards directly!
      const lastHouse = remaining[0];
      this.currentHouse = lastHouse;
      this.revealedPostsInCurrent = [];
      this.enterScratchArena(lastHouse);
      window.soundEngine.playFanfare();
      window.confettiEngine.burst(window.innerWidth / 2, window.innerHeight * 0.45, 65, [lastHouse.color, "#EAB308", "#111827", "#FFFFFF"]);
      try {
        window.history.pushState({ stage: "scratch", houseId: lastHouse.id }, "");
      } catch (e) {}
    } else {
      // 2 or more houses left: return to wheel to spin
      this.showView("wheel");
      this.updateWheel();
      try {
        window.history.pushState({ stage: "wheel" }, "");
      } catch (e) {}
    }
  }

  // =======================================================
  // PHASE 2: SCHOOL CABINET (CENTRAL COUNCIL) CEREMONY
  // =======================================================

  startCabinetPhase() {
    this.ceremonyPhase = "cabinet";
    this.currentHouse = null;
    this.currentCabinetPost = null;

    window.soundEngine.playFanfare();
    window.confettiEngine.stageCannons(["#059669", "#0D9488", "#7C3AED", "#EA580C", "#D97706"]);

    this.showView("wheel");
    this.updateCabinetWheel();

    try {
      window.history.pushState({ stage: "cabinet_wheel" }, "");
    } catch (e) {}
  }

  onCabinetWheelLanded(selectedPost) {
    this.currentCabinetPost = selectedPost;

    const modal = document.getElementById("selectedHouseModal");
    const banner = document.getElementById("selectedHouseBanner");
    const title = document.getElementById("selectedHouseTitle");
    const preLabel = document.getElementById("modalPreLabel");
    const btnProceed = document.getElementById("btnProceedToResults");

    if (preLabel) {
      preLabel.textContent = "APEX CABINET POST SELECTED";
    }
    if (banner) {
      banner.style.borderTop = `8px solid ${selectedPost.color || '#059669'}`;
    }
    if (title) {
      title.textContent = selectedPost.fullName || selectedPost.postTitle || selectedPost.name;
      title.style.color = selectedPost.color || '#059669';
    }
    if (btnProceed) {
      btnProceed.innerHTML = `<span>Reveal Winner ➔</span>`;
    }

    modal.classList.add("active");

    try {
      window.history.pushState({ stage: "cabinet_modal", postId: selectedPost.id }, "");
    } catch (e) {}
  }

  enterCabinetScratchArena(post) {
    this.showView("scratch");

    const scratchHeader = document.getElementById("scratchHouseHeader");
    const scratchTitle = document.getElementById("scratchHouseTitle");
    const preLabel = scratchHeader ? scratchHeader.querySelector(".house-pre-label") : null;
    const nextBtn = document.getElementById("btnNextHouse");

    if (preLabel) {
      preLabel.textContent = "🏛️ APEX LEADERSHIP · SCHOOL CABINET";
    }
    if (scratchHeader) {
      scratchHeader.style.borderTop = `6px solid ${post.color || '#059669'}`;
    }
    if (scratchTitle) {
      scratchTitle.textContent = post.fullName || post.postTitle || post.name;
      scratchTitle.style.color = post.color || '#059669';
    }

    if (nextBtn) {
      nextBtn.disabled = true;
      nextBtn.classList.remove("unlocked");
      nextBtn.innerHTML = `<span>Scratch to Reveal Winner</span>`;
    }

    if (this.scratchManager) {
      this.scratchManager.destroy();
    }

    this.scratchManager = new ScratchArenaManager(
      "scratchArenaContainer",
      "scratchSpotlightModal",
      post,
      {
        isCabinet: true,
        onAllRevealed: () => this.onCabinetPostFullyRevealed(post)
      }
    );

    try {
      window.history.pushState({ stage: "scratch_cabinet", postId: post.id }, "");
    } catch (e) {}
  }

  onCabinetPostFullyRevealed(post) {
    const nextBtn = document.getElementById("btnNextHouse");
    const remaining = this.getActiveCabinetPosts().filter(p => p.id !== post.id);

    if (nextBtn) {
      nextBtn.disabled = false;
      nextBtn.classList.add("unlocked");
      if (remaining.length === 0) {
        nextBtn.innerHTML = `<span>View Complete Grand Finale ➔</span>`;
      } else if (remaining.length === 1) {
        nextBtn.innerHTML = `<span>Final Post: ${remaining[0].name} ➔</span>`;
      } else {
        nextBtn.innerHTML = `<span>Next Cabinet Post ➔</span>`;
      }
    }

    window.confettiEngine.stageCannons([post.color || "#059669", "#EAB308", "#111827", "#FFFFFF"]);
  }

  completeCurrentCabinetPostAndProceed() {
    if (this.currentCabinetPost && !this.revealedCabinetPostIds.includes(this.currentCabinetPost.id)) {
      this.revealedCabinetPostIds.push(this.currentCabinetPost.id);
    }

    if (this.scratchManager) {
      this.scratchManager.destroy();
      this.scratchManager = null;
    }

    this.currentCabinetPost = null;

    const remaining = this.getActiveCabinetPosts();

    if (remaining.length === 0) {
      // All 5 School Cabinet posts declared! Show full Grand Finale
      this.showView("finale");
      this.renderFinale();
      try {
        window.history.pushState({ stage: "finale" }, "");
      } catch (e) {}
    } else if (remaining.length === 1) {
      // Exactly 1 Cabinet post remains: skip wheel scrolling/spinning and show final card directly!
      const lastPost = remaining[0];
      this.currentCabinetPost = lastPost;
      this.enterCabinetScratchArena(lastPost);
      window.soundEngine.playFanfare();
      window.confettiEngine.burst(window.innerWidth / 2, window.innerHeight * 0.45, 65, [lastPost.color || "#059669", "#EAB308", "#111827", "#FFFFFF"]);
      try {
        window.history.pushState({ stage: "scratch_cabinet", postId: lastPost.id }, "");
      } catch (e) {}
    } else {
      // 2 or more posts left: return to wheel to spin
      this.showView("wheel");
      this.updateCabinetWheel();
      try {
        window.history.pushState({ stage: "cabinet_wheel" }, "");
      } catch (e) {}
    }
  }

  // =======================================================
  // FINALE RENDERING (House Councils vs. Complete Cabinet)
  // =======================================================

  renderFinale() {
    window.soundEngine.playFinaleChime();
    window.confettiEngine.stageCannons();

    const mainTitle = document.getElementById("finaleMainTitle");
    const subTitle = document.getElementById("finaleSubTitle");
    const cabinetLaunchBanner = document.getElementById("cabinetLaunchBanner");
    const finaleGrid = document.getElementById("finaleCabinetGrid");

    if (!finaleGrid) return;
    finaleGrid.innerHTML = "";

    const isCompleteGrandFinale = (this.ceremonyPhase === "cabinet" && this.revealedCabinetPostIds.length >= this.cabinetPosts.length);

    if (isCompleteGrandFinale) {
      // 1. COMPLETE GRAND FINALE (Both School Cabinet & 6 Houses)
      if (mainTitle) mainTitle.textContent = "Elected Student Council & Cabinet 2026";
      if (subTitle) subTitle.textContent = "Official School Leadership Team 2026 · Central Cabinet & House Councils";
      if (cabinetLaunchBanner) cabinetLaunchBanner.style.display = "none";

      // Render School Cabinet apex card at top
      const centralCard = document.createElement("div");
      centralCard.className = "finale-house-panel finale-central-panel";
      centralCard.style.borderTop = "7px solid #059669";

      let centralHtml = "";
      this.cabinetPosts.forEach(cp => {
        const c = cp.candidate || {};
        const winnerName = c.name || cp.winnerName || "Elected Leader";
        const grade = c.grade || cp.grade || "Class 10";
        const postTitle = cp.fullName || cp.postTitle || cp.name;

        centralHtml += `
          <div class="finale-leader-row">
            <div class="finale-post-col" style="color: #065f46; font-weight: 700;">${postTitle}</div>
            <div class="finale-name-col">${winnerName}</div>
            <div class="finale-grade-col"><span class="finale-grade-badge" style="background:#ecfdf5; color:#065f46; border:1px solid rgba(5,150,105,0.3); font-weight: 700;">${grade}</span></div>
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

    } else {
      // 2. HOUSE LEADERSHIP FINALE (6 Houses Revealed, School Cabinet Launch Banner Prompt)
      if (mainTitle) mainTitle.textContent = "Elected House Leadership 2026";
      if (subTitle) subTitle.textContent = "Congratulations to the elected representatives of all 6 houses";
      if (cabinetLaunchBanner) cabinetLaunchBanner.style.display = "flex";
    }

    // Render 6 Houses
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
    this.ceremonyPhase = "houses";
    this.revealedHouseIds = [];
    this.currentHouse = null;
    this.revealedPostsInCurrent = [];
    this.revealedCabinetPostIds = [];
    this.currentCabinetPost = null;
    this.updateWheel();
    this.showView("wheel");
    try {
      window.history.pushState({ stage: "wheel" }, "");
    } catch (e) {}
  }

  saveCustomData() {
    try {
      localStorage.setItem(this.customDataKey, JSON.stringify(this.houses));
      this.updateWheel();
    } catch (e) {}
  }

  loadCustomData() {
    try {
      const saved = localStorage.getItem(this.customDataKey);
      if (saved) {
        return JSON.parse(saved);
      }
    } catch (e) {}
    return null;
  }

  resetAllDataToDefaults() {
    localStorage.removeItem(this.customDataKey);
    this.houses = JSON.parse(JSON.stringify(DEFAULT_HOUSES));
    this.cabinetPosts = JSON.parse(JSON.stringify(DEFAULT_CABINET_POSTS));
    this.resetProgress();
  }
}

window.addEventListener("DOMContentLoaded", () => {
  window.app = new ElectionApp();
});
