/* Election Admin Console — Clean, Modular Production Controller */
(function () {
  "use strict";

  const electionId = window.ADMIN_DATA?.electionId || "elec_spr_2026";
  const positionId = window.ADMIN_DATA?.positionId || "Vote_Captain";
  const houses = window.ADMIN_DATA?.houses || [];
  const houseMap = {};
  houses.forEach((h) => {
    houseMap[h.code] = h;
  });

  let latestSnapshot = null;
  let activeKpi = null; // 'eligible' | 'accepted' | 'cancelled' | 'remaining' | null
  let pendingCancelBallotId = null;
  let pendingDeleteAdm = null;
  const prevAcceptedVoterSet = new Set();

  const el = {
    seedSupabaseBtn: document.getElementById("seed-supabase-btn"),
    freezeHousePollingBtn: document.getElementById("freeze-house-polling-btn"),
    freezeBtnIcon: document.getElementById("freeze-btn-icon"),
    freezeBtnText: document.getElementById("freeze-btn-text"),
    houseClosedBanner: document.getElementById("house-closed-banner"),
    refreshBtn: document.getElementById("refresh-btn"),
    printResultsBtn: document.getElementById("print-results-btn"),
    sbOfflineBanner: document.getElementById("sb-offline-banner"),
    sbOfflineMsg: document.getElementById("sb-offline-msg"),

    kpiEligible: document.getElementById("kpi-eligible"),
    kpiAccepted: document.getElementById("kpi-accepted"),
    kpiTurnout: document.getElementById("kpi-turnout"),
    kpiCancelled: document.getElementById("kpi-cancelled"),
    kpiRemaining: document.getElementById("kpi-remaining"),
    kpiButtons: Array.from(document.querySelectorAll("[data-kpi-filter]")),

    houseGrid: document.getElementById("admin-house-grid") || document.getElementById("house-grid"),

    drilldownPanel: document.getElementById("kpi-drilldown-panel"),
    drilldownTitle: document.getElementById("drilldown-title"),
    drilldownSubtitle: document.getElementById("drilldown-subtitle"),
    closeDrilldownBtn: document.getElementById("close-drilldown-btn"),
    drilldownSearch: document.getElementById("drilldown-search"),
    drilldownHouseFilter: document.getElementById("drilldown-house-filter"),
    drilldownBoothFilter: document.getElementById("drilldown-booth-filter"),
    drilldownClassFilter: document.getElementById("drilldown-class-filter"),
    drilldownSectionFilter: document.getElementById("drilldown-section-filter"),
    drilldownThead: document.getElementById("drilldown-thead"),
    drilldownTbody: document.getElementById("drilldown-tbody"),
    drilldownEmpty: document.getElementById("drilldown-empty"),

    cancelModal: document.getElementById("cancel-modal"),
    cancelModalDesc: document.getElementById("cancel-modal-desc"),
    cancelModalReason: document.getElementById("cancel-modal-reason"),
    cancelModalClose: document.getElementById("cancel-modal-close"),
    cancelErrorText: document.getElementById("cancel-error-text"),
    confirmCancelBtn: document.getElementById("confirm-cancel-btn"),

    deleteModal: document.getElementById("delete-modal"),
    deleteModalDesc: document.getElementById("delete-modal-desc"),
    deleteModalClose: document.getElementById("delete-modal-close"),
    deleteErrorText: document.getElementById("delete-error-text"),
    confirmDeleteBtn: document.getElementById("confirm-delete-btn"),

    photoModal: document.getElementById("photo-modal"),
    photoModalMeta: document.getElementById("photo-modal-meta"),
    photoModalImg: document.getElementById("photo-modal-img"),
    photoModalClose: document.getElementById("photo-modal-close"),

    sbModal: document.getElementById("supabase-modal"),
    sbUrlInput: document.getElementById("sb-url-input"),
    sbKeyInput: document.getElementById("sb-key-input"),
    sbModalError: document.getElementById("sb-modal-error"),
    sbModalClose: document.getElementById("sb-modal-close"),
    sbModalSave: document.getElementById("sb-modal-save"),
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

  function canonicalSection(s) {
    if (!s) return "";
    const str = String(s).trim().toUpperCase();
    if (str.includes("MAHA") || str.includes("PRATAP") || str.includes("10-MP") || str === "MRP") return "MRP";
    if (str.includes("SHIVAJI") || str.includes("10-CS") || str === "CS") return "CS";
    if (str.includes("ASHOKA") || str.includes("10-AC") || str === "AC") return "AC";
    if (str.includes("JHANSI") || str.includes("10-JL") || str === "JLB") return "JLB";
    if (str.includes("AMBEDKAR") || str.includes("DR BR")) return "AMBEDKAR";
    if (str.includes("LLR")) return "LLR";
    if (str.includes("BCP")) return "BCP";
    if (str.includes("BGT")) return "BGT";
    if (str === "VS" || str.includes("VS ") || str.includes("6-VS")) return "VS";
    if (str.includes("SITARAMA") || str.includes("ASR") || str.includes("7-AS")) return "ASR";
    if (str.includes("BHAGATH") || str.includes("7-BS") || str === "BS") return "BS";
    if (str.includes("CHANDRA SHEKAR") || str.includes("7-CA") || str === "CSA") return "CSA";
    if (str.includes("RAJGURU") || str.includes("7-RG") || str === "RG") return "RG";
    if (str.includes("SUBHASH") || str.includes("7-SB") || str === "SCB") return "SCB";
    if (str.includes("CHANAKYA") || str.includes("8-CH") || str === "CK") return "CK";
    if (str.includes("DAYANANDA") || str.includes("8-DS") || str === "DS") return "DS";
    if (str.includes("HEDGEWAR") || str.includes("8-HW") || str === "HG") return "HG";
    if (str.includes("GURUJI") || str.includes("8-SG") || str === "SG") return "SG";
    if (str.includes("VIVEKANANDA") || str.includes("8-SV") || str === "SV") return "SV";
    if (str.includes("KALAM") || str.includes("9-AK") || str === "APJ") return "APJ";
    if (str.includes("ARYABHATTA") || str.includes("9-AB") || str === "AB") return "AB";
    if (str.includes("CHAWLA") || str.includes("9-KC") || str === "KC") return "KC";
    if (str.includes("DHAWAN") || str.includes("9-SD") || str === "SD") return "SD";
    if (str.includes("SARABHAI") || str.includes("9-VS") || str === "VSB") return "VSB";
    return str;
  }

  function normSection(s) {
    return canonicalSection(s).toLowerCase();
  }

  function populateHouseFilter() {
    if (!el.drilldownHouseFilter) return;
    el.drilldownHouseFilter.innerHTML = '<option value="">All Houses</option>';
    houses.forEach((h) => {
      if (h.code === "ALL") return;
      const opt = document.createElement("option");
      opt.value = h.code;
      opt.textContent = h.code === "CENTRAL" ? "School Cabinet" : `${h.name} House`;
      el.drilldownHouseFilter.appendChild(opt);
    });
  }

  function populateClassAndSectionFilters(studentList) {
    if (!el.drilldownClassFilter || !el.drilldownSectionFilter) return;
    const students = studentList || window.ADMIN_DATA?.students || [];

    const rawClasses = Array.from(new Set(students.map((s) => String(s.className || "").trim()).filter(Boolean)));
    rawClasses.sort((a, b) => {
      const numA = parseInt(a, 10);
      const numB = parseInt(b, 10);
      if (!isNaN(numA) && !isNaN(numB)) return numB - numA;
      if (!isNaN(numA)) return -1;
      if (!isNaN(numB)) return 1;
      return a.localeCompare(b);
    });

    const curClass = el.drilldownClassFilter.value;
    el.drilldownClassFilter.innerHTML = '<option value="">All Classes</option>';
    rawClasses.forEach((cls) => {
      const opt = document.createElement("option");
      opt.value = cls;
      opt.textContent = cls.toLowerCase().startsWith("class") ? cls : `Class ${cls}`;
      el.drilldownClassFilter.appendChild(opt);
    });

    if (curClass && rawClasses.includes(curClass)) {
      el.drilldownClassFilter.value = curClass;
    }

    updateSectionFilterOptions(students);
  }

  function updateSectionFilterOptions(studentList) {
    if (!el.drilldownSectionFilter) return;
    const students = studentList || latestSnapshot?.students || window.ADMIN_DATA?.students || [];
    const selectedClass = el.drilldownClassFilter ? el.drilldownClassFilter.value.trim() : "";
    const currentSection = el.drilldownSectionFilter.value;

    const filteredStudents = selectedClass
      ? students.filter((s) => normClass(s.className) === normClass(selectedClass))
      : students;

    const rawSections = Array.from(new Set(filteredStudents.map((s) => canonicalSection(s.section)).filter(Boolean)));
    rawSections.sort((a, b) => a.localeCompare(b));

    el.drilldownSectionFilter.innerHTML = '<option value="">All Sections</option>';
    rawSections.forEach((sec) => {
      const opt = document.createElement("option");
      opt.value = sec;
      opt.textContent = sec;
      el.drilldownSectionFilter.appendChild(opt);
    });

    if (currentSection && rawSections.includes(canonicalSection(currentSection))) {
      el.drilldownSectionFilter.value = canonicalSection(currentSection);
    } else {
      el.drilldownSectionFilter.value = "";
    }
  }

  function formatTime(iso) {
    if (!iso) return "—";
    try {
      return new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
    } catch (_) {
      return iso;
    }
  }

  function makePhotoCell(ballotOrVoter) {
    const photoUrl = ballotOrVoter.photoDataUrl || (ballotOrVoter.ballots && ballotOrVoter.ballots.find((b) => b.photoDataUrl)?.photoDataUrl);
    if (!photoUrl) {
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
    img.src = photoUrl;
    img.alt = `Photo of ${ballotOrVoter.fullName || "Voter"}`;
    thumbBtn.appendChild(img);
    thumbBtn.addEventListener("click", () => openPhotoModal(ballotOrVoter));

    const viewBtn = document.createElement("button");
    viewBtn.type = "button";
    viewBtn.className = "btn btn-secondary";
    viewBtn.style.padding = "2px 7px";
    viewBtn.style.fontSize = "0.72rem";
    viewBtn.textContent = "View Photo";
    viewBtn.addEventListener("click", () => openPhotoModal(ballotOrVoter));

    wrap.appendChild(thumbBtn);
    wrap.appendChild(viewBtn);
    return wrap;
  }

  function openPhotoModal(ballotOrVoter) {
    const photoUrl = ballotOrVoter.photoDataUrl || (ballotOrVoter.ballots && ballotOrVoter.ballots.find((b) => b.photoDataUrl)?.photoDataUrl);
    const hName = formatHouseLabel(houseMap[ballotOrVoter.houseCode]?.name || ballotOrVoter.houseCode);
    el.photoModalMeta.textContent = `${ballotOrVoter.fullName} (ID ${ballotOrVoter.admissionNo}) · ${hName} · Recorded at ${formatTime(ballotOrVoter.castAt || ballotOrVoter.cancelledAt)}`;
    el.photoModalImg.src = photoUrl;
    el.photoModal.hidden = false;
  }

  function populateBoothFilter(snap) {
    if (!el.drilldownBoothFilter) return;
    const currentVal = el.drilldownBoothFilter.value;
    const booths = new Set();
    (snap?.ballots || []).forEach((b) => {
      const name = b.boothName || b.booth_name;
      if (name && String(name).trim()) booths.add(String(name).trim());
    });
    if (booths.size === 0) booths.add("Booth 1");
    el.drilldownBoothFilter.innerHTML = `<option value="">All Booths (${booths.size})</option>`;
    Array.from(booths).sort().forEach((b) => {
      const opt = document.createElement("option");
      opt.value = b;
      opt.textContent = `📍 ${b}`;
      if (b === currentVal) opt.selected = true;
      el.drilldownBoothFilter.appendChild(opt);
    });
  }

  function renderDrilldown(snap) {
    populateBoothFilter(snap);

    el.kpiButtons.forEach((b) => {
      b.classList.toggle("is-active", b.dataset.kpiFilter === activeKpi);
    });

    if (!activeKpi) {
      el.drilldownPanel.hidden = true;
      return;
    }

    el.drilldownPanel.hidden = false;
    const q = el.drilldownSearch.value.trim().toLowerCase();
    const hFilter = el.drilldownHouseFilter.value;
    const bFilter = el.drilldownBoothFilter ? el.drilldownBoothFilter.value.trim() : "";
    const cFilter = el.drilldownClassFilter ? el.drilldownClassFilter.value.trim() : "";
    const sFilter = el.drilldownSectionFilter ? el.drilldownSectionFilter.value.trim() : "";

    const positions = window.ADMIN_DATA?.positions || [{ id: positionId, title: "House Captain" }];
    const studentStatus = (stu) => {
      const states = positions.map((p) => snap.voterStatus[`${electionId}_${stu.admissionNo}_${p.id}`]?.status || "not_voted");
      if (states.every((s) => s === "voted")) return "voted";
      if (states.some((s) => s === "cancelled")) return "cancelled";
      if (states.some((s) => s === "voted")) return "partial";
      return "not_voted";
    };

    el.drilldownThead.innerHTML = "";
    el.drilldownTbody.innerHTML = "";

    if (activeKpi === "eligible" || activeKpi === "remaining") {
      const isRemaining = activeKpi === "remaining";
      el.drilldownTitle.textContent = isRemaining
        ? "Remaining Not Voted Students"
        : "Total Eligible Students (Master Register)";
      el.drilldownSubtitle.textContent = isRemaining
        ? "Eligible students who have not yet completed all leadership role votes."
        : "All active eligible students across the six houses.";

      el.drilldownThead.innerHTML = `
        <tr>
          <th>Voter ID</th>
          <th>Student</th>
          <th>Class</th>
          <th>Sec</th>
          <th>House</th>
          <th>Role</th>
          <th>Status</th>
        </tr>
      `;

      const rows = snap.students
        .filter((s) => s.isActive)
        .filter((s) => {
          if (hFilter && s.houseCode !== hFilter) return false;
          if (cFilter && normClass(s.className) !== normClass(cFilter)) return false;
          if (sFilter && normSection(s.section) !== normSection(sFilter)) return false;
          if (isRemaining && studentStatus(s) === "voted") return false;
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

      el.drilldownEmpty.hidden = rows.length > 0;
      rows.forEach((s) => {
        const house = houseMap[s.houseCode] || { name: s.houseCode, accentText: "#141413" };
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
          <td><strong style="color:${house.accentText};">${formatHouseLabel(house.name)}</strong></td>
          <td>${s.isCandidate ? s.positionName || "Candidate" : (s.isStaff ? "Faculty" : "Voter")}</td>
          <td>${badge}</td>
        `;
        const vId = getDisplayVoterId(s);
        if (vId === "--") {
          tr.children[0].innerHTML = '<span style="color:var(--text-muted); font-weight:700;">--</span>';
        } else {
          tr.children[0].innerHTML = `<strong class="mono" style="color:#0369a1; font-weight:800; font-size:1.02rem;">${vId}</strong>`;
        }
        tr.children[1].querySelector("strong").textContent = s.fullName;
        const clsLabel = s.className ? (s.className.toString().toLowerCase().startsWith("class") ? s.className : `Class ${s.className}`) : "--";
        tr.children[2].querySelector(".mono").textContent = clsLabel;
        tr.children[3].textContent = canonicalSection(s.section) || "--";
        el.drilldownTbody.appendChild(tr);
      });
      return;
    }

    if (activeKpi === "accepted") {
      el.drilldownTitle.textContent = "Active Accepted Voters";
      el.drilldownSubtitle.textContent = "All students who have submitted active votes across booths. Reviewing photos, cast times, or resetting ballots is managed inside Edit Votes.";

      el.drilldownThead.innerHTML = `
        <tr>
          <th>Voter ID</th>
          <th>Student</th>
          <th>Class</th>
          <th>Sec</th>
          <th>House</th>
          <th>Booth</th>
          <th>Status</th>
          <th>Action</th>
        </tr>
      `;

      const acceptedBallots = snap.ballots.filter((b) => b.status === "accepted");
      const acceptedAdmSet = new Set(acceptedBallots.map((b) => b.admissionNo));
      const admBoothMap = new Map();
      acceptedBallots.forEach((b) => {
        if (!admBoothMap.has(b.admissionNo)) {
          admBoothMap.set(b.admissionNo, b.boothName || b.booth_name || "Booth 1");
        }
      });

      const rows = snap.students
        .filter((s) => s.isActive && acceptedAdmSet.has(s.admissionNo))
        .filter((s) => {
          if (hFilter && s.houseCode !== hFilter) return false;
          if (cFilter && normClass(s.className) !== normClass(cFilter)) return false;
          if (sFilter && normSection(s.section) !== normSection(sFilter)) return false;
          const stuBooth = admBoothMap.get(s.admissionNo) || "Booth 1";
          if (bFilter && stuBooth !== bFilter) return false;
          if (q) {
            const hay = `${s.admissionNo} ${s.fullName} ${s.className}-${s.section} ${stuBooth}`.toLowerCase();
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

      el.drilldownEmpty.hidden = rows.length > 0;
      rows.forEach((s) => {
        const house = houseMap[s.houseCode] || { name: s.houseCode, accentText: "#141413" };
        const st = studentStatus(s);
        const stuBooth = admBoothMap.get(s.admissionNo) || "Booth 1";
        const badge =
          st === "voted"
            ? `<span class="badge badge-success">Voted (4/4)</span>`
            : `<span class="badge badge-warning">Partial Vote</span>`;

        const tr = document.createElement("tr");
        if (prevAcceptedVoterSet.size > 0 && !prevAcceptedVoterSet.has(s.admissionNo)) {
          tr.style.animation = "rowHighlightFlash 2.2s ease-out";
        }

        tr.innerHTML = `
          <td class="mono"></td>
          <td><strong></strong></td>
          <td><span class="mono"></span></td>
          <td></td>
          <td><strong style="color:${house.accentText};">${formatHouseLabel(house.name)}</strong></td>
          <td><span class="badge" style="background:rgba(5,150,105,0.12); color:#047857; font-weight:700; border:1px solid rgba(5,150,105,0.25);">📍 ${stuBooth}</span></td>
          <td>${badge}</td>
          <td>
            <a href="./edit-votes.html?adm=${encodeURIComponent(s.admissionNo)}" class="btn btn-secondary" style="font-size:0.75rem; padding:0.25rem 0.55rem; min-height:auto;">Edit Ballots →</a>
          </td>
        `;
        const vId = getDisplayVoterId(s);
        if (vId === "--") {
          tr.children[0].innerHTML = '<span style="color:var(--text-muted); font-weight:700;">--</span>';
        } else {
          tr.children[0].innerHTML = `<strong class="mono" style="color:#0369a1; font-weight:800; font-size:1.02rem;">${vId}</strong>`;
        }
        tr.children[1].querySelector("strong").textContent = s.fullName;
        const clsLabel = s.className ? (s.className.toString().toLowerCase().startsWith("class") ? s.className : `Class ${s.className}`) : "--";
        tr.children[2].querySelector(".mono").textContent = clsLabel;
        tr.children[3].textContent = canonicalSection(s.section) || "--";
        el.drilldownTbody.appendChild(tr);
      });

      // Update prevAcceptedVoterSet
      acceptedAdmSet.forEach((adm) => prevAcceptedVoterSet.add(adm));
      return;
    }

    if (activeKpi === "cancelled") {
      el.drilldownTitle.textContent = "Cancelled Ballots";
      el.drilldownSubtitle.textContent = "Students whose vote was cancelled (excluded from results; student can re-vote).";

      el.drilldownThead.innerHTML = `
        <tr>
          <th>Voter ID</th>
          <th>Student</th>
          <th>House</th>
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
      (snap.ballots || []).forEach((b) => {
        if (b.status !== "cancelled") return;
        if (!cancelledVoterMap.has(b.admissionNo)) {
          cancelledVoterMap.set(b.admissionNo, {
            admissionNo: b.admissionNo,
            fullName: b.fullName || b.admissionNo,
            className: b.className || "",
            section: b.section || "",
            houseCode: b.houseCode || "",
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
        if (hFilter && v.houseCode !== hFilter) return false;
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
        const house = houseMap[v.houseCode] || { name: v.houseCode, accentText: "#141413" };
        const sKey = `${electionId}_${v.admissionNo}_${v.ballots[0]?.positionId || positionId}`;
        const curStatus = snap.voterStatus[sKey]?.status || "cancelled";
        const curBadge =
          curStatus === "voted"
            ? `<span class="badge badge-success">Re-voted</span>`
            : `<span class="badge badge-warning">Pending Re-vote</span>`;
        const canceller = v.cancelledBy || "rc4616105@gmail.com";
        const roleCount = v.ballots.length || (v.houseCode === "CENTRAL" ? 5 : 4);

        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td class="mono"></td>
          <td><strong></strong><div class="stat-note"></div></td>
          <td><strong style="color:${house.accentText};">${formatHouseLabel(house.name)}</strong></td>
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
        const vId = getDisplayVoterId(v);
        if (vId === "--") {
          tr.children[0].innerHTML = '<span style="color:var(--text-muted); font-weight:700;">--</span>';
        } else {
          tr.children[0].innerHTML = `<strong class="mono" style="color:#0369a1; font-weight:800; font-size:1.02rem;">${vId}</strong>`;
        }
        tr.children[1].querySelector("strong").textContent = v.fullName;
        const clsSecLabel = v.className ? `Class ${v.className}-${v.section || "--"}` : (v.section || "--");
        tr.children[1].querySelector(".stat-note").textContent = clsSecLabel;
        tr.children[4].appendChild(makePhotoCell(v));
        tr.children[6].textContent = formatTime(v.cancelledAt);
        el.drilldownTbody.appendChild(tr);
      });
      return;
    }
  }

  function renderOverview(snap) {
    const eligible = snap.students.filter((s) => s.isActive).length;
    const acceptedBallotsAll = snap.ballots.filter((b) => b.status === "accepted");
    const votedVotersCount = new Set(acceptedBallotsAll.map((b) => b.admissionNo)).size;
    const cancelledBallotsAll = snap.ballots.filter((b) => b.status === "cancelled");
    const cancelledVotersCount = new Set(cancelledBallotsAll.map((b) => b.admissionNo)).size;
    const pct = eligible ? Math.round((votedVotersCount / eligible) * 100) : 0;

    el.kpiEligible.textContent = String(eligible);
    el.kpiAccepted.textContent = String(votedVotersCount);
    el.kpiTurnout.textContent = `${pct}% turnout · ${acceptedBallotsAll.length} role ballots →`;
    el.kpiCancelled.textContent = String(cancelledVotersCount);
    el.kpiRemaining.textContent = String(Math.max(0, eligible - votedVotersCount));

    if (el.houseGrid) {
      el.houseGrid.innerHTML = "";
    }
    const centralPosIds = new Set([
      "Vote_President", "Vote_Vice_President", "Vote_Literary_Sec", "Vote_Sports_Sec", "Vote_Social_Cultural_Sec",
      "PRESIDENT", "VICE_PRESIDENT", "LITERARY_SECRETARY", "SPORTS_SECRETARY", "SOCIAL_CULTURAL_SECRETARY",
      "Vote_Central_10_President", "Vote_Central_9_VicePresident", "Vote_Central_9_LiterarySec", "Vote_Central_9_SportsSec", "Vote_Central_9_CulturalSec"
    ]);

    houses.forEach((h) => {
      if (h.code === "ALL" || h.slug === "all") return;
      const isCentral = h.code === "CENTRAL" || h.slug === "central";
      const totalInHouse = isCentral
        ? snap.students.filter((s) => (s.isStaff || s.houseCode === "ALL") && s.isActive).length
        : snap.students.filter((s) => s.houseCode === h.code && s.isActive).length;

      const acceptedBallots = snap.ballots.filter((b) =>
        (b.houseCode === h.code || (isCentral && (b.houseCode === "CENTRAL" || centralPosIds.has(b.positionId)))) &&
        b.status === "accepted"
      );
      const houseVotersCount = new Set(acceptedBallots.map((b) => b.admissionNo)).size;
      const cancelledBallotsForHouse = snap.ballots.filter((b) =>
        (b.houseCode === h.code || (isCentral && (b.houseCode === "CENTRAL" || centralPosIds.has(b.positionId)))) &&
        b.status === "cancelled"
      );
      const cancelledCount = new Set(cancelledBallotsForHouse.map((b) => b.admissionNo)).size;
      const hPct = totalInHouse ? Math.round((houseVotersCount / totalInHouse) * 100) : 0;

      let cands = snap.candidates.filter((c) => c.houseCode === h.code && c.isApproved);
      if (cands.length === 0) {
        cands = (window.ADMIN_DATA.candidates || []).filter((c) => c.houseCode === h.code);
      }

      const card = document.createElement("a");
      card.href = `./house.html?house=${h.slug}`;
      card.className = "admin-house-card";
      card.style.setProperty("--card-accent", h.accent);
      card.style.setProperty("--card-ink", h.accentText);

      if (isCentral) {
        card.style.background = "linear-gradient(135deg, var(--bg-card) 0%, #ecfdf5 100%)";
        card.style.borderColor = "#a7f3d0";
      }

      card.innerHTML = `
        <div class="admin-house-top">
          <h3 class="admin-house-title">${formatHouseLabel(h.name)}</h3>
          <span class="admin-house-count">${houseVotersCount} / ${totalInHouse} voted</span>
        </div>
        <div class="house-bar-track">
          <div class="house-bar-fill" style="width:${hPct}%; background:${h.accent};"></div>
        </div>
        <div class="admin-house-meta">
          <span>${cands.length} candidates · ${isCentral ? "Teachers Only" : `${cancelledCount} cancelled`}</span>
          <span class="admin-house-cta">Graphs &amp; Voters →</span>
        </div>
      `;
      if (el.houseGrid) el.houseGrid.appendChild(card);
    });

    // Tool Card 1: All Election Results (Navigates to dedicated screen)
    const resultsCard = document.createElement("a");
    resultsCard.href = "./results.html";
    resultsCard.className = "admin-house-card admin-tool-card admin-tool-results";
    resultsCard.style.setProperty("--card-accent", "#d97706");
    resultsCard.style.setProperty("--card-ink", "#92400e");
    resultsCard.innerHTML = `
      <div class="admin-house-top">
        <h3 class="admin-house-title" style="color: #92400e;">🏆 All Election Results</h3>
        <span class="badge badge-gold" style="font-size:0.75rem;">Live Tally</span>
      </div>
      <div class="house-bar-track">
        <div class="house-bar-fill" style="width:100%; background:#d97706;"></div>
      </div>
      <div class="admin-house-meta">
        <span>29 posts · Post winners &amp; table</span>
        <span class="admin-house-cta" style="color: #92400e;">View Results →</span>
      </div>
    `;
    if (el.houseGrid) el.houseGrid.appendChild(resultsCard);

    // Tool Card 2: Edit & Manage Votes (Navigates to dedicated screen)
    const editorCard = document.createElement("a");
    editorCard.href = "./edit-votes.html";
    editorCard.className = "admin-house-card admin-tool-card admin-tool-editor";
    editorCard.style.setProperty("--card-accent", "#4f46e5");
    editorCard.style.setProperty("--card-ink", "#4338ca");
    editorCard.innerHTML = `
      <div class="admin-house-top">
        <h3 class="admin-house-title" style="color: #4338ca;">✏️ Edit &amp; Manage Votes</h3>
        <span class="badge" style="background:#eef2ff; color:#4338ca; border:1px solid #c7d2fe; font-size:0.75rem;">Ballot Control</span>
      </div>
      <div class="house-bar-track">
        <div class="house-bar-fill" style="width:100%; background:#4f46e5;"></div>
      </div>
      <div class="admin-house-meta">
        <span>Inspect photos · Cancel votes · Reset</span>
        <span class="admin-house-cta" style="color: #4338ca;">Open Editor →</span>
      </div>
    `;
    if (el.houseGrid) el.houseGrid.appendChild(editorCard);

    // Tool Card 3: Live Voters Stream & Activity Feed
    const liveVotersCard = document.createElement("a");
    liveVotersCard.href = "./live-voters/index.html";
    liveVotersCard.className = "admin-house-card admin-tool-card";
    liveVotersCard.style.setProperty("--card-accent", "#059669");
    liveVotersCard.style.setProperty("--card-ink", "#047857");
    liveVotersCard.innerHTML = `
      <div class="admin-house-top">
        <h3 class="admin-house-title" style="color: #047857;">⚡ Live Voters Stream</h3>
        <span class="badge" style="background:#ecfdf5; color:#047857; border:1px solid #a7f3d0; font-size:0.75rem;"><span class="pulse-dot" style="display:inline-block; vertical-align:middle; margin-right:3px;"></span> Live Feed</span>
      </div>
      <div class="house-bar-track">
        <div class="house-bar-fill" style="width:100%; background:linear-gradient(90deg, #10b981, #059669);"></div>
      </div>
      <div class="admin-house-meta">
        <span>Real-time incoming check-ins · Photos · Sound</span>
        <span class="admin-house-cta" style="color: #047857;">Open Live Feed →</span>
      </div>
    `;
    if (el.houseGrid) el.houseGrid.appendChild(liveVotersCard);

    renderDrilldown(snap);
  }

  function openCancelModal(ballot) {
    pendingCancelBallotId = ballot.id;
    el.cancelModalDesc.textContent = `Cancel vote for ${ballot.fullName} (ID ${ballot.admissionNo})? The record stays in cancelled history and the student can cast a new vote.`;
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

  let isRefreshing = false;
  async function refreshAll() {
    if (isRefreshing) return;
    isRefreshing = true;
    try {
      latestSnapshot = await window.AdminBackend.getSnapshot();
      renderOverview(latestSnapshot);
    updateFreezeButtonState();
    if (typeof BroadcastChannel !== "undefined") {
      try {
        const chan = new BroadcastChannel("election_spr_2026_sync");
        chan.addEventListener("message", (e) => {
          if (e.data && (e.data.type === "house_polling_closed" || e.data.type === "house_polling_opened")) {
            updateFreezeButtonState();
          }
        });
      } catch (_) {}
    }
    } catch (err) {
      console.warn("Unable to load election snapshot:", err);
      const sub = document.querySelector(".page-sub");
      if (sub && window.AdminBackend.backendError) {
        sub.textContent = `Supabase error: ${err.message || window.AdminBackend.backendError}`;
      }
    } finally {
      isRefreshing = false;
    }
  }

  el.kpiButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const target = btn.dataset.kpiFilter;
      activeKpi = activeKpi === target ? null : target;
      if (latestSnapshot) renderDrilldown(latestSnapshot);
    });
  });

  el.closeDrilldownBtn.addEventListener("click", () => {
    activeKpi = null;
    if (latestSnapshot) renderDrilldown(latestSnapshot);
  });

  if (el.drilldownSearch) {
    el.drilldownSearch.addEventListener("input", () => {
      if (latestSnapshot) renderDrilldown(latestSnapshot);
    });
  }

  if (el.drilldownHouseFilter) {
    el.drilldownHouseFilter.addEventListener("change", () => {
      if (latestSnapshot) renderDrilldown(latestSnapshot);
    });
  }

  if (el.drilldownBoothFilter) {
    el.drilldownBoothFilter.addEventListener("change", () => {
      if (latestSnapshot) renderDrilldown(latestSnapshot);
    });
  }

  if (el.drilldownClassFilter) {
    el.drilldownClassFilter.addEventListener("change", () => {
      updateSectionFilterOptions();
      if (latestSnapshot) renderDrilldown(latestSnapshot);
    });
  }

  if (el.drilldownSectionFilter) {
    el.drilldownSectionFilter.addEventListener("change", () => {
      if (latestSnapshot) renderDrilldown(latestSnapshot);
    });
  }

  if (el.refreshBtn) el.refreshBtn.addEventListener("click", refreshAll);

  function openSupabaseModal(msg) {
    el.sbUrlInput.value = window.AdminBackend?.getDefaultUrl ? window.AdminBackend.getDefaultUrl() : "https://rziptxcknaeuorekxwrl.supabase.co";
    let savedKey = "";
    try {
      const saved = JSON.parse(localStorage.getItem("election_spr_2026_sb_cfg_v1") || "null");
      if (saved && saved.anonKey) savedKey = saved.anonKey;
    } catch (_) {}
    if (!savedKey && typeof window.AdminBackend?.getKey === "function") {
      savedKey = window.AdminBackend.getKey();
    }
    el.sbKeyInput.value = savedKey;
    if (msg) {
      el.sbModalError.textContent = msg;
      el.sbModalError.hidden = false;
    } else {
      el.sbModalError.hidden = true;
    }
    el.sbModal.hidden = false;
    if (!savedKey) {
      el.sbKeyInput.focus();
    }
  }

  el.seedSupabaseBtn.addEventListener("click", async () => {
    try {
      el.seedSupabaseBtn.disabled = true;
      let mode = window.AdminBackend?.mode || "offline";
      if (mode !== "supabase") {
        mode = (window.AdminBackend && typeof window.AdminBackend.init === "function")
          ? await window.AdminBackend.init()
          : "offline";
      }
      if (mode !== "supabase") {
        openSupabaseModal(window.AdminBackend?.backendError || "Supabase not connected.");
        return;
      }
      const res = await window.AdminBackend.syncRosterToSupabase();
      await refreshAll();
      alert(`Synced ${res.totalVoters} students (${res.insertedVoters} newly added) and ${res.candidates} candidates into Supabase.`);
    } catch (err) {
      if (err.message && err.message.includes("voters_house_code_check")) {
        alert("⚠️ Supabase Schema Update Required:\n\nYour Supabase database table 'voters' has an older check constraint that doesn't permit 'ALL' (for the 87 Teachers) or 'BHEESHMA'.\n\nFix: Open Supabase Dashboard -> SQL Editor and run FIX_SUPABASE_CONSTRAINT.sql, then click 'Sync Roster to Supabase' again.");
      } else {
        alert(err.message);
      }
    } finally {
      el.seedSupabaseBtn.disabled = false;
    }
  });

  // Two-Stage Electoral Lifecycle: Pause/Resume House Polling & Tally 24 House Winners
  function updateFreezeButtonState() {
    if (!el.freezeHousePollingBtn) return;
    const isClosed = localStorage.getItem("ELECTION_HOUSE_POLLING_CLOSED") === "true";
    if (isClosed) {
      if (el.freezeBtnIcon) el.freezeBtnIcon.textContent = "▶️";
      if (el.freezeBtnText) el.freezeBtnText.textContent = "Resume House Polling";
      el.freezeHousePollingBtn.title = "Click to resume house voting for students";
      el.freezeHousePollingBtn.style.background = "#dcfce7";
      el.freezeHousePollingBtn.style.color = "#15803d";
      el.freezeHousePollingBtn.style.borderColor = "#22c55e";
      el.freezeHousePollingBtn.style.fontWeight = "700";
      if (el.houseClosedBanner) el.houseClosedBanner.hidden = false;
    } else {
      if (el.freezeBtnIcon) el.freezeBtnIcon.textContent = "⏸️";
      if (el.freezeBtnText) el.freezeBtnText.textContent = "Pause House Polling & Tally";
      el.freezeHousePollingBtn.title = "Pause house voting kiosks, tally 24 winners, and unlock School Cabinet";
      el.freezeHousePollingBtn.style.background = "";
      el.freezeHousePollingBtn.style.color = "";
      el.freezeHousePollingBtn.style.borderColor = "";
      el.freezeHousePollingBtn.style.fontWeight = "";
      if (el.houseClosedBanner) el.houseClosedBanner.hidden = true;
    }
  }

  async function tallyAndLockHouseWinners() {
    const { houses, positions, candidates } = window.ADMIN_DATA;
    const houseList = houses.filter((h) => h.code !== "CENTRAL");
    const roleList = positions.filter((p) => p.id !== "CENTRAL" && !p.id.startsWith("HEAD_") && p.id !== "SPORTS_CAPTAIN");

    let ballots = [];
    try {
      const snap = await window.AdminBackend.getSnapshot();
      ballots = snap.ballots || [];
    } catch (_) {}

    const acceptedBallots = (ballots || []).filter((b) => b.status === "accepted");
    const twentyFourWinners = [];
    const customTemplateHouses = [];

    houseList.forEach((house) => {
      const houseCodeUpper = String(house.code).toUpperCase().trim();
      const houseBallots = acceptedBallots.filter(
        (b) => String(b.house_code || "").toUpperCase().trim() === houseCodeUpper
      );
      const houseCandidates = candidates.filter(
        (c) => String(c.houseCode || "").toUpperCase().trim() === houseCodeUpper
      );

      const houseCustomCandidates = {};

      roleList.forEach((roleDef) => {
        const roleCands = houseCandidates.filter(
          (c) => c.positionId === roleDef.id || c.positionId === roleDef.code
        );

        const candsWithVotes = roleCands.map((c) => {
          const votes = houseBallots.filter(
            (b) => b.candidate_id === c.id || (b.candidate_name && c.fullName && b.candidate_name.trim().toLowerCase() === c.fullName.trim().toLowerCase())
          ).length;
          return {
            ...c,
            votes
          };
        });

        candsWithVotes.sort((a, b) => b.votes - a.votes || (a.fullName || "").localeCompare(b.fullName || ""));

        const winner = candsWithVotes[0] || roleCands[0];
        if (winner) {
          const winnerObj = {
            admissionNo: winner.admissionNo || winner.id || "",
            fullName: winner.fullName || "",
            name: winner.fullName || "",
            postTitle: roleDef.title || roleDef.name || "House Leader",
            role: roleDef.title || roleDef.name || "House Leader",
            roleKey: roleDef.id,
            houseCode: house.code,
            houseName: house.name,
            house: house.name,
            votes: winner.votes || 0,
            className: winner.className || "10",
            section: winner.section || "",
            photoUrl: winner.photoUrl || winner.photoPath || "",
            symbolName: winner.symbolObj?.name || "",
            symbolIcon: winner.symbolObj?.icon || "⭐"
          };
          twentyFourWinners.push(winnerObj);

          const roleKey = roleDef.id === "CAPTAIN_BOY" ? "boys_captain"
            : roleDef.id === "CAPTAIN_GIRL" ? "girls_captain"
            : roleDef.id === "VICE_CAPTAIN_BOY" ? "boys_vc"
            : "girls_vc";

          houseCustomCandidates[roleKey] = {
            name: winner.fullName,
            grade: winner.className ? `Grade ${winner.className}` : "Grade 10",
            section: winner.section || "",
            photo: winner.photoUrl || winner.photoPath || "",
            symbol: winner.symbolObj?.name || "",
            symbolIcon: winner.symbolObj?.icon || "⭐",
            symbolImage: winner.symbolObj?.image || "",
            votes: winner.votes || 0,
            totalVotes: houseBallots.length,
            percentage: houseBallots.length > 0 ? Math.round((winner.votes / houseBallots.length) * 100) : 0,
            tagline: winner.tagline || ""
          };
        }
      });

      customTemplateHouses.push({
        id: house.slug || house.code.toLowerCase(),
        name: house.name,
        fullName: `${house.name} House`,
        color: house.accent,
        colorDark: house.accentText,
        theme: house.slug || house.code.toLowerCase(),
        candidates: houseCustomCandidates
      });
    });

    localStorage.setItem("ELECTED_HOUSE_WINNERS_2026", JSON.stringify(twentyFourWinners));
    localStorage.setItem("SCHOOL_ELECTION_2026_CUSTOM_DATA_V5", JSON.stringify(customTemplateHouses));
    localStorage.setItem("ELECTION_HOUSE_POLLING_CLOSED", "true");

    if (typeof BroadcastChannel !== "undefined") {
      try {
        const chan = new BroadcastChannel("election_spr_2026_sync");
        chan.postMessage({ type: "house_polling_closed", winnersCount: twentyFourWinners.length, at: Date.now() });
      } catch (_) {}
    }

    return twentyFourWinners;
  }

  if (el.freezeHousePollingBtn) {
    el.freezeHousePollingBtn.addEventListener("click", async () => {
      const isCurrentlyClosed = localStorage.getItem("ELECTION_HOUSE_POLLING_CLOSED") === "true";
      if (!isCurrentlyClosed) {
        const confirmed = confirm(
          "⏸️ PAUSE HOUSE POLLING & TALLY WINNERS?\n\nThis will:\n1. Pause the 6 student house voting booths.\n2. Automatically tally the votes across all houses.\n3. Lock the 24 elected House Captains & Vice Captains.\n4. Authorize the 24 winners to vote inside the School Cabinet booth.\n5. Load the winners into the Scratch Card Ceremony.\n\n(You can resume house polling anytime by clicking 'Resume House Polling'.)\n\nProceed to pause house polling?"
        );
        if (!confirmed) return;

        try {
          el.freezeHousePollingBtn.disabled = true;
          const winners = await tallyAndLockHouseWinners();
          updateFreezeButtonState();
          alert(
            `⏸️ House Polling Paused!\n\n• Successfully tallied and locked ${winners.length} House Captains & Vice Captains.\n• The 6 House Booths are now paused.\n• The 24 winners are now authorized to vote in the School Cabinet booth!\n• The Scratch Card & Houses Wheel ceremony is ready to reveal them.\n\n(The button has now switched to '▶️ Resume House Polling' if you ever need to resume).`
          );
        } catch (err) {
          alert(`Error pausing house polling: ${err.message}`);
        } finally {
          el.freezeHousePollingBtn.disabled = false;
        }
      } else {
        const confirmed = confirm(
          "▶️ RESUME HOUSE POLLING?\n\nThis will re-open the 6 House Booths and allow students to resume voting.\n\nProceed to resume?"
        );
        if (!confirmed) return;

        localStorage.removeItem("ELECTION_HOUSE_POLLING_CLOSED");
        if (typeof BroadcastChannel !== "undefined") {
          try {
            const chan = new BroadcastChannel("election_spr_2026_sync");
            chan.postMessage({ type: "house_polling_opened", at: Date.now() });
          } catch (_) {}
        }
        updateFreezeButtonState();
        alert("▶️ House Polling Resumed! Students can now vote in all 6 House Booths.");
      }
    });
  }

  el.sbModalClose.addEventListener("click", () => {
    el.sbModal.hidden = true;
  });

  el.sbModalSave.addEventListener("click", async () => {
    try {
      el.sbModalSave.disabled = true;
      el.sbModalError.hidden = true;
      await window.AdminBackend.configureBrowserKey(el.sbUrlInput.value, el.sbKeyInput.value);
      el.seedSupabaseBtn.textContent = "Sync Roster to Supabase";
      el.seedSupabaseBtn.title = "Connected to Supabase";
      if (el.sbOfflineBanner) el.sbOfflineBanner.hidden = true;
      const res = await window.AdminBackend.syncRosterToSupabase();
      el.sbModal.hidden = true;
      await refreshAll();
      alert(`Connected & synced ${res.totalVoters} students (${res.insertedVoters} newly added) and ${res.candidates} candidates into Supabase.`);
    } catch (err) {
      if (err.message && err.message.includes("voters_house_code_check")) {
        el.sbModalError.textContent = "Supabase check constraint error: please run FIX_SUPABASE_CONSTRAINT.sql in your Supabase SQL Editor.";
      } else {
        el.sbModalError.textContent = err.message || "Unable to connect to Supabase.";
      }
      el.sbModalError.hidden = false;
    } finally {
      el.sbModalSave.disabled = false;
    }
  });

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

  if (el.printResultsBtn) {
    el.printResultsBtn.addEventListener("click", async () => {
      if (typeof window.exportElectionResultsToExcel === "function") {
        await window.exportElectionResultsToExcel(latestSnapshot);
      } else {
        window.print();
      }
    });
  }

  async function boot() {
    try {
      localStorage.removeItem("spr_admin_snapshot_cache");
    } catch (_) {}
    populateHouseFilter();
    populateClassAndSectionFilters();
    // Always paint initial roster KPIs & house cards immediately before awaiting network
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
    renderOverview(latestSnapshot);
    updateFreezeButtonState();
    if (typeof BroadcastChannel !== "undefined") {
      try {
        const chan = new BroadcastChannel("election_spr_2026_sync");
        chan.addEventListener("message", (e) => {
          if (e.data && (e.data.type === "house_polling_closed" || e.data.type === "house_polling_opened")) {
            updateFreezeButtonState();
          }
        });
      } catch (_) {}
    }

    const mode = (window.AdminBackend && typeof window.AdminBackend.init === "function")
      ? await window.AdminBackend.init()
      : "offline";
    if (mode === "supabase") {
      el.seedSupabaseBtn.hidden = false;
      el.seedSupabaseBtn.textContent = "Sync Roster to Supabase";
      el.seedSupabaseBtn.title = "Connected to Supabase";
      if (el.sbOfflineBanner) el.sbOfflineBanner.hidden = true;
    } else {
      el.seedSupabaseBtn.hidden = false;
      el.seedSupabaseBtn.textContent = "Connect & Sync Supabase";
      el.seedSupabaseBtn.title = window.AdminBackend?.backendError || "Supabase not connected — click to paste your Publishable key";
      if (el.sbOfflineBanner) {
        el.sbOfflineBanner.hidden = false;
        if (el.sbOfflineMsg && window.AdminBackend?.backendError) {
          el.sbOfflineMsg.textContent = `${window.AdminBackend.backendError} Click Connect & Sync Supabase above.`;
        }
      }
    }
    await refreshAll();
    if (window.AdminBackend?.subscribeUpdates) {
      window.AdminBackend.subscribeUpdates(async () => {
        await refreshAll();
      });
    }

    // Guaranteed real-time auto-sync every 2 seconds without manual refresh
    setInterval(refreshAll, 2000);
  }

  boot();
})();
