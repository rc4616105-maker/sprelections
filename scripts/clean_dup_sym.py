from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent

for slug in ['bheeshma', 'gurudrona', 'hanuman', 'karna', 'vasistha', 'vishwamithra', 'central', 'teachers']:
    p = ROOT / "Houses" / slug / "app.js"
    if not p.exists():
        continue
    text = p.read_text(encoding="utf-8")
    
    # Remove duplicate const sym
    old_line = '          const sym = cand.symbolObj || ELECTION_SYMBOLS[candIdx % ELECTION_SYMBOLS.length];\n'
    if old_line in text:
        text = text.replace(old_line, '')
        print(f" -> Removed duplicate const sym in Houses/{slug}/app.js")
        
    p.write_text(text, encoding="utf-8")

print("Cleaned up duplicate declarations.")
