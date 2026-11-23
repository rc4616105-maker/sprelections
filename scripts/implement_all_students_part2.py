import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ev_html_path = ROOT / "Houses" / "admin" / "edit-votes.html"
html = ev_html_path.read_text(encoding="utf-8")

# 1. Update sidebar navigation
old_nav = '''      <nav class="sidebar-nav" aria-label="Edit votes navigation">
        <button type="button" id="nav-btn-ballots" class="nav-btn is-active" data-edit-view="ballots">📋 All Cast
          Ballots</button>
      </nav>'''

new_nav = '''      <nav class="sidebar-nav" aria-label="Edit votes navigation">
        <button type="button" id="nav-btn-ballots" class="nav-btn is-active" data-edit-view="ballots">🗳️ All Cast Ballots</button>
        <button type="button" id="nav-btn-students" class="nav-btn" data-edit-view="students">👥 All Students Roster</button>
      </nav>'''

html = html.replace(old_nav, new_nav)

# 2. Shift Add Student / View Added from view-ballots header to view-students
old_ballots_head_actions = '''          <div style="display:flex; gap:0.5rem; flex-wrap:wrap; align-items:center;">
            <button type="button" id="btn-view-added-students" class="btn btn-secondary"
              style="font-weight:700; display:inline-flex; align-items:center; gap:0.45rem; border:1.5px solid #cbd5e1; background:#ffffff;"
              title="View all students who were manually added to the voter roster">
              <span>📋 View Added Students</span>
              <span id="badge-added-count" style="background:#0284c7; color:#fff; font-size:0.75rem; font-weight:800; padding:0.15rem 0.55rem; border-radius:999px;">0</span>
            </button>
            <button type="button" id="btn-open-add-student" class="btn btn-primary"
              style="background:#059669; border-color:#059669; font-weight:700;">➕ Add Student to Voter List</button>
          </div>'''

new_ballots_head_actions = '''          <div style="display:flex; gap:0.5rem; flex-wrap:wrap; align-items:center;">
            <button type="button" id="btn-switch-to-students" class="btn btn-secondary"
              style="font-weight:700; display:inline-flex; align-items:center; gap:0.45rem; border:1.5px solid #cbd5e1; background:#ffffff;"
              title="Switch to All Students Roster to view all house students, edit details, or add new students">
              <span>👥 All Students Roster &amp; Add Student →</span>
            </button>
          </div>'''

html = html.replace(old_ballots_head_actions, new_ballots_head_actions)

