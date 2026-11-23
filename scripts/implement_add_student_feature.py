import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ==============================================================================
# 1. Update Houses/admin/edit-votes.html
# ==============================================================================
html_path = ROOT / "Houses" / "admin" / "edit-votes.html"
html_content = html_path.read_text(encoding="utf-8")

# Replace header button
old_btn = r'<button type="button" id="btn-open-add-candidate"[^>]*>.*?</button>'
new_btn = """<button type="button" id="btn-open-add-student" class="btn btn-primary"
              style="background:#059669; border-color:#059669; font-weight:700;">➕ Add Student to Voter List</button>"""
html_content = re.sub(old_btn, new_btn, html_content)

# Replace the modal markup
modal_regex = r'<!-- Add Candidate to Participate Modal -->[\s\S]*?</div>\s*</div>\s*(?=<script)'

NEW_MODAL = """<!-- Add Student to Voter List Modal -->
  <div id="add-student-modal" class="modal-overlay" hidden>
    <div class="modal-card" style="max-width: 560px;" role="dialog" aria-modal="true"
      aria-labelledby="add-student-modal-title">
      <h3 id="add-student-modal-title" class="modal-title">➕ Add Missing Student to Voter List</h3>
      <p class="modal-desc">Register a missing student into the master election roster with an unidentifiable 6-character random Voter ID so they can cast their ballot.</p>

      <form id="add-student-form" onsubmit="return false;">
        <div style="display:flex; flex-direction:column; gap:0.85rem; margin-top:1rem;">
          <div class="form-group">
            <label class="form-label" for="new-student-name"
              style="font-weight:700; font-size:0.82rem; text-transform:uppercase;">Student Full Name *</label>
            <input type="text" id="new-student-name" class="form-control"
              placeholder="e.g. Rahul Sharma" required autocomplete="off" />
          </div>

          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:0.75rem;">
            <div class="form-group">
              <label class="form-label" for="new-student-father"
                style="font-weight:700; font-size:0.82rem; text-transform:uppercase;">Father's Name</label>
              <input type="text" id="new-student-father" class="form-control"
                placeholder="e.g. M. Sharma" autocomplete="off" />
            </div>

            <div class="form-group">
              <label class="form-label" for="new-student-gender"
                style="font-weight:700; font-size:0.82rem; text-transform:uppercase;">Gender *</label>
              <select id="new-student-gender" class="form-control" required>
                <option value="Boy">Boy</option>
                <option value="Girl">Girl</option>
              </select>
            </div>
          </div>

          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:0.75rem;">
            <div class="form-group">
              <label class="form-label" for="new-student-class"
                style="font-weight:700; font-size:0.82rem; text-transform:uppercase;">Class *</label>
              <select id="new-student-class" class="form-control" required>
                <option value="10">Class 10</option>
                <option value="9">Class 9</option>
                <option value="8">Class 8</option>
                <option value="7">Class 7</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label" for="new-student-section"
                style="font-weight:700; font-size:0.82rem; text-transform:uppercase;">Section *</label>
              <select id="new-student-section" class="form-control" required>
                <!-- Populated dynamically based on Class selection -->
              </select>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label" for="new-student-house"
              style="font-weight:700; font-size:0.82rem; text-transform:uppercase;">House Assignment *</label>
            <select id="new-student-house" class="form-control" required>
              <option value="BHEESHMA">Bheeshma House</option>
              <option value="GURUDRONA">Gurudrona House</option>
              <option value="HANUMAN">Hanuman House</option>
              <option value="KARNA">Karna House</option>
              <option value="VASISTHA">Vasistha House</option>
              <option value="VISHWAMITHRA">Vishwamithra House</option>
            </select>
          </div>

          <!-- 6-Character Random Voter ID Generator -->
          <div class="form-group" style="background:#f8fafc; border:1.5px solid #cbd5e1; border-radius:10px; padding:0.85rem;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
              <label class="form-label" for="new-student-voter-id"
                style="font-weight:800; font-size:0.82rem; text-transform:uppercase; color:#0f172a; margin:0;">
                Generated Voter ID (6-Char Random Code) *
              </label>
              <button type="button" id="btn-reroll-code" class="btn btn-secondary"
                style="font-size:0.75rem; padding:0.25rem 0.6rem; font-weight:700; display:inline-flex; align-items:center; gap:0.3rem;"
                title="Generate another completely random non-sequential voter code">
                🎲 Re-Roll Code
              </button>
            </div>

            <div style="display:flex; gap:0.5rem; align-items:center;">
              <input type="text" id="new-student-voter-id" class="form-control"
                style="font-family:'JetBrains Mono',monospace; font-size:1.15rem; font-weight:800; letter-spacing:0.12em; text-transform:uppercase; color:#0369a1; background:#ffffff;"
                maxlength="6" required autocomplete="off" />
              <span id="code-status-pill" style="font-size:0.72rem; font-weight:700; padding:0.3rem 0.6rem; border-radius:6px; background:#dcfce7; color:#15803d; white-space:nowrap;">
                ✓ Unique (No Repetition)
              </span>
            </div>

            <p style="font-size:0.72rem; color:#64748b; margin-top:0.4rem; margin-bottom:0; line-height:1.3;">
              Prefix (<strong id="code-prefix-hint">1C</strong>) matches Class &amp; Section · 4 non-sequential random digits · Cannot be identified or sequenced.
            </p>
          </div>
        </div>

        <p id="add-student-error" class="stat-note" style="color: #b91c1c; margin-top: 0.65rem;" hidden></p>
        <p id="add-student-success" class="stat-note" style="color: #047857; margin-top: 0.65rem; font-weight: 700;" hidden></p>

        <div class="modal-actions" style="margin-top: 1.25rem;">
          <button type="button" id="add-student-modal-close" class="btn btn-secondary">Close</button>
          <button type="submit" id="add-student-submit-btn" class="btn btn-primary"
            style="background:#059669; border-color:#059669; font-weight:700;">➕ Save &amp; Register Student</button>
        </div>
      </form>
    </div>
  </div>

  """

