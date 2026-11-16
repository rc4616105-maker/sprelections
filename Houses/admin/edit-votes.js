// Edit & Manage Votes Controller — Full Ballots Management, Choice Editing & Reset
(function () {
  const { houses, electionId, positionId } = window.ADMIN_DATA;
  const houseMap = Object.fromEntries(houses.map((h) => [h.code, h]));

  let latestSnapshot = null;
  let activeView = "ballots"; // 'ballots' | 'search'
  let selectedEditorAdm = null;
  let pendingCancelBallotId = null;
  let pendingDeleteAdm = null;

  const el = {
    refreshBtn: document.getElementById("refresh-btn"),
    navBtnBallots: document.getElementById("nav-btn-ballots"),
    navBtnSearch: document.getElementById("nav-btn-search"),
    sbOfflineBanner: document.getElementById("sb-offline-banner"),
    sbOfflineMsg: document.getElementById("sb-offline-msg"),

    kpiAcceptedBallots: document.getElementById("kpi-accepted-ballots"),
    kpiVotersCount: document.getElementById("kpi-voters-count"),
    kpiCancelledBallots: document.getElementById("kpi-cancelled-ballots"),
    kpiEligibleRoster: document.getElementById("kpi-eligible-roster"),
    kpiRemainingRoster: document.getElementById("kpi-remaining-roster"),
    kpiButtons: Array.from(document.querySelectorAll("[data-ballot-kpi]")),

    viewBallots: document.getElementById("view-ballots"),
    ballotsPanelHeading: document.getElementById("ballots-panel-heading"),
    ballotsPanelCaption: document.getElementById("ballots-panel-caption"),

    ballotSearch: document.getElementById("ballot-search"),
    ballotHouseFilter: document.getElementById("ballot-house-filter"),
    ballotClassFilter: document.getElementById("ballot-class-filter"),
    ballotSectionFilter: document.getElementById("ballot-section-filter"),
    ballotStatusFilter: document.getElementById("ballot-status-filter"),
    ballotsTableTbody: document.getElementById("ballots-table-tbody"),
    ballotsTableEmpty: document.getElementById("ballots-table-empty"),
    emptyIcon: document.getElementById("empty-icon"),
    emptyTitle: document.getElementById("empty-title"),
    emptySubtitle: document.getElementById("empty-subtitle"),

    voteSearchInput: document.getElementById("vote-search-input"),
    voteSearchClear: document.getElementById("vote-search-clear"),
    voteSearchSuggestions: document.getElementById("vote-search-suggestions"),
    voteEditorContent: document.getElementById("vote-editor-content"),
    voterProfileStrip: document.getElementById("voter-profile-strip"),
    voterBallotsList: document.getElementById("voter-ballots-list"),
    voterNoBallots: document.getElementById("voter-no-ballots"),
    voteEditorResetBtn: document.getElementById("vote-editor-reset-btn"),

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

  function formatHouseLabel(name) {
    if (!name) return "";
    const str = String(name).trim();
    if (str.endsWith("House") || str.endsWith("Houses") || str === "School Cabinet") {
      return str;
    }
    return `${str} House`;
  }

  function normClass(c) {
    return String(c || "").trim().toLowerCase().replace(/^class\s*/i, "");
  }

  function normSection(s) {
    return String(s || "").trim().toLowerCase();
  }

  function formatTime(iso) {
    if (!iso) return "—";
    try {
      return new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
    } catch (_) {
      return iso;
    }
  }

  function makePhotoCell(ballot) {
    if (!ballot.photoDataUrl) {
      const span = document.createElement("span");
      span.textContent = "—";
      span.style.color = "var(--text-muted)";
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
    img.alt = `Photo of ${ballot.fullName}`;
    thumbBtn.appendChild(img);
    thumbBtn.addEventListener("click", () => openPhotoModal(ballot));

    const viewBtn = document.createElement("button");
    viewBtn.type = "button";
    viewBtn.className = "btn btn-secondary btn-sm btn-pill";
    viewBtn.textContent = "View Photo";
    viewBtn.addEventListener("click", () => openPhotoModal(ballot));

    wrap.append(thumbBtn, viewBtn);
    return wrap;
  }

  async function openPhotoModal(ballot) {
    const hName = formatHouseLabel(houseMap[ballot.houseCode]?.name || ballot.houseCode);
    el.photoModalMeta.textContent = `${ballot.fullName} (ID ${ballot.admissionNo}) · ${hName} · Cast at ${formatTime(ballot.castAt)}`;
    let photoUrl = ballot.photoDataUrl;
    if (!photoUrl && ballot.photoPath && typeof window.AdminBackend?.resolveSignedPhotoUrl === "function") {
      photoUrl = await window.AdminBackend.resolveSignedPhotoUrl(ballot.photoPath);
      ballot.photoDataUrl = photoUrl;
    }
    el.photoModalImg.src = photoUrl || "";
    el.photoModal.hidden = false;
  }

  let pendingCancelVoter = null;

  function openCancelModal(voterOrBallot) {
    if (voterOrBallot.ballots) {
      pendingCancelVoter = voterOrBallot;
      pendingCancelBallotId = voterOrBallot.ballots[0]?.id || null;
      const count = voterOrBallot.ballots.length;
      el.cancelModalDesc.textContent = `Cancel vote for ${voterOrBallot.fullName} (Voter ID ${voterOrBallot.admissionNo}) across all ${count} leadership posts? The record stays in cancelled history and the student can cast a new vote.`;
    } else {
      pendingCancelVoter = null;
      pendingCancelBallotId = voterOrBallot.id;
      el.cancelModalDesc.textContent = `Cancel vote for ${voterOrBallot.fullName} (ID ${voterOrBallot.admissionNo})? The record stays in cancelled history and the student can cast a new vote.`;
    }
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

  function populateClassAndSectionFilters() {
    if (!el.ballotClassFilter || !el.ballotSectionFilter) return;
    const students = latestSnapshot?.students || window.ADMIN_DATA?.students || [];

    const rawClasses = Array.from(new Set(students.map((s) => String(s.className || "").trim()).filter(Boolean)));
    rawClasses.sort((a, b) => {
      const numA = parseInt(a, 10);
      const numB = parseInt(b, 10);
      if (!isNaN(numA) && !isNaN(numB)) return numB - numA;
      if (!isNaN(numA)) return -1;
      if (!isNaN(numB)) return 1;
      return a.localeCompare(b);
    });

    el.ballotClassFilter.innerHTML = '<option value="">All Classes</option>';
    rawClasses.forEach((cls) => {
      const opt = document.createElement("option");
      opt.value = cls;
      opt.textContent = cls.toLowerCase().startsWith("class") ? cls : `Class ${cls}`;
      el.ballotClassFilter.appendChild(opt);
    });

    const rawSections = Array.from(new Set(students.map((s) => String(s.section || "").trim()).filter(Boolean)));
    rawSections.sort((a, b) => a.localeCompare(b));
    el.ballotSectionFilter.innerHTML = '<option value="">All Sections</option>';
    rawSections.forEach((sec) => {
      const opt = document.createElement("option");
      opt.value = sec;
      opt.textContent = sec;
      el.ballotSectionFilter.appendChild(opt);
    });
  }

    function renderOverviewKpis(snap) {
    const eligible = (snap.students || []).filter((s) => s.isActive).length;
    const acceptedBallotsAll = (snap.ballots || []).filter((b) => b.status === "accepted");
    const votedVotersCount = new Set(acceptedBallotsAll.map((b) => b.admissionNo)).size;
    const cancelledBallotsAll = (snap.ballots || []).filter((b) => b.status === "cancelled");
    const cancelledVotersCount = new Set(cancelledBallotsAll.map((b) => b.admissionNo)).size;

    if (el.kpiAcceptedBallots) el.kpiAcceptedBallots.textContent = String(votedVotersCount);
    if (el.kpiVotersCount) el.kpiVotersCount.textContent = `${acceptedBallotsAll.length} role ballots cast`;
    if (el.kpiCancelledBallots) el.kpiCancelledBallots.textContent = String(cancelledVotersCount);
    if (el.kpiEligibleRoster) el.kpiEligibleRoster.textContent = String(eligible);
    if (el.kpiRemainingRoster) el.kpiRemainingRoster.textContent = String(Math.max(0, eligible - votedVotersCount));
  }

    function updatePanelHeader(target) {
    if (!el.ballotsPanelHeading || !el.ballotsPanelCaption) return;
    if (target === "accepted") {
      el.ballotsPanelHeading.textContent = "Active Accepted Voters Master Register";
      el.ballotsPanelCaption.textContent = "Students who have submitted active votes across booths. Review verification photos or cancel votes.";
    } else if (target === "cancelled") {
      el.ballotsPanelHeading.textContent = "Cancelled Ballots Register";
      el.ballotsPanelCaption.textContent = "Students whose vote was cancelled (excluded from results; student can re-vote). Review who cancelled and delete/reset if authorized.";
    } else if (target === "eligible") {
      el.ballotsPanelHeading.textContent = "Total Eligible Students (Master Register)";
      el.ballotsPanelCaption.textContent = "All 966 active eligible students and faculty across houses.";
    } else if (target === "remaining") {
      el.ballotsPanelHeading.textContent = "Remaining Not Voted Students";
      el.ballotsPanelCaption.textContent = "Eligible students who have not yet completed all leadership role votes.";
    } else {
      el.ballotsPanelHeading.textContent = "All Cast Ballots Master Register";
      el.ballotsPanelCaption.textContent = "Review verification photos, cast timestamps, cancel votes, or delete student ballots.";
    }
  }

  function setKpiFilter(target) {
    if (el.kpiButtons) {
      el.kpiButtons.forEach((btn) => {
        btn.classList.toggle("is-active", btn.dataset.ballotKpi === target);
      });
    }
    if (el.ballotStatusFilter) {
      el.ballotStatusFilter.value = target;
    }
    updatePanelHeader(target);
    if (latestSnapshot) {
      renderBallotsTable(latestSnapshot);
    }
  }

  function makePhotoCell(ballotOrVoter) {
    const photoUrl = ballotOrVoter.photoDataUrl || (ballotOrVoter.ballots && ballotOrVoter.ballots.find((b) => b.photoDataUrl)?.photoDataUrl);
    if (!photoUrl) {
      const span = document.createElement("span");
      span.textContent = "—";
      span.style.color = "var(--text-muted)";
      return span;
    }
    const wrap = document.createElement("div");
    wrap.className = "photo-cell-wrap";

    const thumbBtn = document.createElement("button");
    thumbBtn.type = "button";
    thumbBtn.className = "photo-thumb-btn";
    thumbBtn.title = "View verification photo";
    const img = document.createElement("img");
    img.src = photoUrl;
    img.alt = `Photo of ${ballotOrVoter.fullName || "Voter"}`;
    thumbBtn.appendChild(img);

    const txtBtn = document.createElement("button");
    txtBtn.type = "button";
    txtBtn.className = "photo-text-btn";
    txtBtn.textContent = "View Photo";

    const openPhoto = () => {
      if (el.photoModalImg) el.photoModalImg.src = photoUrl;
      if (el.photoModalMeta) {
        el.photoModalMeta.textContent = `${ballotOrVoter.fullName} · ID ${ballotOrVoter.admissionNo} · Verification Photo`;
      }
      if (el.photoModal) el.photoModal.hidden = false;
    };

    thumbBtn.addEventListener("click", openPhoto);
    txtBtn.addEventListener("click", openPhoto);

    wrap.appendChild(thumbBtn);
    wrap.appendChild(txtBtn);
    return wrap;
  }

  // --- View 1: Render All Ballots Table (1 Consolidated Row Per Voter & Confidential Ballot Secrecy) ---
  function renderBallotsTable(snap) {
    if (!el.ballotsTableTbody) return;
    const q = (el.ballotSearch?.value || "").trim().toLowerCase();
    const hFilter = el.ballotHouseFilter?.value || "";
    const cFilter = el.ballotClassFilter?.value.trim() || "";
    const sFilter = el.ballotSectionFilter?.value.trim() || "";
    const statusFilter = el.ballotStatusFilter?.value || "accepted";

    // Group ballots by voter (admissionNo) to ensure 1 consolidated row per voter and protect ballot secrecy
    const voterMap = new Map();
    (snap.ballots || []).forEach((b) => {
      if (!voterMap.has(b.admissionNo)) {
        voterMap.set(b.admissionNo, {
          admissionNo: b.admissionNo,
          fullName: b.fullName || b.admissionNo,
          className: b.className || "",
          section: b.section || "",
          houseCode: b.houseCode || "",
          photoDataUrl: b.photoDataUrl || "",
          castAt: b.castAt,
          cancelledAt: b.cancelledAt,
          cancelledBy: b.cancelledBy,
          cancelledReason: b.cancelledReason,
          ballots: [],
          hasAccepted: false,
          hasCancelled: false,
        });
      }
      const v = voterMap.get(b.admissionNo);
      v.ballots.push(b);
      if (b.status === "accepted") v.hasAccepted = true;
      if (b.status === "cancelled") v.hasCancelled = true;
      if (!v.photoDataUrl && b.photoDataUrl) v.photoDataUrl = b.photoDataUrl;
      if (!v.castAt && b.castAt) v.castAt = b.castAt;
      if (!v.cancelledBy && b.cancelledBy) v.cancelledBy = b.cancelledBy;
      if (!v.cancelledAt && b.cancelledAt) v.cancelledAt = b.cancelledAt;
    });

    // Handle "remaining" (Pending students who haven't voted)
    if (statusFilter === "remaining") {
      const acceptedAdmSet = new Set((snap.ballots || []).filter((b) => b.status === "accepted").map((b) => b.admissionNo));
      const remainingStudents = (snap.students || [])
        .filter((s) => s.isActive && !acceptedAdmSet.has(s.admissionNo))
        .filter((s) => {
          if (hFilter && s.houseCode !== hFilter) return false;
          if (cFilter && normClass(s.className) !== normClass(cFilter)) return false;
          if (sFilter && normSection(s.section) !== normSection(sFilter)) return false;
          if (q) {
            const hay = `${s.admissionNo} ${s.fullName} ${s.className}-${s.section}`.toLowerCase();
            if (!hay.includes(q)) return false;
          }
          return true;
        })
        .sort((a, b) => a.admissionNo.localeCompare(b.admissionNo));

      el.ballotsTableTbody.innerHTML = "";
      if (el.ballotsTableEmpty) {
        el.ballotsTableEmpty.hidden = remainingStudents.length > 0;
        if (remainingStudents.length === 0) {
          if (el.emptyIcon) el.emptyIcon.textContent = "🎉";
          if (el.emptyTitle) el.emptyTitle.textContent = "All Students Have Voted!";
          if (el.emptySubtitle) el.emptySubtitle.textContent = "100% voter turnout achieved.";
        }
      }

      remainingStudents.forEach((s) => {
        const house = houseMap[s.houseCode] || { name: s.houseCode, accentText: "#141413" };
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td class="mono" style="font-weight:700;"></td>
          <td>
            <strong></strong>
            <div class="stat-note"></div>
          </td>
          <td><strong style="color:${house.accentText};">${formatHouseLabel(house.name)}</strong></td>
          <td><span class="stat-note" style="color:var(--text-muted); font-style:italic;">No vote cast yet</span></td>
          <td><span class="stat-note">—</span></td>
          <td><span class="stat-note">—</span></td>
          <td><span class="badge badge-muted">Not Voted</span></td>
          <td><span class="stat-note">—</span></td>
        `;

        tr.children[0].textContent = s.admissionNo;
        tr.children[1].querySelector("strong").textContent = s.fullName;
        const clsSec = s.className ? `Class ${s.className}-${s.section || "--"}` : (s.section || "--");
        tr.children[1].querySelector(".stat-note").textContent = clsSec;

        el.ballotsTableTbody.appendChild(tr);
      });
      return;
    }

    // Handle "eligible" (All 966 registered students & faculty)
    if (statusFilter === "eligible") {
      const acceptedAdmSet = new Set((snap.ballots || []).filter((b) => b.status === "accepted").map((b) => b.admissionNo));
      const cancelledAdmSet = new Set((snap.ballots || []).filter((b) => b.status === "cancelled").map((b) => b.admissionNo));

      const eligibleStudents = (snap.students || [])
        .filter((s) => s.isActive)
        .filter((s) => {
          if (hFilter && s.houseCode !== hFilter) return false;
          if (cFilter && normClass(s.className) !== normClass(cFilter)) return false;
          if (sFilter && normSection(s.section) !== normSection(sFilter)) return false;
          if (q) {
            const hay = `${s.admissionNo} ${s.fullName} ${s.className}-${s.section}`.toLowerCase();
            if (!hay.includes(q)) return false;
          }
          return true;
        })
        .sort((a, b) => a.admissionNo.localeCompare(b.admissionNo));

      el.ballotsTableTbody.innerHTML = "";
      if (el.ballotsTableEmpty) {
        el.ballotsTableEmpty.hidden = eligibleStudents.length > 0;
        if (eligibleStudents.length === 0) {
          if (el.emptyIcon) el.emptyIcon.textContent = "📋";
          if (el.emptyTitle) el.emptyTitle.textContent = "No Students Found";
          if (el.emptySubtitle) el.emptySubtitle.textContent = "No eligible students match the current filters.";
        }
      }

      eligibleStudents.forEach((s) => {
        const house = houseMap[s.houseCode] || { name: s.houseCode, accentText: "#141413" };
        const hasAccepted = acceptedAdmSet.has(s.admissionNo);
        const hasCancelled = cancelledAdmSet.has(s.admissionNo);
        const voterData = voterMap.get(s.admissionNo);

        const roleCount = s.houseCode === "CENTRAL" || s.isStaff ? 5 : 4;
        const votedStatusHtml = hasAccepted
          ? `<span class="badge badge-success" style="font-weight:700; padding:4px 9px; font-size:0.8rem; background:rgba(21,128,61,0.12); color:#15803d; border:1px solid rgba(21,128,61,0.3);">✓ Voted (All ${roleCount} Posts)</span><div class="stat-note" style="color:var(--text-muted); margin-top:3px; font-size:0.75rem;">Ballot Choice Confidential</div>`
          : hasCancelled
          ? `<span class="badge badge-warning" style="font-weight:700; padding:4px 9px; font-size:0.8rem;">Cancelled (${roleCount} Posts)</span><div class="stat-note" style="color:var(--text-muted); margin-top:3px; font-size:0.75rem;">Ballot Choice Confidential</div>`
          : `<span class="stat-note" style="color:var(--text-muted); font-style:italic;">No vote cast yet</span>`;

        const statusBadge = hasAccepted
          ? `<span class="badge badge-success">Accepted</span>`
          : hasCancelled
          ? `<span class="badge badge-warning">Cancelled</span>`
          : `<span class="badge badge-muted">Not Voted</span>`;

        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td class="mono" style="font-weight:700;"></td>
          <td>
            <strong></strong>
            <div class="stat-note"></div>
          </td>
          <td><strong style="color:${house.accentText};">${formatHouseLabel(house.name)}</strong></td>
          <td>${votedStatusHtml}</td>
          <td></td>
          <td class="mono" style="font-size:0.8rem;">${hasAccepted ? formatTime(voterData?.castAt) : (hasCancelled ? formatTime(voterData?.cancelledAt) : "—")}</td>
          <td>${statusBadge}</td>
          <td>
            <div class="action-stack">
              ${hasAccepted ? '<button type="button" class="btn-action-cancel btn-cancel-row">Cancel Vote</button>' : ""}
              ${(hasAccepted || hasCancelled) ? '<button type="button" class="btn-action-delete btn-delete-row">Delete</button>' : '<span class="stat-note">—</span>'}
            </div>
          </td>
        `;

        tr.children[0].textContent = s.admissionNo;
        tr.children[1].querySelector("strong").textContent = s.fullName;
        const clsSec = s.className ? `Class ${s.className}-${s.section || "--"}` : (s.section || "--");
        tr.children[1].querySelector(".stat-note").textContent = clsSec;
        if (voterData) {
          tr.children[4].appendChild(makePhotoCell(voterData));
        } else {
          tr.children[4].innerHTML = '<span class="stat-note">—</span>';
        }

        const cancelBtn = tr.querySelector(".btn-cancel-row");
        if (cancelBtn && voterData) {
          cancelBtn.addEventListener("click", () => openCancelModal(voterData));
        }
        const delBtn = tr.querySelector(".btn-delete-row");
        if (delBtn) {
          delBtn.addEventListener("click", () => openDeleteModal(s.admissionNo, s.fullName));
        }

        el.ballotsTableTbody.appendChild(tr);
      });
      return;
    }

    // Filter voterRows (accepted, cancelled, or all cast ballots)
    const voterRows = Array.from(voterMap.values()).filter((v) => {
      const isAccepted = v.hasAccepted;
      if (statusFilter === "accepted" && !isAccepted) return false;
      if (statusFilter === "cancelled" && (!v.hasCancelled || isAccepted)) return false;
      if (hFilter && v.houseCode !== hFilter) return false;
      if (cFilter && normClass(v.className) !== normClass(cFilter)) return false;
      if (sFilter && normSection(v.section) !== normSection(sFilter)) return false;
      if (q) {
        const hay = `${v.admissionNo} ${v.fullName} ${v.className}-${v.section}`.toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });

    el.ballotsTableTbody.innerHTML = "";
    if (el.ballotsTableEmpty) {
      el.ballotsTableEmpty.hidden = voterRows.length > 0;
      if (voterRows.length === 0) {
        if (el.emptyIcon) el.emptyIcon.textContent = "🗳️";
        if (statusFilter === "cancelled") {
          if (el.emptyTitle) el.emptyTitle.textContent = "No Cancelled Ballots Found";
          if (el.emptySubtitle) el.emptySubtitle.textContent = "No cancelled ballots match the current filters.";
        } else if (statusFilter === "accepted") {
          if (el.emptyTitle) el.emptyTitle.textContent = "No Accepted Ballots Found";
          if (el.emptySubtitle) el.emptySubtitle.textContent = "No active votes match the current filters.";
        } else {
          if (el.emptyTitle) el.emptyTitle.textContent = "No Ballots Found";
          if (el.emptySubtitle) el.emptySubtitle.textContent = "No cast ballots match the current filters.";
        }
      }
    }

    voterRows.forEach((v) => {
      const house = houseMap[v.houseCode] || { name: v.houseCode, accentText: "#141413" };
      const isAccepted = v.hasAccepted;
      const canceller = v.cancelledBy || "rc4616105@gmail.com";
      const statusBadge = isAccepted
        ? `<span class="badge badge-success">Accepted</span>`
        : `<span class="badge badge-warning">Cancelled</span><div class="stat-note" style="color:#b91c1c; margin-top:2px; font-weight:600;">By: ${canceller}</div>`;

      const roleCount = v.ballots.length || (v.houseCode === "CENTRAL" ? 5 : 4);
      const votedStatusHtml = isAccepted
        ? `<span class="badge badge-success" style="font-weight:700; padding:4px 9px; font-size:0.8rem; background:rgba(21,128,61,0.12); color:#15803d; border:1px solid rgba(21,128,61,0.3);">✓ Voted (All ${roleCount} Posts)</span>`
        : `<span class="badge badge-warning" style="font-weight:700; padding:4px 9px; font-size:0.8rem;">Cancelled (${roleCount} Posts)</span>`;

      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td class="mono" style="font-weight:700;"></td>
        <td>
          <strong></strong>
          <div class="stat-note"></div>
        </td>
        <td><strong style="color:${house.accentText};">${formatHouseLabel(house.name)}</strong></td>
        <td>
          ${votedStatusHtml}
          <div class="stat-note" style="color:var(--text-muted); margin-top:3px; font-size:0.75rem;">Ballot Choice Confidential</div>
        </td>
        <td></td>
        <td class="mono" style="font-size:0.8rem;">${formatTime(isAccepted ? v.castAt : v.cancelledAt)}</td>
        <td>${statusBadge}</td>
        <td>
          <div class="action-stack">
            ${isAccepted ? '<button type="button" class="btn-action-cancel btn-cancel-row">Cancel Vote</button>' : ""}
            <button type="button" class="btn-action-delete btn-delete-row">Delete</button>
          </div>
        </td>
      `;

      tr.children[0].textContent = v.admissionNo;
      tr.children[1].querySelector("strong").textContent = v.fullName;
      const clsSec = v.className ? `Class ${v.className}-${v.section || "--"}` : (v.section || "--");
      tr.children[1].querySelector(".stat-note").textContent = clsSec;
      tr.children[4].appendChild(makePhotoCell(v));

      // Action Handlers
      const cancelBtn = tr.querySelector(".btn-cancel-row");
      if (cancelBtn) {
        cancelBtn.addEventListener("click", () => openCancelModal(v));
      }

      tr.querySelector(".btn-delete-row").addEventListener("click", () => {
        openDeleteModal(v.admissionNo, v.fullName);
      });

      el.ballotsTableTbody.appendChild(tr);
    });
  }

  // --- View 2: Search & Single-Voter Choice Editor ---
  function loadStudentEditor(admissionNo) {
    if (!admissionNo || !latestSnapshot) return;
    selectedEditorAdm = admissionNo;
    const stu = latestSnapshot.students.find((s) => s.admissionNo === admissionNo);
    if (!stu) return;

    if (el.voteSearchInput) el.voteSearchInput.value = `${stu.admissionNo} - ${stu.fullName}`;
    if (el.voteSearchSuggestions) el.voteSearchSuggestions.hidden = true;
    if (el.voteSearchClear) el.voteSearchClear.hidden = false;
    if (el.voteEditorContent) el.voteEditorContent.hidden = false;

    const house = houseMap[stu.houseCode] || { name: stu.houseCode, accentText: "#141413", accent: "#cc785c" };
    const ballots = (latestSnapshot.ballots || []).filter((b) => b.admissionNo === admissionNo);
    const hasVoted = ballots.some((b) => b.status === "accepted");
    const hasCancelled = ballots.some((b) => b.status === "cancelled");

    const stBadge = hasVoted
      ? `<span class="badge badge-success">Voted (${ballots.filter((b) => b.status === "accepted").length} Ballots)</span>`
      : hasCancelled
      ? `<span class="badge badge-warning">Cancelled (Can Re-vote)</span>`
      : `<span class="badge badge-muted">Not Voted</span>`;

    if (el.voterProfileStrip) {
      el.voterProfileStrip.innerHTML = `
        <div class="voter-profile-main">
          <div class="voter-profile-name">${stu.fullName}</div>
          <div class="voter-profile-meta">
            Voter ID: <strong class="mono">${stu.admissionNo}</strong> · 
            Class: <strong>${stu.className || "--"} (${stu.section || "--"})</strong> · 
            House: <strong style="color:${house.accentText};">${formatHouseLabel(house.name)}</strong>
          </div>
        </div>
        <div>${stBadge}</div>
      `;
    }

    if (el.voterBallotsList) {
      el.voterBallotsList.innerHTML = "";
      if (ballots.length === 0) {
        if (el.voterNoBallots) el.voterNoBallots.hidden = false;
      } else {
        if (el.voterNoBallots) el.voterNoBallots.hidden = true;

        ballots.forEach((b) => {
          const card = document.createElement("div");
          card.className = "ballot-edit-card";

          const isAccepted = b.status === "accepted";
          const canceller = b.cancelledBy || "rc4616105@gmail.com";
          const statusBadge = isAccepted
            ? `<span class="badge badge-success">Accepted</span>`
            : `<span class="badge badge-warning">Cancelled</span> <span class="stat-note" style="color:#b91c1c; font-weight:600;">(By: ${canceller})</span>`;

          const eligibleCands = (latestSnapshot.candidates || window.ADMIN_DATA.candidates || []).filter(
            (c) => c.houseCode === b.houseCode && (c.positionId === b.positionId || !b.positionId) && c.isApproved
          );

          let optionsHtml = "";
          eligibleCands.forEach((c) => {
            const isSelected = c.id === b.candidateId || c.fullName === b.candidateName;
            optionsHtml += `<option value="${c.id}" data-name="${c.fullName}" ${isSelected ? "selected" : ""}>${c.fullName} (${c.section || c.tagline || "Option"})</option>`;
          });

          if (!eligibleCands.some((c) => c.id === b.candidateId || c.fullName === b.candidateName) && b.candidateName) {
            optionsHtml = `<option value="${b.candidateId || ""}" data-name="${b.candidateName}" selected>${b.candidateName} (Current Choice)</option>` + optionsHtml;
          }

          card.innerHTML = `
            <div class="ballot-edit-head">
              <div>
                <span class="ballot-edit-title">${b.positionName || "Leadership Role"}</span>
                <span class="stat-note" style="margin-left:0.5rem;">Cast: ${formatTime(b.castAt)}</span>
              </div>
              <div>${statusBadge}</div>
            </div>
            <div class="ballot-edit-row" style="display:flex; align-items:center; justify-content:space-between; gap:1rem; flex-wrap:wrap;">
              <div>
                <span class="stat-note" style="font-size:0.78rem; text-transform:uppercase; font-weight:700; color:var(--text-muted);">Voted For:</span>
                <strong style="font-size:1.05rem; color:var(--text-primary); margin-left:0.35rem;">${b.candidateName || "Candidate"}</strong>
              </div>
              <div class="action-stack">
                ${isAccepted ? '<button type="button" class="btn-action-cancel btn-cancel-choice">Cancel Vote</button>' : ""}
              </div>
            </div>
          `;

          const cancelChoiceBtn = card.querySelector(".btn-cancel-choice");
          if (cancelChoiceBtn) {
            cancelChoiceBtn.addEventListener("click", () => {
              openCancelModal(b);
            });
          }

          el.voterBallotsList.appendChild(card);
        });
      }
    }

    if (el.voteEditorResetBtn) {
      el.voteEditorResetBtn.onclick = () => {
        openDeleteModal(stu.admissionNo, stu.fullName);
      };
    }
  }

  function switchView(target) {
    activeView = target;
    if (el.navBtnBallots) el.navBtnBallots.classList.toggle("is-active", target === "ballots");
    if (el.navBtnSearch) el.navBtnSearch.classList.toggle("is-active", target === "search");
    if (el.viewBallots) el.viewBallots.hidden = target !== "ballots";
    if (el.viewSearch) el.viewSearch.hidden = target !== "search";
    if (target === "ballots" && latestSnapshot) {
      renderBallotsTable(latestSnapshot);
    }
  }

  let isRefreshing = false;
  async function refreshAll() {
    if (isRefreshing) return;
    isRefreshing = true;
    try {
      latestSnapshot = await window.AdminBackend.getSnapshot();
      renderOverviewKpis(latestSnapshot);
      renderBallotsTable(latestSnapshot);
      if (selectedEditorAdm) {
        loadStudentEditor(selectedEditorAdm);
      }
    } catch (err) {
      console.warn("Unable to load snapshot in edit-votes:", err);
      const sub = document.querySelector(".page-sub");
      if (sub) {
        sub.textContent = `Supabase error: ${err.message || "Check your Supabase connection."}`;
      }
    } finally {
      isRefreshing = false;
    }
  }

  // --- Search Input Listener ---
  if (el.voteSearchInput) {
    el.voteSearchInput.addEventListener("input", () => {
      const q = el.voteSearchInput.value.trim().toLowerCase();
      if (!q || !latestSnapshot) {
        if (el.voteSearchSuggestions) el.voteSearchSuggestions.hidden = true;
        if (el.voteSearchClear) el.voteSearchClear.hidden = true;
        return;
      }
      if (el.voteSearchClear) el.voteSearchClear.hidden = false;
      const matches = latestSnapshot.students
        .filter((s) => s.admissionNo.toLowerCase().includes(q) || s.fullName.toLowerCase().includes(q))
        .slice(0, 8);

      if (matches.length === 0) {
        el.voteSearchSuggestions.innerHTML = '<div style="padding:0.65rem 0.95rem; font-size:0.84rem; color:var(--text-muted);">No matching students found.</div>';
        el.voteSearchSuggestions.hidden = false;
        return;
      }

      el.voteSearchSuggestions.innerHTML = "";
      matches.forEach((s) => {
        const item = document.createElement("div");
        item.className = "search-suggestion-item";
        item.innerHTML = `
          <div>
            <strong class="mono" style="color:var(--accent-text);">${s.admissionNo}</strong> — <strong>${s.fullName}</strong>
            <div class="stat-note">Class ${s.className || "--"} (${s.section || "--"}) · ${formatHouseLabel(s.houseCode)}</div>
          </div>
          <span class="btn btn-secondary" style="font-size:0.75rem; padding:0.2rem 0.5rem; min-height:auto;">Select</span>
        `;
        item.addEventListener("click", () => {
          loadStudentEditor(s.admissionNo);
        });
        el.voteSearchSuggestions.appendChild(item);
      });
      el.voteSearchSuggestions.hidden = false;
    });
  }

  if (el.voteSearchClear) {
    el.voteSearchClear.addEventListener("click", () => {
      el.voteSearchInput.value = "";
      el.voteSearchClear.hidden = true;
      el.voteSearchSuggestions.hidden = true;
      if (el.voteEditorContent) el.voteEditorContent.hidden = true;
      selectedEditorAdm = null;
      el.voteSearchInput.focus();
    });
  }

    // KPI Summary Card Click Listeners (Synchronizes view and filters exactly like Main Dashboard)
  if (el.kpiButtons && el.kpiButtons.length > 0) {
    el.kpiButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        const target = btn.dataset.ballotKpi;
        setKpiFilter(target);
      });
    });
  }

  // Filter Listeners for View 1
  if (el.ballotSearch) el.ballotSearch.addEventListener("input", () => { if (latestSnapshot) renderBallotsTable(latestSnapshot); });
  if (el.ballotHouseFilter) el.ballotHouseFilter.addEventListener("change", () => { if (latestSnapshot) renderBallotsTable(latestSnapshot); });
  if (el.ballotClassFilter) el.ballotClassFilter.addEventListener("change", () => { if (latestSnapshot) renderBallotsTable(latestSnapshot); });
  if (el.ballotSectionFilter) el.ballotSectionFilter.addEventListener("change", () => { if (latestSnapshot) renderBallotsTable(latestSnapshot); });
  if (el.ballotStatusFilter) {
    el.ballotStatusFilter.addEventListener("change", () => {
      const target = el.ballotStatusFilter.value;
      if (el.kpiButtons) {
        el.kpiButtons.forEach((btn) => {
          btn.classList.toggle("is-active", btn.dataset.ballotKpi === target);
        });
      }
      updatePanelHeader(target);
      if (latestSnapshot) renderBallotsTable(latestSnapshot);
    });
  }

  // Nav View Listeners
  if (el.navBtnBallots) el.navBtnBallots.addEventListener("click", () => switchView("ballots"));
  if (el.navBtnSearch) el.navBtnSearch.addEventListener("click", () => switchView("search"));
  if (el.refreshBtn) el.refreshBtn.addEventListener("click", refreshAll);

  // Modal Listeners
  if (el.cancelModalClose) {
    el.cancelModalClose.addEventListener("click", () => {
      el.cancelModal.hidden = true;
      pendingCancelBallotId = null;
    });
  }

  if (el.confirmCancelBtn) {
    el.confirmCancelBtn.addEventListener("click", async () => {
      if (!pendingCancelVoter && !pendingCancelBallotId) return;
      try {
        el.confirmCancelBtn.disabled = true;
        const actorName = (typeof sessionStorage !== "undefined" && (sessionStorage.getItem("spr_admin_email") || sessionStorage.getItem("spr_admin_name"))) || "rc4616105@gmail.com";
        if (pendingCancelVoter && window.AdminBackend.cancelStudentBallots) {
          await window.AdminBackend.cancelStudentBallots(pendingCancelVoter.admissionNo, "", actorName);
        } else if (pendingCancelBallotId) {
          await window.AdminBackend.cancelBallot(pendingCancelBallotId, "", actorName);
        }
        el.cancelModal.hidden = true;
        pendingCancelVoter = null;
        pendingCancelBallotId = null;
        await refreshAll();
      } catch (err) {
        el.cancelErrorText.textContent = err.message;
        el.cancelErrorText.hidden = false;
      } finally {
        el.confirmCancelBtn.disabled = false;
      }
    });
  }

  if (el.deleteModalClose) {
    el.deleteModalClose.addEventListener("click", () => {
      el.deleteModal.hidden = true;
      pendingDeleteAdm = null;
    });
  }

  if (el.confirmDeleteBtn) {
    el.confirmDeleteBtn.addEventListener("click", async () => {
      if (!pendingDeleteAdm) return;
      try {
        el.confirmDeleteBtn.disabled = true;
        el.deleteErrorText.hidden = true;
        const actorName = (typeof sessionStorage !== "undefined" && (sessionStorage.getItem("spr_admin_email") || sessionStorage.getItem("spr_admin_name"))) || "rc4616105@gmail.com";
        await window.AdminBackend.clearStudentBallots(pendingDeleteAdm, actorName);
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
  }

  if (el.photoModalClose) {
    el.photoModalClose.addEventListener("click", () => {
      el.photoModal.hidden = true;
    });
  }

  // --- Add Candidate to Participate Modal Logic ---
  const btnOpenAddCandidate = document.getElementById("btn-open-add-candidate");
  const addCandModal = document.getElementById("add-candidate-modal");
  const addCandForm = document.getElementById("add-candidate-form");
  const addCandClose = document.getElementById("add-cand-modal-close");
  const addCandSubmitBtn = document.getElementById("add-cand-submit-btn");
  const candNameInput = document.getElementById("new-cand-name");
  const candHouseSelect = document.getElementById("new-cand-house");
  const candPositionSelect = document.getElementById("new-cand-position");
  const candClassSelect = document.getElementById("new-cand-class");
  const candSectionInput = document.getElementById("new-cand-section");
  const candAdmInput = document.getElementById("new-cand-adm");
  const candTaglineInput = document.getElementById("new-cand-tagline");
  const addCandError = document.getElementById("add-cand-error");
  const addCandSuccess = document.getElementById("add-cand-success");

  const HOUSE_POSITIONS = [
    { id: "CAPTAIN_BOY", title: "Boys Captain (Class 10 Boy)", defaultClass: "10" },
    { id: "CAPTAIN_GIRL", title: "Girls Captain (Class 10 Girl)", defaultClass: "10" },
    { id: "VICE_CAPTAIN_BOY", title: "Boys Vice Captain (Class 9 Boy)", defaultClass: "9" },
    { id: "VICE_CAPTAIN_GIRL", title: "Girls Vice Captain (Class 9 Girl)", defaultClass: "9" },
  ];

  const CABINET_POSITIONS = [
    { id: "PRESIDENT", title: "School President (Class 10)", defaultClass: "10" },
    { id: "VICE_PRESIDENT", title: "School Vice President (Class 9)", defaultClass: "9" },
    { id: "LITERARY_SECRETARY", title: "Literary Secretary (Class 9)", defaultClass: "9" },
    { id: "SPORTS_SECRETARY", title: "Sports Secretary (Class 9)", defaultClass: "9" },
    { id: "SOCIAL_CULTURAL_SECRETARY", title: "Social & Cultural Secretary (Class 9)", defaultClass: "9" },
  ];

  function updateCandidatePostOptions() {
    if (!candHouseSelect || !candPositionSelect) return;
    const isCabinet = candHouseSelect.value === "CENTRAL";
    const posts = isCabinet ? CABINET_POSITIONS : HOUSE_POSITIONS;
    candPositionSelect.innerHTML = "";
    posts.forEach((p) => {
      const opt = document.createElement("option");
      opt.value = p.id;
      opt.textContent = p.title;
      opt.dataset.defaultClass = p.defaultClass;
      candPositionSelect.appendChild(opt);
    });
    if (posts[0] && candClassSelect) candClassSelect.value = posts[0].defaultClass;
  }

  if (candHouseSelect) {
    candHouseSelect.addEventListener("change", updateCandidatePostOptions);
    updateCandidatePostOptions();
  }

  if (candPositionSelect) {
    candPositionSelect.addEventListener("change", () => {
      const opt = candPositionSelect.options[candPositionSelect.selectedIndex];
      if (opt && opt.dataset.defaultClass && candClassSelect) {
        candClassSelect.value = opt.dataset.defaultClass;
      }
    });
  }

  if (btnOpenAddCandidate && addCandModal) {
    btnOpenAddCandidate.addEventListener("click", () => {
      addCandError.hidden = true;
      addCandSuccess.hidden = true;
      candNameInput.value = "";
      candSectionInput.value = "";
      candAdmInput.value = "";
      candTaglineInput.value = "";
      updateCandidatePostOptions();
      addCandModal.hidden = false;
      setTimeout(() => candNameInput.focus(), 60);
    });
  }

  if (addCandClose && addCandModal) {
    addCandClose.addEventListener("click", () => {
      addCandModal.hidden = true;
    });
  }

  if (addCandForm) {
    addCandForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      addCandError.hidden = true;
      addCandSuccess.hidden = true;

      const fullName = candNameInput.value.trim();
      if (!fullName) {
        addCandError.textContent = "Please enter the candidate's full name.";
        addCandError.hidden = false;
        return;
      }
      const houseCode = candHouseSelect.value;
      const positionId = candPositionSelect.value;
      const opt = candPositionSelect.options[candPositionSelect.selectedIndex];
      const positionName = opt ? opt.textContent : positionId;
      const className = candClassSelect.value.trim();
      const section = candSectionInput.value.trim();
      const admissionNo = candAdmInput.value.trim();
      const tagline = candTaglineInput.value.trim();

      const houseNameMap = {
        BHEESHMA: "Bheeshma House",
        GURUDRONA: "Gurudrona House",
        HANUMAN: "Hanuman House",
        KARNA: "Karna House",
        VASISTHA: "Vasistha House",
        VISHWAMITHRA: "Vishwamithra House",
        CENTRAL: "School Cabinet",
      };

      try {
        addCandSubmitBtn.disabled = true;
        addCandSubmitBtn.textContent = "Saving Candidate... ⏳";

        await window.AdminBackend.addCandidate({
          fullName,
          className,
          section,
          houseCode,
          houseName: houseNameMap[houseCode] || houseCode,
          positionId,
          positionName,
          admissionNo,
          tagline,
        });

        addCandSuccess.textContent = `Candidate "${fullName}" added successfully for ${positionName} in ${houseNameMap[houseCode]}! 🎉`;
        addCandSuccess.hidden = false;

        await refreshAll();

        setTimeout(() => {
          addCandModal.hidden = true;
          addCandSuccess.hidden = true;
        }, 1400);
      } catch (err) {
        addCandError.textContent = err.message || "Failed to add candidate.";
        addCandError.hidden = false;
      } finally {
        addCandSubmitBtn.disabled = false;
        addCandSubmitBtn.textContent = "➕ Save & Add Candidate";
      }
    });
  }

  async function boot() {
    populateClassAndSectionFilters();

    // 1. Instant Cache Render: load latest known ballots from localStorage on frame 1 (0ms!)
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
    renderOverviewKpis(latestSnapshot);

    if (initialBallots.length > 0) {
      renderBallotsTable(latestSnapshot);
    } else {
      // First visit: show clean loading state while fetching from cloud
      if (el.ballotsTableEmpty) {
        el.ballotsTableEmpty.hidden = false;
        if (el.emptyIcon) el.emptyIcon.textContent = "⏳";
        if (el.emptyTitle) el.emptyTitle.textContent = "Loading Live Ballots from Supabase...";
        if (el.emptySubtitle) el.emptySubtitle.textContent = "Connecting to Supabase cloud and fetching latest cast votes.";
      }
    }

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

    // Reset empty state text to normal for subsequent user filtering
    if (el.emptyIcon) el.emptyIcon.textContent = "🗳️";
    if (el.emptyTitle) el.emptyTitle.textContent = "No Ballots Found";
    if (el.emptySubtitle) el.emptySubtitle.textContent = "No cast ballots match the current filters.";

    // Check if URL has ?adm=0000 to pre-filter voter in master register
    const params = new URLSearchParams(window.location.search);
    const qAdm = params.get("adm");
    if (qAdm && el.ballotSearch) {
      el.ballotSearch.value = qAdm;
      if (latestSnapshot) renderBallotsTable(latestSnapshot);
    }

    window.AdminBackend.subscribeUpdates(async () => {
      await refreshAll();
    });

    // Real-time auto-sync every 2 seconds
    setInterval(refreshAll, 2000);
  }

  boot();
})();
