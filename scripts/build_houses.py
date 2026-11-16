from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from parse_roster import (
    HOUSES,
    CENTRAL_HOUSE,
    XLSX_PATH,
    build_admin_data_js,
    build_demo_candidates,
    build_unassigned_markdown,
    get_positions,
    get_central_positions,
    parse_xlsx,
)

STUDENTS, BLANK_HOUSE_STUDENTS, _HOUSE_COUNTS = parse_xlsx(XLSX_PATH)
CANDIDATES = build_demo_candidates()
POSITIONS = get_positions()

def build_index_html(house: dict) -> str:
    is_central = house.get("slug") == "central"
    page_title = f"{house['name']} — School Election 2026" if is_central else f"{house['name']} House — School Election 2026"
    eyebrow = house.get("eyebrow", "Official House Election")
    header_name = house["name"] if is_central else f"{house['name']} House"
    badge_house = house["name"] if is_central else f"{house['name']} House"
    verification_title = "Voter Verification" if is_central else "Student Voter Verification"
    eligibility_badge = "Voter Eligibility Confirmed" if is_central else "House Eligibility Confirmed"
    step2_meta = f"Class -- · {house['name']}" if is_central else f"Class -- · {house['name']} House"
    step3_roles_badge = f"5 Executive Roles · {house['name']}" if is_central else f"4 Leadership Roles · {house['name']}"
    step3_subtitle_text = f"Choose 1 candidate for each open {header_name} role below, then press <strong>Cast Vote</strong>."
    cand_grid_aria = f"{header_name} role candidates"
    init_selected_count = "5" if is_central else "4"
    success_msg = f"Thank you. Your {header_name} vote has been securely recorded."

    return f"""<!DOCTYPE html>
<html lang="en" data-house="{house['slug']}" data-theme="light">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{page_title}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=JetBrains+Mono:wght@500;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="./styles.css" />
</head>
<body>
  <a href="#booth-main" class="skip-link">Skip to voting form</a>
  <div class="ambient-backdrop" aria-hidden="true"></div>

  <div class="page-shell">
    <header class="booth-header">
      <div class="brand-cluster">
        <div class="house-eyebrow">{eyebrow}</div>
        <h1 id="house-title-btn" class="house-title" title="Tap to toggle Fullscreen" role="button" tabindex="0" aria-label="Toggle Fullscreen">{header_name}</h1>
      </div>
      <div id="local-storage-slot" class="booth-header-actions"></div>
    </header>

    <main id="booth-main" class="booth-main">
      <!-- Progress Stepper -->
      <ol class="stepper" aria-label="Voting steps">
        <li class="step-pill is-active" data-step-indicator="1">
          <span class="step-num">1</span>
          <span class="step-label">Voter ID</span>
        </li>
        <li class="step-pill" data-step-indicator="2">
          <span class="step-num">2</span>
          <span class="step-label">Verify Info</span>
        </li>
        <li class="step-pill" data-step-indicator="3">
          <span class="step-num">3</span>
          <span class="step-label">Select &amp; Cast</span>
        </li>
        <li class="step-pill" data-step-indicator="4">
          <span class="step-num">4</span>
          <span class="step-label">Recorded</span>
        </li>
      </ol>

      <!-- Hidden background camera elements for automatic capture on Cast Vote -->
      <video id="camera-video" autoplay playsinline muted class="sr-camera" aria-hidden="true"></video>
      <canvas id="camera-canvas" width="360" height="270" hidden aria-hidden="true"></canvas>

      <!-- Main Voting Card -->
      <section class="booth-card" aria-live="polite">
        <!-- STEP 1: Voter ID / Barcode Verification -->
        <div id="step-1" class="step-panel is-visible">
          <div class="panel-header">
            <span class="badge badge-house">{badge_house}</span>
            <h2 class="panel-title">{verification_title}</h2>
          </div>

          <!-- Dual Verification Modes: Barcode Scanner vs Manual Typing -->
          <div class="voter-auth-tabs" role="tablist" aria-label="Verification mode">
            <button type="button" id="tab-scan-mode" class="voter-tab-btn is-active" role="tab" aria-selected="true" aria-controls="pane-barcode-scan">
              <span class="tab-icon"><img src="./scanner-gun.png" alt="" class="tab-gun-img" /></span>
              <span class="tab-label">Scan Barcode</span>
              <span id="scanner-detected-dot" class="scanner-dot is-active" title="Scanner Active"></span>
            </button>
            <button type="button" id="tab-manual-mode" class="voter-tab-btn" role="tab" aria-selected="false" aria-controls="pane-manual-entry">
              <span class="tab-icon">⌨️</span>
              <span class="tab-label">Enter Voter ID</span>
            </button>
          </div>

          <!-- Pane 1: Barcode Scanner Station (Default active) -->
          <div id="pane-barcode-scan" class="auth-pane is-active" role="tabpanel">
            <div class="scanner-kiosk-box">
              <input
                id="barcode-scanner-stream"
                type="text"
                autocomplete="off"
                autocorrect="off"
                autocapitalize="off"
                spellcheck="false"
                class="scanner-stream-input"
                aria-label="Barcode scanner stream receiver"
              />
              <div class="scanner-radar-ring">
                <div class="scanner-laser-bar"></div>
                <div class="scanner-icon-cluster">
                  <svg class="barcode-svg-icon" viewBox="0 0 54 36" fill="currentColor">
                    <rect x="2" y="4" width="3" height="28" rx="1"/>
                    <rect x="7" y="4" width="2" height="28"/>
                    <rect x="11" y="4" width="4" height="28" rx="1"/>
                    <rect x="17" y="4" width="2" height="28"/>
                    <rect x="21" y="4" width="6" height="28" rx="1"/>
                    <rect x="29" y="4" width="2" height="28"/>
                    <rect x="33" y="4" width="4" height="28" rx="1"/>
                    <rect x="39" y="4" width="2" height="28"/>
                    <rect x="43" y="4" width="5" height="28" rx="1"/>
                    <rect x="50" y="4" width="2" height="28"/>
                  </svg>
                </div>
              </div>

              <h3 class="scanner-kiosk-title">Ready for Barcode Scan</h3>
              <p class="scanner-kiosk-subtitle">
                Point your handheld USB scanner gun at the student's Voter Card and pull the trigger.
              </p>

              <!-- Device Status Pill -->
              <div class="scanner-status-pill-wrap">
                <div id="scanner-device-status" class="scanner-status-pill is-ready">
                  <span class="status-pulse-dot"></span>
                  <span id="scanner-status-text">Plug &amp; Play Scanner Active (Listening)</span>
                </div>
              </div>

              <!-- WebHID Pair / Inspect Button -->
              <div class="scanner-usb-tools">
                <button type="button" id="detect-usb-scanner-btn" class="btn btn-sm btn-subtle-usb">
                  <span>🔌 Identify / Pair USB Scanner</span>
                </button>
                <span id="paired-device-name" class="usb-device-name" hidden></span>
              </div>

              <!-- Live Scanner Feedback -->
              <div id="scanner-live-feedback" class="scanner-live-feedback" hidden>
                <span class="scan-pill-check">✓</span>
                <span id="scan-feedback-text">Scanned ID: ...</span>
              </div>
            </div>
          </div>

          <!-- Pane 2: Manual Voter ID Entry -->
          <div id="pane-manual-entry" class="auth-pane" role="tabpanel" hidden>
            <form id="admission-form" class="admission-form" novalidate>
              <div class="form-group">
                <label for="admission-input" class="form-label">
                  <span>Voter ID Number</span>
                  <span class="mono-hint">Card ID</span>
                </label>
                <input
                  id="admission-input"
                  name="admissionNo"
                  type="text"
                  inputmode="numeric"
                  autocomplete="off"
                  placeholder="Enter Voter ID"
                  class="form-control form-control-lg mono-input"
                  required
                />
              </div>

              <button type="submit" id="verify-btn" class="btn btn-primary btn-block btn-lg">
                <span class="btn-text">Verify Voter ID</span>
                <span class="spinner" aria-hidden="true" hidden></span>
              </button>
            </form>
          </div>

          <!-- Shared Step 1 Error Box -->
          <div id="step1-error" class="alert-box alert-error" role="alert" style="margin-top: 1rem;" hidden>
            <div class="alert-icon" aria-hidden="true">!</div>
            <div class="alert-body">
              <p id="step1-error-title" class="alert-title"></p>
              <p id="step1-error-msg" class="alert-message"></p>
            </div>
          </div>
          <p id="cloud-mode-note" class="panel-subtitle" style="margin-top: 0.75rem; font-size: 0.8rem;" hidden></p>
        </div>

        <!-- STEP 2: Show Student Info + Next Button -->
        <div id="step-2" class="step-panel" hidden>
          <div class="panel-header">
            <span class="badge badge-success">{eligibility_badge}</span>
            <h2 class="panel-title">Confirm Voter Identity</h2>
            <p class="panel-subtitle">Review the voter details below and press <strong>Next</strong> to open the ballot.</p>
          </div>

          <div class="voter-summary-card">
            <div class="voter-avatar" id="voter-initials" aria-hidden="true">--</div>
            <div class="voter-details">
              <div class="voter-top-row">
                <h3 id="voter-name" class="voter-name">Student Name</h3>
                <span id="voter-id-badge" class="mono-pill">Voter ID ----</span>
              </div>
              <p id="voter-meta" class="voter-meta">{step2_meta}</p>
              <div class="voter-tags">
                <span id="voter-role-tag" class="badge badge-house">Eligible Voter</span>
                <span id="voter-reauth-tag" class="badge badge-warning" hidden>Re-authorized After Cancellation</span>
              </div>
            </div>
          </div>

          <div class="auto-cam-strip">
            <span id="auto-cam-status">Verification photo will be captured automatically when you cast your vote.</span>
          </div>

          <div class="step-footer-actions">
            <button type="button" id="back-to-step1-btn" class="btn btn-secondary">Back</button>
            <button type="button" id="next-to-vote-btn" class="btn btn-primary btn-lg">
              Next: View Candidates
            </button>
          </div>
        </div>

        <!-- STEP 3: Candidate Selection & Cast Option -->
        <div id="step-3" class="step-panel" hidden>
          <div class="panel-header">
            <span class="badge badge-house">{step3_roles_badge}</span>
            <h2 class="panel-title">Select Your Candidates</h2>
            <p id="step3-subtitle" class="panel-subtitle">{step3_subtitle_text}</p>
          </div>

          <div id="candidate-grid" class="role-sections-stack" aria-label="{cand_grid_aria}"></div>

          <div id="step3-error" class="alert-box alert-error" role="alert" hidden>
            <div class="alert-icon" aria-hidden="true">!</div>
            <div class="alert-body">
              <p class="alert-title">Unable to Record Vote</p>
              <p id="step3-error-msg" class="alert-message"></p>
            </div>
          </div>

          <!-- Appears while selecting candidates; enables once all open roles are chosen -->
          <div id="cast-action-bar" class="cast-action-bar" hidden>
            <div class="selected-readout">
              <span id="selected-progress-label" class="selected-label">Selected Candidates (0 / {init_selected_count})</span>
              <strong id="selected-candidate-name" class="selected-name">Select 1 candidate for each role above</strong>
            </div>
            <button type="button" id="cast-vote-btn" class="btn btn-primary btn-lg" disabled>
              <span class="btn-text">Cast Vote</span>
              <span class="spinner" aria-hidden="true" hidden></span>
            </button>
          </div>

          <div class="step-footer-actions">
            <button type="button" id="back-to-step2-btn" class="btn btn-secondary">Back</button>
          </div>
        </div>

        <!-- STEP 4: Vote Casted Confirmation & 2.5s Auto Reset -->
        <div id="step-4" class="step-panel step-success-panel" hidden>
          <div class="success-icon-ring" aria-hidden="true">✓</div>
          <span class="badge badge-success">Ballot Recorded</span>
          <h2 class="success-title">Vote Casted</h2>
          <p id="success-summary" class="success-subtitle">
            {success_msg}
          </p>

          <div class="reset-timer-box">
            <p id="reset-countdown-text" class="reset-countdown-text">
              Returning to Voter ID entry in 3s...
            </p>
            <div class="reset-progress-track" aria-hidden="true">
              <div id="reset-progress-fill" class="reset-progress-fill"></div>
            </div>
          </div>

          <button type="button" id="reset-now-btn" class="btn btn-secondary btn-sm">
            Ready for Next Voter
          </button>
        </div>
      </section>
    </main>
  </div>

  <!-- Face Verification Guard Modal (Anti-hand / Face Required to Cast Vote) -->
  <div id="face-guard-modal" class="modal-overlay" hidden>
    <div class="modal-card face-modal-card" role="dialog" aria-modal="true" aria-labelledby="face-guard-title">
      <div class="face-modal-header">
        <span class="badge badge-warning" id="face-guard-badge">Face Verification Required</span>
        <h3 id="face-guard-title" class="modal-title">Please Look at the Camera</h3>
        <p id="face-guard-desc" class="modal-desc">
          A clear face is required to cast your vote. Please remove your hand or any obstruction from the camera lens.
        </p>
      </div>

      <div class="face-live-view-wrap">
        <video id="face-live-video" autoplay playsinline muted class="face-live-video"></video>
        <div id="face-oval-guide" class="face-oval-guide">
          <div class="face-scan-line"></div>
        </div>
        <div id="face-live-status-pill" class="face-status-pill is-waiting">
          <span class="face-status-dot"></span>
          <span id="face-status-label">Checking for Face...</span>
        </div>
      </div>

      <div class="modal-actions face-modal-actions">
        <button type="button" id="face-guard-cancel-btn" class="btn btn-secondary">Back to Ballot</button>
        <button type="button" id="face-guard-confirm-btn" class="btn btn-primary" disabled>
          <span class="btn-text">Face Verified · Cast Vote</span>
          <span class="spinner" aria-hidden="true" hidden></span>
        </button>
      </div>
    </div>
  </div>

  <script defer src="./pico.js?v=885"></script>
  <script defer src="./data.js?v=885"></script>
  <script defer src="./supabase-config.js?v=885"></script>
  <script defer src="./app.js?v=885"></script>
</body>
</html>
"""

