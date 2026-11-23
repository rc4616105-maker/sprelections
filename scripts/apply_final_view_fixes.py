import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 1. Update Houses/admin/supabase-config.js
sb_cfg = ROOT / 'Houses' / 'admin' / 'supabase-config.js'
sb_code = sb_cfg.read_text(encoding='utf-8')

merge_custom = '''          // Merge custom added students from localStorage
          try {
            const rawCustom = localStorage.getItem("spr_admin_custom_students");
            if (rawCustom) {
              JSON.parse(rawCustom).forEach((cs) => {
                if (cs && cs.admissionNo && !byAdm.has(cs.admissionNo)) {
                  byAdm.set(cs.admissionNo, {
                    admissionNo: cs.admissionNo,
                    fullName: cs.fullName || cs.admissionNo,
                    fatherName: cs.fatherName || "",
                    gender: cs.gender || "Boy",
                    className: cs.className || "10",
                    section: cs.section || "",
                    houseCode: cs.houseCode || "BHEESHMA",
                    isStaff: false,
                    isActive: true,
                    isCandidate: false,
                    isCustom: true,
                  });
                }
              });
            }
          } catch (_) {}'''

if 'const rawCustom = localStorage.getItem' not in sb_code:
    sb_code = sb_code.replace('const positions = window.ADMIN_DATA.positions', merge_custom + '\n\n          const positions = window.ADMIN_DATA.positions')
    sb_cfg.write_text(sb_code, encoding='utf-8')
    print('Updated supabase-config.js with localStorage custom students merge!')
else:
    print('supabase-config.js already has custom students merge.')

# 2. Update Houses/admin/edit-votes.js
ev_path = ROOT / 'Houses' / 'admin' / 'edit-votes.js'
ev_code = ev_path.read_text(encoding='utf-8')

# Ensure addedStudents in statusFilter === "added" uses customList directly and highlights viewed student
old_added_block = '''      const addedStudents = (snap.students || [])
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
        })'''

new_added_block = '''      const addedStudents = customList
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
        })'''

if old_added_block in ev_code:
    ev_code = ev_code.replace(old_added_block, new_added_block)
    print('Updated statusFilter === "added" to use customList directly!')

# In modal View button, reset filters and scroll
old_modal_view = '''    // View in table action: closes modal, switches table to 'added', populates search with Voter ID, and scrolls table into view
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
    });'''

new_modal_view = '''    // View in table action: closes modal, switches table to 'added', populates search with Voter ID, and scrolls table into view
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

ev_code = ev_code.replace(old_modal_view, new_modal_view)

# In accepted mode search fallback: when searching an unvoted student in accepted mode, show them
search_fallback = '''    // If searching and no cast ballots matched, check if any registered or added student matches q
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
    }'''

target_anchor = 'el.ballotsTableTbody.innerHTML = "";\n    if (el.ballotsTableEmpty) {'
if 'const allStudentsPool = [...(snap.students || [])];' not in ev_code and target_anchor in ev_code:
    ev_code = ev_code.replace(target_anchor, search_fallback + '\n\n    ' + target_anchor)
    print('Inserted accepted mode search fallback!')

ev_path.write_text(ev_code, encoding='utf-8')
print('Updated Houses/admin/edit-votes.js!')

# 3. Update Houses/admin/edit-votes.html
ev_html = ROOT / 'Houses' / 'admin' / 'edit-votes.html'
html_text = ev_html.read_text(encoding='utf-8')
html_text = html_text.replace('âœ¨ Added Students (Custom)', '📋 Added Students (Custom)')
html_text = re.sub(r'(\./edit-votes\.js\?v=)[^"]*', r'\g<1>20261122m', html_text)
ev_html.write_text(html_text, encoding='utf-8')
print('Updated edit-votes.html!')

# 4. Update Houses/admin/index.html
idx_html = ROOT / 'Houses' / 'admin' / 'index.html'
idx_text = idx_html.read_text(encoding='utf-8')
idx_text = re.sub(r'src="\./app\.js(\?v=[^"]*)?"', 'src="./app.js?v=20261122m"', idx_text)
idx_html.write_text(idx_text, encoding='utf-8')
print('Updated index.html!')
