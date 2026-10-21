"""Universal dispatch + job-tracking sections: one neutral skeleton for any service business.
Homepage gets the skeleton with a switcher (moving, landscaping, junk removal, delivery).
moving/, landscaping/, junk-removal/ get the same skeleton fixed to their own service.
trucking-logistics/ keeps the original freight version (add_dispatch.py).
Idempotent: output sits between UNIVERSAL-START / UNIVERSAL-END markers. Writes assets/cf-universal.js (the switcher data).
"""
import json, html, re
from pathlib import Path
R = Path(__file__).parent
START, END = "<!-- UNIVERSAL-START -->", "<!-- UNIVERSAL-END -->"

SAY_HEAD = "WAITING FOR THE CREW"
V = {
  "roofing": {
    "tab": "Roofing", "noun": "job", "page": "",
    "j": [("Roof tear-off and reshingle", "Laval"), ("Flat roof repair", "Verdun"), ("Flashing and gutters", "Longueuil")],
    "head": "JOB #1041 · ROOF RESHINGLE, LAVAL",
    "aria": "A roofing job started by your crew, part of it handed off to a subcontractor crew and finished, tracked the whole way",
    "r": [("Crew arrives · Laval", "The job sheet is signed on the crew's phone. GPS starts.", "WITH: YOUR CREW"),
          ("On the roof · hours tracked", "Live on your map. Crew hours and materials logged to the job.", "WITH: YOUR CREW"),
          ("Handed off · subcontractor crew", "The subcontractor signs for the flashing and gutters. Time and place filed.", "WITH: SUBCONTRACTOR"),
          ("Finished · Laval", "The customer signs off. Before and after photos saved as proof of completion.", "WITH: THE CUSTOMER")],
    "say": [SAY_HEAD, "CREW ARRIVED · JOB SHEET SIGNED", "ON THE ROOF · YOUR CREW · GPS LIVE", "HANDED OFF · SUBCONTRACTOR SIGNED", "ON THE JOB · SUBCONTRACTOR · GPS LIVE", "FINISHED · CUSTOMER SIGNED OFF"],
  },
  "construction": {
    "tab": "Construction", "noun": "job", "page": "",
    "j": [("Kitchen renovation", "Plateau"), ("Basement framing", "Brossard"), ("Deck build", "Laval")],
    "head": "JOB #1041 · KITCHEN RENOVATION, PLATEAU",
    "aria": "A construction job started by your crew, part of it handed off to a subcontractor and finished, tracked the whole way",
    "r": [("Crew arrives · Plateau", "The job sheet is signed on the crew's phone. GPS starts.", "WITH: YOUR CREW"),
          ("On site · hours tracked", "Live on your map. Crew hours and materials logged to the job.", "WITH: YOUR CREW"),
          ("Handed off · electrician subcontractor", "The subcontractor signs in for the rough-in. Time and place filed.", "WITH: SUBCONTRACTOR"),
          ("Finished · Plateau", "The customer signs off. Photos and proof of completion saved to the job.", "WITH: THE CUSTOMER")],
    "say": [SAY_HEAD, "CREW ARRIVED · JOB SHEET SIGNED", "ON SITE · YOUR CREW · GPS LIVE", "HANDED OFF · SUBCONTRACTOR SIGNED", "ON SITE · SUBCONTRACTOR · GPS LIVE", "FINISHED · CUSTOMER SIGNED OFF"],
  },
  "moving": {
    "tab": "Moving", "noun": "move", "page": "moving/index.html",
    "j": [("3-bedroom move", "Lachine to Brossard"), ("Office move", "Laval to Montreal"), ("Studio move", "Verdun to Westmount")],
    "head": "JOB #1041 · 3-BEDROOM MOVE, LACHINE TO BROSSARD",
    "aria": "A move picked up by your crew, handed off to a partner crew and delivered, tracked the whole way",
    "r": [("Crew arrives · Lachine", "The job sheet is signed on the crew's phone. GPS starts.", "WITH: YOUR CREW · TRUCK 2"),
          ("On the way · Lachine to Brossard", "Live on your map, every minute of the drive.", "WITH: YOUR CREW · TRUCK 2"),
          ("Handed off · storage warehouse", "The partner crew signs for the items. Time and place filed.", "WITH: PARTNER CREW"),
          ("Delivered · Brossard", "The customer signs for delivery. Proof of delivery saved to the job.", "WITH: THE CUSTOMER")],
    "say": [SAY_HEAD, "CREW ARRIVED · JOB SHEET SIGNED", "ON THE WAY · YOUR CREW · GPS LIVE", "HANDED OFF · PARTNER CREW SIGNED", "ON THE WAY · PARTNER CREW · GPS LIVE", "DELIVERED · CUSTOMER SIGNED"],
  },
  "landscaping": {
    "tab": "Landscaping", "noun": "job", "page": "landscaping/index.html",
    "j": [("Weekly lawn care", "Dollard-des-Ormeaux"), ("Spring cleanup", "Pointe-Claire"), ("Garden bed install", "Kirkland")],
    "head": "JOB #1041 · SPRING CLEANUP, POINTE-CLAIRE",
    "aria": "A landscaping job started by your crew, handed off to a subcontractor crew and finished, tracked the whole way",
    "r": [("Crew arrives · Pointe-Claire", "The job sheet is signed on the crew's phone. GPS starts.", "WITH: YOUR CREW"),
          ("Between properties · live", "Live on your map, every stop timed.", "WITH: YOUR CREW"),
          ("Handed off · subcontractor crew", "The subcontractor signs for the rest of the route. Time and place filed.", "WITH: SUBCONTRACTOR"),
          ("Finished · Kirkland", "The customer signs off. Proof of completion saved with the photos.", "WITH: THE CUSTOMER")],
    "say": [SAY_HEAD, "CREW ARRIVED · JOB SHEET SIGNED", "BETWEEN PROPERTIES · YOUR CREW · GPS LIVE", "HANDED OFF · SUBCONTRACTOR SIGNED", "BETWEEN PROPERTIES · SUBCONTRACTOR · GPS LIVE", "FINISHED · CUSTOMER SIGNED OFF"],
  },
  "junk": {
    "tab": "Junk removal", "noun": "haul", "page": "junk-removal/index.html",
    "j": [("Garage cleanout", "Brossard"), ("Appliance pickup", "Longueuil"), ("Estate cleanout", "Laval")],
    "head": "JOB #1041 · GARAGE CLEANOUT, BROSSARD",
    "aria": "A junk removal haul picked up by your crew, handed off to a partner and dropped off, tracked the whole way",
    "r": [("Crew arrives · Brossard", "The job sheet is signed on the crew's phone. GPS starts.", "WITH: YOUR CREW"),
          ("Hauling to the depot", "Live on your map all the way to the drop-off.", "WITH: YOUR CREW"),
          ("Handed off · recycling partner", "The partner signs for the load. Time and place filed.", "WITH: PARTNER"),
          ("Dropped off · the depot", "The depot signs for the drop-off. Receipt saved to the job.", "WITH: THE DEPOT")],
    "say": [SAY_HEAD, "CREW ARRIVED · JOB SHEET SIGNED", "HAULING · YOUR CREW · GPS LIVE", "HANDED OFF · PARTNER SIGNED", "HAULING · PARTNER · GPS LIVE", "DROPPED OFF · DEPOT SIGNED"],
  },
  "delivery": {
    "tab": "Delivery", "noun": "run", "page": "trucking-logistics/index.html",
    "j": [("Delivery run 4471", "Montreal to Toronto"), ("Delivery run 4472", "Laval to Ottawa"), ("Delivery run 4473", "Dorval to Quebec City")],
    "head": "RUN #4471 · MONTREAL TO TORONTO",
    "aria": "A delivery picked up by your crew, handed off to a partner crew and delivered, tracked the whole way",
    "r": [("Picked up · Dorval warehouse", "The sender signs the job sheet on the crew's phone. GPS starts.", "WITH: YOUR CREW · TRUCK 2"),
          ("In transit · Montreal to Cornwall", "Live on your map, every minute of the drive.", "WITH: YOUR CREW · TRUCK 2"),
          ("Handed off · Cornwall yard", "The partner crew signs for the items. Time and place filed.", "WITH: PARTNER CREW"),
          ("Delivered · Toronto", "The recipient signs for delivery. Proof of delivery saved to the job.", "WITH: THE RECIPIENT")],
    "say": [SAY_HEAD, "PICKED UP · JOB SHEET SIGNED", "IN TRANSIT · YOUR CREW · GPS LIVE", "HANDED OFF · PARTNER CREW SIGNED", "IN TRANSIT · PARTNER CREW · GPS LIVE", "DELIVERED · RECIPIENT SIGNED"],
  },
}

