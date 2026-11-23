import glob

files = [
    "Houses/bheeshma/app.js",
    "Houses/gurudrona/app.js",
    "Houses/hanuman/app.js",
    "Houses/karna/app.js",
    "Houses/vasistha/app.js",
    "Houses/vishwamithra/app.js",
    "Houses/central/app.js",
]

target = """    try {
      if (!window.ElectionBackend || typeof window.ElectionBackend.init !== "function") {
        showStep1Error("System Initializing", "Kiosk database is preparing. Please try again in a moment.");
        stopDelayedSpinner();
        if (el.verifyBtn) el.verifyBtn.disabled = false;
        return;
      }
      await window.ElectionBackend.init();"""

for f in files:
    txt = open(f, encoding="utf-8").read()
    if 'await window.ElectionBackend.init();' in txt:
        # replace the plain call
        old_pattern = '    try {\n      await window.ElectionBackend.init();'
        if old_pattern in txt:
            new_txt = txt.replace(old_pattern, target)
            with open(f, "w", encoding="utf-8") as out:
                out.write(new_txt)
            print(f"Added safe ElectionBackend guard to {f}")
        else:
            print(f"Pattern variation in {f}")
