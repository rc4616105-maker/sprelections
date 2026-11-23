import glob
import re

html_files = [
    'Houses/bheeshma/index.html',
    'Houses/gurudrona/index.html',
    'Houses/hanuman/index.html',
    'Houses/karna/index.html',
    'Houses/vasistha/index.html',
    'Houses/vishwamithra/index.html',
    'Houses/teachers/index.html',
]

note_html = '<p id="cloud-mode-note" class="cloud-status-note is-connected" style="margin-top: 0.85rem; font-size: 0.82rem;"><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#16a34a;margin-right:4px;"></span> Supabase connected — all votes &amp; photos save strictly to Supabase.</p>'

for hf in html_files:
    with open(hf, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'id="cloud-mode-note"' in content:
        # replace existing tag to ensure it is visible and has default connected markup
        content = re.sub(r'<p\s+id="cloud-mode-note"[^>]*>.*?</p>', note_html, content)
        print(f"Updated existing cloud-mode-note in {hf}")
    else:
        # add under step1-error
        if 'id="step1-error"' in content:
            content = content.replace('</div>\n          </div>\n        </div>\n\n        <!-- STEP 2', f'</div>\n          </div>\n          {note_html}\n        </div>\n\n        <!-- STEP 2')
            if 'id="cloud-mode-note"' not in content:
                # fallback for teachers
                content = content.replace('</div>\n          </div>', f'</div>\n          </div>\n          {note_html}', 1)
            print(f"Inserted cloud-mode-note in {hf}")
        else:
            print(f"Warning: could not find step1-error in {hf}")
            
    with open(hf, 'w', encoding='utf-8') as f:
        f.write(content)
