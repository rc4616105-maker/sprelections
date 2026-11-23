import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ==============================================================================
# 1. Update Houses/admin/app.js
# ==============================================================================
app_path = ROOT / "Houses" / "admin" / "app.js"
app_code = app_path.read_text(encoding="utf-8")

GET_DISPLAY_VOTER_ID_FN = """
  function getDisplayVoterId(s) {
    if (!s) return "--";
    const adm = String(s.admissionNo || "").trim();

    // 1. Aditya Vikram demo voter code
    if (adm === "1C8492" || (s.fullName === "Aditya Vikram" && (adm === "0000" || adm === "1C8492"))) {
      return "1C8492";
    }

    // 2. Custom student object flag
    if (s.isCustom) return adm.toUpperCase();

    // 3. Stored custom registered students in localStorage
    try {
      const raw = localStorage.getItem("spr_admin_custom_students");
      if (raw) {
        const list = JSON.parse(raw);
        if (list.some((cs) => String(cs.admissionNo || "").toUpperCase() === adm.toUpperCase())) {
          return adm.toUpperCase();
        }
      }
    } catch (_) {}

    // 4. Matches official 6-character random format: 1 digit + 1 letter + 4 digits (e.g. 1M5168, 1C8492, 9K4821)
    if (/^[0-9][A-Za-z][0-9]{4}$/.test(adm)) {
      return adm.toUpperCase();
    }

    // For all other students who do not have an official 6-character random Voter ID created yet:
    // Per school requirement: "FOR WHOM THEY NOT HAVE IDS IE NOT YET CREATED JUST KEEP -- FOR NOW LATER WE WILL ADD"
    return "--";
  }
"""

if "function getDisplayVoterId(" not in app_code:
    app_code = app_code.replace("function formatHouseLabel(", GET_DISPLAY_VOTER_ID_FN + "\n  function formatHouseLabel(")

# Replace table header "Admission ID" -> "Voter ID"
app_code = app_code.replace("<th>Admission ID</th>", "<th>Voter ID</th>")

# In eligible & remaining table render (line ~320):
old_render_row1 = "tr.children[0].textContent = s.admissionNo;"
new_render_row1 = """const vId = getDisplayVoterId(s);
        if (vId === "--") {
          tr.children[0].innerHTML = '<span style="color:var(--text-muted); font-weight:700;">--</span>';
        } else {
          tr.children[0].innerHTML = `<strong class="mono" style="color:#0369a1; font-weight:800; font-size:1.02rem;">${vId}</strong>`;
        }"""
app_code = app_code.replace(old_render_row1, new_render_row1)

# In accepted table render (line ~399):
# Notice in accepted table, tr.children[0].textContent = s.admissionNo; was already replaced if exact match, let's check
app_code = re.sub(
    r'tr\.children\[0\]\.textContent = s\.admissionNo;',
    new_render_row1,
    app_code
)

# In cancelled table render: tr.children[0].textContent = v.admissionNo;
old_render_row_cancelled = "tr.children[0].textContent = v.admissionNo;"
new_render_row_cancelled = """const vId = getDisplayVoterId(v);
        if (vId === "--") {
          tr.children[0].innerHTML = '<span style="color:var(--text-muted); font-weight:700;">--</span>';
        } else {
          tr.children[0].innerHTML = `<strong class="mono" style="color:#0369a1; font-weight:800; font-size:1.02rem;">${vId}</strong>`;
        }"""
app_code = app_code.replace(old_render_row_cancelled, new_render_row_cancelled)

# Sort so created voter IDs appear at top of drilldown table
old_sort_eligible = ".sort((a, b) => a.admissionNo.localeCompare(b.admissionNo));"
new_sort_eligible = """.sort((a, b) => {
          const vA = getDisplayVoterId(a);
          const vB = getDisplayVoterId(b);
          if (vA !== "--" && vB === "--") return -1;
          if (vA === "--" && vB !== "--") return 1;
          if (vA !== "--" && vB !== "--") return vA.localeCompare(vB);
          return (a.fullName || "").localeCompare(b.fullName || "");
        });"""