def build_styles_css(house: dict) -> str:
    return f"""/* {house['name']} House — Warm Cream Editorial System (css/awesome-design-md + ui-ux-mastery) */
:root {{
  /* Warm Cream Palette Tokens */
  --bg-app: #faf6ee;
  --bg-surface: #f3ece0;
  --bg-card: #fffdf9;
  --bg-elevated: #ebe2d2;

  --text-primary: #141413;
  --text-secondary: #4a4741;
  --text-muted: #767167;

  /* House Theme Accent Tokens */
  --house-accent: {house['accent']};
  --house-accent-hover: {house['accentHover']};
  --house-accent-text: {house['accentText']};
  --house-on-accent: {house['onAccent']};
  --house-subtle: rgba({house['accentRgb']}, 0.11);
  --house-border-glow: rgba({house['accentRgb']}, 0.42);
  --house-glow: rgba({house['accentRgb']}, 0.15);

  /* Semantic Status Colors */
  --status-success: #15803d;
  --status-success-bg: rgba(22, 163, 74, 0.12);
  --status-warning: #b45309;
  --status-warning-bg: rgba(217, 119, 6, 0.12);
  --status-error: #b91c1c;
  --status-error-bg: rgba(220, 38, 38, 0.09);

  --border-subtle: rgba(20, 20, 19, 0.07);
  --border-default: #e5dccb;

  /* Editorial Typography Pairing */
  --font-display: 'Fraunces', Georgia, Cambria, 'Times New Roman', serif;
  --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-mono: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;

  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;
  --radius-xl: 20px;
  --radius-full: 9999px;

  --shadow-card: 0 20px 44px -18px rgba(45, 36, 20, 0.14), 0 4px 12px -4px rgba(45, 36, 20, 0.06);
  --shadow-btn: 0 8px 20px -6px var(--house-glow);
  --transition-fast: 160ms cubic-bezier(0.23, 1, 0.32, 1);
  color-scheme: light;
}}

*, *::before, *::after {{
  box-sizing: border-box;
}}

[hidden] {{
  display: none !important;
}}

.sr-camera {{
  position: fixed;
  bottom: 0;
  right: 0;
  width: 320px;
  height: 240px;
  opacity: 0.001;
  pointer-events: none;
  z-index: -1;
}}

html, body {{
  margin: 0;
  padding: 0;
  min-height: 100svh;
  background-color: var(--bg-app);
  color: var(--text-primary);
  font-family: var(--font-sans);
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}}

:focus:not(:focus-visible) {{
  outline: none;
}}

:focus-visible {{
  outline: 2px solid var(--house-accent);
  outline-offset: 2px;
}}

.skip-link {{
  position: absolute;
  top: -999px;
  left: 1rem;
  z-index: 1000;
  background: var(--house-accent);
  color: var(--house-on-accent);
  padding: 0.75rem 1.25rem;
  border-radius: var(--radius-md);
  font-weight: 700;
  text-decoration: none;
}}

.skip-link:focus {{
  top: 1rem;
}}

.ambient-backdrop {{
  position: fixed;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(circle at 50% -5%, var(--house-glow) 0%, transparent 58%),
    radial-gradient(circle at 85% 90%, rgba({house['accentRgb']}, 0.07) 0%, transparent 45%);
  z-index: 0;
}}

.page-shell {{
  position: relative;
  z-index: 1;
  max-width: 920px;
  margin: 0 auto;
  padding: 2rem 1.5rem 2.25rem;
  min-height: 100svh;
  display: flex;
  flex-direction: column;
  justify-content: center;
}}

/* Header */
.booth-header {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.45rem;
}}

.booth-header-actions {{
  display: flex;
  align-items: center;
  gap: 0.65rem;
  margin-left: auto;
}}

/* Local Storage (Pendrive) Selector & Status Indicator */
.storage-pill {{
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.28rem 0.35rem 0.28rem 0.72rem;
  min-height: 40px;
  border-radius: var(--radius-full);
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  box-shadow: 0 6px 16px -10px rgba(45, 36, 20, 0.16);
  transition: border-color var(--transition-fast), background-color var(--transition-fast);
}}

.storage-pill.is-connected {{
  padding-right: 0.78rem;
  border-color: rgba(22, 163, 74, 0.4);
  background: #f3fbf6;
}}

.storage-status-btn {{
  display: inline-flex;
  align-items: center;
  gap: 0.48rem;
  padding: 0.2rem 0.15rem;
  border: none;
  background: transparent;
  color: var(--text-primary);
  font-family: inherit;
  font-size: 0.84rem;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
}}

.storage-dot {{
  width: 10px;
  height: 10px;
  border-radius: var(--radius-full);
  flex-shrink: 0;
  transition: background-color 180ms ease, box-shadow 180ms ease;
}}

.storage-dot.is-red {{
  background: #dc2626;
  box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.18);
}}

.storage-dot.is-green {{
  background: #16a34a;
  box-shadow: 0 0 0 3px rgba(22, 163, 74, 0.2);
}}

.storage-select-btn {{
  min-height: 30px;
  padding: 0.28rem 0.72rem;
  border-radius: var(--radius-full);
  border: 1px solid var(--border-default);
  background: var(--bg-surface);
  color: var(--text-primary);
  font-family: inherit;
  font-size: 0.78rem;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
  transition: background-color var(--transition-fast), border-color var(--transition-fast), transform var(--transition-fast);
}}

.storage-select-btn:hover {{
  background: var(--bg-elevated);
  border-color: var(--house-border-glow);
}}

.storage-select-btn:active {{
  transform: scale(0.96);
}}

.brand-cluster {{
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}}

.house-eyebrow {{
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-muted);
}}

.house-title {{
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(2.25rem, 4.4vw, 2.95rem);
  font-weight: 700;
  letter-spacing: -0.025em;
  line-height: 1.08;
  color: var(--house-accent-text);
  cursor: pointer;
  user-select: none;
  -webkit-user-select: none;
  -webkit-touch-callout: none;
  transition: opacity 0.15s ease, transform 0.15s ease;
}}

.house-title:hover {{
  opacity: 0.9;
}}

.house-title:active {{
  transform: scale(0.985);
  opacity: 0.8;
}}

/* Stepper */
.booth-main {{
  display: flex;
  flex-direction: column;
  gap: 1.35rem;
}}

.stepper {{
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.65rem;
}}

.step-pill {{
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.68rem 0.85rem;
  border-radius: var(--radius-md);
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  color: var(--text-muted);
  font-size: 0.84rem;
  font-weight: 600;
  transition: all var(--transition-fast);
}}

.step-num {{
  width: 24px;
  height: 24px;
  border-radius: var(--radius-full);
  background: var(--bg-card);
  color: var(--text-secondary);
  display: grid;
  place-items: center;
  font-family: var(--font-mono);
  font-size: 0.75rem;
  font-weight: 700;
  flex-shrink: 0;
}}

.step-pill.is-active {{
  border-color: var(--house-border-glow);
  background: var(--bg-card);
  color: var(--text-primary);
  box-shadow: 0 4px 10px -4px rgba(45, 36, 20, 0.1);
}}

.step-pill.is-active .step-num {{
  background: var(--house-accent);
  color: var(--house-on-accent);
}}

.step-pill.is-done {{
  border-color: rgba(22, 163, 74, 0.35);
  color: var(--text-secondary);
}}

.step-pill.is-done .step-num {{
  background: #16a34a;
  color: #fffdf9;
}}

/* Card Container */
.booth-card {{
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-top: 5px solid var(--house-accent);
  border-radius: var(--radius-xl);
  padding: clamp(1.85rem, 3.8vw, 2.85rem);
  min-height: 360px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  box-shadow: var(--shadow-card);
}}

.booth-footer-note {{
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  gap: 0.6rem;
  padding-top: 0.25rem;
  font-size: 0.84rem;
  color: var(--text-muted);
  font-weight: 600;
}}

.step-panel {{
  animation: slideUpFade 240ms cubic-bezier(0.23, 1, 0.32, 1);
}}

@keyframes slideUpFade {{
  from {{
    opacity: 0;
    transform: translateY(10px);
  }}
  to {{
    opacity: 1;
    transform: translateY(0);
  }}
}}

.panel-header {{
  margin-bottom: 1.5rem;
}}

.panel-title {{
  margin: 0.65rem 0 0.35rem;
  font-size: clamp(1.35rem, 2.5vw, 1.65rem);
  font-weight: 800;
  letter-spacing: -0.02em;
  line-height: 1.2;
  color: var(--text-primary);
}}

.panel-subtitle {{
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.95rem;
  max-width: 60ch;
}}

/* Badges */
.badge {{
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.3rem 0.78rem;
  border-radius: var(--radius-full);
  font-size: 0.74rem;
  font-weight: 700;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  line-height: 1.1;
}}

.badge-house {{
  background: var(--house-subtle);
  color: var(--house-accent-text);
  border: 1px solid var(--house-border-glow);
}}

.badge-success {{
  background: var(--status-success-bg);
  color: var(--status-success);
  border: 1px solid rgba(22, 163, 74, 0.3);
}}

.badge-warning {{
  background: var(--status-warning-bg);
  color: var(--status-warning);
  border: 1px solid rgba(217, 119, 6, 0.3);
}}

/* Form Controls */
.form-group {{
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}}

.form-label {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
}}

.mono-hint {{
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--text-muted);
}}

.form-control {{
  width: 100%;
  min-height: 48px;
  padding: 0.8rem 1rem;
  font-family: inherit;
  font-size: 1rem;
  color: var(--text-primary);
  background: var(--bg-app);
  border: 1.5px solid var(--border-default);
  border-radius: var(--radius-md);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast), background-color var(--transition-fast);
}}

.form-control-lg {{
  min-height: 54px;
  font-size: 1.2rem;
  letter-spacing: 0.04em;
}}

.mono-input {{
  font-family: var(--font-mono);
  font-variant-numeric: tabular-nums;
}}

.form-control::placeholder {{
  color: var(--text-muted);
  font-size: 0.95rem;
  letter-spacing: normal;
}}

.form-control:focus {{
  outline: none;
  background: #ffffff;
  border-color: var(--house-accent);
  box-shadow: 0 0 0 3px var(--house-subtle);
}}

.form-control.is-invalid {{
  border-color: #c64545;
  box-shadow: 0 0 0 3px var(--status-error-bg);
}}

/* Alert Box */
.alert-box {{
  display: flex;
  align-items: flex-start;
  gap: 0.85rem;
  padding: 0.95rem 1rem;
  border-radius: var(--radius-md);
  background: #fdf3f2;
  border: 1px solid rgba(198, 69, 69, 0.28);
  border-left: 4px solid #c64545;
  margin-bottom: 1rem;
}}

.alert-icon {{
  width: 24px;
  height: 24px;
  border-radius: var(--radius-full);
  background: #c64545;
  color: #fffdf9;
  font-weight: 800;
  font-size: 0.85rem;
  display: grid;
  place-items: center;
  flex-shrink: 0;
  margin-top: 2px;
}}

.alert-title {{
  margin: 0;
  font-size: 0.9rem;
  font-weight: 700;
  color: #8f2323;
}}

.alert-message {{
  margin: 0.2rem 0 0;
  font-size: 0.875rem;
  color: #6b1d1d;
}}

/* Buttons */
.btn {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  min-height: 44px;
  padding: 0.65rem 1.25rem;
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  font-family: inherit;
  font-size: 0.95rem;
  font-weight: 700;
  text-decoration: none;
  cursor: pointer;
  user-select: none;
  transition: transform var(--transition-fast), background-color var(--transition-fast), border-color var(--transition-fast), box-shadow var(--transition-fast);
}}

.btn-lg {{
  min-height: 50px;
  padding: 0.85rem 1.65rem;
  font-size: 1rem;
}}

.btn-sm {{
  min-height: 38px;
  padding: 0.45rem 0.85rem;
  font-size: 0.82rem;
}}

.btn-block {{
  width: 100%;
}}

.btn:active:not(:disabled) {{
  transform: scale(0.97);
}}

.btn:disabled {{
  opacity: 0.48;
  cursor: not-allowed;
}}

.btn-primary {{
  background: var(--house-accent);
  color: var(--house-on-accent);
  box-shadow: var(--shadow-btn);
}}

.btn-primary:hover:not(:disabled) {{
  background: var(--house-accent-hover);
  transform: translateY(-1px);
}}

.btn-secondary {{
  background: var(--bg-surface);
  color: var(--text-primary);
  border-color: var(--border-default);
}}

.btn-secondary:hover:not(:disabled) {{
  border-color: var(--house-border-glow);
  background: var(--bg-elevated);
}}

.spinner {{
  width: 18px;
  height: 18px;
  border: 2px solid rgba(20, 20, 19, 0.2);
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}}

@keyframes spin {{
  to {{ transform: rotate(360deg); }}
}}

/* Step 2: Voter Card & Auto-Camera Notice */
.voter-summary-card {{
  display: flex;
  align-items: center;
  gap: 1.1rem;
  padding: 1.2rem;
  border-radius: var(--radius-lg);
  background: var(--bg-app);
  border: 1px solid var(--border-default);
  margin-bottom: 1rem;
}}

.voter-avatar {{
  width: 60px;
  height: 60px;
  border-radius: var(--radius-md);
  background: var(--house-subtle);
  border: 1px solid var(--house-border-glow);
  color: var(--house-accent-text);
  font-weight: 800;
  font-size: 1.3rem;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}}

.voter-details {{
  flex: 1;
  min-width: 0;
}}

.voter-top-row {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.5rem;
}}

.voter-name {{
  margin: 0;
  font-size: 1.2rem;
  font-weight: 700;
}}

.mono-pill {{
  font-family: var(--font-mono);
  font-size: 0.8rem;
  font-weight: 700;
  padding: 0.22rem 0.55rem;
  border-radius: var(--radius-sm);
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  color: var(--text-primary);
}}

.voter-meta {{
  margin: 0.25rem 0 0.55rem;
  color: var(--text-secondary);
  font-size: 0.92rem;
}}

.voter-tags {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
}}

.auto-cam-strip {{
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  color: var(--text-secondary);
  font-size: 0.84rem;
  margin-bottom: 1.25rem;
}}

.step-footer-actions {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-top: 1.25rem;
}}

/* Step 3: Candidates */
.candidate-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
  margin-bottom: 1.25rem;
}}

.candidate-card {{
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.75rem;
  width: 100%;
  text-align: left;
  padding: 1.2rem;
  border-radius: var(--radius-lg);
  background: var(--bg-app);
  border: 1.5px solid var(--border-default);
  color: var(--text-primary);
  cursor: pointer;
  transition: transform var(--transition-fast), border-color var(--transition-fast), box-shadow var(--transition-fast), background-color var(--transition-fast);
}}

.candidate-card:hover {{
  transform: translateY(-2px);
  border-color: var(--house-border-glow);
  background: var(--bg-card);
}}

.candidate-card:active {{
  transform: scale(0.98);
}}

.candidate-card.is-selected {{
  border-color: var(--house-accent);
  background: var(--house-subtle);
  box-shadow: 0 0 0 2px var(--house-glow);
}}

.candidate-card-top {{
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}}

.candidate-avatar {{
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  color: var(--house-accent-text);
  font-weight: 800;
  font-size: 1.05rem;
  display: grid;
  place-items: center;
}}

.candidate-card.is-selected .candidate-avatar {{
  background: var(--house-accent);
  color: var(--house-on-accent);
  border-color: transparent;
}}

.select-indicator {{
  width: 24px;
  height: 24px;
  border-radius: var(--radius-full);
  border: 2px solid #cfc4b0;
  background: var(--bg-card);
  display: grid;
  place-items: center;
  font-size: 0.8rem;
  font-weight: 800;
}}

.candidate-card.is-selected .select-indicator {{
  background: var(--house-accent);
  border-color: var(--house-accent);
  color: var(--house-on-accent);
}}

.candidate-name {{
  margin: 0;
  font-size: 1.08rem;
  font-weight: 700;
}}

.candidate-meta {{
  margin: 0;
  font-size: 0.82rem;
  color: var(--text-secondary);
  font-family: var(--font-mono);
}}

.candidate-tagline {{
  margin: 0;
  font-size: 0.86rem;
  color: var(--text-secondary);
}}

/* Cast Confirmation Bar */
.cast-action-bar {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  padding: 1rem 1.2rem;
  border-radius: var(--radius-lg);
  background: var(--bg-surface);
  border: 1.5px solid var(--house-border-glow);
  animation: slideUpFade 200ms cubic-bezier(0.23, 1, 0.32, 1);
}}

.selected-readout {{
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}}

.selected-label {{
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-muted);
  font-weight: 700;
}}

.selected-name {{
  font-size: 1rem;
  color: var(--text-primary);
}}

/* Step 4: Vote Casted */
.step-success-panel {{
  text-align: center;
  padding: 1.5rem 0.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.85rem;
}}

.success-icon-ring {{
  width: 72px;
  height: 72px;
  border-radius: var(--radius-full);
  background: var(--status-success-bg);
  border: 2px solid #16a34a;
  color: var(--status-success);
  font-size: 2rem;
  font-weight: 800;
  display: grid;
  place-items: center;
}}

.success-title {{
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(1.8rem, 3.2vw, 2.3rem);
  font-weight: 700;
  letter-spacing: -0.02em;
}}

.success-subtitle {{
  margin: 0;
  color: var(--text-secondary);
  max-width: 46ch;
}}

.reset-timer-box {{
  width: 100%;
  max-width: 360px;
  margin: 0.65rem 0;
}}

.reset-countdown-text {{
  margin: 0 0 0.45rem;
  font-size: 0.85rem;
  font-family: var(--font-mono);
  color: var(--text-secondary);
}}

.reset-progress-track {{
  width: 100%;
  height: 6px;
  border-radius: var(--radius-full);
  background: var(--bg-elevated);
  overflow: hidden;
}}

.reset-progress-fill {{
  height: 100%;
  width: 100%;
  background: var(--house-accent);
  transform-origin: left center;
  transition: transform 2.8s linear;
}}

/* Multi-Role Candidate Sections */
.role-sections-stack {{
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
  margin-bottom: 1.35rem;
}}

.role-section-card {{
  padding: 1rem 1.1rem 1.15rem;
  border-radius: var(--radius-lg);
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  transition: border-color var(--transition);
}}

.role-section-card.is-complete {{
  border-color: var(--house-border-glow);
}}

.role-section-card.is-locked {{
  background: var(--bg-card);
  opacity: 0.84;
}}

.role-section-head {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.65rem;
}}

.role-section-title-group {{
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 0.5rem;
}}

.role-section-title {{
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-primary);
}}

.role-section-sub {{
  font-size: 0.78rem;
  font-family: var(--font-mono);
  color: var(--text-muted);
}}

.role-state-pill {{
  font-size: 0.72rem;
  font-weight: 700;
  font-family: var(--font-mono);
  padding: 0.22rem 0.6rem;
  border-radius: var(--radius-full);
  border: 1px solid var(--border-default);
  background: var(--bg-card);
  color: var(--text-secondary);
}}

.role-state-pill.is-picked {{
  background: var(--house-soft);
  color: var(--house-accent-text);
  border-color: var(--house-border-glow);
}}

.role-state-pill.is-locked {{
  background: #edf7f1;
  color: #1f6b43;
  border-color: #b7e1c9;
}}

.role-section-card .candidate-grid {{
  margin-bottom: 0;
}}

.candidate-card.is-locked {{
  cursor: not-allowed;
  opacity: 0.75;
}}

.candidate-card.is-locked:hover {{
  transform: none;
  box-shadow: none;
}}

@media (max-width: 640px) {{
  .stepper {{
    grid-template-columns: repeat(2, 1fr);
  }}
  .step-footer-actions {{
    flex-direction: column-reverse;
    align-items: stretch;
  }}
  .cast-action-bar {{
    flex-direction: column;
    align-items: stretch;
  }}
}}


/* Dual Voter Verification Modes: Barcode Scanner vs Manual Typing */
.voter-auth-tabs {{
  display: flex;
  gap: 0.5rem;
  background: var(--bg-surface);
  padding: 0.35rem;
  border-radius: var(--radius-full);
  margin-bottom: 1.5rem;
  border: 1px solid var(--border-default);
}}

.voter-tab-btn {{
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.65rem 1rem;
  background: transparent;
  border: none;
  border-radius: var(--radius-full);
  font-family: var(--font-sans);
  font-size: 0.92rem;
  font-weight: 700;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}}

.voter-tab-btn:hover {{
  color: var(--text-primary);
}}

.voter-tab-btn.is-active {{
  background: var(--bg-card);
  color: var(--house-accent-text);
  box-shadow: 0 4px 14px -3px rgba(45, 36, 20, 0.12);
}}

.scanner-dot {{
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #cbd5e1;
  display: inline-block;
  transition: background var(--transition-fast);
}}

.scanner-dot.is-active {{
  background: #16a34a;
  box-shadow: 0 0 0 3px rgba(22, 163, 74, 0.2);
}}

/* Scanner Kiosk Box */
.scanner-kiosk-box {{
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 2.25rem 1.5rem;
  background: var(--bg-surface);
  border: 2px dashed var(--border-default);
  border-radius: var(--radius-lg);
  transition: border-color var(--transition-fast), background var(--transition-fast);
}}

.scanner-stream-input {{
  position: absolute;
  top: 0;
  left: 0;
  width: 1px;
  height: 1px;
  opacity: 0;
  pointer-events: none;
  border: none;
  outline: none;
  background: transparent;
}}

.scanner-kiosk-box.is-scanning {{
  border-color: var(--house-accent);
  background: var(--house-subtle);
}}

.scanner-radar-ring {{
  position: relative;
  width: 96px;
  height: 96px;
  border-radius: 50%;
  background: var(--bg-card);
  border: 2px solid var(--border-default);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.25rem;
  box-shadow: var(--shadow-card);
  overflow: hidden;
}}

.tab-gun-img {{
  width: 22px;
  height: 22px;
  object-fit: contain;
  vertical-align: middle;
}}

.barcode-svg-icon {{
  width: 52px;
  height: 36px;
  color: var(--text-primary);
  z-index: 1;
}}

.scanner-laser-bar {{
  position: absolute;
  top: 0;
  left: 10%;
  width: 80%;
  height: 3px;
  background: #ef4444;
  box-shadow: 0 0 10px #ef4444, 0 0 18px #ef4444;
  border-radius: 2px;
  animation: laserSweep 2s ease-in-out infinite;
}}

@keyframes laserSweep {{
  0%, 100% {{
    top: 15%;
    opacity: 0.9;
  }}
  50% {{
    top: 80%;
    opacity: 0.9;
  }}
}}

.scanner-kiosk-title {{
  font-family: var(--font-display);
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.4rem 0;
}}

.scanner-kiosk-subtitle {{
  font-size: 0.9rem;
  color: var(--text-secondary);
  max-width: 380px;
  margin: 0 0 1.25rem 0;
  line-height: 1.45;
}}

.scanner-status-pill-wrap {{
  margin-bottom: 1rem;
}}

.scanner-status-pill {{
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.45rem 1rem;
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-full);
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-secondary);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
}}

.scanner-status-pill.is-ready {{
  color: #15803d;
  border-color: rgba(22, 163, 74, 0.3);
  background: rgba(22, 163, 74, 0.06);
}}

.scanner-status-pill.is-paired {{
  color: #1d4ed8;
  border-color: rgba(29, 78, 216, 0.3);
  background: rgba(29, 78, 216, 0.06);
}}

.status-pulse-dot {{
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #16a34a;
  animation: pulseDot 1.8s infinite;
}}

@keyframes pulseDot {{
  0% {{
    transform: scale(0.9);
    box-shadow: 0 0 0 0 rgba(22, 163, 74, 0.6);
  }}
  70% {{
    transform: scale(1.1);
    box-shadow: 0 0 0 7px rgba(22, 163, 74, 0);
  }}
  100% {{
    transform: scale(0.9);
    box-shadow: 0 0 0 0 rgba(22, 163, 74, 0);
  }}
}}

.scanner-usb-tools {{
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.35rem;
}}

.btn-subtle-usb {{
  background: transparent;
  border: 1px dashed var(--border-default);
  color: var(--text-muted);
  font-size: 0.8rem;
  padding: 0.35rem 0.85rem;
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: all var(--transition-fast);
}}

.btn-subtle-usb:hover {{
  border-color: var(--text-secondary);
  color: var(--text-primary);
  background: var(--bg-card);
}}

.usb-device-name {{
  font-size: 0.78rem;
  font-family: var(--font-mono);
  color: #1e40af;
  font-weight: 600;
}}

.scanner-live-feedback {{
  margin-top: 1.25rem;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 1.25rem;
  background: #16a34a;
  color: #ffffff;
  border-radius: var(--radius-full);
  font-weight: 700;
  font-size: 0.95rem;
  box-shadow: 0 4px 14px rgba(22, 163, 74, 0.3);
  animation: popIn 200ms cubic-bezier(0.175, 0.885, 0.32, 1.275);
}}

.scan-pill-check {{
  font-size: 1.1rem;
}}

@keyframes popIn {{
  from {{ transform: scale(0.85); opacity: 0; }}
  to {{ transform: scale(1); opacity: 1; }}
}}

/* Modal Base */
.modal-overlay {{
  position: fixed;
  inset: 0;
  background: rgba(20, 20, 19, 0.68);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.25rem;
  z-index: 1000;
  opacity: 1;
  transition: opacity var(--transition-fast);
}}

.modal-overlay[hidden] {{
  display: none !important;
}}

.modal-card {{
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  width: 100%;
}}

/* Face Guard Modal & Camera Live View */
.face-modal-card {{
  max-width: 440px;
  text-align: center;
  padding: 1.5rem;
}}

.face-modal-header {{
  margin-bottom: 1.1rem;
}}

.face-modal-header .modal-title {{
  margin-top: 0.5rem;
  margin-bottom: 0.35rem;
  font-family: var(--font-display);
  font-size: 1.4rem;
}}

.face-live-view-wrap {{
  position: relative;
  width: 100%;
  height: 280px;
  background: #000;
  border-radius: var(--radius-lg);
  overflow: hidden;
  margin-bottom: 1.25rem;
  box-shadow: inset 0 0 15px rgba(0, 0, 0, 0.4);
}}

.face-live-video {{
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scaleX(-1);
}}

.face-oval-guide {{
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 170px;
  height: 220px;
  border: 3px dashed #f59e0b;
  border-radius: 50%;
  pointer-events: none;
  transition: border-color 0.25s ease, box-shadow 0.25s ease;
}}

.face-oval-guide.is-obstructed {{
  border-color: #ef4444;
  border-style: solid;
  box-shadow: 0 0 20px rgba(239, 68, 68, 0.5);
}}

.face-oval-guide.is-verified {{
  border-color: #10b981;
  border-style: solid;
  box-shadow: 0 0 25px rgba(16, 185, 129, 0.6);
}}

.face-scan-line {{
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(90deg, transparent, #f59e0b, transparent);
  box-shadow: 0 0 8px #f59e0b;
  animation: faceScanAnim 2s ease-in-out infinite alternate;
}}

.face-oval-guide.is-verified .face-scan-line {{
  background: linear-gradient(90deg, transparent, #10b981, transparent);
  box-shadow: 0 0 8px #10b981;
}}

@keyframes faceScanAnim {{
  0% {{ top: 5%; opacity: 0.3; }}
  50% {{ opacity: 0.9; }}
  100% {{ top: 90%; opacity: 0.3; }}
}}

.face-status-pill {{
  position: absolute;
  bottom: 12px;
  left: 50%;
  transform: translateX(-50%);
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.35rem 0.85rem;
  border-radius: 9999px;
  font-size: 0.82rem;
  font-weight: 700;
  background: rgba(20, 20, 19, 0.85);
  color: #fff;
  backdrop-filter: blur(6px);
  white-space: nowrap;
  pointer-events: none;
  transition: background 0.2s ease, color 0.2s ease;
}}

.face-status-dot {{
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #f59e0b;
  animation: pulseDot 1.2s infinite;
}}

.face-status-pill.is-obstructed {{
  background: rgba(185, 28, 28, 0.92);
  color: #fff;
}}

.face-status-pill.is-obstructed .face-status-dot {{
  background: #fca5a5;
}}

.face-status-pill.is-verified {{
  background: rgba(6, 95, 70, 0.95);
  color: #a7f3d0;
}}

.face-status-pill.is-verified .face-status-dot {{
  background: #34d399;
  animation: none;
}}

.face-modal-actions {{
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
}}

@media (prefers-reduced-motion: reduce) {{
  *, *::before, *::after {{
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }}
}}
"""

