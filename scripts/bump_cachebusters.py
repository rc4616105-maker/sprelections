import re, glob
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
v = "20261123RR"

count = 0
targets = glob.glob(str(ROOT / "Houses" / "**" / "*.html"), recursive=True) + glob.glob(str(ROOT / "Result declaration" / "**" / "*.html"), recursive=True)

for html_file in targets:
    txt = open(html_file, "r", encoding="utf-8").read()
    new_txt = re.sub(r'data\.js(\?v=[^"\'\s>]+)?', f'data.js?v={v}', txt)
    new_txt = re.sub(r'app\.js(\?v=[^"\'\s>]+)?', f'app.js?v={v}', new_txt)
    new_txt = re.sub(r'house\.js(\?v=[^"\'\s>]+)?', f'house.js?v={v}', new_txt)
    new_txt = re.sub(r'styles\.css(\?v=[^"\'\s>]+)?', f'styles.css?v={v}', new_txt)
    new_txt = re.sub(r'wheel\.js(\?v=[^"\'\s>]+)?', f'wheel.js?v={v}', new_txt)
    new_txt = re.sub(r'scratch\.js(\?v=[^"\'\s>]+)?', f'scratch.js?v={v}', new_txt)
    new_txt = re.sub(r'supabase-sync\.js(\?v=[^"\'\s>]+)?', f'supabase-sync.js?v={v}', new_txt)
    new_txt = re.sub(r'candidates-data\.js(\?v=[^"\'\s>]+)?', f'candidates-data.js?v={v}', new_txt)
    new_txt = re.sub(r'candidates-modal\.js(\?v=[^"\'\s>]+)?', f'candidates-modal.js?v={v}', new_txt)
    new_txt = re.sub(r'all-candidates\.js(\?v=[^"\'\s>]+)?', f'all-candidates.js?v={v}', new_txt)
    if new_txt != txt:
        open(html_file, "w", encoding="utf-8").write(new_txt)
        count += 1
        print(f"Updated {Path(html_file).name} with v={v}")

print(f"Bumped cachebusters in {count} HTML files to v={v}")
