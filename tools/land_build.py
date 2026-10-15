#!/usr/bin/env python3
"""Builders for the 'Land in Gujarat' page and the land cards on Home / Projects."""
import html, json, os

E = html.escape
HERE = os.path.dirname(os.path.abspath(__file__))
GM = json.load(open(os.path.join(HERE, 'geo', 'gmap.json')))

LAND_BUY = "Land in Gujarat — Buy"
LAND_SELL = "Land in Gujarat — Sell"

# ---------------------------------------------------------------- copy ----
REGION_ORDER = ['capital', 'north', 'central', 'south', 'saurashtra', 'kutch']
REGION_COPY = {
    'capital': dict(
        chip="Ahmedabad–Gandhinagar", icon="fa-city",
        blurb="Our home ground, with our office in Kalol, Gandhinagar district. Residential plots along the highway corridors, warehousing near the ring road and expressway, and land around GIFT City and the Dholera investment region.",
        towns=["Kalol", "Sanand", "Dholka", "Bavla", "Dholera", "GIFT City"]),
    'north': dict(
        chip="North Gujarat", icon="fa-wheat-awn",
        blurb="Farm land and industrial plots along the Mehsana to Palanpur highway corridor, plus parcels near Becharaji and Himmatnagar.",
        towns=["Mehsana", "Patan", "Palanpur", "Himmatnagar", "Becharaji", "Visnagar"]),
    'central': dict(
        chip="Central Gujarat", icon="fa-industry",
        blurb="Industrial land around Vadodara, Halol and Savli, residential plots around Vadodara and Anand, and farm land across Kheda and Panchmahal.",
        towns=["Vadodara", "Anand", "Nadiad", "Halol", "Savli", "Godhra"]),
    'south': dict(
        chip="South Gujarat", icon="fa-water",
        blurb="Industrial estates around Ankleshwar, Vapi and Dahej, residential growth around Surat, and farm land in Navsari and Valsad.",
        towns=["Surat", "Bharuch", "Ankleshwar", "Dahej", "Vapi", "Navsari"]),
    'saurashtra': dict(
        chip="Saurashtra", icon="fa-anchor",
        blurb="Engineering and ceramics clusters at Rajkot and Morbi, Jamnagar's industrial belt, coastal land, and temple-town tourism at Somnath and Dwarka.",
        towns=["Rajkot", "Jamnagar", "Morbi", "Bhavnagar", "Junagadh", "Dwarka"]),
    'kutch': dict(
        chip="Kutch", icon="fa-mountain-sun",
        blurb="Port-linked industrial land near Mundra and Gandhidham, and tourism land near the White Rann. Border and coastal areas carry extra permission rules, so the paperwork gets extra care.",
        towns=["Bhuj", "Gandhidham", "Mundra", "Anjar", "Mandvi", "Dhordo"]),
}

TICKER = ["Ahmedabad", "Gandhinagar", "GIFT City", "Sanand", "Dholera", "Mehsana", "Palanpur", "Vadodara", "Anand",
          "Surat", "Bharuch", "Vapi", "Rajkot", "Jamnagar", "Bhavnagar", "Junagadh", "Bhuj", "Mundra"]

PIN_LABEL = {   # dx, dy, text-anchor
    'kalol': (-11, -5, 'end'), 'gift': (10, -3, 'start'), 'ahmedabad': (10, 12, 'start'), 'sanand': (-9, 14, 'end'),
    'dholera': (-9, 4, 'end'), 'mehsana': (-9, 4, 'end'), 'palanpur': (9, 4, 'start'), 'himmatnagar': (9, 4, 'start'),
    'vadodara': (9, 4, 'start'), 'anand': (9, 4, 'start'), 'surat': (9, 4, 'start'), 'bharuch': (9, 4, 'start'),
    'vapi': (9, 4, 'start'), 'rajkot': (0, 17, 'middle'), 'jamnagar': (0, -10, 'middle'), 'bhavnagar': (9, 4, 'start'),
    'junagadh': (0, 17, 'middle'), 'dwarka': (9, 4, 'start'), 'bhuj': (0, -10, 'middle'), 'mundra': (9, 4, 'start'),
}