html_content = re.sub(modal_regex, NEW_MODAL, html_content)
html_path.write_text(html_content, encoding="utf-8")
print("Updated Houses/admin/edit-votes.html successfully!")

# ==============================================================================
# 2. Update Houses/admin/supabase-config.js (add addStudent method)
# ==============================================================================
sb_admin_path = ROOT / "Houses" / "admin" / "supabase-config.js"
sb_admin_code = sb_admin_path.read_text(encoding="utf-8")

ADD_STUDENT_METHOD = """
    async addStudent({ fullName, fatherName, gender, className, section, houseCode, admissionNo }) {
      const cleanName = String(fullName || "").trim();
      if (!cleanName) throw new Error("Student full name is required.");
      const cleanAdm = String(admissionNo || "").trim().toUpperCase();
      if (!cleanAdm) throw new Error("Voter ID is required.");
      if (cleanAdm.length !== 6) throw new Error("Voter ID must be exactly 6 characters.");
      const cleanHouse = String(houseCode || "BHEESHMA").toUpperCase().trim();
      const cleanClass = String(className || "10").trim();
      const cleanSec = String(section || "").trim();
      const cleanGender = String(gender || "Boy").trim();
      const cleanFather = String(fatherName || "").trim();

      if (!window.ADMIN_DATA.students) window.ADMIN_DATA.students = [];
      const duplicate = window.ADMIN_DATA.students.find(
        (s) => String(s.admissionNo || "").toUpperCase() === cleanAdm
      );
      if (duplicate) {
        throw new Error(`Voter ID "${cleanAdm}" already exists for ${duplicate.fullName} (${duplicate.className}-${duplicate.section}). Please click Re-Roll.`);
      }

      const houseNameMap = {
        BHEESHMA: "Bheeshma House",
        GURUDRONA: "Gurudrona House",
        HANUMAN: "Hanuman House",
        KARNA: "Karna House",
        VASISTHA: "Vasistha House",
        VISHWAMITHRA: "Vishwamithra House",
        CENTRAL: "School Cabinet",
      };
      const houseName = houseNameMap[cleanHouse] || cleanHouse;
      const nowIso = new Date().toISOString();

      const newStudentDoc = {
        admission_no: cleanAdm,
        full_name: cleanName,
        father_name: cleanFather,
        gender: cleanGender,
        class_name: cleanClass,
        section: cleanSec,
        house_code: cleanHouse,
        house_name: houseName,
        final_status: "Not Voted",
        is_active: true,
        created_at: nowIso,
      };

      if (this.mode === "supabase") {
        await sbRest("POST", "/rest/v1/voters", [newStudentDoc], "resolution=merge-duplicates,return=representation");
      }

      const studentObj = {
        admissionNo: cleanAdm,
        fullName: cleanName,
        fatherName: cleanFather,
        gender: cleanGender,
        className: cleanClass,
        section: cleanSec,
        houseCode: cleanHouse,
        isActive: true,
        isCandidate: false,
        positionName: null,
        photoUrl: cleanGender === "Girl" ? "../assets/candidates/girl_demo.jpg" : "../assets/candidates/student_demo.jpg",
      };

      window.ADMIN_DATA.students.push(studentObj);

      try {
        const raw = localStorage.getItem("spr_admin_custom_students");
        const customList = raw ? JSON.parse(raw) : [];
        customList.push(studentObj);
        localStorage.setItem("spr_admin_custom_students", JSON.stringify(customList));
      } catch (e) {
        console.warn("Could not save to localStorage:", e);
      }

      const actorName = (typeof sessionStorage !== "undefined" && (sessionStorage.getItem("spr_admin_email") || sessionStorage.getItem("spr_admin_name"))) || "rc4616105@gmail.com";
      if (this.mode === "supabase") {
        await sbRest("POST", "/rest/v1/audit_logs", {
          id: `AUD-${Date.now().toString(36).toUpperCase()}`,
          action: "STUDENT_ADDED",
          ballot_id: null,
          admission_no: cleanAdm,
          student_name: cleanName,
          house_code: cleanHouse,
          reason: `Added missing student "${cleanName}" (${cleanClass}-${cleanSec}, ${houseName}) with Voter ID ${cleanAdm}`,
          actor: actorName,
          created_at: nowIso,
        }).catch(() => {});
      }

      if (channel) channel.postMessage({ type: "store_updated", at: Date.now() });
      return { ok: true, student: studentObj };
    },
"""