def flat(v):
    o = {"head": v["head"], "aria": v["aria"]}
    for i, (t, s) in enumerate(v["j"], 1):
        o["j%dt" % i], o["j%ds" % i] = t, s
    for i, (b, d, h) in enumerate(v["r"], 1):
        o["r%db" % i], o["r%dd" % i], o["r%dh" % i] = b, d, h
    return o

def esc(s): return html.escape(s, quote=True)

ICON_OWN = '<svg viewBox="0 0 24 24" fill="none" stroke="#FFD100" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="9" cy="8" r="3.2"/><path d="M3 20c0-3.6 2.7-6 6-6s6 2.4 6 6"/><circle cx="17.5" cy="9" r="2.4"/><path d="M16.5 14.2c2.9.2 4.5 2.2 4.5 5.3"/></svg>'
ICON_PARTNER = '<svg viewBox="0 0 24 24" fill="none" stroke="#FFD100" stroke-width="1.8" aria-hidden="true"><circle cx="9" cy="12" r="5"/><circle cx="15" cy="12" r="5"/></svg>'
ICON_SUB = '<svg viewBox="0 0 24 24" fill="none" stroke="#FFD100" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="10" cy="8" r="3.4"/><path d="M3.5 20c0-3.8 2.9-6.2 6.5-6.2s6.5 2.4 6.5 6.2"/><path d="M19 5v6M16 8h6"/></svg>'