def _r(v):
    s = '%.1f' % v
    return s[:-2] if s.endswith('.0') else s


# ----------------------------------------------------------- the big map ----
def gmap_svg():
    m = GM
    vw, vh = m['vw'], m['vh']
    region_label = {k: REGION_COPY[k]['chip'] for k in REGION_ORDER}
    o = []
    o.append(f'<svg class="gmap" viewBox="0 0 {vw} {vh}" role="group" aria-label="Map of Gujarat with six land regions and twenty towns" focusable="false" data-gmap>')
    # graticule + neighbours
    o.append(f'<g class="gm-grat" aria-hidden="true"><path d="{m["grat"]}"/>')
    for l in m['gratLabels']:
        o.append(f'<text x="{l["x"]}" y="{l["y"]}" text-anchor="{l["a"]}">{l["t"]}</text>')
    o.append('</g><g class="gm-neigh" aria-hidden="true">')
    for n in m['neighbours']:
        o.append(f'<text x="{n["x"]}" y="{n["y"]}" text-anchor="{n.get("a", "middle")}">{n["t"]}</text>')
    o.append('</g>')
    # regions
    o.append('<g class="gm-regions">')
    for rid in REGION_ORDER:
        r = m['regions'][rid]
        o.append(f'<path class="gm-region" data-region="{rid}" d="{r["d"]}"><title>{E(region_label[rid])}</title></path>')
    o.append('</g>')
    o.append(f'<path class="gm-borders" aria-hidden="true" d="{m["borders"]}"/>')
    o.append(f'<path class="gm-outline" aria-hidden="true" pathLength="1" d="{m["outline"]}"/>')
    # arcs from the Kalol office
    o.append('<g class="gm-arcs" aria-hidden="true">')
    for i, a in enumerate(m['arcs']):
        o.append(f'<path class="gm-arc" style="--i:{i}" pathLength="1" d="{a["d"]}"/>')
    o.append('</g>')
    # pins
    o.append('<g class="gm-pins">')
    for i, p in enumerate(m['pins']):
        dx, dy, anc = PIN_LABEL[p['id']]
        hub = p['id'] == 'kalol'
        rl = region_label[p['region']]
        name = 'Kalol (our office)' if hub else p['label']
        o.append(
            f'<g class="gm-pin{" hub" if hub else ""}" data-region="{p["region"]}" data-pin="{p["id"]}" style="--i:{i}" '
            f'transform="translate({p["x"]} {p["y"]})" tabindex="0" role="button" aria-label="{E(name)}, {E(rl)}">'
            f'<circle class="ring" r="4"/>' + ('<circle class="ring r2" r="4"/>' if hub else '') +
            f'<circle class="dot" r="{4.6 if hub else 3.2}"/>'
            f'<circle class="hit" r="13"/>'
            f'<text class="gm-label" x="{dx}" y="{dy}" text-anchor="{anc}">{E(p["label"])}{" · our office" if hub else ""}</text>'
            f'</g>')
    o.append('</g>')
    # scale bar + north arrow
    sc = m['scale']
    o.append(f'<g class="gm-scale" aria-hidden="true" transform="translate(64 {vh - 34})"><path d="M0 0H{sc["px"]}M0 -4V4M{sc["px"]} -4V4"/><text x="0" y="-9">{sc["label"]}</text></g>')
    o.append(f'<g class="gm-north" aria-hidden="true" transform="translate({vw - 34} 62)"><path d="M0 16V-8M-5 -2L0 -10L5 -2"/><text x="0" y="-16" text-anchor="middle">N</text></g>')
    o.append('</svg>')
    return ''.join(o)