if "async addStudent(" not in sb_admin_code:
    sb_admin_code = sb_admin_code.replace("async addCandidate(", ADD_STUDENT_METHOD.strip() + "\n\n    async addCandidate(")
    sb_admin_path.write_text(sb_admin_code, encoding="utf-8")
    print("Added addStudent method to Houses/admin/supabase-config.js!")

# ==============================================================================
# 3. Update Houses/admin/edit-votes.js (Modal logic and random code generator)
# ==============================================================================
ev_path = ROOT / "Houses" / "admin" / "edit-votes.js"
ev_code = ev_path.read_text(encoding="utf-8")

NEW_STUDENT_MODAL_LOGIC = """  // --- Add Missing Student to Voter List Modal Logic ---
  const btnOpenAddStudent = document.getElementById("btn-open-add-student") || document.getElementById("btn-open-add-candidate");
  const addStudentModal = document.getElementById("add-student-modal") || document.getElementById("add-candidate-modal");
  const addStudentForm = document.getElementById("add-student-form") || document.getElementById("add-candidate-form");
  const addStudentClose = document.getElementById("add-student-modal-close") || document.getElementById("add-cand-modal-close");
  const addStudentSubmitBtn = document.getElementById("add-student-submit-btn") || document.getElementById("add-cand-submit-btn");
  const studentNameInput = document.getElementById("new-student-name") || document.getElementById("new-cand-name");
  const studentFatherInput = document.getElementById("new-student-father");
  const studentGenderSelect = document.getElementById("new-student-gender");
  const studentClassSelect = document.getElementById("new-student-class") || document.getElementById("new-cand-class");
  const studentSectionSelect = document.getElementById("new-student-section");
  const studentHouseSelect = document.getElementById("new-student-house") || document.getElementById("new-cand-house");
  const studentVoterIdInput = document.getElementById("new-student-voter-id") || document.getElementById("new-cand-adm");
  const btnRerollCode = document.getElementById("btn-reroll-code");
  const codeStatusPill = document.getElementById("code-status-pill");
  const codePrefixHint = document.getElementById("code-prefix-hint");
  const addStudentError = document.getElementById("add-student-error") || document.getElementById("add-cand-error");
  const addStudentSuccess = document.getElementById("add-student-success") || document.getElementById("add-cand-success");

  const SECTIONS_BY_CLASS = {
    "10": [
      { name: "Chatrapathi Shivaji (10-CS)", prefix: "1C" },
      { name: "Ashoka Chakravarthi (10-AC)", prefix: "1A" },
      { name: "Jhansi Laxmi Bai (10-JL)", prefix: "1J" },
      { name: "Maha Raana Pratap (10-MP)", prefix: "1M" },
    ],
    "9": [
      { name: "APJ Abdul Kalam (9-AK)", prefix: "9K" },
      { name: "Aryabhatta (9-AB)", prefix: "9A" },
      { name: "Kalpana Chawla (9-KC)", prefix: "9C" },
      { name: "Satish Dhawan (9-SD)", prefix: "9D" },
      { name: "Vikram Sarabhai (9-VS)", prefix: "9S" },
    ],
    "8": [
      { name: "Chanakya (8-CH)", prefix: "8C" },
      { name: "Dayananda Saraswathi (8-DS)", prefix: "8D" },
      { name: "Hedgewar (8-HW)", prefix: "8H" },
      { name: "Sri Guruji (8-SG)", prefix: "8G" },
      { name: "Swamy Vivekananda (8-SV)", prefix: "8V" },
    ],
    "7": [
      { name: "Alluri Sitaramaraju (7-AS)", prefix: "7A" },
      { name: "Bhagath Singh (7-BS)", prefix: "7B" },
      { name: "Chandra Shekar Azad (7-CA)", prefix: "7C" },
      { name: "Rajguru (7-RG)", prefix: "7R" },
      { name: "Subhash Chandra Bose (7-SB)", prefix: "7S" },
    ],
  };

  function getActivePrefix() {
    const c = studentClassSelect ? studentClassSelect.value : "10";
    if (studentSectionSelect) {
      const opt = studentSectionSelect.options[studentSectionSelect.selectedIndex];
      if (opt && opt.dataset.prefix) return opt.dataset.prefix.toUpperCase();
    }
    const list = SECTIONS_BY_CLASS[c] || [];
    return (list[0] && list[0].prefix) || (c.charAt(0) + "S");
  }

  function getAllExistingVoterIds() {
    const set = new Set();
    const students = latestSnapshot?.students || window.ADMIN_DATA?.students || [];
    students.forEach((s) => {
      if (s.admissionNo) set.add(String(s.admissionNo).trim().toUpperCase());
    });
    const ballots = latestSnapshot?.ballots || [];
    ballots.forEach((b) => {
      if (b.admissionNo) set.add(String(b.admissionNo).trim().toUpperCase());
    });
    try {
      const raw = localStorage.getItem("spr_admin_custom_students");
      if (raw) {
        JSON.parse(raw).forEach((cs) => {
          if (cs.admissionNo) set.add(String(cs.admissionNo).trim().toUpperCase());
        });
      }
    } catch (_) {}
    return set;
  }

  function generateUnique6CharVoterId() {
    const prefix = getActivePrefix();
    const existing = getAllExistingVoterIds();
    let attempts = 0;
    while (attempts < 3000) {
      attempts++;
      // Cryptographically secure 4 random digits (1000 - 9999)
      const arr = new Uint32Array(1);
      (window.crypto || window.msCrypto).getRandomValues(arr);
      const randNum = 1000 + (arr[0] % 9000);
      const numStr = String(randNum);

      // Rule out repeating digits (e.g. 1111, 2222)
      if (/^(\\d)\\1{3}$/.test(numStr)) continue;

      // Rule out simple ascending/descending sequences
      const sequences = ["1234", "2345", "3456", "4567", "5678", "6789", "4321", "5432", "6543", "7654", "8765", "9876", "0123"];
      if (sequences.includes(numStr)) continue;

      const code = `${prefix}${numStr}`;
      if (!existing.has(code)) {
        return code;
      }
    }
    return `${prefix}${Math.floor(1000 + Math.random() * 9000)}`;
  }

  function refreshVoterCode() {
    if (!studentVoterIdInput) return;
    const newCode = generateUnique6CharVoterId();
    studentVoterIdInput.value = newCode;
    if (codePrefixHint) codePrefixHint.textContent = getActivePrefix();
    if (codeStatusPill) {
      codeStatusPill.textContent = "✓ Unique (No Repetition)";
      codeStatusPill.style.background = "#dcfce7";
      codeStatusPill.style.color = "#15803d";
    }
  }

  function populateSectionOptionsForClass() {
    if (!studentClassSelect || !studentSectionSelect) return;
    const c = studentClassSelect.value;
    const sections = SECTIONS_BY_CLASS[c] || [
      { name: "Section A", prefix: c.charAt(0) + "A" },
      { name: "Section B", prefix: c.charAt(0) + "B" },
    ];
    studentSectionSelect.innerHTML = "";
    sections.forEach((sec) => {
      const opt = document.createElement("option");
      opt.value = sec.name;
      opt.textContent = `${sec.name} · [Code: ${sec.prefix}XXXX]`;
      opt.dataset.prefix = sec.prefix;
      studentSectionSelect.appendChild(opt);
    });
    refreshVoterCode();
  }

  if (studentClassSelect) {
    studentClassSelect.addEventListener("change", populateSectionOptionsForClass);
  }
  if (studentSectionSelect) {
    studentSectionSelect.addEventListener("change", refreshVoterCode);
  }
  if (btnRerollCode) {
    btnRerollCode.addEventListener("click", () => {
      refreshVoterCode();
      if (studentVoterIdInput) {
        studentVoterIdInput.style.transform = "scale(1.04)";
        setTimeout(() => { studentVoterIdInput.style.transform = "scale(1)"; }, 150);
      }
    });
  }

  if (studentVoterIdInput) {
    studentVoterIdInput.addEventListener("input", () => {
      const val = studentVoterIdInput.value.trim().toUpperCase();
      studentVoterIdInput.value = val;
      const existing = getAllExistingVoterIds();
      if (val.length === 6 && !existing.has(val)) {
        if (codeStatusPill) {
          codeStatusPill.textContent = "✓ Unique";
          codeStatusPill.style.background = "#dcfce7";
          codeStatusPill.style.color = "#15803d";
        }
      } else if (existing.has(val)) {
        if (codeStatusPill) {
          codeStatusPill.textContent = "⚠ Already in Use";
          codeStatusPill.style.background = "#fee2e2";
          codeStatusPill.style.color = "#b91c1c";
        }
      } else {
        if (codeStatusPill) {
          codeStatusPill.textContent = `${val.length}/6 chars`;
          codeStatusPill.style.background = "#f1f5f9";
          codeStatusPill.style.color = "#475569";
        }
      }
    });
  }

  if (btnOpenAddStudent && addStudentModal) {
    btnOpenAddStudent.addEventListener("click", () => {
      if (addStudentError) addStudentError.hidden = true;
      if (addStudentSuccess) addStudentSuccess.hidden = true;
      if (studentNameInput) studentNameInput.value = "";
      if (studentFatherInput) studentFatherInput.value = "";
      populateSectionOptionsForClass();
      addStudentModal.hidden = false;
      setTimeout(() => studentNameInput && studentNameInput.focus(), 60);
    });
  }

  if (addStudentClose && addStudentModal) {
    addStudentClose.addEventListener("click", () => {
      addStudentModal.hidden = true;
    });
  }

  if (addStudentForm) {
    addStudentForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (addStudentError) addStudentError.hidden = true;
      if (addStudentSuccess) addStudentSuccess.hidden = true;

      const fullName = (studentNameInput ? studentNameInput.value : "").trim();
      if (!fullName) {
        addStudentError.textContent = "Please enter the student's full name.";
        addStudentError.hidden = false;
        return;
      }
      const fatherName = (studentFatherInput ? studentFatherInput.value : "").trim();
      const gender = (studentGenderSelect ? studentGenderSelect.value : "Boy").trim();
      const className = (studentClassSelect ? studentClassSelect.value : "10").trim();
      const section = (studentSectionSelect ? studentSectionSelect.value : "").trim();
      const houseCode = (studentHouseSelect ? studentHouseSelect.value : "BHEESHMA").trim();
      const admissionNo = (studentVoterIdInput ? studentVoterIdInput.value : "").trim().toUpperCase();

      if (admissionNo.length !== 6) {
        addStudentError.textContent = "Voter ID must be exactly 6 characters.";
        addStudentError.hidden = false;
        return;
      }

      const houseNameMap = {
        BHEESHMA: "Bheeshma House",
        GURUDRONA: "Gurudrona House",
        HANUMAN: "Hanuman House",
        KARNA: "Karna House",
        VASISTHA: "Vasistha House",
        VISHWAMITHRA: "Vishwamithra House",
      };

      try {
        if (addStudentSubmitBtn) {
          addStudentSubmitBtn.disabled = true;
          addStudentSubmitBtn.textContent = "Registering Student... ⏳";
        }

        await window.AdminBackend.addStudent({
          fullName,
          fatherName,
          gender,
          className,
          section,
          houseCode,
          admissionNo,
        });

        // Also add to latestSnapshot so table and KPI updates immediately
        if (latestSnapshot && latestSnapshot.students) {
          const newStudentObj = {
            admissionNo,
            fullName,
            fatherName,
            gender,
            className,
            section,
            houseCode,
            isActive: true,
            isCandidate: false,
            photoUrl: gender === "Girl" ? "../assets/candidates/girl_demo.jpg" : "../assets/candidates/student_demo.jpg",
          };
          if (!latestSnapshot.students.some((s) => s.admissionNo === admissionNo)) {
            latestSnapshot.students.push(newStudentObj);
          }
        }

        addStudentSuccess.textContent = `Student "${fullName}" registered successfully with Voter ID: ${admissionNo} in ${houseNameMap[houseCode]}! 🎉`;
        addStudentSuccess.hidden = false;

        await refreshAll();

        setTimeout(() => {
          addStudentModal.hidden = true;
          addStudentSuccess.hidden = true;
        }, 1600);
      } catch (err) {
        addStudentError.textContent = err.message || "Failed to add student.";
        addStudentError.hidden = false;
      } finally {
        if (addStudentSubmitBtn) {
          addStudentSubmitBtn.disabled = false;
          addStudentSubmitBtn.textContent = "➕ Save & Register Student";
        }
      }
    });
  }"""

