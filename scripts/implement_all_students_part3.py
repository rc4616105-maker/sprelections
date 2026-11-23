import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ev_js_path = ROOT / "Houses" / "admin" / "edit-votes.js"
code = ev_js_path.read_text(encoding="utf-8")

# Let's inspect where to attach view switching and students master table logic
STUDENTS_MASTER_LOGIC = '''
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

  function switchEditView(viewName) {
    const isStudents = viewName === "students";
    if (stuEl.navBtnBallots) stuEl.navBtnBallots.classList.toggle("is-active", !isStudents);
    if (stuEl.navBtnStudents) stuEl.navBtnStudents.classList.toggle("is-active", isStudents);
    if (stuEl.viewBallots) stuEl.viewBallots.hidden = isStudents;
    if (stuEl.viewStudents) stuEl.viewStudents.hidden = !isStudents;

    if (isStudents && latestSnapshot) {
      renderStudentsMasterTable(latestSnapshot);
      if (stuEl.viewStudents) {
        stuEl.viewStudents.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    } else if (!isStudents && latestSnapshot) {
      renderBallotsTable(latestSnapshot);
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
      if (latestSnapshot) renderStudentsMasterTable(latestSnapshot);
    });
  }

  // House Filter Pills
  stuEl.houseFilterPills.forEach((pill) => {
    pill.addEventListener("click", () => {
      stuEl.houseFilterPills.forEach((p) => p.classList.remove("is-active"));
      pill.classList.add("is-active");
      activeStudentHouseFilter = pill.dataset.house || "";
      if (stuEl.stuHouseFilter) stuEl.stuHouseFilter.value = activeStudentHouseFilter;
      if (latestSnapshot) renderStudentsMasterTable(latestSnapshot);
    });
  });

  if (stuEl.stuHouseFilter) {
    stuEl.stuHouseFilter.addEventListener("change", () => {
      activeStudentHouseFilter = stuEl.stuHouseFilter.value;
      stuEl.houseFilterPills.forEach((p) => {
        p.classList.toggle("is-active", (p.dataset.house || "") === activeStudentHouseFilter);
      });
      if (latestSnapshot) renderStudentsMasterTable(latestSnapshot);
    });
  }

  if (stuEl.stuSearch) {
    stuEl.stuSearch.addEventListener("input", () => {
      if (latestSnapshot) renderStudentsMasterTable(latestSnapshot);
    });
  }
  if (stuEl.stuSectionFilter) {
    stuEl.stuSectionFilter.addEventListener("change", () => {
      if (latestSnapshot) renderStudentsMasterTable(latestSnapshot);
    });
  }
  if (stuEl.stuStatusFilter) {
    stuEl.stuStatusFilter.addEventListener("change", () => {
      if (latestSnapshot) renderStudentsMasterTable(latestSnapshot);
    });
  }

  // Render All Students Master Register Table
  function renderStudentsMasterTable(snap) {
    if (!stuEl.stuTbody) return;

    // Gather complete students list (base + overrides + custom)
    const customList = getCustomStudentsList();
    const customMap = new Map(customList.map((cs) => [String(cs.admissionNo).toUpperCase(), cs]));
    const acceptedAdmSet = new Set((snap.ballots || []).filter((b) => b.status === "accepted").map((b) => String(b.admissionNo).toUpperCase()));

    const allStudentsMap = new Map();

    // 1. Base students from snapshot
    (snap.students || []).forEach((s) => {
      if (s && s.admissionNo) {
        // Exclude duplicate 0000 demo teacher account
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
        const hay = `${vId !== "--" ? vId : ""} ${s.admissionNo} ${s.fullName} ${s.fatherName || ""} ${s.className}-${s.section} ${s.houseCode}`.toLowerCase();
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

    stuEl.stuTbody.innerHTML = "";
    if (stuEl.stuEmpty) {
      stuEl.stuEmpty.hidden = filtered.length > 0;
    }

    filtered.forEach((s) => {
      const sAdmUp = String(s.admissionNo).toUpperCase();
      const vId = getDisplayVoterId(s);
      const hasVoted = acceptedAdmSet.has(sAdmUp);
      const isCustom = s.isCustom || customMap.has(sAdmUp);
      const house = houseMap[s.houseCode] || { name: s.houseCode || "All Houses", accentText: "#141413" };

      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td class="mono" style="font-weight:800; color:#0369a1; font-size:1.02rem;">
          ${vId !== "--" ? `<span>${vId}</span>` : `<span style="color:var(--text-muted); font-weight:700;">--</span>`}
          ${vId !== "--" ? `<button type="button" class="btn btn-secondary btn-copy-adm-row" data-adm="${vId}" style="font-size:0.68rem; padding:0.15rem 0.35rem; margin-left:0.3rem;" title="Copy Voter ID">📋</button>` : ""}
        </td>
        <td>
          <div style="font-weight:700; color:var(--text-primary); font-size:0.95rem;">${s.fullName}</div>
          <div class="stat-note" style="color:var(--text-muted); font-size:0.78rem;">
            ${s.fatherName ? `Father: ${s.fatherName}` : (s.gender ? `Gender: ${s.gender}` : "")}
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
      `;

      stuEl.stuTbody.appendChild(tr);
    });

    // Bind Copy buttons
    stuEl.stuTbody.querySelectorAll(".btn-copy-adm-row").forEach((btn) => {
      btn.addEventListener("click", () => {
        navigator.clipboard.writeText(btn.dataset.adm);
        btn.textContent = "✓";
        setTimeout(() => { btn.textContent = "📋"; }, 1200);
      });
    });

    // Bind Edit / Change buttons
    stuEl.stuTbody.querySelectorAll(".btn-open-edit-student").forEach((btn) => {
      btn.addEventListener("click", () => {
        const adm = btn.dataset.adm;
        const student = fullList.find((s) => String(s.admissionNo).toUpperCase() === String(adm).toUpperCase());
        if (!student) return;
        openEditStudentModal(student, acceptedAdmSet.has(String(adm).toUpperCase()));
      });
    });

    // Bind Delete buttons for custom added students
    stuEl.stuTbody.querySelectorAll(".btn-delete-custom-student").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const adm = btn.dataset.adm;
        const name = btn.dataset.name || adm;
        const confirmDelete = window.confirm(`Are you sure you want to remove student "${name}" (Voter ID: ${adm}) from the voter roster?`);
        if (!confirmDelete) return;

        try {
          btn.disabled = true;
          btn.textContent = "⏳";
          await window.AdminBackend.deleteStudent(adm);
          updateBadgeAddedCount();
          await refreshAll();
        } catch (err) {
          alert("Failed to remove student: " + (err.message || err));
          btn.disabled = false;
          btn.textContent = "🗑️";
        }
      });
    });
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
'''

# Insert STUDENTS_MASTER_LOGIC before the closing or after refreshAll in edit-votes.js
if "ALL STUDENTS MASTER REGISTER (HOUSE-WISE)" not in code:
    code += "\n" + STUDENTS_MASTER_LOGIC
    print("Appended STUDENTS_MASTER_LOGIC to edit-votes.js!")

# Also ensure refreshAll calls renderStudentsMasterTable if students view is active
old_refresh_all = '''        latestSnapshot = await window.AdminBackend.getSnapshot();
        renderOverviewKpis(latestSnapshot);
        renderBallotsTable(latestSnapshot);'''

new_refresh_all = '''        latestSnapshot = await window.AdminBackend.getSnapshot();
        renderOverviewKpis(latestSnapshot);
        renderBallotsTable(latestSnapshot);
        if (typeof renderStudentsMasterTable === "function") {
          renderStudentsMasterTable(latestSnapshot);
        }'''

if old_refresh_all in code:
    code = code.replace(old_refresh_all, new_refresh_all)
    print("Updated refreshAll in edit-votes.js!")

ev_js_path.write_text(code, encoding="utf-8")
print("Saved Houses/admin/edit-votes.js successfully!")
