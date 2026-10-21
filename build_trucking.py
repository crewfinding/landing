"""Build trucking-logistics/index.html from the moving page's chrome + new trucking copy.
Run order: build_subpages.py (if rebuilding verticals) -> build_trucking.py -> add_clips.py
"""
import json, re, sys
from pathlib import Path

ROOT = Path(r"C:\Users\Matthew\Desktop\Crewfinding")
tpl = (ROOT / "moving" / "index.html").read_text(encoding="utf-8")

TITLE = "Trucking & Logistics Software | GPS Trucks, Signed PODs, True Run Profit | CrewFinding"
DESC = ("Trucks on a live map, PODs signed at the dock, fuel and hours on the right run, and the true profit of every run. "
        "Plans from $40 a month, priced by truck.")

FAQ = [
    ("Does CrewFinding work for a small trucking or courier company?",
     "It is built for companies running two to five crews or trucks: box-truck fleets, couriers, local cartage and last-mile delivery. Plans start at $40 a month, priced by truck, with everyone included."),
    ("Is CrewFinding an ELD or a dispatch system?",
     "No. CrewFinding is not an ELD and it is not a full dispatch or TMS platform. Keep your ELD for hours-of-service rules. CrewFinding sits next to it and handles what it does not: GPS arrivals, signed BOLs and PODs, tracked hours, expenses and the true profit of every run."),
    ("Can the receiver sign the proof of delivery on a phone?",
     "Yes. The receiver signs the BOL and proof of delivery on the driver's phone at the dock, and the driver can snap a photo of the freight. Everything saves to the job file with the time and GPS stamp, so it cannot be lost."),
    ("Does it track where my trucks are?",
     "Every truck appears on a live map. A geofence stamps the arrival time automatically when the truck reaches the address, so you know the drop happened because the app saw the truck arrive."),
    ("What does it cost?",
     "Plans start at $40 a month, priced by truck: $40 for up to 2 trucks, $60 for 3 trucks, $80 for up to 5. More than 5 trucks, contact us. Everything is included. See the <a class=\"seolink\" href=\"../pricing/index.html\">full pricing</a>."),
    ("Does it handle driver payroll?",
     "No, and we will not pretend it does. CrewFinding tracks every driver's hours per run and totals them into a timesheet, so when you run payroll you are working from exact tracked hours instead of paper or memory."),
    ("I dispatch loads that other carriers run. Does this work for me?",
     "Yes. Put the driver on CrewFinding and you watch the run from wherever you are: the arrival stamp, the signed POD and the cost of the run. You do not have to own the truck to see the whole job."),
]

def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s)