def tabs_html(default, label):
    b = "".join('<button type="button" role="tab" data-v="%s" aria-selected="%s">%s</button>' % (k, "true" if k == default else "false", v["tab"]) for k, v in V.items())
    d = V[default]
    return ('<div class="vtabs" role="tablist" aria-label="%s" data-vtabs><span class="vt-l">SEE IT FOR</span>%s'
            '<a class="vlink" data-vlink href="%s"%s>See the full %s version</a></div>') % (label, b, d["page"], "" if d["page"] else " hidden", d["tab"].lower())

def build(prefix, vk, tabs):
    v = V[vk]; f = flat(v)
    u = lambda k: 'data-u="%s"' % k
    noun = v["noun"]
    t1 = tabs_html(vk, "Pick your kind of work to see the same flow for it") if tabs else ""
    t2 = tabs_html(vk, "Pick your kind of work to see the same flow for it") if tabs else ""
    lane = lambda ico, ttl, sub, ts: ('<div class="db-lane" data-lane>\n'
        '          <div class="db-lh"><i class="db-ico">%s</i><div><b>%s</b><span>%s</span></div></div>\n'
        '          <div class="db-slot" data-slot></div>\n'
        '          <div class="db-rc"><i data-rc="sent"><b>SENT</b><u>%s</u></i><i data-rc="recv"><b>RECEIVED</b><u>%s</u></i><i data-rc="acc"><b>ACCEPTED</b><u>%s</u></i><em class="db-route">Job sheet and route on their phone</em></div>\n'
        '        </div>') % ((ico, ttl, sub) + ts)
    say = esc(json.dumps(v["say"], ensure_ascii=False))
    rows = ""
    times = ["08:22", "08:22 to 11:40", "11:40", "15:05"]
    for i in range(1, 5):
        rows += ('        <li data-row><i class="n">%d</i><div><b %s>%s</b><span class="d" %s>%s</span></div><span class="t">%s</span><span class="held" %s>%s</span></li>\n'
                 % (i, u("r%db" % i), esc(f["r%db" % i]), u("r%dd" % i), esc(f["r%dd" % i]), times[i-1], u("r%dh" % i), esc(f["r%dh" % i])))
    return f"""{START}
<!-- ============================================================
     DISPATCH · any service business: your crews, your partners, your subcontractors, tracked to done
============================================================ -->
<section id="dispatch" class="band-night dspsec" data-vertical="{vk}" style="padding:14vh 0 6vh;position:relative">
  <div class="wrap beat-inner">
    <div class="dsp-top">
      <div>
        <span class="eyebrow cool">Scheduling + dispatch</span>
        <h2>Book the {noun}. Send it to any crew. See it received.</h2>
      </div>
      <div class="dsp-copy"><p>Most service businesses don't run every job with their own people. Some go to a partner you trust, or a subcontractor you hire for the day. CrewFinding puts all of it on one dispatch board: your own crews, your partners and your subcontractors. Create the job, pick who does it, set the route and send it. The moment they receive it and accept, you see it, with the time.</p></div>
    </div>
    <ol class="flow" data-flow aria-label="How a job moves, from booking to the final mile">
        <li data-s="1"><i>1</i><b>Book</b><span>Create the job</span></li>
        <li data-s="2"><i>2</i><b>Assign</b><span>Crew, partner or subcontractor</span></li>
        <li data-s="3"><i>3</i><b>Received</b><span>Accepted, with the time</span></li>
        <li data-s="4"><i>4</i><b>Tracked</b><span>Job sheet signed, GPS live</span></li>
        <li data-s="5"><i>5</i><b>Final mile</b><span>Customer signs off</span></li>
        <em class="fg g1">SCHEDULING AND DISPATCH</em><em class="fg g2">JOB TRACKING</em>
      </ol>
    {t1}
    <div class="dispcard" data-board>
      <div class="sh-head"><span>DISPATCH BOARD · MONDAY</span><span class="sh-live"><i></i>LIVE</span></div>
      <div class="db-grid">
        <div class="db-queue"><div class="db-h">TO ASSIGN</div>
          <div class="db-job" data-job><b {u("j1t")}>{esc(f["j1t"])}</b><span {u("j1s")}>{esc(f["j1s"])}</span></div>
          <div class="db-job" data-job><b {u("j2t")}>{esc(f["j2t"])}</b><span {u("j2s")}>{esc(f["j2s"])}</span></div>
          <div class="db-job" data-job><b {u("j3t")}>{esc(f["j3t"])}</b><span {u("j3s")}>{esc(f["j3s"])}</span></div>
        </div>
        <div class="db-lanes">
          <div class="db-h">WHO DOES IT</div>
          {lane(ICON_OWN, "YOUR OWN CREW", "Your crew gets the day and the route", ("6:45", "6:47", "6:52"))}
          {lane(ICON_PARTNER, "YOUR PARTNER", "A company you work with gets the job", ("6:46", "7:03", "7:10"))}
          {lane(ICON_SUB, "A SUBCONTRACTOR", "A crew you hire for the day receives it in the app", ("6:46", "7:12", "7:30"))}
        </div>
      </div>
      <div class="db-foot"><span class="db-sum" data-sum aria-live="polite">0 OF 3 RECEIVED</span><button type="button" class="sh-replay" data-board-replay>REPLAY THE BOARD</button></div>
    </div>
    <p class="dsp-note dsp-center">Built for service businesses that run their own crews and partner crews side by side.</p>
  </div>
</section>
<section id="shipment" class="band-night dspsec" style="padding:6vh 0 15vh;position:relative">
  <div class="wrap beat-inner">
    {t2}
    <div class="dsp-grid">
    <div>
    <div class="shipcard" data-shipment data-say="{say}">
      <div class="sh-head"><span {u("head")}>{esc(f["head"])}</span><span class="sh-live"><i></i>LIVE</span></div>
      <div class="sh-bar"><span class="sh-status" data-status aria-live="polite">{esc(SAY_HEAD)}</span><span class="sh-clock" data-clock>--:--</span></div>
      <svg class="sh-svg" viewBox="0 0 720 130" role="img" aria-label="{esc(v["aria"])}" data-u="aria" data-attr="aria-label">
        <line x1="46" y1="68" x2="674" y2="68" stroke="#2B4766" stroke-width="2.5" stroke-dasharray="3 11" stroke-linecap="round"/>
        <line data-prog x1="70" y1="68" x2="70" y2="68" stroke="#FFD100" stroke-width="3.5" stroke-linecap="round" style="filter:drop-shadow(0 0 7px rgba(255,209,0,.7))"/>
        <g class="sh-node" data-node transform="translate(70,68)"><circle class="ring" r="14"/><circle class="ring r2" r="14"/><circle class="core" r="9"/></g>
        <g class="sh-node" data-node transform="translate(385,68)"><circle class="ring" r="14"/><circle class="ring r2" r="14"/><circle class="core" r="9"/></g>
        <g class="sh-node" data-node transform="translate(650,68)"><circle class="ring" r="14"/><circle class="ring r2" r="14"/><circle class="core" r="9"/></g>
        <g class="sh-badge" data-badge transform="translate(70,20)"><circle r="13"/><text>1</text></g>
        <g class="sh-badge" data-badge transform="translate(385,20)"><circle r="13"/><text>2</text></g>
        <g class="sh-badge" data-badge transform="translate(650,20)"><circle r="13"/><text>3</text></g>
        <text class="mk-lab" x="70" y="112">START</text><text class="mk-lab" x="385" y="112">HAND-OFF</text><text class="mk-lab" x="650" y="112">DONE</text>
        <g class="sh-veh mk" data-a transform="translate(70,68)"><circle class="mk-ring" r="17"/><circle class="mk-core" r="8"/></g>
        <g class="sh-veh mk pt dim" data-b transform="translate(428,68)"><circle class="mk-ring" r="17"/><circle class="mk-core" r="8"/></g>
      </svg>
      <ol class="sh-rows">
{rows}      </ol>
      <button type="button" class="sh-replay" data-replay>REPLAY THE JOB</button>
    </div>
    </div>
    <div class="dsp-copy">
      <span class="eyebrow cool">Job tracking · the final mile</span>
      <h2>Then watch it all the way to the final mile.</h2>
      <p>Once your crew arrives, the job is signed on their phone and GPS tracking starts. You follow it live on your own screen. If it changes hands, that hand-off is signed and time-stamped. At the destination, the recipient signs off on delivery. Your items go all the way to where they belong, with every hand on them recorded.</p>
      <ul class="dsp-steps">
        <li><b>Pickup.</b> You sign off and tracking starts.</li>
        <li><b>In transit.</b> Live on your map, every hand-off signed.</li>
        <li><b>Delivery.</b> The recipient signs and proof of delivery is filed.</li>
      </ul>
      <a class="seolink" href="{prefix}trucking-logistics/index.html" style="display:inline-block;margin-top:10px">dispatch and delivery tracking software</a>
    </div>
    </div>
  </div>
</section>
{END}"""

