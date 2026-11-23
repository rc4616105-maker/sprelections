with open('Houses/admin/edit-votes.js', 'r', encoding='utf-8') as f:
    code = f.read()

old_block = """    stuEl.stuTbody.innerHTML = "";
    if (stuEl.stuEmpty) {
      stuEl.stuEmpty.hidden = filtered.length > 0;
    }

    filtered.forEach((s) => {
      const sAdmUp = String(s.admissionNo).toUpperCase();
      const vId = getDisplayVoterId(s);
      const hasVoted = acceptedAdmSet.has(sAdmUp);
      const isCustom = s.isCustom || customMap.has(sAdmUp);
      const house = houseMap[s.houseCode] || { name: s.houseCode || "All Houses", accentText: "#141413" };

      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td class="mono" style="font-weight:800; color:#0369a1; font-size:1.02rem;">
          ${vId !== "--" ? `<span>${vId}</span>` : `<span style="color:var(--text-muted); font-weight:700;">--</span>`}
          ${vId !== "--" ? `<button type="button" class="btn btn-secondary btn-copy-adm-row" data-adm="${vId}" style="font-size:0.68rem; padding:0.15rem 0.35rem; margin-left:0.3rem;" title="Copy Voter ID">📋</button>` : ""}
        </td>
        <td>
          <div style="font-weight:700; color:var(--text-primary); font-size:0.95rem;">${s.fullName}</div>
          <div class="stat-note" style="color:var(--text-muted); font-size:0.78rem;">
            ${s.gender ? `Gender: ${s.gender}` : ""}
            ${isCustom ? ` · <span style="color:#059669; font-weight:700;">[Added]</span>` : ""}
          </div>
        </td>
        <td><strong style="font-size:0.88rem;">${s.className ? `Class ${s.className}` : (s.isStaff ? "Faculty" : "--")}</strong></td>
        <td><span style="font-size:0.86rem; color:var(--text-secondary);">${s.section || "--"}</span></td>
        <td><strong style="color:${house.accentText}; font-size:0.88rem;">${formatHouseLabel(house.name)}</strong></td>
        <td>
          ${hasVoted
            ? `<span class="badge badge-success" style="font-size:0.75rem; padding:3px 8px; font-weight:700;">✓ Voted</span>`
            : `<span class="badge badge-muted" style="font-size:0.75rem; padding:3px 8px;">Not Voted</span>`
          }
        </td>
        <td style="white-space:nowrap;">
          <button type="button" class="btn btn-secondary btn-open-edit-student" data-adm="${s.admissionNo}" style="font-size:0.75rem; padding:0.25rem 0.55rem; font-weight:700; border-color:#cbd5e1;" title="Change student details">
            ✏️ Change
          </button>
          ${isCustom ? `
            <button type="button" class="btn btn-danger btn-delete-custom-student" data-adm="${s.admissionNo}" data-name="${s.fullName}" style="font-size:0.75rem; padding:0.25rem 0.5rem; margin-left:0.25rem; background:#dc2626; border-color:#dc2626; color:#fff; font-weight:700;" title="Remove student">
              🗑️
            </button>
          ` : ""}
        </td>
      `;

      stuEl.stuTbody.appendChild(tr);
    });

    // Bind Copy buttons
    stuEl.stuTbody.querySelectorAll(".btn-copy-adm-row").forEach((btn) => {
      btn.addEventListener("click", () => {
        navigator.clipboard.writeText(btn.dataset.adm);
        btn.textContent = "✓";
        setTimeout(() => { btn.textContent = "📋"; }, 1200);
      });
    });

    // Bind Edit / Change buttons
    stuEl.stuTbody.querySelectorAll(".btn-open-edit-student").forEach((btn) => {
      btn.addEventListener("click", () => {
        const adm = btn.dataset.adm;
        const student = fullList.find((s) => String(s.admissionNo).toUpperCase() === String(adm).toUpperCase());
        if (!student) return;
        openEditStudentModal(student, acceptedAdmSet.has(String(adm).toUpperCase()));
      });
    });

    // Bind Delete buttons for custom added students
    stuEl.stuTbody.querySelectorAll(".btn-delete-custom-student").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const adm = btn.dataset.adm;
        const name = btn.dataset.name || adm;
        const confirmDelete = window.confirm(`Are you sure you want to remove student "${name}" (Voter ID: ${adm}) from the voter roster?`);
        if (!confirmDelete) return;

        try {
          btn.disabled = true;
          btn.textContent = "⏳";
          await window.AdminBackend.deleteStudent(adm);
          updateBadgeAddedCount();
          await refreshAll();
        } catch (err) {
          alert("Failed to remove student: " + (err.message || err));
          btn.disabled = false;
          btn.textContent = "🗑️";
        }
      });
    });"""

new_block = """    currentFilteredStudents = filtered;

    // Attach event delegation and pagination controls once
    if (!isStuTbodyDelegated) {
      isStuTbodyDelegated = true;

      stuEl.stuTbody.addEventListener("click", async (e) => {
        const copyBtn = e.target.closest(".btn-copy-adm-row");
        if (copyBtn) {
          const adm = copyBtn.dataset.adm;
          navigator.clipboard.writeText(adm);
          copyBtn.textContent = "✓";
          setTimeout(() => { copyBtn.textContent = "📋"; }, 1200);
          return;
        }

        const editBtn = e.target.closest(".btn-open-edit-student");
        if (editBtn) {
          const adm = editBtn.dataset.adm;
          const student = currentStudentsList.find((s) => String(s.admissionNo).toUpperCase() === String(adm).toUpperCase());
          if (student) {
            openEditStudentModal(student, currentAcceptedAdmSet.has(String(adm).toUpperCase()));
          }
          return;
        }

        const delBtn = e.target.closest(".btn-delete-custom-student");
        if (delBtn) {
          const adm = delBtn.dataset.adm;
          const name = delBtn.dataset.name || adm;
          const confirmDelete = window.confirm(`Are you sure you want to remove student "${name}" (Voter ID: ${adm}) from the voter register?`);
          if (!confirmDelete) return;

          try {
            delBtn.disabled = true;
            delBtn.textContent = "⏳";
            await window.AdminBackend.deleteStudent(adm);
            updateBadgeAddedCount();
            await refreshAll();
          } catch (err) {
            alert("Failed to remove student: " + (err.message || err));
            delBtn.disabled = false;
            delBtn.textContent = "🗑️";
          }
          return;
        }
      });

      if (stuEl.btnStuLoadMore) {
        stuEl.btnStuLoadMore.addEventListener("click", () => {
          visibleStudentLimit += 80;
          updateStudentTableDOM();
        });
      }
      if (stuEl.btnStuLoadAll) {
        stuEl.btnStuLoadAll.addEventListener("click", () => {
          visibleStudentLimit = currentFilteredStudents.length;
          updateStudentTableDOM();
        });
      }
    }

    updateStudentTableDOM();"""

assert old_block in code, "old_block not found in edit-votes.js"
code = code.replace(old_block, new_block, 1)

with open('Houses/admin/edit-votes.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("edit-votes.js updated successfully!")