# Replace lines from `// --- Add Candidate to Participate Modal Logic ---` to `async function boot() {`
pattern = r'// --- Add Candidate to Participate Modal Logic ---[\s\S]*?(?=async function boot\(\) \{)'
ev_code = re.sub(pattern, lambda m: NEW_STUDENT_MODAL_LOGIC.strip() + "\n\n  ", ev_code)

# Ensure custom students from localStorage are loaded at boot
boot_load_code = """
    // Load custom registered students from localStorage into ADMIN_DATA
    try {
      const rawCustom = localStorage.getItem("spr_admin_custom_students");
      if (rawCustom) {
        const customList = JSON.parse(rawCustom);
        if (!window.ADMIN_DATA.students) window.ADMIN_DATA.students = [];
        customList.forEach((cs) => {
          if (!window.ADMIN_DATA.students.some((s) => s.admissionNo === cs.admissionNo)) {
            window.ADMIN_DATA.students.push(cs);
          }
        });
      }
    } catch (_) {}
"""
if "spr_admin_custom_students" not in ev_code:
    ev_code = ev_code.replace("async function boot() {", "async function boot() {" + boot_load_code)

ev_path.write_text(ev_code, encoding="utf-8")
print("Updated Houses/admin/edit-votes.js successfully!")

# ==============================================================================
# 4. Update Houses/*/supabase-config.js (Kiosks check custom students & Supabase)
# ==============================================================================
HOUSES = ["bheeshma", "gurudrona", "hanuman", "karna", "vasistha", "vishwamithra", "central", "teachers"]

