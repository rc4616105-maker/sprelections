import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ==============================================================================
# 1. Update Houses/admin/edit-votes.html
# ==============================================================================
html_path = ROOT / "Houses" / "admin" / "edit-votes.html"
html_content = html_path.read_text(encoding="utf-8")

# Add the "View Added Students" button next to "Add Student to Voter List"
old_btn_group = r'(<div style="display:flex; gap:0.5rem; flex-wrap:wrap; align-items:center;">\s*)(<button type="button" id="btn-open-add-student"[^>]*>.*?</button>)'

new_btn_group = r'''\1<button type="button" id="btn-view-added-students" class="btn btn-secondary"
              style="font-weight:700; display:inline-flex; align-items:center; gap:0.45rem; border:1.5px solid #cbd5e1; background:#ffffff;"
              title="View all students who were manually added to the voter roster">
              <span>📋 View Added Students</span>
              <span id="badge-added-count" style="background:#0284c7; color:#fff; font-size:0.75rem; font-weight:800; padding:0.15rem 0.55rem; border-radius:999px;">0</span>
            </button>
            \2'''

if 'id="btn-view-added-students"' not in html_content:
    html_content = re.sub(old_btn_group, new_btn_group, html_content)

# Add "✨ Added Students (Custom)" option in ballot-status-filter
if 'value="added"' not in html_content:
    html_content = html_content.replace(
        '<option value="remaining">Pending (Not Voted)</option>',
        '<option value="remaining">Pending (Not Voted)</option>\n            <option value="added">✨ Added Students (Custom)</option>'
    )

# Add the View Added Students modal markup right before `<div id="add-student-modal"`
VIEW_ADDED_MODAL = """<!-- View Added Students Modal -->
  <div id="view-added-modal" class="modal-overlay" hidden>
    <div class="modal-card" style="max-width: 800px; width: 95%; max-height: 88vh; display: flex; flex-direction: column;" role="dialog" aria-modal="true"
      aria-labelledby="view-added-modal-title">
      <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem;">
        <div>
          <h3 id="view-added-modal-title" class="modal-title" style="margin: 0; display: flex; align-items: center; gap: 0.5rem;">
            <span>📋 Manually Added Students</span>
            <span id="modal-added-count-pill" style="font-size: 0.75rem; font-weight: 800; background: #e0f2fe; color: #0369a1; padding: 0.2rem 0.6rem; border-radius: 999px;">0 Students</span>
          </h3>
          <p class="modal-desc" style="margin-top: 0.35rem; margin-bottom: 0;">Students registered into the roster who were missing from the initial school register.</p>
        </div>
        <button type="button" id="view-added-modal-close-x" class="btn btn-secondary" style="font-size: 1.1rem; padding: 0.2rem 0.6rem; line-height: 1;" title="Close">✕</button>
      </div>

      <div style="overflow-y: auto; flex: 1; border: 1.5px solid #e2e8f0; border-radius: 8px; margin-top: 0.5rem; background: #ffffff;">
        <table class="data-table" style="margin: 0; width: 100%;">
          <thead>
            <tr style="background: #f8fafc;">
              <th style="width: 20%;">Voter ID</th>
              <th style="width: 32%;">Student Details</th>
              <th style="width: 20%;">House</th>
              <th style="width: 18%;">Status</th>
              <th style="width: 10%;">Action</th>
            </tr>
          </thead>
          <tbody id="added-students-tbody">
            <!-- Rendered dynamically -->
          </tbody>
        </table>
        <div id="added-students-empty" style="text-align: center; padding: 2.5rem 1rem;" hidden>
          <div style="font-size: 2.2rem; margin-bottom: 0.5rem;">📋</div>
          <h4 style="margin: 0; font-size: 1.05rem; font-weight: 700; color: #334155;">No Added Students Yet</h4>
          <p style="margin: 0.35rem 0 0; font-size: 0.85rem; color: #64748b;">Click <strong>"+ Add Student to Voter List"</strong> to register any missing student.</p>
        </div>
      </div>

      <div class="modal-actions" style="margin-top: 1rem; display: flex; justify-content: space-between; align-items: center;">
        <button type="button" id="btn-open-add-from-view" class="btn btn-primary" style="background:#059669; border-color:#059669; font-weight:700;">
          ➕ Add Another Student
        </button>
        <button type="button" id="view-added-modal-close" class="btn btn-secondary">Close</button>
      </div>
    </div>
  </div>

  """

if 'id="view-added-modal"' not in html_content:
    html_content = html_content.replace('<!-- Add Student to Voter List Modal -->', VIEW_ADDED_MODAL + '<!-- Add Student to Voter List Modal -->')

# Bump cachebuster
html_content = re.sub(r'(\./edit-votes\.js\?v=)[^"]*', r'\g<1>20261122h', html_content)
html_content = re.sub(r'(\./supabase-config\.js\?v=)[^"]*', r'\g<1>20261122h', html_content)

