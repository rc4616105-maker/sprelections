from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent

# 1. Update Houses/admin/styles.css
css_path = ROOT / "Houses" / "admin" / "styles.css"
css = css_path.read_text(encoding="utf-8")

SPHERE_CSS = '''
/* 3D Sphere for Vasistha House (Rose Pink) */
.sphere-pink {
  display: inline-block;
  width: 13px;
  height: 13px;
  border-radius: 50%;
  background: radial-gradient(circle at 35% 35%, #fbcfe8 0%, #f472b6 30%, #db2777 70%, #9d174d 100%);
  box-shadow: inset -1px -1px 2px rgba(0, 0, 0, 0.3), 0 1px 2px rgba(0, 0, 0, 0.12);
  vertical-align: middle;
  margin-right: 4px;
}
'''

if ".sphere-pink" not in css:
    css += "\n" + SPHERE_CSS
    css_path.write_text(css, encoding="utf-8")
    print("Added .sphere-pink to styles.css!")

# 2. Update Houses/admin/edit-votes.html
ev_html_path = ROOT / "Houses" / "admin" / "edit-votes.html"
html = ev_html_path.read_text(encoding="utf-8")

# Replace 🌸 Vasistha with sphere icon
svg_sphere = '<span class="sphere-pink" aria-hidden="true"></span>Vasistha'
html = html.replace('<span>🌸 Vasistha</span>', f'<span>{svg_sphere}</span>')
html = html.replace('🌸 Vasistha', f'{svg_sphere}')

# Bump cachebusters to 20261122r
html = re.sub(r'(\./edit-votes\.js\?v=)[^"]*', r'\g<1>20261122r', html)
html = re.sub(r'(\./supabase-config\.js\?v=)[^"]*', r'\g<1>20261122r', html)
html = re.sub(r'(\./styles\.css\?v=)[^"]*', r'\g<1>20261122r', html)
ev_html_path.write_text(html, encoding="utf-8")
print("Updated Houses/admin/edit-votes.html with sphere for Vasistha!")

# Also bump index.html cachebuster
idx_path = ROOT / "Houses" / "admin" / "index.html"
idx_html = idx_path.read_text(encoding="utf-8")
idx_html = re.sub(r'(\./styles\.css\?v=)[^"]*', r'\g<1>20261122r', idx_html)
idx_path.write_text(idx_html, encoding="utf-8")
print("Updated Houses/admin/index.html!")
