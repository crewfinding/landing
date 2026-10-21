"""Idempotent site patch (re-run after build_subpages.py / build_trucking.py):
 - swap the GPS / e-sign / costing card stills for the short clips (assets/clip-*.mp4 + posters)
 - load assets/cf-clips.js on every page that uses them
 - add the Trucking & logistics page to the nav dropdown, homepage strip + footer, vertical close links
 - sitemap.xml + llms.txt entries
"""
import re
from pathlib import Path

ROOT = Path(r"C:\Users\Matthew\Desktop\Crewfinding")
PAGES = ["index.html"] + [f"{d}/index.html" for d in
         ("moving", "landscaping", "junk-removal", "trucking-logistics", "pricing", "what-is-crewfinding", "privacy", "terms")]
CLIP = {"gps": ("gps", "loop"), "esign": ("esign", "loop"), "costing": ("cost", "loop")}
IMG = re.compile(r'<img src="((?:\.\./)?)assets/feat-(gps|esign|costing)\.webp" alt="([^"]*)" loading="lazy">')

def clip_html(m):
    pre, key, alt = m.group(1), m.group(2), m.group(3)
    n, mode = CLIP[key]
    return (f'<span class="clip" data-src="{pre}assets/clip-{n}.mp4" data-mode="{mode}">'
            f'<img src="{pre}assets/clip-{n}.webp" alt="{alt}" loading="lazy" width="1112" height="834"></span>')

for rel in PAGES:
    p = ROOT / rel
    if not p.exists():
        continue
    h = p.read_text(encoding="utf-8")
    o = h
    pre = "" if rel == "index.html" else "../"
    h = IMG.sub(clip_html, h)
    if "clip-" in h and "cf-clips.js" not in h:
        h = h.replace("</body>", f'<script src="{pre}assets/cf-clips.js" defer></script>\n</body>', 1)
    # nav dropdown
    link = f'<a href="{pre}trucking-logistics/index.html">🚛 Trucking &amp; logistics</a>'
    mv = f'<a href="{pre}moving/index.html">🚚 Moving companies</a>'
    if "trucking-logistics" not in h.split("ndcard", 1)[-1][:700] and mv in h:
        h = h.replace(mv, mv + "\n          " + link, 1)
    if rel == "index.html":
        strip = '<a href="trucking-logistics/index.html">🚛 TRUCKING &amp; LOGISTICS</a>'
        if strip not in h:
            h = h.replace('<a href="moving/index.html">🚚 MOVING COMPANIES</a>',
                          '<a href="moving/index.html">🚚 MOVING COMPANIES</a>\n    ' + strip, 1)
        foot = '<a href="trucking-logistics/index.html">Trucking &amp; logistics</a>'
        if foot not in h:
            h = h.replace('<a href="moving/index.html">Moving companies</a>',
                          '<a href="moving/index.html">Moving companies</a>\n      ' + foot, 1)
        h = h.replace("Stopwatch with orange progress arc", "Stopwatch with gold progress arc")
    # close-card seo links on the verticals
    if rel in ("moving/index.html", "landscaping/index.html", "junk-removal/index.html"):
        t = '<a class="seolink" href="../trucking-logistics/index.html">trucking and logistics software</a>'
        if t not in h:
            h = h.replace(' &nbsp;·&nbsp; <a class="seolink" href="../pricing/index.html">CrewFinding pricing</a>',
                          ' &nbsp;·&nbsp; ' + t + ' &nbsp;·&nbsp; <a class="seolink" href="../pricing/index.html">CrewFinding pricing</a>', 1)
    if h != o:
        p.write_text(h, encoding="utf-8")
        print("patched", rel)

sm = ROOT / "sitemap.xml"
s = sm.read_text(encoding="utf-8")
if "trucking-logistics" not in s:
    s = s.replace('  <url><loc>https://crewfinding.com/landscaping/</loc>',
                  '  <url><loc>https://crewfinding.com/trucking-logistics/</loc><changefreq>monthly</changefreq><priority>0.9</priority></url>\n  <url><loc>https://crewfinding.com/landscaping/</loc>', 1)
    sm.write_text(s, encoding="utf-8"); print("patched sitemap.xml")

ll = ROOT / "llms.txt"
t = ll.read_text(encoding="utf-8")
if "trucking-logistics" not in t:
    t = t.replace("- [For landscaping crews]",
                  "- [For trucking and logistics companies](https://crewfinding.com/trucking-logistics/): GPS arrivals at the dock, BOLs and PODs signed on a phone, detention time on the clock, true profit per run\n- [For landscaping crews]", 1)
    ll.write_text(t, encoding="utf-8"); print("patched llms.txt")
