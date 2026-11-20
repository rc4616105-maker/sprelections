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
    evmPostIndex: 0,
    cachedCandidates: [],
    mediaStream: null,
    resetInterval: null,
    resetTimeout: null,
    isSubmitting: false,
  };

  const scannerState = {
    mode: localStorage.getItem("election_voter_input_mode") || "manual",
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

    mainStepper: document.getElementById("main-stepper"),
    evmPostStepper: document.getElementById("evm-post-stepper"),
    evmIndicators: Array.from(document.querySelectorAll("[data-evm-indicator]")),
    evmBallotView: document.getElementById("evm-ballot-view"),
    evmReviewView: document.getElementById("evm-review-view"),
    evmPostBadge: document.getElementById("evm-post-badge"),
    evmPostTitle: document.getElementById("evm-post-title"),
    evmPostSubtitle: document.getElementById("evm-post-subtitle"),
    evmCandidateList: document.getElementById("evm-candidate-list"),
    evmBackBtn: document.getElementById("evm-back-btn"),
    evmSelectionStatus: document.getElementById("evm-selection-status"),
    evmNextBtn: document.getElementById("evm-next-btn"),
    evmReviewGrid: document.getElementById("evm-review-grid"),
    evmReviewBackBtn: document.getElementById("evm-review-back-btn"),
    evmFinalCastBtn: document.getElementById("evm-final-cast-btn"),

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

    const pageShell = document.querySelector(".page-shell");
    if (pageShell) {
      pageShell.classList.toggle("evm-active", stepNum === 3);
    }
    if (el.mainStepper) el.mainStepper.hidden = (stepNum === 3);
    if (el.evmPostStepper) el.evmPostStepper.hidden = (stepNum !== 3);
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
      await el.cameraVideo.play().catch(() => { });
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
      } catch (_) { }
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

    if (el.castActionBar) el.castActionBar.hidden = false;
    if (el.selectedProgressLabel) {
      el.selectedProgressLabel.textContent = `Selected Candidates (${pickedCount} / ${totalNeeded})`;
    }
    if (el.selectedCandidateName) {
      el.selectedCandidateName.textContent =
        pickedCount > 0 ? pickedPairs.join(" · ") : "Choose 1 candidate for each open role above";
    }
    if (el.castVoteBtn) {
      el.castVoteBtn.disabled = pickedCount < totalNeeded || totalNeeded === 0;
    }
  }

  const ELECTION_SYMBOLS = [
    { name: "Torch", icon: "🔦" },
    { name: "Book", icon: "📖" },
    { name: "Rising Sun", icon: "🌅" },
    { name: "Star", icon: "⭐" },
    { name: "Shield", icon: "🛡️" },
    { name: "Rocket", icon: "🚀" }
  ];

  function updateEvmStepper() {
    if (!el.evmIndicators || !el.evmIndicators.length) return;
    const posList = getPositionsList();
    el.evmIndicators.forEach((pill, idx) => {
      const isActive = idx === state.evmPostIndex;
      let isDone = false;
      if (idx < posList.length) {
        const pos = posList[idx];
        isDone = Boolean(state.selectedByRole[pos.id] || state.votedRoles[pos.id]);
      } else {
        isDone = posList.every((p) => Boolean(state.selectedByRole[p.id] || state.votedRoles[p.id]));
      }
      pill.classList.toggle("is-active", isActive);
      pill.classList.toggle("is-done", isDone && !isActive);
    });
  }

  function renderEvmView() {
    const posList = getPositionsList();
    updateEvmStepper();

    if (state.evmPostIndex < posList.length) {
      // Ballot View for single post
      if (el.evmBallotView) el.evmBallotView.hidden = false;
      if (el.evmReviewView) el.evmReviewView.hidden = true;

      const currentPos = posList[state.evmPostIndex];
      const votedBallot = state.votedRoles[currentPos.id] || null;
      const roleCands = state.cachedCandidates.filter((c) => (c.positionId || currentPos.id) === currentPos.id);

      if (el.evmPostBadge) el.evmPostBadge.textContent = `POST ${state.evmPostIndex + 1} OF ${posList.length}`;
      if (el.evmPostTitle) el.evmPostTitle.textContent = currentPos.title;
      if (el.evmPostSubtitle) el.evmPostSubtitle.textContent = currentPos.subtitle || "";

      if (el.evmCandidateList) {
        el.evmCandidateList.innerHTML = "";
        const pickedCand = state.selectedByRole[currentPos.id] || (votedBallot ? { id: votedBallot.candidateId, fullName: votedBallot.candidateName } : null);

        roleCands.forEach((cand, candIdx) => {
          const sym = cand.symbolObj || ELECTION_SYMBOLS[candIdx % ELECTION_SYMBOLS.length];
          const isPicked = pickedCand && pickedCand.id === cand.id;
          const serialFormatted = String(candIdx + 1).padStart(2, "0");

          const row = document.createElement("div");
          row.className = `evm-candidate-row${isPicked ? " is-selected" : ""}`;
          row.setAttribute("role", "radio");
          row.setAttribute("aria-checked", isPicked ? "true" : "false");
          row.dataset.candidateId = cand.id;

          const photoHtml = cand.photoPath || cand.photoUrl
            ? `<img src="${cand.photoPath || cand.photoUrl}" alt="${cand.fullName}" />`
            : `<span>${getInitials(cand.fullName)}</span>`;

          const subText = String(cand.admissionNo || "").startsWith("DEMO-")
            ? cand.section
            : (cand.className ? `Class ${cand.className} ${cand.section || ""}` : (cand.section || ""));

          row.innerHTML = `
            <span class="evm-cand-num">${serialFormatted}</span>
            <div class="evm-cand-avatar">${photoHtml}</div>
            <div class="evm-cand-info">
              <h3 class="evm-cand-name">${cand.fullName}</h3>
              <span class="evm-cand-sub">${subText}</span>
            </div>
            <div class="evm-right-cluster">
              <div class="evm-symbol-badge" title="Election Symbol: ${sym.name}">
                <span class="evm-symbol-icon">${sym.icon}</span>
                <span class="evm-symbol-name">${sym.name}</span>
              </div>
              <span class="evm-led-lamp"></span>
              <button type="button" class="evm-vote-btn" tabindex="-1">
                ${isPicked ? (votedBallot ? "RECORDED ✓" : "VOTED ✓") : "VOTE"}
              </button>
            </div>
          `;

          if (votedBallot) {
            row.style.pointerEvents = "none";
          } else {
            row.addEventListener("click", () => {
              state.selectedByRole[currentPos.id] = cand;
              updateCastBar();
              renderEvmView();
            });
          }

          el.evmCandidateList.appendChild(row);
        });
      }

      // Update Footer
      if (el.evmBackBtn) {
        if (state.evmPostIndex === 0) {
          el.evmBackBtn.innerHTML = `← Back: Verify Info`;
        } else {
          const prevPos = posList[state.evmPostIndex - 1];
          el.evmBackBtn.innerHTML = `← Back: ${prevPos.shortTitle || prevPos.title}`;
        }
      }

      const pickedCand = state.selectedByRole[currentPos.id] || (votedBallot ? { id: votedBallot.candidateId, fullName: votedBallot.candidateName } : null);
      if (el.evmSelectionStatus) {
        if (pickedCand) {
          el.evmSelectionStatus.innerHTML = `<span style="color:#16a34a; font-weight:800;">✓ Selected: ${pickedCand.fullName}</span>`;
        } else {
          el.evmSelectionStatus.innerHTML = `<span style="color:var(--text-muted);">Please tap a candidate or press blue VOTE button</span>`;
        }
      }

      if (el.evmNextBtn) {
        el.evmNextBtn.disabled = !pickedCand;
        const nextPos = posList[state.evmPostIndex + 1];
        if (nextPos) {
          el.evmNextBtn.innerHTML = `Next: ${nextPos.shortTitle || nextPos.title} →`;
        } else {
          el.evmNextBtn.innerHTML = `Next: Review &amp; Cast →`;
        }
      }

    } else {
      // Review & Cast View (state.evmPostIndex === posList.length)
      if (el.evmBallotView) el.evmBallotView.hidden = true;
      if (el.evmReviewView) el.evmReviewView.hidden = false;

      if (el.evmReviewGrid) {
        el.evmReviewGrid.innerHTML = "";
        posList.forEach((pos, idx) => {
          const picked = state.selectedByRole[pos.id] || (state.votedRoles[pos.id] ? { id: state.votedRoles[pos.id].candidateId, fullName: state.votedRoles[pos.id].candidateName } : null);
          const card = document.createElement("div");
          card.className = "evm-review-card";

          const photoHtml = picked && (picked.photoPath || picked.photoUrl)
            ? `<img src="${picked.photoPath || picked.photoUrl}" alt="${picked.fullName}" />`
            : `<span>${getInitials(picked ? picked.fullName : "?")}</span>`;

          const subText = picked
            ? (String(picked.admissionNo || "").startsWith("DEMO-") ? picked.section : (picked.className ? `Class ${picked.className} ${picked.section || ""}` : (picked.section || "")))
            : "No candidate chosen";

          card.innerHTML = `
            <div class="evm-review-card-left">
              <div class="evm-cand-avatar">${photoHtml}</div>
              <div>
                <p class="evm-review-role-title">${pos.title}</p>
                <h4 class="evm-review-cand-name" style="${!picked ? 'color:#dc2626;' : ''}">${picked ? picked.fullName : 'Not Selected'}</h4>
                <p class="evm-review-cand-sub">${subText}</p>
              </div>
            </div>
            <button type="button" class="evm-review-change-btn" data-change-idx="${idx}">
              Change
            </button>
          `;

          const changeBtn = card.querySelector(".evm-review-change-btn");
          if (changeBtn) {
            changeBtn.addEventListener("click", () => {
              state.evmPostIndex = idx;
              renderEvmView();
            });
          }

          el.evmReviewGrid.appendChild(card);
        });
      }

      const allChosen = posList.every((p) => Boolean(state.selectedByRole[p.id] || state.votedRoles[p.id]));
      if (el.evmFinalCastBtn) el.evmFinalCastBtn.disabled = !allChosen;
    }
  }

  async function renderCandidatesStep() {
    state.cachedCandidates = await window.ElectionBackend.getHouseCandidates(houseConfig.code);
    const posList = getPositionsList();
    if (!state.pendingRoleIds.length) {
      state.pendingRoleIds = posList.filter((p) => !state.votedRoles[p.id]).map((p) => p.id);
    }
    state.selectedByRole = {};
    state.evmPostIndex = 0;
    el.step3Error.hidden = true;
    updateCastBar();
    renderEvmView();
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
    closeFaceGuardModal();
    stopCamera();
    state.verifiedStudent = null;
    state.pendingRoleIds = [];
    state.votedRoles = {};
    state.cancelledRoleIds = [];
    state.selectedByRole = {};
    state.evmPostIndex = 0;
    state.cachedCandidates = [];
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
      try { input.focus(); } catch (_) { }
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
    } catch (_) { }
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
      } catch (_) { }
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
    startDelayedSpinner("Verifying Voter...", "Please wait a moment...", 400);

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
      const isTeacher = result.student.isStaff === true || result.student.houseCode === "ALL" || result.student.admissionNo === "0000";
      el.voterMeta.textContent = isTeacher
        ? `${result.student.subject ? `${result.student.subject} Faculty` : "Teaching Staff"} · ${houseConfig.name}`
        : `Class ${result.student.className}-${result.student.section} · ${houseConfig.name} House`;
      el.voterRoleTag.textContent = isTeacher
        ? "Authorized Teacher / Faculty"
        : result.student.isCandidate
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

  let noCamFallbackTimer = null;

  function openFaceGuardModal(initialReason, isObstructed) {
    if (!el.faceGuardModal) return;
    el.faceGuardModal.hidden = false;
    updateFaceGuardUI(initialReason || "Please look directly at the camera.", isObstructed, false);

    if (el.faceLiveVideo && state.mediaStream) {
      el.faceLiveVideo.srcObject = state.mediaStream;
      el.faceLiveVideo.play().catch(() => { });
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
        updateFaceGuardUI("✓ Face Detected! Hold still...", false, true);
        if (el.faceGuardConfirmBtn) el.faceGuardConfirmBtn.disabled = false;
        if (steadyFaceCount >= 2 && !state.isSubmitting) {
          clearInterval(faceCheckInterval);
          if (noCamFallbackTimer) clearTimeout(noCamFallbackTimer);
          await submitFinalVote(lastVerifiedPhoto);
        }
      } else {
        steadyFaceCount = 0;
        updateFaceGuardUI(res.reason, res.obstructed, false);
        if (el.faceGuardConfirmBtn) el.faceGuardConfirmBtn.disabled = true;
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

  if (el.evmIndicators) {
    el.evmIndicators.forEach((pill, idx) => {
      pill.style.cursor = "pointer";
      pill.addEventListener("click", () => {
        const posList = getPositionsList();
        if (idx < posList.length) {
          state.evmPostIndex = idx;
          renderEvmView();
        } else if (idx === posList.length) {
          state.evmPostIndex = posList.length;
          renderEvmView();
        }
      });
    });
  }

  if (el.evmBackBtn) {
    el.evmBackBtn.addEventListener("click", () => {
      if (state.evmPostIndex > 0) {
        state.evmPostIndex--;
        renderEvmView();
      } else {
        goToStep(2);
      }
    });
  }

  if (el.evmNextBtn) {
    el.evmNextBtn.addEventListener("click", () => {
      const posList = getPositionsList();
      if (state.evmPostIndex < posList.length) {
        state.evmPostIndex++;
        renderEvmView();
      }
    });
  }

  if (el.evmReviewBackBtn) {
    el.evmReviewBackBtn.addEventListener("click", () => {
      const posList = getPositionsList();
      state.evmPostIndex = Math.max(0, posList.length - 1);
      renderEvmView();
    });
  }

  if (el.evmFinalCastBtn) {
    el.evmFinalCastBtn.addEventListener("click", () => {
      if (el.castVoteBtn) {
        el.castVoteBtn.click();
      }
    });
  }

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
          root.requestFullscreen().catch(() => { });
        } else if (root.webkitRequestFullscreen) {
          root.webkitRequestFullscreen();
        } else if (root.mozRequestFullScreen) {
          root.mozRequestFullScreen();
        } else if (root.msRequestFullscreen) {
          root.msRequestFullscreen();
        }
      } else {
        if (doc.exitFullscreen) {
          doc.exitFullscreen().catch(() => { });
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