def swap(h, block, anchor_re=None):
    if START in h:
        return re.sub(re.escape(START) + r".*?" + re.escape(END), lambda m: block, h, count=1, flags=re.S)
    raise SystemExit("no marker")

# ---- homepage: replace the old freight blocks (banner through the shipment section) the first time
p = R / "index.html"; h = p.read_text(encoding="utf-8")
home = build("", "roofing", True)
if START in h:
    h = swap(h, home)
else:
    d0 = h.rfind("<!-- ====", 0, h.index("DISPATCH · own crews"))
    d1 = h.index("</section>", h.index('<section id="shipment"')) + len("</section>")
    h = h[:d0] + home + h[d1:]
if "cf-universal.js" not in h:
    h = h.replace('<script src="assets/cf-dispatch.js" defer></script>', '<script src="assets/cf-dispatch.js" defer></script>\n<script src="assets/cf-universal.js" defer></script>', 1)
p.write_text(h, encoding="utf-8")

# ---- vertical pages: fixed to their own service, inserted after the story-of-a-day section
for folder, vk in (("moving", "moving"), ("landscaping", "landscaping"), ("junk-removal", "junk")):
    p = R / folder / "index.html"; h = p.read_text(encoding="utf-8")
    block = build("../", vk, False).replace('style="padding:14vh 0 6vh;position:relative"', 'style="padding:14vh 0 6vh;position:relative"')
    block = block.replace('src="assets/', 'src="../assets/')
    if START in h:
        h = swap(h, block)
    else:
        CSS = '<link rel="stylesheet" href="../assets/cf.css">'
        h = h.replace(CSS, CSS + "\n" + '<link rel="stylesheet" href="../assets/cf-dispatch.css">', 1)
        h = h.replace("</body>", '<script src="../assets/cf-dispatch.js" defer></script>\n</body>', 1)
        m = re.search(r'<section class="pains band-navy">', h)
        h = h[:m.start()] + block + "\n" + h[m.start():]
    p.write_text(h, encoding="utf-8")
    print(folder, "ok")

