// House Admin Page Controller — Graphs (Comparison) & Voters (Master List + Cancel + Photo)
(function () {
  const { houses, electionId, positionId } = window.ADMIN_DATA;
  const params = new URLSearchParams(window.location.search);
  const rawSlug = (params.get("house") || "bheeshma").toLowerCase();
  const slug = (rawSlug === "bishma" || rawSlug === "bhishma") ? "bheeshma" : rawSlug;
  const house = houses.find((h) => h.slug === slug) || houses[0];

  const isCentral = house.code === "CENTRAL" || house.slug === "central";
  const houseDisplayName = isCentral ? "School Cabinet" : `${house.name} House`;

  // Apply house-specific theme accents
  const rootStyle = document.documentElement.style;
  rootStyle.setProperty("--accent-primary", house.accent);
  rootStyle.setProperty("--accent-hover", house.accentText);
  rootStyle.setProperty("--accent-text", house.accentText);
  rootStyle.setProperty("--accent-subtle", `rgba(${house.accentRgb}, 0.12)`);
  rootStyle.setProperty("--on-accent", (house.code === "BHEESHMA" || house.code === "BHISHMA" || house.code === "HANUMAN") ? "#141413" : "#fffdf9");
  document.title = `${houseDisplayName} Admin — School Elections 2026`;

  let latestSnapshot = null;
  let currentView = params.get("view") === "voters" ? "voters" : "graphs";
  let activeHouseKpi = null; // 'eligible' | 'accepted' | 'cancelled' | 'remaining' | null
  let activeRoleFilter = "ALL";
  let pendingCancelBallotId = null;
  let pendingDeleteAdm = null;
  const positions = isCentral
    ? (window.ADMIN_DATA.centralPositions || [
        { id: "PRESIDENT", code: "Vote_President", title: "School President", shortTitle: "President", subtitle: "Class 10 · Central Cabinet", className: "10", gender: "Any" },
        { id: "VICE_PRESIDENT", code: "Vote_Vice_President", title: "School Vice President", shortTitle: "Vice President", subtitle: "Class 9 · Central Cabinet", className: "9", gender: "Any" },
        { id: "LITERARY_SECRETARY", code: "Vote_Literary_Sec", title: "Literary Secretary", shortTitle: "Literary Sec", subtitle: "Class 9 · Central Cabinet", className: "9", gender: "Any" },
        { id: "SPORTS_SECRETARY", code: "Vote_Sports_Sec", title: "Sports Secretary", shortTitle: "Sports Sec", subtitle: "Class 9 · Central Cabinet", className: "9", gender: "Any" },
        { id: "SOCIAL_CULTURAL_SECRETARY", code: "Vote_Social_Cultural_Sec", title: "Social & Cultural Secretary", shortTitle: "Social & Cultural Sec", subtitle: "Class 9 · Central Cabinet", className: "9", gender: "Any" }
      ])
    : (window.ADMIN_DATA.positions || [{ id: positionId, title: "House Captain", subtitle: "House" }]);
  const graphNodes = new Map();
  const roleCardRefs = new Map();
  const prevCandidateVotes = new Map();
  let graphsMounted = false;

  function getHouseStudents(snap) {
    const targetCode = String(house.code || "").toUpperCase();
    return (snap.students || []).filter((s) => {
      if (!s.isActive || s.admissionNo === "0000") return false;
      const sHouse = String(s.houseCode || "").toUpperCase();
      const isStaffMember = Boolean(s.isStaff || sHouse === "ALL" || String(s.className || "").toLowerCase() === "staff" || String(s.admissionNo || "").toUpperCase().startsWith("SPR"));
      if (isCentral) {
        return sHouse === "CENTRAL" || isStaffMember;
      }
      return sHouse === targetCode && !isStaffMember;
    });
  }

  const el = {
    sidebarHouseTitle: document.getElementById("sidebar-house-title"),
    houseNameHighlight: document.getElementById("house-name-highlight"),
    sbOfflineBanner: document.getElementById("sb-offline-banner"),
    sbOfflineMsg: document.getElementById("sb-offline-msg"),
    refreshBtn: document.getElementById("refresh-btn"),
    navBtns: Array.from(document.querySelectorAll(".nav-btn")),
    views: {
      graphs: document.getElementById("view-graphs"),
      voters: document.getElementById("view-voters"),
    },
    pageEyebrow: document.getElementById("page-eyebrow"),
    pageTitle: document.getElementById("house-page-title"),
    pageSub: document.getElementById("house-page-sub"),

    hkpiButtons: Array.from(document.querySelectorAll("[data-hkpi-filter]")),
    hkpiEligible: document.getElementById("hkpi-eligible"),
    hkpiAccepted: document.getElementById("hkpi-accepted"),
    hkpiTurnout: document.getElementById("hkpi-turnout"),
    hkpiCancelled: document.getElementById("hkpi-cancelled"),
    hkpiRemaining: document.getElementById("hkpi-remaining"),

    drilldownPanel: document.getElementById("house-drilldown-panel"),
    drilldownTitle: document.getElementById("house-drilldown-title"),
    drilldownSubtitle: document.getElementById("house-drilldown-subtitle"),
    closeDrilldownBtn: document.getElementById("close-house-drilldown-btn"),
    drilldownSearch: document.getElementById("house-drilldown-search"),
    drilldownClassFilter: document.getElementById("house-drilldown-class-filter"),
    drilldownSectionFilter: document.getElementById("house-drilldown-section-filter"),
    drilldownThead: document.getElementById("house-drilldown-thead"),
    drilldownTbody: document.getElementById("house-drilldown-tbody"),
    drilldownEmpty: document.getElementById("house-drilldown-empty"),

    roleFilterBtns: Array.from(document.querySelectorAll("[data-role-filter]")),
    roleGraphsGrid: document.getElementById("role-graphs-grid"),

    voterSearch: document.getElementById("voter-search"),
    voterStatusFilter: document.getElementById("voter-status-filter"),
    voterClassFilter: document.getElementById("voter-class-filter"),
    voterSectionFilter: document.getElementById("voter-section-filter"),
    votersTbody: document.getElementById("voters-tbody"),
    votersEmpty: document.getElementById("voters-empty"),
    cancelledCard: document.getElementById("cancelled-history-card"),
    cancelledTbody: document.getElementById("cancelled-tbody"),

    cancelModal: document.getElementById("cancel-modal"),
    cancelModalDesc: document.getElementById("cancel-modal-desc"),
    cancelErrorText: document.getElementById("cancel-error-text"),
    cancelModalClose: document.getElementById("cancel-modal-close"),
    confirmCancelBtn: document.getElementById("confirm-cancel-btn"),

    deleteModal: document.getElementById("delete-modal"),
    deleteModalDesc: document.getElementById("delete-modal-desc"),
    deleteErrorText: document.getElementById("delete-error-text"),
    deleteModalClose: document.getElementById("delete-modal-close"),
    confirmDeleteBtn: document.getElementById("confirm-delete-btn"),

    photoModal: document.getElementById("photo-modal"),
    photoModalMeta: document.getElementById("photo-modal-meta"),
    photoModalImg: document.getElementById("photo-modal-img"),
    photoModalClose: document.getElementById("photo-modal-close"),
  };

  if (el.houseNameHighlight) el.houseNameHighlight.textContent = houseDisplayName;
  if (el.sidebarHouseTitle) el.sidebarHouseTitle.textContent = houseDisplayName;

  function formatTime(iso) {
    if (!iso) return "—";
    try {
      return new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
    } catch (_) {
      return iso;
    }
  }

  function switchView(viewName) {
    currentView = viewName;
    el.navBtns.forEach((b) => b.classList.toggle("is-active", b.dataset.view === viewName));
    Object.entries(el.views).forEach(([k, section]) => {
      section.hidden = k !== viewName;
    });
    if (viewName === "graphs") {
      if (el.pageEyebrow) el.pageEyebrow.textContent = `${houseDisplayName} · Graphs`;
      if (el.pageTitle) el.pageTitle.textContent = isCentral ? "Executive Council Vote Comparison" : "Participants Vote Comparison";
      if (el.pageSub) el.pageSub.textContent = `Visual comparison of accepted votes across ${houseDisplayName} candidates.`;
    } else {
      if (el.pageEyebrow) el.pageEyebrow.textContent = `${houseDisplayName} · Voters`;
      if (el.pageTitle) el.pageTitle.textContent = isCentral ? "School Cabinet Voter List" : "Master Student & Voter List";
      if (el.pageSub) el.pageSub.textContent = `Inspect verification photos, see who voted for whom, or cancel a vote for ${houseDisplayName}.`;
    }
  }

  function renderKPIs(snap) {
    const houseStudents = getHouseStudents(snap);
    const houseBallots = snap.ballots.filter((b) => b.houseCode === house.code);
    const acceptedBallots = houseBallots.filter((b) => b.status === "accepted");
    const votedVotersCount = new Set(acceptedBallots.map((b) => b.admissionNo)).size;
    const cancelled = houseBallots.filter((b) => b.status === "cancelled").length;
    const pct = houseStudents.length ? Math.round((votedVotersCount / houseStudents.length) * 100) : 0;

    el.hkpiEligible.textContent = String(houseStudents.length);
    el.hkpiAccepted.textContent = String(votedVotersCount);
    el.hkpiTurnout.textContent = `${pct}% turnout · ${acceptedBallots.length} role ballots →`;
    el.hkpiCancelled.textContent = String(cancelled);
    el.hkpiRemaining.textContent = String(Math.max(0, houseStudents.length - votedVotersCount));
    renderHouseDrilldown(snap);
  }

  function makePhotoCell(ballot, altName) {
    if (!ballot.photoDataUrl) {
      const span = document.createElement("span");
      span.textContent = "—";
      return span;
    }
    const wrap = document.createElement("div");
    wrap.className = "photo-cell-wrap";

    const thumbBtn = document.createElement("button");
    thumbBtn.type = "button";
    thumbBtn.className = "photo-thumb-btn";
    thumbBtn.title = "View verification photo";
    const img = document.createElement("img");
    img.src = ballot.photoDataUrl;
    img.alt = `Photo of ${altName || ballot.fullName}`;
    thumbBtn.appendChild(img);
    thumbBtn.addEventListener("click", () => openPhotoModal(ballot));

    const viewBtn = document.createElement("button");
    viewBtn.type = "button";
    viewBtn.className = "btn btn-secondary";
    viewBtn.textContent = "View Photo";
    viewBtn.addEventListener("click", () => openPhotoModal(ballot));

    wrap.append(thumbBtn, viewBtn);
    return wrap;
  }

  function normClass(c) {
    return String(c || "").trim().toLowerCase().replace(/^class\s*/i, "");
  }

  function normSection(s) {
    return String(s || "").trim().toLowerCase();
  }

  function populateHouseClassAndSectionFilters(studentList) {
    const rawRoster = studentList || latestSnapshot?.students || window.ADMIN_DATA?.students || [];
    const students = getHouseStudents({ students: rawRoster });

    const rawClasses = Array.from(new Set(students.map((s) => String(s.className || "").trim()).filter(Boolean)));
    rawClasses.sort((a, b) => {
      const numA = parseInt(a, 10);
      const numB = parseInt(b, 10);
      if (!isNaN(numA) && !isNaN(numB)) return numB - numA;
      if (!isNaN(numA)) return -1;
      if (!isNaN(numB)) return 1;
      return a.localeCompare(b);
    });

    [el.drilldownClassFilter, el.voterClassFilter].forEach((sel) => {
      if (!sel) return;
      const cur = sel.value;
      sel.innerHTML = '<option value="">All Classes</option>';
      rawClasses.forEach((cls) => {
        const opt = document.createElement("option");
        opt.value = cls;
        opt.textContent = cls.toLowerCase().startsWith("class") ? cls : `Class ${cls}`;
        sel.appendChild(opt);
      });
      if (cur && rawClasses.includes(cur)) sel.value = cur;
    });

    updateHouseSectionFilterOptions(students);
  }

  function updateHouseSectionFilterOptions(studentList) {
    const rawRoster = studentList || latestSnapshot?.students || window.ADMIN_DATA?.students || [];
    const students = Array.isArray(studentList) ? studentList : getHouseStudents({ students: rawRoster });

    if (el.drilldownSectionFilter) {
      const selectedClass = el.drilldownClassFilter ? el.drilldownClassFilter.value.trim() : "";
      const currentSec = el.drilldownSectionFilter.value;
      const filtered = selectedClass
        ? students.filter((s) => normClass(s.className) === normClass(selectedClass))
        : students;
      const rawSecs = Array.from(new Set(filtered.map((s) => String(s.section || "").trim()).filter(Boolean))).sort();
      el.drilldownSectionFilter.innerHTML = '<option value="">All Sections</option>';
      rawSecs.forEach((sec) => {
        const opt = document.createElement("option");
        opt.value = sec;
        opt.textContent = sec;
        el.drilldownSectionFilter.appendChild(opt);
      });
      if (currentSec && rawSecs.includes(currentSec)) el.drilldownSectionFilter.value = currentSec;
      else el.drilldownSectionFilter.value = "";
    }

    if (el.voterSectionFilter) {
      const selectedClass = el.voterClassFilter ? el.voterClassFilter.value.trim() : "";
      const currentSec = el.voterSectionFilter.value;
      const filtered = selectedClass
        ? students.filter((s) => normClass(s.className) === normClass(selectedClass))
        : students;
      const rawSecs = Array.from(new Set(filtered.map((s) => String(s.section || "").trim()).filter(Boolean))).sort();
      el.voterSectionFilter.innerHTML = '<option value="">All Sections</option>';
      rawSecs.forEach((sec) => {
        const opt = document.createElement("option");
        opt.value = sec;
        opt.textContent = sec;
        el.voterSectionFilter.appendChild(opt);
      });
      if (currentSec && rawSecs.includes(currentSec)) el.voterSectionFilter.value = currentSec;
      else el.voterSectionFilter.value = "";
    }
  }

  function renderHouseDrilldown(snap) {
    if (el.hkpiButtons) {
      el.hkpiButtons.forEach((b) => {
        b.classList.toggle("is-active", b.dataset.hkpiFilter === activeHouseKpi);
      });
    }
    if (!el.drilldownPanel || !activeHouseKpi) {
      if (el.drilldownPanel) el.drilldownPanel.hidden = true;
      return;
    }

    el.drilldownPanel.hidden = false;
    const q = el.drilldownSearch.value.trim().toLowerCase();
    const cFilter = el.drilldownClassFilter ? el.drilldownClassFilter.value.trim() : "";
    const sFilter = el.drilldownSectionFilter ? el.drilldownSectionFilter.value.trim() : "";
    const houseStudents = getHouseStudents(snap);
    const houseBallots = snap.ballots.filter((b) => b.houseCode === house.code);
    const studentStatus = (stu) => {
      const states = positions.map((p) => snap.voterStatus[`${electionId}_${stu.admissionNo}_${p.id}`]?.status || "not_voted");
      if (states.every((s) => s === "voted")) return "voted";
      if (states.some((s) => s === "cancelled")) return "cancelled";
      if (states.some((s) => s === "voted")) return "partial";
      return "not_voted";
    };

    el.drilldownThead.innerHTML = "";
    el.drilldownTbody.innerHTML = "";

    if (activeHouseKpi === "eligible" || activeHouseKpi === "remaining") {
      const isRemaining = activeHouseKpi === "remaining";
      el.drilldownTitle.textContent = isRemaining
        ? `${house.name} House — Not Voted Yet`
        : `${house.name} House — Eligible Voters`;
      el.drilldownSubtitle.textContent = isRemaining
        ? `Eligible voters in ${house.name} House who have not yet completed an accepted vote.`
        : `All active eligible voters registered in ${house.name} House.`;

      el.drilldownThead.innerHTML = `
        <tr>
          <th>Voter ID</th>
          <th>Student</th>
          <th>Class</th>
          <th>Sec</th>
          <th>Role</th>
          <th>Status</th>
        </tr>
      `;

      const rows = houseStudents
        .filter((s) => {
          if (cFilter && normClass(s.className) !== normClass(cFilter)) return false;
          if (sFilter && normSection(s.section) !== normSection(sFilter)) return false;
          if (isRemaining && studentStatus(s) === "voted") return false;
          if (q) {
            const hay = `${s.admissionNo} ${s.fullName} ${s.className}-${s.section}`.toLowerCase();
            if (!hay.includes(q)) return false;
          }
          return true;
        })
        .sort((a, b) => a.admissionNo.localeCompare(b.admissionNo));

      el.drilldownEmpty.hidden = rows.length > 0;
      rows.forEach((s) => {
        const st = studentStatus(s);
        const badge =
          st === "voted"
            ? `<span class="badge badge-success">Voted (4/4)</span>`
            : st === "cancelled"
            ? `<span class="badge badge-warning">Cancelled (Pending Re-vote)</span>`
            : st === "partial"
            ? `<span class="badge badge-warning">Partial Vote</span>`
            : `<span class="badge badge-muted">Not Voted</span>`;
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td class="mono"></td>
          <td><strong></strong></td>
          <td><span class="mono"></span></td>
          <td></td>
          <td>${s.isCandidate ? s.positionName || "Candidate" : "Voter"}</td>
          <td>${badge}</td>
        `;
        tr.children[0].textContent = s.admissionNo;
        tr.children[1].querySelector("strong").textContent = s.fullName;
        const clsLabel = s.isStaff ? (s.subject || "Faculty") : (s.className ? (s.className.toString().toLowerCase().startsWith("class") ? s.className : `Class ${s.className}`) : "--");
        tr.children[2].querySelector(".mono").textContent = clsLabel;
        tr.children[3].textContent = s.isStaff ? (s.section || "Staff") : (s.section || "--");
        el.drilldownTbody.appendChild(tr);
      });
      return;
    }

    if (activeHouseKpi === "accepted") {
      el.drilldownTitle.textContent = `${house.name} House — Accepted Votes`;
      el.drilldownSubtitle.textContent = `Active accepted ballots in ${house.name} House with verification photo and cancel option.`;
      el.drilldownThead.innerHTML = `
        <tr>
          <th>Voter ID</th>
          <th>Voter</th>
          <th>Voted For</th>
          <th>Photo</th>
          <th>Cast Time</th>
          <th>Action</th>
        </tr>
      `;

      const rows = houseBallots.filter((b) => {
        if (b.status !== "accepted") return false;
        if (cFilter && normClass(b.className) !== normClass(cFilter)) return false;
        if (sFilter && normSection(b.section) !== normSection(sFilter)) return false;
        if (q) {
          const hay = `${b.admissionNo} ${b.fullName} ${b.candidateName}`.toLowerCase();
          if (!hay.includes(q)) return false;
        }
        return true;
      });

      el.drilldownEmpty.hidden = rows.length > 0;
      rows.forEach((b) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td class="mono"></td>
          <td><strong></strong><div class="stat-note"></div></td>
          <td><strong></strong><div class="stat-note">${b.positionName || "House Captain"}</div></td>
          <td></td>
          <td class="mono"></td>
          <td></td>
        `;
        tr.children[0].textContent = b.admissionNo;
        tr.children[1].querySelector("strong").textContent = b.fullName;
        tr.children[1].querySelector(".stat-note").textContent = `Class ${b.className}-${b.section}`;
        tr.children[2].querySelector("strong").textContent = b.candidateName;
        tr.children[3].appendChild(makePhotoCell(b));
        tr.children[4].textContent = formatTime(b.castAt);

        const actionWrap = document.createElement("div");
        actionWrap.className = "action-stack";

        const cancelBtn = document.createElement("button");
        cancelBtn.type = "button";
        cancelBtn.className = "btn btn-danger";
        cancelBtn.textContent = "Cancel Vote";
        cancelBtn.addEventListener("click", () => openCancelModal(b));

        actionWrap.appendChild(cancelBtn);
        tr.children[5].appendChild(actionWrap);
        el.drilldownTbody.appendChild(tr);
      });
      return;
    }

    if (activeHouseKpi === "cancelled") {
      el.drilldownTitle.textContent = `${house.name} House — Cancelled Ballots`;
      el.drilldownSubtitle.textContent = `Students in ${house.name} House whose vote was cancelled (excluded from tally; student can re-vote).`;
      el.drilldownThead.innerHTML = `
        <tr>
          <th>Voter ID</th>
          <th>Student</th>
          <th>Cancelled Status</th>
          <th>Photo</th>
          <th>Cancelled By</th>
          <th>Cancelled Time</th>
          <th>Current Status</th>
          <th>Action</th>
        </tr>
      `;

      // Group cancelled ballots by voter (admissionNo) to ensure 1 consolidated row per voter and protect ballot secrecy
      const cancelledVoterMap = new Map();
      houseBallots.forEach((b) => {
        if (b.status !== "cancelled") return;
        if (!cancelledVoterMap.has(b.admissionNo)) {
          cancelledVoterMap.set(b.admissionNo, {
            admissionNo: b.admissionNo,
            fullName: b.fullName || b.admissionNo,
            className: b.className || "",
            section: b.section || "",
            houseCode: b.houseCode || house.code,
            photoDataUrl: b.photoDataUrl || "",
            cancelledAt: b.cancelledAt,
            cancelledBy: b.cancelledBy,
            cancelledReason: b.cancelledReason,
            ballots: [],
          });
        }
        const v = cancelledVoterMap.get(b.admissionNo);
        v.ballots.push(b);
        if (!v.photoDataUrl && b.photoDataUrl) v.photoDataUrl = b.photoDataUrl;
        if (!v.cancelledBy && b.cancelledBy) v.cancelledBy = b.cancelledBy;
        if (!v.cancelledAt && b.cancelledAt) v.cancelledAt = b.cancelledAt;
      });

      const rows = Array.from(cancelledVoterMap.values()).filter((v) => {
        if (cFilter && normClass(v.className) !== normClass(cFilter)) return false;
        if (sFilter && normSection(v.section) !== normSection(sFilter)) return false;
        if (q) {
          const hay = `${v.admissionNo} ${v.fullName} ${v.className}-${v.section} ${v.cancelledBy || ""}`.toLowerCase();
          if (!hay.includes(q)) return false;
        }
        return true;
      });

      el.drilldownEmpty.hidden = rows.length > 0;
      rows.forEach((v) => {
        const sKey = `${electionId}_${v.admissionNo}_${v.ballots[0]?.positionId || positionId}`;
        const curStatus = snap.voterStatus[sKey]?.status || "cancelled";
        const curBadge =
          curStatus === "voted"
            ? `<span class="badge badge-success">Re-voted</span>`
            : `<span class="badge badge-warning">Pending Re-vote</span>`;
        const canceller = v.cancelledBy || "rc4616105@gmail.com";
        const roleCount = v.ballots.length || 4;

        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td class="mono"></td>
          <td><strong></strong><div class="stat-note"></div></td>
          <td>
            <span class="badge badge-warning" style="font-weight:700; padding:4px 9px; font-size:0.8rem;">Cancelled (${roleCount} Posts)</span>
            <div class="stat-note" style="color:var(--text-muted); margin-top:3px; font-size:0.75rem;">Ballot Choice Confidential</div>
          </td>
          <td></td>
          <td><span class="badge" style="background:rgba(220,38,38,0.1); color:#b91c1c; font-weight:700; border:1px solid rgba(220,38,38,0.25);">👤 ${canceller}</span></td>
          <td class="mono"></td>
          <td>${curBadge}</td>
          <td>
            <a href="./edit-votes.html?adm=${encodeURIComponent(v.admissionNo)}" class="btn btn-secondary btn-sm" style="padding: 4px 10px; font-size: 0.78rem; text-decoration:none;">Manage →</a>
          </td>
        `;
        tr.children[0].textContent = v.admissionNo;
        tr.children[1].querySelector("strong").textContent = v.fullName;
        tr.children[1].querySelector(".stat-note").textContent = `Class ${v.className}-${v.section || "--"}`;
        tr.children[3].appendChild(makePhotoCell(v, v.fullName));
        tr.children[5].textContent = formatTime(v.cancelledAt);
        el.drilldownTbody.appendChild(tr);
      });
      return;
    }
  }

  function populateRoleFilterBar() {
    const bar = document.getElementById("role-filter-bar");
    if (!bar) return;
    bar.innerHTML = "";

    const allBtn = document.createElement("button");
    allBtn.type = "button";
    allBtn.className = "role-tab-btn is-active";
    allBtn.dataset.roleFilter = "ALL";
    allBtn.textContent = `All ${positions.length} Roles`;
    allBtn.addEventListener("click", () => {
      activeRoleFilter = "ALL";
      applyRoleVisibility();
    });
    bar.appendChild(allBtn);

    positions.forEach((pos) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "role-tab-btn";
      btn.dataset.roleFilter = pos.id;
      const classBadge = pos.className ? ` (${pos.className}${pos.gender && pos.gender !== "Any" ? pos.gender[0] : ""})` : "";
      btn.textContent = `${pos.shortTitle || pos.title}${classBadge}`;
      btn.addEventListener("click", () => {
        activeRoleFilter = pos.id;
        applyRoleVisibility();
      });
      bar.appendChild(btn);
    });
  }

  function applyRoleVisibility() {
    const btns = Array.from(document.querySelectorAll("#role-filter-bar [data-role-filter]"));
    btns.forEach((btn) => {
      btn.classList.toggle("is-active", btn.dataset.roleFilter === activeRoleFilter);
    });
    if (el.roleGraphsGrid) {
      el.roleGraphsGrid.classList.toggle("is-single", activeRoleFilter !== "ALL");
    }
    roleCardRefs.forEach((ref, posId) => {
      ref.card.hidden = activeRoleFilter !== "ALL" && activeRoleFilter !== posId;
      if (ref.compList) {
        ref.compList.hidden = activeRoleFilter === "ALL";
      }
    });
  }

  function renderGraphs(snap) {
    if (!el.roleGraphsGrid) return;
    const allHouseCandidates = snap.candidates.filter((c) => c.houseCode === house.code && c.isApproved);
    const houseBallots = snap.ballots.filter((b) => b.houseCode === house.code);

    if (!graphsMounted) {
      el.roleGraphsGrid.innerHTML = "";
      graphNodes.clear();
      roleCardRefs.clear();

      positions.forEach((pos) => {
        const cands = allHouseCandidates.filter((c) => c.positionId === pos.id);
        const card = document.createElement("div");
        card.className = "panel-card role-graph-card";
        card.innerHTML = `
          <div class="panel-head-row">
            <div>
              <h3 class="panel-heading"></h3>
              <p class="panel-caption role-card-sub"></p>
            </div>
            <span class="badge badge-muted role-total-pill">0 accepted</span>
          </div>
          <div class="column-chart-wrap">
            <div class="column-chart-grid"></div>
          </div>
          <div class="comparison-list"></div>
        `;
        card.querySelector(".panel-heading").textContent = pos.title;
        card.querySelector(".role-card-sub").textContent = `${pos.subtitle} · ${houseDisplayName}`;

        const colGrid = card.querySelector(".column-chart-grid");
        const compList = card.querySelector(".comparison-list");

        cands.forEach((s) => {
          let secClean = String(s.section || "").replace(/^Class\s*/i, "").trim();
          let candSub = String(s.admissionNo || "").startsWith("DEMO-")
            ? `${pos.subtitle}`
            : (secClean && secClean !== String(s.className) ? `Class ${s.className} (${secClean})` : `Class ${s.className}`);

          const col = document.createElement("div");
          col.className = "chart-col";
          col.innerHTML = `
            <div class="chart-col-count">0 votes</div>
            <div class="chart-col-track">
              <div class="chart-col-bar" style="--bar-scale: 0; --bar-opacity: 0.25;"></div>
            </div>
            <div class="chart-col-axis"></div>
            <div class="chart-cand-info">
              <div class="chart-cand-name"></div>
              <div class="chart-cand-sub"></div>
            </div>
          `;
          let cleanName = String(s.fullName || "").trim();
          // Remove stray leading punctuation e.g. ".SNIGDHA" -> "SNIGDHA"
          cleanName = cleanName.replace(/^[\.\,\s\-]+/, "");
          // Insert a clean space after initials if missing, e.g. "A.Rishitha" -> "A. Rishitha", "K.Kruthvik" -> "K. Kruthvik"
          cleanName = cleanName.replace(/^([A-Za-z]{1,3}\.)([A-Za-z])/g, "$1 $2");
          cleanName = cleanName.replace(/\s+/g, " ");

          col.querySelector(".chart-cand-name").textContent = cleanName;
          col.querySelector(".chart-cand-sub").textContent = candSub;
          colGrid.appendChild(col);

          const row = document.createElement("div");
          row.className = "comparison-row";
          row.innerHTML = `
            <div class="comparison-row-top">
              <div>
                <strong></strong>
                <span class="stat-note cand-row-sub"></span>
                <span class="badge badge-success cand-leader-badge" style="margin-left:0.45rem;" hidden>Leading</span>
              </div>
              <div class="mono cand-tally-text"></div>
            </div>
            <div class="comparison-bar-track">
              <div class="comparison-bar-fill" style="--bar-scale-x: 0;"></div>
            </div>
          `;
          row.querySelector("strong").textContent = cleanName;
          row.querySelector(".cand-row-sub").textContent = ` · ${candSub}`;
          compList.appendChild(row);

          graphNodes.set(s.id, {
            col,
            colCount: col.querySelector(".chart-col-count"),
            colBar: col.querySelector(".chart-col-bar"),
            leaderBadge: row.querySelector(".cand-leader-badge"),
            tallyText: row.querySelector(".cand-tally-text"),
            rowFill: row.querySelector(".comparison-bar-fill"),
          });
        });

        roleCardRefs.set(pos.id, {
          card,
          compList,
          totalPill: card.querySelector(".role-total-pill"),
        });
        el.roleGraphsGrid.appendChild(card);
      });
    }

    const applyValues = () => {
      positions.forEach((pos) => {
        const cands = allHouseCandidates.filter((c) => c.positionId === pos.id);
        const roleBallots = houseBallots.filter((b) => (b.positionId || pos.id) === pos.id);
        const totalAccepted = roleBallots.filter((b) => b.status === "accepted").length;
        const roleRef = roleCardRefs.get(pos.id);
        if (roleRef) {
          roleRef.totalPill.textContent = `${totalAccepted} accepted`;
        }

        const stats = cands.map((c) => {
          const forCand = roleBallots.filter((b) => b.candidateId === c.id);
          const acceptedCount = forCand.filter((b) => b.status === "accepted").length;
          const cancelledCount = forCand.filter((b) => b.status === "cancelled").length;
          const share = totalAccepted ? Math.round((acceptedCount / totalAccepted) * 100) : 0;
          return { ...c, acceptedCount, cancelledCount, share };
        });

        const maxVotes = Math.max(1, ...stats.map((s) => s.acceptedCount));
        const maxAcceptedLeader = Math.max(0, ...stats.map((s) => s.acceptedCount));

        stats.forEach((s) => {
          const n = graphNodes.get(s.id);
          if (!n) return;
          const isLeader = maxAcceptedLeader > 0 && s.acceptedCount === maxAcceptedLeader;
          const scaleY = s.acceptedCount === 0 ? 0.035 : Math.max(0.08, s.acceptedCount / maxVotes);
          const scaleX = totalAccepted ? s.acceptedCount / totalAccepted : 0;

          n.colCount.textContent = `${s.acceptedCount} ${s.acceptedCount === 1 ? "vote" : "votes"}`;
          n.colBar.style.setProperty("--bar-scale", scaleY.toFixed(4));
          n.colBar.style.setProperty("--bar-opacity", s.acceptedCount === 0 ? "0.24" : "1");
          n.leaderBadge.hidden = !isLeader;
          n.tallyText.innerHTML = `<strong>${s.acceptedCount}</strong> (${s.share}%)${s.cancelledCount ? ` · <span style="color:#b45309;">${s.cancelledCount} cancelled</span>` : ""}`;
          n.rowFill.style.setProperty("--bar-scale-x", scaleX.toFixed(4));

          const prev = prevCandidateVotes.get(s.id);
          if (prev !== undefined && s.acceptedCount > prev) {
            const diff = s.acceptedCount - prev;
            const badge = document.createElement("span");
            badge.className = "vote-plus-one";
            badge.textContent = `+${diff}`;
            n.col.appendChild(badge);
            setTimeout(() => badge.remove(), 1250);

            n.col.classList.remove("is-rising");
            void n.col.offsetWidth;
            n.col.classList.add("is-rising");
            setTimeout(() => n.col.classList.remove("is-rising"), 750);
          }
          prevCandidateVotes.set(s.id, s.acceptedCount);
        });
      });
      applyRoleVisibility();
    };

    if (!graphsMounted) {
      graphsMounted = true;
      requestAnimationFrame(() => requestAnimationFrame(applyValues));
    } else {
      applyValues();
    }
  }

  function renderVoters(snap) {
    const q = el.voterSearch.value.trim().toLowerCase();
    const sFilter = el.voterStatusFilter.value;
    const cFilter = el.voterClassFilter ? el.voterClassFilter.value.trim() : "";
    const secFilter = el.voterSectionFilter ? el.voterSectionFilter.value.trim() : "";

    const houseStudents = getHouseStudents(snap)
      .sort((a, b) => a.admissionNo.localeCompare(b.admissionNo));

    const houseBallots = snap.ballots.filter((b) => b.houseCode === house.code);

    const rows = houseStudents
      .map((stu) => {
        const states = positions.map((p) => snap.voterStatus[`${electionId}_${stu.admissionNo}_${p.id}`]?.status || "not_voted");
        const vStatus = states.every((s) => s === "voted")
          ? "voted"
          : states.some((s) => s === "cancelled")
          ? "cancelled"
          : states.some((s) => s === "voted")
          ? "voted"
          : "not_voted";
        const studentBallots = houseBallots.filter((b) => b.admissionNo === stu.admissionNo);
        const acceptedBallots = studentBallots.filter((b) => b.status === "accepted");
        return { stu, vStatus, acceptedBallots, studentBallots };
      })
      .filter(({ stu, vStatus }) => {
        if (sFilter && vStatus !== sFilter) return false;
        if (cFilter && normClass(stu.className) !== normClass(cFilter)) return false;
        if (secFilter && normSection(stu.section) !== normSection(secFilter)) return false;
        if (q) {
          const hay = `${stu.admissionNo} ${stu.fullName} ${stu.className}-${stu.section}`.toLowerCase();
          if (!hay.includes(q)) return false;
        }
        return true;
      });

    el.votersTbody.innerHTML = "";
    el.votersEmpty.hidden = rows.length > 0;

    rows.forEach(({ stu, vStatus, acceptedBallots, studentBallots }) => {
      const tr = document.createElement("tr");
      const statusBadge =
        vStatus === "voted"
          ? `<span class="badge badge-success">Voted (${acceptedBallots.length}/${positions.length})</span>`
          : vStatus === "cancelled"
          ? `<span class="badge badge-warning">Cancelled</span>`
          : `<span class="badge badge-muted">Not Voted</span>`;

      tr.innerHTML = `
        <td class="mono"></td>
        <td><strong></strong><div class="stat-note"></div></td>
        <td>${statusBadge}</td>
        <td></td>
        <td></td>
        <td class="mono"></td>
        <td></td>
      `;

      tr.children[0].textContent = stu.admissionNo;
      tr.children[1].querySelector("strong").textContent = stu.fullName;
      tr.children[1].querySelector(".stat-note").textContent = stu.isStaff ? `${stu.subject || "Faculty"} · Teaching Staff` : `Class ${stu.className}-${stu.section}${stu.isCandidate ? " · Candidate" : ""}`;

      if (acceptedBallots.length > 0) {
        const listWrap = document.createElement("div");
        acceptedBallots.forEach((ab) => {
          const p = positions.find((x) => x.id === ab.positionId);
          const line = document.createElement("div");
          line.className = "stat-note";
          line.style.marginBottom = "0.18rem";
          const strong = document.createElement("strong");
          strong.style.color = "var(--text-primary)";
          strong.textContent = p ? p.shortTitle : ab.positionName;
          line.append(strong, `: ${ab.candidateName}`);
          listWrap.appendChild(line);
        });
        tr.children[3].appendChild(listWrap);

        tr.children[4].appendChild(makePhotoCell(acceptedBallots[0], stu.fullName));
        tr.children[5].textContent = formatTime(acceptedBallots[0].castAt);

        const actionWrap = document.createElement("div");
        actionWrap.style.display = "flex";
        actionWrap.style.flexDirection = "column";
        actionWrap.style.gap = "0.28rem";
        acceptedBallots.forEach((ab) => {
          const p = positions.find((x) => x.id === ab.positionId);
          const cancelBtn = document.createElement("button");
          cancelBtn.type = "button";
          cancelBtn.className = "btn btn-danger";
          cancelBtn.style.padding = "0.3rem 0.65rem";
          cancelBtn.style.fontSize = "0.75rem";
          cancelBtn.textContent = p ? `Cancel ${p.shortTitle}` : "Cancel Vote";
          cancelBtn.addEventListener("click", () => openCancelModal(ab));
          actionWrap.appendChild(cancelBtn);
        });
        const delBtn = document.createElement("button");
        delBtn.type = "button";
        delBtn.className = "btn btn-solid-danger";
        delBtn.dataset.deleteAdm = stu.admissionNo;
        delBtn.style.padding = "0.3rem 0.65rem";
        delBtn.style.fontSize = "0.75rem";
        delBtn.textContent = "Delete Ballots";
        delBtn.addEventListener("click", () => openDeleteModal(stu.admissionNo, stu.fullName));
        actionWrap.appendChild(delBtn);
        tr.children[6].appendChild(actionWrap);
      } else {
        tr.children[3].textContent = "—";
        tr.children[4].textContent = "—";
        tr.children[5].textContent = "—";
        if (studentBallots.length > 0) {
          const actionWrap = document.createElement("div");
          actionWrap.style.display = "flex";
          actionWrap.style.flexDirection = "column";
          actionWrap.style.gap = "0.28rem";
          if (vStatus === "cancelled") {
            const note = document.createElement("span");
            note.className = "stat-note";
            note.textContent = "Re-vote allowed";
            actionWrap.appendChild(note);
          }
          const delBtn = document.createElement("button");
          delBtn.type = "button";
          delBtn.className = "btn btn-solid-danger";
          delBtn.dataset.deleteAdm = stu.admissionNo;
          delBtn.style.padding = "0.3rem 0.65rem";
          delBtn.style.fontSize = "0.75rem";
          delBtn.textContent = "Delete Ballots";
          delBtn.addEventListener("click", () => openDeleteModal(stu.admissionNo, stu.fullName));
          actionWrap.appendChild(delBtn);
          tr.children[6].appendChild(actionWrap);
        } else {
          tr.children[6].textContent = vStatus === "cancelled" ? "Re-vote allowed" : "—";
        }
      }

      el.votersTbody.appendChild(tr);
    });

    // Cancelled history section for this house
    const cancelledBallots = houseBallots.filter((b) => b.status === "cancelled");
    el.cancelledCard.hidden = cancelledBallots.length === 0;
    el.cancelledTbody.innerHTML = "";

    const houseCancelledVoterMap = new Map();
    cancelledBallots.forEach((b) => {
      if (!houseCancelledVoterMap.has(b.admissionNo)) {
        houseCancelledVoterMap.set(b.admissionNo, {
          admissionNo: b.admissionNo,
          fullName: b.fullName || b.admissionNo,
          className: b.className || "",
          section: b.section || "",
          houseCode: b.houseCode || house.code,
          photoDataUrl: b.photoDataUrl || "",
          cancelledAt: b.cancelledAt,
          cancelledBy: b.cancelledBy,
          cancelledReason: b.cancelledReason,
          ballots: [],
        });
      }
      const v = houseCancelledVoterMap.get(b.admissionNo);
      v.ballots.push(b);
      if (!v.photoDataUrl && b.photoDataUrl) v.photoDataUrl = b.photoDataUrl;
      if (!v.cancelledBy && b.cancelledBy) v.cancelledBy = b.cancelledBy;
      if (!v.cancelledAt && b.cancelledAt) v.cancelledAt = b.cancelledAt;
    });

    Array.from(houseCancelledVoterMap.values()).forEach((v) => {
      const canceller = v.cancelledBy || "rc4616105@gmail.com";
      const roleCount = v.ballots.length || 4;
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td class="mono">${v.admissionNo}</td>
        <td><strong></strong></td>
        <td>
          <span class="badge badge-warning" style="font-weight:700; padding:3px 8px; font-size:0.75rem;">Cancelled (${roleCount} Posts)</span>
          <div class="stat-note" style="color:var(--text-muted); font-size:0.72rem;">Ballot Choice Confidential</div>
        </td>
        <td></td>
        <td><span class="badge" style="background:rgba(220,38,38,0.1); color:#b91c1c; font-weight:700; border:1px solid rgba(220,38,38,0.25);">👤 ${canceller}</span></td>
        <td class="mono">${formatTime(v.cancelledAt)}</td>
      `;
      tr.children[1].querySelector("strong").textContent = v.fullName;
      if (v.photoDataUrl) {
        const viewBtn = document.createElement("button");
        viewBtn.type = "button";
        viewBtn.className = "btn btn-secondary";
        viewBtn.textContent = "View Photo";
        viewBtn.addEventListener("click", () => openPhotoModal(v));
        tr.children[3].appendChild(viewBtn);
      } else {
        tr.children[3].textContent = "—";
      }
      el.cancelledTbody.appendChild(tr);
    });
  }

  function openPhotoModal(ballot) {
    el.photoModalMeta.textContent = `${ballot.fullName} (ID ${ballot.admissionNo}) · ${house.name} House · Recorded at ${formatTime(ballot.castAt || ballot.cancelledAt)}`;
    el.photoModalImg.src = ballot.photoDataUrl;
    el.photoModal.hidden = false;
  }

  function openCancelModal(ballot) {
    pendingCancelBallotId = ballot.id;
    el.cancelModalDesc.textContent = `Cancel vote for ${ballot.fullName} (ID ${ballot.admissionNo}, voted for ${ballot.candidateName})? The record stays in cancelled history and the student can cast a new vote.`;
    el.cancelErrorText.hidden = true;
    el.cancelModal.hidden = false;
    el.confirmCancelBtn.focus();
  }

  function openDeleteModal(admissionNo, fullName) {
    pendingDeleteAdm = admissionNo;
    const count = (latestSnapshot?.ballots || []).filter((b) => b.admissionNo === admissionNo).length;
    el.deleteModalDesc.textContent = `Delete ALL ballots (${count} record${count === 1 ? "" : "s"}) and clear verification photos for ${fullName || admissionNo} (Admission No. ${admissionNo})? Their voter status will reset to Not Voted.`;
    el.deleteErrorText.hidden = true;
    el.deleteModal.hidden = false;
    el.confirmDeleteBtn.focus();
  }

  async function refreshAll() {
    try {
      latestSnapshot = await window.AdminBackend.getSnapshot();
      renderKPIs(latestSnapshot);
      renderGraphs(latestSnapshot);
      renderVoters(latestSnapshot);
    } catch (err) {
      console.warn("Unable to load house snapshot:", err);
      el.pageSub.textContent = `Supabase error: ${err.message || "Check your Supabase key and supabase/schema.sql."}`;
    }
  }

  // Event Listeners
  el.hkpiButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const target = btn.dataset.hkpiFilter;
      activeHouseKpi = activeHouseKpi === target ? null : target;
      if (latestSnapshot) renderHouseDrilldown(latestSnapshot);
    });
  });

  if (el.closeDrilldownBtn) {
    el.closeDrilldownBtn.addEventListener("click", () => {
      activeHouseKpi = null;
      if (latestSnapshot) renderHouseDrilldown(latestSnapshot);
    });
  }

  if (el.drilldownSearch) {
    el.drilldownSearch.addEventListener("input", () => {
      if (latestSnapshot) renderHouseDrilldown(latestSnapshot);
    });
  }

  if (el.drilldownClassFilter) {
    el.drilldownClassFilter.addEventListener("change", () => {
      updateHouseSectionFilterOptions();
      if (latestSnapshot) renderHouseDrilldown(latestSnapshot);
    });
  }

  if (el.drilldownSectionFilter) {
    el.drilldownSectionFilter.addEventListener("change", () => {
      if (latestSnapshot) renderHouseDrilldown(latestSnapshot);
    });
  }

  el.navBtns.forEach((btn) => {
    btn.addEventListener("click", () => switchView(btn.dataset.view));
  });

  if (el.voterSearch) {
    el.voterSearch.addEventListener("input", () => {
      if (latestSnapshot) renderVoters(latestSnapshot);
    });
  }

  if (el.voterStatusFilter) {
    el.voterStatusFilter.addEventListener("change", () => {
      if (latestSnapshot) renderVoters(latestSnapshot);
    });
  }

  if (el.voterClassFilter) {
    el.voterClassFilter.addEventListener("change", () => {
      updateHouseSectionFilterOptions();
      if (latestSnapshot) renderVoters(latestSnapshot);
    });
  }

  if (el.voterSectionFilter) {
    el.voterSectionFilter.addEventListener("change", () => {
      if (latestSnapshot) renderVoters(latestSnapshot);
    });
  }

  el.refreshBtn.addEventListener("click", refreshAll);

  el.cancelModalClose.addEventListener("click", () => {
    el.cancelModal.hidden = true;
    pendingCancelBallotId = null;
  });

  el.confirmCancelBtn.addEventListener("click", async () => {
    if (!pendingCancelBallotId) return;
    try {
      el.confirmCancelBtn.disabled = true;
      const actorName = (typeof sessionStorage !== "undefined" && (sessionStorage.getItem("spr_admin_email") || sessionStorage.getItem("spr_admin_name"))) || "rc4616105@gmail.com";
      await window.AdminBackend.cancelBallot(
        pendingCancelBallotId,
        "",
        actorName
      );
      el.cancelModal.hidden = true;
      pendingCancelBallotId = null;
      await refreshAll();
    } catch (err) {
      el.cancelErrorText.textContent = err.message;
      el.cancelErrorText.hidden = false;
    } finally {
      el.confirmCancelBtn.disabled = false;
    }
  });

  el.deleteModalClose.addEventListener("click", () => {
    el.deleteModal.hidden = true;
    pendingDeleteAdm = null;
  });

  el.confirmDeleteBtn.addEventListener("click", async () => {
    if (!pendingDeleteAdm) return;
    try {
      el.confirmDeleteBtn.disabled = true;
      el.deleteErrorText.hidden = true;
      await window.AdminBackend.clearStudentBallots(
        pendingDeleteAdm,
        "Principal / Authorized Admin"
      );
      el.deleteModal.hidden = true;
      pendingDeleteAdm = null;
      await refreshAll();
    } catch (err) {
      el.deleteErrorText.textContent = err.message;
      el.deleteErrorText.hidden = false;
    } finally {
      el.confirmDeleteBtn.disabled = false;
    }
  });

  el.photoModalClose.addEventListener("click", () => {
    el.photoModal.hidden = true;
  });

  async function boot() {
    switchView(currentView);
    populateRoleFilterBar();
    populateHouseClassAndSectionFilters();
    let initialBallots = [];
    let initialVoterStatus = {};
    try {
      const cached = JSON.parse(localStorage.getItem("spr_admin_snapshot_cache") || "null");
      if (cached && Array.isArray(cached.ballots) && cached.ballots.length > 0) {
        initialBallots = cached.ballots;
        initialVoterStatus = cached.voterStatus || {};
      }
    } catch (_) {}

    const baseRoster = [
      ...(window.ADMIN_DATA?.students || []),
      ...(window.ADMIN_DATA?.teachers || window.TEACHERS_DATA || []),
    ];
    const seenAdms = new Set();
    const initialStudents = [];
    baseRoster.forEach((s) => {
      if (!seenAdms.has(s.admissionNo)) {
        seenAdms.add(s.admissionNo);
        initialStudents.push({ ...s });
      }
    });
    latestSnapshot = {
      students: initialStudents,
      candidates: window.ADMIN_DATA?.candidates || [],
      voterStatus: initialVoterStatus,
      ballots: initialBallots,
      auditLogs: [],
    };
    renderKPIs(latestSnapshot);
    renderGraphs(latestSnapshot);
    renderVoters(latestSnapshot);

    const mode = await window.AdminBackend.init();
    if (el.sbOfflineBanner) {
      el.sbOfflineBanner.hidden = mode === "supabase";
      if (mode !== "supabase" && el.sbOfflineMsg && window.AdminBackend.backendError) {
        el.sbOfflineMsg.innerHTML = `${escapeHtml(window.AdminBackend.backendError)} Open <a href="./index.html" style="color:inherit;text-decoration:underline;font-weight:700;">All Houses Admin</a> to connect &amp; sync.`;
      }
    }
    await refreshAll();
    window.AdminBackend.subscribeUpdates(async () => {
      await refreshAll();
    });
    setInterval(refreshAll, 2500);
  }

  boot();
})();
