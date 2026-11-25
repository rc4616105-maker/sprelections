import re

houses = ['bheeshma', 'gurudrona', 'hanuman', 'karna', 'vasistha', 'vishwamithra']

old_block = """  if (el.evmIndicators) {
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
  }"""

new_block = """  if (el.evmIndicators) {
    el.evmIndicators.forEach((pill, idx) => {
      pill.addEventListener("click", () => {
        const posList = getPositionsList();
        if (idx > state.evmPostIndex) {
          const curPos = posList[state.evmPostIndex];
          if (curPos && !state.selectedByRole[curPos.id] && !state.votedRoles[curPos.id]) {
            alert("This post is empty! Please select a candidate for " + curPos.title + " before moving ahead.");
            return;
          }
          const missingBefore = posList.slice(0, idx).find((p) => !state.selectedByRole[p.id] && !state.votedRoles[p.id]);
          if (missingBefore) {
            alert("Cannot skip: " + missingBefore.title + " is empty! Please vote for " + missingBefore.title + " first.");
            return;
          }
        }
        if (idx < posList.length) {
          state.evmPostIndex = idx;
          renderEvmView();
        } else if (idx === posList.length) {
          const missingAny = posList.find((p) => !state.selectedByRole[p.id] && !state.votedRoles[p.id]);
          if (missingAny) {
            alert("Cannot go to Review & Cast: " + missingAny.title + " is empty! Please vote for all posts first.");
            return;
          }
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
      }
    });
  }

  if (el.evmNextBtn) {
    el.evmNextBtn.addEventListener("click", () => {
      const posList = getPositionsList();
      const curPos = posList[state.evmPostIndex];
      if (curPos && !state.selectedByRole[curPos.id] && !state.votedRoles[curPos.id]) {
        alert("This post is empty! Please select a candidate for " + curPos.title + " before moving to the next post.");
        return;
      }
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
      const posList = getPositionsList();
      const missingPos = posList.filter((p) => !state.selectedByRole[p.id] && !state.votedRoles[p.id]);
      if (missingPos.length > 0) {
        const missingNames = missingPos.map((p) => p.title).join(", ");
        alert("Cannot cast ballot: This post is empty!\\n\\nMissing vote for: " + missingNames + ".\\n\\nPlease select a candidate for all posts before submitting.");
        const firstMissingIdx = posList.findIndex((p) => !state.selectedByRole[p.id] && !state.votedRoles[p.id]);
        if (firstMissingIdx !== -1) {
          state.evmPostIndex = firstMissingIdx;
          renderEvmView();
        }
        return;
      }
      if (el.castVoteBtn) {
        el.castVoteBtn.click();
      }
    });
  }"""

for h in houses:
    p = f'Houses/{h}/app.js'
    with open(p, 'r', encoding='utf-8') as f:
        c = f.read()
    
    if old_block in c:
        c = c.replace(old_block, new_block)
        # Also ensure castVoteBtn alerts on missing posts
        c = c.replace(
            'el.step3ErrorMsg.textContent = `Please select a candidate for: ${missingNames}.`;\n        el.step3Error.hidden = false;\n      }\n      return;',
            'el.step3ErrorMsg.textContent = `Please select a candidate for: ${missingNames}.`;\n        el.step3Error.hidden = false;\n        alert("Cannot cast ballot: This post is empty!\\n\\nMissing vote for: " + missingNames + ".\\n\\nPlease select a candidate for all posts before submitting.");\n      }\n      return;'
        )
        with open(p, 'w', encoding='utf-8') as f:
            f.write(c)
        print(f"Updated navigation guard in {h}")
    else:
        print(f"Could not find exact block in {h}")
