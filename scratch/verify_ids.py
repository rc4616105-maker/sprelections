houses = ['bheeshma', 'central', 'gurudrona', 'hanuman', 'karna', 'vasistha', 'vishwamithra']

needed_ids = [
    "step-1", "step-2", "step-3", "step-4",
    "admission-form", "admission-input", "verify-btn",
    "step1-error", "step1-error-title", "step1-error-msg",
    "tab-scan-mode", "tab-manual-mode", "pane-barcode-scan", "pane-manual-entry",
    "barcode-scanner-stream", "auto-cam-status",
    "camera-video", "camera-canvas",
    "back-to-step1-btn", "next-to-vote-btn",
    "step3-subtitle", "candidateGrid", "candidate-grid",
    "cast-action-bar", "selected-progress-label", "selected-candidate-name", "cast-vote-btn",
    "step3-error", "step3-error-msg", "back-to-step2-btn",
    "face-guard-modal", "face-guard-badge", "face-guard-title", "face-guard-desc",
    "face-live-video", "face-oval-guide", "face-live-status-pill", "face-status-label",
    "face-guard-cancel-btn", "face-guard-confirm-btn",
    "success-summary", "reset-now-btn"
]

for h in houses:
    with open(f'Houses/{h}/index.html', 'r', encoding='utf-8') as f:
        html = f.read()
    missing = []
    for nid in needed_ids:
        if f'id="{nid}"' not in html and f"id='{nid}'" not in html:
            if nid != "candidateGrid": # candidate-grid is the actual id
                missing.append(nid)
    print(f"{h}: missing IDs = {missing}")
