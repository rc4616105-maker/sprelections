with open('Houses/admin/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update makePhotoCell to support voter or ballot
idx_photo = text.find('function makePhotoCell(ballot) {')
idx_photo_end = text.find('function openPhotoModal(ballot) {')

new_photo_func = """function makePhotoCell(ballotOrVoter) {
    const photoUrl = ballotOrVoter.photoDataUrl || (ballotOrVoter.ballots && ballotOrVoter.ballots.find((b) => b.photoDataUrl)?.photoDataUrl);
    if (!photoUrl) {
      const span = document.createElement("span");
      span.textContent = "—";
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
    thumbBtn.addEventListener("click", () => openPhotoModal(ballotOrVoter));

    const viewBtn = document.createElement("button");
    viewBtn.type = "button";
    viewBtn.className = "btn btn-secondary";
    viewBtn.style.padding = "2px 7px";
    viewBtn.style.fontSize = "0.72rem";
    viewBtn.textContent = "View Photo";
    viewBtn.addEventListener("click", () => openPhotoModal(ballotOrVoter));

    wrap.appendChild(thumbBtn);
    wrap.appendChild(viewBtn);
    return wrap;
  }

  function openPhotoModal(ballotOrVoter) {
    const photoUrl = ballotOrVoter.photoDataUrl || (ballotOrVoter.ballots && ballotOrVoter.ballots.find((b) => b.photoDataUrl)?.photoDataUrl);
    const hName = formatHouseLabel(houseMap[ballotOrVoter.houseCode]?.name || ballotOrVoter.houseCode);
    el.photoModalMeta.textContent = `${ballotOrVoter.fullName} (ID ${ballotOrVoter.admissionNo}) · ${hName} · Recorded at ${formatTime(ballotOrVoter.castAt || ballotOrVoter.cancelledAt)}`;
    el.photoModalImg.src = photoUrl;
    el.photoModal.hidden = false;
  }

  """

text = text[:idx_photo] + new_photo_func + text[text.find('function openCancelModal(ballot) {'):]

# 2. Update activeKpi === "cancelled"
idx_canc = text.find('if (activeKpi === "cancelled") {')
idx_canc_end = text.find('function renderOverview(snap) {')

new_cancelled_block = """if (activeKpi === "cancelled") {
      el.drilldownTitle.textContent = "Cancelled Ballots";
      el.drilldownSubtitle.textContent = "Students whose vote was cancelled (excluded from results; student can re-vote).";

      el.drilldownThead.innerHTML = `
        <tr>
          <th>Voter ID</th>
          <th>Student</th>
          <th>House</th>
          <th>Cancelled Status</th>
          <th>Photo</th>
          <th>Cancelled By</th>
          <th>Cancelled Time</th>
          <th>Current Status</th>
          <th>Action</th>
        </tr>
      `;

      // Group cancelled ballots by voter (admissionNo) to ensure 1 consolidated row per voter and protect ballot secrecy
      const cancelledVoterMap = new Map();
      snap.ballots.forEach((b) => {
        if (b.status !== "cancelled") return;
        if (!cancelledVoterMap.has(b.admissionNo)) {
          cancelledVoterMap.set(b.admissionNo, {
            admissionNo: b.admissionNo,
            fullName: b.fullName || b.admissionNo,
            className: b.className || "",
            section: b.section || "",
            houseCode: b.houseCode || "",
            photoDataUrl: b.photoDataUrl || "",
            cancelledAt: b.cancelledAt,
            cancelledBy: b.cancelledBy,
            cancelledReason: b.cancelledReason,
            ballots: [],
          });
        }
        const v = cancelledVoterMap.get(b.admissionNo);
        v.ballots.push(b);
        if (!v.photoDataUrl && b.photoDataUrl) v.photoDataUrl = b.photoDataUrl;
        if (!v.cancelledBy && b.cancelledBy) v.cancelledBy = b.cancelledBy;
        if (!v.cancelledAt && b.cancelledAt) v.cancelledAt = b.cancelledAt;
      });

      const rows = Array.from(cancelledVoterMap.values()).filter((v) => {
        if (hFilter && v.houseCode !== hFilter) return false;
        if (cFilter && normClass(v.className) !== normClass(cFilter)) return false;
        if (sFilter && normSection(v.section) !== normSection(sFilter)) return false;
        if (q) {
          const hay = `${v.admissionNo} ${v.fullName} ${v.className}-${v.section} ${v.cancelledBy || ""}`.toLowerCase();
          if (!hay.includes(q)) return false;
        }
        return true;
      });

      el.drilldownEmpty.hidden = rows.length > 0;
      rows.forEach((v) => {
        const house = houseMap[v.houseCode] || { name: v.houseCode, accentText: "#141413" };
        const sKey = `${electionId}_${v.admissionNo}_${v.ballots[0]?.positionId || positionId}`;
        const curStatus = snap.voterStatus[sKey]?.status || "cancelled";
        const curBadge =
          curStatus === "voted"
            ? `<span class="badge badge-success">Re-voted</span>`
            : `<span class="badge badge-warning">Pending Re-vote</span>`;
        const canceller = v.cancelledBy || "rc4616105@gmail.com";
        const roleCount = v.ballots.length || (v.houseCode === "CENTRAL" ? 5 : 4);

        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td class="mono"></td>
          <td><strong></strong><div class="stat-note"></div></td>
          <td><strong style="color:${house.accentText};">${formatHouseLabel(house.name)}</strong></td>
          <td>
            <span class="badge badge-warning" style="font-weight:700; padding:4px 9px; font-size:0.8rem;">Cancelled (${roleCount} Posts)</span>
            <div class="stat-note" style="color:var(--text-muted); margin-top:3px; font-size:0.75rem;">Ballot Choice Confidential</div>
          </td>
          <td></td>
          <td><span class="badge" style="background:rgba(220,38,38,0.1); color:#b91c1c; font-weight:700; border:1px solid rgba(220,38,38,0.25);">👤 ${canceller}</span></td>
          <td class="mono"></td>
          <td>${curBadge}</td>
          <td>
            <a href="./edit-votes.html" class="btn btn-secondary btn-sm" style="padding: 4px 10px; font-size: 0.78rem; text-decoration:none;">Manage →</a>
          </td>
        `;
        tr.children[0].textContent = v.admissionNo;
        tr.children[1].querySelector("strong").textContent = v.fullName;
        const clsSecLabel = v.className ? `Class ${v.className}-${v.section || "--"}` : (v.section || "--");
        tr.children[1].querySelector(".stat-note").textContent = clsSecLabel;
        tr.children[4].appendChild(makePhotoCell(v));
        tr.children[6].textContent = formatTime(v.cancelledAt);
        el.drilldownTbody.appendChild(tr);
      });
      return;
    }
  }

  """

text = text[:idx_canc] + new_cancelled_block + text[idx_canc_end:]

# 3. Update renderOverview cancelled KPI display to show unique voters
idx_ro = text.find('function renderOverview(snap) {')
idx_ro_body = text.find('const cancelled =', idx_ro)
idx_ro_kpi = text.find('el.kpiCancelled.textContent =', idx_ro)

old_part = text[idx_ro_body:idx_ro_kpi+50]
print("Old overview part:", old_part)

text = text.replace(
    'const cancelled = snap.ballots.filter((b) => b.status === "cancelled").length;',
    'const cancelledBallotsAll = snap.ballots.filter((b) => b.status === "cancelled");\n    const cancelledVotersCount = new Set(cancelledBallotsAll.map((b) => b.admissionNo)).size;'
)

text = text.replace(
    'el.kpiCancelled.textContent = String(cancelled);',
    'el.kpiCancelled.textContent = String(cancelledVotersCount);'
)

with open('Houses/admin/app.js', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated Houses/admin/app.js successfully!")
