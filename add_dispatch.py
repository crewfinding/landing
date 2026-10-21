"""Re-adds the dispatch + 3PL section to trucking-logistics/index.html after build_trucking.py rebuilds it.
Run order: build_subpages.py -> build_trucking.py -> add_clips.py -> add_dispatch.py   (idempotent)
Snapshot of the section lives in assets-hf/dispatch-trucking-section.html.
"""
from pathlib import Path
R = Path(__file__).parent
p = R / "trucking-logistics" / "index.html"
h = p.read_text(encoding="utf-8")
CSS = '<link rel="stylesheet" href="../assets/cf.css">'
if "cf-dispatch.css" not in h:
    h = h.replace(CSS, CSS + chr(10) + '<link rel="stylesheet" href="../assets/cf-dispatch.css">', 1)
if "cf-dispatch.js" not in h:
    h = h.replace("</body>", '<script src="../assets/cf-dispatch.js" defer></script>' + chr(10) + "</body>", 1)
if 'id="dispatch"' not in h:
    sec = (R / "assets-hf" / "dispatch-trucking-section.html").read_text(encoding="utf-8")
    DAY = '<section class="day band-ivory on-light round-top">'
    h = h.replace(DAY, sec + chr(10) + DAY, 1)
p.write_text(h, encoding="utf-8")
print("dispatch section present:", 'id="dispatch"' in h)