def mini_svg(cls="gmap mini"):
    """Small decorative Gujarat outline with a few pulsing pins (Home land card, Projects banner)."""
    m = GM
    pins = {p['id']: p for p in m['pins']}
    use = ['surat', 'vadodara', 'rajkot', 'bhuj', 'bhavnagar', 'jamnagar']
    hub = pins['kalol']
    o = [f'<svg class="{cls}" viewBox="{m["mini"]["vb"]}" aria-hidden="true" focusable="false">']
    o.append(f'<path class="gm-fill" d="{m["mini"]["outline"]}"/>')
    o.append(f'<path class="gm-outline" pathLength="1" d="{m["mini"]["outline"]}"/>')
    o.append('<g class="gm-arcs">')
    import math
    for i, pid in enumerate(use):
        p = pins[pid]
        x1, y1, x2, y2 = hub['x'], hub['y'], p['x'], p['y']
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = x2 - x1, y2 - y1
        dist = math.hypot(dx, dy)
        nx, ny = -dy / dist, dx / dist
        if ny > 0:
            nx, ny = -nx, -ny
        cx, cy = mx + nx * dist * .16, my + ny * dist * .16
        o.append(f'<path class="gm-arc" style="--i:{i}" pathLength="1" d="M{_r(x1)} {_r(y1)}Q{_r(cx)} {_r(cy)} {_r(x2)} {_r(y2)}"/>')
    o.append('</g><g class="gm-pins">')
    for i, pid in enumerate(use):
        p = pins[pid]
        o.append(f'<g class="gm-pin" style="--i:{i}" transform="translate({p["x"]} {p["y"]})"><circle class="dot" r="3.4"/></g>')
    o.append(f'<g class="gm-pin hub" transform="translate({hub["x"]} {hub["y"]})"><circle class="ring" r="4"/><circle class="ring r2" r="4"/><circle class="dot" r="5"/></g>')
    o.append('</g></svg>')
    return ''.join(o)


# ------------------------------------------------------------ components ----
def chips():
    out = []
    for rid in REGION_ORDER:
        c = REGION_COPY[rid]
        out.append(
            f'<button type="button" class="rchip" data-region="{rid}" aria-pressed="false" data-title="{E(GM["regions"][rid]["label"])}" '
            f'data-towns="{E(", ".join(c["towns"]))}" data-count="{len(GM["regions"][rid]["districts"])}">'
            f'<i class="fas {c["icon"]}" aria-hidden="true"></i><span>{E(c["chip"])}</span></button>')
    return ''.join(out)


def hero_map():
    return f"""<figure class="gmap-wrap" data-gmap-wrap>
  <div class="gmap-frame">{gmap_svg()}</div>
  <div class="gmap-info" aria-live="polite">
    <div class="gmap-info-idle">
      <strong>Pick a region or a town</strong>
      <span>Gold lines run from our office in Kalol. Tap a region to see where we work.</span>
    </div>
    <div class="gmap-info-live" hidden>
      <strong data-i="title"></strong>
      <span data-i="meta"></span>
      <a class="gmap-info-link" data-i="link" href="#regions">Read about this region <i class="fas fa-arrow-down" aria-hidden="true"></i></a>
    </div>
  </div>
</figure>
<div class="rchips" role="group" aria-label="Choose a region">{chips()}</div>"""


def ticker(words=None, label="Towns and corridors we cover"):
    items = ''.join(f'<li>{E(t)}</li>' for t in (words or TICKER))
    return (f'<div class="ticker" role="region" aria-label="{E(label)}">'
            f'<div class="ticker-track"><ul>{items}</ul><ul aria-hidden="true">{items}</ul></div></div>')


def region_cards():
    out = []
    for i, rid in enumerate(REGION_ORDER):
        c = REGION_COPY[rid]
        r = GM['regions'][rid]
        towns = ''.join(f'<li>{E(t)}</li>' for t in c['towns'])
        out.append(f"""<article class="region-card spot reveal" id="region-{rid}" data-region="{rid}">
  <div class="region-top"><div class="icon-ring"><i class="fas {c['icon']}" aria-hidden="true"></i></div><span class="region-count">{len(r['districts'])} district{'s' if len(r['districts']) != 1 else ''}</span></div>
  <h3>{E(r['label'])}</h3>
  <p>{E(c['blurb'])}</p>
  <ul class="town-pills">{towns}</ul>
  <button type="button" class="region-ask" data-enquire="Land in Gujarat — {E(c['chip'])}" data-interest="{LAND_BUY}">Ask about this region <i class="fas fa-arrow-right" aria-hidden="true"></i></button>
</article>""")
    return '\n'.join(out)