jsonld = {
    "@context": "https://schema.org", "@type": "FAQPage",
    "mainEntity": [{"@type": "Question", "name": q,
                    "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in FAQ],
}

CSS = """.hero{padding:0;overflow:hidden;position:relative;min-height:min(88vh,800px);display:flex;align-items:center}
.hero .hbg{position:absolute;inset:0;background:#071426 url(../assets/logistics-hero.webp) center right/cover no-repeat}
.hero .hvid{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:right center}
.hero .hscrim{position:absolute;inset:0;pointer-events:none;
  background:linear-gradient(90deg,rgba(7,20,38,.97) 0%,rgba(7,20,38,.86) 36%,rgba(7,20,38,.3) 64%,rgba(7,20,38,0) 82%),
             linear-gradient(0deg,#071426 0%,rgba(7,20,38,0) 24%)}
.hero .hcopy{position:relative;z-index:1;padding-top:150px;padding-bottom:120px;width:100%}
.hero h1{font-size:clamp(34px,4.5vw,60px);line-height:1.04;letter-spacing:-.028em;max-width:720px}
.hero .sub{color:var(--fg-body);font-size:clamp(17px,2vw,19px);line-height:1.7;max-width:560px;margin:24px 0 32px}
.hero .sub strong{color:#fff;font-weight:700}
@media(max-width:880px){
  .hero .hscrim{background:linear-gradient(180deg,rgba(7,20,38,.9) 0%,rgba(7,20,38,.74) 50%,rgba(7,20,38,.94) 100%)}
  .hero .hcopy{padding-top:130px;padding-bottom:90px}
}
"""

def page_css():
    m = re.search(r"<style>\n(.*?)</style>", tpl, re.S)
    css = m.group(1)
    a = css.index(".hero{padding")
    b = css.index("/* the day, as a timeline (ivory) */")
    css = css[:a] + CSS + css[b:]
    return css + ".fine{margin-top:26px;font-size:13.5px;color:var(--fg-mute)}\n"

def section(html, start_marker, end_marker):
    i = html.index(start_marker)
    j = html.index(end_marker, i)
    return i, j

html = tpl

# ---- head
html = re.sub(r"<title>.*?</title>", f"<title>{TITLE.replace('&', '&amp;')}</title>", html, count=1, flags=re.S)
html = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', html, count=1)
html = html.replace('href="https://crewfinding.com/moving/"', 'href="https://crewfinding.com/trucking-logistics/"')
html = re.sub(r'<meta property="og:title" content="[^"]*">',
              '<meta property="og:title" content="Trucking and logistics software: GPS trucks, signed PODs, true run profit">', html, count=1)
html = re.sub(r'<script type="application/ld\+json">.*?</script>',
              lambda m: '<script type="application/ld+json">\n' + json.dumps(jsonld, indent=2, ensure_ascii=False) + "\n</script>",
              html, count=1, flags=re.S)
html = re.sub(r"<style>\n.*?</style>", lambda m: "<style>\n" + page_css() + "</style>", html, count=1, flags=re.S)

# ---- body sections (everything between the nav and the footer is rewritten)
i0 = html.index('<section class="hero')
i1 = html.index("<footer")
head_part, foot_part = html[:i0], html[i1:]

# keep the store badges markup from the template hero so the download row is identical
badges = re.search(r'<div class="ctarow">.*?</div>\s*</div>', tpl[tpl.index('<section class="hero'):], re.S).group(0)
ctarow = badges  # the whole .ctarow block (button + store badges)
body = f'''<section class="hero thero band-night">
  <div class="hbg" aria-hidden="true"></div>
  <video class="hvid" id="hvid" src="../assets/logistics-hero.mp4" poster="../assets/logistics-hero.webp" autoplay muted loop playsinline preload="auto" aria-hidden="true"></video>
  <div class="hscrim" aria-hidden="true"></div>
  <div class="wrap hcopy inner">
    <span class="eyebrow">For trucking and logistics</span>
    <h1>The truck arrives on the clock. The POD signs at the dock. The run ends with its real number.</h1>
    <p class="sub">CrewFinding tracks your trucks and drivers from depot to final drop: GPS arrivals at the dock, BOLs and PODs signed on a phone, tracked hours, every fuel receipt, and <strong>the true profit of every run</strong>.</p>
    {ctarow}
    <p class="ctanote">FREE TO DOWNLOAD · FROM $40/MO · PRICED BY TRUCK · NEVER PER SEAT</p>
  </div>
</section>

<section class="day band-ivory on-light round-top">
  <svg class="motif" style="right:-150px;top:30px;width:520px;height:520px" viewBox="0 0 400 400" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="200" cy="200" r="150"/><circle cx="200" cy="200" r="100" stroke-dasharray="3 9"/><circle cx="200" cy="200" r="46"/><path d="M200 6v76M200 318v76M6 200h76M318 200h76" stroke-linecap="round"/><circle cx="200" cy="200" r="7" fill="currentColor" stroke="none"/></svg>
  <div class="wrap inner">
    <span class="eyebrow cool">One run, dock to dock</span>
    <h2>A Thursday four-drop run, Dorval to Ottawa, exactly as CrewFinding saw it.</h2>
    <div class="steps">
      <div class="step"><span class="t num">06:10</span><span class="e">🚛</span><div><h3>Dispatched from the depot</h3><p>Karim and Léa get the run on their phones: four drops, four BOLs, every receiver's contact. The box truck leaves Dorval.</p></div></div>
      <div class="step"><span class="t num">08:31</span><span class="e">📍</span><div><h3>Geofence stamps the first drop</h3><p>The app sees the truck reach the Kanata dock and stamps 08:31. Nobody radios to ask where the truck is.</p></div></div>
      <div class="step"><span class="t num">08:52</span><span class="e">✍️</span><div><h3>The receiver signs the POD at the dock</h3><p>The BOL and the proof of delivery are signed on the driver's phone, with a photo of the freight. Both file themselves to Job #3107.</p></div></div>
      <div class="step"><span class="t num">13:20</span><span class="e">⏱</span><div><h3>The clock keeps the dock honest</h3><p>Drop 3 held the truck <b>1 h 20 min</b> before unloading. The clock has it, so detention is a number you can bill, not an argument. The $212 diesel receipt gets snapped at the pump and lands on this job.</p></div></div>
      <div class="step"><span class="t num">17:05</span><span class="e">🧾</span><div><h3>Four drops signed, and the real number</h3><p>$1,950 billed, $1,160 in wages, fuel and tolls, <span class="kept num">$790 kept</span>. You knew before the truck was back at Dorval.</p></div></div>
    </div>
    <p class="fine">A sample run, shown for illustration.</p>
  </div>
</section>

<section class="pains band-navy">
  <svg class="motif" style="left:-40px;bottom:10px;width:640px;height:200px" viewBox="0 0 640 200" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M20 170 C 160 150, 200 60, 340 90 S 520 150, 610 40" stroke-dasharray="6 10" stroke-linecap="round"/><circle cx="20" cy="170" r="11"/><circle cx="610" cy="40" r="8" fill="currentColor" stroke="none"/></svg>
  <div class="wrap inner">
    <span class="eyebrow cool">The three fights CrewFinding ends</span>
    <h2>Trucking problems, handled at the dock.</h2>
    <div class="paingrid">
      <div class="pain"><div class="ico">📄</div><h3>"The receiver says it never showed up."</h3><p>The geofence stamped the arrival and the receiver signed the POD with a photo of the freight. <b>The proof is in the job file with a timestamp, not in a driver's glovebox.</b></p></div>
      <div class="pain"><div class="ico">⏱</div><h3>"The truck sat at their dock for two hours."</h3><p>The clock tracks every minute the truck waits. <b>Detention stops being a feeling and becomes a number you can bill.</b></p></div>
      <div class="pain"><div class="ico">⛽</div><h3>"The run paid. Did it make money?"</h3><p>Wages, fuel and tolls land on the run that burned them, the day it happens. <b>You see the real number per run, not a month-end mystery.</b></p></div>
    </div>
  </div>
</section>

<section class="feats band-white on-light">
  <div class="wrap inner">
    <span class="eyebrow cool">Built for the cab, not the office</span>
    <h2>The three features a driver touches every run.</h2>
    <div class="featgrid">
      <a class="acard" href="../index.html#appgrid">
        <span class="clip" data-src="../assets/clip-gps.mp4" data-mode="loop"><img src="../assets/clip-gps.webp" alt="Gold GPS pin with a geofence ring pulsing on a city block" loading="lazy" width="1112" height="834"></span>
        <h3>GPS truck tracking</h3>
        <p>Every truck on the live map, with a geofence that stamps arrivals at the dock on its own.</p>
        <p class="ben">You know the drop happened because the app saw the truck arrive.</p>
      </a>
      <a class="acard" href="../index.html#appgrid">
        <span class="clip" data-src="../assets/clip-esign.mp4" data-mode="loop"><img src="../assets/clip-esign.webp" alt="A pen signing a document on a tablet" loading="lazy" width="1112" height="834"></span>
        <h3>E-sign BOLs and PODs</h3>
        <p>Bill of lading and proof of delivery signed at the dock, with a freight photo, filed to the job instantly.</p>
        <p class="ben">The paperwork that wins the dispute, signed before the truck leaves.</p>
      </a>
      <a class="acard" href="../index.html#appgrid">
        <span class="clip" data-src="../assets/clip-cost.mp4" data-mode="loop"><img src="../assets/clip-cost.webp" alt="Receipts and coins with a glowing total line" loading="lazy" width="1112" height="834"></span>
        <h3>Run costing</h3>
        <p>Tracked hours times wages, plus fuel and tolls, tallied per run as it happens.</p>
        <p class="ben">The real number: what the run cost and what you kept.</p>
      </a>
    </div>
  </div>
</section>

<section class="founder band-night citytex">
  <p><strong>Built by a moving company owner</strong> who ran real trucks and crews for years and couldn't find software that told him what a run actually cost. Not a VC product team guessing at the road. Built from the truck cab out.</p>
</section>

<section class="faq band-ivory on-light">
  <svg class="motif" style="left:-190px;top:40px;width:480px;height:480px" viewBox="0 0 400 400" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="200" cy="200" r="150"/><circle cx="200" cy="200" r="100" stroke-dasharray="3 9"/><circle cx="200" cy="200" r="46"/><path d="M200 6v76M200 318v76M6 200h76M318 200h76" stroke-linecap="round"/><circle cx="200" cy="200" r="7" fill="currentColor" stroke="none"/></svg>
  <div class="wrap inner">
    <span class="eyebrow cool">Questions trucking companies ask</span>
    <h2>Before you download it.</h2>
    <div class="qa">
''' + "\n".join(f"      <details><summary>{q}</summary><p>{a}</p></details>" for q, a in FAQ) + '''
    </div>
  </div>
</section>

<section class="close citytex band-night">
  <div class="inner">
    <div class="cta-card">
    <h2>Know what every run really makes.</h2>
    <a class="btn on-gold" href="#" data-store style="font-size:17px;padding:16px 38px">Download CrewFinding</a>
    <p class="ctanote">FREE TO DOWNLOAD · iOS &amp; ANDROID · FROM $40/MO</p>
    <p class="links"><a class="seolink" href="../moving/index.html">moving company software</a> &nbsp;·&nbsp; <a class="seolink" href="../landscaping/index.html">landscaping crew software</a> &nbsp;·&nbsp; <a class="seolink" href="../junk-removal/index.html">junk removal software</a> &nbsp;·&nbsp; <a class="seolink" href="../pricing/index.html">CrewFinding pricing</a></p>
  </div>
  </div>
</section>

'''

# reduced-motion / data-saver: stop the hero loop, the poster stays
HERO_JS = (
    "var hv=document.getElementById('hvid');\n"
    "if(hv){var rm=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches,sd=navigator.connection&&navigator.connection.saveData;\n"
    "if(rm||sd){hv.removeAttribute('autoplay');hv.pause();}\n"
    "if(sd){hv.removeAttribute('src');hv.load();}}\n"
)
TAIL = "})();\n</script>"
assert TAIL in foot_part
foot_part = foot_part.replace(TAIL, HERO_JS + TAIL, 1)

out = head_part + body + foot_part
(ROOT / "trucking-logistics").mkdir(exist_ok=True)
(ROOT / "trucking-logistics" / "index.html").write_text(out, encoding="utf-8")
print("wrote trucking-logistics/index.html", len(out))
