import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'dashboard_executive.html'
DEST_ASSETS = ROOT / 'deploy_vercel_dist' / 'assets'
DEST_ASSETS.mkdir(parents=True, exist_ok=True)

html = SRC.read_text(encoding='utf-8')

# Extract Chart.js block: find the "Chart.js v" marker and the "End inlined Chart.js" marker
chart_start_marker = 'Chart.js v'
end_marker = '/* End inlined Chart.js */'
chart_js = None
if chart_start_marker in html and end_marker in html:
    i = html.find(chart_start_marker)
    # walk backwards to the <script> start
    script_open = html.rfind('<script', 0, i)
    if script_open != -1:
        script_close = html.find('</script>', i)
        if script_close != -1:
            # extract content between the first > after <script and </script>
            gt = html.find('>', script_open)
            chart_js = html[gt+1:script_close]

if chart_js:
    (DEST_ASSETS / 'chart.full.js').write_text(chart_js, encoding='utf-8')
    print('Wrote chart.full.js')
else:
    print('Chart.js block not found')

# Extract window.DASH_DATA JSON by finding "window.DASH_DATA" and parsing braces
m = re.search(r'window\.DASH_DATA\s*=\s*\{', html)
if m:
    start = m.start()
    brace_pos = html.find('{', m.end()-1)
    if brace_pos != -1:
        pos = brace_pos
        depth = 0
        endpos = None
        while pos < len(html):
            ch = html[pos]
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    endpos = pos
                    break
            pos += 1
        if endpos:
            json_text = html[brace_pos:endpos+1]
            out = 'window.DASH_DATA = ' + json_text + ';
'
            (DEST_ASSETS / 'dash_data.js').write_text(out, encoding='utf-8')
            print('Wrote dash_data.js')
        else:
            print('Could not find end of DASH_DATA object')
else:
    print('window.DASH_DATA not found in source')

# Update deploy HTML files to reference local assets
import glob

dist_html_files = list((ROOT / 'deploy_vercel_dist').glob('*.html'))
for h in dist_html_files:
    txt = h.read_text(encoding='utf-8')
    changed = False
    # Replace Plotly CDN with local path
    txt_new = re.sub(r'<script[^>]*src="https://cdn.plot.ly/[^">]+"[^>]*></script>', '<script src="assets/plotly.min.js"></script>', txt)
    if txt_new != txt:
        txt = txt_new
        changed = True
    # Replace inlined Chart.js script tag by local include if present
    if '/* End inlined Chart.js */' in txt:
        # remove the first <script>...</script> that contains Chart.js v
        chart_re = re.compile(r'<script[^>]*>\s*!/\*\!\s*Chart\.js[\s\S]*?End inlined Chart\.js\s*\*/\s*</script>', re.IGNORECASE)
        txt_new = chart_re.sub('<script src="assets/chart.full.js"></script>', txt, count=1)
        if txt_new != txt:
            txt = txt_new
            changed = True
    # Ensure dash_data.js is referenced before other scripts that need it
    if 'assets/dash_data.js' not in txt:
        # insert before closing </head> if exists, else before first script in body
        if '</head>' in txt:
            txt = txt.replace('</head>', '    <script src="assets/dash_data.js"></script>\n</head>')
            changed = True
        else:
            # fallback: prepend at top
            txt = '<script src="assets/dash_data.js"></script>\n' + txt
            changed = True
    if changed:
        h.write_text(txt, encoding='utf-8')
        print(f'Updated {h.name}')

print('Done')