FAQ = [
    ("Can NRIs buy land in Gujarat?",
     "NRIs and OCI cardholders generally cannot buy agricultural land, plantation property or farmhouses in India. They can buy residential and commercial property, and can inherit land. These rules sit under FEMA and can change, so check the current RBI position before you commit."),
    ("Which documents should a seller keep ready?",
     "Recent 7/12 and 8A extracts, Village Form 6, the NA order and approved layout plan (if the land is non-agricultural), earlier sale deeds, property tax or revenue receipts, ID and PAN of every owner, heirship papers if the land was inherited, and a bank NOC if it is mortgaged."),
    ("How long does a land deal take?",
     "It depends on the paperwork. A clean, non-agricultural plot with every document in place can move quickly. Farm land, new tenure land and land with several co-owners or heirs usually takes longer because permissions and signatures have to be lined up first."),
    ("Do you give legal advice?",
     "No. We are real estate advisors, not a law firm. A title opinion from your own advocate is part of every careful land purchase. We help you collect and organise the documents that your lawyer will ask for."),
    ("Can I sell only part of my land?",
     "Part-sales usually need a sub-division or layout approval first, and farm land has minimum-size rules. Ask the revenue office what is allowed for your survey number before you promise a portion to anyone."),
    ("Is land near the coast or the border different?",
     "Yes. Coastal land can fall under Coastal Regulation Zone limits, and some border districts need extra permissions for transfers. Confirm both before you pay a token amount."),
]


def faq():
    out = []
    for i, (q, a) in enumerate(FAQ):
        out.append(f"""<div class="faq-item reveal">
  <button type="button" class="faq-q" aria-expanded="false" aria-controls="faq-a{i}" id="faq-q{i}"><span>{E(q)}</span><i class="fas fa-plus" aria-hidden="true"></i></button>
  <div class="faq-a" id="faq-a{i}" role="region" aria-labelledby="faq-q{i}"><div><p>{E(a)}</p></div></div>
</div>""")
    return '\n'.join(out)


def land_form(idp="l"):
    regs = ''.join(f'<option>{E(REGION_COPY[r]["chip"])}</option>' for r in REGION_ORDER)
    return f"""<div class="form-shell">
<form class="inquiry-form" novalidate data-project="Land in Gujarat">
  <div class="form-row">
    <div class="form-group"><input id="{idp}-name" name="name" type="text" placeholder=" " autocomplete="name" required/><label for="{idp}-name">Full name *</label><span class="field-error" aria-live="polite"></span></div>
    <div class="form-group"><input id="{idp}-phone" name="phone" type="tel" inputmode="tel" placeholder=" " autocomplete="tel" required/><label for="{idp}-phone">Phone *</label><span class="field-error" aria-live="polite"></span></div>
  </div>
  <div class="form-group"><input id="{idp}-email" name="email" type="email" placeholder=" " autocomplete="email"/><label for="{idp}-email">Email (optional)</label><span class="field-error" aria-live="polite"></span></div>
  <div class="form-row">
    <div class="form-group"><select id="{idp}-goal" name="goal" data-label="I want to"><option selected>Buy land</option><option>Sell land</option><option>Not sure yet</option></select><label for="{idp}-goal">I want to</label></div>
    <div class="form-group"><select id="{idp}-type" name="landtype" data-label="Land type"><option>NA / residential plot</option><option>Agricultural land</option><option>Industrial land</option><option>Commercial land</option><option>Bulk / development land</option><option>Not sure yet</option></select><label for="{idp}-type">Land type</label></div>
  </div>
  <div class="form-row">
    <div class="form-group"><select id="{idp}-region" name="region" data-label="Region">{regs}<option>Other / not sure</option></select><label for="{idp}-region">Region</label></div>
    <div class="form-group"><input id="{idp}-place" name="place" type="text" placeholder=" " data-label="Village / town / survey no."/><label for="{idp}-place">Village, town or survey no.</label></div>
  </div>
  <div class="form-group"><input id="{idp}-size" name="size" type="text" placeholder=" " data-label="Size / budget"/><label for="{idp}-size">Size or budget (optional)</label></div>
  <div class="form-row">
    <div class="form-group">
      <select id="{idp}-who" name="who" data-label="You are">
        <option>Buying for myself / family</option><option>Investor</option><option>NRI buyer</option><option>Selling my property</option><option>Broker / channel partner</option>
      </select><label for="{idp}-who">You are</label>
    </div>
    <div class="form-group">
      <select id="{idp}-when" name="when" data-label="Plan to buy">
        <option>Within 3 months</option><option>3 – 6 months</option><option>6 – 12 months</option><option>Just exploring</option>
      </select><label for="{idp}-when">Plan to buy</label>
    </div>
  </div>
  <div class="form-group"><textarea id="{idp}-message" name="message" rows="3" placeholder=" "></textarea><label for="{idp}-message">Anything else we should know (optional)</label></div>
  <div class="form-actions">
    <button type="submit" class="submit-btn wa-submit"><i class="fas fa-paper-plane"></i> <span class="btn-label">Send enquiry</span></button>
  </div>
  <p class="form-note"><i class="fas fa-lock"></i> Your data is secure. We never share your details with anyone without your consent. Your number is checked and confirmed on WhatsApp only to make sure every enquiry comes from a genuine buyer, not a fake one. To stop spam, we also note your device type and approximate location with the enquiry.</p>
</form>
<div class="form-success" role="status">
  <i class="fas fa-check-circle"></i><h3>Enquiry sent</h3><p data-s="msg"></p>
  <button type="button" class="cta-btn ghost small" data-form-reset>Start a new enquiry</button>
</div>
</div>"""


