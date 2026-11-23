import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 1. Update Houses/admin/edit-votes.js
ev_path = ROOT / "Houses" / "admin" / "edit-votes.js"
code = ev_path.read_text(encoding="utf-8")

# Update refreshAll
old_refresh = '''        latestSnapshot = await window.AdminBackend.getSnapshot();
        renderOverviewKpis(latestSnapshot);
        renderBallotsTable(latestSnapshot);
        if (selectedEditorAdm) {'''

new_refresh = '''        latestSnapshot = await window.AdminBackend.getSnapshot();
        renderOverviewKpis(latestSnapshot);
        renderBallotsTable(latestSnapshot);
        if (typeof renderStudentsMasterTable === "function") {
          renderStudentsMasterTable(latestSnapshot);
        }
        if (selectedEditorAdm) {'''

if old_refresh in code:
    code = code.replace(old_refresh, new_refresh)
    print("Updated refreshAll to call renderStudentsMasterTable!")

# Update updateBadgeAddedCount to update both badges
old_badge = '''  function updateBadgeAddedCount() {
    const list = getCustomStudentsList();
    const count = list.length;
    if (badgeAddedCount) badgeAddedCount.textContent = count;
    if (modalAddedCountPill) modalAddedCountPill.textContent = `${count} Student${count === 1 ? "" : "s"}`;
  }'''

new_badge = '''  function updateBadgeAddedCount() {
    const list = getCustomStudentsList();
    const count = list.length;
    if (badgeAddedCount) badgeAddedCount.textContent = count;
    const badgeAlt = document.getElementById("badge-added-count-alt");
    if (badgeAlt) badgeAlt.textContent = count;
    if (modalAddedCountPill) modalAddedCountPill.textContent = `${count} Student${count === 1 ? "" : "s"}`;
  }'''

if old_badge in code:
    code = code.replace(old_badge, new_badge)
    print("Updated updateBadgeAddedCount!")

# Update modal View button in added students modal to switch to students master view
old_modal_view = '''    // View in table action: closes modal, switches table to 'added', populates search with Voter ID, and scrolls table into view
    addedStudentsTbody.querySelectorAll(".btn-view-in-table").forEach((btn) => {
      btn.addEventListener("click", () => {
        if (viewAddedModal) viewAddedModal.hidden = true;
        const adm = btn.dataset.adm;
        if (el.ballotHouseFilter) el.ballotHouseFilter.value = "";
        if (el.ballotClassFilter) el.ballotClassFilter.value = "";
        if (el.ballotSectionFilter) el.ballotSectionFilter.value = "";
        if (el.ballotStatusFilter) el.ballotStatusFilter.value = "added";
        if (el.ballotSearch) el.ballotSearch.value = adm;
        updatePanelHeader("added");
        if (latestSnapshot) renderBallotsTable(latestSnapshot);
        if (el.viewBallots) {
          el.viewBallots.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      });
    });'''

new_modal_view = '''    // View in table action: closes modal, switches to All Students Roster, populates search with Voter ID, and scrolls table into view
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
    });'''

if old_modal_view in code:
    code = code.replace(old_modal_view, new_modal_view)
    print("Updated modal View button to switch to students master view!")

ev_path.write_text(code, encoding="utf-8")
print("Saved Houses/admin/edit-votes.js successfully!")

# Bump cachebusters to 20261122n in edit-votes.html and index.html
ev_html_path = ROOT / "Houses" / "admin" / "edit-votes.html"
html = ev_html_path.read_text(encoding="utf-8")
html = re.sub(r'(\./edit-votes\.js\?v=)[^"]*', r'\g<1>20261122n', html)
html = re.sub(r'(\./supabase-config\.js\?v=)[^"]*', r'\g<1>20261122n', html)
html = re.sub(r'(\./styles\.css\?v=)[^"]*', r'\g<1>20261122n', html)
ev_html_path.write_text(html, encoding="utf-8")
print("Bumped cachebusters in edit-votes.html!")

idx_html_path = ROOT / "Houses" / "admin" / "index.html"
idx_html = idx_html_path.read_text(encoding="utf-8")
idx_html = re.sub(r'src="\./app\.js(\?v=[^"]*)?"', 'src="./app.js?v=20261122n"', idx_html)
idx_html = re.sub(r'src="\./supabase-config\.js(\?v=[^"]*)?"', 'src="./supabase-config.js?v=20261122n"', idx_html)
idx_html_path.write_text(idx_html, encoding="utf-8")
print("Bumped cachebusters in index.html!")

print("\nFinal flow adjustments complete!")
