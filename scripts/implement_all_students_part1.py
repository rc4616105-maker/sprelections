import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ==============================================================================
# 1. Update Houses/admin/supabase-config.js
# ==============================================================================
sb_path = ROOT / "Houses" / "admin" / "supabase-config.js"
sb_code = sb_path.read_text(encoding="utf-8")

# Add updateStudent method
UPDATE_STUDENT_FN = '''    async updateStudent({ admissionNo, fullName, fatherName, gender, className, section, houseCode }) {
      const cleanAdm = String(admissionNo || "").trim().toUpperCase();
      if (!cleanAdm) throw new Error("Voter ID is required.");
      const cleanName = String(fullName || "").trim();
      if (!cleanName) throw new Error("Student full name is required.");
      const cleanFather = String(fatherName || "").trim();
      const cleanGender = String(gender || "Boy").trim();
      const cleanClass = String(className || "10").trim();
      const cleanSec = String(section || "").trim();
      const cleanHouse = String(houseCode || "BHEESHMA").toUpperCase().trim();

      const houseNameMap = {
        BHEESHMA: "Bheeshma House",
        GURUDRONA: "Gurudrona House",
        HANUMAN: "Hanuman House",
        KARNA: "Karna House",
        VASISTHA: "Vasistha House",
        VISHWAMITHRA: "Vishwamithra House",
        CENTRAL: "School Cabinet",
        ALL: "All Houses / Faculty",
      };
      const houseName = houseNameMap[cleanHouse] || cleanHouse;

      const patchData = {
        fullName: cleanName,
        fatherName: cleanFather,
        gender: cleanGender,
        className: cleanClass,
        section: cleanSec,
        houseCode: cleanHouse,
        houseName: houseName,
      };

      // 1. Save to spr_admin_student_overrides in localStorage
      try {
        const raw = localStorage.getItem("spr_admin_student_overrides");
        const map = raw ? JSON.parse(raw) : {};
        map[cleanAdm] = { ...(map[cleanAdm] || {}), ...patchData };
        localStorage.setItem("spr_admin_student_overrides", JSON.stringify(map));
      } catch (_) {}

      // 2. If present in spr_admin_custom_students, update it there
      try {
        const rawCustom = localStorage.getItem("spr_admin_custom_students");
        if (rawCustom) {
          const list = JSON.parse(rawCustom);
          const idx = list.findIndex((s) => String(s.admissionNo).toUpperCase() === cleanAdm);
          if (idx !== -1) {
            list[idx] = { ...list[idx], ...patchData };
            localStorage.setItem("spr_admin_custom_students", JSON.stringify(list));
          }
        }
      } catch (_) {}

      // 3. Update memory data
      if (window.ADMIN_DATA && window.ADMIN_DATA.students) {
        const target = window.ADMIN_DATA.students.find((s) => String(s.admissionNo).toUpperCase() === cleanAdm);
        if (target) Object.assign(target, patchData);
      }

      // 4. Update Supabase voters table if connected
      if (this.mode === "supabase") {
        try {
          const nowIso = new Date().toISOString();
          await sbRest("PATCH", `/rest/v1/voters?admission_no=eq.${encodeURIComponent(cleanAdm)}`, {
            full_name: cleanName,
            class_name: cleanClass,
            section: cleanSec,
            house_code: cleanHouse,
            house_name: houseName,
            updated_at: nowIso,
          });

          await sbRest("POST", "/rest/v1/audit_logs", {
            id: `AUD-${Date.now().toString(36).toUpperCase()}`,
            action: "STUDENT_UPDATED",
            admission_no: cleanAdm,
            student_name: cleanName,
            house_code: cleanHouse,
            reason: `Admin updated student details: Class ${cleanClass}-${cleanSec}, House: ${cleanHouse}`,
            actor: this.userEmail || "Admin",
            created_at: nowIso,
          }).catch(() => {});
        } catch (sbErr) {
          console.warn("Supabase voter update warning:", sbErr);
        }
      }

      return { success: true, student: { admissionNo: cleanAdm, ...patchData } };
    },
'''

if "async updateStudent(" not in sb_code:
    sb_code = sb_code.replace("async deleteStudent(", UPDATE_STUDENT_FN + "\n    async deleteStudent(")
    print("Added updateStudent to supabase-config.js!")

# Apply overrides in getSnapshot
OVERRIDE_MERGE = '''          // Apply student overrides from localStorage
          try {
            const rawOverrides = localStorage.getItem("spr_admin_student_overrides");
            if (rawOverrides) {
              const overrides = JSON.parse(rawOverrides);
              byAdm.forEach((stu, adm) => {
                if (overrides[adm]) {
                  Object.assign(stu, overrides[adm]);
                }
              });
            }
          } catch (_) {}'''

if "const rawOverrides = localStorage.getItem" not in sb_code:
    sb_code = sb_code.replace("const positions = window.ADMIN_DATA.positions", OVERRIDE_MERGE + "\n\n          const positions = window.ADMIN_DATA.positions")
    print("Added student overrides merge in getSnapshot()!")

sb_path.write_text(sb_code, encoding="utf-8")
print("Saved Houses/admin/supabase-config.js")

# ==============================================================================
# 2. Update Houses/admin/styles.css
# ==============================================================================
css_path = ROOT / "Houses" / "admin" / "styles.css"
css_code = css_path.read_text(encoding="utf-8")

PILL_CSS = '''
/* House Filter Pills for All Students Roster */
.house-filter-pills {
  display: flex;
  gap: 0.45rem;
  overflow-x: auto;
  padding: 0.4rem 0 0.75rem 0;
  scrollbar-width: thin;
}
.btn-house-pill {
  padding: 0.38rem 0.85rem;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 700;
  border: 1.5px solid #cbd5e1;
  background: #ffffff;
  color: var(--text-secondary);
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}
.btn-house-pill:hover {
  border-color: #94a3b8;
  background: #f8fafc;
  color: var(--text-primary);
}
.btn-house-pill.is-active {
  background: #0f172a;
  color: #ffffff;
  border-color: #0f172a;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.15);
}
.btn-house-pill.is-active .pill-badge {
  background: rgba(255, 255, 255, 0.25);
  color: #ffffff;
}
.pill-badge {
  font-size: 0.72rem;
  padding: 0.1rem 0.45rem;
  border-radius: 999px;
  background: #f1f5f9;
  color: #475569;
  font-weight: 800;
}
'''

if ".btn-house-pill" not in css_code:
    css_code += "\n" + PILL_CSS
    css_path.write_text(css_code, encoding="utf-8")
    print("Added pill styles to Houses/admin/styles.css!")

print("Step 1 and 2 completed.")
