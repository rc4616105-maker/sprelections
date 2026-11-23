import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
graphs_html_path = ROOT / "Houses" / "graphs.html"

HTML_CONTENT = '''<!DOCTYPE html>
<html lang="en" data-theme="light">

<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>House Voting Graphs — School House Elections 2026</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link
    href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=JetBrains+Mono:wght@500;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap"
    rel="stylesheet" />
  <style>
    :root {
      --bg-app: #faf6ee;
      --bg-surface: #f3ece0;
      --bg-card: #fffdf9;
      --bg-elevated: #ebe2d2;
      --text-primary: #141413;
      --text-secondary: #4a4741;
      --text-muted: #767167;
      --accent-primary: #cc785c;
      --border-default: #e5dccb;

      --ease-out: cubic-bezier(0.23, 1, 0.32, 1);
      --ease-spring: cubic-bezier(0.175, 0.885, 0.32, 1.15);

      --font-display: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      --font-mono: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      color-scheme: light;
    }

    *,
    *::before,
    *::after {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      min-height: 100svh;
      background:
        radial-gradient(circle at 12% 0%, rgba(234, 179, 8, 0.08), transparent 42%),
        radial-gradient(circle at 88% 0%, rgba(204, 120, 92, 0.1), transparent 45%),
        var(--bg-app);
      color: var(--text-primary);
      font-family: var(--font-sans);
      line-height: 1.5;
      -webkit-font-smoothing: antialiased;
    }

    .container {
      max-width: 1260px;
      margin: 0 auto;
      padding: 2.25rem 1.25rem 3.5rem;
    }

    .topbar {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      flex-wrap: wrap;
      gap: 1rem;
      margin-bottom: 1.75rem;
    }

    .eyebrow {
      font-family: var(--font-mono);
      font-size: 0.76rem;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: var(--text-muted);
      font-weight: 700;
    }

    h1 {
      margin: 0.35rem 0 0.4rem;
      font-family: var(--font-display);
      font-size: clamp(1.9rem, 3.6vw, 2.65rem);
      font-weight: 700;
      letter-spacing: -0.025em;
      line-height: 1.1;
    }

    .subtitle {
      margin: 0;
      color: var(--text-secondary);
      max-width: 62ch;
    }

    .top-actions {
      display: flex;
      align-items: center;
      gap: 0.65rem;
      flex-wrap: wrap;
    }

    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.45rem;
      min-height: 42px;
      padding: 0.55rem 1.1rem;
      border-radius: 10px;
      border: 1px solid var(--border-default);
      background: var(--bg-card);
      color: var(--text-primary);
      font-family: inherit;
      font-size: 0.88rem;
      font-weight: 700;
      text-decoration: none;
      cursor: pointer;
      transition: transform 160ms var(--ease-out), background-color 160ms ease;
    }

    .btn:hover {
      background: var(--bg-surface);
    }

    .btn:active {
      transform: scale(0.97);
    }

    /* KPI Summary Row */
    .summary-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 1rem;
      margin-bottom: 1.75rem;
    }

    .stat-card {
      background: var(--bg-card);
      border: 1px solid var(--border-default);
      border-radius: 14px;
      padding: 1.15rem 1.25rem;
      box-shadow: 0 8px 22px -14px rgba(45, 36, 20, 0.12);
    }

    .stat-label {
      font-size: 0.8rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-secondary);
      display: flex;
      align-items: center;
      gap: 0.35rem;
    }

    .stat-value {
      font-size: 1.95rem;
      font-weight: 800;
      margin: 0.25rem 0 0.1rem;
      font-variant-numeric: tabular-nums;
      display: inline-block;
    }

    .stat-note {
      font-size: 0.78rem;
      color: var(--text-muted);
      font-weight: 600;
    }

    /* Single Graph Sheet Panel Card */
    .panel-card {
      background: var(--bg-card);
      border: 1px solid var(--border-default);
      border-radius: 20px;
      padding: 1.5rem 1.65rem 1.75rem;
      box-shadow: 0 12px 32px -16px rgba(45, 36, 20, 0.14);
      position: relative;
    }

    .panel-head {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 0.75rem;
      margin-bottom: 1.5rem;
      border-bottom: 1px solid rgba(20, 20, 19, 0.07);
      padding-bottom: 1rem;
    }

    .panel-title {
      margin: 0;
      font-size: 1.3rem;
      font-weight: 800;
      letter-spacing: -0.015em;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .panel-caption {
      margin: 0.25rem 0 0;
      font-size: 0.84rem;
      color: var(--text-muted);
    }

    .graph-legend-badge {
      display: inline-flex;
      align-items: center;
      gap: 1.25rem;
      background: var(--bg-app);
      border: 1px solid var(--border-default);
      border-radius: 999px;
      padding: 0.4rem 0.95rem;
      font-size: 0.82rem;
      font-weight: 700;
    }

    .legend-entry {
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
    }

    .legend-bar-sample {
      width: 14px;
      height: 14px;
      border-radius: 4px;
      display: inline-block;
    }

    /* Unified Chart Sheet Container */
    .chart-sheet-wrap {
      padding: 1.5rem 1rem 1rem;
      border-radius: 16px;
      background: var(--bg-app);
      border: 1px solid var(--border-default);
      overflow-x: auto;
    }

    .unified-chart-grid {
      display: grid;
      grid-template-columns: repeat(6, 1fr);
      gap: 1.25rem;
      align-items: end;
      min-height: 290px;
      padding-top: 2rem;
      border-bottom: 2px solid var(--border-default);
    }

    @media (max-width: 900px) {
      .unified-chart-grid {
        min-width: 760px;
      }
      .unified-labels-grid {
        min-width: 760px;
      }
    }

    /* House Cluster: Contains Boys Bar & Girls Bar Side-by-Side */
    .house-bar-cluster {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: flex-end;
      height: 100%;
      position: relative;
    }

    .bars-pair-container {
      display: flex;
      align-items: flex-end;
      justify-content: center;
      gap: 10px;
      width: 100%;
      height: 220px;
    }

    .single-bar-unit {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: flex-end;
      gap: 0.35rem;
      height: 100%;
      flex: 1;
      max-width: 58px;
      position: relative;
    }

    .bar-stat-label {
      font-family: var(--font-mono);
      font-size: 0.74rem;
      font-weight: 800;
      line-height: 1.15;
      text-align: center;
      color: var(--text-primary);
      white-space: nowrap;
    }

    .bar-stat-pct {
      font-size: 0.68rem;
      color: var(--text-muted);
      font-weight: 700;
      display: block;
    }

    .bar-gender-badge {
      font-size: 0.75rem;
      display: block;
      margin-bottom: 1px;
    }

    /* Bar Track & Fill */
    .bar-track {
      width: 100%;
      height: 165px;
      background: rgba(20, 20, 19, 0.05);
      border-radius: 8px 8px 0 0;
      position: relative;
      overflow: hidden;
      border: 1px solid rgba(20, 20, 19, 0.06);
      border-bottom: none;
    }

    .bar-fill {
      position: relative;
      width: 100%;
      height: 100%;
      border-radius: 7px 7px 0 0;
      transform-origin: bottom center;
      transform: scaleY(var(--bar-scale, 0.035));
      opacity: var(--bar-opacity, 0.3);
      transition:
        transform 560ms var(--ease-spring),
        opacity 220ms var(--ease-out);
      will-change: transform;
      overflow: hidden;
    }

    .bar-fill::after {
      content: "";
      position: absolute;
      inset: 0;
      background: linear-gradient(180deg, rgba(255, 255, 255, 0.45) 0%, rgba(255, 255, 255, 0) 65%);
      opacity: 0;
      transform: translateY(100%);
      pointer-events: none;
    }

    .single-bar-unit.is-rising .bar-fill::after {
      animation: barRiseGlow 750ms var(--ease-out);
    }

    .single-bar-unit.is-rising .bar-stat-label,
    .stat-value.is-bumping {
      animation: numberBump 320ms var(--ease-out);
    }

    @keyframes barRiseGlow {
      0% { opacity: 0.85; transform: translateY(100%); }
      100% { opacity: 0; transform: translateY(-20%); }
    }

    @keyframes numberBump {
      0% { transform: scale(1); }
      45% { transform: scale(1.14); }
      100% { transform: scale(1); }
    }

    /* Labels Grid at Bottom of Unified Chart */
    .unified-labels-grid {
      display: grid;
      grid-template-columns: repeat(6, 1fr);
      gap: 1.25rem;
      padding: 0.9rem 0 0.25rem;
      text-align: center;
    }

    .house-cluster-label {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 0.15rem;
    }

    .house-label-name {
      font-family: var(--font-display);
      font-size: 0.96rem;
      font-weight: 800;
      letter-spacing: -0.01em;
    }

    .house-sub-sublabel {
      font-size: 0.74rem;
      color: var(--text-muted);
      font-weight: 700;
    }

    .house-total-badge {
      font-family: var(--font-mono);
      font-size: 0.72rem;
      font-weight: 800;
      padding: 0.12rem 0.5rem;
      border-radius: 999px;
      margin-top: 2px;
      background: rgba(20, 20, 19, 0.05);
      color: var(--text-secondary);
    }

    /* Floating +1 / +N vote animation badge */
    .vote-plus-one {
      position: absolute;
      top: -10px;
      left: 50%;
      transform: translate(-50%, 0);
      font-family: var(--font-mono);
      font-size: 0.8rem;
      font-weight: 800;
      color: #059669;
      background: #ecfdf5;
      border: 1px solid rgba(5, 150, 105, 0.45);
      border-radius: 9999px;
      padding: 0.1rem 0.45rem;
      pointer-events: none;
      z-index: 20;
      box-shadow: 0 4px 12px rgba(5, 150, 105, 0.28);
      animation: floatPlusOneUp 1.25s cubic-bezier(0.22, 1, 0.36, 1) forwards;
    }

    @keyframes floatPlusOneUp {
      0% { opacity: 0; transform: translate(-50%, 10px) scale(0.65); }
      22% { opacity: 1; transform: translate(-50%, -4px) scale(1.15); }
      75% { opacity: 1; transform: translate(-50%, -24px) scale(1); }
      100% { opacity: 0; transform: translate(-50%, -38px) scale(0.9); }
    }

    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
      }
    }
  </style>
</head>

<body>
  <main class="container">
    <header class="topbar">
      <div>
        <div class="eyebrow">School House Elections 2026</div>
        <h1>House Voting Turnout Graphs</h1>
        <p class="subtitle">Live voter turnout breakdown across all 6 houses with side-by-side Boys and Girls bar graphs for each house.</p>
      </div>
      <div class="top-actions">
        <a id="back-btn" href="./index.html" class="btn">← Back</a>
      </div>
    </header>

    <!-- 4 KPI Summary Cards -->
    <section class="summary-grid" aria-label="School turnout totals">
      <div class="stat-card">
        <div class="stat-label">Total Voted</div>
        <div id="g-voted" class="stat-value">0 / 0</div>
        <div id="g-pct" class="stat-note">0% overall turnout</div>
      </div>
      <div class="stat-card" style="border-left: 4px solid #0284c7;">
        <div class="stat-label" style="color: #0369a1;">👦 Boys Turnout</div>
        <div id="g-boys-voted" class="stat-value" style="color: #0369a1;">0 / 0</div>
        <div id="g-boys-pct" class="stat-note">0% boys turnout</div>
      </div>
      <div class="stat-card" style="border-left: 4px solid #db2777;">
        <div class="stat-label" style="color: #be185d;">👧 Girls Turnout</div>
        <div id="g-girls-voted" class="stat-value" style="color: #be185d;">0 / 0</div>
        <div id="g-girls-pct" class="stat-note">0% girls turnout</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Pending to Vote</div>
        <div id="g-remaining" class="stat-value">0</div>
        <div class="stat-note">Students remaining</div>
      </div>
    </section>

    <!-- 1 Single Graph Sheet: Each House Has 2 Bars (Boys & Girls Side-by-Side) -->
    <section class="panel-card" aria-label="House turnout comparison">
      <div class="panel-head">
        <div>
          <h2 class="panel-title">
            <span>📊 House-Wise Voter Turnout (Boys &amp; Girls in 1 Graph)</span>
          </h2>
          <p class="panel-caption">Side-by-side comparison of boy and girl voter turnout across all 6 houses, rendered in house brand colors.</p>
        </div>

        <div class="graph-legend-badge">
          <span class="legend-entry">
            <span class="legend-bar-sample" style="background: #475569;"></span>
            <span>👦 Boys Bar (Solid House Color)</span>
          </span>
          <span class="legend-entry">
            <span class="legend-bar-sample" style="background: linear-gradient(180deg, #ffffff 0%, #475569 85%); border:1px solid #475569;"></span>
            <span>👧 Girls Bar (Light Gradient House Color)</span>
          </span>
        </div>
      </div>

      <div class="chart-sheet-wrap">
        <div id="unified-chart-grid" class="unified-chart-grid"></div>
        <div id="unified-labels-grid" class="unified-labels-grid"></div>
      </div>
    </section>
  </main>

  <script defer src="./admin/data.js?v=20261122s"></script>
  <script defer src="./admin/teachers.js?v=20261122s"></script>
  <script defer src="./admin/supabase-config.js?v=20261122s"></script>
  <script defer>
    window.addEventListener("DOMContentLoaded", () => {
      const { houses } = window.ADMIN_DATA;
      const params = new URLSearchParams(window.location.search);
      const backBtn = document.getElementById("back-btn");
      if (params.get("from") === "admin") {
        backBtn.href = "./admin/index.html";
        backBtn.textContent = "← Back to Admin";
      } else {
        backBtn.href = "./index.html";
        backBtn.textContent = "← Back to Houses";
      }

      const el = {
        voted: document.getElementById("g-voted"),
        pct: document.getElementById("g-pct"),
        boysVoted: document.getElementById("g-boys-voted"),
        boysPct: document.getElementById("g-boys-pct"),
        girlsVoted: document.getElementById("g-girls-voted"),
        girlsPct: document.getElementById("g-girls-pct"),
        remaining: document.getElementById("g-remaining"),

        chartGrid: document.getElementById("unified-chart-grid"),
        labelsGrid: document.getElementById("unified-labels-grid"),
      };

      const sixHouses = houses.filter((h) => h.code !== "ALL" && h.code !== "CENTRAL");
      const houseNodes = new Map();

      const prevCounts = new Map();
      let prevTotalVoted = null;
      let isMounted = false;

      function isBoyStudent(s) {
        const g = String(s?.gender || "").trim().toUpperCase();
        return g === "M" || g === "BOY" || g === "MALE";
      }
      function isGirlStudent(s) {
        const g = String(s?.gender || "").trim().toUpperCase();
        return g === "F" || g === "GIRL" || g === "FEMALE";
      }

      // Build DOM Nodes: 1 Unified Graph Sheet where each House has 2 Bars (Boys & Girls)
      function initNodes() {
        sixHouses.forEach((h) => {
          // Cluster column for this house
          const clusterCol = document.createElement("div");
          clusterCol.className = "house-bar-cluster";

          // Boys bar uses solid house accent; Girls bar uses lighter gradient of house accent
          clusterCol.innerHTML = `
            <div class="bars-pair-container">
              <!-- Boys Bar Unit -->
              <div class="single-bar-unit unit-boys" title="${h.name} Boys">
                <div class="bar-stat-label label-boys">
                  <span class="bar-gender-badge">👦</span>
                  <span class="b-fraction">0 / 0</span>
                  <span class="bar-stat-pct b-pct">0%</span>
                </div>
                <div class="bar-track">
                  <div class="bar-fill bar-fill-boys" style="background: ${h.accent}; --bar-scale: 0; --bar-opacity: 0.28;"></div>
                </div>
              </div>

              <!-- Girls Bar Unit -->
              <div class="single-bar-unit unit-girls" title="${h.name} Girls">
                <div class="bar-stat-label label-girls">
                  <span class="bar-gender-badge">👧</span>
                  <span class="g-fraction">0 / 0</span>
                  <span class="bar-stat-pct g-pct">0%</span>
                </div>
                <div class="bar-track">
                  <div class="bar-fill bar-fill-girls" style="background: linear-gradient(180deg, #ffffff 0%, ${h.accent} 78%); border: 1.5px solid ${h.accent}; --bar-scale: 0; --bar-opacity: 0.28;"></div>
                </div>
              </div>
            </div>
          `;
          el.chartGrid.appendChild(clusterCol);

          // House Label below the cluster
          const labelCol = document.createElement("div");
          labelCol.className = "house-cluster-label";
          labelCol.innerHTML = `
            <span class="house-label-name" style="color: ${h.accentText};">${h.name}</span>
            <span class="house-sub-sublabel">👦 Boys &bull; 👧 Girls</span>
            <span class="house-total-badge total-badge">0 / 0 Total</span>
          `;
          el.labelsGrid.appendChild(labelCol);

          houseNodes.set(h.code, {
            clusterCol,
            boysUnit: clusterCol.querySelector(".unit-boys"),
            bFraction: clusterCol.querySelector(".b-fraction"),
            bPct: clusterCol.querySelector(".b-pct"),
            bFill: clusterCol.querySelector(".bar-fill-boys"),

            girlsUnit: clusterCol.querySelector(".unit-girls"),
            gFraction: clusterCol.querySelector(".g-fraction"),
            gPct: clusterCol.querySelector(".g-pct"),
            gFill: clusterCol.querySelector(".bar-fill-girls"),

            totalBadge: labelCol.querySelector(".total-badge"),
          });
        });
      }

      function triggerPulse(nodeList, className, durationMs) {
        nodeList.forEach((n) => {
          if (!n) return;
          n.classList.remove(className);
          void n.offsetWidth;
          n.classList.add(className);
          setTimeout(() => n.classList.remove(className), durationMs);
        });
      }

      function updateGraphInPlace(snap) {
        const students = snap.students || window.ADMIN_DATA?.students || [];
        const activeStudents = students.filter((s) => s.isActive && s.admissionNo !== "0000");

        const acceptedAll = (snap.ballots || []).filter((b) => b.status === "accepted");
        const acceptedVotersSet = new Set(acceptedAll.map((b) => String(b.admissionNo).toUpperCase()));

        // Global Totals
        const totalEligible = activeStudents.length;
        const totalVoted = activeStudents.filter((s) => acceptedVotersSet.has(String(s.admissionNo).toUpperCase())).length;
        const overallPct = totalEligible ? Math.round((totalVoted / totalEligible) * 100) : 0;

        // Boys Global
        const boysEligible = activeStudents.filter((s) => isBoyStudent(s)).length;
        const boysVoted = activeStudents.filter((s) => isBoyStudent(s) && acceptedVotersSet.has(String(s.admissionNo).toUpperCase())).length;
        const boysPct = boysEligible ? Math.round((boysVoted / boysEligible) * 100) : 0;

        // Girls Global
        const girlsEligible = activeStudents.filter((s) => isGirlStudent(s)).length;
        const girlsVoted = activeStudents.filter((s) => isGirlStudent(s) && acceptedVotersSet.has(String(s.admissionNo).toUpperCase())).length;
        const girlsPct = girlsEligible ? Math.round((girlsVoted / girlsEligible) * 100) : 0;

        // Update Top KPIs
        el.voted.textContent = `${totalVoted} / ${totalEligible}`;
        el.pct.textContent = `${overallPct}% overall turnout (${acceptedAll.length} ballots)`;
        el.boysVoted.textContent = `${boysVoted} / ${boysEligible}`;
        el.boysPct.textContent = `${boysPct}% boys turnout`;
        el.girlsVoted.textContent = `${girlsVoted} / ${girlsEligible}`;
        el.girlsPct.textContent = `${girlsPct}% girls turnout`;
        el.remaining.textContent = String(Math.max(0, totalEligible - totalVoted));

        if (prevTotalVoted !== null && totalVoted !== prevTotalVoted) {
          triggerPulse([el.voted, el.remaining, el.boysVoted, el.girlsVoted], "is-bumping", 360);
        }
        prevTotalVoted = totalVoted;

        const applyBars = () => {
          sixHouses.forEach((h) => {
            const hStudents = activeStudents.filter((s) => s.houseCode === h.code);

            // House Boys
            const bEligible = hStudents.filter((s) => isBoyStudent(s)).length;
            const bVoted = hStudents.filter((s) => isBoyStudent(s) && acceptedVotersSet.has(String(s.admissionNo).toUpperCase())).length;
            const bRatio = bEligible ? bVoted / bEligible : 0;
            const bPct = Math.round(bRatio * 100);

            // House Girls
            const gEligible = hStudents.filter((s) => isGirlStudent(s)).length;
            const gVoted = hStudents.filter((s) => isGirlStudent(s) && acceptedVotersSet.has(String(s.admissionNo).toUpperCase())).length;
            const gRatio = gEligible ? gVoted / gEligible : 0;
            const gPct = Math.round(gRatio * 100);

            // House Total
            const hTotalEligible = bEligible + gEligible;
            const hTotalVoted = bVoted + gVoted;
            const hTotalPct = hTotalEligible ? Math.round((hTotalVoted / hTotalEligible) * 100) : 0;

            const node = houseNodes.get(h.code);
            if (!node) return;

            // 1. Update Boys Bar
            node.bFraction.textContent = `${bVoted} / ${bEligible}`;
            node.bPct.textContent = `${bPct}%`;
            const bVisualScale = bVoted === 0 ? 0.035 : Math.max(0.08, bRatio);
            node.bFill.style.setProperty("--bar-scale", bVisualScale.toFixed(4));
            node.bFill.style.setProperty("--bar-opacity", bVoted === 0 ? "0.28" : "1");

            // 2. Update Girls Bar
            node.gFraction.textContent = `${gVoted} / ${gEligible}`;
            node.gPct.textContent = `${gPct}%`;
            const gVisualScale = gVoted === 0 ? 0.035 : Math.max(0.08, gRatio);
            node.gFill.style.setProperty("--bar-scale", gVisualScale.toFixed(4));
            node.gFill.style.setProperty("--bar-opacity", gVoted === 0 ? "0.28" : "1");

            // 3. Update House Total Label
            node.totalBadge.textContent = `${hTotalVoted} / ${hTotalEligible} Total (${hTotalPct}%)`;

            // Animate pulses on vote increment
            const prevB = prevCounts.get(`${h.code}_b`);
            if (prevB !== undefined && bVoted > prevB) {
              const diff = bVoted - prevB;
              const badge = document.createElement("span");
              badge.className = "vote-plus-one";
              badge.textContent = `+${diff}`;
              node.boysUnit.appendChild(badge);
              setTimeout(() => badge.remove(), 1250);
              triggerPulse([node.boysUnit], "is-rising", 800);
            }

            const prevG = prevCounts.get(`${h.code}_g`);
            if (prevG !== undefined && gVoted > prevG) {
              const diff = gVoted - prevG;
              const badge = document.createElement("span");
              badge.className = "vote-plus-one";
              badge.textContent = `+${diff}`;
              node.girlsUnit.appendChild(badge);
              setTimeout(() => badge.remove(), 1250);
              triggerPulse([node.girlsUnit], "is-rising", 800);
            }

            prevCounts.set(`${h.code}_b`, bVoted);
            prevCounts.set(`${h.code}_g`, gVoted);
          });
        };

        if (!isMounted) {
          isMounted = true;
          requestAnimationFrame(() => requestAnimationFrame(applyBars));
        } else {
          applyBars();
        }
      }

      let isRefreshing = false;
      async function refreshInPlace() {
        if (isRefreshing) return;
        isRefreshing = true;
        try {
          const snap = await window.AdminBackend.getSnapshot();
          updateGraphInPlace(snap);
        } catch (err) {
          console.warn("Unable to load graphs snapshot:", err);
        } finally {
          isRefreshing = false;
        }
      }

      async function boot() {
        initNodes();

        // Frame 1 immediate cache render
        let initialBallots = [];
        try {
          const cached = JSON.parse(localStorage.getItem("spr_admin_snapshot_cache") || "null");
          if (cached && Array.isArray(cached.ballots)) initialBallots = cached.ballots;
        } catch (_) {}

        const initialStudents = [
          ...(window.ADMIN_DATA?.students || []),
          ...(window.ADMIN_DATA?.teachers || window.TEACHERS_DATA || []),
        ];

        updateGraphInPlace({
          students: initialStudents,
          ballots: initialBallots,
        });

        // Supabase / Backend live sync
        if (window.AdminBackend) {
          await window.AdminBackend.init();
          await refreshInPlace();
          window.AdminBackend.subscribeUpdates(async () => {
            await refreshInPlace();
          });
        }

        setInterval(refreshInPlace, 2000);
      }

      boot();
    });
  </script>
</body>

</html>
'''

graphs_html_path.write_text(HTML_CONTENT, encoding="utf-8")
print("Saved Houses/graphs.html cleanly with 1 single graph sheet!")
