// Teacher Universal Polling Booth — 5-Step Progressive Controller
// Allows teachers to vote for School Cabinet (5 roles) + All 6 Student Houses (24 roles) in one unified flow.
(function () {
  const { houses, candidates, electionId } = window.TEACHER_BOOTH_DATA || { houses: [], candidates: [] };
  const totalAvailableRoles = houses.reduce((sum, h) => sum + (h.positions?.length || 0), 0);

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
    ballotContainer: document.getElementById("universal-ballot-container"),
    stickyCastBar: document.getElementById("sticky-cast-bar"),
    stickyProgressCount: document.getElementById("sticky-progress-count"),
    stickyProgressFill: document.getElementById("sticky-progress-fill"),
    proceedCastBtn: document.getElementById("proceed-cast-btn"),
    backToStep2Btn: document.getElementById("back-to-step2-btn"),

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
    }

    if (stepNum === 3) {
      if (el.stickyCastBar) el.stickyCastBar.hidden = false;
      window.scrollTo({ top: 0, behavior: "smooth" });
    } else {
      if (el.stickyCastBar) el.stickyCastBar.hidden = true;
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

  // --- Step 3 Ballot Rendering ---
  function renderAllHousesBallot() {
    if (!el.houseTabsBar || !el.ballotContainer) return;

    el.houseTabsBar.innerHTML = "";
    el.ballotContainer.innerHTML = "";

    houses.forEach((house, hIdx) => {
      const houseCode = house.code;
      const houseRoles = house.positions || [];

      // 1. Create Navigation Tab Pill
      const tabChip = document.createElement("button");
      tabChip.type = "button";
      tabChip.className = "house-tab-chip";
      tabChip.id = `tab-chip-${houseCode}`;
      tabChip.style.setProperty("--accent-chip", house.accent);
      if (hIdx === 0) tabChip.classList.add("is-active");

      tabChip.innerHTML = `
        <span>${house.shortName || house.name}</span>
        <span class="tab-badge" id="tab-count-${houseCode}">0/${houseRoles.length}</span>
      `;
      tabChip.addEventListener("click", () => {
        document.querySelectorAll(".house-tab-chip").forEach((c) => c.classList.remove("is-active"));
        tabChip.classList.add("is-active");
        const sec = document.getElementById(`house-sec-${houseCode}`);
        if (sec) sec.scrollIntoView({ behavior: "smooth", block: "start" });
      });
      el.houseTabsBar.appendChild(tabChip);

      // 2. Create House Ballot Section
      const sec = document.createElement("section");
      sec.className = "house-ballot-section";
      sec.id = `house-sec-${houseCode}`;
      sec.style.borderLeftColor = house.accent;

      const candsForHouse = candidates.filter((c) => c.houseCode === houseCode && c.isApproved);

      let rolesHtml = "";
      houseRoles.forEach((role) => {
        const roleKey = `${houseCode}_${role.id}`;
        const roleCands = candsForHouse.filter((c) => c.positionId === role.id);
        const alreadyVoted = state.votedRolesMap[roleKey];

        let cardsHtml = "";
        if (alreadyVoted) {
          cardsHtml = `
            <div style="background:#f0fdf4; border:1.5px solid #86efac; border-radius:12px; padding:0.9rem 1.25rem; color:#166534; font-weight:700;">
              ✓ You have already voted for <strong>${alreadyVoted.candidateName}</strong> in this position.
            </div>
          `;
        } else if (roleCands.length === 0) {
          cardsHtml = `<p style="color:var(--text-muted); font-size:0.9rem;">No candidates registered for this role.</p>`;
        } else {
          cardsHtml = `
            <div class="candidate-selection-grid">
              ${roleCands
                .map((cand) => {
                  const isSelected = state.selectedByRole[roleKey]?.id === cand.id;
                  return `
                    <button
                      type="button"
                      class="candidate-card-btn ${isSelected ? "is-selected" : ""}"
                      data-role-key="${roleKey}"
                      data-cand-id="${cand.id}"
                      data-house-code="${houseCode}"
                      data-pos-id="${role.id}"
                      data-pos-name="${role.title}"
                    >
                      <div class="cand-check-indicator">✓</div>
                      <h4 class="cand-name">${cand.fullName}</h4>
                      <div class="cand-meta">${cand.className ? `Class ${cand.className}` : ""}${cand.section ? `-${cand.section}` : ""}</div>
                      ${cand.tagline ? `<div class="cand-tagline">&ldquo;${cand.tagline}&rdquo;</div>` : ""}
                    </button>
                  `;
                })
                .join("")}
            </div>
          `;
        }

        rolesHtml += `
          <div class="role-block">
            <h3 class="role-block-title">
              <span>${role.title}</span>
              <span class="role-subtitle">· ${role.subtitle || ""}</span>
            </h3>
            ${cardsHtml}
          </div>
        `;
      });

      sec.innerHTML = `
        <div class="house-ballot-header">
          <div style="display:flex; align-items:center; gap:0.6rem;">
            <h2 class="house-ballot-title" style="color:${house.accent};">${house.name}</h2>
          </div>
          <span class="house-badge-pill" style="color:${house.accent}; border-color:${house.accent};">${house.badge || "House Candidates"}</span>
        </div>
        <div class="roles-container">
          ${rolesHtml}
        </div>
      `;

      el.ballotContainer.appendChild(sec);
    });

    // Attach click handlers to candidate selection cards
    el.ballotContainer.querySelectorAll(".candidate-card-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const roleKey = btn.dataset.roleKey;
        const candId = btn.dataset.candId;
        const houseCode = btn.dataset.houseCode;
        const posId = btn.dataset.posId;
        const posName = btn.dataset.posName;

        const cand = candidates.find((c) => c.id === candId);
        if (!cand) return;

        // Deselect previous in this role
        el.ballotContainer.querySelectorAll(`.candidate-card-btn[data-role-key="${roleKey}"]`).forEach((b) => {
          b.classList.remove("is-selected");
        });

        // Select clicked card
        btn.classList.add("is-selected");
        state.selectedByRole[roleKey] = {
          houseCode,
          positionId: posId,
          positionName: posName,
          candidate: cand,
        };

        updateProgressUI();
      });
    });

    updateProgressUI();
  }

  function updateProgressUI() {
    let totalSelected = 0;
    let totalNeeded = 0;

    houses.forEach((house) => {
      const houseCode = house.code;
      const roles = house.positions || [];
      let houseSelected = 0;

      roles.forEach((r) => {
        const rk = `${houseCode}_${r.id}`;
        totalNeeded++;
        if (state.selectedByRole[rk] || state.votedRolesMap[rk]) {
          houseSelected++;
          totalSelected++;
        }
      });

      const tabBadge = document.getElementById(`tab-count-${houseCode}`);
      const tabChip = document.getElementById(`tab-chip-${houseCode}`);
      if (tabBadge && tabChip) {
        tabBadge.textContent = `${houseSelected}/${roles.length}`;
        const isHouseDone = houseSelected >= roles.length && roles.length > 0;
        tabChip.classList.toggle("is-complete", isHouseDone);
        if (isHouseDone) {
          tabBadge.textContent = `✓ ${houseSelected}/${roles.length}`;
        }
      }
    });

    if (el.stickyProgressCount) {
      el.stickyProgressCount.textContent = `${totalSelected} / ${totalNeeded} Roles Selected`;
    }
    if (el.stickyProgressFill) {
      const pct = totalNeeded ? Math.round((totalSelected / totalNeeded) * 100) : 0;
      el.stickyProgressFill.style.width = `${pct}%`;
    }

    if (el.proceedCastBtn) {
      const isComplete = totalSelected >= totalNeeded && totalNeeded > 0;
      el.proceedCastBtn.disabled = !isComplete;
      el.proceedCastBtn.innerHTML = isComplete
        ? `<span>Confirm &amp; Cast Universal Ballot (${totalSelected}/${totalNeeded}) &rarr;</span>`
        : `<span>Select All Roles (${totalSelected}/${totalNeeded})</span>`;
    }
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
    state.verifiedTeacher = null;
    state.votedRolesMap = {};
    state.selectedByRole = {};
    state.isSubmitting = false;
    state.scannerBuffer = "";

    if (el.admissionInput) el.admissionInput.value = "";
    if (el.scannerStreamInput) el.scannerStreamInput.value = "";
    clearError();
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

    // Manual form submit
    el.admissionForm?.addEventListener("submit", (e) => {
      e.preventDefault();
      const id = el.admissionInput.value.trim();
      handleTeacherIdVerification(id);
    });

    // Navigation buttons
    el.backToStep1Btn?.addEventListener("click", () => setStep(1));
    el.nextToVoteBtn?.addEventListener("click", () => {
      renderAllHousesBallot();
      setStep(3);
    });
    el.backToStep2Btn?.addEventListener("click", () => setStep(2));

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
    setStep(1);
    warmUpCamera().catch(() => {});
    document.addEventListener("click", () => warmUpCamera().catch(() => {}), { once: true });
    const mode = await window.TeacherBackend.init();
    const noteSpan = document.querySelector(".auth-security-note span");
    if (noteSpan) {
      if (mode === "supabase") {
        noteSpan.textContent = "Supabase connected — all votes & photos save strictly to Supabase.";
      } else {
        noteSpan.textContent = "Supabase NOT connected — connect Supabase in Admin Dashboard to sync.";
      }
    }
    loadPicoFaceClassifier();
  });
})();