def home_land_card():
    return f"""<a href="land.html" class="dest-card land-card spot tilt reveal" data-tilt="2" data-rv="zoom">
  <div class="land-card-map" aria-hidden="true">{mini_svg()}</div>
  <div class="dest-body land-card-body">
    <span class="section-tag">All 34 districts</span>
    <h3>Land across Gujarat</h3>
    <p>Buy or sell plots, farm land, industrial and commercial parcels anywhere in the state. We check the documents first, then take you to the site.</p>
    <div class="dest-facts">
      <div><strong>34</strong>districts</div>
      <div><strong>6</strong>regions</div>
      <div><strong>Buy · Sell</strong>both sides of the deal</div>
    </div>
    <span class="cta-btn primary small">Explore land in Gujarat <i class="fas fa-arrow-right"></i></span>
  </div>
</a>"""


def projects_land_banner():
    return f"""<a href="land.html" class="promo-land spot reveal tilt" data-tilt="2">
  <div class="promo-land-map" aria-hidden="true">{mini_svg("gmap mini faint")}</div>
  <div class="promo-land-body">
    <span class="section-tag">Land in Gujarat</span>
    <h3>Want land instead of an apartment?</h3>
    <p>We also help you buy or sell plots, farm land, industrial and commercial land in every district of Gujarat.</p>
    <span class="go">See how land deals work <i class="fas fa-arrow-right"></i></span>
  </div>
</a>"""


LAND_CHIPS_MAP = [
    # icon, label, sub, kind, a, b, zoom
    ("fa-map", "Gujarat overview", "The whole state", "q", "Gujarat, India", None, 7),
    ("fa-city", "Ahmedabad–Gandhinagar", "Kalol, Sanand, GIFT City", "q", "Gandhinagar, Gujarat", None, 10),
    ("fa-industry", "Dholera region", "Special Investment Region", "q", "Dholera, Gujarat", None, 11),
    ("fa-water", "Surat–Bharuch", "South Gujarat", "q", "Surat, Gujarat", None, 9),
    ("fa-building", "Vadodara–Anand", "Central Gujarat", "q", "Vadodara, Gujarat", None, 10),
    ("fa-anchor", "Rajkot–Jamnagar", "Saurashtra", "q", "Rajkot, Gujarat", None, 9),
    ("fa-mountain-sun", "Bhuj–Mundra", "Kutch", "q", "Bhuj, Kutch, Gujarat", None, 9),
]