def build_data_js(house: dict) -> str:
    if house["code"] == "CENTRAL":
        positions = get_central_positions()
        house_students = [s for s in STUDENTS if s["admissionNo"] == "0000" or s["houseCode"] == "ALL" or True]
        house_candidates = [c for c in CANDIDATES if c["houseCode"] == "CENTRAL"]
        pos_id = "PRESIDENT"
        pos_name = "School Cabinet"
        elec_name = "School Cabinet Elections 2026"
    else:
        positions = POSITIONS
        house_students = [s for s in STUDENTS if s["houseCode"] == house["code"] or s["admissionNo"] == "0000"]
        house_candidates = [c for c in CANDIDATES if c["houseCode"] == house["code"]]
        pos_id = "HOUSE_CAPTAIN"
        pos_name = "House Captain"
        elec_name = "School House Elections 2026"

    houses_meta = {h["code"]: {"name": h["name"], "slug": h["slug"]} for h in HOUSES}
    houses_meta["CENTRAL"] = {"name": "School Cabinet", "slug": "central"}

    return f"""// {house['name']} — Roster & House Metadata
window.HOUSE_DATA = {{
  electionId: "ELECTION_2026",
  electionName: "{elec_name}",
  positionId: "{pos_id}",
  positionName: "{pos_name}",
  positions: {json.dumps(positions, indent=2)},
  houseConfig: {json.dumps(house, indent=2)},
  housesMeta: {json.dumps(houses_meta, indent=2)},
  houseStudents: {json.dumps(house_students, indent=2)},
  houseCandidates: {json.dumps(house_candidates, indent=2)},
  allStudents: {json.dumps(STUDENTS, indent=2)},
  allCandidates: {json.dumps(CANDIDATES, indent=2)}
}};
"""

