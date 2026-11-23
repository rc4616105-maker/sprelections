import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ==============================================================================
# 1. Update Houses/admin/app.js
# ==============================================================================
app_path = ROOT / "Houses" / "admin" / "app.js"
app_code = app_path.read_text(encoding="utf-8")

# Fix duplicate 0000 in baseRoster
old_app_base_loop = """    baseRoster.forEach((s) => {
      if (!seenAdms.has(s.admissionNo)) {
        seenAdms.add(s.admissionNo);
        initialStudents.push({ ...s });
      }
    });"""

new_app_base_loop = """    baseRoster.forEach((s) => {
      // Exclude duplicate 0000 teacher demo account so Aditya Vikram appears only once as 1C8492
      if (s.admissionNo === "0000") return;
      if (!seenAdms.has(s.admissionNo)) {
        seenAdms.add(s.admissionNo);
        initialStudents.push({ ...s });
      }
    });"""

app_code = app_code.replace(old_app_base_loop, new_app_base_loop)

# Fix getDisplayVoterId in app.js
old_get_voter_fn = """  function getDisplayVoterId(s) {
    if (!s) return "--";
    const adm = String(s.admissionNo || "").trim();

    // 1. Aditya Vikram demo voter code
    if (adm === "1C8492" || (s.fullName === "Aditya Vikram" && (adm === "0000" || adm === "1C8492"))) {
      return "1C8492";
    }"""

new_get_voter_fn = """  function getDisplayVoterId(s) {
    if (!s) return "--";
    const adm = String(s.admissionNo || "").trim().toUpperCase();

    // 1. Aditya Vikram demo voter code
    if (adm === "1C8492") {
      return "1C8492";
    }"""

app_code = app_code.replace(old_get_voter_fn, new_get_voter_fn)

app_path.write_text(app_code, encoding="utf-8")
print("Updated Houses/admin/app.js successfully!")

# ==============================================================================
# 2. Update Houses/admin/edit-votes.js
# ==============================================================================
ev_path = ROOT / "Houses" / "admin" / "edit-votes.js"
ev_code = ev_path.read_text(encoding="utf-8")

# Fix duplicate 0000 in baseRoster
ev_code = ev_code.replace(old_app_base_loop, new_app_base_loop)
ev_code = ev_code.replace(old_get_voter_fn, new_get_voter_fn)

# Replace any lingering filterAndRender() calls with renderBallotsTable(latestSnapshot)
ev_code = re.sub(r'filterAndRender\(\);', 'if (latestSnapshot) renderBallotsTable(latestSnapshot);', ev_code)

# Enhance renderBallotsTable when statusFilter === "accepted" so if user searched an unvoted student (or clicked View), they appear in the table!
SEARCH_FALLBACK_CODE = """      // If searching and no cast ballots matched, check if an unvoted student matches q
      if (filteredVoters.length === 0 && q) {
        const studentMatches = (snap.students || []).filter((s) => {
          if (hFilter && s.houseCode !== hFilter) return false;
          if (cFilter && normClass(s.className) !== normClass(cFilter)) return false;
          if (sFilter && normSection(s.section) !== normSection(sFilter)) return false;
          const vId = getDisplayVoterId(s);
          const hay = `${vId !== "--" ? vId : ""} ${s.admissionNo} ${s.fullName} ${s.className}-${s.section}`.toLowerCase();
          return hay.includes(q);
        });

        if (studentMatches.length > 0) {
          el.ballotsTableEmpty.hidden = true;
          studentMatches.forEach((s) => {
            const house = houseMap[s.houseCode] || { name: s.houseCode, accentText: "#141413" };
            const vId = getDisplayVoterId(s);
            const tr = document.createElement("tr");
            tr.innerHTML = `
              <td class="mono" style="font-weight:800; color:#0369a1; font-size:1.05rem;">
                ${vId !== "--" ? `<span>${vId}</span>` : `<span style="color:var(--text-muted); font-weight:700;">--</span>`}
              </td>
              <td>
                <strong>${s.fullName}</strong>
                <div class="stat-note">${s.className ? `Class ${s.className}-${s.section || "--"}` : (s.section || "--")} ${s.fatherName ? `· Father: ${s.fatherName}` : ""}</div>
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
"""

# Insert SEARCH_FALLBACK_CODE before `el.ballotsTableEmpty.hidden = filteredVoters.length > 0;` in accepted handler
old_empty_block = """      el.ballotsTableEmpty.hidden = filteredVoters.length > 0;
      if (filteredVoters.length === 0) {
        if (el.emptyIcon) el.emptyIcon.textContent = "🗳️";
        if (el.emptyTitle) el.emptyTitle.textContent = "No Cast Ballots Found";"""

if "const studentMatches = (snap.students || []).filter" not in ev_code:
    new_empty_block = SEARCH_FALLBACK_CODE + "\n      " + old_empty_block
    ev_code = ev_code.replace(old_empty_block, new_empty_block)

# In modal View button: ensure it switches to 'added' and calls renderBallotsTable(latestSnapshot)
old_view_btn_handler = """    // View in table action
    addedStudentsTbody.querySelectorAll(".btn-view-in-table").forEach((btn) => {
      btn.addEventListener("click", () => {
        if (viewAddedModal) viewAddedModal.hidden = true;
        if (el.ballotStatusFilter) el.ballotStatusFilter.value = "added";
        if (el.ballotSearch) el.ballotSearch.value = btn.dataset.adm;
        updatePanelHeader("added");
        if (latestSnapshot) renderBallotsTable(latestSnapshot);
      });
    });"""

new_view_btn_handler = """    // View in table action: closes modal, switches table to 'added', populates search with Voter ID, and scrolls table into view
    addedStudentsTbody.querySelectorAll(".btn-view-in-table").forEach((btn) => {
      btn.addEventListener("click", () => {
        if (viewAddedModal) viewAddedModal.hidden = true;
        const adm = btn.dataset.adm;
        if (el.ballotStatusFilter) el.ballotStatusFilter.value = "added";
        if (el.ballotSearch) el.ballotSearch.value = adm;
        updatePanelHeader("added");
        if (latestSnapshot) renderBallotsTable(latestSnapshot);
        if (el.viewBallots) {
          el.viewBallots.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      });
    });"""

ev_code = ev_code.replace(old_view_btn_handler, new_view_btn_handler)

ev_path.write_text(ev_code, encoding="utf-8")
print("Updated Houses/admin/edit-votes.js successfully!")

# ==============================================================================
# 3. Bump cachebusters in index.html and edit-votes.html
# ==============================================================================
index_path = ROOT / "Houses" / "admin" / "index.html"
index_html = index_path.read_text(encoding="utf-8")
index_html = re.sub(r'src="\./app\.js(\?v=[^"]*)?"', 'src="./app.js?v=20261122l"', index_html)
index_path.write_text(index_html, encoding="utf-8")
print("Bumped cachebusters in index.html to v=20261122l")

ev_html_path = ROOT / "Houses" / "admin" / "edit-votes.html"
ev_html = ev_html_path.read_text(encoding="utf-8")
ev_html = re.sub(r'(\./edit-votes\.js\?v=)[^"]*', r'\g<1>20261122l', ev_html)
ev_html_path.write_text(ev_html, encoding="utf-8")
print("Bumped cachebusters in edit-votes.html to v=20261122l")

print("\nDone! View in table and cast votes display finalized.")
