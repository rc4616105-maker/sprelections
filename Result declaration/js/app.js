/**
 * Master Application Controller
 * Handles two-phase ceremony (House Councils -> School Cabinet),
 * view transitions, elimination logic, zero-scroll direct navigation on the 6th house
 * and 5th cabinet post, and the complete Grand Finale.
 */

class ElectionApp {
  constructor() {
    this.customDataKey = "SCHOOL_ELECTION_2026_CUSTOM_DATA_V5";

    // 1. House Data
    this.houses = this.loadCustomData() || JSON.parse(JSON.stringify(DEFAULT_HOUSES));
    const CANONICAL_NAMES = {
      bheeshma: "Bheeshma",
      gurudrona: "Gurudrona",
      hanuman: "Hanuman",
      karna: "Karna",
      vasistha: "Vasistha",
      vishwamithra: "Vishwamithra",
    };
    if (Array.isArray(this.houses)) {
      this.houses.forEach(h => {
        if (h.id === "vasishta") h.id = "vasistha";
        if (CANONICAL_NAMES[h.id]) h.name = CANONICAL_NAMES[h.id];
      });
    }
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

    // 4. Start clean at the wheel (check if URL specifies #cabinet, ?mode=cabinet, or ?phase=cabinet)
    const urlParams = new URLSearchParams(window.location.search);
    const isCabinetMode = window.location.hash === "#cabinet" || urlParams.get("phase") === "cabinet" || urlParams.get("mode") === "cabinet";
    if (isCabinetMode) {
      this.switchCeremonyPhase("cabinet");
    } else {
      this.switchCeremonyPhase("houses");
    }

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
    // Wheel Ceremony Mode Switcher (Houses vs School Cabinet)
    const tabHouses = document.getElementById("tabModeHouses");
    if (tabHouses) {
      tabHouses.addEventListener("click", () => this.switchCeremonyPhase("houses"));
    }
    const tabCabinet = document.getElementById("tabModeCabinet");
    if (tabCabinet) {
      tabCabinet.addEventListener("click", () => this.switchCeremonyPhase("cabinet"));
    }

    const btnLaunchCabinetFromHome = document.getElementById("btnLaunchCabinetFromHome");
    if (btnLaunchCabinetFromHome) {
      btnLaunchCabinetFromHome.addEventListener("click", () => {
        this.switchCeremonyPhase("cabinet");
      });
    }

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

  switchCeremonyPhase(phase) {
    this.ceremonyPhase = phase; // "houses" | "cabinet"

    const tabHouses = document.getElementById("tabModeHouses");
    const tabCabinet = document.getElementById("tabModeCabinet");
    if (tabHouses && tabCabinet) {
      tabHouses.classList.toggle("active", phase === "houses");
      tabCabinet.classList.toggle("active", phase === "cabinet");
      tabCabinet.classList.toggle("is-cabinet", phase === "cabinet");
      tabHouses.setAttribute("aria-selected", phase === "houses" ? "true" : "false");
      tabCabinet.setAttribute("aria-selected", phase === "cabinet" ? "true" : "false");
    }

    const stageTitle = document.getElementById("wheelStageTitle");
    if (stageTitle) {
      stageTitle.textContent = phase === "cabinet" ? "School Cabinet Selection Wheel" : "House Selection Wheel";
    }

    this.showView("wheel");
    this.updateWheel();
  }

  showHomeCompleted() {
    this.showView("wheel");
    const activeStage = document.getElementById("wheelActiveStage");
    const completedStage = document.getElementById("wheelCompletedStage");
    const title = document.getElementById("completedStageTitle");
    const desc = document.getElementById("completedStageDesc");

    if (activeStage) activeStage.style.display = "none";
    if (completedStage) completedStage.style.display = "flex";

    if (this.ceremonyPhase === "cabinet") {
      if (title) title.textContent = "Results of All 5 Cabinet Posts Declared Successfully";
      if (desc) desc.textContent = "All 5 School Cabinet Apex Leaders have been officially declared.";
    } else {
      if (title) title.textContent = "Results of All 6 Houses Declared Successfully";
      if (desc) desc.textContent = "All 24 House Captains & Vice Captains have been officially declared.";
    }

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
      // Save the 24 elected house winners to localStorage for the School Cabinet Electoral College
      try {
        const twentyFourWinners = [];
        const activeKeys = (Array.isArray(window.POST_KEYS) && window.POST_KEYS.length > 0) ? window.POST_KEYS : ["boys_captain", "girls_captain", "boys_vc", "girls_vc"];
        this.houses.forEach((house) => {
          activeKeys.forEach((pk) => {
            const c = house.candidates && house.candidates[pk];
            const meta = (window.POST_METADATA && window.POST_METADATA[pk]) || {};
            if (c) {
              twentyFourWinners.push({
                houseCode: (house.id || "").toUpperCase(),
                houseName: house.fullName || `${house.name} House`,
                postKey: pk,
                postTitle: meta.title || pk,
                fullName: c.name,
                grade: c.grade,
                photo: c.photo || "",
                admissionNo: c.admissionNo || "",
              });
            }
          });
        });
        localStorage.setItem("ELECTED_HOUSE_WINNERS_2026", JSON.stringify(twentyFourWinners));
        console.info("[ResultDeclaration] Saved 24 elected house winners for School Cabinet.", twentyFourWinners);
      } catch (e) {
        console.warn("Could not save 24 winners to localStorage:", e);
      }

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
    const finaleGrid = document.getElementById("finaleCabinetGrid");

    if (!finaleGrid) return;
    finaleGrid.innerHTML = "";

    if (this.ceremonyPhase === "cabinet") {
      if (mainTitle) mainTitle.textContent = "Official Elected School Cabinet 2026";
      if (subTitle) subTitle.textContent = "Congratulations to the apex student leaders of SPR School of Excellence";

      this.cabinetPosts.forEach((post) => {
        const c = post.candidate || { name: "Leader Elect", grade: post.grade || "Class 10", quote: "" };
        const postCard = document.createElement("div");
        postCard.className = "finale-house-panel";
        postCard.style.borderTop = `7px solid ${post.color || "#059669"}`;
        postCard.innerHTML = `
          <div class="finale-house-header">
            <div>
              <span class="sub-tagline" style="color:${post.color || '#059669'}; font-weight:800; font-size:0.75rem;">APEX CABINET POST</span>
              <h3 style="color:${post.color || '#059669'}; margin:0.15rem 0 0; font-size:1.2rem;">${post.fullName || post.name}</h3>
            </div>
            <span class="finale-star-badge" style="background:${post.color || '#059669'}; color:#fff; padding:0.25rem 0.65rem; border-radius:9999px; font-size:0.75rem; font-weight:800;">⭐ ELECTED</span>
          </div>
          <div style="padding:1.25rem; display:flex; align-items:center; gap:1.15rem;">
            <div style="width:68px; height:68px; border-radius:50%; overflow:hidden; border:3px solid ${post.color || '#059669'}; flex-shrink:0; background:#f1f5f9; display:flex; align-items:center; justify-content:center;">
              ${c.photo ? `<img src="${c.photo}" alt="${c.name}" style="width:100%; height:100%; object-fit:cover;" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';" /><div style="display:none; font-weight:800; font-size:1.4rem; color:#475569;">⭐</div>` : `<div style="font-weight:800; font-size:1.4rem; color:#475569;">⭐</div>`}
            </div>
            <div style="flex:1; min-width:0;">
              <h4 style="font-size:1.15rem; font-weight:800; color:#0f172a; margin:0 0 0.2rem;">${c.name}</h4>
              <p style="font-size:0.85rem; font-weight:600; color:#64748b; margin:0 0 0.35rem;">${c.grade || "Class 10"}</p>
              <p style="font-size:0.8rem; font-style:italic; color:#475569; margin:0; line-height:1.35;">&ldquo;${c.quote || "Dedicated to student excellence and school governance."}&rdquo;</p>
            </div>
          </div>
        `;
        finaleGrid.appendChild(postCard);
      });
      return;
    }

    if (mainTitle) mainTitle.textContent = "Official Elected House Leadership 2026";
    if (subTitle) subTitle.textContent = "Congratulations to the 24 elected Captains & Vice Captains across all 6 Houses";

    // Render 6 Houses
    this.houses.forEach(house => {
      const houseCard = document.createElement("div");
      houseCard.className = "finale-house-panel";
      houseCard.style.borderTop = `7px solid ${house.color}`;

      let candidatesHtml = "";
      const activeKeys = (Array.isArray(window.POST_KEYS) && window.POST_KEYS.length > 0) ? window.POST_KEYS : ["boys_captain", "girls_captain", "boys_vc", "girls_vc"];
      activeKeys.forEach(pk => {
        const c = (house.candidates && house.candidates[pk]) || { name: "Contestant", grade: "Class 10" };
        const meta = (window.POST_METADATA && window.POST_METADATA[pk]) || { title: pk };
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
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed)) {
          const CANONICAL_NAMES = {
            bheeshma: "Bheeshma",
            gurudrona: "Gurudrona",
            hanuman: "Hanuman",
            karna: "Karna",
            vasistha: "Vasistha",
            vishwamithra: "Vishwamithra",
          };
          parsed.forEach(h => {
            if (h.id === "vasishta") h.id = "vasistha";
            if (CANONICAL_NAMES[h.id]) h.name = CANONICAL_NAMES[h.id];
            if (h.candidates) {
              Object.values(h.candidates).forEach((c) => {
                if (c && typeof c.photo === "string") {
                  c.photo = c.photo.trim().replace(/^\.\.\/assets\//, "assets/").replace(/^\.\/assets\//, "assets/");
                }
                if (c && !c.photo && Array.isArray(window.ALL_CONTESTING_CANDIDATES) && c.name) {
                  const norm = (s) => String(s || "").toLowerCase().replace(/[\s\.\-_]+/g, "");
                  const found = window.ALL_CONTESTING_CANDIDATES.find((x) => norm(x.fullName) === norm(c.name) && String(x.houseCode || "").toUpperCase() === String(h.id || "").toUpperCase())
                    || window.ALL_CONTESTING_CANDIDATES.find((x) => norm(x.fullName) === norm(c.name));
                  if (found) c.photo = String(found.photoPath || found.photoUrl || "").replace(/^\.\.\/assets\//, "assets/");
                }
              });
            }
          });
          return parsed;
        }
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

function syncResultPauseLock() {
  const lockOverlay = document.getElementById("result-pause-lock-overlay");
  if (!lockOverlay) return false;
  let isClosed = false;
  try {
    isClosed = localStorage.getItem("ELECTION_HOUSE_POLLING_CLOSED") === "true";
  } catch (_) {}
  lockOverlay.hidden = isClosed;
  lockOverlay.style.display = isClosed ? "none" : "flex";
  return isClosed;
}

window.addEventListener("DOMContentLoaded", () => {
  let wasClosed = syncResultPauseLock();
  window.app = new ElectionApp();

  const onSync = () => {
    const isClosedNow = syncResultPauseLock();
    if (!wasClosed && isClosedNow) {
      // Newly paused & tallied by Admin — reload to pull fresh 24 winners!
      window.location.reload();
    }
    wasClosed = isClosedNow;
  };

  window.addEventListener("storage", (e) => {
    if (!e.key || e.key === "ELECTION_HOUSE_POLLING_CLOSED" || e.key === "SCHOOL_ELECTION_2026_CUSTOM_DATA_V5") {
      onSync();
    }
  });
  if (typeof BroadcastChannel !== "undefined") {
    try {
      const bc = new BroadcastChannel("election_spr_2026_sync");
      bc.onmessage = () => onSync();
    } catch (_) {}
  }
  setInterval(onSync, 1000);
});
