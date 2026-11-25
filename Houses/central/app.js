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
    currentPostIdx: 0,
    isReviewActive: false,
    allCandidates: [],
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
    castVoteBtn: document.getElementById("evm-final-cast-btn") || document.getElementById("cast-vote-btn"),
    step3Error: document.getElementById("step3-error"),
    step3ErrorMsg: document.getElementById("step3-error-msg"),
    backToStep2Btn: document.getElementById("back-to-step2-btn"),

    postStepperBar: document.getElementById("post-stepper-bar"),
    evmBallotView: document.getElementById("evm-ballot-view"),
    evmHouseBadge: document.getElementById("evm-house-badge"),
    evmPostTitle: document.getElementById("evm-post-title"),
    evmPostSubtitle: document.getElementById("evm-post-subtitle"),
    evmCandidateList: document.getElementById("evm-candidate-list"),
    evmBackBtn: document.getElementById("evm-back-btn"),
    evmSelectionStatus: document.getElementById("evm-selection-status"),
    evmOverallCount: document.getElementById("evm-overall-count"),
    evmNextBtn: document.getElementById("evm-next-btn"),
    evmReviewView: document.getElementById("evm-review-view"),
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
    // Kept for backward compatibility
  }

  function renderPostStepper() {
    if (!el.postStepperBar) return;
    el.postStepperBar.innerHTML = "";
    const posList = getPositionsList();

    posList.forEach((pos, pIdx) => {
      const isSelected = Boolean(state.selectedByRole[pos.id] || state.votedRoles[pos.id]);
      const isActive = !state.isReviewActive && pIdx === state.currentPostIdx;

      const pill = document.createElement("button");
      pill.type = "button";
      pill.className = `post-step-pill${isActive ? " is-active" : ""}${isSelected ? " is-done" : ""}`;
      pill.setAttribute("role", "tab");
      pill.setAttribute("aria-selected", isActive ? "true" : "false");
      pill.innerHTML = `
        <span class="post-step-num">${isSelected ? "✓" : (pIdx + 1)}</span>
        <span>${(pos.shortTitle || pos.title).replace(/\s*Sec\b/i, "")}</span>
      `;

      pill.addEventListener("click", () => {
        state.currentPostIdx = pIdx;
        state.isReviewActive = false;
        renderEvmView();
      });

      el.postStepperBar.appendChild(pill);
    });
  }

  function renderEvmView() {
    if (!el.evmBallotView || !el.evmReviewView) return;
    const posList = getPositionsList();

    if (state.isReviewActive) {
      el.evmBallotView.hidden = true;
      el.evmReviewView.hidden = false;
      renderEvmReviewGrid();
      return;
    }

    el.evmBallotView.hidden = false;
    el.evmReviewView.hidden = true;

    renderPostStepper();

    const currentRole = posList[state.currentPostIdx];
    if (!currentRole) return;

    const votedBallot = state.votedRoles[currentRole.id] || null;
    const picked = state.selectedByRole[currentRole.id] || (votedBallot ? { candidate: { id: votedBallot.candidateId, fullName: votedBallot.candidateName } } : null);

    // Update Header Strip
    if (el.evmHouseBadge) {
      el.evmHouseBadge.textContent = `School Cabinet · Post ${state.currentPostIdx + 1} of ${posList.length}`;
    }
    if (el.evmPostTitle) el.evmPostTitle.textContent = currentRole.title;
    if (el.evmPostSubtitle) el.evmPostSubtitle.textContent = currentRole.subtitle || `Class ${currentRole.className} · Central Cabinet`;

    // Render Candidates List for current role (separated by post, exactly like teachers)
    if (el.evmCandidateList) {
      el.evmCandidateList.innerHTML = "";
      const roleCands = (state.allCandidates || []).filter((c) => (c.positionId || currentRole.id) === currentRole.id);

      if (votedBallot) {
        const votedMsg = document.createElement("div");
        votedMsg.style.cssText = "background:#f0fdf4; border:1.5px solid #86efac; border-radius:14px; padding:1.25rem 1.5rem; color:#166534; font-weight:700; text-align:center; font-size:1.1rem; margin:auto;";
        votedMsg.innerHTML = `✓ You have already voted for <strong>${votedBallot.candidateName}</strong> in this position.`;
        el.evmCandidateList.appendChild(votedMsg);
      } else if (roleCands.length === 0) {
        const noCand = document.createElement("p");
        noCand.style.cssText = "color:var(--text-muted); font-size:1rem; text-align:center; margin:auto;";
        noCand.textContent = "No approved candidates registered for this role.";
        el.evmCandidateList.appendChild(noCand);
      } else {
        roleCands.forEach((cand) => {
          const isSelected = picked && (picked.candidate?.id === cand.id || picked.id === cand.id);

          const photoHtml = cand.photoPath || cand.photoUrl
            ? `<img src="${cand.photoPath || cand.photoUrl}" alt="${cand.fullName}" />`
            : `<span>${getInitials(cand.fullName)}</span>`;

          const subText = cand.className ? `Class ${cand.className}` : "Class 10";

          const row = document.createElement("div");
          row.className = `evm-candidate-row${isSelected ? " is-selected" : ""}`;
          row.setAttribute("role", "radio");
          row.setAttribute("aria-checked", isSelected ? "true" : "false");
          row.dataset.candId = cand.id;

          const sym = cand.symbolObj || { name: "Candidate Choice", icon: "⭐" };
          const symSlug = (sym.slug || sym.name || "star").toLowerCase().replace(/[\s-]+/g, "_");
          const symImg = (sym.image || sym.imagePath || `../assets/symbols/${symSlug}.png`) + '?v=20261123N';

          row.innerHTML = `
            <div class="evm-cand-avatar">${photoHtml}</div>
            <div class="evm-cand-symbol" title="Election Symbol: ${sym.name}">
              <div class="evm-symbol-box">
                <img src="${symImg}" alt="${sym.name}" class="evm-symbol-img" onerror="this.style.display='none';this.nextElementSibling.style.display='inline-block';" />
                <span class="evm-symbol-fallback" style="display:none;">${sym.icon || "⭐"}</span>
              </div>
            </div>
            <div class="evm-cand-info">
              <h3 class="evm-cand-name">${cand.fullName}</h3>
              <span class="evm-cand-sub">${subText}${cand.tagline ? ` &bull; ${cand.tagline}` : ""}</span>
            </div>
            <div class="evm-right-cluster">
              <span class="evm-led-lamp"></span>
              <button type="button" class="evm-vote-btn" tabindex="-1">
                ${isSelected ? "VOTED ✓" : "VOTE"}
              </button>
            </div>
          `;

          row.addEventListener("click", () => {
            state.selectedByRole[currentRole.id] = {
              positionId: currentRole.id,
              positionName: currentRole.title,
              candidate: cand,
              id: cand.id,
              fullName: cand.fullName
            };
            if (el.step3Error) el.step3Error.hidden = true;
            renderEvmView();
          });

          el.evmCandidateList.appendChild(row);
        });
      }
    }

    // Update Kiosk Navigation & Status Footer
    const hasChosenCur = Boolean(state.selectedByRole[currentRole.id] || votedBallot);
    const selectedCount = Object.keys(state.selectedByRole).length;

    if (el.evmSelectionStatus) {
      if (picked && (picked.candidate || picked.fullName)) {
        el.evmSelectionStatus.textContent = `✓ Selected: ${picked.candidate?.fullName || picked.fullName}`;
      } else {
        el.evmSelectionStatus.textContent = "Select 1 candidate to proceed";
      }
    }

    if (el.evmOverallCount) {
      el.evmOverallCount.textContent = `${selectedCount} / ${posList.length} Selected`;
    }

    if (el.evmBackBtn) {
      if (state.currentPostIdx > 0) {
        el.evmBackBtn.innerHTML = "&larr; Previous Post";
      } else {
        el.evmBackBtn.innerHTML = "&larr; Back to Info";
      }
    }

    if (el.evmNextBtn) {
      const isLastPost = state.currentPostIdx >= posList.length - 1;
      el.evmNextBtn.disabled = !hasChosenCur;
      el.evmNextBtn.style.opacity = hasChosenCur ? "1" : "0.45";
      el.evmNextBtn.style.cursor = hasChosenCur ? "pointer" : "not-allowed";

      if (!isLastPost) {
        const nextRole = posList[state.currentPostIdx + 1];
        el.evmNextBtn.innerHTML = `Next: ${(nextRole.shortTitle || nextRole.title).replace(/\s*Sec\b/i, "")} &rarr;`;
      } else {
        el.evmNextBtn.innerHTML = `Review &amp; Cast Vote &rarr;`;
      }
    }
  }

  function renderEvmReviewGrid() {
    if (!el.evmReviewGrid) return;
    el.evmReviewGrid.innerHTML = "";
    const posList = getPositionsList();

    const selectedCount = Object.keys(state.selectedByRole).length;
    const totalCount = posList.length;

    if (el.evmFinalCastBtn) {
      const canCast = selectedCount >= totalCount && totalCount > 0;
      el.evmFinalCastBtn.disabled = !canCast;
      el.evmFinalCastBtn.innerHTML = canCast
        ? `<span>Confirm &amp; Cast School Cabinet Ballot (${selectedCount}/${totalCount}) &rarr;</span>`
        : `<span>Select All Roles (${selectedCount}/${totalCount}) to Cast</span>`;
    }

    posList.forEach((pos, pIdx) => {
      const picked = state.selectedByRole[pos.id] || (state.votedRoles[pos.id] ? { candidate: { fullName: state.votedRoles[pos.id].candidateName } } : null);

      const card = document.createElement("div");
      card.className = `evm-review-card${picked ? " is-filled" : ""}`;
      card.style.cursor = "pointer";
      card.title = "Click to change choice for this post";

      const candObj = picked?.candidate || picked;
      const photoHtml = candObj?.photoPath || candObj?.photoUrl
        ? `<img src="${candObj.photoPath || candObj.photoUrl}" alt="${candObj.fullName}" />`
        : `<span>${getInitials(candObj?.fullName || "?")}</span>`;

      const sym = candObj?.symbolObj || { name: "", icon: "⭐" };
      const symSlug = (sym.slug || sym.name || "star").toLowerCase().replace(/[\s-]+/g, "_");
      const symImg = (sym.image || sym.imagePath || `../assets/symbols/${symSlug}.png`) + '?v=20261123N';

      card.innerHTML = `
        <div class="evm-review-avatar">${photoHtml}</div>
        <div class="evm-review-info">
          <p class="evm-review-role">${pos.title}</p>
          <h4 class="evm-review-cand">${candObj ? candObj.fullName : '<span style="color:#dc2626;">Not Selected &bull; Click to Choose</span>'}</h4>
          <span class="evm-review-sub">${pos.subtitle || "School Cabinet"}</span>
        </div>
        ${candObj ? `
          <div class="evm-review-symbol" title="Symbol: ${sym.name}">
            <img src="${symImg}" alt="${sym.name}" onerror="this.style.display='none';" />
          </div>
        ` : ""}
      `;

      card.addEventListener("click", () => {
        state.currentPostIdx = pIdx;
        state.isReviewActive = false;
        renderEvmView();
      });

      el.evmReviewGrid.appendChild(card);
    });
  }

  async function renderCandidatesStep() {
    state.allCandidates = await window.ElectionBackend.getHouseCandidates(houseConfig.code);
    const posList = getPositionsList();
    if (!state.pendingRoleIds.length) {
      state.pendingRoleIds = posList.filter((p) => !state.votedRoles[p.id]).map((p) => p.id);
    }
    state.selectedByRole = {};
    state.currentPostIdx = 0;
    state.isReviewActive = false;
    if (el.step3Error) el.step3Error.hidden = true;

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

      // Prominent Registered House Display (FIRST IT WILL SHOW HIS HOUSE)
      const registeredHouseTitle = result.student.registeredHouseTitle || result.student.winnerHouseName || (result.student.houseCode ? `${result.student.houseCode} House` : "Student House");
      const registeredConstituency = result.student.constituency || "";
      const contestantRole = result.student.winnerRoleTitle || (isCabinetContestant ? "School Cabinet Contestant" : "House Leader");
      const studentClassSec = result.student.classSec || (result.student.className ? `Class ${result.student.className}-${result.student.section}` : "");

      const houseMainEl = document.getElementById("voter-house-main-name");
      const houseConstEl = document.getElementById("voter-house-constituency-pill");
      const houseSubEl = document.getElementById("voter-house-sub-info");
      const houseCardEl = document.getElementById("voter-house-highlight-card");
      if (houseMainEl) houseMainEl.textContent = registeredHouseTitle;
      if (houseConstEl) houseConstEl.textContent = registeredConstituency ? `${registeredConstituency} Constituency` : "Official Constituency";
      if (houseSubEl) houseSubEl.textContent = `${studentClassSec ? `${studentClassSec} · ` : ""}${contestantRole}`;
      if (houseCardEl) houseCardEl.hidden = false;

      el.voterMeta.textContent = isWinner
        ? `🏛️ ${registeredHouseTitle}${registeredConstituency ? ` (${registeredConstituency})` : ""} · ${contestantRole}`
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

  // EVM Navigation & Review Action Listeners
  if (el.evmNextBtn) {
    el.evmNextBtn.addEventListener("click", () => {
      const posList = getPositionsList();
      const currentRole = posList[state.currentPostIdx];
      const hasChosenCur = Boolean(state.selectedByRole[currentRole.id] || state.votedRoles[currentRole.id]);
      if (!hasChosenCur) return;

      if (state.currentPostIdx < posList.length - 1) {
        state.currentPostIdx++;
        renderEvmView();
      } else {
        state.isReviewActive = true;
        renderEvmView();
      }
    });
  }

  if (el.evmBackBtn) {
    el.evmBackBtn.addEventListener("click", () => {
      if (state.currentPostIdx > 0) {
        state.currentPostIdx--;
        renderEvmView();
      } else {
        goToStep(2);
      }
    });
  }

  if (el.evmReviewBackBtn) {
    el.evmReviewBackBtn.addEventListener("click", () => {
      state.isReviewActive = false;
      renderEvmView();
    });
  }

  async function triggerFaceGuardAndCast() {
    const posList = getPositionsList();
    const pendingIds = state.pendingRoleIds.length ? state.pendingRoleIds : posList.map((p) => p.id);
    const missingIds = pendingIds.filter((pid) => !state.selectedByRole[pid]);
    if (state.isSubmitting || !state.verifiedStudent || missingIds.length > 0) {
      if (missingIds.length > 0) {
        const missingNames = missingIds
          .map((pid) => posList.find((p) => p.id === pid)?.title || pid)
          .join(", ");
        if (el.step3ErrorMsg) el.step3ErrorMsg.textContent = `Please select a candidate for: ${missingNames}.`;
        if (el.step3Error) el.step3Error.hidden = false;
        alert("Cannot cast ballot: Missing vote for:\n\n" + missingNames + ".\n\nPlease select a candidate for all posts before submitting.");
      }
      return;
    }

    state.isSubmitting = false;
    if (el.evmFinalCastBtn) setLoading(el.evmFinalCastBtn, false);
    if (el.step3Error) el.step3Error.hidden = true;

    try {
      if (!state.mediaStream) {
        await warmUpBackgroundCamera();
        await new Promise((r) => setTimeout(r, 250));
      }
      openFaceGuardModal("Please look at the camera to verify voter identity.");
    } catch (err) {
      openFaceGuardModal("Camera error: " + (err.message || "Unable to access webcam."));
    }
  }

  if (el.evmFinalCastBtn) {
    el.evmFinalCastBtn.addEventListener("click", triggerFaceGuardAndCast);
  }
  if (el.castVoteBtn && el.castVoteBtn !== el.evmFinalCastBtn) {
    el.castVoteBtn.addEventListener("click", triggerFaceGuardAndCast);
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
      const voterGroup = urlParams.get("voterGroup");
      const step1Badge = document.querySelector("#step-1 .badge-house");
      const step1Title = document.querySelector("#step-1 .panel-title");
      if (step1Badge && step1Title) {
        step1Badge.textContent = "👑 School Cabinet Voting · For House Winners (Elected Captains)";
        step1Title.textContent = "House Winners Verification";
        document.title = "School Cabinet (For House Winners) — School Election 2026";
      }

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
