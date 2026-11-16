with open('Houses/admin/edit-votes.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's inspect renderOverviewKpis, makePhotoCell, renderBallotsTable, openCancelModal, confirmCancelBtn
idx_kpi = text.find('function renderOverviewKpis(')
idx_table_end = text.find('// --- View 2: Search & Single-Voter Choice Editor ---')

print("KPI start:", idx_kpi, "Table end:", idx_table_end)

new_kpi_and_table = """  function renderOverviewKpis(snap) {
    const eligible = (snap.students || []).filter((s) => s.isActive).length;
    const acceptedBallotsAll = (snap.ballots || []).filter((b) => b.status === "accepted");
    const votedVotersCount = new Set(acceptedBallotsAll.map((b) => b.admissionNo)).size;
    const cancelledBallotsAll = (snap.ballots || []).filter((b) => b.status === "cancelled");
    const cancelledVotersCount = new Set(cancelledBallotsAll.map((b) => b.admissionNo)).size;

    if (el.kpiAcceptedBallots) el.kpiAcceptedBallots.textContent = String(votedVotersCount);
    if (el.kpiVotersCount) el.kpiVotersCount.textContent = `${acceptedBallotsAll.length} role ballots cast`;
    if (el.kpiCancelledBallots) el.kpiCancelledBallots.textContent = String(cancelledVotersCount);
    if (el.kpiEligibleRoster) el.kpiEligibleRoster.textContent = String(eligible);
    if (el.kpiRemainingRoster) el.kpiRemainingRoster.textContent = String(Math.max(0, eligible - votedVotersCount));
  }

  function makePhotoCell(ballotOrVoter) {
    const photoUrl = ballotOrVoter.photoDataUrl || (ballotOrVoter.ballots && ballotOrVoter.ballots.find((b) => b.photoDataUrl)?.photoDataUrl);
    if (!photoUrl) {
      const span = document.createElement("span");
      span.textContent = "—";
      span.style.color = "var(--text-muted)";
      return span;
    }
    const wrap = document.createElement("div");
    wrap.className = "photo-cell-wrap";

    const thumbBtn = document.createElement("button");
    thumbBtn.type = "button";
    thumbBtn.className = "photo-thumb-btn";
    thumbBtn.title = "View verification photo";
    const img = document.createElement("img");
    img.src = photoUrl;
    img.alt = `Photo of ${ballotOrVoter.fullName || "Voter"}`;
    thumbBtn.appendChild(img);

    const txtBtn = document.createElement("button");
    txtBtn.type = "button";
    txtBtn.className = "photo-text-btn";
    txtBtn.textContent = "View Photo";

    const openPhoto = () => {
      if (el.photoModalImg) el.photoModalImg.src = photoUrl;
      if (el.photoModalMeta) {
        el.photoModalMeta.textContent = `${ballotOrVoter.fullName} · ID ${ballotOrVoter.admissionNo} · Verification Photo`;
      }
      if (el.photoModal) el.photoModal.hidden = false;
    };

    thumbBtn.addEventListener("click", openPhoto);
    txtBtn.addEventListener("click", openPhoto);

    wrap.appendChild(thumbBtn);
    wrap.appendChild(txtBtn);
    return wrap;
  }

  // --- View 1: Render All Ballots Table (1 Consolidated Row Per Voter & Confidential Ballot Secrecy) ---
  function renderBallotsTable(snap) {
    if (!el.ballotsTableTbody) return;
    const q = (el.ballotSearch?.value || "").trim().toLowerCase();
    const hFilter = el.ballotHouseFilter?.value || "";
    const cFilter = el.ballotClassFilter?.value.trim() || "";
    const sFilter = el.ballotSectionFilter?.value.trim() || "";
    const statusFilter = el.ballotStatusFilter?.value || "accepted";

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
      if (el.ballotsTableEmpty) el.ballotsTableEmpty.hidden = remainingStudents.length > 0;

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
          <td>
            <button type="button" class="btn btn-secondary btn-sm btn-pill btn-lookup-student">Lookup Voter →</button>
          </td>
        `;

        tr.children[0].textContent = s.admissionNo;
        tr.children[1].querySelector("strong").textContent = s.fullName;
        const clsSec = s.className ? `Class ${s.className}-${s.section || "--"}` : (s.section || "--");
        tr.children[1].querySelector(".stat-note").textContent = clsSec;

        tr.querySelector(".btn-lookup-student").addEventListener("click", () => {
          switchView("search");
          loadStudentEditor(s.admissionNo);
        });

        el.ballotsTableTbody.appendChild(tr);
      });
      return;
    }

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

    const voterRows = Array.from(voterMap.values()).filter((v) => {
      const isAccepted = v.hasAccepted;
      if (statusFilter === "accepted" && !isAccepted) return false;
      if (statusFilter === "cancelled" && isAccepted) return false;
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
    if (el.ballotsTableEmpty) el.ballotsTableEmpty.hidden = voterRows.length > 0;

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

text = text[:idx_kpi] + new_kpi_and_table + text[idx_table_end:]

# Now update openCancelModal and confirmCancelBtn
idx_open_cancel = text.find('function openCancelModal(')
idx_open_delete = text.find('function openDeleteModal(')

new_open_cancel = """let pendingCancelVoter = null;

  function openCancelModal(voterOrBallot) {
    if (voterOrBallot.ballots) {
      pendingCancelVoter = voterOrBallot;
      pendingCancelBallotId = voterOrBallot.ballots[0]?.id || null;
      const count = voterOrBallot.ballots.length;
      el.cancelModalDesc.textContent = `Cancel vote for ${voterOrBallot.fullName} (Voter ID ${voterOrBallot.admissionNo}) across all ${count} leadership posts? The record stays in cancelled history and the student can cast a new vote.`;
    } else {
      pendingCancelVoter = null;
      pendingCancelBallotId = voterOrBallot.id;
      el.cancelModalDesc.textContent = `Cancel vote for ${voterOrBallot.fullName} (ID ${voterOrBallot.admissionNo})? The record stays in cancelled history and the student can cast a new vote.`;
    }
    el.cancelErrorText.hidden = true;
    el.cancelModal.hidden = false;
    el.confirmCancelBtn.focus();
  }

  """

text = text[:idx_open_cancel] + new_open_cancel + text[idx_open_delete:]

# Update confirmCancelBtn listener
idx_confirm = text.find('el.confirmCancelBtn.addEventListener("click"')
idx_confirm_end = text.find('el.deleteModalClose.addEventListener', idx_confirm)

new_confirm = """el.confirmCancelBtn.addEventListener("click", async () => {
      if (!pendingCancelVoter && !pendingCancelBallotId) return;
      try {
        el.confirmCancelBtn.disabled = true;
        const actorName = (typeof sessionStorage !== "undefined" && (sessionStorage.getItem("spr_admin_email") || sessionStorage.getItem("spr_admin_name"))) || "rc4616105@gmail.com";
        if (pendingCancelVoter && window.AdminBackend.cancelStudentBallots) {
          await window.AdminBackend.cancelStudentBallots(pendingCancelVoter.admissionNo, "", actorName);
        } else if (pendingCancelBallotId) {
          await window.AdminBackend.cancelBallot(pendingCancelBallotId, "", actorName);
        }
        el.cancelModal.hidden = true;
        pendingCancelVoter = null;
        pendingCancelBallotId = null;
        await refreshAll();
      } catch (err) {
        el.cancelErrorText.textContent = err.message;
        el.cancelErrorText.hidden = false;
      } finally {
        el.confirmCancelBtn.disabled = false;
      }
    });
  }

  if ("""

text = text[:idx_confirm] + new_confirm + text[idx_confirm_end+6:]

with open('Houses/admin/edit-votes.js', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated Houses/admin/edit-votes.js successfully!")
