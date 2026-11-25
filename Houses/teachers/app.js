// Teacher Universal Polling Booth — 5-Step Progressive Controller
// Allows teachers to vote for School Cabinet (5 roles) + All 6 Student Houses (24 roles) in one unified flow.
(function () {
  const boothData = window.TEACHER_BOOTH_DATA || {};
  const houses = boothData.houses || [];
  const candidates = (boothData.candidates && boothData.candidates.length > 0)
    ? boothData.candidates
    : (window.ALL_CONTESTING_CANDIDATES || []);
  const electionId = boothData.electionId || "ELECTION_2026";
  const totalAvailableRoles = houses.reduce((sum, h) => sum + (h.positions?.length || 0), 0);

  const ELECTION_SYMBOLS = [
    { name: "Torch", icon: "🔦" },
    { name: "Book", icon: "📖" },
    { name: "Rising Sun", icon: "🌅" },
    { name: "Star", icon: "⭐" },
    { name: "Shield", icon: "🛡️" },
    { name: "Rocket", icon: "🚀" }
  ];

  const state = {
    step: 1,
    verifiedTeacher: null,
    votedRolesMap: {},
    selectedByRole: {}, // { [`${houseCode}_${posId}`]: candidate }
    mediaStream: null,
    picoClassifier: null,
    faceDetectLoopId: null,
    consecutiveFaces: 0,
    capturedPhotoDataUrl: null,
    resetInterval: null,
    isSubmitting: false,
    scannerBuffer: "",
    // EVM Post-by-Post Stepper State
    currentHouseIdx: 0,
    currentPostIdx: 0,
    isReviewActive: false,
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

    voterInitials: document.getElementById("voter-initials"),
    voterName: document.getElementById("voter-name"),
    voterIdBadge: document.getElementById("voter-id-badge"),
    voterMeta: document.getElementById("voter-meta"),
    backToStep1Btn: document.getElementById("back-to-step1-btn"),
    nextToVoteBtn: document.getElementById("next-to-vote-btn"),

    houseTabsBar: document.getElementById("house-tabs-bar"),
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
    step3Error: document.getElementById("step3-error"),
    step3ErrorMsg: document.getElementById("step3-error-msg"),

    cameraVideo: document.getElementById("camera-video"),
    cameraCanvas: document.getElementById("camera-canvas"),
    faceGuardModal: document.getElementById("face-guard-modal"),
    faceLiveVideo: document.getElementById("face-live-video"),
    cameraGuideRing: document.getElementById("camera-guide-ring"),
    faceStatusLabel: document.getElementById("face-status-label"),
    faceGuardCancelBtn: document.getElementById("face-guard-cancel-btn"),
    faceGuardConfirmBtn: document.getElementById("face-guard-confirm-btn"),

    successSummary: document.getElementById("success-summary"),
    resetCountdownText: document.getElementById("reset-countdown-text"),
    resetNowBtn: document.getElementById("reset-now-btn"),
    boothStationName: document.getElementById("booth-station-name"),
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

  function setStep(stepNum) {
    state.step = stepNum;
    el.stepPanels.forEach((p, idx) => {
      if (p) p.hidden = idx + 1 !== stepNum;
    });
    el.stepIndicators.forEach((pill, idx) => {
      const n = idx + 1;
      pill.classList.toggle("is-active", n === stepNum);
      pill.classList.toggle("is-complete", n < stepNum);
    });

    const pageShell = document.querySelector(".page-shell");
    if (pageShell) {
      pageShell.classList.toggle("step-3-active", stepNum === 3);
      pageShell.classList.toggle("evm-active", stepNum === 3);
    }

    if (stepNum === 3) {
      window.scrollTo(0, 0);
    }

    if (stepNum === 1) {
      focusScannerInput();
    }
  }

  let spinnerTimer = null;
  function showDelayedSpinner(title = "Recording Universal Ballot...", sub = "Saving School Cabinet and House votes to Supabase...") {
    const overlay = document.getElementById("loading-overlay");
    if (!overlay) return;
    const tEl = document.getElementById("loading-overlay-title");
    const sEl = document.getElementById("loading-overlay-subtitle");
    if (tEl) tEl.textContent = title;
    if (sEl) sEl.textContent = sub;
    clearTimeout(spinnerTimer);
    spinnerTimer = setTimeout(() => {
      overlay.hidden = false;
    }, 280);
  }

  function hideDelayedSpinner() {
    clearTimeout(spinnerTimer);
    const overlay = document.getElementById("loading-overlay");
    if (overlay) overlay.hidden = true;
  }

  function showError(msg, title = "Accreditation Error") {
    if (!el.step1Error) return;
    el.step1ErrorTitle.textContent = title;
    el.step1ErrorMsg.textContent = msg;
    el.step1Error.hidden = false;
  }

  function clearError() {
    if (el.step1Error) el.step1Error.hidden = true;
  }

  function focusScannerInput() {
    if (state.step !== 1) return;
    if (el.paneBarcodeScan && !el.paneBarcodeScan.hidden && el.scannerStreamInput) {
      setTimeout(() => {
        el.scannerStreamInput.focus();
      }, 50);
    } else if (el.paneManualEntry && !el.paneManualEntry.hidden && el.admissionInput) {
      setTimeout(() => {
        el.admissionInput.focus();
      }, 50);
    }
  }

  // --- Hardware Camera & Pico.js Biometrics ---
  async function warmUpCamera() {
    if (state.mediaStream) return;
    try {
      state.mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: "user" },
        audio: false,
      });
      if (el.cameraVideo) {
        el.cameraVideo.srcObject = state.mediaStream;
        el.cameraVideo.play().catch(() => {});
      }
    } catch (e) {
      console.warn("Camera warmup note:", e);
    }
  }

  async function loadPicoFaceClassifier() {
    if (state.picoClassifier) return state.picoClassifier;
    try {
      const res = await fetch("./facefinder");
      if (!res.ok) throw new Error("Status " + res.status);
      const buf = await res.arrayBuffer();
      if (typeof pico !== "undefined" && pico.unpack_cascade) {
        state.picoClassifier = pico.unpack_cascade(new Int8Array(buf));
      }
    } catch (e) {
      console.warn("Pico facefinder load:", e);
    }
    return state.picoClassifier;
  }

  function generateBoothSnapshot(label = "Teacher Verification Snapshot") {
    const canvas = el.cameraCanvas || document.createElement("canvas");
    canvas.width = 360;
    canvas.height = 270;
    const ctx = canvas.getContext("2d");
    const w = 360, h = 270;

    // Background
    ctx.fillStyle = "#faf6ee";
    ctx.fillRect(0, 0, w, h);

    // Border
    ctx.strokeStyle = "#059669";
    ctx.lineWidth = 6;
    ctx.strokeRect(3, 3, w - 6, h - 6);

    // Initials Avatar
    ctx.fillStyle = "#059669";
    ctx.beginPath();
    ctx.arc(w / 2, 85, 42, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 26px sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(getInitials(state.verifiedTeacher?.fullName), w / 2, 85);

    // Teacher Details
    ctx.fillStyle = "#141413";
    ctx.font = "bold 16px sans-serif";
    ctx.fillText(state.verifiedTeacher?.fullName || "Verified Teacher", w / 2, 155);

    ctx.fillStyle = "#4a4741";
    ctx.font = "13px monospace";
    ctx.fillText(`Faculty ID: ${state.verifiedTeacher?.admissionNo || ""}`, w / 2, 185);

    ctx.fillStyle = "#047857";
    ctx.font = "bold 12px sans-serif";
    ctx.fillText("All Houses & School Cabinet Ballot", w / 2, 212);

    ctx.fillStyle = "#767167";
    ctx.font = "11px monospace";
    ctx.fillText(`${label} · ${new Date().toLocaleTimeString()}`, w / 2, 240);

    return canvas.toDataURL("image/jpeg", 0.78);
  }

  function captureWebcamFrame() {
    const video = (el.cameraVideo && el.cameraVideo.readyState >= 2 && el.cameraVideo.videoWidth > 0)
      ? el.cameraVideo
      : (el.faceLiveVideo && el.faceLiveVideo.readyState >= 2 && el.faceLiveVideo.videoWidth > 0)
      ? el.faceLiveVideo
      : null;

    if (state.mediaStream && video) {
      try {
        const canvas = el.cameraCanvas || document.createElement("canvas");
        canvas.width = 360;
        canvas.height = 270;
        const ctx = canvas.getContext("2d");
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        return canvas.toDataURL("image/jpeg", 0.78);
      } catch (err) {
        console.warn("Camera canvas capture error, falling back to generated badge:", err);
      }
    }
    return generateBoothSnapshot("Teacher Automatic Capture");
  }

  function startFaceDetectionLoop() {
    state.consecutiveFaces = 0;
    if (el.cameraGuideRing) el.cameraGuideRing.classList.remove("is-ready");
    if (el.faceStatusLabel) {
      el.faceStatusLabel.textContent = "Position face inside oval guide...";
      el.faceStatusLabel.style.background = "#fef3c7";
      el.faceStatusLabel.style.color = "#92400e";
    }
    if (el.faceGuardConfirmBtn) el.faceGuardConfirmBtn.disabled = true;

    if (state.mediaStream && el.faceLiveVideo) {
      el.faceLiveVideo.srcObject = state.mediaStream;
      el.faceLiveVideo.play().catch(() => {});
    }

    const checkFrame = async () => {
      if (!el.faceGuardModal || el.faceGuardModal.hidden) return;

      const video = el.faceLiveVideo;
      if (video && video.readyState >= 2 && video.videoWidth > 0) {
        const w = 320, h = 240;
        const canvas = el.cameraCanvas;
        canvas.width = w;
        canvas.height = h;
        const ctx = canvas.getContext("2d");
        ctx.drawImage(video, 0, 0, w, h);

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
        const stdDev = Math.sqrt(Math.max(0, (sumSq / n) - (mean * mean)));

        if (mean > 15 && stdDev > 9.0) {
          const classifier = await loadPicoFaceClassifier();
          if (classifier && typeof pico !== "undefined") {
            const gray = new Uint8Array(w * h);
            for (let r = 0; r < h; ++r) {
              for (let c = 0; c < w; ++c) {
                gray[r * w + c] = (2 * d[r * 4 * w + 4 * c] + 7 * d[r * 4 * w + 4 * c + 1] + 1 * d[r * 4 * w + 4 * c + 2]) / 10;
              }
            }
            const dets = pico.run_cascade({ pixels: gray, nrows: h, ncols: w, ldim: w }, classifier, {
              shiftfactor: 0.1,
              minsize: 36,
              maxsize: 210,
              scalefactor: 1.1,
            });
            const clustered = pico.cluster_detections(dets, 0.2);
            const valid = clustered.filter((pt) => pt[3] > 36.0);

            if (valid.length > 0) {
              state.consecutiveFaces++;
            } else {
              state.consecutiveFaces = Math.max(0, state.consecutiveFaces - 1);
            }
          } else {
            // Hardware/Pico fallback
            state.consecutiveFaces++;
          }
        } else {
          state.consecutiveFaces = 0;
        }

        if (state.consecutiveFaces >= 2) {
          if (el.cameraGuideRing) el.cameraGuideRing.classList.add("is-ready");
          if (el.faceStatusLabel) {
            el.faceStatusLabel.textContent = "✓ Face Verified! Ready to cast.";
            el.faceStatusLabel.style.background = "#dcfce7";
            el.faceStatusLabel.style.color = "#15803d";
          }
          if (el.faceGuardConfirmBtn) el.faceGuardConfirmBtn.disabled = false;
        }
      }

      state.faceDetectLoopId = setTimeout(checkFrame, 180);
    };

    checkFrame();
  }

  function stopFaceDetectionLoop() {
    if (state.faceDetectLoopId) {
      clearTimeout(state.faceDetectLoopId);
      state.faceDetectLoopId = null;
    }
  }

  // --- Step 1 Authentication & Verification ---
  async function handleTeacherIdVerification(idStr) {
    clearError();
    const cleanId = String(idStr || "").trim();
    if (!cleanId) {
      showError("Please scan your Teacher Card barcode or enter your Faculty ID.");
      return;
    }

    try {
      if (el.verifyBtn) el.verifyBtn.disabled = true;
      const res = await window.TeacherBackend.verifyTeacher(cleanId);
      if (!res.ok) {
        showError(res.message || "Teacher verification failed.", res.code === "ALREADY_VOTED" ? "Already Voted" : "Accreditation Error");
        return;
      }

      state.verifiedTeacher = res.teacher;
      state.votedRolesMap = res.votedRolesMap || {};

      // Populate Step 2 Profile
      el.voterInitials.textContent = getInitials(res.teacher.fullName);
      el.voterName.textContent = res.teacher.fullName;
      el.voterMeta.textContent = `${res.teacher.subject || "Faculty"} · ${res.teacher.houseName || "All Houses & Cabinet"}`;
      el.voterIdBadge.textContent = `Faculty ID ${res.teacher.admissionNo}`;

      // Start background camera
      warmUpCamera();

      // Advance to Step 2
      setStep(2);
    } catch (err) {
      showError(err.message || "Error reaching database.");
    } finally {
      if (el.verifyBtn) el.verifyBtn.disabled = false;
    }
  }

  // --- Step 3 EVM Zero-Scroll Post-by-Post Ballot Controller ---
  function countTotalProgress() {
    let selected = 0;
    let total = 0;
    houses.forEach((h) => {
      (h.positions || []).forEach((r) => {
        total++;
        const rk = `${h.code}_${r.id}`;
        if (state.selectedByRole[rk] || state.votedRolesMap[rk]) selected++;
      });
    });
    return { selected, total };
  }

  function renderHouseTabs() {
    if (!el.houseTabsBar) return;
    el.houseTabsBar.innerHTML = "";

    houses.forEach((house, hIdx) => {
      const houseCode = house.code;
      const roles = house.positions || [];
      let filledCount = 0;
      roles.forEach((r) => {
        const rk = `${houseCode}_${r.id}`;
        if (state.selectedByRole[rk] || state.votedRolesMap[rk]) filledCount++;
      });
      const isComplete = filledCount >= roles.length && roles.length > 0;
      const isActive = hIdx === state.currentHouseIdx;

      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = `house-tab-chip${isActive ? " is-active" : ""}${isComplete ? " is-complete" : ""}`;
      chip.style.setProperty("--chip-accent", house.accent || "var(--accent-teacher)");
      chip.innerHTML = `
        <span>${house.shortName || house.name}</span>
        <span class="tab-badge">${isComplete ? "✓ " : ""}${filledCount}/${roles.length}</span>
      `;
      chip.addEventListener("click", () => {
        state.currentHouseIdx = hIdx;
        state.currentPostIdx = 0;
        state.isReviewActive = false;
        renderEvmView();
      });
      el.houseTabsBar.appendChild(chip);
    });
  }

  function renderPostStepper() {
    if (!el.postStepperBar) return;
    el.postStepperBar.innerHTML = "";

    const currentHouse = houses[state.currentHouseIdx];
    if (!currentHouse) return;
    const roles = currentHouse.positions || [];

    roles.forEach((role, pIdx) => {
      const rk = `${currentHouse.code}_${role.id}`;
      const isSelected = Boolean(state.selectedByRole[rk] || state.votedRolesMap[rk]);
      const isActive = pIdx === state.currentPostIdx;

      const pill = document.createElement("button");
      pill.type = "button";
      pill.className = `post-step-pill${isActive ? " is-active" : ""}${isSelected ? " is-done" : ""}`;
      const hAccent = currentHouse.accent || "#059669";
      const hText = currentHouse.accentText || hAccent;
      const hOnAccent = currentHouse.onAccent || "#ffffff";
      if (isActive) {
        pill.style.borderColor = hAccent;
        pill.style.color = hText;
        pill.style.boxShadow = `0 2px 8px ${hAccent}25`;
      }
      pill.innerHTML = `
        <span class="post-step-num" style="${isActive ? `background:${hAccent}; color:${hOnAccent};` : ''}">${isSelected ? "✓" : (pIdx + 1)}</span>
        <span>${role.shortTitle || role.title}</span>
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

    if (state.isReviewActive) {
      el.evmBallotView.hidden = true;
      el.evmReviewView.hidden = false;
      renderEvmReviewGrid();
      return;
    }

    el.evmBallotView.hidden = false;
    el.evmReviewView.hidden = true;

    renderHouseTabs();
    renderPostStepper();

    const currentHouse = houses[state.currentHouseIdx];
    if (!currentHouse) return;
    const roles = currentHouse.positions || [];
    const currentRole = roles[state.currentPostIdx];
    if (!currentRole) return;

    // --- Dynamic House Theme Color Switching ---
    const houseAccent = currentHouse.accent || "#059669";
    const houseHover = currentHouse.accentHover || currentHouse.hover || houseAccent;
    const houseText = currentHouse.accentText || currentHouse.text || houseAccent;
    const houseOnAccent = currentHouse.onAccent || "#ffffff";
    const houseSubtle = `${houseAccent}18`;

    // 1. Update booth card top border to match the active house
    const boothCard = document.querySelector(".booth-card");
    if (boothCard) {
      boothCard.style.borderTopColor = houseAccent;
    }

    // 2. Update house eyebrow text and color in header
    const houseEyebrow = document.querySelector(".house-eyebrow");
    if (houseEyebrow) {
      houseEyebrow.textContent = `${currentHouse.name} · Faculty Voting Station`;
      houseEyebrow.style.color = houseAccent;
    }

    // 3. Set dynamic CSS variables on pageShell
    const pageShell = document.querySelector(".page-shell");
    if (pageShell) {
      pageShell.style.setProperty("--house-accent", houseAccent);
      pageShell.style.setProperty("--house-hover", houseHover);
      pageShell.style.setProperty("--house-text", houseText);
      pageShell.style.setProperty("--house-on-accent", houseOnAccent);
      pageShell.style.setProperty("--house-subtle", houseSubtle);
    }

    const roleKey = `${currentHouse.code}_${currentRole.id}`;
    const alreadyVoted = state.votedRolesMap[roleKey];
    const picked = state.selectedByRole[roleKey] || (alreadyVoted ? { candidate: { id: alreadyVoted.candidateId, fullName: alreadyVoted.candidateName } } : null);

    // Update Header Strip with house accent
    if (el.evmHouseBadge) {
      el.evmHouseBadge.textContent = `${currentHouse.name} · Post ${state.currentPostIdx + 1} of ${roles.length}`;
      el.evmHouseBadge.style.background = houseSubtle;
      el.evmHouseBadge.style.color = houseText;
      el.evmHouseBadge.style.borderColor = houseAccent;
    }
    if (el.evmPostTitle) el.evmPostTitle.textContent = currentRole.title;
    if (el.evmPostSubtitle) el.evmPostSubtitle.textContent = currentRole.subtitle || "";

    // Render Candidates List (2-3 candidates for current role, strictly zero scroll)
    if (el.evmCandidateList) {
      el.evmCandidateList.innerHTML = "";
      const roleCands = candidates.filter((c) => c.houseCode === currentHouse.code && c.positionId === currentRole.id && c.isApproved);

      if (alreadyVoted) {
        const votedMsg = document.createElement("div");
        votedMsg.style.cssText = "background:#f0fdf4; border:1.5px solid #86efac; border-radius:14px; padding:1.25rem 1.5rem; color:#166534; font-weight:700; text-align:center; font-size:1.1rem; margin:auto;";
        votedMsg.innerHTML = `✓ You have already voted for <strong>${alreadyVoted.candidateName}</strong> in this position.`;
        el.evmCandidateList.appendChild(votedMsg);
      } else if (roleCands.length === 0) {
        const noCand = document.createElement("p");
        noCand.style.cssText = "color:var(--text-muted); font-size:1rem; text-align:center; margin:auto;";
        noCand.textContent = "No candidates registered for this role.";
        el.evmCandidateList.appendChild(noCand);
      } else {
        roleCands.forEach((cand, candIdx) => {
          const isSelected = picked && picked.candidate.id === cand.id;

          const photoHtml = cand.photoPath || cand.photoUrl
            ? `<img src="${cand.photoPath || cand.photoUrl}" alt="${cand.fullName}" />`
            : `<span>${getInitials(cand.fullName)}</span>`;

          let subText = String(cand.section || "").trim();
          if (!/^class\s+/i.test(subText)) {
            subText = cand.className ? `Class ${cand.className} · ${subText}` : subText;
          }

          const row = document.createElement("div");
          row.className = `evm-candidate-row${isSelected ? " is-selected" : ""}`;
          row.setAttribute("role", "radio");
          row.setAttribute("aria-checked", isSelected ? "true" : "false");
          row.dataset.candId = cand.id;

                      const sym = cand.symbolObj || { name: "Candidate Choice", icon: "⭐" };
            const symSlug = (sym.slug || sym.name || "star").toLowerCase().replace(/[\s-]+/g, "_");
            const symImg = (sym.image || sym.imagePath || `../assets/symbols/${symSlug}.png`) + '?v=20261123N';

            row.innerHTML = `
              <div class="evm-cand-avatar" style="${!cand.photoPath && !cand.photoUrl ? `background:${houseSubtle}; border-color:${houseAccent}60; color:${houseText};` : ''}">${photoHtml}</div>
              <div class="evm-cand-symbol" title="Election Symbol: ${sym.name}">
                <div class="evm-symbol-box">
                  <img src="${symImg}" alt="${sym.name}" class="evm-symbol-img" onerror="this.style.display='none';this.nextElementSibling.style.display='inline-block';" />
                  <span class="evm-symbol-fallback" style="display:none;">${sym.icon || "⭐"}</span>
                </div>
                <span class="evm-symbol-caption">${sym.name}</span>
              </div>
              <div class="evm-cand-info">
                <h3 class="evm-cand-name">${cand.fullName}</h3>
                <span class="evm-cand-sub">${subText}</span>
                ${cand.tagline ? `<span class="evm-cand-tagline">&ldquo;${cand.tagline}&rdquo;</span>` : ""}
              </div>
              <div class="evm-right-cluster">
                <span class="evm-led-lamp"></span>
                <button type="button" class="evm-vote-btn" tabindex="-1">
                  ${isSelected ? "VOTED ✓" : "VOTE"}
                </button>
              </div>
            `;

          if (isSelected) {
            row.style.borderColor = houseAccent;
            row.style.boxShadow = `0 6px 20px -2px ${houseAccent}40`;
          }

          row.addEventListener("click", () => {
            state.selectedByRole[roleKey] = {
              houseCode: currentHouse.code,
              positionId: currentRole.id,
              positionName: currentRole.title,
              candidate: cand,
            };
            renderEvmView();
          });

          el.evmCandidateList.appendChild(row);
        });
      }
    }

    // Update Footer Navigation
    updateFooterNav(currentHouse, currentRole, roles, picked);
  }

  function updateFooterNav(currentHouse, currentRole, roles, picked) {
    const { selected, total } = countTotalProgress();

    // 1. Back button
    if (el.evmBackBtn) {
      if (state.currentHouseIdx === 0 && state.currentPostIdx === 0) {
        el.evmBackBtn.innerHTML = `&larr; Back to Profile`;
      } else if (state.currentPostIdx > 0) {
        const prevRole = roles[state.currentPostIdx - 1];
        el.evmBackBtn.innerHTML = `&larr; Back: ${prevRole.shortTitle || prevRole.title}`;
      } else {
        const prevHouse = houses[state.currentHouseIdx - 1];
        el.evmBackBtn.innerHTML = `&larr; Back: ${prevHouse.shortName || prevHouse.name}`;
      }
    }

    // 2. Status text & overall progress
    if (el.evmSelectionStatus) {
      if (picked) {
        el.evmSelectionStatus.innerHTML = `<span style="color:#059669; font-weight:800;">✓ Selected: ${picked.candidate.fullName}</span>`;
      } else {
        el.evmSelectionStatus.innerHTML = `<span style="color:var(--text-muted);">Please tap candidate or press blue VOTE button</span>`;
      }
    }
    if (el.evmOverallCount) {
      el.evmOverallCount.textContent = `${selected} / ${total} Selected`;
    }

    // 3. Next button
    if (el.evmNextBtn) {
      const isLastPostInHouse = state.currentPostIdx >= roles.length - 1;
      const isLastHouse = state.currentHouseIdx >= houses.length - 1;

      const hAccent = currentHouse.accent || "#059669";
      const hHover = currentHouse.accentHover || currentHouse.hover || hAccent;
      const hOnAccent = currentHouse.onAccent || "#ffffff";
      el.evmNextBtn.style.background = hAccent;
      el.evmNextBtn.style.color = hOnAccent;
      el.evmNextBtn.style.boxShadow = `0 4px 0 ${hHover}`;

      if (!isLastPostInHouse) {
        const nextRole = roles[state.currentPostIdx + 1];
        el.evmNextBtn.innerHTML = `Next: ${nextRole.shortTitle || nextRole.title} &rarr;`;
      } else if (!isLastHouse) {
        const nextHouse = houses[state.currentHouseIdx + 1];
        el.evmNextBtn.innerHTML = `Next House: ${nextHouse.shortName || nextHouse.name} &rarr;`;
      } else {
        el.evmNextBtn.innerHTML = `Review &amp; Cast Ballot &rarr;`;
      }
    }
  }

  function renderEvmReviewGrid() {
    if (!el.evmReviewGrid) return;
    el.evmReviewGrid.innerHTML = "";

    const { selected, total } = countTotalProgress();
    if (el.evmFinalCastBtn) {
      const canCast = selected >= total && total > 0;
      el.evmFinalCastBtn.disabled = !canCast;
      el.evmFinalCastBtn.innerHTML = canCast
        ? `<span>Confirm &amp; Cast Universal Ballot (${selected}/${total}) &rarr;</span>`
        : `<span>Select All Roles (${selected}/${total}) to Cast</span>`;
    }

    houses.forEach((h, hIdx) => {
      (h.positions || []).forEach((r, pIdx) => {
        const rk = `${h.code}_${r.id}`;
        const picked = state.selectedByRole[rk] || (state.votedRolesMap[rk] ? { candidate: { fullName: state.votedRolesMap[rk].candidateName } } : null);

        const card = document.createElement("div");
        card.className = `evm-review-card${picked ? " is-filled" : ""}`;
        card.style.cursor = "pointer";
        card.title = "Click to jump to this role";

        const photoHtml = picked?.candidate?.photoPath || picked?.candidate?.photoUrl
          ? `<img src="${picked.candidate.photoPath || picked.candidate.photoUrl}" alt="${picked.candidate.fullName}" />`
          : `<span>${getInitials(picked?.candidate?.fullName || "?")}</span>`;

        card.innerHTML = `
          <div class="evm-review-avatar" style="background:${h.accent}15; color:${h.accentText || h.accent};">${photoHtml}</div>
          <div class="evm-review-info">
            <p class="evm-review-role" style="color:${h.accentText || h.accent};">${h.shortName || h.name} · ${r.shortTitle || r.title}</p>
            <h4 class="evm-review-cand">${picked ? picked.candidate.fullName : "<span style='color:#ef4444; font-weight:600;'>Not Selected</span>"}</h4>
          </div>
        `;

        card.addEventListener("click", () => {
          state.currentHouseIdx = hIdx;
          state.currentPostIdx = pIdx;
          state.isReviewActive = false;
          renderEvmView();
        });

        el.evmReviewGrid.appendChild(card);
      });
    });
  }

  // --- Submission & Finalization ---
  async function submitUniversalBallot() {
    if (state.isSubmitting) return;
    state.isSubmitting = true;

    try {
      if (el.proceedCastBtn) {
        el.proceedCastBtn.disabled = true;
        el.proceedCastBtn.innerHTML = `<span>Recording Universal Ballot...</span>`;
      }
      if (el.evmFinalCastBtn) {
        el.evmFinalCastBtn.disabled = true;
        el.evmFinalCastBtn.innerHTML = `<span>Recording Universal Ballot...</span>`;
      }
      if (el.faceGuardConfirmBtn) {
        el.faceGuardConfirmBtn.disabled = true;
        el.faceGuardConfirmBtn.textContent = "Recording Ballots...";
      }

      showDelayedSpinner("Recording Universal Ballot...", "Saving School Cabinet and House votes to Supabase...");

      const selections = Object.values(state.selectedByRole);
      if (selections.length === 0) {
        throw new Error("No candidate selections found.");
      }

      // Automatically capture snapshot from running webcam in background
      const photoUrl = captureWebcamFrame();
      const currentBooth = (typeof window.getRegisteredBooth === "function" && window.getRegisteredBooth()) || "Teacher Station";

      const res = await window.TeacherBackend.castUniversalBallot({
        teacher: state.verifiedTeacher,
        selections,
        photoDataUrl: photoUrl,
        boothName: currentBooth,
      });

      // Stop any lingering face loops if open
      stopFaceDetectionLoop();
      if (el.faceGuardModal) el.faceGuardModal.hidden = true;

      // Advance to Step 4 (Success)
      el.successSummary.textContent = `Thank you, ${res.teacherName}. All ${res.count} ballots across School Cabinet and student houses have been securely recorded.`;
            const prevVotes = parseInt(sessionStorage.getItem("kiosk_session_votes") || "0", 10);
      sessionStorage.setItem("kiosk_session_votes", String(prevVotes + 1));
      setStep(4);

      // 5-second countdown timer
      let timeLeft = 5;
      if (state.resetInterval) clearInterval(state.resetInterval);
      state.resetInterval = setInterval(() => {
        timeLeft--;
        if (el.resetCountdownText) {
          el.resetCountdownText.innerHTML = `Station resets for next teacher in <strong>${timeLeft}</strong>s`;
        }
        if (timeLeft <= 0) {
          clearInterval(state.resetInterval);
          resetStation();
        }
      }, 1000);
    } catch (err) {
      alert("Error recording ballot: " + err.message);
      if (el.proceedCastBtn) {
        el.proceedCastBtn.disabled = false;
        el.proceedCastBtn.innerHTML = `<span>Confirm &amp; Cast Universal Ballot &rarr;</span>`;
      }
      if (el.evmFinalCastBtn) {
        el.evmFinalCastBtn.disabled = false;
        el.evmFinalCastBtn.innerHTML = `<span>Confirm &amp; Cast Universal Ballot &rarr;</span>`;
      }
      if (el.faceGuardConfirmBtn) {
        el.faceGuardConfirmBtn.disabled = false;
        el.faceGuardConfirmBtn.textContent = "Confirm & Cast Vote";
      }
    } finally {
      hideDelayedSpinner();
      state.isSubmitting = false;
    }
  }

  function resetStation() {
    if (state.resetInterval) clearInterval(state.resetInterval);

    // ── 10-Vote Auto Cache Buster (Stays on this Teacher kiosk with spinning wheel) ──
    const totalVotes = parseInt(sessionStorage.getItem("kiosk_session_votes") || "0", 10);
    const lastBust = parseInt(sessionStorage.getItem("kiosk_last_cache_bust") || "0", 10);
    if (totalVotes > 0 && totalVotes % 10 === 0 && totalVotes !== lastBust) {
      sessionStorage.setItem("kiosk_last_cache_bust", String(totalVotes));
      if (el.loadingOverlayTitle) el.loadingOverlayTitle.textContent = "Refreshing Booth Cache...";
      if (el.loadingOverlaySubtitle) el.loadingOverlaySubtitle.textContent = `${totalVotes} votes recorded · Optimizing booth for next teacher...`;
      if (el.loadingOverlay) el.loadingOverlay.hidden = false;
      setTimeout(() => {
        window.location.replace(window.location.pathname + "?v=" + Date.now());
      }, 700);
      return;
    }
    state.verifiedTeacher = null;
    state.votedRolesMap = {};
    state.selectedByRole = {};
    state.isSubmitting = false;
    state.scannerBuffer = "";
    state.currentHouseIdx = 0;
    state.currentPostIdx = 0;
    state.isReviewActive = false;

    if (el.admissionInput) el.admissionInput.value = "";
    if (el.scannerStreamInput) el.scannerStreamInput.value = "";
    clearError();
    if (el.tabManualMode && el.tabScanMode && el.paneBarcodeScan && el.paneManualEntry) {
      el.tabManualMode.classList.add("is-active");
      el.tabScanMode.classList.remove("is-active");
      el.paneBarcodeScan.hidden = true;
      el.paneManualEntry.hidden = false;
    }
    setStep(1);
  }

  // --- Event Listeners Setup ---
  function initEvents() {
    // Mode tabs
    el.tabScanMode?.addEventListener("click", () => {
      el.tabScanMode.classList.add("is-active");
      el.tabManualMode.classList.remove("is-active");
      el.paneBarcodeScan.hidden = false;
      el.paneManualEntry.hidden = true;
      focusScannerInput();
    });

    el.tabManualMode?.addEventListener("click", () => {
      el.tabManualMode.classList.add("is-active");
      el.tabScanMode.classList.remove("is-active");
      el.paneBarcodeScan.hidden = true;
      el.paneManualEntry.hidden = false;
      el.admissionInput?.focus();
    });

    // Channel 1: Dedicated Invisible Stream Input
    let streamTimer = null;
    if (el.scannerStreamInput) {
      el.scannerStreamInput.addEventListener("input", () => {
        clearTimeout(streamTimer);
        streamTimer = setTimeout(() => {
          const val = el.scannerStreamInput.value.trim();
          if (val.length >= 2) {
            el.scannerStreamInput.value = "";
            handleTeacherIdVerification(val);
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
            handleTeacherIdVerification(val);
          }
        }
      });
    }

    // Channel 2: Tap/Click anywhere on Step 1 restores scanner/input focus
    document.addEventListener("click", (e) => {
      if (state.step === 1) {
        const isInteractive = e.target.closest("button, a, input, select, textarea, [role='button'], video");
        if (!isInteractive) {
          focusScannerInput();
        }
      }
    });
    window.addEventListener("focus", () => {
      if (state.step === 1) focusScannerInput();
    });
    document.addEventListener("visibilitychange", () => {
      if (!document.hidden && state.step === 1) focusScannerInput();
    });

    // Channel 3: Rapid Scanner Detection on Manual Input (Auto-submits if gun used on manual tab)
    let manualBurstTimer = null;
    let manualBurstCount = 0;
    let manualLastTime = 0;
    if (el.admissionInput) {
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
        clearError();
        if (manualBurstCount >= 3) {
          clearTimeout(manualBurstTimer);
          manualBurstTimer = setTimeout(() => {
            const val = el.admissionInput.value.trim();
            if (val.length >= 2) {
              handleTeacherIdVerification(val);
            }
          }, 120);
        }
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
        if (state.scannerBuffer.length >= 2) {
          e.preventDefault();
          const code = state.scannerBuffer.trim();
          state.scannerBuffer = "";
          handleTeacherIdVerification(code);
        }
        state.scannerBuffer = "";
        return;
      }

      if (e.key && e.key.length === 1 && !e.ctrlKey && !e.metaKey && !e.altKey) {
        state.scannerBuffer += e.key;
        clearTimeout(globalBufferTimer);
        globalBufferTimer = setTimeout(() => {
          if (state.scannerBuffer.length >= 2) {
            const code = state.scannerBuffer.trim();
            state.scannerBuffer = "";
            handleTeacherIdVerification(code);
          }
          state.scannerBuffer = "";
        }, 150);
      }
    });

    // Keep scanner stream focused if clicked anywhere on scanner box
    document.querySelector(".scanner-kiosk-box")?.addEventListener("click", focusScannerInput);

    // Manual form submit & button click
    el.admissionForm?.addEventListener("submit", (e) => {
      e.preventDefault();
      const id = el.admissionInput.value.trim();
      handleTeacherIdVerification(id);
    });
    el.verifyBtn?.addEventListener("click", (e) => {
      e.preventDefault();
      const id = el.admissionInput.value.trim();
      handleTeacherIdVerification(id);
    });

    // Navigation buttons
    el.backToStep1Btn?.addEventListener("click", () => setStep(1));
    el.nextToVoteBtn?.addEventListener("click", () => {
      state.currentHouseIdx = 0;
      state.currentPostIdx = 0;
      state.isReviewActive = false;
      renderEvmView();
      setStep(3);
    });
    el.backToStep2Btn?.addEventListener("click", () => setStep(2));

    // EVM Stepper Navigation
    el.evmBackBtn?.addEventListener("click", () => {
      if (state.currentHouseIdx === 0 && state.currentPostIdx === 0) {
        setStep(2);
        return;
      }
      if (state.currentPostIdx > 0) {
        state.currentPostIdx--;
      } else {
        state.currentHouseIdx--;
        const prevHouseRoles = houses[state.currentHouseIdx].positions || [];
        state.currentPostIdx = Math.max(0, prevHouseRoles.length - 1);
      }
      renderEvmView();
    });

    el.evmNextBtn?.addEventListener("click", () => {
      const currentHouse = houses[state.currentHouseIdx];
      const roles = currentHouse?.positions || [];
      if (state.currentPostIdx < roles.length - 1) {
        state.currentPostIdx++;
        renderEvmView();
      } else if (state.currentHouseIdx < houses.length - 1) {
        state.currentHouseIdx++;
        state.currentPostIdx = 0;
        renderEvmView();
      } else {
        state.isReviewActive = true;
        renderEvmView();
      }
    });

    el.evmReviewBackBtn?.addEventListener("click", () => {
      state.isReviewActive = false;
      renderEvmView();
    });

    el.evmFinalCastBtn?.addEventListener("click", () => {
      submitUniversalBallot();
    });

    // Automatically capture photo and cast ballot directly (no face modal interruption)
    el.proceedCastBtn?.addEventListener("click", () => {
      submitUniversalBallot();
    });

    el.faceGuardCancelBtn?.addEventListener("click", () => {
      stopFaceDetectionLoop();
      if (el.faceGuardModal) el.faceGuardModal.hidden = true;
    });

    el.faceGuardConfirmBtn?.addEventListener("click", submitUniversalBallot);

    el.resetNowBtn?.addEventListener("click", resetStation);

    // Fullscreen toggle on title
    document.getElementById("house-title-btn")?.addEventListener("click", () => {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(() => {});
      } else {
        document.exitFullscreen().catch(() => {});
      }
    });

    // Sync registered station name
    if (typeof window.getRegisteredBooth === "function") {
      const bName = window.getRegisteredBooth();
      if (bName && el.boothStationName) {
        el.boothStationName.textContent = bName;
      }
    }
  }

  // Initialize
  document.addEventListener("DOMContentLoaded", async () => {
    initEvents();
    if (el.tabManualMode && el.tabScanMode && el.paneBarcodeScan && el.paneManualEntry) {
      el.tabManualMode.classList.add("is-active");
      el.tabScanMode.classList.remove("is-active");
      el.paneBarcodeScan.hidden = true;
      el.paneManualEntry.hidden = false;
    }
    setStep(1);
    warmUpCamera().catch(() => {});
    document.addEventListener("click", () => warmUpCamera().catch(() => {}), { once: true });
    function syncTeacherCloudStatus(m) {
      const noteSpan = document.querySelector(".auth-security-note span");
      if (noteSpan) {
        if (m === "supabase") {
          noteSpan.textContent = "Supabase connected — all votes & photos save strictly to Supabase.";
        } else {
          noteSpan.textContent = "Supabase NOT connected — connect Supabase in Admin Dashboard to sync.";
        }
      }
      const noteEl = document.getElementById("cloud-mode-note");
      if (noteEl) {
        noteEl.hidden = false;
        if (m === "supabase") {
          noteEl.className = "cloud-status-note is-connected";
          noteEl.innerHTML = `<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#16a34a;margin-right:4px;"></span> Supabase connected — all votes &amp; photos save strictly to Supabase.`;
        } else {
          noteEl.className = "cloud-status-note is-disconnected";
          noteEl.innerHTML = `<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#dc2626;margin-right:4px;"></span> Supabase NOT connected — connect Supabase in Admin Dashboard to sync.`;
        }
      }
    }
    const mode = await window.TeacherBackend.init();
    syncTeacherCloudStatus(mode);
    window.addEventListener("storage", async (e) => {
      if (e.key === "election_spr_2026_sb_cfg_v1" || e.key === "spr_supabase_direct_cfg_v1") {
        if (window.TeacherBackend && typeof window.TeacherBackend.init === "function") {
          window.TeacherBackend._initPromise = null;
          const freshMode = await window.TeacherBackend.init();
          syncTeacherCloudStatus(freshMode);
        }
      }
    });
    loadPicoFaceClassifier();
  });
})();