# 3. Insert view-students section
VIEW_STUDENTS_SECTION = '''
      <!-- View 2: All Students Master Register View (House-wise) -->
      <section id="view-students" class="panel-card" style="margin-bottom: 2rem;" hidden>
        <div class="panel-head-row">
          <div>
            <h3 class="panel-heading" style="display:flex; align-items:center; gap:0.6rem;">
              <span>All Students Master Register (House-wise)</span>
              <span class="badge badge-primary" id="badge-total-students-count" style="font-size:0.8rem; background:#0f172a; color:#fff;">968 Students</span>
            </h3>
            <p class="panel-caption">Complete official register of all students and faculty across houses. Filter house-wise, search by Voter ID, edit student details, or register missing students.</p>
          </div>
          <div style="display:flex; gap:0.5rem; flex-wrap:wrap; align-items:center;">
            <button type="button" id="btn-view-added-students" class="btn btn-secondary"
              style="font-weight:700; display:inline-flex; align-items:center; gap:0.45rem; border:1.5px solid #cbd5e1; background:#ffffff;"
              title="View all students who were manually added to the voter roster">
              <span>📋 View Added Students</span>
              <span id="badge-added-count" style="background:#0284c7; color:#fff; font-size:0.75rem; font-weight:800; padding:0.15rem 0.55rem; border-radius:999px;">0</span>
            </button>
            <button type="button" id="btn-open-add-student" class="btn btn-primary"
              style="background:#059669; border-color:#059669; font-weight:700;">➕ Add Student to Voter List</button>
          </div>
        </div>

        <!-- House Tabs / Pills -->
        <div class="house-filter-pills" id="house-filter-pills" style="margin-top:0.75rem;">
          <button type="button" class="btn-house-pill is-active" data-house="">
            <span>All Houses</span>
            <span class="pill-badge" id="pill-count-all">0</span>
          </button>
          <button type="button" class="btn-house-pill" data-house="BHEESHMA" style="border-left: 3px solid #ca8a04;">
            <span>🟡 Bheeshma</span>
            <span class="pill-badge" id="pill-count-bheeshma">0</span>
          </button>
          <button type="button" class="btn-house-pill" data-house="GURUDRONA" style="border-left: 3px solid #2563eb;">
            <span>🔵 Gurudrona</span>
            <span class="pill-badge" id="pill-count-gurudrona">0</span>
          </button>
          <button type="button" class="btn-house-pill" data-house="HANUMAN" style="border-left: 3px solid #ea580c;">
            <span>🟠 Hanuman</span>
            <span class="pill-badge" id="pill-count-hanuman">0</span>
          </button>
          <button type="button" class="btn-house-pill" data-house="KARNA" style="border-left: 3px solid #dc2626;">
            <span>🔴 Karna</span>
            <span class="pill-badge" id="pill-count-karna">0</span>
          </button>
          <button type="button" class="btn-house-pill" data-house="VASISTHA" style="border-left: 3px solid #db2777;">
            <span>🌸 Vasistha</span>
            <span class="pill-badge" id="pill-count-vasistha">0</span>
          </button>
          <button type="button" class="btn-house-pill" data-house="VISHWAMITHRA" style="border-left: 3px solid #7c3aed;">
            <span>🟣 Vishwamithra</span>
            <span class="pill-badge" id="pill-count-vishwamithra">0</span>
          </button>
          <button type="button" class="btn-house-pill" data-house="ALL" style="border-left: 3px solid #475569;">
            <span>👔 Faculty</span>
            <span class="pill-badge" id="pill-count-faculty">0</span>
          </button>
        </div>

        <!-- Filters Bar for Students Master List -->
        <div class="filters-bar" style="margin-top: 0.5rem; margin-bottom: 1.25rem;">
          <input id="stu-master-search" type="search" class="form-control"
            placeholder="Search Voter ID, Student Name, Father's Name..." />
          <select id="stu-master-house-filter" class="form-control" aria-label="Filter by House">
            <option value="">All Houses</option>
            <option value="BHEESHMA">Bheeshma House</option>
            <option value="GURUDRONA">Gurudrona House</option>
            <option value="HANUMAN">Hanuman House</option>
            <option value="KARNA">Karna House</option>
            <option value="VASISTHA">Vasistha House</option>
            <option value="VISHWAMITHRA">Vishwamithra House</option>
            <option value="ALL">All Houses / Faculty</option>
          </select>
          <select id="stu-master-class-filter" class="form-control" aria-label="Filter by Class">
            <option value="">All Classes</option>
            <option value="10">Class 10</option>
            <option value="9">Class 9</option>
            <option value="8">Class 8</option>
            <option value="7">Class 7</option>
            <option value="Staff">Faculty / Staff</option>
          </select>
          <select id="stu-master-section-filter" class="form-control" aria-label="Filter by Section">
            <option value="">All Sections</option>
          </select>
          <select id="stu-master-status-filter" class="form-control" aria-label="Filter by Status">
            <option value="">All Voting Statuses</option>
            <option value="voted">✓ Voted</option>
            <option value="not_voted">Pending (Not Voted)</option>
            <option value="added">📋 Manually Added</option>
          </select>
        </div>

        <div class="table-container" style="margin-bottom: 0;">
          <table class="data-table">
            <thead>
              <tr>
                <th style="width: 12%;">Voter ID</th>
                <th style="width: 25%;">Student Details</th>
                <th style="width: 10%;">Class</th>
                <th style="width: 18%;">Section</th>
                <th style="width: 15%;">House</th>
                <th style="width: 10%;">Status</th>
                <th style="width: 10%; min-width: 130px;">Action</th>
              </tr>
            </thead>
            <tbody id="stu-master-tbody"></tbody>
          </table>
          <div id="stu-master-empty" class="empty-state" hidden>
            <div style="font-size: 1.6rem; margin-bottom: 0.35rem;">👥</div>
            <strong style="color: var(--text-primary); font-size: 0.95rem; display: block; margin-bottom: 0.2rem;">No Students Found</strong>
            <span style="color: var(--text-muted); font-size: 0.82rem;">No students match the current filters.</span>
          </div>
        </div>
      </section>
'''

if 'id="view-students"' not in html:
    html = html.replace('</section>\n    </main>', '</section>\n' + VIEW_STUDENTS_SECTION + '    </main>')
    print("Inserted view-students section!")