CHECK_SNIPPET = """      // Step 1: Check Admission No. against the student roster or demo accounts
      let localMatch = DEMO_ACCOUNTS[cleanId] ? { ...DEMO_ACCOUNTS[cleanId] } : (allStudents.find((s) => s.admissionNo === cleanId) || null);
      if (!localMatch) {
        try {
          const rawCustom = localStorage.getItem("spr_admin_custom_students");
          if (rawCustom) {
            const customList = JSON.parse(rawCustom);
            const found = customList.find((s) => String(s.admissionNo).toUpperCase() === cleanId.toUpperCase());
            if (found) localMatch = { ...found };
          }
        } catch (_) {}
      }
      if (!localMatch && this.mode === "supabase") {
        try {
          const rows = await sbFetchAll(`voters?admission_no=eq.${encodeURIComponent(cleanId)}`);
          if (rows && rows.length > 0) {
            const r = rows[0];
            localMatch = {
              admissionNo: r.admission_no,
              fullName: r.full_name,
              fatherName: r.father_name || "",
              gender: r.gender || "Boy",
              className: r.class_name,
              section: r.section,
              houseCode: r.house_code,
              isActive: r.is_active !== false,
              photoUrl: r.photo_url || (r.gender === "Girl" ? "../assets/candidates/girl_demo.jpg" : "../assets/candidates/student_demo.jpg"),
            };
          }
        } catch (_) {}
      }"""

