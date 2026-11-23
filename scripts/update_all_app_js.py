import shutil

# Update bheeshma/app.js first
bheeshma_app = 'Houses/bheeshma/app.js'
with open(bheeshma_app, 'r', encoding='utf-8') as f:
    text = f.read()

old_block = '''    const mode = await window.ElectionBackend.init();
    const noteEl = document.getElementById("cloud-mode-note");
    if (noteEl) {
      noteEl.hidden = false;
      if (mode === "supabase") {
        noteEl.textContent = "Supabase connected — all votes & photos save strictly to Supabase.";
      } else {
        noteEl.textContent = "Supabase NOT connected — voting is blocked until Supabase is connected in Admin (Connect & Sync Supabase).";
      }
    }'''

new_block = '''    function syncCloudStatusNote(m) {
      const noteEl = document.getElementById("cloud-mode-note");
      if (!noteEl) return;
      noteEl.hidden = false;
      if (m === "supabase") {
        noteEl.className = "cloud-status-note is-connected";
        noteEl.innerHTML = `<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#16a34a;margin-right:4px;"></span> Supabase connected — all votes &amp; photos save strictly to Supabase.`;
      } else {
        noteEl.className = "cloud-status-note is-disconnected";
        noteEl.innerHTML = `<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#dc2626;margin-right:4px;"></span> Supabase NOT connected — connect Supabase in Admin to sync.`;
      }
    }
    const mode = await window.ElectionBackend.init();
    syncCloudStatusNote(mode);
    window.addEventListener("storage", async (e) => {
      if (e.key === "election_spr_2026_sb_cfg_v1" || e.key === "spr_supabase_direct_cfg_v1") {
        if (window.ElectionBackend && typeof window.ElectionBackend.init === "function") {
          window.ElectionBackend._initPromise = null;
          const freshMode = await window.ElectionBackend.init();
          syncCloudStatusNote(freshMode);
        }
      }
    });'''

if old_block in text:
    text = text.replace(old_block, new_block)
    with open(bheeshma_app, 'w', encoding='utf-8') as f:
        f.write(text)
    print("Updated Houses/bheeshma/app.js successfully!")
else:
    print("Warning: old_block not found in Houses/bheeshma/app.js")

# Copy updated bheeshma/app.js to all other houses
for h in ['gurudrona', 'hanuman', 'karna', 'vasistha', 'vishwamithra']:
    target = f'Houses/{h}/app.js'
    shutil.copyfile(bheeshma_app, target)
    print(f"Synced app.js to {target}")

# Update teachers/app.js
teachers_app = 'Houses/teachers/app.js'
with open(teachers_app, 'r', encoding='utf-8') as f:
    t_text = f.read()

t_old = '''    const mode = await window.TeacherBackend.init();
    const noteSpan = document.querySelector(".auth-security-note span");
    if (noteSpan) {
      if (mode === "supabase") {
        noteSpan.textContent = "Supabase connected — all votes & photos save strictly to Supabase.";
      } else {
        noteSpan.textContent = "Supabase NOT connected — connect Supabase in Admin Dashboard to sync.";
      }
    }'''

t_new = '''    function syncTeacherCloudStatus(m) {
      const noteSpan = document.querySelector(".auth-security-note span");
      if (noteSpan) {
        if (m === "supabase") {
          noteSpan.textContent = "Supabase connected — all votes & photos save strictly to Supabase.";
        } else {
          noteSpan.textContent = "Supabase NOT connected — connect Supabase in Admin Dashboard to sync.";
        }
      }
      const noteEl = document.getElementById("cloud-mode-note");
      if (noteEl) {
        noteEl.hidden = false;
        if (m === "supabase") {
          noteEl.className = "cloud-status-note is-connected";
          noteEl.innerHTML = `<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#16a34a;margin-right:4px;"></span> Supabase connected — all votes &amp; photos save strictly to Supabase.`;
        } else {
          noteEl.className = "cloud-status-note is-disconnected";
          noteEl.innerHTML = `<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#dc2626;margin-right:4px;"></span> Supabase NOT connected — connect Supabase in Admin Dashboard to sync.`;
        }
      }
    }
    const mode = await window.TeacherBackend.init();
    syncTeacherCloudStatus(mode);
    window.addEventListener("storage", async (e) => {
      if (e.key === "election_spr_2026_sb_cfg_v1" || e.key === "spr_supabase_direct_cfg_v1") {
        if (window.TeacherBackend && typeof window.TeacherBackend.init === "function") {
          window.TeacherBackend._initPromise = null;
          const freshMode = await window.TeacherBackend.init();
          syncTeacherCloudStatus(freshMode);
        }
      }
    });'''

if t_old in t_text:
    t_text = t_text.replace(t_old, t_new)
    with open(teachers_app, 'w', encoding='utf-8') as f:
        f.write(t_text)
    print("Updated Houses/teachers/app.js successfully!")
else:
    print("Warning: t_old not found in Houses/teachers/app.js")