app_code = app_code.replace(old_sort_eligible, new_sort_eligible)

# Search filter update in app.js
old_search_hay = "const hay = `${s.admissionNo} ${s.fullName} ${s.className}-${s.section}`.toLowerCase();"
new_search_hay = """const vId = getDisplayVoterId(s);
            const hay = `${vId !== "--" ? vId : ""} ${s.admissionNo} ${s.fullName} ${s.className}-${s.section}`.toLowerCase();"""
app_code = app_code.replace(old_search_hay, new_search_hay)

app_path.write_text(app_code, encoding="utf-8")
print("Updated Houses/admin/app.js successfully!")

# ==============================================================================
# 2. Update Houses/admin/edit-votes.js
# ==============================================================================
ev_path = ROOT / "Houses" / "admin" / "edit-votes.js"
ev_code = ev_path.read_text(encoding="utf-8")

if "function getDisplayVoterId(" not in ev_code:
    ev_code = ev_code.replace("function formatHouseLabel(", GET_DISPLAY_VOTER_ID_FN + "\n  function formatHouseLabel(")

# In edit-votes.js remaining table (line ~456):
old_ev_rem = "tr.children[0].textContent = s.admissionNo;"
new_ev_rem = """const vId = getDisplayVoterId(s);
        if (vId === "--") {
          tr.children[0].innerHTML = '<span style="color:var(--text-muted); font-weight:700;">--</span>';
        } else {
          tr.children[0].innerHTML = `<strong class="mono" style="color:#0369a1; font-weight:800; font-size:1.02rem;">${vId}</strong>`;
        }"""
ev_code = re.sub(r'tr\.children\[0\]\.textContent = s\.admissionNo;', new_ev_rem, ev_code)

# In edit-votes.js cancelled / cast (line ~627):
old_ev_cast = "tr.children[0].textContent = v.admissionNo;"
new_ev_cast = """const vId = getDisplayVoterId(v);
        if (vId === "--") {
          tr.children[0].innerHTML = '<span style="color:var(--text-muted); font-weight:700;">--</span>';
        } else {
          tr.children[0].innerHTML = `<strong class="mono" style="color:#0369a1; font-weight:800; font-size:1.02rem;">${vId}</strong>`;
        }"""
ev_code = ev_code.replace(old_ev_cast, new_ev_cast)

# Sort so created voter IDs appear at top in edit-votes.js
ev_code = ev_code.replace(".sort((a, b) => a.admissionNo.localeCompare(b.admissionNo));", new_sort_eligible)

ev_path.write_text(ev_code, encoding="utf-8")
print("Updated Houses/admin/edit-votes.js successfully!")

# ==============================================================================
# 3. Bump cachebusters in index.html and edit-votes.html
# ==============================================================================
index_path = ROOT / "Houses" / "admin" / "index.html"
index_html = index_path.read_text(encoding="utf-8")
index_html = re.sub(r'src="\./app\.js(\?v=[^"]*)?"', 'src="./app.js?v=20261122i"', index_html)
index_html = re.sub(r'href="\./styles\.css(\?v=[^"]*)?"', 'href="./styles.css?v=20261122i"', index_html)
index_path.write_text(index_html, encoding="utf-8")
print("Bumped cachebusters in Houses/admin/index.html to v=20261122i")

ev_html_path = ROOT / "Houses" / "admin" / "edit-votes.html"
ev_html = ev_html_path.read_text(encoding="utf-8")
ev_html = re.sub(r'(\./edit-votes\.js\?v=)[^"]*', r'\g<1>20261122i', ev_html)
ev_html_path.write_text(ev_html, encoding="utf-8")
print("Bumped cachebusters in Houses/admin/edit-votes.html to v=20261122i")

print("\nDone! Voter ID display updated across all admin tables.")