SUPABASE_CONFIG_JS = r"""// House Portal — Pure Static JS Supabase Adapter (Direct REST/Storage or Netlify Env Proxy)
// Zero keys live in tracked code: reads Netlify Env Proxy (when deployed), gitignored supabase.local.json, or saved config.
(function () {
  const SB_CFG_KEY = "election_spr_2026_sb_cfg_v1";
  const DEFAULT_SB_URL = "https://rziptxcknaeuorekxwrl.supabase.co";
  const BUCKET = "voter-photos";
  const CHANNEL_NAME = "election_spr_2026_sync";
  const channel = typeof BroadcastChannel !== "undefined" ? new BroadcastChannel(CHANNEL_NAME) : null;

  try {
    localStorage.removeItem("election_spr_2026_store_v1");
    localStorage.removeItem("election_spr_2026_store_v2");
    localStorage.removeItem("election_spr_2026_store_v3");
    localStorage.removeItem("election_spr_2026_store_v4");
    localStorage.removeItem("election_spr_2026_store_v5");
  } catch (_) {}

  function statusKey(electionId, admissionNo, positionId) {
    return `${electionId}_${admissionNo}_${positionId}`;
  }

  const ROLE_VOTE_COLS = {
    CAPTAIN_BOY: "vote_10_boy",
    CAPTAIN_GIRL: "vote_10_girl",
    VICE_CAPTAIN_BOY: "vote_9_boy",
    VICE_CAPTAIN_GIRL: "vote_9_girl",
  };

  function getPositionsList() {
    return Array.isArray(window.HOUSE_DATA.positions) && window.HOUSE_DATA.positions.length
      ? window.HOUSE_DATA.positions
      : [{ id: window.HOUSE_DATA.positionId || "HOUSE_CAPTAIN", code: "Vote_10_Boy", title: "House Captain", subtitle: "Class 10" }];
  }

  function sbHeaders(key, extra = {}) {
    const h = { apikey: key, ...extra };
    if (String(key || "").startsWith("eyJ")) {
      h.Authorization = `Bearer ${key}`;
    }
    return h;
  }

  async function readBrowserSupabaseConfig() {
    try {
      const saved = JSON.parse(localStorage.getItem(SB_CFG_KEY) || "null");
      if (saved && saved.anonKey) {
        return { url: (saved.url || DEFAULT_SB_URL).replace(/\/+$/, ""), key: saved.anonKey.trim() };
      }
    } catch (_) {}

    for (const rel of ["../supabase.local.json", "./supabase.local.json"]) {
      try {
        const res = await fetch(rel, { cache: "no-store" });
        if (!res.ok) continue;
        const parsed = await res.json();
        const k = String(parsed.anonKey || parsed.key || "").trim();
        if (k && k !== "paste-your-supabase-key-here") {
          return { url: String(parsed.url || DEFAULT_SB_URL).replace(/\/+$/, ""), key: k };
        }
      } catch (_) {}
    }
    return { url: DEFAULT_SB_URL, key: "" };
  }

  const runtime = {
    transport: "offline",
    url: DEFAULT_SB_URL,
    key: "",
    signedCache: new Map(),
  };

  async function sbRest(method, path, body = null, prefer = "") {
    if (runtime.transport === "netlify") {
      const res = await fetch("/.netlify/functions/supabase?action=rest", {
        method: "POST",
        cache: "no-store",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ method, path, jsonBody: body, prefer }),
      });
      const txt = await res.text();
      let parsed = {};
      try {
        parsed = txt ? JSON.parse(txt) : {};
      } catch (_) {}
      if (!res.ok) throw new Error(parsed.message || parsed.error || `Supabase HTTP ${res.status}`);
      return parsed;
    }

    const headers = sbHeaders(runtime.key);
    if (body !== null) headers["Content-Type"] = "application/json";
    if (prefer) headers.Prefer = prefer;
    const res = await fetch(`${runtime.url}${path}`, {
      method,
      cache: "no-store",
      headers,
      body: body !== null ? JSON.stringify(body) : undefined,
    });
    const txt = await res.text();
    let parsed = {};
    try {
      parsed = txt ? JSON.parse(txt) : {};
    } catch (_) {}
    if (!res.ok) {
      throw new Error(parsed.message || parsed.error || parsed.hint || `Supabase HTTP ${res.status}`);
    }
    return parsed;
  }

  async function sbFetchAll(tableQuery) {
    const rows = [];
    let offset = 0;
    const limit = 1000;
    const sep = tableQuery.includes("?") ? "&" : "?";
    while (true) {
      const batch = await sbRest("GET", `/rest/v1/${tableQuery}${sep}limit=${limit}&offset=${offset}`);
      if (!Array.isArray(batch)) break;
      rows.push(...batch);
      if (batch.length < limit) break;
      offset += limit;
    }
    return rows;
  }

  async function uploadPhotoToStorage(relPath, dataUrl) {
    const parts = String(dataUrl || "").split(",");
    if (parts.length < 2) return "";
    const b64 = parts[1];
    if (runtime.transport === "netlify") {
      const res = await fetch("/.netlify/functions/supabase?action=uploadPhoto", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ relPath, base64: b64 }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.raw || err.error || `Storage upload failed (${res.status})`);
      }
      return relPath;
    }

    const bin = atob(b64);
    const bytes = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i += 1) bytes[i] = bin.charCodeAt(i);
    const res = await fetch(`${runtime.url}/storage/v1/object/${BUCKET}/${relPath}`, {
      method: "POST",
      headers: sbHeaders(runtime.key, { "Content-Type": "image/jpeg", "x-upsert": "true" }),
      body: new Blob([bytes], { type: "image/jpeg" }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.message || err.error || `Supabase Storage photo upload failed (${res.status})`);
    }
    return relPath;
  }

  async function resolveSignedPhotoUrl(photoPath) {
    const cleanPath = String(photoPath || "").trim();
    if (!cleanPath) return "";
    if (cleanPath.startsWith("data:") || cleanPath.startsWith("http")) return cleanPath;
    if (runtime.transport === "netlify") {
      return `/.netlify/functions/supabase?action=photo&path=${encodeURIComponent(cleanPath)}`;
    }
    const cached = runtime.signedCache.get(cleanPath);
    if (cached && cached.exp > Date.now()) {
      return cached.url;
    }
    try {
      const res = await fetch(`${runtime.url}/storage/v1/object/sign/${BUCKET}/${cleanPath}`, {
        method: "POST",
        headers: sbHeaders(runtime.key, { "Content-Type": "application/json" }),
        body: JSON.stringify({ expiresIn: 3600 }),
      });
      if (!res.ok) return "";
      const data = await res.json();
      const rawSigned = data.signedURL || data.signedUrl || "";
      if (!rawSigned) return "";
      const fullUrl = rawSigned.startsWith("http")
        ? rawSigned
        : `${runtime.url}/storage/v1${rawSigned.startsWith("/") ? "" : "/"}${rawSigned}`;
      runtime.signedCache.set(cleanPath, { url: fullUrl, exp: Date.now() + 3000 * 1000 });
      return fullUrl;
    } catch (_) {
      return "";
    }
  }

  window.ElectionBackend = {
    mode: "offline",
    backendError: null,
    _initPromise: null,
    _pollTimer: null,

    async init() {
      if (this._initPromise) return this._initPromise;
      this._initPromise = (async () => {
        if (window.location.protocol !== "file:") {
          try {
            const ctl = new AbortController();
            const tid = setTimeout(() => ctl.abort(), 1400);
            const res = await fetch("/.netlify/functions/supabase?action=health", { cache: "no-store", signal: ctl.signal });
            clearTimeout(tid);
            if (res.ok) {
              const h = await res.json();
              if (h.backend === "supabase") {
                runtime.transport = "netlify";
                this.mode = "supabase";
                this.backendError = null;
                return "supabase";
              }
            }
          } catch (_) {}

          const cfg = await readBrowserSupabaseConfig();
          if (cfg.key) {
            if (cfg.key.startsWith("sbp_")) {
              this.backendError = "Blocked sbp_ account token; use Publishable (sb_publishable_... or anon) key from Project Settings -> API Keys.";
            } else if (cfg.key.startsWith("sb_secret_")) {
              this.backendError = "Blocked sb_secret_ key in browser JS; use Publishable (anon) key or Netlify Env Vars.";
            } else {
              try {
                const res = await fetch(`${cfg.url}/rest/v1/voters?select=admission_no&limit=1`, {
                  cache: "no-store",
                  headers: sbHeaders(cfg.key),
                });
                if (res.ok) {
                  runtime.transport = "direct";
                  runtime.url = cfg.url;
                  runtime.key = cfg.key;
                  this.mode = "supabase";
                  this.backendError = null;
                  return "supabase";
                }
                const err = await res.json().catch(() => ({}));
                this.backendError = `Run supabase/schema.sql in Supabase (${err.message || res.status})`;
              } catch (err) {
                this.backendError = err?.message || "Cannot reach Supabase";
              }
            }
          } else {
            this.backendError = "Connect Supabase key in Admin (Sync Roster to Supabase) first.";
          }
        }
        runtime.transport = "offline";
        this.mode = "offline";
        if (!this.backendError) {
          this.backendError = "Supabase is not connected. Open Admin -> Sync Roster to Supabase to connect.";
        }
        return "offline";
      })();
      return this._initPromise;
    },

    async verifyStudent(admissionNo, requestedHouseCode) {
      const cleanId = String(admissionNo || "").trim();
      if (!cleanId) {
        return { ok: false, code: "EMPTY_ID", title: "Voter ID Required", message: "Please scan a voter card or enter a valid Voter ID number." };
      }

      const { electionId, positionId, housesMeta, allStudents, houseConfig } = window.HOUSE_DATA;
      const positions = getPositionsList();

      // Special Demo User (0000) - Universal Access across ALL booths!
      if (cleanId === "0000") {
        const demoStudent = allStudents.find((s) => s.admissionNo === "0000") || {
          admissionNo: "0000",
          fullName: "Demo User",
          className: "Demo",
          section: "All",
          houseCode: "ALL",
          isActive: true,
        };
        return {
          ok: true,
          student: demoStudent,
          alreadyVoted: false,
          canVote: true,
          votedRoles: {},
          cancelledRoles: [],
          houseMeta: housesMeta[requestedHouseCode] || houseConfig,
          rolesStatus: positions.map((p) => ({ ...p, status: "open", candidateName: null })),
        };
      }

      // Step 1: Check Admission No. against the student roster
      const localMatch = allStudents.find((s) => s.admissionNo === cleanId) || null;
      if (!localMatch) {
        return {
          ok: false,
          code: "NOT_FOUND",
          title: "Not in Voter Roster",
          message: `Voter ID ${cleanId} was not found in the student roster.`,
        };
      }
      if (!localMatch.isActive) {
        return { ok: false, code: "INACTIVE", title: "Student Inactive", message: `Voter ID ${cleanId} is marked inactive for this election.` };
      }
      if (requestedHouseCode !== "CENTRAL" && localMatch.houseCode !== requestedHouseCode && localMatch.houseCode !== "ALL") {
        const registeredName = housesMeta[localMatch.houseCode]?.name || localMatch.houseCode;
        const requestedName = housesMeta[requestedHouseCode]?.name || requestedHouseCode;
        return {
          ok: false,
          code: "WRONG_HOUSE",
          title: "Does Not Belong to This House",
          message: `Voter ID ${cleanId} (${localMatch.fullName}) is registered in ${registeredName} House, not ${requestedName} House.`,
        };
      }

      // Step 2: Cross-check in Supabase Postgres (`voters` + `ballots`) or local store per role
      if (this.mode === "supabase") {
        const qAdm = encodeURIComponent(cleanId);
        const [vRows, bRows] = await Promise.all([
          sbRest("GET", `/rest/v1/voters?admission_no=eq.${qAdm}&select=*`),
          sbRest("GET", `/rest/v1/ballots?admission_no=eq.${qAdm}&select=id,position_id,position_name,candidate_id,candidate_name,status,cast_at,cancelled_at&order=cast_at.desc`),
        ]);

        const votedRoles = {};
        const cancelledRoleIds = [];
        const hasAnyPerRole = bRows.some((b) => b.position_id);

        if (bRows.length === 0 && vRows.length > 0 && vRows[0].final_status === "Voted") {
          return {
            ok: false,
            code: "ALREADY_VOTED",
            title: "Vote Already Casted",
            message: `Voter ID ${cleanId} (${localMatch.fullName}) is already marked "Voted" in Supabase.`,
          };
        }

        positions.forEach((pos, idx) => {
          const acc = bRows.find((b) => {
            const bPos = b.position_id || (idx === 0 ? pos.id : "");
            return b.status === "accepted" && bPos === pos.id;
          });
          if (acc) {
            votedRoles[pos.id] = {
              ballotId: acc.id,
              positionId: pos.id,
              positionName: acc.position_name || pos.title,
              candidateId: acc.candidate_id,
              candidateName: acc.candidate_name,
              castAt: acc.cast_at,
            };
          } else {
            const hasCan = bRows.some((b) => {
              const bPos = b.position_id || (idx === 0 ? pos.id : "");
              return b.status === "cancelled" && bPos === pos.id;
            });
            if (hasCan || (!hasAnyPerRole && vRows.length > 0 && vRows[0].final_status === "Cancelled")) {
              cancelledRoleIds.push(pos.id);
            }
          }
        });

        const pendingRoleIds = positions.filter((p) => !votedRoles[p.id]).map((p) => p.id);
        if (pendingRoleIds.length === 0) {
          return {
            ok: false,
            code: "ALREADY_VOTED",
            title: "All Votes Already Casted",
            message: `Voter ID ${cleanId} (${localMatch.fullName}) has already voted for all ${positions.length} roles in Supabase.`,
          };
        }

        const isPartial = Object.keys(votedRoles).length > 0;
        const isCancelled = cancelledRoleIds.length > 0;
        let verificationNote = vRows.length > 0 ? "Not Voted in Supabase" : "Ready in Supabase";
        if (isCancelled && isPartial) {
          verificationNote = `Re-vote open for ${cancelledRoleIds.length} cancelled role(s); ${Object.keys(votedRoles).length} locked`;
        } else if (isCancelled) {
          verificationNote = "Previous vote cancelled in Supabase";
        } else if (isPartial) {
          verificationNote = `${Object.keys(votedRoles).length}/${positions.length} role(s) recorded in Supabase`;
        }

        return {
          ok: true,
          student: { ...localMatch, docId: cleanId },
          voterStatus: isCancelled ? "cancelled" : isPartial ? "partial" : "not_voted",
          pendingRoleIds,
          votedRoles,
          cancelledRoleIds,
          verificationNote,
        };
      }

      return {
        ok: false,
        code: "SUPABASE_REQUIRED",
        title: "Supabase Not Connected",
        message: `${this.backendError ? `${this.backendError} — ` : ""}Votes must save strictly to Supabase. Open Admin -> Sync Roster to Supabase and connect your Publishable key first.`,
      };
    },

    async getHouseCandidates(houseCode) {
      if (this.mode === "supabase") {
        try {
          const rows = await sbRest(
            "GET",
            `/rest/v1/candidates?house_code=eq.${encodeURIComponent(houseCode)}&is_approved=eq.true&select=*`
          );
          if (Array.isArray(rows) && rows.length > 0) {
            return rows.map((c) => ({
              id: c.id,
              admissionNo: c.admission_no,
              fullName: c.full_name,
              className: c.class_name,
              section: c.section,
              houseCode: c.house_code,
              positionId: c.position_id || "CAPTAIN_BOY",
              positionName: c.position_name || "Boys Captain",
              tagline: c.tagline || "",
              isApproved: c.is_approved !== false,
            }));
          }
        } catch (_) {}
        return window.HOUSE_DATA.houseCandidates;
      }
      return window.HOUSE_DATA.houseCandidates;
    },

    async getHouseSnapshot(houseCode) {
      if (this.mode === "supabase") {
        const { electionId, positionId, houseStudents } = window.HOUSE_DATA;
        const positions = getPositionsList();
        const qH = encodeURIComponent(houseCode);
        const [voterRows, ballotRows] = await Promise.all([
          sbFetchAll(`voters?house_code=eq.${qH}&select=*`),
          sbFetchAll(`ballots?house_code=eq.${qH}&select=*&order=cast_at.desc`),
        ]);

        const byAdm = new Map(houseStudents.map((s) => [s.admissionNo, { ...s }]));
        const voterStatus = {};
        const ballotsByAdmRole = new Map();

        ballotRows.forEach((b) => {
          const posId = b.position_id || positionId;
          const k = `${b.admission_no}::${posId}`;
          if (!ballotsByAdmRole.has(k)) ballotsByAdmRole.set(k, []);
          ballotsByAdmRole.get(k).push(b);
        });

        voterRows.forEach((v) => {
          if (!byAdm.has(v.admission_no)) {
            byAdm.set(v.admission_no, {
              admissionNo: v.admission_no,
              fullName: v.full_name || v.admission_no,
              className: v.class_name || "",
              section: v.section || "",
              houseCode,
              isActive: v.is_active !== false,
              isCandidate: false,
              positionName: null,
            });
          }
          let foundPerRole = false;
          positions.forEach((pos) => {
            const list = ballotsByAdmRole.get(`${v.admission_no}::${pos.id}`) || [];
            const acc = list.find((b) => b.status === "accepted");
            const can = list.find((b) => b.status === "cancelled");
            if (acc || can) {
              foundPerRole = true;
              const st = acc ? "voted" : "cancelled";
              voterStatus[statusKey(electionId, v.admission_no, pos.id)] = {
                electionId,
                admissionNo: v.admission_no,
                houseCode,
                positionId: pos.id,
                status: st,
                activeBallotId: acc ? acc.id : null,
                updatedAt: acc ? acc.cast_at : can.cancelled_at,
              };
            }
          });
          if (!foundPerRole && (v.final_status === "Voted" || v.final_status === "Cancelled")) {
            const st = v.final_status === "Voted" ? "voted" : "cancelled";
            const fallbackPosId = positions[0]?.id || positionId;
            voterStatus[statusKey(electionId, v.admission_no, fallbackPosId)] = {
              electionId,
              admissionNo: v.admission_no,
              houseCode,
              positionId: fallbackPosId,
              status: st,
              activeBallotId: st === "voted" ? v.ballot_id : null,
              updatedAt: st === "voted" ? v.cast_at : v.cancelled_at,
            };
          }
        });

        const uniquePaths = Array.from(new Set(ballotRows.map((b) => b.photo_path).filter(Boolean)));
        await Promise.all(uniquePaths.map((p) => resolveSignedPhotoUrl(p)));

        const ballots = await Promise.all(
          ballotRows.map(async (b) => {
            const stu = byAdm.get(b.admission_no) || {};
            const photoDataUrl = b.photo_path ? await resolveSignedPhotoUrl(b.photo_path) : "";
            const posId = b.position_id || positionId;
            return {
              id: b.id,
              electionId: b.election_id || electionId,
              admissionNo: b.admission_no,
              fullName: stu.fullName || b.admission_no,
              className: stu.className || "",
              section: stu.section || "",
              houseCode,
              positionId: posId,
              positionName: b.position_name || "House Captain",
              candidateId: b.candidate_id,
              candidateName: b.candidate_name,
              photoField: b.photo_field || "",
              photoDataUrl,
              status: b.status,
              castAt: b.cast_at,
              cancelledAt: b.cancelled_at,
              cancelReason: b.cancel_reason,
            };
          })
        );

        let houseCandidates = window.HOUSE_DATA.houseCandidates;
        try {
          const liveCands = await this.getHouseCandidates(houseCode);
          if (Array.isArray(liveCands) && liveCands.length > 0) {
            houseCandidates = liveCands;
          }
        } catch (_) {}

        return {
          students: Array.from(byAdm.values()),
          candidates: houseCandidates,
          voterStatus,
          ballots,
          auditLogs: [],
        };
      }
      return {
        students: window.HOUSE_DATA.houseStudents,
        candidates: window.HOUSE_DATA.houseCandidates,
        voterStatus: {},
        ballots: [],
        auditLogs: [],
      };
    },

    async castVote({ student, selections, candidate, photoDataUrl }) {
      const { electionId, positionId, positionName, houseConfig, allStudents, houseCandidates } = window.HOUSE_DATA;
      const positions = getPositionsList();
      const nowIso = new Date().toISOString();

      let rawSelections = [];
      if (Array.isArray(selections) && selections.length > 0) {
        rawSelections = selections;
      } else if (selections && typeof selections === "object") {
        rawSelections = Object.entries(selections)
          .filter(([, cand]) => Boolean(cand))
          .map(([pid, cand]) => ({ positionId: pid, candidate: cand }));
      } else if (candidate) {
        rawSelections = [{ positionId: candidate.positionId || positionId, candidate }];
      }
      if (rawSelections.length === 0) {
        throw new Error("Select a candidate for each open leadership role.");
      }

      const normalizedSels = rawSelections.map((sel) => {
        const cand = sel.candidate || sel;
        const pos = positions.find((p) => p.id === (sel.positionId || cand?.positionId));
        const posId = pos ? pos.id : sel.positionId || cand?.positionId || positionId;
        const posTitle = pos ? pos.title : cand?.positionName || positionName;
        const candDoc = houseCandidates.find((c) => c.id === cand?.id);
        if (!candDoc || !candDoc.isApproved) {
          throw new Error(`Selected candidate for ${posTitle} is not eligible for this house.`);
        }
        if (candDoc.positionId && candDoc.positionId !== posId) {
          throw new Error(`${candDoc.fullName} does not run for ${posTitle}.`);
        }
        return { positionId: posId, positionName: posTitle, candidate: candDoc };
      });

      if (this.mode === "supabase") {
        let stu = allStudents.find((s) => s.admissionNo === student.admissionNo);
        if (student.admissionNo === "0000" && !stu) {
          stu = { admissionNo: "0000", fullName: "Demo User", className: "Demo", section: "All", houseCode: "ALL", isActive: true };
        }
        if (!stu || !stu.isActive || (stu.houseCode !== houseConfig.code && stu.houseCode !== "ALL" && stu.admissionNo !== "0000" && houseConfig.code !== "CENTRAL")) {
          throw new Error("Student does not belong to this house roster.");
        }

        const qAdm = encodeURIComponent(stu.admissionNo);
        const existingRows = await sbRest("GET", `/rest/v1/voters?admission_no=eq.${qAdm}&select=*`);
        let voterRow = existingRows[0] || null;
        if (!voterRow) {
          const created = await sbRest(
            "POST",
            "/rest/v1/voters",
            {
              admission_no: stu.admissionNo,
              full_name: stu.fullName,
              class_name: stu.className,
              section: stu.section,
              house_code: houseConfig.code,
              house_name: houseConfig.name,
              final_status: "Not Voted",
              voted_for: "",
              vote_10_boy: "",
              vote_10_girl: "",
              vote_9_boy: "",
              vote_9_girl: "",
              position_name: "4 Roles",
              photo_path: "",
              photos_history: [],
              is_active: true,
              updated_at: nowIso,
            },
            "resolution=ignore-duplicates,return=representation"
          );
          voterRow = Array.isArray(created) ? created[0] : created;
        }

        const priorBallots = await sbRest(
          "GET",
          `/rest/v1/ballots?admission_no=eq.${qAdm}&select=id,position_id,position_name,candidate_id,candidate_name,status,photo_field,photo_path,cast_at&order=cast_at.desc`
        );

        for (const sel of normalizedSels) {
          const dup = priorBallots.find((b) => b.status === "accepted" && (b.position_id || sel.positionId) === sel.positionId);
          if (dup && stu.admissionNo !== "0000") {
            throw new Error(`Vote already casted for ${sel.positionName} (${stu.admissionNo}).`);
          }
        }

        const existingHist = Array.isArray(voterRow?.photos_history) ? voterRow.photos_history : [];
        const priorPhotoBatches = new Set(priorBallots.map((b) => b.photo_field || b.cast_at).filter(Boolean)).size;
        const attemptNum = Math.max(priorPhotoBatches, existingHist.length) + 1;
        const photoField = attemptNum === 1 ? "Photo" : `Photo${attemptNum}`;
        const photoFile = attemptNum === 1 ? "photo.jpg" : `photo${attemptNum}.jpg`;
        const relPath = `${houseConfig.slug}/${stu.admissionNo}/${photoFile}`;
        const storedPath = photoDataUrl ? await uploadPhotoToStorage(relPath, photoDataUrl) : "";

        const tsBase = Date.now().toString(36).toUpperCase();
        const ballotsToInsert = normalizedSels.map((sel) => {
          const safeRole = sel.positionId.replace(/[^A-Z0-9]/g, "");
          return {
            id: `BLT-${tsBase}-${stu.admissionNo}-${safeRole}`,
            election_id: electionId,
            admission_no: stu.admissionNo,
            house_code: houseConfig.code,
            position_id: sel.positionId,
            position_name: sel.positionName,
            candidate_id: sel.candidate.id,
            candidate_name: sel.candidate.fullName,
            photo_field: photoField,
            photo_path: storedPath,
            status: "accepted",
            cast_at: nowIso,
            cancelled_at: null,
            cancel_reason: null,
            cancelled_by: null,
          };
        });

        await sbRest("POST", "/rest/v1/ballots", ballotsToInsert);

        const acceptedByPos = new Map();
        priorBallots
          .filter((b) => b.status === "accepted" && b.position_id)
          .forEach((b) => acceptedByPos.set(b.position_id, { candidateName: b.candidate_name, candidateId: b.candidate_id }));
        normalizedSels.forEach((sel) => {
          acceptedByPos.set(sel.positionId, { candidateName: sel.candidate.fullName, candidateId: sel.candidate.id });
        });

        const voteColsPatch = {};
        const summaryParts = [];
        positions.forEach((pos) => {
          const col = ROLE_VOTE_COLS[pos.id];
          const chosen = acceptedByPos.get(pos.id);
          if (col) voteColsPatch[col] = chosen ? chosen.candidateName : "";
          if (chosen) summaryParts.push(`${pos.shortTitle || pos.title}: ${chosen.candidateName}`);
        });

        const allRolesAccepted = positions.every((p) => acceptedByPos.has(p.id));
        const lastBallot = ballotsToInsert[ballotsToInsert.length - 1];
        const nextHistory = [...existingHist];
        if (storedPath) {
          nextHistory.push({ field: photoField, path: storedPath, ballotId: lastBallot.id, castAt: nowIso });
        }

        await sbRest("PATCH", `/rest/v1/voters?admission_no=eq.${qAdm}`, {
          ...voteColsPatch,
          final_status: allRolesAccepted ? "Voted" : "Cancelled",
          voted_for: summaryParts.join(" | "),
          candidate_id: lastBallot.candidate_id,
          position_name: allRolesAccepted ? `All ${positions.length} Roles` : lastBallot.position_name,
          ballot_id: lastBallot.id,
          cast_at: nowIso,
          cancelled_at: null,
          active_photo_field: photoField,
          photo_path: storedPath,
          photos_history: nextHistory,
          updated_at: nowIso,
        });

        if (channel) channel.postMessage({ type: "store_updated", at: Date.now() });
        return { ok: true, ballotIds: ballotsToInsert.map((b) => b.id), ballotId: lastBallot.id };
      }

      throw new Error(this.backendError || "Supabase is not connected — votes must be saved strictly in Supabase, never locally.");
    },

    subscribeHouseUpdates(houseCode, onChange) {
      if (channel) {
        channel.addEventListener("message", () => onChange());
      }
      window.addEventListener("storage", (e) => {
        if (e.key === SB_CFG_KEY) onChange();
      });
      if (this.mode === "supabase" && !this._pollTimer) {
        this._pollTimer = setInterval(() => onChange(), 3000);
      }
    },
  };

  // Dedicated Pendrive / Local Folder Storage Engine (House-Isolated)
  const FS_DB_NAME = "election_spr_2026_pendrive_v1";
  const FS_STORE = "handles";

  function openHandleDb() {
    return new Promise((resolve, reject) => {
      if (typeof indexedDB === "undefined") {
        reject(new Error("IndexedDB unavailable"));
        return;
      }
      const req = indexedDB.open(FS_DB_NAME, 1);
      req.onupgradeneeded = () => {
        if (!req.result.objectStoreNames.contains(FS_STORE)) {
          req.result.createObjectStore(FS_STORE);
        }
      };
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  }

  async function idbGetHandle(key) {
    try {
      const db = await openHandleDb();
      return await new Promise((resolve) => {
        const tx = db.transaction(FS_STORE, "readonly");
        const req = tx.objectStore(FS_STORE).get(key);
        req.onsuccess = () => resolve(req.result || null);
        req.onerror = () => resolve(null);
      });
    } catch (_) {
      return null;
    }
  }

  async function idbSetHandle(key, value) {
    try {
      const db = await openHandleDb();
      await new Promise((resolve) => {
        const tx = db.transaction(FS_STORE, "readwrite");
        tx.objectStore(FS_STORE).put(value, key);
        tx.oncomplete = () => resolve();
        tx.onerror = () => resolve();
      });
    } catch (_) {}
  }

  async function photoSourceToBytes(photoSrc) {
    const src = String(photoSrc || "").trim();
    if (!src) return null;
    if (src.startsWith("data:")) {
      const parts = src.split(",");
      if (parts.length < 2) return null;
      const bin = atob(parts[1]);
      const bytes = new Uint8Array(bin.length);
      for (let i = 0; i < bin.length; i++) {
        bytes[i] = bin.charCodeAt(i);
      }
      return bytes;
    }
    try {
      const resp = await fetch(src, { cache: "no-store" });
      if (!resp.ok) return null;
      const buf = await resp.arrayBuffer();
      return new Uint8Array(buf);
    } catch (_) {
      return null;
    }
  }

  function getVoterFolderName(admissionNo, fullName) {
    const cleanId = String(admissionNo || "unknown").trim().replace(/[<>:"/\\|?*\x00-\x1f]/g, "_");
    const cleanName = String(fullName || "Student")
      .trim()
      .replace(/[<>:"/\\|?*\x00-\x1f]/g, "_")
      .replace(/\s+/g, "_");
    return `${cleanId}_${cleanName}`;
  }

  function formatLocalTime(iso) {
    if (!iso) return "—";
    try {
      return new Date(iso).toLocaleString();
    } catch (_) {
      return iso;
    }
  }

  function buildCancelledMarkdown({ student, houseMeta, cancelledBallots, photoByBallotId }) {
    const cls = student ? `${student.className}-${student.section}` : "—";
    const lines = [
      `# Cancelled Ballot Record — ${student.fullName} (${student.admissionNo})`,
      "",
      "## Student Info",
      "",
      `- **Admission No:** \`${student.admissionNo}\``,
      `- **Student Name:** ${student.fullName}`,
      `- **Class & Section:** ${cls}`,
      `- **House:** ${houseMeta.name} House`,
      "",
      "",
      "## Cancelled Vote Details",
      "",
    ];

    cancelledBallots.forEach((b, idx) => {
      const cPhoto = (photoByBallotId && photoByBallotId.get(b.id)) || (idx === 0 ? "photo.jpg" : `photo${idx + 1}.jpg`);
      if (cancelledBallots.length > 1) {
        lines.push(`### Cancelled Attempt ${idx + 1}`, "");
      }
      lines.push(
        `- **Voted For (Cancelled):** ${b.candidateName} (\`${b.candidateId || ""}\`)`,
        `- **Position:** ${b.positionName || window.HOUSE_DATA.positionName}`,
        `- **Status:** Cancelled`,
        `- **Ballot ID:** \`${b.id}\``,
        `- **Cast Time:** ${formatLocalTime(b.castAt)}`,
        `- **Cancelled Time:** ${formatLocalTime(b.cancelledAt)}`,
        `- **Reason:** ${b.cancelReason || "Cancelled by Admin"}`,
        `- **Photo File:** \`${cPhoto}\``,
        ""
      );
    });

    return lines.join("\n") + "\n";
  }

  function buildVoterMarkdown({ student, houseMeta, activeBallot, activeBallots, cancelledBallots, stageLabel, photoByBallotId }) {
    const cls = student ? `${student.className}-${student.section}` : "—";
    const list = Array.isArray(activeBallots) ? activeBallots : activeBallot ? [activeBallot] : [];
    const lines = [
      `# Voter Record — ${student.fullName} (${student.admissionNo})`,
      "",
      "## Student Info",
      "",
      `- **Admission No:** \`${student.admissionNo}\``,
      `- **Student Name:** ${student.fullName}`,
      `- **Class & Section:** ${cls}`,
      `- **House:** ${houseMeta.name} House`,
      "",
      "",
      "",
      "## Vote Details",
      "",
    ];

    if (list.length > 0) {
      const uniquePhotoFiles = Array.from(
        new Set(list.map((b) => (photoByBallotId && photoByBallotId.get(b.id)) || "photo.jpg"))
      );
      const latestCastAt = list.map((b) => b.castAt).filter(Boolean).sort().pop() || "";
      list.forEach((b) => {
        const posLabel = b.positionName || window.HOUSE_DATA.positionName;
        const pf = (photoByBallotId && photoByBallotId.get(b.id)) || "photo.jpg";
        lines.push(`- **${posLabel}:** ${b.candidateName} (\`${b.candidateId || ""}\` · \`${b.id}\` · \`${pf}\`)`);
      });
      lines.push(
        `- **Status:** Accepted (${list.length} role${list.length > 1 ? "s" : ""})`,
        `- **Cast Time:** ${formatLocalTime(latestCastAt)}`,
        `- **Photo File${uniquePhotoFiles.length > 1 ? "s" : ""}:** ${uniquePhotoFiles.map((f) => `\`${f}\``).join(", ")}`
      );
    } else {
      const position = (cancelledBallots && cancelledBallots[0]?.positionName) || "All 4 Leadership Roles";
      const statusText = stageLabel || "Voting Started (Verified — Selecting Candidates)";
      lines.push(
        `- **Voted For:** Pending Selection`,
        `- **Position:** ${position}`,
        `- **Status:** ${statusText}`,
        `- **Started At:** ${formatLocalTime(new Date().toISOString())}`
      );
    }

    return lines.join("\n") + "\n";
  }

  function buildHouseSummaryMarkdown(meta, students, candidates, ballots) {
    const eligible = students.filter((s) => s.isActive).length;
    const accepted = ballots.filter((b) => b.status === "accepted");
    const cancelled = ballots.filter((b) => b.status === "cancelled");
    const votedStudents = new Set(accepted.map((b) => b.admissionNo)).size;
    const pct = eligible ? Math.round((votedStudents / eligible) * 100) : 0;

    const lines = [
      `# ${meta.name} House — Local Backup Summary`,
      "",
      `- **Last Updated:** ${new Date().toISOString()}`,
      `- **Eligible Students:** ${eligible}`,
      `- **Voters With Accepted Votes:** ${votedStudents} (${pct}% turnout · ${accepted.length} role ballots)`,
      `- **Cancelled Ballots:** ${cancelled.length}`,
      `- **Remaining To Vote:** ${Math.max(0, eligible - votedStudents)}`,
      "",
      "## Candidate Tally (Accepted Votes)",
      "",
      "| Role | Candidate | Admission No | Class | Accepted Votes |",
      "| :--- | :--- | :--- | :--- | :---: |",
    ];

    candidates.forEach((c) => {
      const count = accepted.filter((b) => b.candidateId === c.id).length;
      lines.push(`| ${c.positionName || "Role"} | ${c.fullName} | \`${c.admissionNo}\` | ${c.className}-${c.section} | ${count} |`);
    });

    lines.push(
      "",
      "## Recorded Voter Folders",
      "",
      "| Folder | Student | Status | Voted For |",
      "| :--- | :--- | :--- | :--- |"
    );

    const byAdm = new Map();
    ballots.forEach((b) => {
      if (!byAdm.has(b.admissionNo)) byAdm.set(b.admissionNo, []);
      byAdm.get(b.admissionNo).push(b);
    });

    byAdm.forEach((list, admNo) => {
      const activeList = list.filter((b) => b.status === "accepted");
      const latest = activeList[0] || list[0];
      const folder = getVoterFolderName(admNo, latest.fullName);
      const summaryChoice = activeList.length
        ? activeList.map((b) => `${b.positionName}: ${b.candidateName}`).join(" ; ")
        : `${latest.positionName}: ${latest.candidateName}`;
      lines.push(
        `| \`${folder}/\` | ${latest.fullName} | ${activeList.length > 0 ? `Accepted (${activeList.length})` : "Cancelled"} | ${summaryChoice} |`
      );
    });

    return lines.join("\n") + "\n";
  }

  async function writeBinaryFile(dirHandle, filename, bytes) {
    const fileHandle = await dirHandle.getFileHandle(filename, { create: true });
    const writable = await fileHandle.createWritable();
    await writable.write(bytes);
    await writable.close();
  }

  async function writeTextFile(dirHandle, filename, content) {
    const fileHandle = await dirHandle.getFileHandle(filename, { create: true });
    const writable = await fileHandle.createWritable();
    await writable.write(content);
    await writable.close();
  }

  const pendriveState = {
    dirHandle: null,
    connected: false,
    scopeKey: null,
    houseMeta: null,
    getSnapshotFn: null,
    widgetEls: null,
    writtenPhotos: new Set(),
    boundPhotoNames: new Map(),
    activeStartedFolder: null,
    writeQueue: Promise.resolve(),
  };

  async function readTextFileSafe(dirHandle, filename) {
    try {
      const fh = await dirHandle.getFileHandle(filename, { create: false });
      const file = await fh.getFile();
      return await file.text();
    } catch (_) {
      return null;
    }
  }

  async function fileExistsSafe(dirHandle, filename) {
    try {
      await dirHandle.getFileHandle(filename, { create: false });
      return true;
    } catch (_) {
      return false;
    }
  }

  async function removeFileSafe(dirHandle, filename) {
    try {
      if (typeof dirHandle.removeEntry === "function") {
        await dirHandle.removeEntry(filename);
      }
    } catch (_) {}
  }

  async function resolvePhotoFilename(voterDir, folderName, ballot, attemptIdx, usedNames) {
    const ballotId = ballot?.id || ballot;
    const fieldMatch = String(ballot?.photoField || "").match(/^(?:Photo|photo)(\d*)$/);
    if (fieldMatch) {
      const num = fieldMatch[1];
      const exactName = !num || num === "1" ? "photo.jpg" : `photo${num}.jpg`;
      if (!usedNames || !usedNames.has(exactName)) {
        if (usedNames) usedNames.add(exactName);
        return exactName;
      }
    }
    const cacheKey = `${folderName}::${ballotId}`;
    if (pendriveState.boundPhotoNames.has(cacheKey)) {
      const cached = pendriveState.boundPhotoNames.get(cacheKey);
      if (!usedNames || !usedNames.has(cached)) {
        if (usedNames) usedNames.add(cached);
        return cached;
      }
    }
    const [resMd, canMd] = await Promise.all([
      readTextFileSafe(voterDir, "result.md"),
      readTextFileSafe(voterDir, "cancelled.md"),
    ]);
    const escapedId = String(ballotId || "").replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const idRe = new RegExp("`" + escapedId + "`[^\\n]*(?:\\n[^\\n]*){0,6}?`(photo\\d*\\.jpg)`");
    for (const mdText of [canMd, resMd]) {
      if (!mdText) continue;
      const m = mdText.match(idRe);
      if (m && m[1] && (!usedNames || !usedNames.has(m[1]))) {
        pendriveState.boundPhotoNames.set(cacheKey, m[1]);
        if (usedNames) usedNames.add(m[1]);
        return m[1];
      }
    }
    let idx = attemptIdx;
    let candidateName = idx === 0 ? "photo.jpg" : `photo${idx + 1}.jpg`;
    while ((usedNames && usedNames.has(candidateName)) || (await fileExistsSafe(voterDir, candidateName))) {
      idx += 1;
      candidateName = `photo${idx + 1}.jpg`;
    }
    pendriveState.boundPhotoNames.set(cacheKey, candidateName);
    if (usedNames) usedNames.add(candidateName);
    return candidateName;
  }

  function refreshWidgetUi() {
    const w = pendriveState.widgetEls;
    if (!w) return;
    w.pill.classList.toggle("is-connected", pendriveState.connected);
    w.dot.classList.toggle("is-green", pendriveState.connected);
    w.dot.classList.toggle("is-red", !pendriveState.connected);
    w.selectBtn.hidden = pendriveState.connected;
    if (pendriveState.connected && pendriveState.dirHandle) {
      w.statusBtn.title = `Saving ${pendriveState.houseMeta.name} House voter folders to "${pendriveState.dirHandle.name}" (click to change folder)`;
    } else {
      w.statusBtn.title = `Select pendrive folder for ${pendriveState.houseMeta?.name || "this"} House`;
    }
  }

  async function writeHouseBundleToDisk(snapshot) {
    const dir = pendriveState.dirHandle;
    const meta = pendriveState.houseMeta;
    if (!dir || !meta || !pendriveState.connected) return;

    const students = (snapshot.students || []).filter((s) => s.houseCode === meta.code);
    const candidates = (snapshot.candidates || []).filter((c) => c.houseCode === meta.code && c.isApproved);
    const ballots = (snapshot.ballots || []).filter((b) => b.houseCode === meta.code);

    await writeTextFile(
      dir,
      `${meta.code}_SUMMARY.md`,
      buildHouseSummaryMarkdown(meta, students, candidates, ballots)
    );

    if (ballots.length === 0) {
      pendriveState.writtenPhotos.clear();
      return;
    }

    const byStudent = new Map();
    ballots.forEach((b) => {
      if (!byStudent.has(b.admissionNo)) byStudent.set(b.admissionNo, []);
      byStudent.get(b.admissionNo).push(b);
    });

    for (const [admNo, list] of byStudent.entries()) {
      const stu = students.find((s) => s.admissionNo === admNo) || list[0];
      const ordered = [...list].sort((a, b) => (a.castAt || "").localeCompare(b.castAt || ""));
      const activeBallots = ordered.filter((b) => b.status === "accepted");
      const cancelledBallots = ordered.filter((b) => b.status === "cancelled");
      const folderName = getVoterFolderName(admNo, stu.fullName);
      const voterDir = await dir.getDirectoryHandle(folderName, { create: true });

      const photoByBallotId = new Map();
      const usedNames = new Set();
      const seenCastTimes = new Map();
      for (let i = 0; i < ordered.length; i++) {
        const b = ordered[i];
        const batchKey = b.castAt || b.photoField || `i_${i}`;
        let fname = seenCastTimes.get(batchKey);
        if (!fname) {
          fname = await resolvePhotoFilename(voterDir, folderName, b, seenCastTimes.size, usedNames);
          seenCastTimes.set(batchKey, fname);
        }
        photoByBallotId.set(b.id, fname);
        if (b.photoDataUrl) {
          const photoKey = `${folderName}_${fname}`;
          if (!pendriveState.writtenPhotos.has(photoKey) && !(await fileExistsSafe(voterDir, fname))) {
            const bytes = await photoSourceToBytes(b.photoDataUrl);
            if (bytes) {
              await writeBinaryFile(voterDir, fname, bytes);
              pendriveState.writtenPhotos.add(photoKey);
            }
          } else {
            pendriveState.writtenPhotos.add(photoKey);
          }
        }
      }

      if (cancelledBallots.length > 0) {
        await writeTextFile(
          voterDir,
          "cancelled.md",
          buildCancelledMarkdown({ student: stu, houseMeta: meta, cancelledBallots, photoByBallotId })
        );
      } else {
        await removeFileSafe(voterDir, "cancelled.md");
      }

      if (activeBallots.length > 0) {
        const md = buildVoterMarkdown({
          student: stu,
          houseMeta: meta,
          activeBallots,
          cancelledBallots,
          photoByBallotId,
        });
        await writeTextFile(voterDir, "result.md", md);
      } else {
        await removeFileSafe(voterDir, "result.md");
      }
    }
  }

  function enqueuePendriveWrite(snapshot) {
    if (!pendriveState.connected || !pendriveState.dirHandle) return Promise.resolve(false);
    pendriveState.writeQueue = pendriveState.writeQueue
      .then(async () => {
        await writeHouseBundleToDisk(snapshot);
        return true;
      })
      .catch((err) => {
        console.warn("Pendrive write failed; disconnecting storage status:", err);
        pendriveState.connected = false;
        pendriveState.dirHandle = null;
        refreshWidgetUi();
        return false;
      });
    return pendriveState.writeQueue;
  }

  window.PendriveStorage = {
    async selectFolder() {
      if (typeof window.showDirectoryPicker !== "function") {
        alert("Direct pendrive folder saving requires Chrome or Edge over http://localhost or https://.");
        return false;
      }
      try {
        const picked = await window.showDirectoryPicker({
          id: pendriveState.scopeKey || "house_pendrive",
          mode: "readwrite",
        });
        let perm = await picked.queryPermission({ mode: "readwrite" });
        if (perm !== "granted") {
          perm = await picked.requestPermission({ mode: "readwrite" });
        }
        if (perm !== "granted") {
          return false;
        }
        pendriveState.dirHandle = picked;
        pendriveState.connected = true;
        pendriveState.writtenPhotos.clear();
        await idbSetHandle(pendriveState.scopeKey, picked);
        refreshWidgetUi();
        await this.syncNow();
        return true;
      } catch (err) {
        if (err && err.name !== "AbortError") {
          console.warn("Unable to open local storage folder:", err);
          alert("Could not access the selected folder. Please choose a writable folder on your pendrive.");
        }
        return false;
      }
    },

    async mount({ container, houseMeta, getSnapshot }) {
      if (!container) return;
      pendriveState.houseMeta = houseMeta;
      pendriveState.scopeKey = `house_${houseMeta.slug}`;
      pendriveState.getSnapshotFn = getSnapshot;

      container.innerHTML = `
        <div class="storage-pill" role="region" aria-label="Local pendrive storage status">
          <button type="button" class="storage-status-btn" title="Local storage folder not selected">
            <span class="storage-dot is-red" aria-hidden="true"></span>
            <span class="storage-label">Local Storage</span>
          </button>
          <button type="button" class="storage-select-btn">Select</button>
        </div>
      `;

      pendriveState.widgetEls = {
        pill: container.querySelector(".storage-pill"),
        statusBtn: container.querySelector(".storage-status-btn"),
        dot: container.querySelector(".storage-dot"),
        selectBtn: container.querySelector(".storage-select-btn"),
      };

      const onPick = () => this.selectFolder();
      pendriveState.widgetEls.selectBtn.addEventListener("click", onPick);
      pendriveState.widgetEls.statusBtn.addEventListener("click", onPick);

      const saved = await idbGetHandle(pendriveState.scopeKey);
      if (saved && typeof saved.queryPermission === "function") {
        try {
          const perm = await saved.queryPermission({ mode: "readwrite" });
          if (perm === "granted") {
            pendriveState.dirHandle = saved;
            pendriveState.connected = true;
            refreshWidgetUi();
            await this.syncNow();
            return;
          }
        } catch (_) {}
      }
      refreshWidgetUi();
    },

    async markVoterStarted(student) {
      if (!pendriveState.connected || !pendriveState.dirHandle || !pendriveState.houseMeta || !student) {
        return false;
      }
      const meta = pendriveState.houseMeta;
      if (student.houseCode !== meta.code && student.houseCode !== "ALL" && student.admissionNo !== "0000" && meta.code !== "CENTRAL") return false;
      const folderName = getVoterFolderName(student.admissionNo, student.fullName);
      pendriveState.writeQueue = pendriveState.writeQueue
        .then(async () => {
          const dir = pendriveState.dirHandle;
          let folderExisted = false;
          try {
            await dir.getDirectoryHandle(folderName, { create: false });
            folderExisted = true;
          } catch (_) {}
          const voterDir = await dir.getDirectoryHandle(folderName, { create: true });
          if (!folderExisted) {
            const md = buildVoterMarkdown({
              student,
              houseMeta: meta,
              activeBallots: [],
              cancelledBallots: [],
              stageLabel: "Voting Started (Verified — Selecting Candidates)",
            });
            await writeTextFile(voterDir, "result.md", md);
            pendriveState.activeStartedFolder = folderName;
          } else {
            pendriveState.activeStartedFolder = null;
          }
          return true;
        })
        .catch((err) => {
          console.warn("Pendrive start-folder write failed:", err);
          pendriveState.connected = false;
          pendriveState.dirHandle = null;
          refreshWidgetUi();
          return false;
        });
      return pendriveState.writeQueue;
    },

    async clearIncompleteStarted() {
      const folderToClean = pendriveState.activeStartedFolder;
      pendriveState.activeStartedFolder = null;
      if (!folderToClean || !pendriveState.connected || !pendriveState.dirHandle) return;
      const dir = pendriveState.dirHandle;
      pendriveState.writeQueue = pendriveState.writeQueue
        .then(async () => {
          if (typeof dir.removeEntry === "function") {
            await dir.removeEntry(folderToClean, { recursive: true });
          }
        })
        .catch(() => {});
      return pendriveState.writeQueue;
    },

    async syncNow() {
      pendriveState.activeStartedFolder = null;
      if (!pendriveState.connected || !pendriveState.dirHandle || !pendriveState.getSnapshotFn) {
        return false;
      }
      try {
        const snap = await pendriveState.getSnapshotFn();
        return await enqueuePendriveWrite(snap);
      } catch (err) {
        console.warn("Unable to fetch snapshot for pendrive backup:", err);
        return false;
      }
    },
  };

  if (channel) {
    channel.addEventListener("message", () => {
      if (pendriveState.connected) {
        window.PendriveStorage.syncNow();
      }
    });
  }
  window.addEventListener("storage", (e) => {
    if (e.key === SB_CFG_KEY && pendriveState.connected) {
      window.PendriveStorage.syncNow();
    }
  });
})();
"""

