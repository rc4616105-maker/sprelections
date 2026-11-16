// Election Results Controller — Clean School Cabinet & 6 House Cards with Post Winners Drilldown
(function () {
  const { houses } = window.ADMIN_DATA;

  let latestSnapshot = null;
  let selectedCategory = null; // Currently open house/cabinet in drilldown panel (null | 'CENTRAL' | 'BHEESHMA' | ... | 'ALL')

  const categoryDefs = [
    { code: "CENTRAL", label: "School Cabinet", name: "School Cabinet", postCount: 5, accent: "#059669", ink: "#047857", icon: "🏛️" },
    { code: "BHEESHMA", label: "Bheeshma House", name: "Bheeshma House", postCount: 4, accent: "#eab308", ink: "#925c04", icon: "🟡" },
    { code: "GURUDRONA", label: "Gurudrona House", name: "Gurudrona House", postCount: 4, accent: "#2563eb", ink: "#1d4ed8", icon: "🔵" },
    { code: "HANUMAN", label: "Hanuman House", name: "Hanuman House", postCount: 4, accent: "#f97316", ink: "#ea580c", icon: "🟠" },
    { code: "KARNA", label: "Karna House", name: "Karna House", postCount: 4, accent: "#b91c1c", ink: "#991b1b", icon: "🔴" },
    { code: "VASISTHA", label: "Vasistha House", name: "Vasistha House", postCount: 4, accent: "#db2777", ink: "#be185d", icon: "🟣" },
    { code: "VISHWAMITHRA", label: "Vishwamithra House", name: "Vishwamithra House", postCount: 4, accent: "#7c3aed", ink: "#6d28d9", icon: "🟣" },
  ];

  const el = {
    refreshBtn: document.getElementById("refresh-btn"),
    printResultsBtn: document.getElementById("print-results-btn"),
    sbOfflineBanner: document.getElementById("sb-offline-banner"),
    sbOfflineMsg: document.getElementById("sb-offline-msg"),

    resKpiTotalVotes: document.getElementById("res-kpi-total-votes"),
    resKpiTurnout: document.getElementById("res-kpi-turnout"),
    resKpiCandidates: document.getElementById("res-kpi-candidates"),

    sidebarCategoryNav: document.getElementById("sidebar-category-nav"),
    resultsCategoryPills: document.getElementById("results-category-pills"),

    sectionCategoryTitle: document.getElementById("section-category-title"),
    sectionCategorySubtitle: document.getElementById("section-category-subtitle"),
    resultsHousesGrid: document.getElementById("results-houses-grid"),

    resultsDrilldownPanel: document.getElementById("results-drilldown-panel"),
    drilldownTitle: document.getElementById("drilldown-title"),
    drilldownSubtitle: document.getElementById("drilldown-subtitle"),
    closeDrilldownBtn: document.getElementById("close-drilldown-btn"),
    drilldownTbody: document.getElementById("drilldown-tbody"),
  };

  function formatHouseLabel(name) {
    if (!name) return "";
    const str = String(name).trim();
    if (str.endsWith("House") || str.endsWith("Houses") || str === "School Cabinet") {
      return str;
    }
    return `${str} House`;
  }

  function getCandidateClassSec(cand, post) {
    if (!cand) return post ? `Class ${post.className || "—"}` : "—";
    const stu = (latestSnapshot?.students || []).find((s) => s.admissionNo === cand.admissionNo || s.fullName === cand.fullName);
    if (stu && stu.className && stu.section) {
      const cls = String(stu.className).toLowerCase().startsWith("class") ? stu.className : `Class ${stu.className}`;
      return `${cls} · Sec ${stu.section}`;
    }
    const cls = cand.className
      ? (String(cand.className).toLowerCase().startsWith("class") ? cand.className : `Class ${cand.className}`)
      : (post?.className ? `Class ${post.className}` : "");
    let sec = cand.section || "";
    if (sec.includes("· Option")) {
      sec = "Sec " + sec.split("· Option").pop().trim();
    } else if (sec.startsWith("Class ")) {
      sec = "";
    }
    if (cls && sec) return `${cls} · ${sec}`;
    return cls || sec || "—";
  }

  function getAllElectionPosts(candidatesList) {
    let cands = candidatesList || latestSnapshot?.candidates || window.ADMIN_DATA.candidates || [];
    if (!cands || cands.length === 0) {
      cands = window.ADMIN_DATA.candidates || [];
    }
    const posts = [];

    // 1. School Cabinet (Central) — 5 Posts
    const centralPositions = window.ADMIN_DATA.centralPositions || [
      { id: "PRESIDENT", code: "Vote_President", title: "School President", subtitle: "Class 10 · Central Cabinet", className: "10" },
      { id: "VICE_PRESIDENT", code: "Vote_Vice_President", title: "School Vice President", subtitle: "Class 9 · Central Cabinet", className: "9" },
      { id: "LITERARY_SECRETARY", code: "Vote_Literary_Sec", title: "Literary Secretary", subtitle: "Class 9 · Central Cabinet", className: "9" },
      { id: "SPORTS_SECRETARY", code: "Vote_Sports_Sec", title: "Sports Secretary", subtitle: "Class 9 · Central Cabinet", className: "9" },
      { id: "SOCIAL_CULTURAL_SECRETARY", code: "Vote_Social_Cultural_Sec", title: "Social & Cultural Secretary", subtitle: "Class 9 · Central Cabinet", className: "9" },
    ];

    centralPositions.forEach((cp) => {
      let postCands = cands.filter(
        (c) => c.houseCode === "CENTRAL" && (c.positionId === cp.id || c.positionId === cp.code) && c.isApproved
      );
      if (postCands.length === 0) {
        postCands = (window.ADMIN_DATA.candidates || []).filter(
          (c) => c.houseCode === "CENTRAL" && (c.positionId === cp.id || c.positionId === cp.code)
        );
      }
      posts.push({
        key: `CENTRAL_${cp.id}`,
        houseCode: "CENTRAL",
        houseName: "School Cabinet",
        categoryName: "School Cabinet",
        categoryAccent: "#059669",
        categoryInk: "#047857",
        positionId: cp.id,
        positionCode: cp.code,
        title: cp.title,
        subtitle: cp.subtitle,
        className: cp.className,
        isCentral: true,
        candidates: postCands,
      });
    });

    // 2. Regular 6 Houses — 24 Posts
    const regularHouses = houses.filter((h) => h.code !== "ALL" && h.code !== "CENTRAL");
    const regularPositions = window.ADMIN_DATA.positions || [
      { id: "CAPTAIN_BOY", code: "Vote_10_Boy", title: "Boys Captain", subtitle: "Class 10 Boy", className: "10" },
      { id: "CAPTAIN_GIRL", code: "Vote_10_Girl", title: "Girls Captain", subtitle: "Class 10 Girl", className: "10" },
      { id: "VICE_CAPTAIN_BOY", code: "Vote_9_Boy", title: "Boys Vice Captain", subtitle: "Class 9 Boy", className: "9" },
      { id: "VICE_CAPTAIN_GIRL", code: "Vote_9_Girl", title: "Girls Vice Captain", subtitle: "Class 9 Girl", className: "9" },
    ];

    regularHouses.forEach((h) => {
      regularPositions.forEach((rp) => {
        let postCands = cands.filter(
          (c) => c.houseCode === h.code && (c.positionId === rp.id || c.positionId === rp.code) && c.isApproved
        );
        if (postCands.length === 0) {
          postCands = (window.ADMIN_DATA.candidates || []).filter(
            (c) => c.houseCode === h.code && (c.positionId === rp.id || c.positionId === rp.code)
          );
        }
        posts.push({
          key: `${h.code}_${rp.id}`,
          houseCode: h.code,
          houseName: formatHouseLabel(h.name),
          categoryName: `${h.name} House`,
          categoryAccent: h.accent,
          categoryInk: h.accentText,
          positionId: rp.id,
          positionCode: rp.code,
          title: rp.title,
          subtitle: `${h.name} · ${rp.subtitle}`,
          className: rp.className,
          isCentral: false,
          candidates: postCands,
        });
      });
    });

    return posts;
  }

  function computeElectionPostData(snap) {
    const acceptedBallotsAll = (snap.ballots || []).filter((b) => b.status === "accepted");
    const allPosts = getAllElectionPosts(snap.candidates);

    return allPosts.map((post) => {
      const candsWithVotes = post.candidates.map((c) => {
        const votes = acceptedBallotsAll.filter((b) => {
          const matchCand = b.candidateId === c.id || b.candidateName === c.fullName;
          if (!matchCand) return false;
          if (post.isCentral) {
            return (
              b.houseCode === "CENTRAL" ||
              b.positionId === post.positionId ||
              b.positionId === post.positionCode ||
              (b.positionName && b.positionName.includes(post.title))
            );
          }
          return (
            b.houseCode === post.houseCode &&
            (b.positionId === post.positionId || b.positionId === post.positionCode || (b.positionName && b.positionName.includes(post.title)))
          );
        }).length;

        return {
          ...c,
          votes,
        };
      });

      const totalPostVotes = candsWithVotes.reduce((sum, c) => sum + c.votes, 0);
      candsWithVotes.forEach((c) => {
        c.pct = totalPostVotes > 0 ? ((c.votes / totalPostVotes) * 100).toFixed(1) : "0.0";
      });

      candsWithVotes.sort((a, b) => b.votes - a.votes || a.fullName.localeCompare(b.fullName));

      let winner = null;
      let isTied = false;
      if (totalPostVotes > 0) {
        const maxVotes = candsWithVotes[0].votes;
        const topCands = candsWithVotes.filter((c) => c.votes === maxVotes);
        if (topCands.length === 1) {
          winner = topCands[0];
        } else {
          isTied = true;
          winner = topCands;
        }
      }

      return {
        post,
        totalPostVotes,
        candidates: candsWithVotes,
        winner,
        isTied,
      };
    });
  }

  function renderView(snap) {
    if (!snap) return;
    const eligible = (snap.students || []).filter((s) => s.isActive).length;
    const acceptedBallotsAll = (snap.ballots || []).filter((b) => b.status === "accepted");
    const votedVotersCount = new Set(acceptedBallotsAll.map((b) => b.admissionNo)).size;
    const pct = eligible ? Math.round((votedVotersCount / eligible) * 100) : 0;

    const allCandidates = snap.candidates && snap.candidates.length === 87
      ? snap.candidates
      : window.ADMIN_DATA.candidates || [];

    if (el.resKpiTotalVotes) el.resKpiTotalVotes.textContent = String(acceptedBallotsAll.length);
    if (el.resKpiTurnout) el.resKpiTurnout.textContent = `${pct}% (${votedVotersCount}/${eligible})`;
    if (el.resKpiCandidates) el.resKpiCandidates.textContent = String(allCandidates.length);

    const postDataList = computeElectionPostData(snap);

    // Sync Category Filter Pills
    if (el.resultsCategoryPills) {
      el.resultsCategoryPills.innerHTML = "";
      const pillDefs = [
        ...categoryDefs,
        { code: "ALL", label: "📊 All 29 Posts", name: "All 29 Leadership Posts" },
      ];
      pillDefs.forEach((cat) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = `filter-pill-btn ${selectedCategory === cat.code ? "is-active" : ""}`;
        btn.dataset.cat = cat.code;
        btn.textContent = cat.label;
        btn.addEventListener("click", () => {
          if (selectedCategory === cat.code) {
            selectedCategory = null;
            if (el.resultsDrilldownPanel) el.resultsDrilldownPanel.hidden = true;
          } else {
            selectedCategory = cat.code;
            renderDrilldownTable(cat.code, postDataList);
            if (el.resultsDrilldownPanel) {
              el.resultsDrilldownPanel.hidden = false;
              el.resultsDrilldownPanel.scrollIntoView({ behavior: "smooth", block: "nearest" });
            }
          }
          renderHouseCards(postDataList);
          syncNavActive();
        });
        el.resultsCategoryPills.appendChild(btn);
      });
    }

    syncNavActive();

    // Render 7 House & Cabinet Cards Grid
    renderHouseCards(postDataList);

    // If a drilldown is open, re-render its table
    if (selectedCategory) {
      renderDrilldownTable(selectedCategory, postDataList);
      if (el.resultsDrilldownPanel) el.resultsDrilldownPanel.hidden = false;
    } else {
      if (el.resultsDrilldownPanel) el.resultsDrilldownPanel.hidden = true;
    }
  }

  function syncNavActive() {
    if (el.sidebarCategoryNav) {
      el.sidebarCategoryNav.querySelectorAll(".nav-btn").forEach((btn) => {
        const isAct = btn.dataset.cat === selectedCategory;
        btn.classList.toggle("is-active", isAct);
        const cat = categoryDefs.find((c) => c.code === btn.dataset.cat);
        if (cat) {
          if (isAct) {
            btn.style.borderLeft = `4px solid ${cat.accent}`;
            btn.style.color = cat.ink;
            btn.style.background = `${cat.accent}14`;
          } else {
            btn.style.borderLeft = "";
            btn.style.color = "";
            btn.style.background = "";
          }
        }
      });
    }
    if (el.resultsCategoryPills) {
      el.resultsCategoryPills.querySelectorAll(".filter-pill-btn").forEach((btn) => {
        const isAct = btn.dataset.cat === selectedCategory || (selectedCategory === "ALL" && btn.dataset.cat === "ALL");
        btn.classList.toggle("is-active", isAct);
        const cat = categoryDefs.find((c) => c.code === btn.dataset.cat);
        if (cat) {
          if (isAct) {
            btn.style.borderColor = cat.accent;
            btn.style.color = cat.ink;
            btn.style.background = `${cat.accent}18`;
          } else {
            btn.style.borderColor = "";
            btn.style.color = "";
            btn.style.background = "";
          }
        }
      });
    }
  }

  // --- Render 7 Cards: School Cabinet + 6 Houses ---
  function renderHouseCards(postDataList) {
    if (!el.resultsHousesGrid) return;
    el.resultsHousesGrid.innerHTML = "";

    categoryDefs.forEach((cat) => {
      const isSelected = selectedCategory === cat.code;
      const housePosts = postDataList.filter((pd) => pd.post.houseCode === cat.code);
      const decidedCount = housePosts.filter((pd) => pd.totalPostVotes > 0 && pd.winner && !pd.isTied).length;
      const totalHouseVotes = housePosts.reduce((sum, pd) => sum + pd.totalPostVotes, 0);

      const card = document.createElement("div");
      card.className = `admin-house-card ${isSelected ? "is-selected-card" : ""}`;
      card.style.setProperty("--card-accent", cat.accent);
      card.style.setProperty("--card-ink", cat.ink);
      card.style.cursor = "pointer";

      if (cat.code === "CENTRAL") {
        card.style.background = "linear-gradient(135deg, var(--bg-card) 0%, #ecfdf5 100%)";
        card.style.borderColor = "#a7f3d0";
      }

      let statusBadge = "";
      let barPct = 0;

      if (totalHouseVotes === 0) {
        statusBadge = "Pending Votes";
        barPct = 0;
      } else if (decidedCount === cat.postCount) {
        statusBadge = "🏆 All Decided";
        barPct = 100;
      } else {
        statusBadge = `${decidedCount}/${cat.postCount} Decided`;
        barPct = Math.round((decidedCount / cat.postCount) * 100);
      }

      card.innerHTML = `
        <div class="admin-house-top">
          <div>
            <h3 class="admin-house-title" style="color: ${cat.ink}; font-size: 1.25rem;">${cat.name}</h3>
            <div style="font-size: 0.8rem; color: var(--text-muted); font-weight: 600; margin-top: 0.2rem;">${cat.postCount} Leadership Posts</div>
          </div>
          <span class="badge" style="background:${cat.accent}18; color:${cat.ink}; font-weight:800; border:1px solid ${cat.accent}40; font-size:0.75rem;">
            ${statusBadge}
          </span>
        </div>

        <div class="house-bar-track" style="margin-top: 0.4rem;">
          <div class="house-bar-fill" style="width:${barPct}%; background:${cat.accent};"></div>
        </div>

        <div class="admin-house-meta" style="margin-top: 0.35rem; display: flex; align-items: center; justify-content: space-between;">
          <span style="font-size: 0.82rem; font-weight: 700; color: var(--text-secondary);">${totalHouseVotes} Total Votes</span>
          <span class="admin-house-cta" style="color: ${cat.ink}; font-weight: 700; font-size: 0.84rem;">${isSelected ? "Close Winners ↑" : "View Posts & Winners ↓"}</span>
        </div>
      `;

      card.addEventListener("click", () => {
        if (selectedCategory === cat.code) {
          selectedCategory = null;
          if (el.resultsDrilldownPanel) el.resultsDrilldownPanel.hidden = true;
        } else {
          selectedCategory = cat.code;
          renderDrilldownTable(cat.code, postDataList);
          if (el.resultsDrilldownPanel) {
            el.resultsDrilldownPanel.hidden = false;
            el.resultsDrilldownPanel.scrollIntoView({ behavior: "smooth", block: "nearest" });
          }
        }
        renderHouseCards(postDataList);
        syncNavActive();
      });

      el.resultsHousesGrid.appendChild(card);
    });
  }

  // --- Render Drilldown Table Below ---
  // If catCode === 'ALL': shows all 29 posts with their declared winner (1 row per post)
  // If catCode is a specific house/cabinet: shows each post AND ALL candidates with their votes!
  function renderDrilldownTable(catCode, postDataList) {
    if (!el.resultsDrilldownPanel || !el.drilldownTbody) return;

    const thCandidateCol = document.getElementById("th-candidate-col");

    if (catCode === "ALL") {
      // 1. ALL 29 POSTS: 1 row per post showing declared winner
      if (thCandidateCol) thCandidateCol.textContent = "Winner Candidate";
      if (el.closeDrilldownBtn) el.closeDrilldownBtn.textContent = "Close Winners ✕";
      if (el.drilldownTitle) el.drilldownTitle.textContent = "All 29 Leadership Posts — Declared Winners";
      if (el.drilldownSubtitle) {
        el.drilldownSubtitle.textContent = "Complete election summary showing declared winners and winning vote counts across School Cabinet and all 6 houses.";
      }

      el.drilldownTbody.innerHTML = "";

      postDataList.forEach((pd) => {
        let winnerNameHtml = "";
        let classSecText = "";
        let votesHtml = "";
        let statusBadgeHtml = "";

        if (pd.totalPostVotes === 0) {
          winnerNameHtml = `
            <span style="color: var(--text-muted); font-style: italic;">Awaiting votes</span>
            <div class="stat-note">${pd.candidates.length} Nominated Candidates</div>
          `;
          classSecText = `Class ${pd.post.className || "—"}`;
          votesHtml = `
            <span class="mono" style="color: var(--text-muted); font-weight: 700;">0</span>
            <div class="stat-note">0%</div>
          `;
          statusBadgeHtml = `<span class="badge badge-muted">PENDING</span>`;
        } else if (pd.isTied) {
          winnerNameHtml = `
            <strong style="color: #92400e;">${pd.winner.map((w) => w.fullName).join(", ")}</strong>
            <div class="stat-note" style="color: #b45309;">Tied: ${pd.winner[0].votes} votes each</div>
          `;
          classSecText = pd.winner.map((w) => getCandidateClassSec(w, pd.post)).join(", ");
          votesHtml = `
            <strong class="mono" style="font-size: 1.05rem; font-weight: 800; color: #b45309;">${pd.winner[0].votes}</strong>
            <div class="stat-note">Tied votes</div>
          `;
          statusBadgeHtml = `<span class="badge badge-warning" style="background:#e0f2fe; color:#0369a1; border-color:#bae6fd;">🤝 TIED</span>`;
        } else {
          const w = pd.winner;
          winnerNameHtml = `
            <strong style="font-size: 0.98rem; color: #14532d;">${w.fullName}</strong>
            <div class="stat-note">${w.admissionNo ? `ID: ${w.admissionNo}` : ""}</div>
          `;
          classSecText = getCandidateClassSec(w, pd.post);
          votesHtml = `
            <strong class="mono" style="font-size: 1.15rem; font-weight: 800; color: #15803d;">${w.votes}</strong>
            <div class="stat-note" style="color: #166534; font-weight: 600;">${w.pct}% of post</div>
          `;
          statusBadgeHtml = `<span class="badge badge-gold" style="font-weight: 800;">🏆 WINNER</span>`;
        }

        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>
            <strong style="font-size: 0.96rem; color: ${pd.post.categoryInk};">${pd.post.title}</strong>
            <div class="stat-note">${pd.post.subtitle}</div>
          </td>
          <td>${winnerNameHtml}</td>
          <td><strong style="font-size: 0.88rem; color: var(--text-primary);">${classSecText}</strong></td>
          <td style="text-align: right;">${votesHtml}</td>
          <td style="text-align: center;">${statusBadgeHtml}</td>
        `;

        el.drilldownTbody.appendChild(tr);
      });
      return;
    }

    // 2. SPECIFIC HOUSE OR CABINET: Shows all posts AND ALL candidates for each post with their votes!
    const cat = categoryDefs.find((c) => c.code === catCode) || categoryDefs[0];
    const targetPosts = postDataList.filter((pd) => pd.post.houseCode === catCode);

    if (thCandidateCol) thCandidateCol.textContent = "Candidate Name";
    if (el.closeDrilldownBtn) el.closeDrilldownBtn.textContent = "Close Table ✕";
    if (el.drilldownTitle) el.drilldownTitle.textContent = `${cat.name} — All Posts & Candidates`;
    if (el.drilldownSubtitle) {
      el.drilldownSubtitle.textContent = `Showing all ${targetPosts.length} leadership posts, all nominated candidates, and live vote counts for ${cat.name}.`;
    }

    el.drilldownTbody.innerHTML = "";

    targetPosts.forEach((pd, postIdx) => {
      // Post Section Header Banner
      const headerTr = document.createElement("tr");
      headerTr.style.background = `${cat.accent}14`;
      headerTr.style.borderTop = postIdx > 0 ? `2px solid ${cat.accent}55` : `1px solid var(--border-default)`;
      headerTr.innerHTML = `
        <td colspan="5" style="padding: 0.75rem 1rem;">
          <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem;">
            <div>
              <strong style="color: ${cat.ink}; font-size: 1rem;">📌 ${pd.post.title}</strong>
              <span style="font-size: 0.82rem; color: var(--text-muted); font-weight: 600; margin-left: 0.5rem;">${pd.post.subtitle}</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.75rem;">
              <span style="font-size: 0.8rem; font-weight: 700; color: var(--text-secondary);">${pd.candidates.length} Nominated Candidates</span>
              <span class="badge" style="background: ${cat.accent}24; color: ${cat.ink}; font-weight: 800; font-size: 0.75rem; border: 1px solid ${cat.accent}44;">
                ${pd.totalPostVotes} Total Votes
              </span>
            </div>
          </div>
        </td>
      `;
      el.drilldownTbody.appendChild(headerTr);

      // Render every candidate of this post, sorted descending by votes
      pd.candidates.forEach((c) => {
        const classSec = getCandidateClassSec(c, pd.post);
        let statusBadge = "";
        let voteColor = "var(--text-muted)";

        if (pd.totalPostVotes === 0) {
          statusBadge = `<span class="badge badge-muted">NOMINEE</span>`;
        } else if (pd.isTied && c.votes === pd.winner[0].votes) {
          statusBadge = `<span class="badge badge-warning" style="background:#e0f2fe; color:#0369a1; border-color:#bae6fd;">🤝 TIED</span>`;
          voteColor = "#b45309";
        } else if (pd.winner && c.id === pd.winner.id) {
          statusBadge = `<span class="badge badge-gold" style="font-weight: 800;">🏆 WINNER</span>`;
          voteColor = "#15803d";
        } else {
          statusBadge = `<span class="badge badge-muted">Runner-Up</span>`;
          voteColor = "var(--text-primary)";
        }

        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>
            <strong style="font-size: 0.94rem; color: ${cat.ink};">${pd.post.title}</strong>
            <div class="stat-note">${pd.post.subtitle}</div>
          </td>
          <td>
            <strong style="font-size: 0.98rem; color: var(--text-primary);">${c.fullName}</strong>
            ${c.admissionNo ? `<div class="stat-note">ID: ${c.admissionNo}</div>` : ""}
          </td>
          <td>
            <strong style="font-size: 0.88rem; color: var(--text-primary);">${classSec}</strong>
          </td>
          <td style="text-align: right;">
            <strong class="mono" style="font-size: 1.12rem; font-weight: 800; color: ${voteColor};">${c.votes}</strong>
            <div class="stat-note" style="font-weight: 600;">${c.pct}% of post</div>
          </td>
          <td style="text-align: center;">
            ${statusBadge}
          </td>
        `;
        el.drilldownTbody.appendChild(tr);
      });
    });
  }

  let isRefreshing = false;
  async function refreshAll() {
    if (isRefreshing) return;
    isRefreshing = true;
    try {
      latestSnapshot = await window.AdminBackend.getSnapshot();
      renderView(latestSnapshot);
    } catch (err) {
      console.warn("Unable to refresh election results:", err);
    } finally {
      isRefreshing = false;
    }
  }

  async function boot() {
    // Sidebar nav listeners
    if (el.sidebarCategoryNav) {
      el.sidebarCategoryNav.querySelectorAll(".nav-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
          const cat = btn.dataset.cat || "CENTRAL";
          if (selectedCategory === cat) {
            selectedCategory = null;
            if (el.resultsDrilldownPanel) el.resultsDrilldownPanel.hidden = true;
          } else {
            selectedCategory = cat;
            if (latestSnapshot) {
              const postDataList = computeElectionPostData(latestSnapshot);
              renderDrilldownTable(cat, postDataList);
              if (el.resultsDrilldownPanel) {
                el.resultsDrilldownPanel.hidden = false;
                el.resultsDrilldownPanel.scrollIntoView({ behavior: "smooth", block: "nearest" });
              }
            }
          }
          if (latestSnapshot) {
            const postDataList = computeElectionPostData(latestSnapshot);
            renderHouseCards(postDataList);
          }
          syncNavActive();
        });
      });
    }

    // Close button on drilldown table panel
    if (el.closeDrilldownBtn) {
      el.closeDrilldownBtn.addEventListener("click", () => {
        selectedCategory = null;
        if (el.resultsDrilldownPanel) el.resultsDrilldownPanel.hidden = true;
        if (latestSnapshot) {
          const postDataList = computeElectionPostData(latestSnapshot);
          renderHouseCards(postDataList);
        }
        syncNavActive();
      });
    }

    if (el.refreshBtn) {
      el.refreshBtn.addEventListener("click", () => refreshAll());
    }

    if (el.printResultsBtn) {
      el.printResultsBtn.addEventListener("click", async () => {
        if (typeof window.exportElectionResultsToExcel === "function") {
          await window.exportElectionResultsToExcel(latestSnapshot);
        } else {
          window.print();
        }
      });
    }

    latestSnapshot = {
      students: window.ADMIN_DATA.students || [],
      candidates: window.ADMIN_DATA.candidates || [],
      voterStatus: {},
      ballots: [],
      auditLogs: [],
    };
    renderView(latestSnapshot);

    const mode = await window.AdminBackend.init();
    if (mode === "supabase") {
      if (el.sbOfflineBanner) el.sbOfflineBanner.hidden = true;
    } else {
      if (el.sbOfflineBanner) {
        el.sbOfflineBanner.hidden = false;
        if (el.sbOfflineMsg && window.AdminBackend.backendError) {
          el.sbOfflineMsg.textContent = `${window.AdminBackend.backendError} Open All Houses Admin to connect.`;
        }
      }
    }

    await refreshAll();
    window.AdminBackend.subscribeUpdates(async () => {
      await refreshAll();
    });

    // Real-time auto-sync tally every 2 seconds
    setInterval(refreshAll, 2000);
  }

  boot();
})();
