// Election Results Excel & Print Exporter
// Generates a clean, hierarchical Microsoft Excel (.xlsx) workbook organized by House & Post:
// - House Section Header (e.g. 🏛️ SCHOOL CABINET, 🟡 BHEESHMA HOUSE)
// - Post Heading (e.g. 📌 School President, 📌 Boys Captain - Class 10)
// - Table Columns: Candidate Name | Class & Sec | No. of Votes (sorted descending by votes)
(function () {
  function formatHouseLabel(name) {
    if (!name) return "";
    const str = String(name).trim();
    if (str.endsWith("House") || str.endsWith("Houses") || str === "School Cabinet") {
      return str;
    }
    return `${str} House`;
  }

  function getCandidateClassSec(cand, post, students) {
    if (!cand) return post ? `Class ${post.className || "—"}` : "—";
    const stu = (students || []).find(
      (s) => s.admissionNo === cand.admissionNo || s.fullName === cand.fullName
    );
    if (stu && stu.className && stu.section) {
      const cls = String(stu.className).toLowerCase().startsWith("class")
        ? stu.className
        : `Class ${stu.className}`;
      return `${cls} · Sec ${stu.section}`;
    }
    const cls = cand.className
      ? String(cand.className).toLowerCase().startsWith("class")
        ? cand.className
        : `Class ${cand.className}`
      : post?.className
      ? `Class ${post.className}`
      : "";
    let sec = cand.section || "";
    if (sec.includes("· Option")) {
      sec = "Sec " + sec.split("· Option").pop().trim();
    } else if (sec.startsWith("Class ")) {
      sec = "";
    }
    if (cls && sec) return `${cls} · ${sec}`;
    return cls || sec || "—";
  }

  function getElectionGroups(candidatesList, studentsList) {
    const adminData = window.ADMIN_DATA || {};
    let cands = candidatesList || adminData.candidates || [];
    if (!cands || cands.length === 0) {
      cands = adminData.candidates || [];
    }
    const students = studentsList || adminData.students || [];

    const groups = [];

    // 1. School Cabinet (Central Council) — 5 Posts
    const centralPositions = adminData.centralPositions || [
      { id: "PRESIDENT", code: "Vote_President", title: "School President", subtitle: "Class 10 · Central Cabinet", className: "10" },
      { id: "VICE_PRESIDENT", code: "Vote_Vice_President", title: "School Vice President", subtitle: "Class 9 · Central Cabinet", className: "9" },
      { id: "LITERARY_SECRETARY", code: "Vote_Literary_Sec", title: "Literary Secretary", subtitle: "Class 9 · Central Cabinet", className: "9" },
      { id: "SPORTS_SECRETARY", code: "Vote_Sports_Sec", title: "Sports Secretary", subtitle: "Class 9 · Central Cabinet", className: "9" },
      { id: "SOCIAL_CULTURAL_SECRETARY", code: "Vote_Social_Cultural_Sec", title: "Social & Cultural Secretary", subtitle: "Class 9 · Central Cabinet", className: "9" },
    ];

    const cabinetPosts = centralPositions.map((cp) => {
      let postCands = cands.filter(
        (c) => c.houseCode === "CENTRAL" && (c.positionId === cp.id || c.positionId === cp.code) && c.isApproved
      );
      if (postCands.length === 0) {
        postCands = (adminData.candidates || []).filter(
          (c) => c.houseCode === "CENTRAL" && (c.positionId === cp.id || c.positionId === cp.code)
        );
      }
      return {
        id: cp.id,
        code: cp.code,
        title: cp.title,
        subtitle: cp.subtitle,
        className: cp.className,
        isCentral: true,
        houseCode: "CENTRAL",
        candidates: postCands,
      };
    });

    groups.push({
      code: "CENTRAL",
      name: "School Cabinet",
      icon: "🏛️",
      posts: cabinetPosts,
    });

    // 2. Regular 6 Houses — 4 Posts each
    const houseDefs = [
      { code: "BHEESHMA", name: "Bheeshma House", icon: "🟡" },
      { code: "GURUDRONA", name: "Gurudrona House", icon: "🔵" },
      { code: "HANUMAN", name: "Hanuman House", icon: "🟠" },
      { code: "KARNA", name: "Karna House", icon: "🔴" },
      { code: "VASISTHA", name: "Vasistha House", icon: "🟣" },
      { code: "VISHWAMITHRA", name: "Vishwamithra House", icon: "🟣" },
    ];

    const regularPositions = adminData.positions || [
      { id: "CAPTAIN_BOY", code: "Vote_10_Boy", title: "Boys Captain", subtitle: "Class 10 Boy", className: "10" },
      { id: "CAPTAIN_GIRL", code: "Vote_10_Girl", title: "Girls Captain", subtitle: "Class 10 Girl", className: "10" },
      { id: "VICE_CAPTAIN_BOY", code: "Vote_9_Boy", title: "Boys Vice Captain", subtitle: "Class 9 Boy", className: "9" },
      { id: "VICE_CAPTAIN_GIRL", code: "Vote_9_Girl", title: "Girls Vice Captain", subtitle: "Class 9 Girl", className: "9" },
    ];

    houseDefs.forEach((h) => {
      const housePosts = regularPositions.map((rp) => {
        let postCands = cands.filter(
          (c) => c.houseCode === h.code && (c.positionId === rp.id || c.positionId === rp.code) && c.isApproved
        );
        if (postCands.length === 0) {
          postCands = (adminData.candidates || []).filter(
            (c) => c.houseCode === h.code && (c.positionId === rp.id || c.positionId === rp.code)
          );
        }
        return {
          id: rp.id,
          code: rp.code,
          title: rp.title,
          subtitle: `${h.name} · ${rp.subtitle}`,
          className: rp.className,
          isCentral: false,
          houseCode: h.code,
          candidates: postCands,
        };
      });

      groups.push({
        code: h.code,
        name: h.name,
        icon: h.icon,
        posts: housePosts,
      });
    });

    return groups;
  }

  function computeElectionHierarchy(snap) {
    const acceptedBallots = (snap.ballots || []).filter((b) => b.status === "accepted");
    const students = snap.students || window.ADMIN_DATA?.students || [];
    const groups = getElectionGroups(snap.candidates, students);

    return groups.map((g) => {
      const postsWithVotes = g.posts.map((post) => {
        const candsWithVotes = post.candidates.map((c) => {
          const votes = acceptedBallots.filter((b) => {
            const matchCand = b.candidateId === c.id || b.candidateName === c.fullName;
            if (!matchCand) return false;
            if (post.isCentral) {
              return (
                b.houseCode === "CENTRAL" ||
                b.positionId === post.id ||
                b.positionId === post.code ||
                (b.positionName && b.positionName.includes(post.title))
              );
            }
            return (
              b.houseCode === post.houseCode &&
              (b.positionId === post.id ||
                b.positionId === post.code ||
                (b.positionName && b.positionName.includes(post.title)))
            );
          }).length;

          return {
            fullName: c.fullName,
            classSec: getCandidateClassSec(c, post, students),
            votes,
          };
        });

        // Sort candidates descending according to number of votes (highest votes first)
        candsWithVotes.sort((a, b) => b.votes - a.votes || a.fullName.localeCompare(b.fullName));

        const totalVotes = candsWithVotes.reduce((sum, c) => sum + c.votes, 0);

        return {
          title: post.title,
          subtitle: post.subtitle,
          className: post.className,
          totalVotes,
          candidates: candsWithVotes,
        };
      });

      return {
        code: g.code,
        name: g.name,
        icon: g.icon,
        posts: postsWithVotes,
      };
    });
  }

  function showExportToast(fileName) {
    let toast = document.getElementById("excel-export-toast");
    if (!toast) {
      toast = document.createElement("div");
      toast.id = "excel-export-toast";
      toast.style.cssText = `
        position: fixed;
        bottom: 24px;
        right: 24px;
        z-index: 99999;
        background: #047857;
        color: #ffffff;
        padding: 1rem 1.4rem;
        border-radius: 12px;
        box-shadow: 0 16px 36px -8px rgba(4, 120, 87, 0.45);
        display: flex;
        align-items: center;
        gap: 1.1rem;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.92rem;
        animation: slideUpFade 240ms ease-out;
      `;
      document.body.appendChild(toast);
    }

    toast.innerHTML = `
      <div style="display:flex; align-items:center; gap:0.6rem;">
        <span style="font-size:1.4rem;">📊</span>
        <div>
          <strong style="display:block; font-size:0.95rem;">Excel Report Downloaded!</strong>
          <span style="opacity:0.9; font-size:0.82rem;">${fileName}</span>
        </div>
      </div>
      <div style="display:flex; align-items:center; gap:0.5rem; margin-left: 0.5rem;">
        <button type="button" id="toast-print-paper" style="
          background: #ffffff;
          color: #047857;
          border: none;
          font-weight: 700;
          padding: 0.45rem 0.85rem;
          border-radius: 6px;
          cursor: pointer;
          font-size: 0.82rem;
        ">🖨️ Print Paper</button>
        <button type="button" id="toast-close-btn" style="
          background: transparent;
          color: #ffffff;
          border: none;
          font-size: 1.1rem;
          cursor: pointer;
          opacity: 0.8;
          padding: 0.2rem 0.4rem;
        ">✕</button>
      </div>
    `;

    toast.hidden = false;

    const printBtn = document.getElementById("toast-print-paper");
    if (printBtn) {
      printBtn.onclick = () => window.print();
    }
    const closeBtn = document.getElementById("toast-close-btn");
    if (closeBtn) {
      closeBtn.onclick = () => {
        toast.hidden = true;
      };
    }

    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => {
      toast.hidden = true;
    }, 7000);
  }

  async function exportElectionResultsToExcel(providedSnapshot) {
    let snap = providedSnapshot;
    if (!snap) {
      try {
        if (window.AdminBackend && typeof window.AdminBackend.getSnapshot === "function") {
          snap = await window.AdminBackend.getSnapshot();
        }
      } catch (e) {
        console.warn("Could not retrieve live snapshot, using local fallback data:", e);
      }
    }
    if (!snap) {
      snap = {
        students: window.ADMIN_DATA?.students || [],
        candidates: window.ADMIN_DATA?.candidates || [],
        ballots: [],
      };
    }

    const groups = computeElectionHierarchy(snap);

    // Build hierarchical sheet data:
    // House Header (Row)
    //   Post Header (Row)
    //     Column Headers: Candidate Name | Class & Sec | No. of Votes
    //     Candidate Rows...
    //   (blank spacer row)
    const sheetData = [];
    const merges = [];
    let currentRow = 0;

    groups.forEach((g) => {
      // 1. House Section Header Row (Merged A:C)
      sheetData.push([`${g.icon} ${g.name.toUpperCase()}`, "", ""]);
      merges.push({ s: { r: currentRow, c: 0 }, e: { r: currentRow, c: 2 } });
      currentRow += 1;

      g.posts.forEach((p) => {
        // 2. Post Title & Level Heading Row (Merged A:C)
        const postLabel = p.subtitle ? `📌 ${p.title} (${p.subtitle})` : `📌 ${p.title}`;
        sheetData.push([postLabel, "", ""]);
        merges.push({ s: { r: currentRow, c: 0 }, e: { r: currentRow, c: 2 } });
        currentRow += 1;

        // 3. Table Column Headers
        sheetData.push(["Candidate Name", "Class & Sec", "No. of Votes"]);
        currentRow += 1;

        // 4. Candidates sorted according to number of votes
        p.candidates.forEach((c) => {
          sheetData.push([c.fullName, c.classSec, c.votes]);
          currentRow += 1;
        });

        // 5. Blank row spacer between posts
        sheetData.push(["", "", ""]);
        currentRow += 1;
      });
    });

    const fileName = "School_Election_Results_2026_Official.xlsx";

    // Check if SheetJS XLSX is available
    if (window.XLSX && typeof window.XLSX.utils?.book_new === "function") {
      const wb = window.XLSX.utils.book_new();

      const ws = window.XLSX.utils.aoa_to_sheet(sheetData);
      ws["!cols"] = [
        { wch: 34 }, // Candidate Name
        { wch: 24 }, // Class & Sec
        { wch: 16 }, // No. of Votes
      ];
      ws["!merges"] = merges;

      window.XLSX.utils.book_append_sheet(wb, ws, "Election Results");
      window.XLSX.writeFile(wb, fileName);
    } else {
      // Fallback CSV with exact same layout
      const csvContent = sheetData
        .map((row) =>
          row
            .map((val) => {
              const str = String(val ?? "").replace(/"/g, '""');
              return `"${str}"`;
            })
            .join(",")
        )
        .join("\r\n");

      const blob = new Blob(["\uFEFF" + csvContent], { type: "text/csv;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "School_Election_Results_2026_Official.csv";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }

    showExportToast(fileName);
  }

  window.exportElectionResultsToExcel = exportElectionResultsToExcel;
})();