APP_JS = r"""// House Booth 5-Step Kiosk Controller (Warm Cream + Automatic Photo Capture)
(function () {
  const { houseConfig, positions } = window.HOUSE_DATA;

  const state = {
    step: 1,
    verifiedStudent: null,
    pendingRoleIds: [],
    votedRoles: {},
    cancelledRoleIds: [],
    selectedByRole: {},
    mediaStream: null,
    resetInterval: null,
    resetTimeout: null,
    isSubmitting: false,
  };

  const scannerState = {
    mode: localStorage.getItem("election_voter_input_mode") || "scan",
    buffer: "",
    lastKeystrokeTime: 0,
    pairedDeviceName: localStorage.getItem("election_usb_scanner_name") || "",
  };

  const el = {
    stepPanels: [1, 2, 3, 4].map((n) => document.getElementById(`step-${n}`)),
    stepIndicators: Array.from(document.querySelectorAll("[data-step-indicator]")),
    admissionForm: document.getElementById("admission-form"),
    admissionInput: document.getElementById("admission-input"),
    verifyBtn: document.getElementById("verify-btn"),
    step1Error: document.getElementById("step1-error"),
    step1ErrorTitle: document.getElementById("step1-error-title"),
    step1ErrorMsg: document.getElementById("step1-error-msg"),

    tabScanMode: document.getElementById("tab-scan-mode"),
    tabManualMode: document.getElementById("tab-manual-mode"),
    paneBarcodeScan: document.getElementById("pane-barcode-scan"),
    paneManualEntry: document.getElementById("pane-manual-entry"),
    scannerStreamInput: document.getElementById("barcode-scanner-stream"),
    scannerKioskBox: document.querySelector(".scanner-kiosk-box"),
    scannerStatusText: document.getElementById("scanner-status-text"),
    scannerDeviceStatus: document.getElementById("scanner-device-status"),
    detectUsbBtn: document.getElementById("detect-usb-scanner-btn"),
    pairedDeviceName: document.getElementById("paired-device-name"),
    scannerLiveFeedback: document.getElementById("scanner-live-feedback"),
    scanFeedbackText: document.getElementById("scan-feedback-text"),

    voterInitials: document.getElementById("voter-initials"),
    voterName: document.getElementById("voter-name"),
    voterIdBadge: document.getElementById("voter-id-badge"),
    voterMeta: document.getElementById("voter-meta"),
    voterRoleTag: document.getElementById("voter-role-tag"),
    voterReauthTag: document.getElementById("voter-reauth-tag"),
    autoCamStatus: document.getElementById("auto-cam-status"),

    cameraVideo: document.getElementById("camera-video"),
    cameraCanvas: document.getElementById("camera-canvas"),
    backToStep1Btn: document.getElementById("back-to-step1-btn"),
    nextToVoteBtn: document.getElementById("next-to-vote-btn"),

    step3Subtitle: document.getElementById("step3-subtitle"),
    candidateGrid: document.getElementById("candidate-grid"),
    castActionBar: document.getElementById("cast-action-bar"),
    selectedProgressLabel: document.getElementById("selected-progress-label"),
    selectedCandidateName: document.getElementById("selected-candidate-name"),
    castVoteBtn: document.getElementById("cast-vote-btn"),
    step3Error: document.getElementById("step3-error"),
    step3ErrorMsg: document.getElementById("step3-error-msg"),
    backToStep2Btn: document.getElementById("back-to-step2-btn"),

    faceGuardModal: document.getElementById("face-guard-modal"),
    faceGuardBadge: document.getElementById("face-guard-badge"),
    faceGuardTitle: document.getElementById("face-guard-title"),
    faceGuardDesc: document.getElementById("face-guard-desc"),
    faceLiveVideo: document.getElementById("face-live-video"),
    faceOvalGuide: document.getElementById("face-oval-guide"),
    faceLiveStatusPill: document.getElementById("face-live-status-pill"),
    faceStatusLabel: document.getElementById("face-status-label"),
    faceGuardCancelBtn: document.getElementById("face-guard-cancel-btn"),
    faceGuardConfirmBtn: document.getElementById("face-guard-confirm-btn"),

    successSummary: document.getElementById("success-summary"),
    resetCountdownText: document.getElementById("reset-countdown-text"),
    resetProgressFill: document.getElementById("reset-progress-fill"),
    resetNowBtn: document.getElementById("reset-now-btn"),
  };

  function getInitials(name) {
    return String(name || "?")
      .trim()
      .split(/\s+/)
      .slice(0, 2)
      .map((p) => p[0])
      .join("")
      .toUpperCase();
  }

  function setLoading(button, loading) {
    const spinner = button.querySelector(".spinner");
    button.disabled = loading;
    button.setAttribute("aria-busy", loading ? "true" : "false");
    if (spinner) spinner.hidden = !loading;
  }

  function goToStep(stepNum) {
    state.step = stepNum;
    el.stepPanels.forEach((panel, idx) => {
      const active = idx + 1 === stepNum;
      panel.hidden = !active;
      panel.classList.toggle("is-visible", active);
    });
    el.stepIndicators.forEach((pill, idx) => {
      const s = idx + 1;
      pill.classList.toggle("is-active", s === stepNum);
      pill.classList.toggle("is-done", s < stepNum);
    });
  }

  function clearStep1Error() {
    el.step1Error.hidden = true;
    el.step1ErrorTitle.textContent = "";
    el.step1ErrorMsg.textContent = "";
    el.admissionInput.classList.remove("is-invalid");
  }

  function showStep1Error(title, msg) {
    el.step1ErrorTitle.textContent = title;
    el.step1ErrorMsg.textContent = msg;
    el.step1Error.hidden = false;
    el.admissionInput.classList.add("is-invalid");
  }

  function stopCamera() {
    if (state.mediaStream) {
      state.mediaStream.getTracks().forEach((t) => t.stop());
      state.mediaStream = null;
    }
    el.cameraVideo.srcObject = null;
  }

  async function warmUpBackgroundCamera() {
    if (state.mediaStream) return;
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      el.autoCamStatus.textContent = "Booth auto-snapshot active (webcam unavailable on this browser).";
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "user", width: { ideal: 480 }, height: { ideal: 360 } },
        audio: false,
      });
      state.mediaStream = stream;
      el.cameraVideo.srcObject = stream;
      await el.cameraVideo.play().catch(() => {});
      el.autoCamStatus.textContent = "Camera ready — verification photo will auto-capture when you press Cast Vote.";
    } catch (_) {
      el.autoCamStatus.textContent = "Booth auto-snapshot ready (camera permission not granted).";
    }
  }

  function generateBoothSnapshot(reasonLabel) {
    const ctx = el.cameraCanvas.getContext("2d");
    const w = el.cameraCanvas.width;
    const h = el.cameraCanvas.height;

    ctx.fillStyle = "#faf6ee";
    ctx.fillRect(0, 0, w, h);

    ctx.strokeStyle = houseConfig.accent;
    ctx.lineWidth = 4;
    ctx.strokeRect(8, 8, w - 16, h - 16);

    ctx.fillStyle = houseConfig.accent;
    ctx.beginPath();
    ctx.arc(w / 2, 108, 42, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = houseConfig.onAccent;
    ctx.font = "bold 28px sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(getInitials(state.verifiedStudent?.fullName), w / 2, 108);

    ctx.fillStyle = "#141413";
    ctx.font = "bold 18px sans-serif";
    ctx.fillText(state.verifiedStudent?.fullName || "Verified Voter", w / 2, 178);

    ctx.fillStyle = "#4a4741";
    ctx.font = "14px monospace";
    ctx.fillText(
      `ID ${state.verifiedStudent?.admissionNo || ""} · ${houseConfig.name} House`,
      w / 2,
      206
    );

    ctx.fillStyle = "#767167";
    ctx.font = "12px monospace";
    ctx.fillText(`${reasonLabel} · ${new Date().toLocaleTimeString()}`, w / 2, 234);

    return el.cameraCanvas.toDataURL("image/jpeg", 0.72);
  }

  let picoClassifier = null;
  async function loadPicoFaceClassifier() {
    if (picoClassifier) return picoClassifier;
    try {
      const res = await fetch("./facefinder");
      if (!res.ok) throw new Error("Status " + res.status);
      const buf = await res.arrayBuffer();
      if (typeof pico !== "undefined" && pico.unpack_cascade) {
        picoClassifier = pico.unpack_cascade(new Int8Array(buf));
      }
    } catch (e) {
      console.warn("Pico facefinder load:", e);
    }
    return picoClassifier;
  }

  function analyzeCameraFrame(ctx, w, h) {
    const imgData = ctx.getImageData(0, 0, w, h);
    const d = imgData.data;
    let sum = 0, sumSq = 0;
    const n = d.length / 4;
    for (let i = 0; i < d.length; i += 4) {
      const g = (d[i] * 299 + d[i + 1] * 587 + d[i + 2] * 114) / 1000;
      sum += g;
      sumSq += g * g;
    }
    const mean = sum / n;
    const variance = (sumSq / n) - (mean * mean);
    const stdDev = Math.sqrt(Math.max(0, variance));

    // Complete dark / finger taped over lens:
    if (mean < 14) {
      return { ok: false, obstructed: true, reason: "Camera is completely covered or too dark. Please remove your hand from the lens." };
    }
    // Palm / hand pressed flat against the lens:
    if (stdDev < 8.5) {
      return { ok: false, obstructed: true, reason: "Camera is blocked by hand or object. Please uncover the lens." };
    }
    return { ok: true, obstructed: false, mean, stdDev, imgData };
  }

  async function detectHumanFace(videoEl, canvasEl) {
    if (!videoEl || videoEl.readyState < 2 || videoEl.videoWidth === 0) {
      return { ok: false, reason: "Webcam is warming up... please look at the screen.", obstructed: false };
    }
    const w = 320, h = 240;
    canvasEl.width = w;
    canvasEl.height = h;
    const ctx = canvasEl.getContext("2d");
    ctx.drawImage(videoEl, 0, 0, w, h);

    const frameAnalysis = analyzeCameraFrame(ctx, w, h);
    if (!frameAnalysis.ok) {
      return { ok: false, reason: frameAnalysis.reason, obstructed: true };
    }

    // Layer 1: Native Chrome / Android Hardware FaceDetector
    if (window.FaceDetector) {
      try {
        const fd = new window.FaceDetector({ fastMode: true, maxDetectedFaces: 2 });
        const nativeFaces = await fd.detect(canvasEl);
        if (nativeFaces && nativeFaces.length > 0) {
          return {
            ok: true,
            faceCount: nativeFaces.length,
            photoDataUrl: canvasEl.toDataURL("image/jpeg", 0.78),
          };
        }
      } catch (_) {}
    }

    // Layer 2: Pico.js Face Cascade
    const classifier = picoClassifier || (await loadPicoFaceClassifier());
    if (classifier && typeof pico !== "undefined") {
      const rgba = frameAnalysis.imgData.data;
      const gray = new Uint8Array(w * h);
      for (let r = 0; r < h; ++r) {
        for (let c = 0; c < w; ++c) {
          gray[r * w + c] = (2 * rgba[r * 4 * w + 4 * c] + 7 * rgba[r * 4 * w + 4 * c + 1] + 1 * rgba[r * 4 * w + 4 * c + 2]) / 10;
        }
      }
      const image = { pixels: gray, nrows: h, ncols: w, ldim: w };
      const params = {
        shiftfactor: 0.1,
        minsize: 36,
        maxsize: 210,
        scalefactor: 1.1,
      };
      let dets = pico.run_cascade(image, classifier, params);
      dets = pico.cluster_detections(dets, 0.2);
      const validFaces = dets.filter((d) => d[3] > 36.0);
      if (validFaces.length > 0) {
        return {
          ok: true,
          faceCount: validFaces.length,
          photoDataUrl: canvasEl.toDataURL("image/jpeg", 0.78),
        };
      }
    }

    return {
      ok: false,
      reason: "Face not detected. Please look directly at the camera.",
      obstructed: false,
    };
  }

  function captureAutomaticPhotoOnCast() {
    if (state.mediaStream && el.cameraVideo.readyState >= 2 && el.cameraVideo.videoWidth > 0) {
      const ctx = el.cameraCanvas.getContext("2d");
      ctx.drawImage(el.cameraVideo, 0, 0, el.cameraCanvas.width, el.cameraCanvas.height);
      const sample = ctx.getImageData(0, 0, 60, 45).data;
      let sum = 0;
      for (let i = 0; i < sample.length; i += 4) {
        sum += sample[i] + sample[i + 1] + sample[i + 2];
      }
      const avgBrightness = sum / (sample.length / 4 * 3);
      if (avgBrightness > 6) {
        return el.cameraCanvas.toDataURL("image/jpeg", 0.75);
      }
    }
    return generateBoothSnapshot("Auto Booth Snapshot");
  }

  function getPositionsList() {
    return Array.isArray(positions) && positions.length
      ? positions
      : [{ id: window.HOUSE_DATA.positionId || "HOUSE_CAPTAIN", title: "House Captain", shortTitle: "House Captain", subtitle: "Class 10" }];
  }

  function updateCastBar() {
    const posList = getPositionsList();
    const pendingIds = state.pendingRoleIds.length ? state.pendingRoleIds : posList.map((p) => p.id);
    const pickedPairs = pendingIds
      .filter((pid) => Boolean(state.selectedByRole[pid]))
      .map((pid) => {
        const pos = posList.find((p) => p.id === pid);
        return `${pos?.shortTitle || pos?.title || pid}: ${state.selectedByRole[pid].fullName}`;
      });
    const pickedCount = pickedPairs.length;
    const totalNeeded = pendingIds.length;

    el.castActionBar.hidden = false;
    if (el.selectedProgressLabel) {
      el.selectedProgressLabel.textContent = `Selected Candidates (${pickedCount} / ${totalNeeded})`;
    }
    el.selectedCandidateName.textContent =
      pickedCount > 0 ? pickedPairs.join(" · ") : "Choose 1 candidate for each open role above";
    el.castVoteBtn.disabled = pickedCount < totalNeeded || totalNeeded === 0;
  }

  async function renderCandidatesStep() {
    const candidates = await window.ElectionBackend.getHouseCandidates(houseConfig.code);
    const posList = getPositionsList();
    if (!state.pendingRoleIds.length) {
      state.pendingRoleIds = posList.filter((p) => !state.votedRoles[p.id]).map((p) => p.id);
    }
    state.selectedByRole = {};
    el.step3Error.hidden = true;
    el.candidateGrid.innerHTML = "";

    if (el.step3Subtitle) {
      if (state.pendingRoleIds.length < posList.length) {
        el.step3Subtitle.textContent = `${state.pendingRoleIds.length} role${state.pendingRoleIds.length > 1 ? "s" : ""} open for ${houseConfig.name} House — previously accepted votes stay locked below.`;
      } else {
        el.step3Subtitle.textContent = `Choose 1 candidate for each of the ${posList.length} ${houseConfig.name} House roles below, then press Cast Vote.`;
      }
    }

    if (!candidates.length) {
      el.candidateGrid.innerHTML = `<p class="panel-subtitle">No approved candidates found for ${houseConfig.name} House.</p>`;
      el.castActionBar.hidden = true;
      return;
    }

    posList.forEach((pos) => {
      const votedBallot = state.votedRoles[pos.id] || null;
      const isCancelledRole = state.cancelledRoleIds.includes(pos.id);
      const roleCands = candidates.filter((c) => (c.positionId || pos.id) === pos.id);

      const section = document.createElement("section");
      section.className = `role-section-card${votedBallot ? " is-locked" : ""}`;
      section.dataset.positionId = pos.id;

      const head = document.createElement("div");
      head.className = "role-section-head";
      const titleGroup = document.createElement("div");
      titleGroup.className = "role-section-title-group";
      const titleEl = document.createElement("h3");
      titleEl.className = "role-section-title";
      titleEl.textContent = pos.title;
      const subEl = document.createElement("span");
      subEl.className = "role-section-sub";
      subEl.textContent = pos.subtitle || "";
      titleGroup.append(titleEl, subEl);

      const pillEl = document.createElement("span");
      pillEl.className = "role-state-pill";
      if (votedBallot) {
        pillEl.classList.add("is-locked");
        pillEl.textContent = `Recorded: ${votedBallot.candidateName}`;
      } else if (isCancelledRole) {
        pillEl.textContent = "Re-vote Open (Cancelled)";
      } else {
        pillEl.textContent = "Select 1 candidate";
      }
      head.append(titleGroup, pillEl);

      const grid = document.createElement("div");
      grid.className = "candidate-grid";
      grid.setAttribute("role", "radiogroup");
      grid.setAttribute("aria-label", `${pos.title} (${pos.subtitle || ""}) candidates`);

      roleCands.forEach((cand) => {
        const card = document.createElement("button");
        card.type = "button";
        card.className = "candidate-card";
        card.dataset.candidateId = cand.id;
        card.setAttribute("role", "radio");
        card.setAttribute("aria-checked", "false");
        card.innerHTML = `
          <div class="candidate-card-top">
            <div class="candidate-avatar" aria-hidden="true">${getInitials(cand.fullName)}</div>
            <span class="select-indicator" aria-hidden="true"></span>
          </div>
          <div>
            <h4 class="candidate-name"></h4>
            <p class="candidate-meta"></p>
          </div>
          <p class="candidate-tagline"></p>
        `;
        card.querySelector(".candidate-name").textContent = cand.fullName;
        card.querySelector(".candidate-meta").textContent = String(cand.admissionNo || "").startsWith("DEMO-")
          ? `${cand.section} · ${pos.subtitle || pos.title}`
          : `ID ${cand.admissionNo} · Class ${cand.className}-${cand.section} · ${pos.title}`;
        card.querySelector(".candidate-tagline").textContent = cand.tagline;

        if (votedBallot) {
          card.disabled = true;
          card.classList.add("is-locked");
          if (cand.id === votedBallot.candidateId) {
            card.classList.add("is-selected");
            card.setAttribute("aria-checked", "true");
            card.querySelector(".select-indicator").textContent = "✓";
          }
        } else {
          card.addEventListener("click", () => {
            Array.from(grid.children).forEach((c) => {
              c.classList.remove("is-selected");
              c.setAttribute("aria-checked", "false");
              c.querySelector(".select-indicator").textContent = "";
            });
            card.classList.add("is-selected");
            card.setAttribute("aria-checked", "true");
            card.querySelector(".select-indicator").textContent = "✓";
            state.selectedByRole[pos.id] = cand;
            section.classList.add("is-complete");
            pillEl.className = "role-state-pill is-picked";
            pillEl.textContent = `Selected: ${cand.fullName}`;
            el.step3Error.hidden = true;
            updateCastBar();
          });
        }

        grid.appendChild(card);
      });

      section.append(head, grid);
      el.candidateGrid.appendChild(section);
    });

    updateCastBar();
  }

  function startAutoResetCountdown() {
    clearInterval(state.resetInterval);
    clearTimeout(state.resetTimeout);

    const totalMs = 2800;
    let remainingSec = 3;
    el.resetCountdownText.textContent = `Returning to Voter ID entry in ${remainingSec}s...`;
    el.resetProgressFill.style.transition = "none";
    el.resetProgressFill.style.transform = "scaleX(1)";
    void el.resetProgressFill.offsetWidth;
    el.resetProgressFill.style.transition = `transform ${totalMs}ms linear`;
    el.resetProgressFill.style.transform = "scaleX(0)";

    state.resetInterval = setInterval(() => {
      remainingSec = Math.max(0, remainingSec - 1);
      el.resetCountdownText.textContent =
        remainingSec > 0
          ? `Returning to Voter ID entry in ${remainingSec}s...`
          : "Resetting booth...";
    }, 950);

    state.resetTimeout = setTimeout(resetBoothToStep1, totalMs);
  }

  function resetBoothToStep1() {
    clearInterval(state.resetInterval);
    clearTimeout(state.resetTimeout);
    closeFaceGuardModal();
    stopCamera();
    state.verifiedStudent = null;
    state.pendingRoleIds = [];
    state.votedRoles = {};
    state.cancelledRoleIds = [];
    state.selectedByRole = {};
    state.isSubmitting = false;
    scannerState.buffer = "";
    el.castVoteBtn.disabled = true;
    if (el.admissionInput) el.admissionInput.value = "";
    if (el.scannerStreamInput) el.scannerStreamInput.value = "";
    if (el.scannerLiveFeedback) el.scannerLiveFeedback.hidden = true;
    clearStep1Error();
    el.step3Error.hidden = true;
    goToStep(1);
    setInputMode(scannerState.mode || "scan");
  }

  function setInputMode(mode) {
    scannerState.mode = mode;
    localStorage.setItem("election_voter_input_mode", mode);

    const isScan = mode === "scan";
    if (el.tabScanMode && el.tabManualMode) {
      el.tabScanMode.classList.toggle("is-active", isScan);
      el.tabScanMode.setAttribute("aria-selected", isScan ? "true" : "false");
      el.tabManualMode.classList.toggle("is-active", !isScan);
      el.tabManualMode.setAttribute("aria-selected", !isScan ? "true" : "false");
    }

    if (el.paneBarcodeScan && el.paneManualEntry) {
      el.paneBarcodeScan.hidden = !isScan;
      el.paneBarcodeScan.classList.toggle("is-active", isScan);
      el.paneManualEntry.hidden = isScan;
      el.paneManualEntry.classList.toggle("is-active", !isScan);
    }

    clearStep1Error();
    if (isScan && el.scannerStreamInput) {
      setTimeout(() => el.scannerStreamInput.focus(), 40);
    } else if (!isScan && el.admissionInput) {
      setTimeout(() => el.admissionInput.focus(), 40);
    }
  }

  if (el.tabScanMode) {
    el.tabScanMode.addEventListener("click", () => setInputMode("scan"));
  }
  if (el.tabManualMode) {
    el.tabManualMode.addEventListener("click", () => setInputMode("manual"));
  }

  function updatePairedScannerUI(name) {
    if (!name) return;
    scannerState.pairedDeviceName = name;
    localStorage.setItem("election_usb_scanner_name", name);
    if (el.pairedDeviceName) {
      el.pairedDeviceName.textContent = `Identified: ${name}`;
      el.pairedDeviceName.hidden = false;
    }
    if (el.scannerStatusText) {
      el.scannerStatusText.textContent = `Scanner Identified: ${name} (Ready)`;
    }
    if (el.scannerDeviceStatus) {
      el.scannerDeviceStatus.classList.remove("is-ready");
      el.scannerDeviceStatus.classList.add("is-paired");
    }
  }

  async function initWebHid() {
    if (scannerState.pairedDeviceName) {
      updatePairedScannerUI(scannerState.pairedDeviceName);
    }
    if (!navigator.hid) return;
    try {
      const devices = await navigator.hid.getDevices();
      if (devices && devices.length > 0) {
        const dev = devices[0];
        updatePairedScannerUI(dev.productName || "USB Barcode Scanner");
      }
    } catch (_) {}
  }

  if (el.detectUsbBtn) {
    el.detectUsbBtn.addEventListener("click", async () => {
      if (!navigator.hid) {
        alert("WebHID API is supported in Chrome and Edge. Your scanner gun still works automatically via Plug & Play!");
        return;
      }
      try {
        const devices = await navigator.hid.requestDevice({ filters: [] });
        if (devices && devices.length > 0) {
          const dev = devices[0];
          updatePairedScannerUI(dev.productName || "USB Barcode Scanner");
        }
      } catch (_) {}
    });
  }

  async function executeVerification(voterId) {
    clearStep1Error();
    const cleanId = String(voterId || "").trim();
    if (!cleanId) {
      showStep1Error("Voter ID Required", "Please scan a voter barcode or enter a valid Voter ID number.");
      return;
    }

    setLoading(el.verifyBtn, true);
    if (el.scannerKioskBox) el.scannerKioskBox.classList.add("is-scanning");

    try {
      await window.ElectionBackend.init();
      const result = await window.ElectionBackend.verifyStudent(
        cleanId,
        houseConfig.code
      );
      if (!result.ok) {
        showStep1Error(result.title, result.message);
        if (el.scannerLiveFeedback) el.scannerLiveFeedback.hidden = true;
        return;
      }

      state.verifiedStudent = result.student;
      state.pendingRoleIds = Array.isArray(result.pendingRoleIds) ? result.pendingRoleIds : [];
      state.votedRoles = result.votedRoles || {};
      state.cancelledRoleIds = Array.isArray(result.cancelledRoleIds) ? result.cancelledRoleIds : [];
      state.selectedByRole = {};
      el.voterInitials.textContent = getInitials(result.student.fullName);
      el.voterName.textContent = result.student.fullName;
      el.voterIdBadge.textContent = `Voter ID ${result.student.admissionNo}`;
      el.voterMeta.textContent = `Class ${result.student.className}-${result.student.section} · ${houseConfig.name} House`;
      el.voterRoleTag.textContent = result.student.isCandidate
        ? `Candidate · ${result.student.positionName || "House Leadership"}`
        : result.verificationNote || "Eligible Voter";
      el.voterReauthTag.hidden = result.voterStatus !== "cancelled";

      goToStep(2);
      if (window.PendriveStorage) {
        window.PendriveStorage.markVoterStarted(result.student);
      }
      warmUpBackgroundCamera();
    } catch (err) {
      showStep1Error(
        "Database Connection Error",
        err?.message || "Unable to verify Voter ID against Supabase. Check your Supabase connection settings."
      );
    } finally {
      setLoading(el.verifyBtn, false);
      if (el.scannerKioskBox) el.scannerKioskBox.classList.remove("is-scanning");
    }
  }

  function triggerScannedVoter(code) {
    const clean = String(code || "").trim();
    if (!clean) return;
    if (el.scannerLiveFeedback && el.scanFeedbackText) {
      el.scanFeedbackText.textContent = `Scanned ID: ${clean}`;
      el.scannerLiveFeedback.hidden = false;
    }
    if (el.admissionInput) el.admissionInput.value = clean;
    executeVerification(clean);
  }

  // Channel 1: Dedicated Invisible Stream Input (Permanently active on "Scan Barcode")
  let streamTimer = null;
  if (el.scannerStreamInput) {
    el.scannerStreamInput.addEventListener("input", () => {
      clearTimeout(streamTimer);
      streamTimer = setTimeout(() => {
        const val = el.scannerStreamInput.value.trim();
        if (val.length >= 2) {
          el.scannerStreamInput.value = "";
          triggerScannedVoter(val);
        }
      }, 100);
    });

    el.scannerStreamInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.keyCode === 13 || e.key === "Tab" || e.keyCode === 9) {
        e.preventDefault();
        clearTimeout(streamTimer);
        const val = el.scannerStreamInput.value.trim();
        if (val.length >= 2) {
          el.scannerStreamInput.value = "";
          triggerScannedVoter(val);
        }
      }
    });
  }

  // Channel 2: Tap/Click anywhere on Step 1 restores scanner focus
  document.addEventListener("click", (e) => {
    if (state.step === 1 && scannerState.mode === "scan" && el.scannerStreamInput) {
      const isInteractive = e.target.closest("button, a, input, select, textarea, [role='button']");
      if (!isInteractive) {
        el.scannerStreamInput.focus();
      }
    }
  });

  // Channel 3: Rapid Scanner Detection on Manual Input (Auto-submits if gun used on manual tab)
  let manualBurstTimer = null;
  let manualBurstCount = 0;
  let manualLastTime = 0;

  el.admissionInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") return;
    const now = performance.now();
    if (now - manualLastTime < 120) {
      manualBurstCount++;
    } else {
      manualBurstCount = 1;
    }
    manualLastTime = now;
  });

  el.admissionInput.addEventListener("input", () => {
    clearStep1Error();
    if (manualBurstCount >= 3) {
      clearTimeout(manualBurstTimer);
      manualBurstTimer = setTimeout(() => {
        const val = el.admissionInput.value.trim();
        if (val.length >= 2) {
          triggerScannedVoter(val);
        }
      }, 120);
    }
  });

  el.admissionForm.addEventListener("submit", (e) => {
    e.preventDefault();
    executeVerification(el.admissionInput.value);
  });

  // Channel 4: Global Barcode Gun Listener (Catches rapid bursts even if blur occurred)
  let globalBufferTimer = null;
  window.addEventListener("keydown", (e) => {
    if (state.step !== 1) return;

    const isInput = e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA";
    if (isInput && e.target !== el.scannerStreamInput) {
      return;
    }

    if (e.key === "Enter" || e.keyCode === 13) {
      clearTimeout(globalBufferTimer);
      if (scannerState.buffer.length >= 2) {
        e.preventDefault();
        const code = scannerState.buffer.trim();
        scannerState.buffer = "";
        triggerScannedVoter(code);
      }
      scannerState.buffer = "";
      return;
    }

    if (e.key && e.key.length === 1 && !e.ctrlKey && !e.metaKey && !e.altKey) {
      scannerState.buffer += e.key;
      clearTimeout(globalBufferTimer);
      globalBufferTimer = setTimeout(() => {
        if (scannerState.buffer.length >= 2) {
          const code = scannerState.buffer.trim();
          scannerState.buffer = "";
          triggerScannedVoter(code);
        }
        scannerState.buffer = "";
      }, 150);
    }
  });

  el.backToStep1Btn.addEventListener("click", async () => {
    if (window.PendriveStorage) {
      await window.PendriveStorage.clearIncompleteStarted();
    }
    resetBoothToStep1();
  });

  el.nextToVoteBtn.addEventListener("click", async () => {
    await renderCandidatesStep();
    goToStep(3);
  });

  el.backToStep2Btn.addEventListener("click", () => {
    goToStep(2);
  });

  let faceCheckInterval = null;
  let steadyFaceCount = 0;
  let lastVerifiedPhoto = "";

  function updateFaceGuardUI(message, isObstructed, isVerified) {
    if (el.faceStatusLabel) el.faceStatusLabel.textContent = message;
    if (el.faceLiveStatusPill) {
      el.faceLiveStatusPill.classList.toggle("is-obstructed", Boolean(isObstructed));
      el.faceLiveStatusPill.classList.toggle("is-verified", Boolean(isVerified));
    }
    if (el.faceOvalGuide) {
      el.faceOvalGuide.classList.toggle("is-obstructed", Boolean(isObstructed));
      el.faceOvalGuide.classList.toggle("is-verified", Boolean(isVerified));
    }
    if (el.faceGuardBadge) {
      if (isVerified) {
        el.faceGuardBadge.className = "badge badge-success";
        el.faceGuardBadge.textContent = "Face Verified";
      } else if (isObstructed) {
        el.faceGuardBadge.className = "badge badge-danger";
        el.faceGuardBadge.textContent = "Camera Obstructed / Hand Detected";
      } else {
        el.faceGuardBadge.className = "badge badge-warning";
        el.faceGuardBadge.textContent = "Face Required to Vote";
      }
    }
  }

  function openFaceGuardModal(initialReason, isObstructed) {
    if (!el.faceGuardModal) return;
    el.faceGuardModal.hidden = false;
    updateFaceGuardUI(initialReason || "Please look directly at the camera.", isObstructed, false);

    if (el.faceLiveVideo && state.mediaStream) {
      el.faceLiveVideo.srcObject = state.mediaStream;
      el.faceLiveVideo.play().catch(() => {});
    }

    steadyFaceCount = 0;
    lastVerifiedPhoto = "";
    if (el.faceGuardConfirmBtn) el.faceGuardConfirmBtn.disabled = true;

    clearInterval(faceCheckInterval);
    faceCheckInterval = setInterval(async () => {
      if (state.isSubmitting) return;
      const res = await detectHumanFace(el.faceLiveVideo || el.cameraVideo, el.cameraCanvas);
      if (res.ok) {
        steadyFaceCount++;
        lastVerifiedPhoto = res.photoDataUrl;
        updateFaceGuardUI("✓ Face Detected! Hold still...", false, true);
        if (el.faceGuardConfirmBtn) el.faceGuardConfirmBtn.disabled = false;
        if (steadyFaceCount >= 3 && !state.isSubmitting) {
          clearInterval(faceCheckInterval);
          await submitFinalVote(lastVerifiedPhoto);
        }
      } else {
        steadyFaceCount = 0;
        updateFaceGuardUI(res.reason, res.obstructed, false);
        if (el.faceGuardConfirmBtn) el.faceGuardConfirmBtn.disabled = true;
      }
    }, 220);
  }

  function closeFaceGuardModal() {
    clearInterval(faceCheckInterval);
    faceCheckInterval = null;
    if (el.faceGuardModal) el.faceGuardModal.hidden = true;
    if (el.faceLiveVideo) el.faceLiveVideo.srcObject = null;
  }

  if (el.faceGuardCancelBtn) {
    el.faceGuardCancelBtn.addEventListener("click", () => {
      closeFaceGuardModal();
      setLoading(el.castVoteBtn, false);
      state.isSubmitting = false;
    });
  }

  if (el.faceGuardConfirmBtn) {
    el.faceGuardConfirmBtn.addEventListener("click", async () => {
      if (lastVerifiedPhoto && !state.isSubmitting) {
        clearInterval(faceCheckInterval);
        await submitFinalVote(lastVerifiedPhoto);
      }
    });
  }

  async function submitFinalVote(photoDataUrl) {
    const posList = getPositionsList();
    const pendingIds = state.pendingRoleIds.length ? state.pendingRoleIds : posList.map((p) => p.id);
    state.isSubmitting = true;
    setLoading(el.castVoteBtn, true);
    if (el.faceGuardConfirmBtn) setLoading(el.faceGuardConfirmBtn, true);
    el.step3Error.hidden = true;

    try {
      closeFaceGuardModal();
      stopCamera();

      const selections = pendingIds.map((pid) => ({
        positionId: pid,
        candidate: state.selectedByRole[pid],
      }));

      await window.ElectionBackend.castVote({
        student: state.verifiedStudent,
        selections,
        photoDataUrl: photoDataUrl || generateBoothSnapshot("Auto Booth Snapshot"),
      });

      if (window.PendriveStorage) {
        await window.PendriveStorage.syncNow();
      }

      const summaryList = selections
        .map((sel) => {
          const pos = posList.find((p) => p.id === sel.positionId);
          return `${pos?.shortTitle || pos?.title || sel.positionId}: ${sel.candidate.fullName}`;
        })
        .join(" · ");
      el.successSummary.textContent = `${state.verifiedStudent.fullName} (ID ${state.verifiedStudent.admissionNo}) — Recorded ${selections.length} vote${selections.length > 1 ? "s" : ""}: ${summaryList} (${houseConfig.name} House).`;
      goToStep(4);
      startAutoResetCountdown();
    } catch (err) {
      el.step3ErrorMsg.textContent = err.message || "Could not record vote.";
      el.step3Error.hidden = false;
    } finally {
      state.isSubmitting = false;
      setLoading(el.castVoteBtn, false);
      if (el.faceGuardConfirmBtn) setLoading(el.faceGuardConfirmBtn, false);
    }
  }

  el.castVoteBtn.addEventListener("click", async () => {
    const posList = getPositionsList();
    const pendingIds = state.pendingRoleIds.length ? state.pendingRoleIds : posList.map((p) => p.id);
    const missingIds = pendingIds.filter((pid) => !state.selectedByRole[pid]);
    if (state.isSubmitting || !state.verifiedStudent || missingIds.length > 0) {
      if (missingIds.length > 0) {
        const missingNames = missingIds
          .map((pid) => posList.find((p) => p.id === pid)?.title || pid)
          .join(", ");
        el.step3ErrorMsg.textContent = `Please select a candidate for: ${missingNames}.`;
        el.step3Error.hidden = false;
      }
      return;
    }

    state.isSubmitting = true;
    setLoading(el.castVoteBtn, true);
    el.step3Error.hidden = true;

    try {
      if (!state.mediaStream) {
        await warmUpBackgroundCamera();
        await new Promise((r) => setTimeout(r, 300));
      }

      const faceResult = await detectHumanFace(el.cameraVideo, el.cameraCanvas);
      if (faceResult.ok) {
        await submitFinalVote(faceResult.photoDataUrl);
      } else {
        setLoading(el.castVoteBtn, false);
        state.isSubmitting = false;
        openFaceGuardModal(faceResult.reason, faceResult.obstructed);
      }
    } catch (err) {
      setLoading(el.castVoteBtn, false);
      state.isSubmitting = false;
      openFaceGuardModal("Camera error: " + (err.message || "Unable to access webcam."));
    }
  });

  el.resetNowBtn.addEventListener("click", resetBoothToStep1);

  // Tap House Title (e.g. "Hanuman House") to toggle Fullscreen mode on Tablets / Laptops
  const houseTitleBtn = document.getElementById("house-title-btn") || document.querySelector(".house-title");
  if (houseTitleBtn) {
    function toggleFullScreen() {
      const doc = document;
      const isFull = doc.fullscreenElement || doc.webkitFullscreenElement || doc.mozFullScreenElement || doc.msFullscreenElement;
      if (!isFull) {
        const root = doc.documentElement;
        if (root.requestFullscreen) {
          root.requestFullscreen().catch(() => {});
        } else if (root.webkitRequestFullscreen) {
          root.webkitRequestFullscreen();
        } else if (root.mozRequestFullScreen) {
          root.mozRequestFullScreen();
        } else if (root.msRequestFullscreen) {
          root.msRequestFullscreen();
        }
      } else {
        if (doc.exitFullscreen) {
          doc.exitFullscreen().catch(() => {});
        } else if (doc.webkitExitFullscreen) {
          doc.webkitExitFullscreen();
        } else if (doc.mozCancelFullScreen) {
          doc.mozCancelFullScreen();
        } else if (doc.msExitFullscreen) {
          doc.msExitFullscreen();
        }
      }
    }
    houseTitleBtn.addEventListener("click", toggleFullScreen);
    houseTitleBtn.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        toggleFullScreen();
      }
    });
  }

  async function boot() {
    loadPicoFaceClassifier();
    setInputMode(scannerState.mode || "scan");
    initWebHid();
    if (window.PendriveStorage) {
      await window.PendriveStorage.mount({
        container: document.getElementById("local-storage-slot"),
        houseMeta: houseConfig,
        getSnapshot: () => window.ElectionBackend.getHouseSnapshot(houseConfig.code),
      });
    }
    const mode = await window.ElectionBackend.init();
    const noteEl = document.getElementById("cloud-mode-note");
    if (noteEl) {
      noteEl.hidden = false;
      if (mode === "supabase") {
        noteEl.textContent = "Supabase connected — all votes & photos save strictly to Supabase.";
      } else {
        noteEl.textContent = "Supabase NOT connected — voting is blocked until Supabase is connected in Admin (Connect & Sync Supabase).";
      }
    }
    if (window.PendriveStorage) {
      window.ElectionBackend.subscribeHouseUpdates(houseConfig.code, () => {
        window.PendriveStorage.syncNow();
      });
      await window.PendriveStorage.syncNow();
    }
  }

  boot();
})();
"""