old_step1_pat = r'// Step 1: Check Admission No\. against the student roster or demo accounts\s+let localMatch = DEMO_ACCOUNTS\[cleanId\] \? \{ \.\.\.DEMO_ACCOUNTS\[cleanId\] \} : \(allStudents\.find\(\(s\) => s\.admissionNo === cleanId\) \|\| null\);'

for h in HOUSES:
    kiosk_sb = ROOT / "Houses" / h / "supabase-config.js"
    if kiosk_sb.exists():
        txt = kiosk_sb.read_text(encoding="utf-8")
        if re.search(old_step1_pat, txt):
            txt = re.sub(old_step1_pat, CHECK_SNIPPET, txt)
            kiosk_sb.write_text(txt, encoding="utf-8")
            print(f"Updated kiosk verifyStudent in Houses/{h}/supabase-config.js")

# Bump cachebusters in edit-votes.html
ev_html = ROOT / "Houses" / "admin" / "edit-votes.html"
txt = ev_html.read_text(encoding="utf-8")
txt = re.sub(r'(\./edit-votes\.js\?v=)[^"]*', r'\g<1>20261122e', txt)
txt = re.sub(r'(\./supabase-config\.js\?v=)[^"]*', r'\g<1>20261122e', txt)
ev_html.write_text(txt, encoding="utf-8")
print("Bumped cachebusters in edit-votes.html to v=20261122e")

print("\nAll Add Student features implemented and synchronized!")