# ---- switcher script
data = {k: dict(flat(v), say=v["say"], page=v["page"], tab=v["tab"].lower()) for k, v in V.items()}
js = """/* Universal dispatch + tracking: the same skeleton shown for each kind of service. Generated by add_universal.py. */
(function(){
  var DATA = %s;
  function apply(key){
    var d = DATA[key]; if(!d) return;
    document.querySelectorAll("[data-u]").forEach(function(el){
      var v = d[el.getAttribute("data-u")]; if(v == null) return;
      if(el.getAttribute("data-attr")) el.setAttribute(el.getAttribute("data-attr"), v); else el.textContent = v;
    });
    document.querySelectorAll("[data-shipment]").forEach(function(c){ c.setAttribute("data-say", JSON.stringify(d.say)); });
    document.querySelectorAll("[data-vtabs]").forEach(function(g){
      g.querySelectorAll("[data-v]").forEach(function(b){ b.setAttribute("aria-selected", b.getAttribute("data-v") === key ? "true" : "false"); });
      var a = g.querySelector("[data-vlink]"); if(a){ a.hidden = !d.page; a.setAttribute("href", d.page || "#"); a.textContent = "See the full " + d.tab + " version"; }
    });
  }
  document.querySelectorAll("[data-vtabs] [data-v]").forEach(function(b){
    b.addEventListener("click", function(){
      apply(b.getAttribute("data-v"));
      var sec = b.closest("section"), r = sec && sec.querySelector("[data-board-replay],[data-replay]");
      if(r) r.click();
    });
  });
})();
""" % json.dumps(data, ensure_ascii=False)
(R / "assets" / "cf-universal.js").write_text(js, encoding="utf-8")
print("universal sections written")
