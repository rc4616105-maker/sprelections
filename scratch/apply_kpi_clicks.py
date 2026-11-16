with open('Houses/admin/edit-votes.js', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add updatePanelHeader and setKpiFilter after renderOverviewKpis
idx_ro_end = text.find('function makePhotoCell(ballotOrVoter) {')

funcs = """  function updatePanelHeader(target) {
    if (!el.ballotsPanelHeading || !el.ballotsPanelCaption) return;
    if (target === "accepted") {
      el.ballotsPanelHeading.textContent = "Active Accepted Voters Master Register";
      el.ballotsPanelCaption.textContent = "Students who have submitted active votes across booths. Review verification photos or cancel votes.";
    } else if (target === "cancelled") {
      el.ballotsPanelHeading.textContent = "Cancelled Ballots Register";
      el.ballotsPanelCaption.textContent = "Students whose vote was cancelled (excluded from results; student can re-vote). Review who cancelled and delete/reset if authorized.";
    } else if (target === "eligible") {
      el.ballotsPanelHeading.textContent = "Total Eligible Students (Master Register)";
      el.ballotsPanelCaption.textContent = "All 966 active eligible students and faculty across houses.";
    } else if (target === "remaining") {
      el.ballotsPanelHeading.textContent = "Remaining Not Voted Students";
      el.ballotsPanelCaption.textContent = "Eligible students who have not yet completed all leadership role votes.";
    } else {
      el.ballotsPanelHeading.textContent = "All Cast Ballots Master Register";
      el.ballotsPanelCaption.textContent = "Review verification photos, cast timestamps, cancel votes, or delete student ballots.";
    }
  }

  function setKpiFilter(target) {
    if (el.kpiButtons) {
      el.kpiButtons.forEach((btn) => {
        btn.classList.toggle("is-active", btn.dataset.ballotKpi === target);
      });
    }
    if (el.ballotStatusFilter) {
      el.ballotStatusFilter.value = target;
    }
    updatePanelHeader(target);
    if (latestSnapshot) {
      renderBallotsTable(latestSnapshot);
    }
  }

  """

text = text[:idx_ro_end] + funcs + text[idx_ro_end:]

# 2. Replace renderBallotsTable with the upgraded implementation
idx_rbt_start = text.find('function renderBallotsTable(snap) {')
idx_rbt_end = text.find('// --- View 2: Search & Single-Voter Choice Editor ---')

new_renderBallotsTable = """function renderBallotsTable(snap) {
    if (!el.ballotsTableTbody) return;
    const q = (el.ballotSearch?.value || "").trim().toLowerCase();
    const hFilter = el.ballotHouseFilter?.value || "";
    const cFilter = el.ballotClassFilter?.value.trim() || "";
    const sFilter = el.ballotSectionFilter?.value.trim() || "";
    const statusFilter = el.ballotStatusFilter?.value || "accepted";

    // Group ballots by voter (admissionNo) to ensure 1 consolidated row per voter and protect ballot secrecy
    const voterMap = new Map();
    (snap.ballots || []).forEach((b) => {
      if (!voterMap.has(b.admissionNo)) {
        voterMap.set(b.admissionNo, {
          admissionNo: b.admissionNo,
          fullName: b.fullName || b.admissionNo,
          className: b.className || "",
          section: b.section || "",
          houseCode: b.houseCode || "",
          photoDataUrl: b.photoDataUrl || "",
          castAt: b.castAt,
          cancelledAt: b.cancelledAt,
          cancelledBy: b.cancelledBy,
          cancelledReason: b.cancelledReason,
          ballots: [],
          hasAccepted: false,
          hasCancelled: false,
        });
      }
      const v = voterMap.get(b.admissionNo);
      v.ballots.push(b);
      if (b.status === "accepted") v.hasAccepted = true;
      if (b.status === "cancelled") v.hasCancelled = true;
      if (!v.photoDataUrl && b.photoDataUrl) v.photoDataUrl = b.photoDataUrl;
      if (!v.castAt && b.castAt) v.castAt = b.castAt;
      if (!v.cancelledBy && b.cancelledBy) v.cancelledBy = b.cancelledBy;
      if (!v.cancelledAt && b.cancelledAt) v.cancelledAt = b.cancelledAt;
    });

    // Handle "remaining" (Pending students who haven't voted)
    if (statusFilter === "remaining") {
      const acceptedAdmSet = new Set((snap.ballots || []).filter((b) => b.status === "accepted").map((b) => b.admissionNo));
      const remainingStudents = (snap.students || [])
        .filter((s) => s.isActive && !acceptedAdmSet.has(s.admissionNo))
        .filter((s) => {
          if (hFilter && s.houseCode !== hFilter) return false;
          if (cFilter && normClass(s.className) !== normClass(cFilter)) return false;
          if (sFilter && normSection(s.section) !== normSection(sFilter)) return false;
          if (q) {
            const hay = `${s.admissionNo} ${s.fullName} ${s.className}-${s.section}`.toLowerCase();
            if (!hay.includes(q)) return false;
          }
          return true;
        })
        .sort((a, b) => a.admissionNo.localeCompare(b.admissionNo));

      el.ballotsTableTbody.innerHTML = "";
      if (el.ballotsTableEmpty) {
        el.ballotsTableEmpty.hidden = remainingStudents.length > 0;
        if (remainingStudents.length === 0) {
          if (el.emptyIcon) el.emptyIcon.textContent = "🎉";
          if (el.emptyTitle) el.emptyTitle.textContent = "All Students Have Voted!";
          if (el.emptySubtitle) el.emptySubtitle.textContent = "100% voter turnout achieved.";
        }
      }

      remainingStudents.forEach((s) => {
        const house = houseMap[s.houseCode] || { name: s.houseCode, accentText: "#141413" };
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td class="mono" style="font-weight:700;"></td>
          <td>
            <strong></strong>
            <div class="stat-note"></div>
          </td>
          <td><strong style="color:${house.accentText};">${formatHouseLabel(house.name)}</strong></td>
          <td><span class="stat-note" style="color:var(--text-muted); font-style:italic;">No vote cast yet</span></td>
          <td><span class="stat-note">—</span></td>
          <td><span class="stat-note">—</span></td>
          <td><span class="badge badge-muted">Not Voted</span></td>
          <td><span class="stat-note">—</span></td>
        `;

        tr.children[0].textContent = s.admissionNo;
        tr.children[1].querySelector("strong").textContent = s.fullName;
        const clsSec = s.className ? `Class ${s.className}-${s.section || "--"}` : (s.section || "--");
        tr.children[1].querySelector(".stat-note").textContent = clsSec;

        el.ballotsTableTbody.appendChild(tr);
      });
      return;
    }

    // Handle "eligible" (All 966 registered students & faculty)
    if (statusFilter === "eligible") {
      const acceptedAdmSet = new Set((snap.ballots || []).filter((b) => b.status === "accepted").map((b) => b.admissionNo));
      const cancelledAdmSet = new Set((snap.ballots || []).filter((b) => b.status === "cancelled").map((b) => b.admissionNo));

      const eligibleStudents = (snap.students || [])
        .filter((s) => s.isActive)
        .filter((s) => {
          if (hFilter && s.houseCode !== hFilter) return false;
          if (cFilter && normClass(s.className) !== normClass(cFilter)) return false;
          if (sFilter && normSection(s.section) !== normSection(sFilter)) return false;
          if (q) {
            const hay = `${s.admissionNo} ${s.fullName} ${s.className}-${s.section}`.toLowerCase();
            if (!hay.includes(q)) return false;
          }
          return true;
        })
        .sort((a, b) => a.admissionNo.localeCompare(b.admissionNo));

      el.ballotsTableTbody.innerHTML = "";
      if (el.ballotsTableEmpty) {
        el.ballotsTableEmpty.hidden = eligibleStudents.length > 0;
        if (eligibleStudents.length === 0) {
          if (el.emptyIcon) el.emptyIcon.textContent = "📋";
          if (el.emptyTitle) el.emptyTitle.textContent = "No Students Found";
          if (el.emptySubtitle) el.emptySubtitle.textContent = "No eligible students match the current filters.";
        }
      }

      eligibleStudents.forEach((s) => {
        const house = houseMap[s.houseCode] || { name: s.houseCode, accentText: "#141413" };
        const hasAccepted = acceptedAdmSet.has(s.admissionNo);
        const hasCancelled = cancelledAdmSet.has(s.admissionNo);
        const voterData = voterMap.get(s.admissionNo);

        const roleCount = s.houseCode === "CENTRAL" || s.isStaff ? 5 : 4;
        const votedStatusHtml = hasAccepted
          ? `<span class="badge badge-success" style="font-weight:700; padding:4px 9px; font-size:0.8rem; background:rgba(21,128,61,0.12); color:#15803d; border:1px solid rgba(21,128,61,0.3);">✓ Voted (All ${roleCount} Posts)</span><div class="stat-note" style="color:var(--text-muted); margin-top:3px; font-size:0.75rem;">Ballot Choice Confidential</div>`
          : hasCancelled
          ? `<span class="badge badge-warning" style="font-weight:700; padding:4px 9px; font-size:0.8rem;">Cancelled (${roleCount} Posts)</span><div class="stat-note" style="color:var(--text-muted); margin-top:3px; font-size:0.75rem;">Ballot Choice Confidential</div>`
          : `<span class="stat-note" style="color:var(--text-muted); font-style:italic;">No vote cast yet</span>`;

        const statusBadge = hasAccepted
          ? `<span class="badge badge-success">Accepted</span>`
          : hasCancelled
          ? `<span class="badge badge-warning">Cancelled</span>`
          : `<span class="badge badge-muted">Not Voted</span>`;

        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td class="mono" style="font-weight:700;"></td>
          <td>
            <strong></strong>
            <div class="stat-note"></div>
          </td>
          <td><strong style="color:${house.accentText};">${formatHouseLabel(house.name)}</strong></td>
          <td>${votedStatusHtml}</td>
          <td></td>
          <td class="mono" style="font-size:0.8rem;">${hasAccepted ? formatTime(voterData?.castAt) : (hasCancelled ? formatTime(voterData?.cancelledAt) : "—")}</td>
          <td>${statusBadge}</td>
          <td>
            <div class="action-stack">
              ${hasAccepted ? '<button type="button" class="btn-action-cancel btn-cancel-row">Cancel Vote</button>' : ""}
              ${(hasAccepted || hasCancelled) ? '<button type="button" class="btn-action-delete btn-delete-row">Delete</button>' : '<span class="stat-note">—</span>'}
            </div>
          </td>
        `;

        tr.children[0].textContent = s.admissionNo;
        tr.children[1].querySelector("strong").textContent = s.fullName;
        const clsSec = s.className ? `Class ${s.className}-${s.section || "--"}` : (s.section || "--");
        tr.children[1].querySelector(".stat-note").textContent = clsSec;
        if (voterData) {
          tr.children[4].appendChild(makePhotoCell(voterData));
        } else {
          tr.children[4].innerHTML = '<span class="stat-note">—</span>';
        }

        const cancelBtn = tr.querySelector(".btn-cancel-row");
        if (cancelBtn && voterData) {
          cancelBtn.addEventListener("click", () => openCancelModal(voterData));
        }
        const delBtn = tr.querySelector(".btn-delete-row");
        if (delBtn) {
          delBtn.addEventListener("click", () => openDeleteModal(s.admissionNo, s.fullName));
        }

        el.ballotsTableTbody.appendChild(tr);
      });
      return;
    }

    // Filter voterRows (accepted, cancelled, or all cast ballots)
    const voterRows = Array.from(voterMap.values()).filter((v) => {
      const isAccepted = v.hasAccepted;
      if (statusFilter === "accepted" && !isAccepted) return false;
      if (statusFilter === "cancelled" && (!v.hasCancelled || isAccepted)) return false;
      if (hFilter && v.houseCode !== hFilter) return false;
      if (cFilter && normClass(v.className) !== normClass(cFilter)) return false;
      if (sFilter && normSection(v.section) !== normSection(sFilter)) return false;
      if (q) {
        const hay = `${v.admissionNo} ${v.fullName} ${v.className}-${v.section}`.toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });

    el.ballotsTableTbody.innerHTML = "";
    if (el.ballotsTableEmpty) {
      el.ballotsTableEmpty.hidden = voterRows.length > 0;
      if (voterRows.length === 0) {
        if (el.emptyIcon) el.emptyIcon.textContent = "🗳️";
        if (statusFilter === "cancelled") {
          if (el.emptyTitle) el.emptyTitle.textContent = "No Cancelled Ballots Found";
          if (el.emptySubtitle) el.emptySubtitle.textContent = "No cancelled ballots match the current filters.";
        } else if (statusFilter === "accepted") {
          if (el.emptyTitle) el.emptyTitle.textContent = "No Accepted Ballots Found";
          if (el.emptySubtitle) el.emptySubtitle.textContent = "No active votes match the current filters.";
        } else {
          if (el.emptyTitle) el.emptyTitle.textContent = "No Ballots Found";
          if (el.emptySubtitle) el.emptySubtitle.textContent = "No cast ballots match the current filters.";
        }
      }
    }

    voterRows.forEach((v) => {
      const house = houseMap[v.houseCode] || { name: v.houseCode, accentText: "#141413" };
      const isAccepted = v.hasAccepted;
      const canceller = v.cancelledBy || "rc4616105@gmail.com";
      const statusBadge = isAccepted
        ? `<span class="badge badge-success">Accepted</span>`
        : `<span class="badge badge-warning">Cancelled</span><div class="stat-note" style="color:#b91c1c; margin-top:2px; font-weight:600;">By: ${canceller}</div>`;

      const roleCount = v.ballots.length || (v.houseCode === "CENTRAL" ? 5 : 4);
      const votedStatusHtml = isAccepted
        ? `<span class="badge badge-success" style="font-weight:700; padding:4px 9px; font-size:0.8rem; background:rgba(21,128,61,0.12); color:#15803d; border:1px solid rgba(21,128,61,0.3);">✓ Voted (All ${roleCount} Posts)</span>`
        : `<span class="badge badge-warning" style="font-weight:700; padding:4px 9px; font-size:0.8rem;">Cancelled (${roleCount} Posts)</span>`;

      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td class="mono" style="font-weight:700;"></td>
        <td>
          <strong></strong>
          <div class="stat-note"></div>
        </td>
        <td><strong style="color:${house.accentText};">${formatHouseLabel(house.name)}</strong></td>
        <td>
          ${votedStatusHtml}
          <div class="stat-note" style="color:var(--text-muted); margin-top:3px; font-size:0.75rem;">Ballot Choice Confidential</div>
        </td>
        <td></td>
        <td class="mono" style="font-size:0.8rem;">${formatTime(isAccepted ? v.castAt : v.cancelledAt)}</td>
        <td>${statusBadge}</td>
        <td>
          <div class="action-stack">
            ${isAccepted ? '<button type="button" class="btn-action-cancel btn-cancel-row">Cancel Vote</button>' : ""}
            <button type="button" class="btn-action-delete btn-delete-row">Delete</button>
          </div>
        </td>
      `;

      tr.children[0].textContent = v.admissionNo;
      tr.children[1].querySelector("strong").textContent = v.fullName;
      const clsSec = v.className ? `Class ${v.className}-${v.section || "--"}` : (v.section || "--");
      tr.children[1].querySelector(".stat-note").textContent = clsSec;
      tr.children[4].appendChild(makePhotoCell(v));

      // Action Handlers
      const cancelBtn = tr.querySelector(".btn-cancel-row");
      if (cancelBtn) {
        cancelBtn.addEventListener("click", () => openCancelModal(v));
      }

      tr.querySelector(".btn-delete-row").addEventListener("click", () => {
        openDeleteModal(v.admissionNo, v.fullName);
      });

      el.ballotsTableTbody.appendChild(tr);
    });
  }

  """

text = text[:idx_rbt_start] + new_renderBallotsTable + text[idx_rbt_end:]

# 3. Add KPI and status filter listeners
idx_listeners = text.find('// Filter Listeners for View 1')
new_listeners = """  // KPI Summary Card Click Listeners (Synchronizes view and filters exactly like Main Dashboard)
  if (el.kpiButtons && el.kpiButtons.length > 0) {
    el.kpiButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        const target = btn.dataset.ballotKpi;
        setKpiFilter(target);
      });
    });
  }

  """

text = text[:idx_listeners] + new_listeners + text[idx_listeners:]

# Also update the ballotStatusFilter change listener to synchronize KPI button active states
idx_bsf = text.find('if (el.ballotStatusFilter) el.ballotStatusFilter.addEventListener("change", () => { if (latestSnapshot) renderBallotsTable(latestSnapshot); });')
replacement_bsf = """if (el.ballotStatusFilter) {
    el.ballotStatusFilter.addEventListener("change", () => {
      const target = el.ballotStatusFilter.value;
      if (el.kpiButtons) {
        el.kpiButtons.forEach((btn) => {
          btn.classList.toggle("is-active", btn.dataset.ballotKpi === target);
        });
      }
      updatePanelHeader(target);
      if (latestSnapshot) renderBallotsTable(latestSnapshot);
    });
  }"""

text = text[:idx_bsf] + replacement_bsf + text[idx_bsf + len('if (el.ballotStatusFilter) el.ballotStatusFilter.addEventListener("change", () => { if (latestSnapshot) renderBallotsTable(latestSnapshot); });'):]

with open('Houses/admin/edit-votes.js', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated edit-votes.js successfully!")
