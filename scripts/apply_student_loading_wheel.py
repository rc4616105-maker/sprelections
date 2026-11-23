# -*- coding: utf-8 -*-
import sys

with open('Houses/admin/edit-votes.js', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update refreshAll to also update students table if students view is active
old_refresh = """      latestSnapshot = await window.AdminBackend.getSnapshot();
      renderOverviewKpis(latestSnapshot);
      renderBallotsTable(latestSnapshot);
      if (selectedEditorAdm) {
        loadStudentEditor(selectedEditorAdm);
      }"""

new_refresh = """      latestSnapshot = await window.AdminBackend.getSnapshot();
      renderOverviewKpis(latestSnapshot);
      renderBallotsTable(latestSnapshot);
      if (stuEl && stuEl.viewStudents && !stuEl.viewStudents.hidden) {
        renderStudentsMasterTable(latestSnapshot);
      }
      if (selectedEditorAdm) {
        loadStudentEditor(selectedEditorAdm);
      }"""

assert old_refresh in code, "old_refresh not found"
code = code.replace(old_refresh, new_refresh, 1)

# 2. Update stuEl elements & state variables
old_stuel = """    stuStatusFilter: document.getElementById("stu-master-status-filter"),
    stuTbody: document.getElementById("stu-master-tbody"),
    stuEmpty: document.getElementById("stu-master-empty"),
    stuPagination: document.getElementById("stu-master-pagination"),
    stuPaginationInfo: document.getElementById("stu-pagination-info"),
    btnStuLoadMore: document.getElementById("btn-stu-load-more"),
    btnStuLoadAll: document.getElementById("btn-stu-load-all"),"""

new_stuel = """    stuStatusFilter: document.getElementById("stu-master-status-filter"),
    stuTbody: document.getElementById("stu-master-tbody"),
    stuLoading: document.getElementById("stu-master-loading"),
    stuEmpty: document.getElementById("stu-master-empty"),"""

assert old_stuel in code, "old_stuel not found"
code = code.replace(old_stuel, new_stuel, 1)

old_state = """  let currentStudentsList = [];
  let currentFilteredStudents = [];
  let currentAcceptedAdmSet = new Set();
  let visibleStudentLimit = 80;
  let isStuTbodyDelegated = false;"""

new_state = """  let currentStudentsList = [];
  let currentFilteredStudents = [];
  let currentAcceptedAdmSet = new Set();
  let isStuTbodyDelegated = false;"""

assert old_state in code, "old_state not found"
code = code.replace(old_state, new_state, 1)

# 3. Remove visibleStudentLimit = 80; in event listeners
old_listeners = """  if (stuEl.stuClassFilter) {
    stuEl.stuClassFilter.addEventListener("change", () => {
      populateStuMasterSections();
      visibleStudentLimit = 80;
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
      visibleStudentLimit = 80;
      renderStudentsMasterTable(latestSnapshot || { students: window.ADMIN_DATA?.students });
    });
  });

  if (stuEl.stuHouseFilter) {
    stuEl.stuHouseFilter.addEventListener("change", () => {
      activeStudentHouseFilter = stuEl.stuHouseFilter.value;
      stuEl.houseFilterPills.forEach((p) => {
        p.classList.toggle("is-active", (p.dataset.house || "") === activeStudentHouseFilter);
      });
      visibleStudentLimit = 80;
      renderStudentsMasterTable(latestSnapshot || { students: window.ADMIN_DATA?.students });
    });
  }

  let searchDebounceTimer = null;
  if (stuEl.stuSearch) {
    stuEl.stuSearch.addEventListener("input", () => {
      clearTimeout(searchDebounceTimer);
      searchDebounceTimer = setTimeout(() => {
        visibleStudentLimit = 80;
        renderStudentsMasterTable(latestSnapshot || { students: window.ADMIN_DATA?.students });
      }, 80);
    });
  }
  if (stuEl.stuSectionFilter) {
    stuEl.stuSectionFilter.addEventListener("change", () => {
      visibleStudentLimit = 80;
      renderStudentsMasterTable(latestSnapshot || { students: window.ADMIN_DATA?.students });
    });
  }
  if (stuEl.stuStatusFilter) {
    stuEl.stuStatusFilter.addEventListener("change", () => {
      visibleStudentLimit = 80;
      renderStudentsMasterTable(latestSnapshot || { students: window.ADMIN_DATA?.students });
    });
  }"""

new_listeners = """  if (stuEl.stuClassFilter) {
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
  }"""

assert old_listeners in code, "old_listeners not found"
code = code.replace(old_listeners, new_listeners, 1)

# 4. Replace entire renderStudentsMasterTable function
start_marker = "  // Render All Students Master Register Table\n  function renderStudentsMasterTable(snap) {"
end_marker = "    updateStudentTableDOM();\n  }"

idx_start = code.find(start_marker)
assert idx_start != -1, "start_marker not found"
idx_end = code.find(end_marker, idx_start)
assert idx_end != -1, "end_marker not found"
idx_end += len(end_marker)

new_func = """  // Render All Students Master Register Table
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
  }"""

code = code[:idx_start] + new_func + code[idx_end:]

with open('Houses/admin/edit-votes.js', 'w', encoding='utf-8') as f:
    f.write(code)

print('Successfully applied student loading wheel and renderer to edit-votes.js!')
