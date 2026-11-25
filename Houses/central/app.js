// House Booth 5-Step Kiosk Controller (Warm Cream + Automatic Photo Capture)
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
    mode: "manual",
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

    loadingOverlay: document.getElementById("loading-overlay"),
    loadingOverlayTitle: document.getElementById("loading-overlay-title"),
    loadingOverlaySubtitle: document.getElementById("loading-overlay-subtitle"),

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

  let delayedSpinnerTimer = null;

  function startDelayedSpinner(title = "Saving Ballot...", subtitle = "Please wait a moment...", delayMs = 350) {
    clearTimeout(delayedSpinnerTimer);
    delayedSpinnerTimer = setTimeout(() => {
      if (el.loadingOverlayTitle) el.loadingOverlayTitle.textContent = title;
      if (el.loadingOverlaySubtitle) el.loadingOverlaySubtitle.textContent = subtitle;
      if (el.loadingOverlay) el.loadingOverlay.hidden = false;
    }, delayMs);
  }

  function stopDelayedSpinner() {
    clearTimeout(delayedSpinnerTimer);
    delayedSpinnerTimer = null;
    if (el.loadingOverlay) el.loadingOverlay.hidden = true;
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
    if (mean < 7.0) {
      return { ok: false, obstructed: true, reason: "Camera is completely covered or too dark. Please remove your hand from the lens." };
    }
    // Palm / hand pressed flat against the lens:
    if (stdDev < 3.5) {
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
        minsize: 24,
        maxsize: 260,
        scalefactor: 1.1,
      };
      let dets = pico.run_cascade(image, classifier, params);
      dets = pico.cluster_detections(dets, 0.2);
      const validFaces = dets.filter((d) => d[3] > 18.0);
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
        const photoHtml = cand.photoPath || cand.photoUrl
          ? `<img src="${cand.photoPath || cand.photoUrl}" alt="${cand.fullName}" style="width:100%;height:100%;object-fit:cover;border-radius:10px;" />`
          : `<span>${getInitials(cand.fullName)}</span>`;
        const sym = cand.symbolObj || { name: "Candidate Choice", icon: "⭐" };
        const symSlug = (sym.slug || sym.name || "star").toLowerCase().replace(/[\s-]+/g, "_");
        const symImg = (sym.image || sym.imagePath || `../assets/symbols/${symSlug}.png`) + '?v=20261123N';
        card.innerHTML = `
          <div class="candidate-card-top">
            <div style="display:flex;align-items:center;gap:10px;">
              <div class="candidate-avatar" aria-hidden="true" style="overflow:hidden;">${photoHtml}</div>
              <div class="candidate-symbol-box" title="Symbol: ${sym.name}" style="width:52px;height:52px;border-radius:10px;background:#fff;border:1px solid #cbd5e1;display:grid;place-items:center;padding:4px;box-sizing:border-box;">
                <img src="${symImg}" alt="${sym.name}" style="width:38px;height:38px;object-fit:contain;" onerror="this.style.display='none';this.nextElementSibling.style.display='inline-block';" />
                <span style="display:none;font-size:1.5rem;">${sym.icon || "⭐"}</span>
              </div>
            </div>
            <span class="select-indicator" aria-hidden="true"></span>
          </div>
          <div>
            <h4 class="candidate-name"></h4>
            <p class="candidate-meta"></p>
          </div>
        `;
        card.querySelector(".candidate-name").textContent = cand.fullName;
        card.querySelector(".candidate-meta").textContent = String(cand.admissionNo || "").startsWith("DEMO-")
          ? `${cand.section} · ${pos.subtitle || pos.title}`
          : `ID ${cand.admissionNo} · Class ${cand.className}-${cand.section} · ${pos.title}`;

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
    clearTimeout(delayedSpinnerTimer);
    stopDelayedSpinner();
    clearInterval(state.resetInterval);
    clearTimeout(state.resetTimeout);

    // ── 10-Vote Auto Cache Buster (Stays on this House kiosk with spinning wheel) ──
    const totalVotes = parseInt(sessionStorage.getItem("kiosk_session_votes") || "0", 10);
    const lastBust = parseInt(sessionStorage.getItem("kiosk_last_cache_bust") || "0", 10);
    if (totalVotes > 0 && totalVotes % 10 === 0 && totalVotes !== lastBust) {
      sessionStorage.setItem("kiosk_last_cache_bust", String(totalVotes));
      if (el.loadingOverlayTitle) el.loadingOverlayTitle.textContent = "Refreshing Booth Cache...";
      if (el.loadingOverlaySubtitle) el.loadingOverlaySubtitle.textContent = `${totalVotes} votes recorded · Optimizing booth for next voter...`;
      if (el.loadingOverlay) el.loadingOverlay.hidden = false;
      setTimeout(() => {
        window.location.replace(window.location.pathname + "?v=" + Date.now());
      }, 700);
      return;
    }
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
    setInputMode(scannerState.mode || "manual");
    triggerAutoFocus();
  }

  function ensureInputFocused() {
    if (state.step !== 1) return;
    const input = scannerState.mode === "scan" && el.scannerStreamInput
      ? el.scannerStreamInput
      : el.admissionInput;
    if (!input) return;
    try {
      input.focus({ preventScroll: true });
    } catch (_) {
      try { input.focus(); } catch (_) {}
    }
  }

  function triggerAutoFocus() {
    ensureInputFocused();
    [25, 80, 200, 450, 800].forEach((ms) => setTimeout(ensureInputFocused, ms));
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
    triggerAutoFocus();
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
    startDelayedSpinner("Verifying Voter...", "Please wait a moment...", 800);

    try {
      // Wait for boot() to finish (Supabase init) before verifying
      if (window._electionBootReady) {
        try { await window._electionBootReady; } catch (e) { /* continue anyway */ }
      }
      if (!window.ElectionBackend || typeof window.ElectionBackend.init !== "function") {
        showStep1Error("System Error", "Kiosk backend failed to load. Please refresh the page.");
        stopDelayedSpinner();
        if (el.verifyBtn) el.verifyBtn.disabled = false;
        return;
      }
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
      const isTeacher = result.student.isStaff === true && result.student.className !== "10" && result.student.className !== "9" && result.student.className !== "8" && result.student.className !== "7" && result.student.admissionNo !== "1C8492" && result.student.admissionNo !== "0000";
      const isWinner = Boolean(result.student.isElectedWinner);
      const isCabinetContestant = Boolean(result.student.isCabinetContestant);
      el.voterMeta.textContent = isWinner
        ? `🎖️ ${result.student.winnerRoleTitle || "Elected House Captain"} · ${result.student.winnerHouseName || "House Council"}`
        : isTeacher
        ? `${result.student.subject ? `${result.student.subject} Faculty` : "Teaching Staff"} · ${houseConfig.name}`
        : `Class ${result.student.className}-${result.student.section} · ${houseConfig.name} House`;
      el.voterRoleTag.textContent = isCabinetContestant
        ? "🎖️ Authorized Voter (School Cabinet Contestant)"
        : isWinner
        ? "Authorized Electoral College Voter (1 of 24 House Leaders)"
        : isTeacher
        ? "Authorized Teacher / Faculty"
        : result.student.isCandidate
        ? `Candidate · ${result.student.positionName || "House Leadership"}`
        : result.verificationNote || "Eligible Voter";
      if (isWinner || isCabinetContestant) {
        el.voterRoleTag.style.background = "#dcfce7";
        el.voterRoleTag.style.color = "#15803d";
        el.voterRoleTag.style.border = "1px solid #86efac";
        el.voterRoleTag.style.fontWeight = "800";
      }
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
      stopDelayedSpinner();
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

  // Channel 2: Tap/Click anywhere on Step 1 restores scanner/input focus
  document.addEventListener("click", (e) => {
    if (state.step === 1) {
      const isInteractive = e.target.closest("button, a, input, select, textarea, [role='button'], video");
      if (!isInteractive) {
        triggerAutoFocus();
      }
    }
  });
  window.addEventListener("focus", () => {
    if (state.step === 1) triggerAutoFocus();
  });
  document.addEventListener("visibilitychange", () => {
    if (!document.hidden && state.step === 1) triggerAutoFocus();
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

  if (el.admissionForm) {
    el.admissionForm.addEventListener("submit", (e) => {
      e.preventDefault();
      executeVerification(el.admissionInput ? el.admissionInput.value : "");
    });
  }
  if (el.verifyBtn) {
    el.verifyBtn.addEventListener("click", (e) => {
      e.preventDefault();
      executeVerification(el.admissionInput ? el.admissionInput.value : "");
    });
  }

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

    let noCamFallbackTimer = null;

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

    if (noCamFallbackTimer) clearTimeout(noCamFallbackTimer);
    if (!state.mediaStream) {
      updateFaceGuardUI("Webcam unavailable — voter snapshot will be recorded.", false, false);
      noCamFallbackTimer = setTimeout(() => {
        if (el.faceGuardConfirmBtn && !state.isSubmitting) {
          el.faceGuardConfirmBtn.disabled = false;
          updateFaceGuardUI("Press Confirm to cast vote with station record.", false, true);
        }
      }, 1500);
    }

    clearInterval(faceCheckInterval);
    faceCheckInterval = setInterval(async () => {
      if (state.isSubmitting) return;
      if (!state.mediaStream) return;
      const res = await detectHumanFace(el.faceLiveVideo || el.cameraVideo, el.cameraCanvas);
      if (res.ok) {
        steadyFaceCount++;
        lastVerifiedPhoto = res.photoDataUrl;
        updateFaceGuardUI("✓ Face Verified! Casting vote...", false, true);
        if (el.faceGuardConfirmBtn) el.faceGuardConfirmBtn.disabled = false;
        if (steadyFaceCount >= 1 && !state.isSubmitting) {
          clearInterval(faceCheckInterval);
          if (noCamFallbackTimer) clearTimeout(noCamFallbackTimer);
          setTimeout(async () => {
            if (!state.isSubmitting) {
              await submitFinalVote(lastVerifiedPhoto);
            }
          }, 280);
        }
      } else {
        updateFaceGuardUI(res.reason, res.obstructed, false);
      }
    }, 200);
  }

  function closeFaceGuardModal() {
    clearInterval(faceCheckInterval);
    faceCheckInterval = null;
    if (noCamFallbackTimer) {
      clearTimeout(noCamFallbackTimer);
      noCamFallbackTimer = null;
    }
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
      if (!state.isSubmitting) {
        clearInterval(faceCheckInterval);
        if (noCamFallbackTimer) clearTimeout(noCamFallbackTimer);
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
    startDelayedSpinner("Saving Ballot...", "Please wait a moment...", 350);

    try {
      closeFaceGuardModal();
      stopCamera();

      const selections = pendingIds.map((pid) => ({
        positionId: pid,
        candidate: state.selectedByRole[pid],
      }));

      const stationBooth = (typeof window.getRegisteredBooth === "function" && window.getRegisteredBooth()) || (typeof sessionStorage !== "undefined" && sessionStorage.getItem("election_booth_name")) || (typeof localStorage !== "undefined" && localStorage.getItem("last_registered_booth")) || "Booth 1";
      await window.ElectionBackend.castVote({
        student: state.verifiedStudent,
        selections,
        photoDataUrl: photoDataUrl || generateBoothSnapshot("Auto Booth Snapshot"),
        boothName: stationBooth,
      });

      if (window.PendriveStorage) {
        window.PendriveStorage.syncNow().catch(() => {});
      }

      const summaryList = selections
        .map((sel) => {
          const pos = posList.find((p) => p.id === sel.positionId);
          return `${pos?.shortTitle || pos?.title || sel.positionId}: ${sel.candidate.fullName}`;
        })
        .join(" · ");
      el.successSummary.textContent = `${state.verifiedStudent.fullName} (ID ${state.verifiedStudent.admissionNo}) — Recorded ${selections.length} vote${selections.length > 1 ? "s" : ""}: ${summaryList} (${houseConfig.name} House).`;
            const prevVotes = parseInt(sessionStorage.getItem("kiosk_session_votes") || "0", 10);
      sessionStorage.setItem("kiosk_session_votes", String(prevVotes + 1));
      goToStep(4);
      startAutoResetCountdown();
    } catch (err) {
      el.step3ErrorMsg.textContent = err.message || "Could not record vote.";
      el.step3Error.hidden = false;
    } finally {
      stopDelayedSpinner();
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

    state.isSubmitting = false;
    setLoading(el.castVoteBtn, false);
    el.step3Error.hidden = true;

    try {
      if (!state.mediaStream) {
        await warmUpBackgroundCamera();
        await new Promise((r) => setTimeout(r, 250));
      }
      openFaceGuardModal("Please look at the camera to verify voter identity.");
    } catch (err) {
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
    setInputMode(scannerState.mode || "manual");
    triggerAutoFocus();
    initWebHid();
    if (window.PendriveStorage) {
      window.PendriveStorage.mount({
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
      window.PendriveStorage.syncNow().catch(() => {});
    }

    try {
      const urlParams = new URLSearchParams(window.location.search);
      const qAdm = urlParams.get("admissionNo") || urlParams.get("voterId");
      if (qAdm && qAdm.trim()) {
        window.history.replaceState({}, document.title, window.location.pathname);
        if (el.admissionInput) el.admissionInput.value = qAdm.trim();
        setTimeout(() => {
          executeVerification(qAdm.trim());
        }, 120);
      }
    } catch (_) {}
  }


  // Store boot promise so executeVerification can await it
  window._electionBootReady = boot();
})();
