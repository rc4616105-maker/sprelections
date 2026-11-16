import re

houses = ['bheeshma', 'central', 'gurudrona', 'hanuman', 'karna', 'vasistha', 'vishwamithra']

NEW_FACE_GUARD_BLOCK = """  let noCamFallbackTimer = null;

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
  }"""

NEW_CAST_VOTE_BLOCK = """  el.castVoteBtn.addEventListener("click", async () => {
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
  });"""

for h in houses:
    path = f'Houses/{h}/app.js'
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    
    # Replace openFaceGuardModal up to submitFinalVote
    start_fg = c.find('function openFaceGuardModal(')
    end_fg = c.find('async function submitFinalVote(', start_fg)
    if start_fg != -1 and end_fg != -1:
        c = c[:start_fg] + NEW_FACE_GUARD_BLOCK + "\n\n  " + c[end_fg:]
    else:
        print(f"FAILED to find face guard block in {h}")

    # Replace castVoteBtn listener
    start_cv = c.find('el.castVoteBtn.addEventListener("click"')
    end_cv = c.find('el.resetNowBtn.addEventListener(', start_cv)
    if start_cv != -1 and end_cv != -1:
        c = c[:start_cv] + NEW_CAST_VOTE_BLOCK + "\n\n  " + c[end_cv:]
    else:
        print(f"FAILED to find castVoteBtn block in {h}")

    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)
    print(f"Updated {h}/app.js successfully!")

    # Now update index.html script version tags
    html_path = f'Houses/{h}/index.html'
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    html = re.sub(r'booth-session\.js\?v=\d+', 'booth-session.js?v=995', html)
    html = re.sub(r'pico\.js\?v=\d+', 'pico.js?v=995', html)
    html = re.sub(r'data\.js\?v=\d+', 'data.js?v=995', html)
    html = re.sub(r'supabase-config\.js\?v=\d+', 'supabase-config.js?v=995', html)
    html = re.sub(r'app\.js\?v=\d+', 'app.js?v=995', html)
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Updated {h}/index.html with ?v=995!")