# 4. Insert edit-student-modal
EDIT_STUDENT_MODAL = '''
  <!-- Edit / Change Student Details Modal -->
  <div id="edit-student-modal" class="modal-overlay" hidden>
    <div class="modal-card" style="max-width: 560px;" role="dialog" aria-modal="true"
      aria-labelledby="edit-student-modal-title">
      <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.75rem;">
        <div>
          <h3 id="edit-student-modal-title" class="modal-title" style="margin:0;">✏️ Change Student Details</h3>
          <p class="modal-desc" style="margin-top:0.35rem; margin-bottom:0;">Update student name, class, section, or house assignment. Changes update in real time.</p>
        </div>
        <button type="button" id="edit-student-modal-close-x" class="btn btn-secondary" style="font-size:1.1rem; padding:0.2rem 0.6rem; line-height:1;" title="Close">✕</button>
      </div>

      <form id="edit-student-form" onsubmit="return false;">
        <input type="hidden" id="edit-student-adm" />

        <div style="display:flex; flex-direction:column; gap:0.85rem; margin-top:0.85rem;">
          <!-- Voter ID Badge -->
          <div style="display:flex; align-items:center; justify-content:space-between; background:#f1f5f9; border:1px solid #cbd5e1; border-radius:8px; padding:0.6rem 0.85rem;">
            <div>
              <span style="font-size:0.75rem; text-transform:uppercase; font-weight:800; color:#64748b;">Voter ID</span>
              <div id="edit-student-voter-id-display" class="mono" style="font-size:1.15rem; font-weight:800; color:#0369a1; letter-spacing:0.08em;">--</div>
            </div>
            <span id="edit-student-voted-pill" class="badge badge-muted" style="font-size:0.75rem;">Not Voted</span>
          </div>

          <div class="form-group">
            <label class="form-label" for="edit-student-name"
              style="font-weight:700; font-size:0.82rem; text-transform:uppercase;">Student Full Name *</label>
            <input type="text" id="edit-student-name" class="form-control" required autocomplete="off" />
          </div>

          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:0.75rem;">
            <div class="form-group">
              <label class="form-label" for="edit-student-father"
                style="font-weight:700; font-size:0.82rem; text-transform:uppercase;">Father's Name</label>
              <input type="text" id="edit-student-father" class="form-control" autocomplete="off" />
            </div>

            <div class="form-group">
              <label class="form-label" for="edit-student-gender"
                style="font-weight:700; font-size:0.82rem; text-transform:uppercase;">Gender *</label>
              <select id="edit-student-gender" class="form-control" required>
                <option value="Boy">Boy</option>
                <option value="Girl">Girl</option>
              </select>
            </div>
          </div>

          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:0.75rem;">
            <div class="form-group">
              <label class="form-label" for="edit-student-class"
                style="font-weight:700; font-size:0.82rem; text-transform:uppercase;">Class *</label>
              <select id="edit-student-class" class="form-control" required>
                <option value="10">Class 10</option>
                <option value="9">Class 9</option>
                <option value="8">Class 8</option>
                <option value="7">Class 7</option>
                <option value="Staff">Faculty / Staff</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label" for="edit-student-section"
                style="font-weight:700; font-size:0.82rem; text-transform:uppercase;">Section *</label>
              <select id="edit-student-section" class="form-control" required>
                <!-- Populated dynamically based on Class -->
              </select>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label" for="edit-student-house"
              style="font-weight:700; font-size:0.82rem; text-transform:uppercase;">House Assignment *</label>
            <select id="edit-student-house" class="form-control" required>
              <option value="BHEESHMA">Bheeshma House</option>
              <option value="GURUDRONA">Gurudrona House</option>
              <option value="HANUMAN">Hanuman House</option>
              <option value="KARNA">Karna House</option>
              <option value="VASISTHA">Vasistha House</option>
              <option value="VISHWAMITHRA">Vishwamithra House</option>
              <option value="ALL">ALL House (Faculty)</option>
            </select>
          </div>
        </div>

        <p id="edit-student-error" class="stat-note" style="color: #b91c1c; margin-top: 0.65rem;" hidden></p>
        <p id="edit-student-success" class="stat-note" style="color: #047857; margin-top: 0.65rem; font-weight: 700;" hidden></p>

        <div class="modal-actions" style="margin-top: 1.25rem;">
          <button type="button" id="edit-student-modal-close" class="btn btn-secondary">Cancel</button>
          <button type="submit" id="edit-student-submit-btn" class="btn btn-primary"
            style="background:#0284c7; border-color:#0284c7; font-weight:700;">💾 Save Changes</button>
        </div>
      </form>
    </div>
  </div>
'''

if 'id="edit-student-modal"' not in html:
    html = html.replace('  <!-- View Added Students Modal -->', EDIT_STUDENT_MODAL + '\n  <!-- View Added Students Modal -->')
    print("Inserted edit-student-modal!")

html = re.sub(r'(\./edit-votes\.js\?v=)[^"]*', r'\g<1>20261122n', html)
html = re.sub(r'(\./supabase-config\.js\?v=)[^"]*', r'\g<1>20261122n', html)
html = re.sub(r'(\./styles\.css\?v=)[^"]*', r'\g<1>20261122n', html)

ev_html_path.write_text(html, encoding="utf-8")
print("Saved Houses/admin/edit-votes.html successfully!")