html_path.write_text(html_content, encoding="utf-8")
print("Updated Houses/admin/edit-votes.html successfully!")

# ==============================================================================
# 2. Update Houses/admin/edit-votes.js
# ==============================================================================
ev_path = ROOT / "Houses" / "admin" / "edit-votes.js"
ev_code = ev_path.read_text(encoding="utf-8")

# In updatePanelHeader:
header_target_block = """    } else if (target === "added") {
      el.ballotsPanelHeading.textContent = "Manually Added Students Register";
      el.ballotsPanelCaption.textContent = "Students registered into the roster who were missing from the initial school register.";"""

if 'target === "added"' not in ev_code:
    ev_code = ev_code.replace('} else if (target === "remaining") {', header_target_block + '\n    } else if (target === "remaining") {')

# In renderBallotsTable: handle statusFilter === "added"
STATUS_ADDED_HANDLER = """    // Handle "added" (Manually added students)
    if (statusFilter === "added") {
      const customList = getCustomStudentsList();
      const customSet = new Set(customList.map((s) => String(s.admissionNo).toUpperCase()));
      const acceptedAdmSet = new Set((snap.ballots || []).filter((b) => b.status === "accepted").map((b) => b.admissionNo));
      const cancelledAdmSet = new Set((snap.ballots || []).filter((b) => b.status === "cancelled").map((b) => b.admissionNo));

      const addedStudents = (snap.students || [])
        .filter((s) => customSet.has(String(s.admissionNo).toUpperCase()) || s.isCustom)
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
            <div class="stat-note">${s.className ? `Class ${s.className}-${s.section || "--"}` : (s.section || "--")} ${s.fatherName ? `· Father: ${s.fatherName}` : ""}</div>
          </td>
          <td><strong style="color:${house.accentText};">${formatHouseLabel(house.name)}</strong></td>
          <td>${votedStatusHtml}</td>
          <td><span class="stat-note">—</span></td>
          <td><span class="stat-note">—</span></td>
          <td><span class="badge badge-success" style="font-size:0.72rem; padding:2px 7px;">Custom Added</span></td>
          <td>
            <button type="button" class="btn btn-secondary btn-search-student-direct" data-adm="${s.admissionNo}" style="font-size:0.75rem; padding:0.25rem 0.55rem;">Inspect</button>
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
            filterAndRender();
          }
        });
      });

      return;
    }
"""

if 'statusFilter === "added"' not in ev_code:
    ev_code = ev_code.replace('// Handle "remaining"', STATUS_ADDED_HANDLER + '\n    // Handle "remaining"')

# Logic for View Added Students Modal & Badge Counter
VIEW_ADDED_CONTROLLER = """  // --- View Added Students Modal & Controller ---
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
          <div class="stat-note">${s.className ? `Class ${s.className}-${s.section || "--"}` : (s.section || "--")} ${s.fatherName ? `· Father: ${s.fatherName}` : ""}</div>
        </td>
        <td><strong style="color:${house.accentText};">${formatHouseLabel(house.name)}</strong></td>
        <td>${statusBadge}</td>
        <td>
          <button type="button" class="btn btn-secondary btn-view-in-table" data-adm="${s.admissionNo}" style="font-size:0.75rem; padding:0.25rem 0.55rem;" title="Show in Table">View</button>
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

    // View in table action
    addedStudentsTbody.querySelectorAll(".btn-view-in-table").forEach((btn) => {
      btn.addEventListener("click", () => {
        if (viewAddedModal) viewAddedModal.hidden = true;
        if (el.ballotStatusFilter) el.ballotStatusFilter.value = "added";
        if (el.ballotSearch) el.ballotSearch.value = btn.dataset.adm;
        updatePanelHeader("added");
        filterAndRender();
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
"""

if "btnViewAddedStudents" not in ev_code:
    ev_code = ev_code.replace("async function boot() {", VIEW_ADDED_CONTROLLER + "\n\n  async function boot() {")

# In boot: call updateBadgeAddedCount()
if "updateBadgeAddedCount();" not in ev_code:
    ev_code = ev_code.replace("populateClassAndSectionFilters();", "populateClassAndSectionFilters();\n    updateBadgeAddedCount();")

# After student is registered in addStudentForm submit: call updateBadgeAddedCount()
if "updateBadgeAddedCount();" not in ev_code[ev_code.find("addStudentSuccess.hidden = false;"):ev_code.find("await refreshAll();")]:
    ev_code = ev_code.replace("await refreshAll();", "updateBadgeAddedCount();\n        await refreshAll();")

ev_path.write_text(ev_code, encoding="utf-8")
print("Updated Houses/admin/edit-votes.js successfully!")
