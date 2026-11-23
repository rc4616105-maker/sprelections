import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ==============================================================================
# 1. Update Houses/admin/supabase-config.js (Add deleteStudent method)
# ==============================================================================
sb_path = ROOT / "Houses" / "admin" / "supabase-config.js"
sb_code = sb_path.read_text(encoding="utf-8")

DELETE_STUDENT_METHOD = """
    async deleteStudent(admissionNo) {
      const cleanAdm = String(admissionNo || "").trim().toUpperCase();
      if (!cleanAdm) throw new Error("Voter ID is required.");
      const qAdm = encodeURIComponent(cleanAdm);

      if (this.mode === "supabase") {
        await sbRest("DELETE", `/rest/v1/ballots?admission_no=eq.${qAdm}`, null, "return=representation").catch(() => {});
        await sbRest("DELETE", `/rest/v1/voters?admission_no=eq.${qAdm}`, null, "return=representation").catch(() => {});
      }

      if (window.ADMIN_DATA && window.ADMIN_DATA.students) {
        const idx = window.ADMIN_DATA.students.findIndex((s) => String(s.admissionNo || "").toUpperCase() === cleanAdm);
        if (idx >= 0) window.ADMIN_DATA.students.splice(idx, 1);
      }

      try {
        const raw = localStorage.getItem("spr_admin_custom_students");
        if (raw) {
          const list = JSON.parse(raw);
          const filtered = list.filter((cs) => String(cs.admissionNo || "").toUpperCase() !== cleanAdm);
          localStorage.setItem("spr_admin_custom_students", JSON.stringify(filtered));
        }
      } catch (e) {
        console.warn("Could not update localStorage:", e);
      }

      const nowIso = new Date().toISOString();
      const actorName = (typeof sessionStorage !== "undefined" && (sessionStorage.getItem("spr_admin_email") || sessionStorage.getItem("spr_admin_name"))) || "rc4616105@gmail.com";
      if (this.mode === "supabase") {
        await sbRest("POST", "/rest/v1/audit_logs", {
          id: `AUD-${Date.now().toString(36).toUpperCase()}`,
          action: "STUDENT_DELETED",
          ballot_id: null,
          admission_no: cleanAdm,
          student_name: cleanAdm,
          house_code: "",
          reason: `Removed student with Voter ID ${cleanAdm} from voter roster`,
          actor: actorName,
          created_at: nowIso,
        }).catch(() => {});
      }

      if (channel) channel.postMessage({ type: "store_updated", at: Date.now() });
      return { ok: true, admissionNo: cleanAdm };
    },
"""

if "async deleteStudent(" not in sb_code:
    sb_code = sb_code.replace("async addCandidate(", DELETE_STUDENT_METHOD.strip() + "\n\n    async addCandidate(")
    sb_path.write_text(sb_code, encoding="utf-8")
    print("Added deleteStudent method to Houses/admin/supabase-config.js!")

# ==============================================================================
# 2. Update Houses/admin/edit-votes.html (Adjust column width)
# ==============================================================================
html_path = ROOT / "Houses" / "admin" / "edit-votes.html"
html_code = html_path.read_text(encoding="utf-8")

html_code = html_code.replace(
    '<th style="width: 32%;">Student Details</th>\n              <th style="width: 20%;">House</th>\n              <th style="width: 18%;">Status</th>\n              <th style="width: 10%;">Action</th>',
    '<th style="width: 30%;">Student Details</th>\n              <th style="width: 18%;">House</th>\n              <th style="width: 16%;">Status</th>\n              <th style="width: 16%;">Action</th>'
)

# Bump cachebusters
html_code = re.sub(r'(\./edit-votes\.js\?v=)[^"]*', r'\g<1>20261122j', html_code)
html_code = re.sub(r'(\./supabase-config\.js\?v=)[^"]*', r'\g<1>20261122j', html_code)

html_path.write_text(html_code, encoding="utf-8")
print("Updated Houses/admin/edit-votes.html successfully!")

# ==============================================================================
# 3. Update Houses/admin/edit-votes.js (Add delete action)
# ==============================================================================
ev_path = ROOT / "Houses" / "admin" / "edit-votes.js"
ev_code = ev_path.read_text(encoding="utf-8")

# In renderAddedStudentsModalList:
old_modal_action = """        <td>
          <button type="button" class="btn btn-secondary btn-view-in-table" data-adm="${s.admissionNo}" style="font-size:0.75rem; padding:0.25rem 0.55rem;" title="Show in Table">View</button>
        </td>"""

new_modal_action = """        <td style="white-space:nowrap;">
          <button type="button" class="btn btn-secondary btn-view-in-table" data-adm="${s.admissionNo}" style="font-size:0.75rem; padding:0.25rem 0.5rem;" title="Show in Table">View</button>
          <button type="button" class="btn btn-danger btn-delete-added-student" data-adm="${s.admissionNo}" data-name="${s.fullName}" style="font-size:0.75rem; padding:0.25rem 0.5rem; margin-left:0.35rem; background:#dc2626; border-color:#dc2626; color:#ffffff; font-weight:700;" title="Remove this student">🗑️ Remove</button>
        </td>"""

ev_code = ev_code.replace(old_modal_action, new_modal_action)

# Add event listeners for btn-delete-added-student
DELETE_LISTENER_CODE = """
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
"""

if "btn-delete-added-student" not in ev_code[ev_code.find("renderAddedStudentsModalList"):ev_code.find("if (btnViewAddedStudents")]:
    ev_code = ev_code.replace(
      '// View in table action',
      DELETE_LISTENER_CODE.strip() + '\n\n    // View in table action'
    )

# Also in main table when statusFilter === "added"
old_table_action = """          <td>
            <button type="button" class="btn btn-secondary btn-search-student-direct" data-adm="${s.admissionNo}" style="font-size:0.75rem; padding:0.25rem 0.55rem;">Inspect</button>
          </td>"""

new_table_action = """          <td style="white-space:nowrap;">
            <button type="button" class="btn btn-secondary btn-search-student-direct" data-adm="${s.admissionNo}" style="font-size:0.75rem; padding:0.25rem 0.45rem;">Inspect</button>
            <button type="button" class="btn btn-danger btn-delete-table-student" data-adm="${s.admissionNo}" data-name="${s.fullName}" style="font-size:0.75rem; padding:0.25rem 0.45rem; margin-left:0.3rem; background:#dc2626; border-color:#dc2626; color:#ffffff; font-weight:700;" title="Remove this student">Delete</button>
          </td>"""

ev_code = ev_code.replace(old_table_action, new_table_action)

# Add listener for btn-delete-table-student in main table
TABLE_DELETE_LISTENER = """      el.ballotsTableTbody.querySelectorAll(".btn-delete-table-student").forEach((btn) => {
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
"""

if "btn-delete-table-student" not in ev_code[ev_code.find('statusFilter === "added"'):ev_code.find('return;\n    }\n\n    // Handle "remaining"')]:
    ev_code = ev_code.replace(
      '// Bind copy and inspect buttons',
      TABLE_DELETE_LISTENER.strip() + '\n\n      // Bind copy and inspect buttons'
    )

ev_path.write_text(ev_code, encoding="utf-8")
print("Updated Houses/admin/edit-votes.js successfully!")
