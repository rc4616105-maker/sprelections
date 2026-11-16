# Read the full snippet of renderOverview from step 7268 output file
with open('C:/Users/Abhinav/.gemini/antigravity/brain/44e72ab9-3bd0-4ded-96fa-40285707e196/.system_generated/steps/7268/output.txt', 'r', encoding='utf-8') as f:
    orig = f.read()

# Extract from 'function renderOverview(snap) {' to 'el.drilldownTbody.appendChild(tr);\n      });\n      return;\n    }\n  }'
idx_start = orig.find('function renderOverview(snap) {')
idx_end = orig.find('el.kpiButtons.forEach((btn) => {')

overview_code = orig[idx_start:idx_end]

# Read current admin/app.js
with open('Houses/admin/app.js', 'r', encoding='utf-8') as f:
    cur = f.read()

# Replace in cur: find where renderDrilldown ends (around line 557)
idx_rd_end = cur.find('      return;\n    }\n  }')
if idx_rd_end != -1:
    before = cur[:idx_rd_end + len('      return;\n    }\n  }')]
    after = cur[cur.find('el.kpiButtons.forEach((btn) => {'):]
    
    # In overview_code, ensure cancelled KPI displays unique voters
    overview_code = overview_code.replace(
        'const cancelled = snap.ballots.filter((b) => b.status === "cancelled").length;',
        'const cancelledBallotsAll = snap.ballots.filter((b) => b.status === "cancelled");\n    const cancelledVotersCount = new Set(cancelledBallotsAll.map((b) => b.admissionNo)).size;'
    )
    overview_code = overview_code.replace(
        'el.kpiCancelled.textContent = String(cancelled);',
        'el.kpiCancelled.textContent = String(cancelledVotersCount);'
    )

    final_code = before + "\n\n  " + overview_code + "\n  " + after
    with open('Houses/admin/app.js', 'w', encoding='utf-8') as f:
        f.write(final_code)
    print("Reassembled Houses/admin/app.js successfully!")
else:
    print("Could not find rd_end in cur")