# ---------------------------------------------------------------- land posted by owners (listings + "post your land")
LAND_API = ""   # Google Apps Script web-app URL from the owner's Google Sheet (see tools/land-listings-apps-script.gs). Empty: posts arrive by email only.
DISTRICTS = ["Ahmedabad", "Amreli", "Anand", "Aravalli", "Banaskantha", "Bharuch", "Bhavnagar", "Botad", "Chhota Udaipur", "Dahod", "Dang",
             "Devbhumi Dwarka", "Gandhinagar", "Gir Somnath", "Jamnagar", "Junagadh", "Kheda", "Kutch", "Mahisagar", "Mehsana", "Morbi", "Narmada",
             "Navsari", "Panchmahal", "Patan", "Porbandar", "Rajkot", "Sabarkantha", "Surat", "Surendranagar", "Tapi", "Vadodara", "Valsad", "Vav-Tharad"]

def land_market():
    return f"""<section class="section" id="for-sale" data-land-market data-api="{E(LAND_API)}" data-static="assets/land-listings.json">
  <div class="container">
    <div class="section-header seq">
      <span class="section-tag">Land for sale</span>
      <h2>Land posted by owners</h2>
      <p>Each land is shown with its own boundary as the owner drew it, its area checked against the 7/12, and the maximum FSI for its zone. Ask us for the documents and a site visit.</p>
      <p class="lm-count" data-lm-count></p>
    </div>
    <div class="lm-grid" data-lm-list aria-live="polite"><div class="lm-empty"><i class="fas fa-spinner fa-spin"></i><p>Loading land listings…</p></div></div>
  </div>

  <div class="modal-overlay land-detail" id="landDetail" aria-hidden="true">
    <div class="modal-content" role="dialog" aria-modal="true" aria-labelledby="ldTitle">
      <button type="button" class="modal-close" aria-label="Close"><i class="fas fa-times"></i></button>
      <span class="project-category" data-ld="type"></span>
      <h2 id="ldTitle" data-ld="title"></h2>
      <div class="price" data-ld="price"></div>
      <div class="ld-views">
        <figure><div class="ld-3d" data-ld="3d"></div><figcaption>3D: the plot in its zone colour; the gold block shows the maximum built-up area (illustrative massing). Drag to turn, pinch or scroll to zoom. Red arrow points north.</figcaption></figure>
        <figure><div class="ld-map" data-ld="map"></div><figcaption>The exact boundary drawn by the owner, on satellite imagery.</figcaption></figure>
      </div>
      <h3 class="detail-h">What can be built (estimate)</h3>
      <div class="ld-fsi" data-ld="fsi"></div>
      <p class="ld-fine">Estimated under the Gujarat CGDCR-2017 tables for the zone and road the owner declared. The zoning certificate from the development authority, any TP-scheme deduction and later amendments decide the final figure; we check these before you pay anything.</p>
      <dl class="ld-facts" data-ld="facts"></dl>
      <p class="ld-checks"><i class="fas fa-shield-halved"></i> <span data-ld="checks"></span></p>
      <p class="ld-notes" data-ld="notes" hidden></p>
      <div class="btn-row">
        <button type="button" class="cta-btn primary" data-ld="enquire"><i class="fas fa-calendar-alt"></i> Enquire / site visit</button>
        <a class="cta-btn wa" data-ld="wa" href="#" target="_blank" rel="noopener noreferrer"><i class="fab fa-whatsapp"></i> WhatsApp</a>
        <a class="cta-btn ghost" data-ld="link" href="#" target="_blank" rel="noopener noreferrer nofollow" hidden><i class="fas fa-map-location-dot"></i> Owner's map link</a>
      </div>
    </div>
  </div>
</section>"""

