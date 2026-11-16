with open('Houses/hanuman/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's inspect openFaceGuardModal and closeFaceGuardModal in hanuman/app.js
idx = text.find('function openFaceGuardModal')
idx_end = text.find('async function submitFinalVote', idx)
print("=== Current openFaceGuardModal ===")
print(text[idx:idx_end])

# Let's inspect castVoteBtn in hanuman/app.js
idx2 = text.find('el.castVoteBtn.addEventListener')
idx2_end = text.find('el.resetNowBtn.addEventListener', idx2)
print("=== Current castVoteBtn listener ===")
print(text[idx2:idx2_end])