def main():
    dest_root = (ROOT / "Houses") if (ROOT / "Houses").exists() else ROOT
    all_booths = HOUSES + [CENTRAL_HOUSE]
    for house in all_booths:
        folder = dest_root / house["slug"]
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "index.html").write_text(build_index_html(house), encoding="utf-8")
        (folder / "styles.css").write_text(build_styles_css(house), encoding="utf-8")
        (folder / "data.js").write_text(build_data_js(house), encoding="utf-8")
        (folder / "supabase-config.js").write_text(SUPABASE_CONFIG_JS, encoding="utf-8")
        old_fb = folder / "firebase-config.js"
        if old_fb.exists():
            old_fb.unlink()
        (folder / "app.js").write_text(APP_JS, encoding="utf-8")
        scanner_gun_src = ROOT / "Houses" / "assets" / "scanner-gun.png"
        if scanner_gun_src.exists():
            (folder / "scanner-gun.png").write_bytes(scanner_gun_src.read_bytes())
        pico_src = ROOT / "Houses" / "assets" / "pico.js"
        if pico_src.exists():
            (folder / "pico.js").write_bytes(pico_src.read_bytes())
        facefinder_src = ROOT / "Houses" / "assets" / "facefinder"
        if facefinder_src.exists():
            (folder / "facefinder").write_bytes(facefinder_src.read_bytes())
    admin_folder = dest_root / "admin"
    admin_folder.mkdir(parents=True, exist_ok=True)
    (admin_folder / "data.js").write_text(
        build_admin_data_js(STUDENTS, CANDIDATES), encoding="utf-8"
    )
    docs_folder = (ROOT / "1docs") if (ROOT / "1docs").exists() else (ROOT / "docs")
    docs_folder.mkdir(parents=True, exist_ok=True)
    (docs_folder / "UNASSIGNED_HOUSE_STUDENTS.md").write_text(
        build_unassigned_markdown(BLANK_HOUSE_STUDENTS), encoding="utf-8"
    )
    print(f"Updated {len(all_booths)} polling booths ({len(STUDENTS)} students, {len(CANDIDATES)} candidates) + admin/data.js in {dest_root.name}.")

if __name__ == "__main__":
    main()
