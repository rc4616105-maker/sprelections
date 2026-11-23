import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
graphs_path = ROOT / "Houses" / "graphs.html"
html = graphs_path.read_text(encoding="utf-8")

# 1. Remove graph-legend-badge HTML
old_legend_html = '''        <div class="graph-legend-badge">
          <span class="legend-entry">
            <span class="legend-bar-sample" style="background: #475569;"></span>
            <span>👦 Boys Bar (Solid House Color)</span>
          </span>
          <span class="legend-entry">
            <span class="legend-bar-sample" style="background: linear-gradient(180deg, #ffffff 0%, #475569 85%); border:1px solid #475569;"></span>
            <span>👧 Girls Bar (Light Gradient House Color)</span>
          </span>
        </div>'''

# Also try regex for legend removal in case of mojibake
html = re.sub(r'<div class="graph-legend-badge">.*?</div>', '', html, flags=re.DOTALL)

# 2. In clusterCol.innerHTML: replace emojis with small text 'Boys' and 'Girls'
html = re.sub(r'<span class="bar-gender-badge">[^<]*</span>', '', html) # remove any existing badge
# Now let's update the bar-stat-label templates in initNodes
old_unit_boys = '''              <!-- Boys Bar Unit -->
              <div class="single-bar-unit unit-boys" title="${h.name} Boys">
                <div class="bar-stat-label label-boys">
                  <span class="b-fraction">0 / 0</span>
                  <span class="bar-stat-pct b-pct">0%</span>
                </div>'''

# Let's replace the whole initNodes innerHTML template cleanly
old_cluster_inner = re.search(r'clusterCol\.innerHTML = `(.*?)`;', html, re.DOTALL)
if old_cluster_inner:
    new_cluster_inner = '''clusterCol.innerHTML = `
            <div class="bars-pair-container">
              <!-- Boys Bar Unit -->
              <div class="single-bar-unit unit-boys" title="${h.name} Boys">
                <div class="bar-stat-label label-boys">
                  <span class="bar-gender-txt">Boys</span>
                  <span class="b-fraction">0 / 0</span>
                  <span class="bar-stat-pct b-pct">0%</span>
                </div>
                <div class="bar-track">
                  <div class="bar-fill bar-fill-boys" style="background: ${h.accent}; --bar-scale: 0; --bar-opacity: 0.28;"></div>
                </div>
              </div>

              <!-- Girls Bar Unit -->
              <div class="single-bar-unit unit-girls" title="${h.name} Girls">
                <div class="bar-stat-label label-girls">
                  <span class="bar-gender-txt">Girls</span>
                  <span class="g-fraction">0 / 0</span>
                  <span class="bar-stat-pct g-pct">0%</span>
                </div>
                <div class="bar-track">
                  <div class="bar-fill bar-fill-girls" style="background: linear-gradient(180deg, #ffffff 0%, ${h.accent} 78%); border: 1.5px solid ${h.accent}; --bar-scale: 0; --bar-opacity: 0.28;"></div>
                </div>
              </div>
            </div>
          `;'''
    html = html.replace(old_cluster_inner.group(0), new_cluster_inner)

# 3. Remove sub-sublabel below house name in labelCol.innerHTML
old_label_inner = re.search(r'labelCol\.innerHTML = `(.*?)`;', html, re.DOTALL)
if old_label_inner:
    new_label_inner = '''labelCol.innerHTML = `
            <span class="house-label-name" style="color: ${h.accentText};">${h.name}</span>
            <span class="house-total-badge total-badge">0 / 0 Total</span>
          `;'''
    html = html.replace(old_label_inner.group(0), new_label_inner)

# 4. Clean up KPI cards: remove emojis from label
html = html.replace('👦 Boys Turnout', 'Boys Turnout')
html = html.replace('👧 Girls Turnout', 'Girls Turnout')

# 5. Add .bar-gender-txt CSS
if '.bar-gender-txt' not in html:
    html = html.replace('.bar-stat-label {', '''.bar-gender-txt {
      font-size: 0.7rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      display: block;
      margin-bottom: 2px;
    }

    .bar-stat-label {''')

# 6. Bump cachebusters
html = re.sub(r'(\./admin/data\.js\?v=)[^"]*', r'\g<1>20261122t', html)
html = re.sub(r'(\./admin/teachers\.js\?v=)[^"]*', r'\g<1>20261122t', html)
html = re.sub(r'(\./admin/supabase-config\.js\?v=)[^"]*', r'\g<1>20261122t', html)

graphs_path.write_text(html, encoding="utf-8")
print("Updated Houses/graphs.html successfully!")