def land_sell(idp="ls"):
    dl = ''.join(f'<option value="{E(d)}"></option>' for d in DISTRICTS)
    auth = ''.join(f'<option value="{k}">{E(v)}</option>' for k, v in [("AUDA", "AUDA / AMC (Ahmedabad)"), ("GUDA", "GUDA (Gandhinagar, outside GMC limits)"),
        ("SUDA", "SUDA / SMC (Surat)"), ("VUDA", "VUDA / VMC (Vadodara)"), ("RUDA", "RUDA / RMC (Rajkot)"), ("TOWN", "Other town development plan"),
        ("OUT", "Village land outside any development plan"), ("UNSURE", "Not sure")])
    def g(name, label, inp, cls=""):
        return f'<div class="form-group{cls}">{inp}<label for="{idp}-{name}">{label}</label><span class="field-error" aria-live="polite"></span></div>'
    def t(name, label, req=False, extra='', typ='text'):
        return g(name, label + (' *' if req else ''), f'<input id="{idp}-{name}" name="{name}" type="{typ}" placeholder=" " {extra}/>')
    def s(name, label, opts, req=False):
        return g(name, label + (' *' if req else ''), f'<select id="{idp}-{name}" name="{name}">{opts}</select>')
    o = lambda items: ''.join(f'<option value="{E(v)}">{E(l)}</option>' for v, l in items)
    return f"""<section class="section bg-alt" id="sell">
  <div class="container">
    <div class="section-header seq">
      <span class="section-tag">Sell your land</span>
      <h2>Post your land for sale</h2>
      <p>Fill in the details from your 7/12 or property card and draw the land on the map. We check the details, then publish your land on this page with its boundary, a 3D view and its FSI. Your phone number is never shown: buyers contact us, and we call you.</p>
    </div>
    <div class="ls-wrap panel reveal">
    <form class="inquiry-form ls-form" data-land-sell data-custom novalidate>
      <fieldset><legend>1. You</legend>
        <div class="form-row">{t('name', 'Full name (as on the 7/12)', True, 'autocomplete="name" maxlength="80"')}{t('phone', 'Mobile number (kept private)', True, 'inputmode="tel" autocomplete="tel" maxlength="20"', 'tel')}</div>
        <div class="form-row">{t('email', 'Email (optional)', False, 'autocomplete="email" maxlength="120"', 'email')}{s('role', 'You are', o([("Owner", "Owner"), ("Joint owner", "Joint owner"), ("Power of attorney holder", "Power of attorney holder"), ("Broker with written mandate", "Broker with the owner's written mandate")]))}</div>
      </fieldset>
      <fieldset><legend>2. The land (from the 7/12 or property card)</legend>
        <div class="form-row">{s('type', 'Land type', o([(x, x) for x in ["Agricultural (old tenure)", "Agricultural (new tenure)", "NA residential", "NA commercial", "NA industrial", "Final plot in a TP scheme"]]), True)}
          {g('district', 'District *', f'<input id="{idp}-district" name="district" type="text" list="{idp}-districts" placeholder=" " autocomplete="off" maxlength="40"/><datalist id="{idp}-districts">{dl}</datalist>')}</div>
        <div class="form-row">{t('taluka', 'Taluka', True, 'maxlength="60"')}{t('village', 'Village / town', True, 'maxlength="60"')}</div>
        <div class="form-row">{t('survey', 'Survey / block no. (7/12)', False, 'maxlength="60"')}{t('pcard', 'Property card / city survey no.', False, 'maxlength="60"')}</div>
        {t('tp', 'TP scheme and final plot no. (if any)', False, 'maxlength="80"')}
        <div class="form-row">{t('areaValue', 'Area as on the 7/12', True, 'inputmode="decimal" maxlength="20"')}
          {s('areaUnit', 'Unit', ''.join(f'<option value="{k}"{" selected" if k == "has" else ""}>{E(v)}</option>' for k, v in [("has", "Hectare-are-sq.m, e.g. 0-80-94"), ("sqm", "sq.m"), ("sqyd", "sq.yd (vaar)"), ("sqft", "sq.ft"), ("guntha", "guntha"), ("vigha16", "vigha = 16 guntha"), ("vigha20", "vigha = 20 guntha"), ("acre", "acre"), ("hectare", "hectare")]), True)}</div>
        <div class="form-row">{t('price', 'Asking price in ₹ (e.g. 25000000)', True, 'inputmode="numeric" maxlength="14"')}
          {s('priceUnit', 'Price is', o([("total", "Total for the land"), ("sqyd", "Per sq.yd"), ("sqm", "Per sq.m"), ("vigha16", "Per vigha"), ("acre", "Per acre")]), True)}</div>
        <p class="ls-price" data-ls-price aria-live="polite"></p>
      </fieldset>
      <fieldset><legend>3. Zoning</legend>
        <div class="form-row">{s('auth', 'Development authority', auth, True)}{s('zone', 'Zone', '', True)}</div>
        <div class="form-row">{s('road', 'Road touching the land', ''.join(f'<option value="{k}">{E(v)}</option>' for k, v in [("none", "No public road / kutcha track"), ("r6", "Under 9 m"), ("r9", "9 m to under 12 m"), ("r12", "12 m to under 18 m"), ("r18", "18 m to under 36 m"), ("r36", "36 m to under 45 m"), ("r45", "45 m and wider")]), True)}
          <label class="ls-check" hidden><input type="checkbox" name="corridor"/> <span>The land is within 200 m of this road</span></label></div>
      </fieldset>
      <fieldset><legend>4. Location and boundary</legend>
        {t('link', 'Google Maps link of the land', True, 'inputmode="url" maxlength="400"', 'url')}
        <p class="ls-help">Open Google Maps, drop a pin on your land, tap Share and paste the link here. Then tap each corner of the land on the satellite map below, in order around the boundary. Drag a corner to adjust it.</p>
        <div class="ls-tools"><button type="button" class="cta-btn ghost small" data-ls-locate><i class="fas fa-location-crosshairs"></i> I am at the land: use my location</button>
          <button type="button" class="cta-btn ghost small" data-ls-undo><i class="fas fa-rotate-left"></i> Undo corner</button>
          <button type="button" class="cta-btn ghost small" data-ls-clear><i class="fas fa-eraser"></i> Clear</button>
          <button type="button" class="cta-btn ghost small" data-ls-3d disabled><i class="fas fa-cube"></i> Preview in 3D</button></div>
        <div class="ls-map" data-ls-map tabindex="0" aria-label="Map: tap the corners of your land"></div>
        <p class="ls-area"><i class="fas fa-draw-polygon"></i> <span data-ls-area></span></p>
        <ul class="ls-checks" data-ls-checks aria-live="polite"></ul>
        <div class="ls-3d" data-ls-3dbox hidden></div>
        <div class="ls-fsi" data-ls-fsi aria-live="polite"></div>
        <span class="field-error" data-err="map" aria-live="polite"></span>
      </fieldset>
      <div class="form-group"><textarea id="{idp}-notes" name="notes" rows="3" maxlength="600" placeholder=" "></textarea><label for="{idp}-notes">Anything buyers should know (water, power, fencing, title status)</label></div>
      <label class="ls-check ls-consent"><input type="checkbox" name="consent"/> <span>I am the owner, or have the owner's written permission, and these details match the 7/12 / property card. I agree that the land, its boundary and price are shown on this website; my phone number and email stay private.</span><span class="field-error" data-err="consent" aria-live="polite"></span></label>
      <input type="text" name="_gotcha" tabindex="-1" autocomplete="off" aria-hidden="true" style="position:absolute;left:-9999px;width:1px;height:1px;opacity:0"/>
      <div class="form-actions"><button type="submit" class="submit-btn"><i class="fas fa-paper-plane"></i> <span class="btn-label">Check and post my land</span></button></div>
      <p class="form-note">We check the drawn area against the 7/12 area, the map link against the boundary, and the location against the authority you chose. Our team verifies every land before it is published, usually within a day. <i class="fas fa-lock"></i> Your phone number and email are never published or shared without your consent.</p>
    </form>
    <div class="form-success ls-done" data-ls-done role="status" hidden>
      <i class="fas fa-check-circle"></i><h3></h3><p></p>
      <button type="button" class="cta-btn ghost small" data-ls-again>Post another land</button>
    </div>
    </div>
  </div>
</section>"""
