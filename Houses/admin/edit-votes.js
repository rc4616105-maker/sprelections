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

  
  function getDisplayVoterId(s) {
    if (!s) return "--";
    const adm = String(s.admissionNo || "").trim().toUpperCase();

    // 1. Aditya Vikram demo voter code
    if (adm === "1C8492" || adm === "0000") {
      return adm;
    }

    // 2. Teacher / Faculty IDs (e.g. SPRCOM820, SPRTEL770, SPRFAC100) or staff
    if (adm.startsWith("SPR") || s.isStaff || String(s.className || "").toLowerCase().includes("staff") || String(s.role || "").toLowerCase() === "faculty" || s.houseCode === "ALL") {
      return adm;
    }

    // 3. Custom student object flag
    if (s.isCustom) return adm.toUpperCase();

    // 4. Stored custom registered students in localStorage
    try {
      const raw = localStorage.getItem("spr_admin_custom_students");
      if (raw) {
        const list = JSON.parse(raw);
        if (list.some((cs) => String(cs.admissionNo || "").toUpperCase() === adm.toUpperCase())) {
          return adm.toUpperCase();
        }
      }
    } catch (_) {}

    // 5. Matches official 6-character random format: 1 digit + 1 letter + 4 digits (e.g. 1M5168, 1C8492, 9K4821)
    if (/^[0-9][A-Za-z][0-9]{4}$/.test(adm)) {
      return adm.toUpperCase();
    }

    // For all other students who do not have an official 6-character random Voter ID created yet:
    // Per school requirement: "FOR WHOM THEY NOT HAVE IDS IE NOT YET CREATED JUST KEEP -- FOR NOW LATER WE WILL ADD"
    return "--";
  }

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
        } else if (target === "added") {
      el.ballotsPanelHeading.textContent = "Manually Added Students Register";
      el.ballotsPanelCaption.textContent = "Students registered into the roster who were missing from the initial school register.";
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

        // Handle "added" (Manually added students)
    if (statusFilter === "added") {
      const customList = getCustomStudentsList();
      const customSet = new Set(customList.map((s) => String(s.admissionNo).toUpperCase()));
      const acceptedAdmSet = new Set((snap.ballots || []).filter((b) => b.status === "accepted").map((b) => b.admissionNo));
      const cancelledAdmSet = new Set((snap.ballots || []).filter((b) => b.status === "cancelled").map((b) => b.admissionNo));

      const addedStudents = customList
        .filter((s) => {
          if (hFilter && s.houseCode !== hFilter) return false;
          if (cFilter && normClass(s.className) !== normClass(cFilter)) return false;
          if (sFilter && normSection(s.section) !== normSection(sFilter)) return false;
          if (q) {
            const vId = getDisplayVoterId(s);
            const hay = `${vId !== "--" ? vId : ""} ${s.admissionNo} ${s.fullName} ${s.className}-${s.section}`.toLowerCase();
            if (!hay.includes(q)) return false;
          }
          return true;
        })
        .sort((a, b) => {
          const vA = getDisplayVoterId(a);
          const vB = getDisplayVoterId(b);
          if (vA !== "--" && vB === "--") return -1;
          if (vA === "--" && vB !== "--") return 1;
          if (vA !== "--" && vB !== "--") return vA.localeCompare(vB);
          return (a.fullName || "").localeCompare(b.fullName || "");
        });

      el.ballotsTableTbody.innerHTML = "";
      if (el.ballotsTableEmpty) {
        el.ballotsTableEmpty.hidden = addedStudents.length > 0;
        if (addedStudents.length === 0) {
          if (el.emptyIcon) el.emptyIcon.textContent = "📋";
          if (el.emptyTitle) el.emptyTitle.textContent = "No Added Students Found";
          if (el.emptySubtitle) el.emptySubtitle.textContent = "No manually added students match the current filters. Click '+ Add Student' to register one.";
        }
      }

      addedStudents.forEach((s) => {
        const house = houseMap[s.houseCode] || { name: s.houseCode, accentText: "#141413" };
        const hasAccepted = acceptedAdmSet.has(s.admissionNo);
        const hasCancelled = cancelledAdmSet.has(s.admissionNo);
        const roleCount = s.houseCode === "CENTRAL" || s.isStaff ? 5 : 4;
        const votedStatusHtml = hasAccepted
          ? `<span class="badge badge-success" style="font-weight:700; padding:4px 9px; font-size:0.8rem; background:rgba(21,128,61,0.12); color:#15803d; border:1px solid rgba(21,128,61,0.3);">✓ Voted (All ${roleCount} Posts)</span>`
          : hasCancelled
          ? `<span class="badge badge-warning" style="font-weight:700; padding:4px 9px; font-size:0.8rem;">Cancelled (${roleCount} Posts)</span>`
          : `<span class="badge badge-muted" style="padding:4px 9px; font-size:0.8rem;">Not Voted</span>`;

        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td class="mono" style="font-weight:800; color:#0369a1; font-size:1.05rem;">
            <span>${s.admissionNo}</span>
            <button type="button" class="btn btn-secondary btn-copy-adm" data-adm="${s.admissionNo}" style="font-size:0.7rem; padding:0.15rem 0.4rem; margin-left:0.35rem;" title="Copy Voter ID">📋</button>
          </td>
          <td>
            <strong>${s.fullName}</strong>
            <div class="stat-note">${s.className ? `Class ${s.className}-${s.section || "--"}` : (s.section || "--")}</div>
          </td>
          <td><strong style="color:${house.accentText};">${formatHouseLabel(house.name)}</strong></td>
          <td>${votedStatusHtml}</td>
          <td><span class="stat-note">—</span></td>
          <td><span class="stat-note">—</span></td>
          <td><span class="badge badge-success" style="font-size:0.72rem; padding:2px 7px;">Custom Added</span></td>
          <td style="white-space:nowrap;">
            <button type="button" class="btn btn-secondary btn-search-student-direct" data-adm="${s.admissionNo}" style="font-size:0.75rem; padding:0.25rem 0.45rem;">Inspect</button>
            <button type="button" class="btn btn-danger btn-delete-table-student" data-adm="${s.admissionNo}" data-name="${s.fullName}" style="font-size:0.75rem; padding:0.25rem 0.45rem; margin-left:0.3rem; background:#dc2626; border-color:#dc2626; color:#ffffff; font-weight:700;" title="Remove this student">Delete</button>
          </td>
        `;
        el.ballotsTableTbody.appendChild(tr);
      });

      // Bind copy and inspect buttons
      el.ballotsTableTbody.querySelectorAll(".btn-copy-adm").forEach((btn) => {
        btn.addEventListener("click", () => {
          navigator.clipboard.writeText(btn.dataset.adm);
          btn.textContent = "✓";
          setTimeout(() => { btn.textContent = "📋"; }, 1200);
        });
      });
      el.ballotsTableTbody.querySelectorAll(".btn-search-student-direct").forEach((btn) => {
        btn.addEventListener("click", () => {
          if (el.ballotSearch) {
            el.ballotSearch.value = btn.dataset.adm;
            if (latestSnapshot) renderBallotsTable(latestSnapshot);
          }
        });
      });

      // Bind delete button in main table
      el.ballotsTableTbody.querySelectorAll(".btn-delete-table-student").forEach((btn) => {
        btn.addEventListener("click", async () => {
          const adm = btn.dataset.adm;
          const name = btn.dataset.name || adm;
          const confirmDelete = window.confirm(`Are you sure you want to remove student "${name}" (Voter ID: ${adm}) from the voter roster?`);
          if (!confirmDelete) return;

          try {
            btn.disabled = true;
            btn.textContent = "Removing... ⏳";
            await window.AdminBackend.deleteStudent(adm);

            if (latestSnapshot && latestSnapshot.students) {
              latestSnapshot.students = latestSnapshot.students.filter(
                (s) => String(s.admissionNo).toUpperCase() !== String(adm).toUpperCase()
              );
            }

            updateBadgeAddedCount();
            await refreshAll();
          } catch (err) {
            alert("Failed to remove student: " + (err.message || err));
            btn.disabled = false;
            btn.textContent = "Delete";
          }
        });
      });

      return;
    }

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
        .sort((a, b) => {
          const vA = getDisplayVoterId(a);
          const vB = getDisplayVoterId(b);
          if (vA !== "--" && vB === "--") return -1;
          if (vA === "--" && vB !== "--") return 1;
          if (vA !== "--" && vB !== "--") return vA.localeCompare(vB);
          return (a.fullName || "").localeCompare(b.fullName || "");
        });

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

        const vId = getDisplayVoterId(s);
        if (vId === "--") {
          tr.children[0].innerHTML = '<span style="color:var(--text-muted); font-weight:700;">--</span>';
        } else {
          tr.children[0].innerHTML = `<strong class="mono" style="color:#0369a1; font-weight:800; font-size:1.02rem;">${vId}</strong>`;
        }
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
        .sort((a, b) => {
          const vA = getDisplayVoterId(a);
          const vB = getDisplayVoterId(b);
          if (vA !== "--" && vB === "--") return -1;
          if (vA === "--" && vB !== "--") return 1;
          if (vA !== "--" && vB !== "--") return vA.localeCompare(vB);
          return (a.fullName || "").localeCompare(b.fullName || "");
        });

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

        const vId = getDisplayVoterId(s);
        if (vId === "--") {
          tr.children[0].innerHTML = '<span style="color:var(--text-muted); font-weight:700;">--</span>';
        } else {
          tr.children[0].innerHTML = `<strong class="mono" style="color:#0369a1; font-weight:800; font-size:1.02rem;">${vId}</strong>`;
        }
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

        // If searching and no cast ballots matched, check if any registered or added student matches q
    if (voterRows.length === 0 && q) {
      const allStudentsPool = [...(snap.students || [])];
      const customList = getCustomStudentsList();
      customList.forEach((cs) => {
        if (!allStudentsPool.some((s) => String(s.admissionNo).toUpperCase() === String(cs.admissionNo).toUpperCase())) {
          allStudentsPool.push(cs);
        }
      });

      const studentMatches = allStudentsPool.filter((s) => {
        if (hFilter && s.houseCode !== hFilter) return false;
        if (cFilter && normClass(s.className) !== normClass(cFilter)) return false;
        if (sFilter && normSection(s.section) !== normSection(sFilter)) return false;
        const vId = getDisplayVoterId(s);
        const hay = `${vId !== "--" ? vId : ""} ${s.admissionNo} ${s.fullName} ${s.className}-${s.section}`.toLowerCase();
        return hay.includes(q);
      });

      if (studentMatches.length > 0) {
        if (el.ballotsTableEmpty) el.ballotsTableEmpty.hidden = true;
        studentMatches.forEach((s) => {
          const house = houseMap[s.houseCode] || { name: s.houseCode, accentText: "#141413" };
          const vId = getDisplayVoterId(s);
          const tr = document.createElement("tr");
          tr.style.backgroundColor = "rgba(254, 243, 199, 0.35)";
          tr.innerHTML = `
            <td class="mono" style="font-weight:800; color:#0369a1; font-size:1.05rem;">
              ${vId !== "--" ? `<span>${vId}</span>` : `<span style="color:var(--text-muted); font-weight:700;">--</span>`}
            </td>
            <td>
              <strong>${s.fullName}</strong>
              <div class="stat-note">${s.className ? `Class ${s.className}-${s.section || "--"}` : (s.section || "--")}</div>
            </td>
            <td><strong style="color:${house.accentText};">${formatHouseLabel(house.name)}</strong></td>
            <td><span class="badge badge-muted" style="padding:4px 9px; font-size:0.8rem;">Not Voted (Pending)</span></td>
            <td><span class="stat-note">—</span></td>
            <td><span class="stat-note">—</span></td>
            <td><span class="badge badge-muted">PENDING</span></td>
            <td><span class="stat-note" style="color:var(--text-muted); font-style:italic;">No vote cast yet</span></td>
          `;
          el.ballotsTableTbody.appendChild(tr);
        });
        return;
      }
    }

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

      const vId = getDisplayVoterId(v);
        if (vId === "--") {
          tr.children[0].innerHTML = '<span style="color:var(--text-muted); font-weight:700;">--</span>';
        } else {
          tr.children[0].innerHTML = `<strong class="mono" style="color:#0369a1; font-weight:800; font-size:1.02rem;">${vId}</strong>`;
        }
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
      if (stuEl && stuEl.viewStudents && !stuEl.viewStudents.hidden) {
        renderStudentsMasterTable(latestSnapshot);
      }
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
        updateBadgeAddedCount();
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
        updateBadgeAddedCount();
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

  // --- Add Missing Student to Voter List Modal Logic ---
  const btnOpenAddStudent = document.getElementById("btn-open-add-student") || document.getElementById("btn-open-add-candidate");
  const addStudentModal = document.getElementById("add-student-modal") || document.getElementById("add-candidate-modal");
  const addStudentForm = document.getElementById("add-student-form") || document.getElementById("add-candidate-form");
  const addStudentClose = document.getElementById("add-student-modal-close") || document.getElementById("add-cand-modal-close");
  const addStudentSubmitBtn = document.getElementById("add-student-submit-btn") || document.getElementById("add-cand-submit-btn");
  const studentNameInput = document.getElementById("new-student-name") || document.getElementById("new-cand-name");
  const studentFatherInput = document.getElementById("new-student-father");
  const studentGenderSelect = document.getElementById("new-student-gender");
  const studentClassSelect = document.getElementById("new-student-class") || document.getElementById("new-cand-class");
  const studentSectionSelect = document.getElementById("new-student-section");
  const studentHouseSelect = document.getElementById("new-student-house") || document.getElementById("new-cand-house");
  const studentVoterIdInput = document.getElementById("new-student-voter-id") || document.getElementById("new-cand-adm");
  const btnRerollCode = document.getElementById("btn-reroll-code");
  const codeStatusPill = document.getElementById("code-status-pill");
  const codePrefixHint = document.getElementById("code-prefix-hint");
  const codeHintText = document.getElementById("code-hint-text");
  const addStudentError = document.getElementById("add-student-error") || document.getElementById("add-cand-error");
  const addStudentSuccess = document.getElementById("add-student-success") || document.getElementById("add-cand-success");

  let activeRegistrationType = "student"; // "student" | "faculty"
  const typeBtnStudent = document.getElementById("type-btn-student");
  const typeBtnFaculty = document.getElementById("type-btn-faculty");
  const studentFieldsBox = document.getElementById("student-fields-box");
  const facultyFieldsBox = document.getElementById("faculty-fields-box");
  const facultySubjectSelect = document.getElementById("new-faculty-subject");
  const labelVoterName = document.getElementById("label-voter-name");

  function setRegistrationType(type) {
    activeRegistrationType = type;
    if (typeBtnStudent && typeBtnFaculty) {
      if (type === "student") {
        typeBtnStudent.classList.add("active");
        typeBtnStudent.style.background = "#ffffff";
        typeBtnStudent.style.color = "#0f172a";
        typeBtnStudent.style.boxShadow = "0 1px 3px rgba(0,0,0,0.1)";

        typeBtnFaculty.classList.remove("active");
        typeBtnFaculty.style.background = "transparent";
        typeBtnFaculty.style.color = "#64748b";
        typeBtnFaculty.style.boxShadow = "none";

        if (studentFieldsBox) studentFieldsBox.style.display = "block";
        if (facultyFieldsBox) facultyFieldsBox.style.display = "none";
        if (labelVoterName) labelVoterName.textContent = "Student Full Name *";
      } else {
        typeBtnFaculty.classList.add("active");
        typeBtnFaculty.style.background = "#ffffff";
        typeBtnFaculty.style.color = "#0f172a";
        typeBtnFaculty.style.boxShadow = "0 1px 3px rgba(0,0,0,0.1)";

        typeBtnStudent.classList.remove("active");
        typeBtnStudent.style.background = "transparent";
        typeBtnStudent.style.color = "#64748b";
        typeBtnStudent.style.boxShadow = "none";

        if (studentFieldsBox) studentFieldsBox.style.display = "none";
        if (facultyFieldsBox) facultyFieldsBox.style.display = "flex";
        if (labelVoterName) labelVoterName.textContent = "Faculty / Staff Full Name *";
      }
    }
    refreshVoterCode();
  }

  if (typeBtnStudent) {
    typeBtnStudent.addEventListener("click", () => setRegistrationType("student"));
  }
  if (typeBtnFaculty) {
    typeBtnFaculty.addEventListener("click", () => setRegistrationType("faculty"));
  }
  if (facultySubjectSelect) {
    facultySubjectSelect.addEventListener("change", refreshVoterCode);
  }

  const SECTIONS_BY_CLASS = {
    "10": [
      { name: "CS", prefix: "1C" },
      { name: "AC", prefix: "1A" },
      { name: "JLB", prefix: "1J" },
      { name: "MRP", prefix: "1M" },
    ],
    "9": [
      { name: "APJ", prefix: "9A" },
      { name: "AB", prefix: "9A" },
      { name: "KC", prefix: "9K" },
      { name: "SD", prefix: "9S" },
      { name: "VSB", prefix: "9V" },
    ],
    "8": [
      { name: "CK", prefix: "8C" },
      { name: "DS", prefix: "8D" },
      { name: "HG", prefix: "8H" },
      { name: "SG", prefix: "8S" },
      { name: "SV", prefix: "8S" },
    ],
    "7": [
      { name: "ASR", prefix: "7A" },
      { name: "BS", prefix: "7B" },
      { name: "CSA", prefix: "7C" },
      { name: "RG", prefix: "7R" },
      { name: "SCB", prefix: "7S" },
      { name: "SG", prefix: "7S" },
    ],
    "6": [
      { name: "AMBEDKAR", prefix: "6A" },
      { name: "BCP", prefix: "6B" },
      { name: "BGT", prefix: "6B" },
      { name: "LLR", prefix: "6L" },
      { name: "VS", prefix: "6V" },
    ],
  };

  function getActivePrefix() {
    const c = studentClassSelect ? studentClassSelect.value : "10";
    if (studentSectionSelect) {
      const opt = studentSectionSelect.options[studentSectionSelect.selectedIndex];
      if (opt && opt.dataset.prefix) return opt.dataset.prefix.toUpperCase();
    }
    const list = SECTIONS_BY_CLASS[c] || [];
    return (list[0] && list[0].prefix) || (c.charAt(0) + "S");
  }

  function getAllExistingVoterIds() {
    const set = new Set();
    const students = latestSnapshot?.students || window.ADMIN_DATA?.students || [];
    students.forEach((s) => {
      if (s.admissionNo) set.add(String(s.admissionNo).trim().toUpperCase());
    });
    const ballots = latestSnapshot?.ballots || [];
    ballots.forEach((b) => {
      if (b.admissionNo) set.add(String(b.admissionNo).trim().toUpperCase());
    });
    try {
      const raw = localStorage.getItem("spr_admin_custom_students");
      if (raw) {
        JSON.parse(raw).forEach((cs) => {
          if (cs.admissionNo) set.add(String(cs.admissionNo).trim().toUpperCase());
        });
      }
    } catch (_) {}
    return set;
  }

  const FACULTY_SUBJECT_CODES = {
    "Maths": "MAT",
    "Science": "SCI",
    "English": "ENG",
    "Telugu": "TEL",
    "Hindi": "HIN",
    "Social": "SOC",
    "Computer": "COM",
    "Physics": "PHY",
    "Chemistry": "CHE",
    "Biology": "BIO",
    "PET": "PET",
    "Art": "ART",
    "AO": "AO",
    "Correspondent": "COR",
    "Faculty": "FAC",
  };

  function getFacultyPrefix() {
    const subj = facultySubjectSelect ? facultySubjectSelect.value : "Faculty";
    const code = FACULTY_SUBJECT_CODES[subj] || subj.slice(0, 3).toUpperCase();
    return `SPR${code}`;
  }

  function generateUniqueFacultyVoterId() {
    const prefix = getFacultyPrefix();
    const existing = getAllExistingVoterIds();
    let attempts = 0;
    while (attempts < 3000) {
      attempts++;
      const arr = new Uint32Array(1);
      (window.crypto || window.msCrypto).getRandomValues(arr);
      const randNum = 100 + (arr[0] % 900);
      const code = `${prefix}${randNum}`;
      if (!existing.has(code)) {
        return code;
      }
    }
    return `${prefix}${Math.floor(100 + Math.random() * 900)}`;
  }

  function generateUnique6CharVoterId() {
    const prefix = getActivePrefix();
    const existing = getAllExistingVoterIds();
    let attempts = 0;
    while (attempts < 3000) {
      attempts++;
      // Cryptographically secure 4 random digits (1000 - 9999)
      const arr = new Uint32Array(1);
      (window.crypto || window.msCrypto).getRandomValues(arr);
      const randNum = 1000 + (arr[0] % 9000);
      const numStr = String(randNum);

      // Rule out repeating digits (e.g. 1111, 2222)
      if (/^(\d)\1{3}$/.test(numStr)) continue;

      // Rule out simple ascending/descending sequences
      const sequences = ["1234", "2345", "3456", "4567", "5678", "6789", "4321", "5432", "6543", "7654", "8765", "9876", "0123"];
      if (sequences.includes(numStr)) continue;

      const code = `${prefix}${numStr}`;
      if (!existing.has(code)) {
        return code;
      }
    }
    return `${prefix}${Math.floor(1000 + Math.random() * 9000)}`;
  }

  function refreshVoterCode() {
    if (!studentVoterIdInput) return;
    if (activeRegistrationType === "faculty") {
      const newCode = generateUniqueFacultyVoterId();
      studentVoterIdInput.value = newCode;
      if (codePrefixHint) codePrefixHint.textContent = getFacultyPrefix();
      if (codeHintText) {
        codeHintText.textContent = `Prefix matches Faculty (${getFacultyPrefix()}) + 3 non-sequential random digits.`;
      }
      if (codeStatusPill) {
        codeStatusPill.textContent = "✓ Unique Faculty ID";
        codeStatusPill.style.background = "#dcfce7";
        codeStatusPill.style.color = "#15803d";
      }
    } else {
      const newCode = generateUnique6CharVoterId();
      studentVoterIdInput.value = newCode;
      if (codePrefixHint) codePrefixHint.textContent = getActivePrefix();
      if (codeHintText) {
        codeHintText.textContent = "Prefix matches Class & Section · 4 non-sequential random digits. Cannot be identified or sequenced.";
      }
      if (codeStatusPill) {
        codeStatusPill.textContent = "✓ Unique (No Repetition)";
        codeStatusPill.style.background = "#dcfce7";
        codeStatusPill.style.color = "#15803d";
      }
    }
  }

  function populateSectionOptionsForClass() {
    if (!studentClassSelect || !studentSectionSelect) return;
    const c = studentClassSelect.value;
    const sections = SECTIONS_BY_CLASS[c] || [
      { name: "Section A", prefix: c.charAt(0) + "A" },
      { name: "Section B", prefix: c.charAt(0) + "B" },
    ];
    studentSectionSelect.innerHTML = "";
    sections.forEach((sec) => {
      const opt = document.createElement("option");
      opt.value = sec.name;
      opt.textContent = sec.name;
      opt.dataset.prefix = sec.prefix;
      studentSectionSelect.appendChild(opt);
    });
    refreshVoterCode();
  }

  if (studentClassSelect) {
    studentClassSelect.addEventListener("change", populateSectionOptionsForClass);
  }
  if (studentSectionSelect) {
    studentSectionSelect.addEventListener("change", refreshVoterCode);
  }
  if (btnRerollCode) {
    btnRerollCode.addEventListener("click", () => {
      refreshVoterCode();
      if (studentVoterIdInput) {
        studentVoterIdInput.style.transform = "scale(1.04)";
        setTimeout(() => { studentVoterIdInput.style.transform = "scale(1)"; }, 150);
      }
    });
  }

  if (studentVoterIdInput) {
    studentVoterIdInput.addEventListener("input", () => {
      const val = studentVoterIdInput.value.trim().toUpperCase();
      studentVoterIdInput.value = val;
      const existing = getAllExistingVoterIds();
      const isFac = activeRegistrationType === "faculty";
      const isValidLen = isFac ? (val.startsWith("SPR") && val.length === 9) : (val.length === 6);

      if (isValidLen && !existing.has(val)) {
        if (codeStatusPill) {
          codeStatusPill.textContent = "✓ Unique";
          codeStatusPill.style.background = "#dcfce7";
          codeStatusPill.style.color = "#15803d";
        }
      } else if (existing.has(val)) {
        if (codeStatusPill) {
          codeStatusPill.textContent = "⚠ Already in Use";
          codeStatusPill.style.background = "#fee2e2";
          codeStatusPill.style.color = "#b91c1c";
        }
      } else {
        if (codeStatusPill) {
          codeStatusPill.textContent = isFac ? `${val.length}/9 chars (SPR...)` : `${val.length}/6 chars`;
          codeStatusPill.style.background = "#f1f5f9";
          codeStatusPill.style.color = "#475569";
        }
      }
    });
  }

  if (btnOpenAddStudent && addStudentModal) {
    btnOpenAddStudent.addEventListener("click", () => {
      if (addStudentError) addStudentError.hidden = true;
      if (addStudentSuccess) addStudentSuccess.hidden = true;
      if (studentNameInput) studentNameInput.value = "";
      if (studentFatherInput) studentFatherInput.value = "";
      setRegistrationType("student");
      populateSectionOptionsForClass();
      addStudentModal.hidden = false;
      setTimeout(() => studentNameInput && studentNameInput.focus(), 60);
    });
  }

  if (addStudentClose && addStudentModal) {
    addStudentClose.addEventListener("click", () => {
      addStudentModal.hidden = true;
    });
  }

  if (addStudentForm) {
    addStudentForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (addStudentError) addStudentError.hidden = true;
      if (addStudentSuccess) addStudentSuccess.hidden = true;

      const isFaculty = activeRegistrationType === "faculty";
      const fullName = (studentNameInput ? studentNameInput.value : "").trim();
      if (!fullName) {
        addStudentError.textContent = isFaculty ? "Please enter faculty member's full name." : "Please enter the student's full name.";
        addStudentError.hidden = false;
        return;
      }
      const fatherName = (studentFatherInput ? studentFatherInput.value : "").trim();
      const gender = (studentGenderSelect ? studentGenderSelect.value : "Boy").trim();
      const className = isFaculty ? "Staff" : (studentClassSelect ? studentClassSelect.value : "10").trim();
      const section = isFaculty ? (facultySubjectSelect ? facultySubjectSelect.value : "Faculty") : (studentSectionSelect ? studentSectionSelect.value : "").trim();
      const houseCode = isFaculty ? "ALL" : (studentHouseSelect ? studentHouseSelect.value : "BHEESHMA").trim();
      const admissionNo = (studentVoterIdInput ? studentVoterIdInput.value : "").trim().toUpperCase();

      if (isFaculty) {
        if (!admissionNo.startsWith("SPR") || admissionNo.length !== 9) {
          addStudentError.textContent = "Faculty Voter ID must start with SPR and be exactly 9 characters (e.g. SPRMAT450).";
          addStudentError.hidden = false;
          return;
        }
      } else {
        if (admissionNo.length !== 6) {
          addStudentError.textContent = "Student Voter ID must be exactly 6 characters.";
          addStudentError.hidden = false;
          return;
        }
      }

      const houseNameMap = {
        BHEESHMA: "Bheeshma House",
        GURUDRONA: "Gurudrona House",
        HANUMAN: "Hanuman House",
        KARNA: "Karna House",
        VASISTHA: "Vasistha House",
        VISHWAMITHRA: "Vishwamithra House",
        ALL: "All Houses & Cabinet",
      };

      try {
        if (addStudentSubmitBtn) {
          addStudentSubmitBtn.disabled = true;
          addStudentSubmitBtn.textContent = isFaculty ? "Registering Faculty... ⏳" : "Registering Student... ⏳";
        }

        await window.AdminBackend.addStudent({
          fullName,
          fatherName,
          gender,
          className,
          section,
          houseCode,
          admissionNo,
          isStaff: isFaculty,
        });

        // Also add to latestSnapshot so table and KPI updates immediately
        if (latestSnapshot && latestSnapshot.students) {
          const newStudentObj = {
            admissionNo,
            fullName,
            fatherName,
            gender,
            className,
            section,
            houseCode,
            isStaff: isFaculty,
            isActive: true,
            isCandidate: false,
            photoUrl: isFaculty
              ? "../assets/candidates/teacher_demo.jpg"
              : gender === "Girl" ? "../assets/candidates/girl_demo.jpg" : "../assets/candidates/student_demo.jpg",
          };
          if (!latestSnapshot.students.some((s) => s.admissionNo === admissionNo)) {
            latestSnapshot.students.push(newStudentObj);
          }
        }

        addStudentSuccess.textContent = isFaculty
          ? `Faculty member "${fullName}" registered successfully with Voter ID: ${admissionNo}! 🎉`
          : `Student "${fullName}" registered successfully with Voter ID: ${admissionNo} in ${houseNameMap[houseCode]}! 🎉`;
        addStudentSuccess.hidden = false;

        updateBadgeAddedCount();
        await refreshAll();

        setTimeout(() => {
          addStudentModal.hidden = true;
          addStudentSuccess.hidden = true;
        }, 1600);
      } catch (err) {
        addStudentError.textContent = err.message || "Failed to add voter.";
        addStudentError.hidden = false;
      } finally {
        if (addStudentSubmitBtn) {
          addStudentSubmitBtn.disabled = false;
          addStudentSubmitBtn.textContent = isFaculty ? "➕ Save & Register Faculty" : "➕ Save & Register Student";
        }
      }
    });
  }

    // --- View Added Students Modal & Controller ---
  const btnViewAddedStudents = document.getElementById("btn-view-added-students");
  const viewAddedModal = document.getElementById("view-added-modal");
  const viewAddedModalClose = document.getElementById("view-added-modal-close");
  const viewAddedModalCloseX = document.getElementById("view-added-modal-close-x");
  const btnOpenAddFromView = document.getElementById("btn-open-add-from-view");
  const badgeAddedCount = document.getElementById("badge-added-count");
  const modalAddedCountPill = document.getElementById("modal-added-count-pill");
  const addedStudentsTbody = document.getElementById("added-students-tbody");
  const addedStudentsEmpty = document.getElementById("added-students-empty");

  function getCustomStudentsList() {
    const customMap = new Map();
    try {
      const raw = localStorage.getItem("spr_admin_custom_students");
      if (raw) {
        JSON.parse(raw).forEach((cs) => {
          if (cs && cs.admissionNo) {
            customMap.set(String(cs.admissionNo).toUpperCase(), { ...cs, isCustom: true });
          }
        });
      }
    } catch (_) {}

    const students = latestSnapshot?.students || window.ADMIN_DATA?.students || [];
    students.forEach((s) => {
      if (s && s.admissionNo) {
        const up = String(s.admissionNo).toUpperCase();
        if (s.isCustom || customMap.has(up)) {
          customMap.set(up, { ...s, isCustom: true });
        }
      }
    });

    return Array.from(customMap.values());
  }

  function updateBadgeAddedCount() {
    const list = getCustomStudentsList();
    const count = list.length;
    if (badgeAddedCount) badgeAddedCount.textContent = count;
    const badgeAlt = document.getElementById("badge-added-count-alt");
    if (badgeAlt) badgeAlt.textContent = count;
    if (modalAddedCountPill) modalAddedCountPill.textContent = `${count} Student${count === 1 ? "" : "s"}`;
  }

  function renderAddedStudentsModalList() {
    const list = getCustomStudentsList();
    updateBadgeAddedCount();
    if (!addedStudentsTbody) return;
    addedStudentsTbody.innerHTML = "";

    if (list.length === 0) {
      if (addedStudentsEmpty) addedStudentsEmpty.hidden = false;
      return;
    }
    if (addedStudentsEmpty) addedStudentsEmpty.hidden = true;

    const acceptedAdmSet = new Set((latestSnapshot?.ballots || []).filter((b) => b.status === "accepted").map((b) => String(b.admissionNo).toUpperCase()));

    list.forEach((s) => {
      const house = houseMap[s.houseCode] || { name: s.houseCode, accentText: "#141413" };
      const hasVoted = acceptedAdmSet.has(String(s.admissionNo).toUpperCase());
      const statusBadge = hasVoted
        ? `<span class="badge badge-success" style="font-weight:700; padding:3px 8px; font-size:0.75rem;">✓ Voted</span>`
        : `<span class="badge badge-muted" style="padding:3px 8px; font-size:0.75rem;">Not Voted</span>`;

      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td class="mono" style="font-weight:800; font-size:1.05rem; color:#0369a1;">
          <span>${s.admissionNo}</span>
          <button type="button" class="btn btn-secondary btn-copy-adm-modal" data-adm="${s.admissionNo}" style="font-size:0.7rem; padding:0.15rem 0.4rem; margin-left:0.35rem;" title="Copy Voter ID">📋</button>
        </td>
        <td>
          <strong>${s.fullName}</strong>
          <div class="stat-note">${s.className ? `Class ${s.className}-${s.section || "--"}` : (s.section || "--")}</div>
        </td>
        <td><strong style="color:${house.accentText};">${formatHouseLabel(house.name)}</strong></td>
        <td>${statusBadge}</td>
        <td style="white-space:nowrap;">
          <button type="button" class="btn btn-secondary btn-view-in-table" data-adm="${s.admissionNo}" style="font-size:0.75rem; padding:0.25rem 0.5rem;" title="Show in Table">View</button>
          <button type="button" class="btn btn-danger btn-delete-added-student" data-adm="${s.admissionNo}" data-name="${s.fullName}" style="font-size:0.75rem; padding:0.25rem 0.5rem; margin-left:0.35rem; background:#dc2626; border-color:#dc2626; color:#ffffff; font-weight:700;" title="Remove this student">🗑️ Remove</button>
        </td>
      `;
      addedStudentsTbody.appendChild(tr);
    });

    // Copy action in modal
    addedStudentsTbody.querySelectorAll(".btn-copy-adm-modal").forEach((btn) => {
      btn.addEventListener("click", () => {
        navigator.clipboard.writeText(btn.dataset.adm);
        btn.textContent = "✓";
        setTimeout(() => { btn.textContent = "📋"; }, 1200);
      });
    });

    // View in table action: closes modal, switches to All Students Roster, populates search with Voter ID, and scrolls table into view
    addedStudentsTbody.querySelectorAll(".btn-view-in-table").forEach((btn) => {
      btn.addEventListener("click", () => {
        if (viewAddedModal) viewAddedModal.hidden = true;
        const adm = btn.dataset.adm;
        if (typeof switchEditView === "function") {
          switchEditView("students");
          if (stuEl.stuHouseFilter) stuEl.stuHouseFilter.value = "";
          activeStudentHouseFilter = "";
          stuEl.houseFilterPills.forEach((p) => p.classList.toggle("is-active", (p.dataset.house || "") === ""));
          if (stuEl.stuClassFilter) stuEl.stuClassFilter.value = "";
          if (stuEl.stuSectionFilter) stuEl.stuSectionFilter.value = "";
          if (stuEl.stuStatusFilter) stuEl.stuStatusFilter.value = "";
          if (stuEl.stuSearch) stuEl.stuSearch.value = adm;
          if (latestSnapshot) renderStudentsMasterTable(latestSnapshot);
          if (stuEl.viewStudents) {
            stuEl.viewStudents.scrollIntoView({ behavior: "smooth", block: "start" });
          }
        } else {
          if (el.ballotStatusFilter) el.ballotStatusFilter.value = "added";
          if (el.ballotSearch) el.ballotSearch.value = adm;
          if (latestSnapshot) renderBallotsTable(latestSnapshot);
        }
      });
    });

    // Delete action in modal
    addedStudentsTbody.querySelectorAll(".btn-delete-added-student").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const adm = btn.dataset.adm;
        const name = btn.dataset.name || adm;
        const confirmDelete = window.confirm(`Are you sure you want to remove student "${name}" (Voter ID: ${adm}) from the voter roster?`);
        if (!confirmDelete) return;

        try {
          btn.disabled = true;
          btn.textContent = "Removing... ⏳";
          await window.AdminBackend.deleteStudent(adm);

          if (latestSnapshot && latestSnapshot.students) {
            latestSnapshot.students = latestSnapshot.students.filter(
              (s) => String(s.admissionNo).toUpperCase() !== String(adm).toUpperCase()
            );
          }

          renderAddedStudentsModalList();
          updateBadgeAddedCount();
          await refreshAll();
        } catch (err) {
          alert("Failed to remove student: " + (err.message || err));
          btn.disabled = false;
          btn.textContent = "🗑️ Remove";
        }
      });
    });
  }

  if (btnViewAddedStudents && viewAddedModal) {
    btnViewAddedStudents.addEventListener("click", () => {
      renderAddedStudentsModalList();
      viewAddedModal.hidden = false;
    });
  }

  if (viewAddedModalClose && viewAddedModal) {
    viewAddedModalClose.addEventListener("click", () => {
      viewAddedModal.hidden = true;
    });
  }
  if (viewAddedModalCloseX && viewAddedModal) {
    viewAddedModalCloseX.addEventListener("click", () => {
      viewAddedModal.hidden = true;
    });
  }

  if (btnOpenAddFromView && viewAddedModal && addStudentModal) {
    btnOpenAddFromView.addEventListener("click", () => {
      viewAddedModal.hidden = true;
      if (btnOpenAddStudent) btnOpenAddStudent.click();
    });
  }


  
  // ============================================================================
  // ALL STUDENTS MASTER REGISTER (HOUSE-WISE) & EDIT DETAILS
  // ============================================================================
  let activeStudentHouseFilter = "";

  const stuEl = {
    navBtnBallots: document.getElementById("nav-btn-ballots"),
    navBtnStudents: document.getElementById("nav-btn-students"),
    viewBallots: document.getElementById("view-ballots"),
    viewStudents: document.getElementById("view-students"),
    btnSwitchToStudents: document.getElementById("btn-switch-to-students"),
    badgeTotalStudentsCount: document.getElementById("badge-total-students-count"),
    houseFilterPills: document.querySelectorAll(".btn-house-pill"),
    stuSearch: document.getElementById("stu-master-search"),
    stuHouseFilter: document.getElementById("stu-master-house-filter"),
    stuClassFilter: document.getElementById("stu-master-class-filter"),
    stuSectionFilter: document.getElementById("stu-master-section-filter"),
    stuStatusFilter: document.getElementById("stu-master-status-filter"),
    stuTbody: document.getElementById("stu-master-tbody"),
    stuLoading: document.getElementById("stu-master-loading"),
    stuEmpty: document.getElementById("stu-master-empty"),

    // Edit Student Modal
    editModal: document.getElementById("edit-student-modal"),
    editClose: document.getElementById("edit-student-modal-close"),
    editCloseX: document.getElementById("edit-student-modal-close-x"),
    editForm: document.getElementById("edit-student-form"),
    editAdm: document.getElementById("edit-student-adm"),
    editVoterIdDisplay: document.getElementById("edit-student-voter-id-display"),
    editVotedPill: document.getElementById("edit-student-voted-pill"),
    editName: document.getElementById("edit-student-name"),
    editFather: document.getElementById("edit-student-father"),
    editGender: document.getElementById("edit-student-gender"),
    editClass: document.getElementById("edit-student-class"),
    editSection: document.getElementById("edit-student-section"),
    editHouse: document.getElementById("edit-student-house"),
    editError: document.getElementById("edit-student-error"),
    editSuccess: document.getElementById("edit-student-success"),
    editSubmitBtn: document.getElementById("edit-student-submit-btn"),
  };

  let currentStudentsList = [];
  let currentFilteredStudents = [];
  let currentAcceptedAdmSet = new Set();
  let isStuTbodyDelegated = false;

  function switchEditView(viewName) {
    const isStudents = viewName === "students";
    if (stuEl.navBtnBallots) stuEl.navBtnBallots.classList.toggle("is-active", !isStudents);
    if (stuEl.navBtnStudents) stuEl.navBtnStudents.classList.toggle("is-active", isStudents);
    if (stuEl.viewBallots) stuEl.viewBallots.hidden = isStudents;
    if (stuEl.viewStudents) stuEl.viewStudents.hidden = !isStudents;

    const snap = latestSnapshot || {
      students: window.ADMIN_DATA?.students || [],
      ballots: [],
    };
    if (isStudents) {
      renderStudentsMasterTable(snap);
    } else {
      renderBallotsTable(snap);
    }
  }

  if (stuEl.navBtnBallots) {
    stuEl.navBtnBallots.addEventListener("click", () => switchEditView("ballots"));
  }
  if (stuEl.navBtnStudents) {
    stuEl.navBtnStudents.addEventListener("click", () => switchEditView("students"));
  }
  if (stuEl.btnSwitchToStudents) {
    stuEl.btnSwitchToStudents.addEventListener("click", () => switchEditView("students"));
  }

  // Populate dynamic sections for Edit Student modal based on class
  function populateEditStudentSections(selectedSecName) {
    if (!stuEl.editClass || !stuEl.editSection) return;
    const c = stuEl.editClass.value;
    const sections = SECTIONS_BY_CLASS[c] || [
      { name: "Section A", prefix: c.charAt(0) + "A" },
      { name: "Section B", prefix: c.charAt(0) + "B" },
    ];
    stuEl.editSection.innerHTML = "";
    sections.forEach((sec) => {
      const opt = document.createElement("option");
      opt.value = sec.name;
      opt.textContent = sec.name;
      if (selectedSecName && (sec.name === selectedSecName || sec.name.includes(selectedSecName))) {
        opt.selected = true;
      }
      stuEl.editSection.appendChild(opt);
    });
  }

  if (stuEl.editClass) {
    stuEl.editClass.addEventListener("change", () => populateEditStudentSections());
  }

  // Populate sections filter for students master list
  function populateStuMasterSections() {
    if (!stuEl.stuClassFilter || !stuEl.stuSectionFilter) return;
    const c = stuEl.stuClassFilter.value;
    stuEl.stuSectionFilter.innerHTML = '<option value="">All Sections</option>';
    if (!c) return;
    const sections = SECTIONS_BY_CLASS[c] || [];
    sections.forEach((sec) => {
      const opt = document.createElement("option");
      opt.value = sec.name;
      opt.textContent = sec.name;
      stuEl.stuSectionFilter.appendChild(opt);
    });
  }

  if (stuEl.stuClassFilter) {
    stuEl.stuClassFilter.addEventListener("change", () => {
      populateStuMasterSections();
      renderStudentsMasterTable(latestSnapshot || { students: window.ADMIN_DATA?.students });
    });
  }

  // House Filter Pills
  stuEl.houseFilterPills.forEach((pill) => {
    pill.addEventListener("click", () => {
      stuEl.houseFilterPills.forEach((p) => p.classList.remove("is-active"));
      pill.classList.add("is-active");
      activeStudentHouseFilter = pill.dataset.house || "";
      if (stuEl.stuHouseFilter) stuEl.stuHouseFilter.value = activeStudentHouseFilter;
      renderStudentsMasterTable(latestSnapshot || { students: window.ADMIN_DATA?.students });
    });
  });

  if (stuEl.stuHouseFilter) {
    stuEl.stuHouseFilter.addEventListener("change", () => {
      activeStudentHouseFilter = stuEl.stuHouseFilter.value;
      stuEl.houseFilterPills.forEach((p) => {
        p.classList.toggle("is-active", (p.dataset.house || "") === activeStudentHouseFilter);
      });
      renderStudentsMasterTable(latestSnapshot || { students: window.ADMIN_DATA?.students });
    });
  }

  let searchDebounceTimer = null;
  if (stuEl.stuSearch) {
    stuEl.stuSearch.addEventListener("input", () => {
      clearTimeout(searchDebounceTimer);
      searchDebounceTimer = setTimeout(() => {
        renderStudentsMasterTable(latestSnapshot || { students: window.ADMIN_DATA?.students });
      }, 60);
    });
  }
  if (stuEl.stuSectionFilter) {
    stuEl.stuSectionFilter.addEventListener("change", () => {
      renderStudentsMasterTable(latestSnapshot || { students: window.ADMIN_DATA?.students });
    });
  }
  if (stuEl.stuStatusFilter) {
    stuEl.stuStatusFilter.addEventListener("change", () => {
      renderStudentsMasterTable(latestSnapshot || { students: window.ADMIN_DATA?.students });
    });
  }

  // Render All Students Master Register Table
  function renderStudentsMasterTable(snap) {
    if (!stuEl.stuTbody) return;

    // Gather base students from snapshot or fallback to window.ADMIN_DATA
    const sourceList = (snap && snap.students && snap.students.length > 0)
      ? snap.students
      : [...(window.ADMIN_DATA?.students || []), ...(window.ADMIN_DATA?.teachers || window.TEACHERS_DATA || [])];

    // If data is still resolving, show clean loading wheel
    if (!sourceList || sourceList.length === 0) {
      if (stuEl.stuLoading) stuEl.stuLoading.hidden = false;
      if (stuEl.stuEmpty) stuEl.stuEmpty.hidden = true;
      stuEl.stuTbody.innerHTML = "";
      return;
    }

    if (stuEl.stuLoading) stuEl.stuLoading.hidden = true;

    // Gather complete students list (base + overrides + custom)
    const customList = getCustomStudentsList();
    const customMap = new Map(customList.map((cs) => [String(cs.admissionNo).toUpperCase(), cs]));
    const acceptedAdmSet = new Set(((snap && snap.ballots) || []).filter((b) => b.status === "accepted").map((b) => String(b.admissionNo).toUpperCase()));

    const allStudentsMap = new Map();

    // 1. Base students from sourceList
    sourceList.forEach((s) => {
      if (s && s.admissionNo) {
        // Exclude duplicate 0000 demo teacher account so Aditya Vikram appears only once
        if (s.admissionNo === "0000") return;
        const up = String(s.admissionNo).toUpperCase();
        allStudentsMap.set(up, { ...s });
      }
    });

    // 2. Merge custom added students
    customList.forEach((cs) => {
      const up = String(cs.admissionNo).toUpperCase();
      if (!allStudentsMap.has(up)) {
        allStudentsMap.set(up, { ...cs, isCustom: true });
      } else {
        allStudentsMap.set(up, { ...allStudentsMap.get(up), ...cs, isCustom: true });
      }
    });

    const fullList = Array.from(allStudentsMap.values());
    currentStudentsList = fullList;
    currentAcceptedAdmSet = acceptedAdmSet;

    // Update Live House Counts on Pills
    const houseCounts = {
      ALL: fullList.length,
      BHEESHMA: 0,
      GURUDRONA: 0,
      HANUMAN: 0,
      KARNA: 0,
      VASISTHA: 0,
      VISHWAMITHRA: 0,
      FACULTY: 0,
    };

    fullList.forEach((s) => {
      const h = String(s.houseCode || "").toUpperCase();
      if (s.isStaff || s.className === "Staff" || h === "ALL") {
        houseCounts.FACULTY++;
      } else if (houseCounts[h] !== undefined) {
        houseCounts[h]++;
      }
    });

    const setPill = (id, count) => {
      const elP = document.getElementById(id);
      if (elP) elP.textContent = count;
    };
    setPill("pill-count-all", houseCounts.ALL);
    setPill("pill-count-bheeshma", houseCounts.BHEESHMA);
    setPill("pill-count-gurudrona", houseCounts.GURUDRONA);
    setPill("pill-count-hanuman", houseCounts.HANUMAN);
    setPill("pill-count-karna", houseCounts.KARNA);
    setPill("pill-count-vasistha", houseCounts.VASISTHA);
    setPill("pill-count-vishwamithra", houseCounts.VISHWAMITHRA);
    setPill("pill-count-faculty", houseCounts.FACULTY);

    if (stuEl.badgeTotalStudentsCount) {
      stuEl.badgeTotalStudentsCount.textContent = `${fullList.length} Students`;
    }

    // Filter students
    const q = (stuEl.stuSearch?.value || "").trim().toLowerCase();
    const hFilter = activeStudentHouseFilter || stuEl.stuHouseFilter?.value || "";
    const cFilter = stuEl.stuClassFilter?.value.trim() || "";
    const sFilter = stuEl.stuSectionFilter?.value.trim() || "";
    const statusFilter = stuEl.stuStatusFilter?.value || "";

    const filtered = fullList.filter((s) => {
      const sAdmUp = String(s.admissionNo).toUpperCase();
      const hasVoted = acceptedAdmSet.has(sAdmUp);
      const isCustom = s.isCustom || customMap.has(sAdmUp);

      // House Filter
      if (hFilter) {
        if (hFilter === "ALL") {
          if (!s.isStaff && s.className !== "Staff" && s.houseCode !== "ALL") return false;
        } else if (String(s.houseCode || "").toUpperCase() !== hFilter) {
          return false;
        }
      }

      // Class Filter
      if (cFilter) {
        if (cFilter === "Staff") {
          if (!s.isStaff && s.className !== "Staff") return false;
        } else if (normClass(s.className) !== normClass(cFilter)) {
          return false;
        }
      }

      // Section Filter
      if (sFilter && normSection(s.section) !== normSection(sFilter)) return false;

      // Status Filter
      if (statusFilter === "voted" && !hasVoted) return false;
      if (statusFilter === "not_voted" && hasVoted) return false;
      if (statusFilter === "added" && !isCustom) return false;

      // Search Query
      if (q) {
        const vId = getDisplayVoterId(s);
        const hay = `${vId !== "--" ? vId : ""} ${s.admissionNo} ${s.fullName} ${s.className}-${s.section} ${s.houseCode}`.toLowerCase();
        if (!hay.includes(q)) return false;
      }

      return true;
    });

    // Sort: Students with generated Voter IDs / custom added first, then alphabetical by name
    filtered.sort((a, b) => {
      const vA = getDisplayVoterId(a);
      const vB = getDisplayVoterId(b);
      if (vA !== "--" && vB === "--") return -1;
      if (vA === "--" && vB !== "--") return 1;
      if (vA !== "--" && vB !== "--") return vA.localeCompare(vB);
      return (a.fullName || "").localeCompare(b.fullName || "");
    });

    currentFilteredStudents = filtered;

    if (filtered.length === 0) {
      stuEl.stuTbody.innerHTML = "";
      if (stuEl.stuEmpty) stuEl.stuEmpty.hidden = false;
      return;
    }

    if (stuEl.stuEmpty) stuEl.stuEmpty.hidden = true;

    // Fast HTML batch generation using native array join
    const rowsHtml = filtered.map((s) => {
      const sAdmUp = String(s.admissionNo).toUpperCase();
      const vId = getDisplayVoterId(s);
      const hasVoted = acceptedAdmSet.has(sAdmUp);
      const isCustom = s.isCustom || customMap.has(sAdmUp);
      const house = houseMap[s.houseCode] || { name: s.houseCode || "All Houses", accentText: "#141413" };

      return `
        <tr>
          <td class="mono" style="font-weight:800; color:#0369a1; font-size:1.02rem;">
            ${vId !== "--" ? `<span>${vId}</span>` : `<span style="color:var(--text-muted); font-weight:700;">--</span>`}
            ${vId !== "--" ? `<button type="button" class="btn btn-secondary btn-copy-adm-row" data-adm="${vId}" style="font-size:0.68rem; padding:0.15rem 0.35rem; margin-left:0.3rem;" title="Copy Voter ID">📋</button>` : ""}
          </td>
          <td>
            <div style="font-weight:700; color:var(--text-primary); font-size:0.95rem;">${s.fullName}</div>
            <div class="stat-note" style="color:var(--text-muted); font-size:0.78rem;">
              ${s.gender ? `Gender: ${s.gender}` : ""}
              ${isCustom ? ` · <span style="color:#059669; font-weight:700;">[Added]</span>` : ""}
            </div>
          </td>
          <td><strong style="font-size:0.88rem;">${s.className ? `Class ${s.className}` : (s.isStaff ? "Faculty" : "--")}</strong></td>
          <td><span style="font-size:0.86rem; color:var(--text-secondary);">${s.section || "--"}</span></td>
          <td><strong style="color:${house.accentText}; font-size:0.88rem;">${formatHouseLabel(house.name)}</strong></td>
          <td>
            ${hasVoted
              ? `<span class="badge badge-success" style="font-size:0.75rem; padding:3px 8px; font-weight:700;">✓ Voted</span>`
              : `<span class="badge badge-muted" style="font-size:0.75rem; padding:3px 8px;">Not Voted</span>`
            }
          </td>
          <td style="white-space:nowrap;">
            <button type="button" class="btn btn-secondary btn-open-edit-student" data-adm="${s.admissionNo}" style="font-size:0.75rem; padding:0.25rem 0.55rem; font-weight:700; border-color:#cbd5e1;" title="Change student details">
              ✏️ Change
            </button>
            ${isCustom ? `
              <button type="button" class="btn btn-danger btn-delete-custom-student" data-adm="${s.admissionNo}" data-name="${s.fullName}" style="font-size:0.75rem; padding:0.25rem 0.5rem; margin-left:0.25rem; background:#dc2626; border-color:#dc2626; color:#fff; font-weight:700;" title="Remove student">
                🗑️
              </button>
            ` : ""}
          </td>
        </tr>
      `;
    }).join("");

    stuEl.stuTbody.innerHTML = rowsHtml;

    // Attach single delegated event listener once
    if (!isStuTbodyDelegated) {
      isStuTbodyDelegated = true;

      stuEl.stuTbody.addEventListener("click", async (e) => {
        const copyBtn = e.target.closest(".btn-copy-adm-row");
        if (copyBtn) {
          const adm = copyBtn.dataset.adm;
          navigator.clipboard.writeText(adm);
          copyBtn.textContent = "✓";
          setTimeout(() => { copyBtn.textContent = "📋"; }, 1200);
          return;
        }

        const editBtn = e.target.closest(".btn-open-edit-student");
        if (editBtn) {
          const adm = editBtn.dataset.adm;
          const student = currentStudentsList.find((s) => String(s.admissionNo).toUpperCase() === String(adm).toUpperCase());
          if (student) {
            openEditStudentModal(student, currentAcceptedAdmSet.has(String(adm).toUpperCase()));
          }
          return;
        }

        const delBtn = e.target.closest(".btn-delete-custom-student");
        if (delBtn) {
          const adm = delBtn.dataset.adm;
          const name = delBtn.dataset.name || adm;
          const confirmDelete = window.confirm(`Are you sure you want to remove student "${name}" (Voter ID: ${adm}) from the voter register?`);
          if (!confirmDelete) return;

          try {
            delBtn.disabled = true;
            delBtn.textContent = "⏳";
            await window.AdminBackend.deleteStudent(adm);
            updateBadgeAddedCount();
            await refreshAll();
          } catch (err) {
            alert("Failed to remove student: " + (err.message || err));
            delBtn.disabled = false;
            delBtn.textContent = "🗑️";
          }
          return;
        }
      });
    }
  }

  // Open Edit Student Modal
  function openEditStudentModal(student, hasVoted) {
    if (!stuEl.editModal) return;
    stuEl.editAdm.value = student.admissionNo;
    const vId = getDisplayVoterId(student);
    stuEl.editVoterIdDisplay.textContent = vId !== "--" ? vId : "-- (Pending Assignment)";
    if (stuEl.editVotedPill) {
      if (hasVoted) {
        stuEl.editVotedPill.className = "badge badge-success";
        stuEl.editVotedPill.textContent = "✓ Voted";
      } else {
        stuEl.editVotedPill.className = "badge badge-muted";
        stuEl.editVotedPill.textContent = "Not Voted";
      }
    }

    stuEl.editName.value = student.fullName || "";
    stuEl.editFather.value = student.fatherName || "";
    stuEl.editGender.value = student.gender || "Boy";
    const cleanClass = String(student.className || "10").replace(/^class\s*/i, "");
    stuEl.editClass.value = cleanClass;
    populateEditStudentSections(student.section);
    stuEl.editHouse.value = (student.houseCode || "BHEESHMA").toUpperCase();

    if (stuEl.editError) stuEl.editError.hidden = true;
    if (stuEl.editSuccess) stuEl.editSuccess.hidden = true;
    stuEl.editModal.hidden = false;
    stuEl.editName.focus();
  }

  // Close Edit Student Modal
  function closeEditStudentModal() {
    if (stuEl.editModal) stuEl.editModal.hidden = true;
  }
  if (stuEl.editClose) stuEl.editClose.addEventListener("click", closeEditStudentModal);
  if (stuEl.editCloseX) stuEl.editCloseX.addEventListener("click", closeEditStudentModal);

  // Submit Edit Student Details
  if (stuEl.editForm) {
    stuEl.editForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const adm = stuEl.editAdm.value.trim();
      const fullName = stuEl.editName.value.trim();
      const fatherName = stuEl.editFather.value.trim();
      const gender = stuEl.editGender.value;
      const className = stuEl.editClass.value;
      const section = stuEl.editSection.value;
      const houseCode = stuEl.editHouse.value;

      if (!fullName) {
        if (stuEl.editError) {
          stuEl.editError.textContent = "Please enter student full name.";
          stuEl.editError.hidden = false;
        }
        return;
      }

      try {
        stuEl.editSubmitBtn.disabled = true;
        stuEl.editSubmitBtn.textContent = "Saving Changes... ⏳";
        if (stuEl.editError) stuEl.editError.hidden = true;

        await window.AdminBackend.updateStudent({
          admissionNo: adm,
          fullName,
          fatherName,
          gender,
          className,
          section,
          houseCode,
        });

        if (stuEl.editSuccess) {
          stuEl.editSuccess.textContent = `✓ Details updated for ${fullName}!`;
          stuEl.editSuccess.hidden = false;
        }

        setTimeout(async () => {
          closeEditStudentModal();
          stuEl.editSubmitBtn.disabled = false;
          stuEl.editSubmitBtn.textContent = "💾 Save Changes";
          await refreshAll();
        }, 600);
      } catch (err) {
        if (stuEl.editError) {
          stuEl.editError.textContent = err.message || "Failed to update student details.";
          stuEl.editError.hidden = false;
        }
        stuEl.editSubmitBtn.disabled = false;
        stuEl.editSubmitBtn.textContent = "💾 Save Changes";
      }
    });
  }

  // Wire KPI Cards clicking: "eligible" or "remaining" switches view to students master list!
  if (el.kpiButtons) {
    el.kpiButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        const kpi = btn.dataset.ballotKpi;
        if (kpi === "eligible") {
          switchEditView("students");
          if (stuEl.stuStatusFilter) stuEl.stuStatusFilter.value = "";
          if (latestSnapshot) renderStudentsMasterTable(latestSnapshot);
        } else if (kpi === "remaining") {
          switchEditView("students");
          if (stuEl.stuStatusFilter) stuEl.stuStatusFilter.value = "not_voted";
          if (latestSnapshot) renderStudentsMasterTable(latestSnapshot);
        } else {
          switchEditView("ballots");
        }
      });
    });
  }

  // Check URL query parameters for default view
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get("view") === "students") {
    switchEditView("students");
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
      // Exclude duplicate 0000 teacher demo account so Aditya Vikram appears only once as 1C8492
      if (s.admissionNo === "0000") return;
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
    updateBadgeAddedCount();
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
      updateBadgeAddedCount();
        await refreshAll();
    });

    // Real-time auto-sync every 2 seconds
    setInterval(refreshAll, 2000);
  }

  boot();
})();
