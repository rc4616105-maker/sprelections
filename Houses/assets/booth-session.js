// Polling Booth Session Management
// Persists the registered booth & presiding officer per browser tab (sessionStorage).
// When the tab is closed and reopened, it asks again.
// While the tab stays open across voting navigation, it remembers the booth and officer.
(function () {
  const SESSION_KEY = "election_booth_name";
  const LOCAL_KEY = "last_registered_booth";
  const SESSION_OFFICER_KEY = "election_officer_name";
  const LOCAL_OFFICER_KEY = "last_registered_officer";

  function getRegisteredBooth() {
    try {
      const b = sessionStorage.getItem(SESSION_KEY);
      return b && b.trim() ? b.trim() : "";
    } catch (_) {
      return "";
    }
  }

  function setRegisteredBooth(name) {
    const clean = String(name || "").trim() || "Booth 1";
    try {
      sessionStorage.setItem(SESSION_KEY, clean);
    } catch (_) {}
    try {
      localStorage.setItem(LOCAL_KEY, clean);
    } catch (_) {}
    return clean;
  }

  function getLastKnownBooth() {
    try {
      const b = localStorage.getItem(LOCAL_KEY);
      return b && b.trim() ? b.trim() : "Booth 1";
    } catch (_) {
      return "Booth 1";
    }
  }

  function getRegisteredOfficer() {
    try {
      const o = sessionStorage.getItem(SESSION_OFFICER_KEY);
      return o && o.trim() ? o.trim() : "";
    } catch (_) {
      return "";
    }
  }

  function setRegisteredOfficer(name) {
    const clean = String(name || "").trim();
    try {
      sessionStorage.setItem(SESSION_OFFICER_KEY, clean);
    } catch (_) {}
    try {
      localStorage.setItem(LOCAL_OFFICER_KEY, clean);
    } catch (_) {}
    return clean;
  }

  function getLastKnownOfficer() {
    try {
      const o = localStorage.getItem(LOCAL_OFFICER_KEY);
      return o && o.trim() ? o.trim() : "";
    } catch (_) {
      return "";
    }
  }

  window.getRegisteredBooth = getRegisteredBooth;
  window.setRegisteredBooth = setRegisteredBooth;
  window.getLastKnownBooth = getLastKnownBooth;
  window.getRegisteredOfficer = getRegisteredOfficer;
  window.setRegisteredOfficer = setRegisteredOfficer;
  window.getLastKnownOfficer = getLastKnownOfficer;

  // -------------------------------------------------------------
  // Universal Kiosk House Polling Pause & Tally Guard
  // -------------------------------------------------------------
  function isHouseBoothPage() {
    const p = (window.location.pathname || "").toLowerCase();
    const houseList = ["bheeshma", "gurudrona", "hanuman", "karna", "vasistha", "vishwamithra"];
    return houseList.some(function (h) { return p.includes("/" + h + "/"); });
  }

  function ensurePauseStyles() {
    if (document.getElementById("booth-pause-styles")) return;
    const style = document.createElement("style");
    style.id = "booth-pause-styles";
    style.textContent = `
      .booth-card {
        position: relative !important;
      }
      .booth-paused-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(254, 252, 248, 0.97);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        z-index: 999999;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2rem 1.5rem;
        border-radius: 24px;
        box-shadow: inset 0 0 40px rgba(217, 119, 6, 0.08);
        animation: boothPauseFadeIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      }
      @keyframes boothPauseFadeIn {
        from { opacity: 0; transform: scale(0.98); }
        to { opacity: 1; transform: scale(1); }
      }
      .booth-paused-card {
        max-width: 520px;
        width: 100%;
        background: #ffffff;
        border: 2px solid #f59e0b;
        box-shadow: 0 25px 50px -12px rgba(217, 119, 6, 0.25), 0 0 0 1px rgba(245, 158, 11, 0.15);
        border-radius: 20px;
        padding: 2.25rem 2rem;
        text-align: center;
        box-sizing: border-box;
      }
      .paused-icon-ring {
        width: 76px;
        height: 76px;
        margin: 0 auto 1.25rem;
        background: linear-gradient(135deg, #fef3c7, #fde68a);
        border: 2px solid #f59e0b;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
        box-shadow: 0 10px 25px -5px rgba(245, 158, 11, 0.35);
      }
      .paused-badge {
        display: inline-block;
        padding: 0.35rem 0.9rem;
        background: #fef3c7;
        color: #b45309;
        font-size: 0.75rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        border-radius: 999px;
        margin-bottom: 0.85rem;
        border: 1px solid #fde68a;
      }
      .paused-title {
        font-size: 1.65rem;
        font-weight: 800;
        color: #1e293b;
        margin: 0 0 0.75rem;
        line-height: 1.25;
      }
      .paused-subtitle {
        font-size: 0.96rem;
        color: #475569;
        line-height: 1.55;
        margin: 0 0 1.25rem;
      }
      .paused-status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.65rem 1.25rem;
        background: #fee2e2;
        color: #991b1b;
        font-weight: 700;
        font-size: 0.88rem;
        border-radius: 12px;
        border: 1px solid #fca5a5;
        margin-bottom: 1.25rem;
      }
      .paused-footer-note {
        font-size: 0.82rem;
        color: #64748b;
        border-top: 1px solid #f1f5f9;
        padding-top: 1rem;
        margin-top: 0.5rem;
        line-height: 1.45;
      }
    `;
    document.head.appendChild(style);
  }

  function applyKioskPauseGuard() {
    if (!isHouseBoothPage()) return;
    let isClosed = false;
    try {
      isClosed = localStorage.getItem("ELECTION_HOUSE_POLLING_CLOSED") === "true";
    } catch (_) {}

    const boothCard = document.querySelector(".booth-card") || document.querySelector("main") || document.body;
    if (!boothCard) return;

    if (isClosed) {
      ensurePauseStyles();
      let overlay = document.getElementById("booth-paused-screen");
      if (!overlay) {
        overlay = document.createElement("div");
        overlay.id = "booth-paused-screen";
        overlay.className = "booth-paused-overlay";
        overlay.setAttribute("role", "alertdialog");
        overlay.setAttribute("aria-live", "assertive");
        overlay.innerHTML = `
          <div class="booth-paused-card">
            <div class="paused-icon-ring" aria-hidden="true">⏸️</div>
            <span class="paused-badge">Election Commission · Official Notice</span>
            <h2 class="paused-title">House Elections Paused</h2>
            <p class="paused-subtitle">
              Voting in all 6 House Polling Booths has been <strong>PAUSED / CONCLUDED</strong>.
              The Election Commission is tallying ballots to declare the 24 House Captains &amp; Vice Captains.
            </p>
            <div class="paused-status-badge">
              <span>🔒 Kiosk Status: Polling Closed · No Votes Allowed</span>
            </div>
            <div class="paused-footer-note">
              This screen will automatically unlock if the Election Presiding Officer / Administrator resumes house polling from the Admin Dashboard.
            </div>
          </div>
        `;
        boothCard.appendChild(overlay);
      }

      // Reset any active student verification / form state
      const step1 = document.getElementById("step-1");
      const step2 = document.getElementById("step-2");
      const step3 = document.getElementById("step-3");
      const step4 = document.getElementById("step-4");
      const stepper = document.getElementById("main-stepper");
      const admissionInput = document.getElementById("admission-no");
      const scannerStreamInput = document.getElementById("barcode-scanner-stream");

      if (step1 && !step1.classList.contains("is-visible")) {
        [step2, step3, step4].forEach(function (s) { if (s) s.classList.remove("is-visible"); });
        step1.classList.add("is-visible");
      }
      if (admissionInput) {
        admissionInput.value = "";
        admissionInput.blur();
      }
      if (scannerStreamInput) {
        scannerStreamInput.value = "";
        scannerStreamInput.blur();
      }
      if (stepper) {
        stepper.querySelectorAll(".step-pill").forEach(function (pill, idx) {
          pill.classList.remove("is-done", "is-active");
          if (idx === 0) pill.classList.add("is-active");
        });
      }
    } else {
      const overlay = document.getElementById("booth-paused-screen");
      if (overlay) {
        overlay.remove();
      }
    }
  }

  window.isHousePollingClosed = function () {
    try {
      return localStorage.getItem("ELECTION_HOUSE_POLLING_CLOSED") === "true";
    } catch (_) {
      return false;
    }
  };

  if (typeof BroadcastChannel !== "undefined") {
    try {
      const syncChannel = new BroadcastChannel("election_spr_2026_sync");
      syncChannel.onmessage = function (ev) {
        if (ev && ev.data && (ev.data.type === "house_polling_closed" || ev.data.type === "house_polling_opened")) {
          applyKioskPauseGuard();
        }
      };
    } catch (_) {}
  }

  window.addEventListener("storage", function (e) {
    if (e.key === "ELECTION_HOUSE_POLLING_CLOSED") {
      applyKioskPauseGuard();
    }
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", applyKioskPauseGuard);
  } else {
    applyKioskPauseGuard();
  }

  setInterval(applyKioskPauseGuard, 1000);
})();
