import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
graphs_html_path = ROOT / "Houses" / "graphs.html"

NEW_GRAPHS_HTML = '''<!DOCTYPE html>
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
      max-width: 1240px;
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
      margin-bottom: 1.5rem;
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

    /* View Switcher Controls */
    .view-switcher-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 0.75rem;
      background: var(--bg-card);
      border: 1px solid var(--border-default);
      border-radius: 14px;
      padding: 0.75rem 1.1rem;
      margin-bottom: 1.5rem;
      box-shadow: 0 4px 14px -8px rgba(45, 36, 20, 0.08);
    }

    .view-pills-group {
      display: flex;
      gap: 0.45rem;
      flex-wrap: wrap;
    }

    .btn-view-pill {
      padding: 0.45rem 0.95rem;
      border-radius: 999px;
      border: 1.5px solid #cbd5e1;
      background: #ffffff;
      color: var(--text-secondary);
      font-family: inherit;
      font-size: 0.84rem;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      transition: all 180ms ease;
    }

    .btn-view-pill:hover {
      border-color: #94a3b8;
      background: #f8fafc;
      color: var(--text-primary);
    }

    .btn-view-pill.is-active {
      background: #0f172a;
      color: #ffffff;
      border-color: #0f172a;
      box-shadow: 0 3px 10px rgba(15, 23, 42, 0.18);
    }

    .graph-legend {
      display: flex;
      align-items: center;
      gap: 1rem;
      font-size: 0.84rem;
      font-weight: 700;
    }

    .legend-item {
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
    }

    .legend-color-dot {
      width: 12px;
      height: 12px;
      border-radius: 3px;
      display: inline-block;
    }

    /* Two-Column Graphs Grid */
    .graphs-container-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 1.5rem;
      margin-bottom: 2rem;
    }

    @media (max-width: 960px) {
      .graphs-container-grid {
        grid-template-columns: 1fr;
      }
    }

    .panel-card {
      background: var(--bg-card);
      border: 1px solid var(--border-default);
      border-radius: 18px;
      padding: 1.35rem 1.4rem;
      box-shadow: 0 12px 28px -16px rgba(45, 36, 20, 0.12);
      position: relative;
    }

    .panel-head {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      flex-wrap: wrap;
      gap: 0.5rem;
      margin-bottom: 1.25rem;
      border-bottom: 1px solid rgba(20, 20, 19, 0.06);
      padding-bottom: 0.75rem;
    }

    .panel-title {
      margin: 0;
      font-size: 1.22rem;
      font-weight: 800;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .panel-caption {
      margin: 0.25rem 0 0;
      font-size: 0.82rem;
      color: var(--text-muted);
    }

    .badge-pill {
      font-family: var(--font-mono);
      font-size: 0.78rem;
      font-weight: 800;
      padding: 0.2rem 0.65rem;
      border-radius: 999px;
      letter-spacing: 0.02em;
    }

    /* Vertical Chart Components */
    .chart-wrap {
      padding: 1.25rem 0.85rem 0.65rem;
      border-radius: 14px;
      background: var(--bg-app);
      border: 1px solid var(--border-default);
    }

    .chart-grid {
      display: grid;
      grid-template-columns: repeat(6, minmax(75px, 1fr));
      gap: 0.85rem;
      align-items: end;
      min-height: 260px;
      padding-top: 1.6rem;
      border-bottom: 2px solid var(--border-default);
      overflow-x: auto;
    }

    .chart-col {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: flex-end;
      gap: 0.4rem;
      height: 100%;
      position: relative;
    }

    .col-fraction {
      font-family: var(--font-mono);
      font-size: 0.82rem;
      font-weight: 800;
      color: var(--text-primary);
      display: inline-block;
      white-space: nowrap;
    }

    .col-pct {
      font-family: var(--font-mono);
      font-size: 0.74rem;
      color: var(--text-muted);
      font-weight: 700;
    }

    .col-track {
      width: 100%;
      max-width: 58px;
      height: 185px;
      background: rgba(20, 20, 19, 0.05);
      border-radius: 9px 9px 0 0;
      position: relative;
      overflow: hidden;
      border: 1px solid rgba(20, 20, 19, 0.06);
      border-bottom: none;
    }

    /* Dual Track for Grouped 1-Graph mode */
    .col-dual-track {
      display: flex;
      gap: 6px;
      align-items: flex-end;
      width: 100%;
      max-width: 88px;
      height: 185px;
    }

    .col-half-track {
      flex: 1;
      height: 100%;
      background: rgba(20, 20, 19, 0.05);
      border-radius: 7px 7px 0 0;
      position: relative;
      overflow: hidden;
      border: 1px solid rgba(20, 20, 19, 0.06);
      border-bottom: none;
    }

    .col-bar {
      position: relative;
      width: 100%;
      height: 100%;
      border-radius: 8px 8px 0 0;
      transform-origin: bottom center;
      transform: scaleY(var(--bar-scale, 0.035));
      opacity: var(--bar-opacity, 0.3);
      transition:
        transform 560ms var(--ease-spring),
        opacity 220ms var(--ease-out);
      will-change: transform;
      overflow: hidden;
    }

    .col-bar::after {
      content: "";
      position: absolute;
      inset: 0;
      background: linear-gradient(180deg, rgba(255, 255, 255, 0.45) 0%, rgba(255, 255, 255, 0) 65%);
      opacity: 0;
      transform: translateY(100%);
      pointer-events: none;
    }

    .chart-col.is-rising .col-bar::after {
      animation: barRiseGlow 750ms var(--ease-out);
    }

    .chart-col.is-rising .col-fraction,
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

    .chart-labels {
      display: grid;
      grid-template-columns: repeat(6, minmax(75px, 1fr));
      gap: 0.85rem;
      padding: 0.75rem 0 0.25rem;
      text-align: center;
      overflow-x: auto;
    }

    .col-house-name {
      font-family: var(--font-display);
      font-size: 0.94rem;
      font-weight: 800;
      white-space: nowrap;
    }

    /* Single Combined Grouped Graph Container */
    #combined-graph-panel {
      margin-bottom: 2rem;
    }

    .combined-labels-sub {
      font-size: 0.72rem;
      color: var(--text-muted);
      margin-top: 2px;
      font-weight: 700;
    }

    /* Floating +1 / +N badge */
    .vote-plus-one {
      position: absolute;
      top: 14px;
      left: 50%;
      transform: translate(-50%, 0);
      font-family: var(--font-mono);
      font-size: 0.84rem;
      font-weight: 800;
      color: #059669;
      background: #ecfdf5;
      border: 1px solid rgba(5, 150, 105, 0.45);
      border-radius: 9999px;
      padding: 0.12rem 0.5rem;
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
        <p class="subtitle">Live voter turnout breakdown across all 6 houses with dedicated Boys and Girls comparison graphs.</p>
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

    <!-- View Mode Switcher -->
    <div class="view-switcher-bar">
      <div class="view-pills-group">
        <button type="button" class="btn-view-pill is-active" data-view-mode="two-graphs">
          <span>👥 2 Graphs (Boys &amp; Girls)</span>
        </button>
        <button type="button" class="btn-view-pill" data-view-mode="combined-one">
          <span>📊 1 Graph (Grouped Bars)</span>
        </button>
        <button type="button" class="btn-view-pill" data-view-mode="boys-only">
          <span>👦 Boys Only</span>
        </button>
        <button type="button" class="btn-view-pill" data-view-mode="girls-only">
          <span>👧 Girls Only</span>
        </button>
      </div>

      <div class="graph-legend">
        <span class="legend-item"><span class="legend-color-dot" style="background:#0284c7;"></span> 👦 Boys</span>
        <span class="legend-item"><span class="legend-color-dot" style="background:#db2777;"></span> 👧 Girls</span>
      </div>
    </div>

    <!-- VIEW 1: Two Separate Graphs (Boys Graph & Girls Graph Side-by-Side) -->
    <section id="two-graphs-section" class="graphs-container-grid">
      <!-- 1. Boys Turnout Graph -->
      <div id="boys-graph-card" class="panel-card" style="border-top: 4px solid #0284c7;">
        <div class="panel-head">
          <div>
            <h2 class="panel-title" style="color: #0369a1;">
              <span>👦 Boys House Turnout</span>
            </h2>
            <p class="panel-caption">Live votes cast by boys across all six houses</p>
          </div>
          <span id="boys-card-pill" class="badge-pill" style="background: #e0f2fe; color: #0369a1;">0 / 0 Voted (0%)</span>
        </div>

        <div class="chart-wrap">
          <div id="boys-chart-grid" class="chart-grid"></div>
          <div id="boys-chart-labels" class="chart-labels"></div>
        </div>
      </div>

      <!-- 2. Girls Turnout Graph -->
      <div id="girls-graph-card" class="panel-card" style="border-top: 4px solid #db2777;">
        <div class="panel-head">
          <div>
            <h2 class="panel-title" style="color: #be185d;">
              <span>👧 Girls House Turnout</span>
            </h2>
            <p class="panel-caption">Live votes cast by girls across all six houses</p>
          </div>
          <span id="girls-card-pill" class="badge-pill" style="background: #fce7f3; color: #be185d;">0 / 0 Voted (0%)</span>
        </div>

        <div class="chart-wrap">
          <div id="girls-chart-grid" class="chart-grid"></div>
          <div id="girls-chart-labels" class="chart-labels"></div>
        </div>
      </div>
    </section>

    <!-- VIEW 2: 1 Graph (Grouped Side-by-Side Bars for Each House) -->
    <section id="combined-graph-panel" class="panel-card" hidden>
      <div class="panel-head">
        <div>
          <h2 class="panel-title">
            <span>📊 House Turnout Comparison (Boys &amp; Girls in 1 Graph)</span>
          </h2>
          <p class="panel-caption">Direct comparison of boy and girl voters in each house side-by-side</p>
        </div>
        <div class="graph-legend">
          <span class="legend-item"><span class="legend-color-dot" style="background:#0284c7;"></span> Boys</span>
          <span class="legend-item"><span class="legend-color-dot" style="background:#db2777;"></span> Girls</span>
        </div>
      </div>

      <div class="chart-wrap">
        <div id="combined-chart-grid" class="chart-grid" style="min-height: 275px;"></div>
        <div id="combined-chart-labels" class="chart-labels"></div>
      </div>
    </section>
  </main>

  <script defer src="./admin/data.js?v=20261122p"></script>
  <script defer src="./admin/teachers.js?v=20261122p"></script>
  <script defer src="./admin/supabase-config.js?v=20261122p"></script>
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

        // Two graphs view
        twoGraphsSection: document.getElementById("two-graphs-section"),
        boysGraphCard: document.getElementById("boys-graph-card"),
        girlsGraphCard: document.getElementById("girls-graph-card"),
        boysCardPill: document.getElementById("boys-card-pill"),
        girlsCardPill: document.getElementById("girls-card-pill"),
        boysChartGrid: document.getElementById("boys-chart-grid"),
        boysChartLabels: document.getElementById("boys-chart-labels"),
        girlsChartGrid: document.getElementById("girls-chart-grid"),
        girlsChartLabels: document.getElementById("girls-chart-labels"),

        // 1 Graph view
        combinedGraphPanel: document.getElementById("combined-graph-panel"),
        combinedChartGrid: document.getElementById("combined-chart-grid"),
        combinedChartLabels: document.getElementById("combined-chart-labels"),

        // Pills
        viewPills: document.querySelectorAll(".btn-view-pill"),
      };

      const sixHouses = houses.filter((h) => h.code !== "ALL" && h.code !== "CENTRAL");
      const boysNodes = new Map();
      const girlsNodes = new Map();
      const combinedNodes = new Map();

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

      // Initialize View Switcher
      el.viewPills.forEach((pill) => {
        pill.addEventListener("click", () => {
          el.viewPills.forEach((p) => p.classList.remove("is-active"));
          pill.classList.add("is-active");
          const mode = pill.dataset.viewMode;

          if (mode === "combined-one") {
            el.twoGraphsSection.hidden = true;
            el.combinedGraphPanel.hidden = false;
          } else if (mode === "boys-only") {
            el.twoGraphsSection.hidden = false;
            el.twoGraphsSection.style.gridTemplateColumns = "1fr";
            el.boysGraphCard.hidden = false;
            el.girlsGraphCard.hidden = true;
            el.combinedGraphPanel.hidden = true;
          } else if (mode === "girls-only") {
            el.twoGraphsSection.hidden = false;
            el.twoGraphsSection.style.gridTemplateColumns = "1fr";
            el.boysGraphCard.hidden = true;
            el.girlsGraphCard.hidden = false;
            el.combinedGraphPanel.hidden = true;
          } else {
            // two-graphs side-by-side
            el.twoGraphsSection.hidden = false;
            el.twoGraphsSection.style.gridTemplateColumns = window.innerWidth > 960 ? "repeat(2, 1fr)" : "1fr";
            el.boysGraphCard.hidden = false;
            el.girlsGraphCard.hidden = false;
            el.combinedGraphPanel.hidden = true;
          }
        });
      });

      window.addEventListener("resize", () => {
        const activePill = document.querySelector(".btn-view-pill.is-active");
        if (activePill && activePill.dataset.viewMode === "two-graphs") {
          el.twoGraphsSection.style.gridTemplateColumns = window.innerWidth > 960 ? "repeat(2, 1fr)" : "1fr";
        }
      });

      // Build DOM Nodes
      function initNodes() {
        sixHouses.forEach((h) => {
          // --- 1. Boys Chart Column ---
          const bCol = document.createElement("div");
          bCol.className = "chart-col";
          bCol.innerHTML = `
            <div class="col-fraction">0 / 0</div>
            <div class="col-pct">0%</div>
            <div class="col-track">
              <div class="col-bar" style="background: linear-gradient(180deg, #38bdf8 0%, #0284c7 100%); --bar-scale: 0; --bar-opacity: 0.28;"></div>
            </div>
          `;
          el.boysChartGrid.appendChild(bCol);

          const bLbl = document.createElement("div");
          bLbl.className = "col-house-name";
          bLbl.style.color = h.accentText;
          bLbl.textContent = h.name;
          el.boysChartLabels.appendChild(bLbl);

          boysNodes.set(h.code, {
            col: bCol,
            fraction: bCol.querySelector(".col-fraction"),
            pct: bCol.querySelector(".col-pct"),
            bar: bCol.querySelector(".col-bar"),
          });

          // --- 2. Girls Chart Column ---
          const gCol = document.createElement("div");
          gCol.className = "chart-col";
          gCol.innerHTML = `
            <div class="col-fraction">0 / 0</div>
            <div class="col-pct">0%</div>
            <div class="col-track">
              <div class="col-bar" style="background: linear-gradient(180deg, #f472b6 0%, #db2777 100%); --bar-scale: 0; --bar-opacity: 0.28;"></div>
            </div>
          `;
          el.girlsChartGrid.appendChild(gCol);

          const gLbl = document.createElement("div");
          gLbl.className = "col-house-name";
          gLbl.style.color = h.accentText;
          gLbl.textContent = h.name;
          el.girlsChartLabels.appendChild(gLbl);

          girlsNodes.set(h.code, {
            col: gCol,
            fraction: gCol.querySelector(".col-fraction"),
            pct: gCol.querySelector(".col-pct"),
            bar: gCol.querySelector(".col-bar"),
          });

          // --- 3. Combined Grouped Dual Bars ---
          const cCol = document.createElement("div");
          cCol.className = "chart-col";
          cCol.innerHTML = `
            <div style="font-family:var(--font-mono); font-size:0.75rem; font-weight:800; text-align:center; line-height:1.2; margin-bottom:0.25rem;">
              <div class="c-boys-text" style="color:#0284c7;">B: 0/0 (0%)</div>
              <div class="c-girls-text" style="color:#db2777;">G: 0/0 (0%)</div>
            </div>
            <div class="col-dual-track">
              <div class="col-half-track" title="Boys">
                <div class="col-bar c-bar-boys" style="background: linear-gradient(180deg, #38bdf8 0%, #0284c7 100%); --bar-scale: 0;"></div>
              </div>
              <div class="col-half-track" title="Girls">
                <div class="col-bar c-bar-girls" style="background: linear-gradient(180deg, #f472b6 0%, #db2777 100%); --bar-scale: 0;"></div>
              </div>
            </div>
          `;
          el.combinedChartGrid.appendChild(cCol);

          const cLbl = document.createElement("div");
          cLbl.className = "col-house-name";
          cLbl.style.color = h.accentText;
          cLbl.innerHTML = `
            <div>${h.name}</div>
            <div class="combined-labels-sub">👦 Boys &bull; 👧 Girls</div>
          `;
          el.combinedChartLabels.appendChild(cLbl);

          combinedNodes.set(h.code, {
            col: cCol,
            boysText: cCol.querySelector(".c-boys-text"),
            girlsText: cCol.querySelector(".c-girls-text"),
            boysBar: cCol.querySelector(".c-bar-boys"),
            girlsBar: cCol.querySelector(".c-bar-girls"),
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

        if (el.boysCardPill) el.boysCardPill.textContent = `${boysVoted} / ${boysEligible} Voted (${boysPct}%)`;
        if (el.girlsCardPill) el.girlsCardPill.textContent = `${girlsVoted} / ${girlsEligible} Voted (${girlsPct}%)`;

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

            // Update Boys Graph Column
            const bNode = boysNodes.get(h.code);
            if (bNode) {
              bNode.fraction.textContent = `${bVoted} / ${bEligible}`;
              bNode.pct.textContent = `${bPct}%`;
              const visualScaleY = bVoted === 0 ? 0.035 : Math.max(0.08, bRatio);
              bNode.bar.style.setProperty("--bar-scale", visualScaleY.toFixed(4));
              bNode.bar.style.setProperty("--bar-opacity", bVoted === 0 ? "0.28" : "1");
            }

            // Update Girls Graph Column
            const gNode = girlsNodes.get(h.code);
            if (gNode) {
              gNode.fraction.textContent = `${gVoted} / ${gEligible}`;
              gNode.pct.textContent = `${gPct}%`;
              const visualScaleY = gVoted === 0 ? 0.035 : Math.max(0.08, gRatio);
              gNode.bar.style.setProperty("--bar-scale", visualScaleY.toFixed(4));
              gNode.bar.style.setProperty("--bar-opacity", gVoted === 0 ? "0.28" : "1");
            }

            // Update Combined Dual Bars
            const cNode = combinedNodes.get(h.code);
            if (cNode) {
              cNode.boysText.textContent = `👦 B: ${bVoted}/${bEligible} (${bPct}%)`;
              cNode.girlsText.textContent = `👧 G: ${gVoted}/${gEligible} (${gPct}%)`;
              const bScale = bVoted === 0 ? 0.035 : Math.max(0.08, bRatio);
              const gScale = gVoted === 0 ? 0.035 : Math.max(0.08, gRatio);
              cNode.boysBar.style.setProperty("--bar-scale", bScale.toFixed(4));
              cNode.girlsBar.style.setProperty("--bar-scale", gScale.toFixed(4));
            }

            // Animate pulses on vote increment
            const prevKey = `${h.code}_total`;
            const hTotalVoted = bVoted + gVoted;
            const prev = prevCounts.get(prevKey);
            if (prev !== undefined && hTotalVoted > prev) {
              const diff = hTotalVoted - prev;
              if (bNode && bVoted > (prevCounts.get(`${h.code}_b`) || 0)) {
                const badge = document.createElement("span");
                badge.className = "vote-plus-one";
                badge.textContent = `+${diff}`;
                bNode.col.appendChild(badge);
                setTimeout(() => badge.remove(), 1250);
                triggerPulse([bNode.col], "is-rising", 800);
              }
              if (gNode && gVoted > (prevCounts.get(`${h.code}_g`) || 0)) {
                const badge = document.createElement("span");
                badge.className = "vote-plus-one";
                badge.textContent = `+${diff}`;
                gNode.col.appendChild(badge);
                setTimeout(() => badge.remove(), 1250);
                triggerPulse([gNode.col], "is-rising", 800);
              }
            }
            prevCounts.set(prevKey, hTotalVoted);
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

graphs_html_path.write_text(NEW_GRAPHS_HTML, encoding="utf-8")
print("Saved Houses/graphs.html successfully!")
