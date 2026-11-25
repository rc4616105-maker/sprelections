(function () {
  function startGraphs() {
    if (!window.ADMIN_DATA || !window.ADMIN_DATA.houses) {
      setTimeout(startGraphs, 50);
      return;
    }

    const { houses } = window.ADMIN_DATA;
    const params = new URLSearchParams(window.location.search);
    const homeLink = document.getElementById("home-link");
    if (homeLink) {
      if (params.get("from") === "admin") {
        homeLink.href = "./admin/index.html";
        homeLink.title = "Click to return to Election Administration";
      } else {
        homeLink.href = "./index.html";
        homeLink.title = "Click to return to Houses index";
      }
    }

    function toggleFullscreen() {
      if (!document.fullscreenElement) {
        if (document.documentElement.requestFullscreen) {
          document.documentElement.requestFullscreen().catch(() => {});
        } else if (document.documentElement.webkitRequestFullscreen) {
          document.documentElement.webkitRequestFullscreen();
        }
      } else {
        if (document.exitFullscreen) {
          document.exitFullscreen().catch(() => {});
        } else if (document.webkitExitFullscreen) {
          document.webkitExitFullscreen();
        }
      }
    }

    document.addEventListener("dblclick", (e) => {
      if (e.target.closest("a, button, input, select, textarea")) return;
      toggleFullscreen();
    });

    const el = {
      voted: document.getElementById("g-voted"),
      pct: document.getElementById("g-pct"),
      boysVoted: document.getElementById("g-boys-voted"),
      boysPct: document.getElementById("g-boys-pct"),
      girlsVoted: document.getElementById("g-girls-voted"),
      girlsPct: document.getElementById("g-girls-pct"),
      remaining: document.getElementById("g-remaining"),

      chartGrid: document.getElementById("unified-chart-grid"),
      labelsGrid: document.getElementById("unified-labels-grid"),
    };

    // Official Constituency mapping from House document
    const CONSTITUENCIES = {
      BHEESHMA: "Gangotri",
      GURUDRONA: "Trimbakeshwar",
      HANUMAN: "Yamunotri",
      KARNA: "Manasarovar",
      VASISTHA: "Mahabaleshwar",
      VISHWAMITHRA: "Amarkantak",
    };

    const sixHouses = houses.filter((h) => h.code !== "ALL" && h.code !== "CENTRAL");
    const houseNodes = new Map();

    const prevCounts = new Map();
    let prevTotalVoted = null;
    let isMounted = false;

    function isBoyStudent(s) {
      const g = String(s?.gender || "").trim().toUpperCase();
      return g === "M" || g === "BOY" || g === "MALE";
    }
    function isGirlStudent(s) {
      const g = String(s?.gender || "").trim().toUpperCase();
      return g === "F" || g === "GIRL" || g === "FEMALE";
    }

    // Build DOM Nodes: House Name, Constituency & Total ABOVE both graphs; Boys/Girls counts BELOW
    function initNodes() {
      if (!el.chartGrid || !el.labelsGrid) return;
      el.chartGrid.innerHTML = "";
      el.labelsGrid.innerHTML = "";
      houseNodes.clear();

      sixHouses.forEach((h) => {
        const constituency = CONSTITUENCIES[h.code] || "";

        // Cluster column for this house
        const clusterCol = document.createElement("div");
        clusterCol.className = "house-bar-cluster";

        clusterCol.innerHTML = `
          <!-- Top Header above both graphs: House Name + Constituency + Total -->
          <div class="house-cluster-header">
            <span class="house-cluster-title" style="color: ${h.accentText};">${h.name}</span>
            <span class="house-constituency-pill" title="Constituency: ${constituency}">${constituency}</span>
            <span class="house-total-badge total-badge">0 / 0 Total (0%)</span>
          </div>

          <div class="bars-pair-container">
            <!-- Boys Bar Unit -->
            <div class="single-bar-unit unit-boys" title="${h.name} Boys (${constituency})">
              <div class="bar-track">
                <div class="bar-fill bar-fill-boys" style="background: ${h.accent}; --bar-scale: 0.035; --bar-opacity: 0.24;"></div>
              </div>
            </div>

            <!-- Girls Bar Unit -->
            <div class="single-bar-unit unit-girls" title="${h.name} Girls (${constituency})">
              <div class="bar-track">
                <div class="bar-fill bar-fill-girls" style="background: ${h.accent}; --bar-scale: 0.035; --bar-opacity: 0.24;"></div>
              </div>
            </div>
          </div>
        `;
        el.chartGrid.appendChild(clusterCol);

        // Labels Grid directly below the baseline for Boys & Girls breakdown
        const labelCol = document.createElement("div");
        labelCol.className = "house-cluster-label";
        labelCol.innerHTML = `
          <div class="gender-sub-row">
            <div class="gender-sub-unit">
              <span class="gender-badge-down">Boys</span>
              <span class="sub-fraction b-fraction">0 / 0</span>
              <span class="sub-pct b-pct">0%</span>
            </div>
            <div class="gender-sub-unit">
              <span class="gender-badge-down">Girls</span>
              <span class="sub-fraction g-fraction">0 / 0</span>
              <span class="sub-pct g-pct">0%</span>
            </div>
          </div>
        `;
        el.labelsGrid.appendChild(labelCol);

        houseNodes.set(h.code, {
          clusterCol,
          totalBadge: clusterCol.querySelector(".total-badge"),

          boysUnit: clusterCol.querySelector(".unit-boys"),
          bFill: clusterCol.querySelector(".bar-fill-boys"),
          bFraction: labelCol.querySelector(".b-fraction"),
          bPct: labelCol.querySelector(".b-pct"),

          girlsUnit: clusterCol.querySelector(".unit-girls"),
          gFill: clusterCol.querySelector(".bar-fill-girls"),
          gFraction: labelCol.querySelector(".g-fraction"),
          gPct: labelCol.querySelector(".g-pct"),
        });
      });
    }

    function triggerPulse(nodeList, className, durationMs) {
      nodeList.forEach((n) => {
        if (!n) return;
        n.classList.remove(className);
        void n.offsetWidth;
        n.classList.add(className);
        setTimeout(() => n.classList.remove(className), durationMs);
      });
    }

    function updateGraphInPlace(snap) {
      const sixHouseCodes = new Set(sixHouses.map((h) => h.code));
      const allStudents = (snap && snap.students && snap.students.length > 0) ? snap.students : (window.ADMIN_DATA?.students || []);
      const allAcceptedBallots = (snap && snap.ballots ? snap.ballots : []).filter((b) => b.status === "accepted" || !b.status);
      const allAcceptedVotersSet = new Set(allAcceptedBallots.map((b) => String(b.admissionNo || b.admission_no || "").trim().toUpperCase()));

      // Active students strictly belonging to the 6 houses
      const activeStudents = allStudents.filter(
        (s) => s.isActive !== false && s.admissionNo !== "0000" && !s.isStaff && sixHouseCodes.has(s.houseCode)
      );

      // 1. Boys Turnout (across all 6 houses)
      const boysEligible = activeStudents.filter((s) => isBoyStudent(s)).length;
      const boysVoted = activeStudents.filter((s) => isBoyStudent(s) && allAcceptedVotersSet.has(String(s.admissionNo).trim().toUpperCase())).length;
      const boysPct = boysEligible ? Math.round((boysVoted / boysEligible) * 100) : 0;

      // 2. Girls Turnout (across all 6 houses)
      const girlsEligible = activeStudents.filter((s) => isGirlStudent(s)).length;
      const girlsVoted = activeStudents.filter((s) => isGirlStudent(s) && allAcceptedVotersSet.has(String(s.admissionNo).trim().toUpperCase())).length;
      const girlsPct = girlsEligible ? Math.round((girlsVoted / girlsEligible) * 100) : 0;

      // 3. Overall House Total
      const totalEligible = activeStudents.length || 1084;
      const totalVoted = boysVoted + girlsVoted;
      const overallPct = totalEligible ? Math.round((totalVoted / totalEligible) * 100) : 0;
      const remainingCount = Math.max(0, totalEligible - totalVoted);

      // Update Top KPIs
      if (el.voted) el.voted.textContent = `${totalVoted} / ${totalEligible}`;
      if (el.pct) el.pct.textContent = `${overallPct}% house turnout (${totalVoted} cast)`;
      if (el.boysVoted) el.boysVoted.textContent = `${boysVoted} / ${boysEligible}`;
      if (el.boysPct) el.boysPct.textContent = `${boysPct}% boys turnout`;
      if (el.girlsVoted) el.girlsVoted.textContent = `${girlsVoted} / ${girlsEligible}`;
      if (el.girlsPct) el.girlsPct.textContent = `${girlsPct}% girls turnout`;
      if (el.remaining) el.remaining.textContent = String(remainingCount);

      if (prevTotalVoted !== null && totalVoted !== prevTotalVoted) {
        triggerPulse([el.voted, el.remaining, el.boysVoted, el.girlsVoted], "is-bumping", 360);
      }
      prevTotalVoted = totalVoted;

      const applyBars = () => {
        sixHouses.forEach((h) => {
          const hStudents = activeStudents.filter((s) => s.houseCode === h.code);

          // House Boys
          const bEligible = hStudents.filter((s) => isBoyStudent(s)).length;
          const bVoted = hStudents.filter((s) => isBoyStudent(s) && allAcceptedVotersSet.has(String(s.admissionNo).toUpperCase())).length;
          const bRatio = bEligible ? bVoted / bEligible : 0;
          const bPct = Math.round(bRatio * 100);

          // House Girls
          const gEligible = hStudents.filter((s) => isGirlStudent(s)).length;
          const gVoted = hStudents.filter((s) => isGirlStudent(s) && allAcceptedVotersSet.has(String(s.admissionNo).toUpperCase())).length;
          const gRatio = gEligible ? gVoted / gEligible : 0;
          const gPct = Math.round(gRatio * 100);

          // House Total
          const hTotalEligible = bEligible + gEligible;
          const hTotalVoted = bVoted + gVoted;
          const hTotalPct = hTotalEligible ? Math.round((hTotalVoted / hTotalEligible) * 100) : 0;

          const node = houseNodes.get(h.code);
          if (!node) return;

          // 1. Update House Total Label (Positioned ABOVE both graphs)
          node.totalBadge.textContent = `${hTotalVoted} / ${hTotalEligible} Total (${hTotalPct}%)`;

          // 2. Update Boys Bar: Unified house accent color (h.accent)
          node.bFraction.textContent = `${bVoted} / ${bEligible}`;
          node.bPct.textContent = `${bPct}%`;
          const bVisualScale = bVoted === 0 ? 0.035 : Math.max(0.08, bRatio);
          node.bFill.style.setProperty("--bar-scale", bVisualScale.toFixed(4));
          node.bFill.style.setProperty("--bar-opacity", bVoted === 0 ? "0.24" : "1");
          node.bFill.style.background = h.accent;

          // 3. Update Girls Bar: Unified house accent color (h.accent)
          node.gFraction.textContent = `${gVoted} / ${gEligible}`;
          node.gPct.textContent = `${gPct}%`;
          const gVisualScale = gVoted === 0 ? 0.035 : Math.max(0.08, gRatio);
          node.gFill.style.setProperty("--bar-scale", gVisualScale.toFixed(4));
          node.gFill.style.setProperty("--bar-opacity", gVoted === 0 ? "0.24" : "1");
          node.gFill.style.background = h.accent;

          // House-level prominent green +1 indicator above the house header
          const prevH = prevCounts.get(`${h.code}_total`);
          if (prevH !== undefined && hTotalVoted > prevH) {
            const diff = hTotalVoted - prevH;
            const hBadge = document.createElement("span");
            hBadge.className = "house-vote-plus-one";
            hBadge.textContent = `+${diff}`;
            node.clusterCol.appendChild(hBadge);
            setTimeout(() => hBadge.remove(), 1750);
            triggerPulse([node.clusterCol], "is-rising", 800);
            triggerPulse([node.totalBadge], "is-bumping", 400);
          }
          prevCounts.set(`${h.code}_total`, hTotalVoted);

          // Animate pulses and float green +1 on Boys bar increment
          const prevB = prevCounts.get(`${h.code}_b`);
          if (prevB !== undefined && bVoted > prevB) {
            const diff = bVoted - prevB;
            const bBadge = document.createElement("span");
            bBadge.className = "bar-vote-plus-one";
            bBadge.textContent = `+${diff}`;
            node.boysUnit.appendChild(bBadge);
            setTimeout(() => bBadge.remove(), 1550);
            triggerPulse([node.boysUnit], "is-rising", 900);
            triggerPulse([node.bFraction], "is-bumping", 400);
          }

          // Animate pulses and float green +1 on Girls bar increment
          const prevG = prevCounts.get(`${h.code}_g`);
          if (prevG !== undefined && gVoted > prevG) {
            const diff = gVoted - prevG;
            const gBadge = document.createElement("span");
            gBadge.className = "bar-vote-plus-one";
            gBadge.textContent = `+${diff}`;
            node.girlsUnit.appendChild(gBadge);
            setTimeout(() => gBadge.remove(), 1550);
            triggerPulse([node.girlsUnit], "is-rising", 900);
            triggerPulse([node.gFraction], "is-bumping", 400);
          }

          prevCounts.set(`${h.code}_b`, bVoted);
          prevCounts.set(`${h.code}_g`, gVoted);
        });
      };

      if (!isMounted) {
        isMounted = true;
        requestAnimationFrame(() => requestAnimationFrame(applyBars));
      } else {
        applyBars();
      }
    }

    const SB_URL = "https://rziptxcknaeuorekxwrl.supabase.co";
    const SB_KEY = "sb_publishable_jcyjkISfyHxcKPwVUloYYQ_4BfL3pUZ";

    function setLiveStatus(state, meta) {
      // Live sync pill removed as per user request
    }

    async function fetchAcceptedBallotsFast() {
      // Ultra-lightweight endpoint fetch (only returns accepted ballots, ~200ms)
      const res = await fetch(`${SB_URL}/rest/v1/ballots?select=admission_no,status&status=eq.accepted`, {
        cache: "no-store",
        headers: {
          apikey: SB_KEY,
          Authorization: `Bearer ${SB_KEY}`,
        },
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    }

    let isRefreshing = false;
    let lastVoteCount = -1;

    async function refreshInPlace() {
      if (isRefreshing) return;
      isRefreshing = true;
      try {
        let ballots = null;
        try {
          ballots = await fetchAcceptedBallotsFast();
        } catch (netErr) {
          // Fallback to AdminBackend or local storage if direct call fails
          if (window.AdminBackend && typeof window.AdminBackend.getSnapshot === "function") {
            const snap = await window.AdminBackend.getSnapshot();
            if (snap && snap.ballots) ballots = snap.ballots;
          }
        }

        if (Array.isArray(ballots)) {
          updateGraphInPlace({
            students: window.ADMIN_DATA?.students || [],
            ballots: ballots,
          });

          const uniqueVoters = new Set(ballots.map((b) => String(b.admission_no || b.admissionNo || "").trim().toUpperCase())).size;
          setLiveStatus("active", `${uniqueVoters} Cast · Live`);
          lastVoteCount = uniqueVoters;
        }
      } catch (err) {
        console.warn("Unable to load graphs snapshot:", err);
        setLiveStatus("warning", "Reconnecting...");
      } finally {
        isRefreshing = false;
      }
    }

    async function boot() {
      initNodes();

      // Immediate initial render from window.ADMIN_DATA
      let initialBallots = [];
      try {
        const cached = JSON.parse(localStorage.getItem("spr_admin_snapshot_cache") || "null");
        if (cached && Array.isArray(cached.ballots)) initialBallots = cached.ballots;
      } catch (_) {}

      const initialStudents = [
        ...(window.ADMIN_DATA?.students || []),
        ...(window.ADMIN_DATA?.teachers || window.TEACHERS_DATA || []),
      ];

      updateGraphInPlace({
        students: initialStudents,
        ballots: initialBallots,
      });

      // 1. Initial fast sync immediately
      await refreshInPlace();

      // 2. BroadcastChannel for 0ms instantaneous updates when voting on same machine
      if (typeof BroadcastChannel !== "undefined") {
        try {
          const syncChan = new BroadcastChannel("election_spr_2026_sync");
          syncChan.addEventListener("message", () => {
            refreshInPlace();
          });
        } catch (_) {}
      }

      // 3. Storage event listener for cross-tab cache sync
      window.addEventListener("storage", (e) => {
        if (e.key && (e.key.includes("ballot") || e.key.includes("snapshot") || e.key.includes("sb_cfg"))) {
          refreshInPlace();
        }
      });

      // 4. AdminBackend update subscription fallback
      if (window.AdminBackend) {
        try {
          if (typeof window.AdminBackend.init === "function") {
            window.AdminBackend.init().catch(() => {});
          }
          if (typeof window.AdminBackend.subscribeUpdates === "function") {
            window.AdminBackend.subscribeUpdates(() => {
              refreshInPlace();
            });
          }
        } catch (e) {
          console.warn("AdminBackend init error:", e);
        }
      }

      // 5. High-frequency 1.5s live polling across all remote booths/laptops via Cloudflare
      setInterval(refreshInPlace, 1500);
    }

    // Helper to test or preview live green +1 vote animation on demand
    window.simulateVote = (houseCode = "GURUDRONA", gender = "GIRL") => {
      const hc = String(houseCode).toUpperCase();
      const node = houseNodes.get(hc);
      if (!node) {
        console.warn("House not found:", houseCode);
        return;
      }
      const isGirl = gender.toUpperCase().startsWith("G");

      const hBadge = document.createElement("span");
      hBadge.className = "house-vote-plus-one";
      hBadge.textContent = "+1";
      node.clusterCol.appendChild(hBadge);
      setTimeout(() => hBadge.remove(), 1750);
      triggerPulse([node.clusterCol], "is-rising", 800);
      triggerPulse([node.totalBadge], "is-bumping", 400);

      const targetUnit = isGirl ? node.girlsUnit : node.boysUnit;
      const targetFraction = isGirl ? node.gFraction : node.bFraction;
      const barBadge = document.createElement("span");
      barBadge.className = "bar-vote-plus-one";
      barBadge.textContent = "+1";
      targetUnit.appendChild(barBadge);
      setTimeout(() => barBadge.remove(), 1550);
      triggerPulse([targetUnit], "is-rising", 900);
      triggerPulse([targetFraction], "is-bumping", 400);
      triggerPulse([el.voted, el.remaining, isGirl ? el.girlsVoted : el.boysVoted], "is-bumping", 400);
    };

    boot();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", startGraphs);
  } else {
    startGraphs();
  }
})();
