from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ev_path = ROOT / "Houses" / "admin" / "edit-votes.js"
text = ev_path.read_text(encoding="utf-8")

replacements = [
    ('â ³', '⏳'),
    ('âœ“', '✓'),
    ('ðŸ’¾', '💾'),
    ('ðŸ—³ï¸ ', '🗳️'),
    ('âœ¨', '📋'),
    ('ðŸ“‹', '📋'),
    ('ðŸ—‘ï¸ ', '🗑️'),
]

for bad, good in replacements:
    text = text.replace(bad, good)

ev_path.write_text(text, encoding="utf-8")
print("Cleaned up mojibake in edit-votes.js successfully!")
