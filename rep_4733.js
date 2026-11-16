  function populateBoothFilter(snap) {
    if (!el.drilldownBoothFilter) return;
    const currentVal = el.drilldownBoothFilter.value;
    const booths = new Set();
    (snap?.ballots || []).forEach((b) => {
      const name = b.boothName || b.booth_name;
      if (name && String(name).trim()) booths.add(String(name).trim());
    });
    if (booths.size === 0) booths.add("Booth 1");
    el.drilldownBoothFilter.innerHTML = `<option value="">All Booths (${booths.size})</option>`;
    Array.from(booths).sort().forEach((b) => {
      const opt = document.createElement("option");
      opt.value = b;
      opt.textContent = `📍 ${b}`;
      if (b === currentVal) opt.selected = true;
      el.drilldownBoothFilter.appendChild(opt);
    });
  }

  function renderDrilldown(snap) {
    populateBoothFilter(snap);

    el.kpiButtons.forEach((b) => {
      b.classList.toggle("is-active", b.dataset.kpiFilter === activeKpi);
    });

    if (!activeKpi) {
      el.drilldownPanel.hidden = true;
      return;
    }

    el.drilldownPanel.hidden = false;
    const q = el.drilldownSearch.value.trim().toLowerCase();
    const hFilter = el.drilldownHouseFilter.value;
    const bFilter = el.drilldownBoothFilter ? el.drilldownBoothFilter.value.trim() : "";
    const cFilter = el.drilldownClassFilter ? el.drilldownClassFilter.value.trim() : "";
    const sFilter = el.drilldownSectionFilter ? el.drilldownSectionFilter.value.trim() : "";

    const positions = window.ADMIN_DATA.positions || [{ id: positionId, title: "House Captain" }];
    const studentStatus = (stu) => {
      const states = positions.map((p) => snap.voterStatus[`${electionId}_${stu.admissionNo}_${p.id}`]?.status || "not_voted");
      if (states.every((s) => s === "voted")) return "voted";
      if (states.some((s) => s === "cancelled")) return "cancelled";
      if (states.some((s) => s === "voted")) return "partial";
      return "not_voted";
    };

    el.drilldownThead.innerHTML = "";
    el.drilldownTbody.innerHTML = "";

    if (activeKpi === "eligible" || activeKpi === "remaining") {
      const isRemaining = activeKpi === "remaining";
      el.drilldownTitle.textContent = isRemaining
        ? "Remaining Not Voted Students"
        : "Total Eligible Students (Master Register)";
      el.drilldownSubtitle.textContent = isRemaining
        ? "Eligible students who have not yet completed all 4 leadership role votes."
        : "All active eligible students across the six houses.";

      el.drilldownThead.innerHTML = `
        <tr>
          <th>Admission ID</th>
          <th>Student</th>
          <th>Class</th>
          <th>Sec</th>
          <th>House</th>
          <th>Role</th>
          <th>Status</th>
        </tr>
      `;

      const rows = snap.students
        .filter((s) => s.isActive)
        .filter((s) => {
          if (hFilter && s.houseCode !== hFilter) return false;
          if (cFilter && normClass(s.className) !== normClass(cFilter)) return false;
          if (sFilter && normSection(s.section) !== normSection(sFilter)) return false;
          if (isRemaining && studentStatus(s) === "voted") return false;
          if (q) {
            const hay = `${s.admissionNo} ${s.fullName} ${s.className}-${s.section}`.toLowerCase();
            if (!hay.includes(q)) return false;
          }
          return true;
        })
        .sort((a, b) => a.admissionNo.localeCompare(b.admissionNo));

      el.drilldownEmpty.hidden = rows.length > 0;
      rows.forEach((s) => {
        const house = houseMap[s.houseCode] || { name: s.houseCode, accentText: "#141413" };
        const st = studentStatus(s);
        const badge =
          st === "voted"
            ? `<span class="badge badge-success">Voted (4/4)</span>`
            : st === "cancelled"
            ? `<span class="badge badge-warning">Cancelled (Pending Re-vote)</span>`
            : st === "partial"
            ? `<span class="badge badge-warning">Partial Vote</span>`
            : `<span class="badge badge-muted">Not Voted</span>`;

        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td class="mono"></td>
          <td><strong></strong></td>
          <td><span class="mono"></span></td>
          <td></td>
          <td><strong style="color:${house.accentText};">${formatHouseLabel(house.name)}</strong></td>
          <td>${s.isCandidate ? s.positionName || "Candidate" : "Voter"}</td>
          <td>${badge}</td>
        `;
        tr.children[0].textContent = s.admissionNo;
        tr.children[1].querySelector("strong").textContent = s.fullName;
        const clsLabel = s.className ? (s.className.toString().toLowerCase().startsWith("class") ? s.className : `Class ${s.className}`) : "--";
        tr.children[2].querySelector(".mono").textContent = clsLabel;
        tr.children[3].textContent = s.section || "--";
        el.drilldownTbody.appendChild(tr);
      });
      return;
    }

    if (activeKpi === "accepted") {
      el.drilldownTitle.textContent = "Active Accepted Voters";
      el.drilldownSubtitle.textContent = "All students who have submitted active votes across booths. Reviewing photos, cast times, changing candidate choices, or resetting ballots is managed inside Edit Votes.";

      el.drilldownThead.innerHTML = `
        <tr>
          <th>Admission ID</th>
          <th>Student</th>
          <th>Class</th>
          <th>Sec</th>
          <th>House</th>
          <th>Booth</th>
          <th>Status</th>
          <th>Action</th>
        </tr>
      `;

      const acceptedBallots = snap.ballots.filter((b) => b.status === "accepted");
      const acceptedAdmSet = new Set(acceptedBallots.map((b) => b.admissionNo));
      const admBoothMap = new Map();
      acceptedBallots.forEach((b) => {
        if (!admBoothMap.has(b.admissionNo)) {
          admBoothMap.set(b.admissionNo, b.boothName || b.booth_name || "Booth 1");
        }
      });

      const rows = snap.students
        .filter((s) => s.isActive && acceptedAdmSet.has(s.admissionNo))
        .filter((s) => {
          if (hFilter && s.houseCode !== hFilter) return false;
          if (cFilter && normClass(s.className) !== normClass(cFilter)) return false;
          if (sFilter && normSection(s.section) !== normSection(sFilter)) return false;
          const stuBooth = admBoothMap.get(s.admissionNo) || "Booth 1";
          if (bFilter && stuBooth !== bFilter) return false;
          if (q) {
            const hay = `${s.admissionNo} ${s.fullName} ${s.className}-${s.section} ${stuBooth}`.toLowerCase();
            if (!hay.includes(q)) return false;
          }
          return true;
        })
        .sort((a, b) => a.admissionNo.localeCompare(b.admissionNo));

      el.drilldownEmpty.hidden = rows.length > 0;
      rows.forEach((s) => {
        const house = houseMap[s.houseCode] || { name: s.houseCode, accentText: "#141413" };
        const st = studentStatus(s);
        const stuBooth = admBoothMap.get(s.admissionNo) || "Booth 1";
        const badge =
          st === "voted"
            ? `<span class="badge badge-success">Voted (4/4)</span>`
            : `<span class="badge badge-warning">Partial Vote</span>`;

        const tr = document.createElement("tr");
        if (prevAcceptedVoterSet.size > 0 && !prevAcceptedVoterSet.has(s.admissionNo)) {
          tr.style.animation = "rowHighlightFlash 2.2s ease-out";
        }

        tr.innerHTML = `
          <td class="mono"></td>
          <td><strong></strong></td>
          <td><span class="mono"></span></td>
          <td></td>
          <td><strong style="color:${house.accentText};">${formatHouseLabel(house.name)}</strong></td>
          <td><span class="badge" style="background:rgba(5,150,105,0.12); color:#047857; font-weight:700; border:1px solid rgba(5,150,105,0.25);">📍 ${stuBooth}</span></td>
          <td>${badge}</td>
          <td>
            <a href="./edit-votes.html?adm=${encodeURIComponent(s.admissionNo)}" class="btn btn-secondary" style="font-size:0.75rem; padding:0.25rem 0.55rem; min-height:auto;">Edit Ballots →</a>
          </td>
        `;
        tr.children[0].textContent = s.admissionNo;
        tr.children[1].querySelector("strong").textContent = s.fullName;
        const clsLabel = s.className ? (s.className.toString().toLowerCase().startsWith("class") ? s.className : `Class ${s.className}`) : "--";
        tr.children[2].querySelector(".mono").textContent = clsLabel;
        tr.children[3].textContent = s.section || "--";
        el.drilldownTbody.appendChild(tr);
      });

      // Update prevAcceptedVoterSet
      acceptedAdmSet.forEach((adm) => prevAcceptedVoterSet.add(adm));
      return;
    }