#!/usr/bin/env python3
"""Assemble the Galaxy Estates Properties static site from shared partials + page bodies."""
import json, html, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import land_build as L
import global_build as G
import props_build as PB

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
OUT = '/home/claude/vr-realtors'

LOGO = "assets/logo.svg"
IMG = "https://township.homedeliveryrealtors.com/wp-content/uploads/"

PROJECTS = [
  dict(id="aster-neo", name="Aster Neo", cats=["2 BHK"], label="2 BHK", price="₹78 Lakhs*", priceLabel="Onwards, all inclusive",
       size="1205 sq.ft. (690 sq.ft. carpet)", possession="Ready to move", rera="PR/GJ/AHMEDABAD/AHMEDABAD CITY/AUDA/RAA11924/070623",
       img=IMG+"2026/03/aster-1024x819.png", color="#7FB3D5"),
  dict(id="embrace", name="Embrace", cats=["3 BHK"], label="3 BHK", price="₹1.42 Cr*", priceLabel="Onwards, all inclusive",
       size="100 sq.m. (1082 sq.ft. carpet)", possession="Nov 2027", rera="PR/GJ/AHMEDABAD/AHMEDABAD CITY/AUDA/RAA12526/251023",
       img=IMG+"2024/04/1920x1080-Birds-Eye-View-2-e1711971183783-768x604.jpg", color="#9B8AD6"),
  dict(id="elysium-novus", name="Elysium Novus", cats=["3 BHK"], label="3 BHK", price="₹1.23 Cr*", priceLabel="Onwards, all inclusive",
       size="975 – 1105 sq.ft. carpet", possession="Apr 2029", rera="PR/GJ/AHMEDABAD/AHMEDABAD CITY/Ahmedabad Urban Development Authority/RAA14729/270125/311228",
       img=IMG+"2025/05/Untitled-design-24-1024x768.png", color="#6FC2B0"),
  dict(id="greenfield", name="Greenfield", cats=["3 BHK", "4 BHK"], label="3 BHK + 4 BHK", price="₹1.73 Cr*", priceLabel="Onwards, all inclusive",
       size="2653 sq.ft. (1380 sq.ft. carpet)", possession="Dec 2029", rera="PR/GJ/AHMEDABAD/AHMEDABAD CITY/AUDA/RAA14879/250225/311229",
       img=IMG+"2025/05/WhatsApp-Image-2025-05-12-at-1.54.53-PM.jpeg", color="#8BC34A"),
  dict(id="ambrosia", name="Ambrosia", cats=["4 BHK"], label="4 BHK", price="₹2.49 Cr*", priceLabel="Onwards, all inclusive",
       size="3208 – 3707 sq.ft. (1784 – 2062 sq.ft. carpet)", possession="Jan 2027", rera="PR/GJ/GANDHINAGAR/GANDHINAGAR/AUDA/RAA10833/201022",
       img=IMG+"2023/07/Landscape-Green.jpg", color="#E8A87C"),
  dict(id="amogha", name="Amogha", cats=["3 BHK"], label="3 BHK", price="On request", priceLabel="Ask for resale availability",
       size="624.09 – 776.40 sq.ft. RERA carpet", possession="Completed", rera="PR/GJ/AHMEDABAD/DASKROI/AUDA/RAA08011/EX1/260224/280225",
       img="", color="#B0BEC5"),
  dict(id="paarijat", name="Paarijat", cats=["4 BHK"], label="4 BHK", price="₹2.49 Cr*", priceLabel="Onwards, all inclusive",
       size="3230 sq.ft. (1713 sq.ft. carpet)", possession="Ready to move", rera="PR/GJ/GANDHINAGAR/GANDHINAGAR/AUDA/RAA10759/121022",
       img=IMG+"2023/07/ggg-2-1-e1688386931572.webp", color="#F28FAD"),
  dict(id="shilp-skyline", name="Skyline", cats=["4 BHK"], label="4 BHK", price="₹2.23 Cr*", priceLabel="Onwards, all inclusive",
       size="3100 sq.ft. (1595 sq.ft. carpet)", possession="Sep 2029", rera="PR/GJ/AHMEDABAD/AHMEDABAD CITY/AUDA/RAA14084/020924/300929",
       img=IMG+"2025/05/WhatsApp-Image-2025-05-12-at-2.57.06-PM.jpeg", color="#5DADE2"),
  dict(id="belrosa", name="Belrosa", cats=["4 BHK"], label="4 BHK", price="₹5.32 Cr*", priceLabel="Onwards",
       size="5450 – 6800 sq.ft. (3000 – 3740 sq.ft. carpet)", possession="Sep 2030", rera="PR/GJ/GANDHINAGAR/GANDHINAGAR/AUDA/RAA15538/180725/310530",
       img=IMG+"2025/08/Untitled-design-768x702.png", color="#C9A962"),
  dict(id="shivalik-shantigram", name="Shivalik Shantigram, Signature Collection", cats=["4 BHK", "5 BHK"], label="4 & 5 BHK + 6 BHK penthouses", price="Price on call", priceLabel="Box price shared on call",
       size="4,147.57 – 11,953.54 sq.ft. RERA area", possession="Dec 2031 (tentative)", rera="Not yet received (developer’s sheet, Oct 2026). We confirm the registration before any booking",
       img="", color="#C8925E"),
  dict(id="north-park", name="The North Park", cats=["Villas"], label="Villas", price="On request", priceLabel="4 BHK villas",
       size="550 sq. yard saleable area", possession="On request", rera="PR/GJ/AHMEDABAD/AHMEDABAD CITY/AUDA/RAA01824/010318",
       img=IMG+"2025/05/Untitled-design-2.png", color="#D4AC6E"),
  dict(id="west-park", name="The West Park", cats=["Villas"], label="Villas", price="On request", priceLabel="Build-to-suit villas",
       size="648 sq. yard onwards", possession="On request", rera="PR/GJ/GANDHINAGAR/GANDHINAGAR/AUDA/RAA11300/020323",
       img=IMG+"2023/07/Villa-Render-1024x819.jpg", color="#E0C38C"),
]
import new_listings as NL
PROJECTS += [dict(p, img='', color='#C9A962') for p in NL.SH_NEW]
PB.GIFT += [p for p in NL.GIFT_NEW if p['id'] not in {q['id'] for q in PB.GIFT}]
for p in PROJECTS:
    kind = "villa community" if "Villas" in p["cats"] else f"{p['label']} residences"
    poss = ("ready to move" if p["possession"].startswith("Ready")
            else "possession date on request" if p["possession"] == "On request"
            else f"possession {p['possession']}")
    p["blurb"] = f"{p['name']} is a {kind} inside Adani Shantigram, {poss}. Sizes: {p['size']}. Starting prices marked * are indicative (as published by Adani Realty, checked 11 Oct 2026); ask us for the current price sheet."

for p in PROJECTS:
    p.update(PB.SH_EXTRA.get(p["id"], {}))
    p.setdefault("developer", "")
    p.update(market="shantigram", city="Ahmedabad", country="India", location="Adani Shantigram, Ahmedabad", regLabel="RERA", hue=40)
    p.setdefault("source", PB.SH_SOURCE)
    kind = "villa community" if "Villas" in p["cats"] else f"{p['label']} residences"
    poss = ("ready to move" if p["possession"].startswith("Ready")
            else "possession date on request" if p["possession"] == "On request"
            else f"possession {p['possession']}")
    p["blurb"] = f"{p['name']} is a {kind} inside Adani Shantigram, {poss}. Sizes: {p['size']}. Prices marked * are indicative, as published by the developer (checked 12 Oct 2026); ask us for the current price sheet."
    p.setdefault("total", PB.ASK_UNITS); p.setdefault("available", PB.ASK_AVAIL); p.setdefault("build", "")
    p["cats"] = ["Adani Shantigram"] + [("Villas & townhouses" if c == "Villas" else ("1-2 BHK / studio" if c == "2 BHK" else c)) for c in p["cats"]]
    if p["id"] == "shivalik-shantigram":
        p["blurb"] = ("Shivalik's Signature Collection inside Adani Shantigram, developed by Shivalik, Adesh and Adani and designed by Architect Hafeez Contractor. "
                      "Four towers on a 10,571 sq m (12,643 sq yd) plot on the edge of the golf course: one home per floor, 31 floors and 138.5 m tall, 4.3 m floor to floor, "
                      "4 & 5 BHK simplex homes and four-level 6 BHK penthouses. Every living room and deck faces the golf course, with the Narmada canal beyond. "
                      "Figures are from the developer's brochure (V4.0, Oct 2026). The box price is shared on call, RERA registration is not yet received and possession is Dec 2031 (tentative). "
                      "Plans and areas are indicative and may change.")
    if p["id"] == "belrosa":
        p["blurb"] = "Belrosa is the tallest residential tower in Adani Shantigram: 125 m and 32 floors, with 100 apartments and 8 duplexes from 4 to 6 BHK, possession Sep 2030. Prices are on request."
for p in PB.GIFT + PB.AHD + PB.INTL:
    p.setdefault("img", ""); p.setdefault("color", "#C9A962")
    p["blurb"] = (f"{p['name']} by {p['developer']} in {p['location']}, {p['country']}. {p['build']}. "
                  if p['developer'] and p['developer'] != 'Ask us' else f"{p['name']} in {p['location']}, {p['country']}. {p['build']}. ") + \
                 f"Checked against: {p['source']}. Prices and availability change, so ask us for the current price sheet."
ALL = PROJECTS + PB.GIFT + PB.AHD + PB.INTL
import official as OFF
_NEW = {p["id"] for p in NL.SH_NEW + NL.GIFT_NEW}
for p in ALL:     # blurbs and map links for the projects added 18 Oct 2026 (map link = centre of the RERA-registered plot)
    if p['id'] not in _NEW: continue
    where = 'inside Adani Shantigram' if p['market'] == 'shantigram' else 'in GIFT City'
    p['blurb'] = (f"{p['name']} by {p['developer']}, {where}: {p['label'].lower()}. {p['build']}. Possession: {p['possession']}. "
                  f"Checked against: {p['source']}. Prices marked * are indicative; ask us for the current price sheet.")
    _poly = (OFF.POLY.get('new:' + str(NL.RERA_ID.get(p['id']))) or {}).get('poly') or []
    if len(_poly) >= 3:
        p['mapq'] = f"{sum(q[0] for q in _poly) / len(_poly):.6f},{sum(q[1] for q in _poly) / len(_poly):.6f}"
import official as OFF
import country_build as CB
OFF.apply(ALL)
# every listing uses its own official exterior photo, stored on this site (assets/img/p/<id>.webp)
for p in ALL:
    f = os.path.join(OUT, 'assets', 'img', 'p', p['id'] + '.webp')
    if not os.path.exists(f):
        sys.exit('missing photo for ' + p['id'])
    p['img'] = 'assets/img/p/' + p['id'] + '.webp'
    p.setdefault('mapq', p['name'] + ', ' + p['location'])
for p in PROJECTS:
    p['mapq'] = {'shivalik-shantigram': 'Belvedere Golf and Country Club, Shantigram, Ahmedabad', 'shilp-skyline': 'Shilp Skyline, Adani Shantigram, Ahmedabad', 'greenfield': 'Shivalik Greenfield, Adani Shantigram, Ahmedabad'}.get(p['id'], 'Adani ' + p['name'] + ', Adani Shantigram, Ahmedabad')

E = html.escape

# Runs in <head> before first paint. 'js' = scripts are running, 'mo' = animations allowed,
# 'seen' = loader already shown this session. If the site scripts never start, the 4.5 s timer
# removes 'mo' (the class every hidden start state hangs on) so content is never lost.
JS_GATE = ("(function(d){var h=d.documentElement,c=h.classList;c.add('js');"
           "try{history.scrollRestoration='manual'}catch(e){}"
           "try{if(!matchMedia('(prefers-reduced-motion: reduce)').matches)c.add('mo')}catch(e){c.add('mo')}"
           "try{if(sessionStorage.getItem('ge_seen'))c.add('seen')}catch(e){}"
           "window.__geFS=setTimeout(function(){c.remove('mo');c.add('is-ready')},4500)})(document);")

import hashlib, base64
GATE_HASH = "sha256-" + base64.b64encode(hashlib.sha256(JS_GATE.encode()).digest()).decode()
# Content-Security-Policy: only this site's own scripts run; data may go only to the lead email service.
CSP = ("default-src 'self'; "
       f"script-src 'self' '{GATE_HASH}' https://www.googletagmanager.com; "
       "style-src 'self' 'unsafe-inline'; "
       "img-src 'self' data: blob: https://township.homedeliveryrealtors.com https://server.arcgisonline.com https://tile.openstreetmap.org https://*.google-analytics.com https://*.googletagmanager.com; "
       "font-src 'self' data:; "
       "connect-src 'self' https://*.google-analytics.com https://*.analytics.google.com https://*.googletagmanager.com https://formsubmit.co https://api.callmebot.com https://ipapi.co https://ipwho.is https://script.google.com https://script.googleusercontent.com; "
       "frame-src https://maps.google.com https://www.google.com; "
       "media-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests")

SITE_URL = "https://galaxyestatesproperties.co.in/"

def head(title, desc, page, extra="", fname="index"):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover"/>
<meta http-equiv="Content-Security-Policy" content="{CSP}"/>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-QXRN29DKLR"></script>
<script src="assets/ga.js"></script>
<meta name="referrer" content="strict-origin-when-cross-origin"/>
<meta name="google-site-verification" content="HE9_46DcpVA3ongsECA8PNhgCoWHJfCqUYxHAGLrgRI"/>
<meta name="google-site-verification" content="PnEn19TreyUuHWWwyu8MaODXWLLrcWz96qDNPAGMi3M"/>
<meta name="format-detection" content="telephone=no"/>
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}"/>
<meta name="theme-color" content="#040C18"/>
<meta property="og:type" content="website"/>
<meta property="og:title" content="{E(title)}"/>
<meta property="og:description" content="{E(desc)}"/>
<meta property="og:image" content="{IMG}2023/07/Landscape-Green.jpg"/>
<meta property="og:url" content="{SITE_URL}{"" if fname=="index" else fname+".html"}"/>
<link rel="canonical" href="{SITE_URL}{"" if fname=="index" else fname+".html"}"/>
<link rel="icon" type="image/svg+xml" href="{LOGO}"/>
<link rel="preconnect" href="https://township.homedeliveryrealtors.com"/>
<link rel="stylesheet" href="assets/vendor/fonts.css"/>
<link rel="stylesheet" href="assets/vendor/fa/all.min.css"/>
<script>{JS_GATE}</script>
<link rel="stylesheet" href="assets/style.css"/>
<link rel="stylesheet" href="assets/motion.css"/>
{('<script type="application/ld+json">' + json.dumps(BUSINESS_LD, ensure_ascii=False) + '</script>') if fname in ('index', 'contact') else ''}
{extra}</head>
<body data-page="{page}">
<div class="page-loader" aria-hidden="true"><div class="loader-mark"><img src="{LOGO}" alt="" width="64" height="64"/><span>Galaxy Estates Properties</span><div class="loader-bar"></div></div></div>
<div class="page-fade" aria-hidden="true"></div>
<div class="scroll-progress" aria-hidden="true"><span></span></div>
<a href="#main" class="sr-only">Skip to content</a>
"""

def nav(solid=False):
    return f"""
<header class="navbar{' solid' if solid else ''}" id="navbar">
  <div class="container navbar-container">
    <a href="index.html" class="logo" aria-label="Galaxy Estates Properties home">
      <img src="{LOGO}" alt="" class="logo-img" width="44" height="44"/>
      <span class="logo-text"><b>Galaxy Estates</b><small>Properties</small></span>
    </a>
    <div class="nav-menu-wrap" id="navMenu">
      <nav aria-label="Main">
        <ul class="nav-menu">
          <li><a href="index.html" class="nav-link" data-page="home">Home</a></li>
          <li class="has-dropdown">
            <button type="button" class="nav-link" aria-expanded="false" aria-haspopup="true">Properties <i class="fas fa-chevron-down"></i></button>
            <ul class="dropdown">
              <li><a href="projects.html" data-page="projects"><i class="fas fa-th-large"></i><span><strong>All properties</strong><small>{len(ALL)} listings in India and abroad</small></span></a></li>
              <li><a href="shantigram.html" data-page="shantigram"><i class="fas fa-tree"></i><span><strong>Adani Shantigram</strong><small>Township explorer in 3D</small></span></a></li>
              <li><a href="gift-city.html" data-page="gift-city"><i class="fas fa-city"></i><span><strong>GIFT City</strong><small>India's first IFSC, in 3D</small></span></a></li>
            </ul>
          </li>
          <li><a href="land.html" class="nav-link" data-page="land">Gujarat Land</a></li>
          <li class="has-dropdown">
            <button type="button" class="nav-link" aria-expanded="false" aria-haspopup="true">Global <i class="fas fa-chevron-down"></i></button>
            <ul class="dropdown">
              <li><a href="global.html" data-page="global"><i class="fas fa-earth-asia"></i><span><strong>All markets</strong><small>{len(G.MARKETS)} countries and cities abroad</small></span></a></li>
{''.join(f'              <li><a href="{c["slug"]}.html" data-page="{c["slug"]}"><i class="fas fa-location-dot"></i><span><strong>{E(c["title"])}</strong><small>Guide for Indian investors</small></span></a></li>' + chr(10) for c in CB.COUNTRIES)}            </ul>
          </li>
          <li><a href="virtual-tours.html" class="nav-link" data-page="virtual-tours">Virtual Tours</a></li>
          <li><a href="about.html" class="nav-link" data-page="about">About</a></li>
          <li><a href="contact.html" class="nav-link" data-page="contact">Contact</a></li>
        </ul>
      </nav>
      <div class="drawer-extra">
        <button type="button" class="cta-btn primary" data-enquire="Private site visit"><i class="fas fa-calendar-alt"></i> Book a site visit</button>
        <a href="#" class="cta-btn wa" data-whatsapp target="_blank" rel="noopener noreferrer"><i class="fab fa-whatsapp"></i> WhatsApp us</a>
        <a href="tel:+918488062309" class="cta-btn secondary" data-phone><i class="fas fa-phone"></i> +91 84880 62309</a>
      </div>
    </div>
    <div class="nav-actions">
      <a href="tel:+918488062309" class="nav-phone" data-phone aria-label="Call +91 84880 62309"><i class="fas fa-phone"></i><span>+91 84880 62309</span></a>
      <button type="button" class="consultation-btn" id="scheduleBtn">Schedule visit</button>
      <button type="button" class="mobile-menu-btn" id="hamburger" aria-label="Open menu" aria-expanded="false" aria-controls="navMenu"><span></span><span></span><span></span></button>
    </div>
  </div>
</header>
<div class="nav-backdrop"></div>
"""

def form(idp, project="General enquiry"):
    return f"""<div class="form-shell">
<form class="inquiry-form" novalidate data-project="{E(project)}">
  <div class="form-row">
    <div class="form-group"><input id="{idp}-name" name="name" type="text" placeholder=" " autocomplete="name" required/><label for="{idp}-name">Full name *</label><span class="field-error" aria-live="polite"></span></div>
    <div class="form-group"><input id="{idp}-phone" name="phone" type="tel" inputmode="tel" placeholder=" " autocomplete="tel" required/><label for="{idp}-phone">Phone *</label><span class="field-error" aria-live="polite"></span></div>
  </div>
  <div class="form-group"><input id="{idp}-email" name="email" type="email" placeholder=" " autocomplete="email"/><label for="{idp}-email">Email (optional)</label><span class="field-error" aria-live="polite"></span></div>
  <div class="form-row">
    <div class="form-group">
      <select id="{idp}-interest" name="interest" data-label="Interested in">
        <option>2 BHK Apartments</option><option selected>3 BHK Apartments</option><option>4 BHK Apartments</option>
        <option>5 BHK &amp; penthouses</option><option>Penthouses</option><option>Villas</option><option>GIFT City — Residential</option><option>GIFT City — Commercial</option><option>Offices &amp; showrooms — Ahmedabad</option><option>Investment advice</option><option>Land in Gujarat — Buy</option><option>Land in Gujarat — Sell</option><option>Global property</option>
      </select><label for="{idp}-interest">Interested in</label>
    </div>
    <div class="form-group">
      <select id="{idp}-visit" name="visit" data-label="Preferred visit">
        <option>Weekday morning</option><option>Weekday evening</option><option selected>Weekend</option><option>Video call walkthrough</option>
      </select><label for="{idp}-visit">Preferred visit</label>
    </div>
  </div>
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
  <div class="form-group"><textarea id="{idp}-message" name="message" rows="3" placeholder=" "></textarea><label for="{idp}-message">Message (optional)</label></div>
  <div class="form-actions">
    <button type="submit" class="submit-btn wa-submit"><i class="fas fa-paper-plane"></i> <span class="btn-label">Send enquiry</span></button>
  </div>
  <p class="form-note"><i class="fas fa-lock"></i> Your data is secure. We never share your details with anyone without your consent. Every enquiry is checked only to make sure it comes from a genuine buyer, not a fake one. To stop spam, we also note your device type and approximate location with the enquiry.</p>
</form>
<div class="form-success" role="status">
  <i class="fas fa-check-circle"></i><h3>Enquiry sent</h3><p data-s="msg"></p>
  <button type="button" class="cta-btn ghost small" data-form-reset>Start a new enquiry</button>
</div>
</div>"""

def footer():
    return f"""
<footer class="footer">
  <div class="container">
    <div class="footer-grid stagger">
      <div class="footer-brand">
        <a href="index.html" class="logo"><img src="{LOGO}" alt="" class="logo-img" width="44" height="44"/><span class="logo-text"><b>Galaxy Estates</b><small>Properties</small></span></a>
        <p>Authorised channel partner for Adani Shantigram, advising buyers on homes and investments across Ahmedabad and GIFT City, on buying or selling land across Gujarat, and on property abroad.</p>
        <div class="socials">
          <a href="#" data-whatsapp target="_blank" rel="noopener noreferrer" aria-label="WhatsApp"><i class="fab fa-whatsapp"></i></a>
          <a href="tel:+918488062309" data-phone aria-label="Call"><i class="fas fa-phone"></i></a>
        </div>
      </div>
      <div class="footer-col">
        <h4>Explore</h4>
        <ul>
          <li><a href="index.html">Home</a></li>
          <li><a href="projects.html">All properties</a></li>
          <li><a href="shantigram.html">Adani Shantigram</a></li>
          <li><a href="gift-city.html">GIFT City</a></li>
          <li><a href="land.html">Land in Gujarat</a></li>
          <li><a href="global.html">Global property</a></li>
          <li><a href="virtual-tours.html">Virtual tours</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>About</h4>
        <ul>
          <li><a href="about.html">About us</a></li>
          <li><a href="contact.html">Contact</a></li>
          <li><a href="virtual-tours.html#3d-renders">3D renderings</a></li>
          <li><a href="shantigram.html#location">Location map</a></li>
          <li><button type="button" data-enquire="Private site visit">Book a site visit</button></li>
        </ul>
      </div>
      <div>
        <h4>Contact</h4>
        <ul class="footer-contact">
          <li><i class="fas fa-phone"></i><a href="tel:+918488062309" data-phone>+91 84880 62309</a></li>
          <li><i class="fab fa-whatsapp"></i><a href="#" data-whatsapp target="_blank" rel="noopener noreferrer">Chat on WhatsApp</a></li>
          <li><i class="fas" aria-hidden="true"><svg viewBox="0 0 512 512" width="1em" height="1em" fill="currentColor" aria-hidden="true" style="vertical-align:-.125em"><path d="M48 96h416a32 32 0 0 1 32 32v16L256 288 16 144v-16a32 32 0 0 1 32-32zM16 181.3 256 325.3l240-144V384a32 32 0 0 1-32 32H48a32 32 0 0 1-32-32z"/></svg></i><a href="mailto:director@galaxyestatesproperties.co.in" style="min-width:0;overflow-wrap:anywhere">director@galaxyestatesproperties.co.in</a></li>
          <li><i class="fas fa-map-marker-alt"></i><span>Office: Kalol, Gujarat</span></li>
        </ul>
      </div>
    </div>
    <div class="footer-disclaimer reveal">
      <p><strong>THIS WEBSITE IS OWNED AND MANAGED BY GALAXY ESTATES PROPERTIES, A REAL ESTATE ADVISORY AND CHANNEL PARTNER FIRM SERVING CLIENTS ACROSS INDIA AND AROUND THE WORLD.</strong></p>
      <p data-rera-wrap hidden>Agency RERA No. <span data-rera-value></span></p>
      <p class="disclaimer-text">Disclaimer: This website is owned and operated by Galaxy Estates Properties, an independent real estate advisory and channel partner firm. It is not the official website of any developer. Project names, images and trademarks belong to their respective owners and are used only to identify the projects. Project details, prices, floor plans and RERA numbers are sourced from the developers and the RERA portal and are for information only; they are not an offer or a contract. Prices marked * are indicative and subject to change, and availability is confirmed at the time of booking. 3D models and renders are illustrative and not to scale. Please verify all details with the developer and on the RERA website before you make a decision.</p>
    </div>
    <div class="footer-bottom reveal">
      <span>© <span data-year>2026</span> Galaxy Estates Properties. All rights reserved.</span>
      <span>Kalol · Gandhinagar · Ahmedabad · Gujarat</span>
    </div>
  </div>
</footer>
"""

def overlays():
    return f"""
<a href="#" class="whatsapp-widget" data-whatsapp target="_blank" rel="noopener noreferrer" aria-label="Chat on WhatsApp">
  <i class="fab fa-whatsapp"></i><span class="widget-tooltip">Chat with us</span>
</a>
<button type="button" class="scroll-to-top" id="scrollTop" aria-label="Back to top">
  <svg viewBox="0 0 48 48" aria-hidden="true"><circle class="track" cx="24" cy="24" r="22"/><circle class="prog" cx="24" cy="24" r="22"/></svg>
  <i class="fas fa-arrow-up"></i>
</button>
"""

def modals():
    """The enquiry and detail pop-ups are the same on every page: they ship once in assets/overlays.js (cached) instead of in every HTML file."""
    return f"""
<div class="modal-overlay" id="modalOverlay" aria-hidden="true">
  <div class="modal-content" role="dialog" aria-modal="true" aria-labelledby="modalTitle">
    <button type="button" class="modal-close" aria-label="Close"><i class="fas fa-times"></i></button>
    <h2 id="modalTitle">Book a private visit</h2>
    <p class="modal-subtitle" id="modalSubtitle">Private consultation</p>
    {form('m')}
  </div>
</div>

<div class="modal-overlay" id="detailOverlay" aria-hidden="true">
  <div class="modal-content detail-modal" role="dialog" aria-modal="true" aria-labelledby="dName">
    <button type="button" class="modal-close" aria-label="Close"><i class="fas fa-times"></i></button>
    <div class="detail-media"><img data-d="img" alt="" src="data:image/gif;base64,R0lGODlhAQABAAAAACw="/><div class="project-art" data-d="art" hidden aria-hidden="true"><span class="pa-city" data-d="artcity"></span><span class="pa-country" data-d="artcountry"></span></div></div>
    <div class="detail-body">
      <span class="project-category" data-d="cat"></span>
      <h2 id="dName" data-d="name"></h2>
      <p class="project-location"><i class="fas fa-map-marker-alt"></i> <span data-d="loc"></span> <a class="project-map" data-d="map" href="https://www.google.com/maps" target="_blank" rel="noopener noreferrer">View on Google Maps</a></p>
      <p class="project-dev" data-d="devwrap">by <span data-d="dev"></span></p>
      <div class="price" data-d="price"></div><span class="price-label" data-d="plabel"></span>
      <p class="detail-blurb" data-d="blurb"></p>
      <p class="travel-refund" data-d="refund" hidden><i class="fas fa-plane"></i> <span><strong>Travel cost refunded.</strong> Fly out to see it before you buy: when your purchase completes through us, we refund your travel cost for the visit.</span></p>
      <dl class="unit-strip big">
        <div><dt>Total units</dt><dd data-d="total"></dd></div>
        <div><dt>Available</dt><dd data-d="avail"></dd></div>
        <div><dt>Possession</dt><dd data-d="poss"></dd></div>
      </dl>
      <h3 class="detail-h">Unit types, sizes and prices</h3>
      <div class="mix-wrap"><table class="mix-table">
        <thead><tr><th scope="col">Unit type</th><th scope="col">Size</th><th scope="col">Price</th><th scope="col">Available</th></tr></thead>
        <tbody data-d="mix"></tbody>
      </table></div>
      <div class="detail-specs">
        <div class="wide"><small>Overall size range</small><strong data-d="size"></strong></div>
        <div class="wide" data-d="buildwrap"><small>Project</small><strong data-d="build"></strong></div>
        <div class="wide"><small data-d="reglabel">RERA</small><strong data-d="rera" style="font-size:.8rem;word-break:break-word"></strong></div>
      </div>
      <p class="detail-source">Source: <span data-d="source"></span>. Prices and availability change; we confirm both before you book.</p>
      <div class="btn-row">
        <button type="button" class="cta-btn primary" data-d="enquire"><i class="fas fa-calendar-alt"></i> Enquire</button>
        <a class="cta-btn wa" data-d="wa" href="#" target="_blank" rel="noopener noreferrer"><i class="fab fa-whatsapp"></i> WhatsApp</a>
      </div>
      <a class="cta-btn ghost" data-d="page" href="projects.html" style="width:100%;margin-top:12px"><i class="fas fa-file-lines"></i> Open the full project page</a>
      <a class="cta-btn ghost" data-d="3d" href="shantigram.html#explorer" style="width:100%;margin-top:12px"><i class="fas fa-cube"></i> See it in the 3D township</a>
    </div>
  </div>
</div>
"""

def scripts(extra=""):
    return f"""<script src="assets/overlays.js"></script>
<script src="assets/data.js"></script>
<script src="assets/main.js"></script>
<script src="assets/motion.js"></script>
{extra}</body>
</html>
"""

def short_avail(v):
    return "On request" if (not v or v.startswith("Ask")) else v.split(" (")[0]

def card(p, delay=0):
    cats = "|".join(p["cats"])
    sh = p["market"] == "shantigram"
    abroad = p["market"] == "abroad"
    if p.get("img"):
        media = f'<img src="{p["img"]}" alt="{E(p["name"])}, {E(p["label"])}, {E(p["location"])}" loading="lazy" width="768" height="600"/>'
    else:
        media = (f'<div class="project-art" style="--hue:{p.get("hue", 40)}" aria-hidden="true"><span class="pa-city">{E(p["city"])}</span>' +
                 (f'<span class="pa-country">{E(p["country"])}</span>' if p["country"] != p["city"] else '') + '</div>')
    corner = (f'<a class="project-3d-link" href="shantigram.html?focus={p["id"]}#explorer"><i class="fas fa-cube"></i> View in 3D</a>' if sh
              else f'<span class="project-flag"><i class="fas {"fa-earth-asia" if abroad else ("fa-leaf" if "Weekend villas & plots" in p["cats"] else "fa-city")}"></i> {"International" if abroad else ("GIFT City" if p["market"] == "gift" else ("Commercial" if "Commercial" in p["cats"] else ("Weekend homes" if "Weekend villas & plots" in p["cats"] else "Ahmedabad")))}</span>')
    import urllib.parse as _u
    maplink = f'<a class="project-map" href="https://www.google.com/maps/search/?api=1&amp;query={_u.quote_plus(p["mapq"])}" target="_blank" rel="noopener noreferrer" aria-label="{E(p["name"])} on Google Maps">Map</a>'
    dev = f'<p class="project-dev">by <span data-f="developer">{E(p["developer"])}</span></p>' if p.get("developer") and p["developer"] != "Ask us" else ''
    loc = p["location"] + ("" if p["country"] == "India" or p["country"] in p["location"] else ", " + p["country"])
    return f"""<article class="project-card reveal tilt" data-tilt="4" data-pid="{p['id']}" data-market="{p['market']}" data-category="{E(cats)}" style="--d:{delay:.2f}s">
  <div class="project-image" data-detail="{p['id']}" role="button" tabindex="0" aria-label="View details for {E(p['name'])}">
    {media}
    <span class="project-category">{E(p['label'])}</span>
    {corner}
  </div>
  <div class="project-content">
    <h3><a class="project-link" href="{p.get('page', 'projects.html')}">{E(p['name'])}</a></h3>
    <p class="project-location"><i class="fas fa-map-marker-alt"></i> <span>{E(loc)}</span> {maplink}</p>
    {dev}
    <div class="project-price"><span class="price" data-f="price">{E(p['price'])}</span><span class="price-label" data-f="priceLabel">{E(p['priceLabel'])}</span></div>
    {'<p class="travel-refund small"><i class="fas fa-plane"></i> <span>Travel cost refunded on purchase</span></p>' if abroad else ''}
    <ul class="project-specs">
      <li><i class="fas fa-ruler-combined"></i> <span data-f="size">{E(p['size'])}</span></li>
      <li><i class="fas fa-key"></i> <span>Possession: <span data-f="possession">{E(p['possession'])}</span></span></li>
    </ul>
    <dl class="unit-strip">
      <div><dt>Total units</dt><dd data-f="total">{E(p['total'])}</dd></div>
      <div><dt>Available</dt><dd data-f="available" data-short>{E(short_avail(p['available']))}</dd></div>
      <div><dt>Unit types</dt><dd>{len(p['mix'])}</dd></div>
    </dl>
    <div class="project-actions">
      <button type="button" class="btn-know-more" data-detail="{p['id']}">Full details</button>
      <button type="button" class="btn-enquire" data-enquire="{p['id']}">Enquire now</button>
    </div>
    <p class="project-rera">{E(p['regLabel'])}: <span data-f="rera">{E(p['rera'])}</span></p>
  </div>
</article>"""

def cards(ids=None):
    ps = ALL if ids is None else [next(p for p in ALL if p['id'] == i) for i in ids]
    return "\n".join(card(p, (i % 3) * 0.08) for i, p in enumerate(ps))

def more_markets():
    tiles = "".join(f'<a class="more-market" href="global.html#market-{k}"><span>{E(n)}</span><small>Shortlist on request</small></a>' for k, n in PB.MORE_MARKETS)
    return f"""<div class="more-markets reveal" data-market-block="abroad">
  <p><strong>More markets.</strong> We also source property in these markets; ask for a current shortlist with unit sizes and prices.</p>
  <div class="more-market-row">{tiles}</div>
</div>"""


RENDER_META = {
  "shivalik-shantigram": ("Architect's render", "Architect Hafeez Contractor's render of the four Shivalik Signature towers. Explore every floor in 3D on its page."),
  "aster-neo": ("3D exterior", "Modern 2 BHK tower with a clean contemporary facade and podium greens."),
  "embrace": ("3D aerial", "Aerial perspective of the Embrace towers with landscaped grounds."),
  "amogha": ("Exterior", "Amogha's eight wings of ground + 14 floors along the township road, from Adani Realty."),
  "elysium-novus": ("3D master plan", "Master-plan rendering with podium amenities, towers and landscaping."),
  "greenfield": ("3D exterior", "Architectural rendering of the Greenfield residential towers."),
  "ambrosia": ("3D landscape", "Landscaped greens and amenity deck of the Ambrosia towers."),
  "paarijat": ("3D exterior", "Render of the Paarijat 4 BHK residences."),
  "belrosa": ("3D exterior", "Render of the Belrosa 4 BHK residences, from 5450 sq.ft."),
  "north-park": ("3D exterior", "4, 5 and 6 BHK villas across North Park phases 2–7 and The North Park (phase 8)."),
  "west-park": ("3D villa", "Build-to-suit villa rendering at West Park."),
  "shilp-skyline": ("3D exterior", "Render of the Skyline 4 BHK residences."),
  "inspire-business-park": ("Photo", "The completed Inspire Business Park: Crown office buildings and Crest corporate houses."),
  "inspire-corporate-capital": ("3D exterior", "The two glass office blocks of Inspire Corporate Capital."),
  "inspire-edge": ("3D exterior", "Inspire Edge office building in Shantigram's business district."),
  "adani-center-point": ("3D exterior", "Center Point retail centre by Vaishnodevi Circle."),
  "amora": ("3D exterior", "Amora's 3 BHK towers above high-street retail."),
  "storeys-golf-coast": ("3D exterior", "The Storeys Golf Coast towers from the Belvedere golf course."),
  "storeys-infinity": ("3D exterior", "East and West towers of The Storeys Infinity."),
  "the-storeys": ("Photo", "The two completed towers of The Storeys on the Belvedere golf course, from Adani Realty."),
  "ikaria": ("Photo", "Ikaria senior-living building, drone photo."),
}
def renders():
    out = []
    for i, p in enumerate(PROJECTS):
        if p["id"] not in RENDER_META: continue
        badge, text = RENDER_META[p["id"]]
        out.append(f'''<article class="render-card reveal" data-pid="{p['id']}" style="--d:{(i % 3) * 0.06:.2f}s">
  <span class="render-badge">{E(badge)}</span>
  <button type="button" class="render-img" data-lightbox="renders" data-src="{p['img']}" data-caption="{E(p['name'])} — {E(badge)}" aria-label="View {E(p['name'])} render full screen">
    <img src="{p['img']}" alt="{E(p['name'])} 3D render" loading="lazy" width="768" height="600"/>
    <span class="render-play"><i class="fas fa-expand-alt"></i></span>
  </button>
  <div class="render-info">
    <h3><a class="project-link" href="{p.get('page', 'projects.html')}">{E(p['name'])}</a></h3>
    <p>{E(text)}</p>
    <div class="render-meta"><span><i class="fas fa-home"></i> {E(p['label'])}</span><span><i class="fas fa-ruler-combined"></i> {E(p['size'].split(' (')[0])}</span><span><i class="fas fa-key"></i> <span data-f="possession">{E(p['possession'])}</span></span></div>
    <button type="button" class="render-btn" data-enquire="{p['id']}"><i class="fas fa-images"></i> Get full render pack</button>
  </div>
</article>''')
    return "\n".join(out)

def filters():
    keys = ["All", "Adani Shantigram", "Ahmedabad & Gandhinagar", "GIFT City", "Commercial", "Weekend villas & plots", "International", "Villas & townhouses"]
    out = []
    for k in keys:
        on = k == "All"
        out.append(f'<button type="button" class="filter-btn{" active" if on else ""}" data-filter="{E(k)}" aria-pressed="{"true" if on else "false"}">{"All properties" if on else E(k)}</button>')
    return '<div class="project-filters reveal" role="group" aria-label="Filter properties">\n  ' + "\n  ".join(out) + '\n</div>'
FILTERS = None


def cta(title="Ready to see it in person?", text="Our advisors arrange private site visits, video walkthroughs and current price sheets for every project we represent.",
        label="Book a site visit", icon="fa-calendar-alt", enquire="Private site visit", interest="", wa="", tag="Private consultation"):
    di = f' data-interest="{E(interest)}"' if interest else ''
    dw = f' data-whatsapp="{E(wa)}"' if wa else ' data-whatsapp'
    return f"""
<section class="section cta-section">
  <div class="stars" aria-hidden="true"></div>
  <div class="container">
    <div class="cta-content seq">
      <span class="section-tag">{tag}</span>
      <h2 class="grad-text">{title}</h2>
      <p>{text}</p>
      <div class="btn-row">
        <button type="button" class="cta-btn large primary" data-enquire="{E(enquire)}"{di}><i class="fas {icon}"></i> {label}</button>
        <a href="#"{dw} class="cta-btn large wa" target="_blank" rel="noopener noreferrer"><i class="fab fa-whatsapp"></i> WhatsApp us</a>
      </div>
    </div>
  </div>
</section>"""

def gmap_q(q, z=14):
    from urllib.parse import quote_plus
    return f"https://maps.google.com/maps?q={quote_plus(q)}&z={z}&hl=en&output=embed"
def gmap_dir(a, b):
    from urllib.parse import quote_plus
    return f"https://maps.google.com/maps?saddr={quote_plus(a)}&daddr={quote_plus(b)}&hl=en&output=embed"
def gopen_q(q):
    from urllib.parse import quote_plus
    return f"https://www.google.com/maps/search/?api=1&query={quote_plus(q)}"
def gopen_dir(a, b):
    from urllib.parse import quote_plus
    return f"https://www.google.com/maps/dir/?api=1&origin={quote_plus(a)}&destination={quote_plus(b)}"

def map_block(title, intro, chips, note):
    """chips: list of (icon, label, sub, kind, a, b)"""
    out = []
    for i, ch in enumerate(chips):
        icon, label, sub, kind, a, b = ch[:6]
        z = ch[6] if len(ch) > 6 else 14
        emb = gmap_q(a, z) if kind == 'q' else gmap_dir(a, b)
        opn = gopen_q(a) if kind == 'q' else gopen_dir(a, b)
        out.append(f'<button type="button" class="map-chip{" active" if i == 0 else ""}" aria-pressed="{"true" if i == 0 else "false"}" data-embed="{E(emb)}" data-open="{E(opn)}"><i class="fas {icon}"></i><span><strong>{E(label)}</strong><small>{E(sub)}</small></span></button>')
    first_open = gopen_q(chips[0][4]) if chips[0][3] == 'q' else gopen_dir(chips[0][4], chips[0][5])
    return f"""<div class="map-wrap reveal" data-map>
  <div class="map-side">
    <h3>{title}</h3>
    <p>{intro}</p>
    <div class="map-chips">{''.join(out)}</div>
    <div class="map-actions">
      <a class="cta-btn primary small" data-map-open href="{E(first_open)}" target="_blank" rel="noopener noreferrer"><i class="fas fa-location-arrow"></i> Open in Google Maps</a>
      <button type="button" class="cta-btn ghost small" data-enquire="Site visit request"><i class="fas fa-calendar-alt"></i> Request a site visit</button>
    </div>
  </div>
  <div class="map-frame loading">
    <div class="map-fallback"><i class="fas fa-map-location-dot"></i><strong data-fb="label">Live map</strong><span data-fb="sub">Opens in Google Maps</span><a class="cta-btn primary small" data-fb-open href="{E(first_open)}" target="_blank" rel="noopener noreferrer"><i class="fas fa-location-arrow"></i> Open in Google Maps</a></div>
    <iframe title="{E(title)} — Google map" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe>
    <div class="map-spinner"><span></span></div>
    <div class="x-group map-toggle" role="group" aria-label="Map style">
      <button type="button" class="active" data-mode="day"><i class="fas fa-sun"></i> Day</button>
      <button type="button" data-mode="night"><i class="fas fa-moon"></i> Night</button>
    </div>
  </div>
</div>
<p class="map-note">{note}</p>"""

def explorer_ui(legend_title, legend_sub, modes=("day", "dusk", "night"), views=(), extra_cls=""):
    icons = {"day": "fa-sun", "dusk": "fa-cloud-sun", "night": "fa-moon"}
    modes = ("night", "dusk", "day")
    mb = "".join(f'<button type="button" data-mode="{m}"><i class="fas {icons[m]}"></i> {m.title()}</button>' for m in modes)
    vb = "".join(f'<button type="button" data-view="{k}">{E(v)}</button>' for k, v in views)
    return f"""<div class="explorer-loading"><div>Loading the 3D map<div class="loader-bar"></div></div></div>
  <div class="x-labels" aria-hidden="true"></div>
  <div class="x-tooltip" aria-hidden="true"></div>
  <div class="explorer-ui">
    <div class="x-legend">
      <div class="x-legend-head"><h4>{legend_title}<small>{legend_sub}</small></h4><button type="button" class="x-legend-toggle" aria-label="Show list"><i class="fas fa-list"></i></button></div>
      <ul></ul>
      <div class="x-legend-foot">Roads, water, golf course and existing buildings from OpenStreetMap. Project plots: the outlines registered on the Gujarat RERA map service (developer map pins where none matches). Floors from the RERA unit lists and published floor counts; footprints from OpenStreetMap where mapped, otherwise estimated.</div>
    </div>
    <div class="x-toolbar">
      <div class="x-group" role="group" aria-label="Lighting">{mb}</div>
      {f'<div class="x-group views" role="group" aria-label="Camera views">{vb}</div>' if vb else ''}
      <div class="x-group icons" role="group" aria-label="Camera controls">
        <button type="button" data-zoom="in" aria-label="Zoom in"><i class="fas fa-plus"></i></button>
        <button type="button" data-zoom="out" aria-label="Zoom out"><i class="fas fa-minus"></i></button>
        <button type="button" data-spin aria-label="Auto-rotate"><i class="fas fa-sync-alt"></i></button>
        <button type="button" data-reset aria-label="Reset view"><i class="fas fa-expand"></i></button>
      </div>
    </div>
    <div class="x-hint"><i class="fas fa-hand-pointer"></i> <span class="hint-d">Drag to rotate · Right-drag or Shift-drag to move · Click a project for the route</span><span class="hint-t">Drag to rotate · Two fingers to move and zoom · Tap a project</span></div>
    <button type="button" class="x-compass" aria-label="Face north"><span>N</span><i></i></button>
    <div class="x-scale" aria-hidden="true"><b></b><span>100 m</span></div>
    <div class="x-route" hidden></div>
    <div class="x-attrib">Map data © <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors</div>
    <div class="x-card" aria-live="polite"><div class="x-card-img"></div><div class="x-card-body"></div></div>
  </div>"""

THREE = '<script src="assets/vendor/three.min.js"></script>\n'

PAGES = {
  "index":        dict(title="Properties in Ahmedabad – Luxury Flats, Offices & Land | Galaxy Estates Properties", desc="New and luxury properties in Ahmedabad and Gandhinagar: 4 & 5 BHK flats in Adani Shantigram, Bodakdev and S.G. Highway, offices, GIFT City homes and land across Gujarat. Call +91 84880 62309.", page="home"),
  "projects":     dict(title="New Projects in Ahmedabad, GIFT City & Abroad – Prices & RERA | Galaxy Estates Properties", desc=f"{len(ALL)} new and luxury projects with prices, sizes, RERA numbers and availability: flats in Ahmedabad, offices on S.G. Highway, weekend villas and plots, Adani Shantigram, GIFT City and homes abroad.", page="projects"),
  "shantigram":   dict(title="Luxury Properties in Adani Shantigram, Ahmedabad – 3D Map & Prices | Galaxy Estates", desc="Luxury 2, 3, 4 BHK flats and villas in Adani Shantigram, Ahmedabad: Belrosa, Skyline, Embrace, The North Park and more, with prices, RERA and an interactive 3D township map.", page="shantigram", scripts=THREE + '<script src="assets/geo-shantigram.js"></script>\n<script src="assets/navmap.js"></script>\n<script src="assets/town-sites.js"></script>\n<script src="assets/shantigram.js"></script>\n'),
  "gift-city":    dict(title="GIFT City Flats & Offices, Gandhinagar – Prices & 3D Map | Galaxy Estates Properties", desc="Buy flats and offices in GIFT City, Gandhinagar: Sobha Elysia, Vida by Nila Spaces and more, with prices, RERA numbers and an interactive 3D map of India's first IFSC.", page="gift-city", scripts=THREE + '<script src="assets/geo-gift.js"></script>\n<script src="assets/navmap.js"></script>\n<script src="assets/town-sites.js"></script>\n<script src="assets/gift-city.js"></script>\n'),
  "land":         dict(title="Land for Sale in Ahmedabad & Gujarat – Plots, Farm & Industrial Land | Galaxy Estates", desc="Buy or sell land in Ahmedabad and all 34 districts of Gujarat: residential plots, farm land, industrial and commercial land, with title checks, site visits and registration support.", page="land", scripts='<script src="assets/land.js"></script>\n<script src="assets/vendor/leaflet/leaflet.js"></script>\n' + THREE + '<script src="assets/land-market.js"></script>\n', extra_head='<link rel="stylesheet" href="assets/vendor/leaflet/leaflet.css"/>\n'),
  "global":       dict(title="Global Property for Indian Investors — Dubai, London, Singapore & More | Galaxy Estates Properties", desc="Buy homes and investment property in Dubai, London, Paris, Monaco, Singapore, Phuket, Bali, Kuala Lumpur and more. Market guides, developers, LRS guidance and shortlists from Galaxy Estates Properties.", page="global", scripts='<script src="assets/land.js"></script>\n<script src="assets/global.js"></script>\n'),
  "404":          dict(title="Page not found | Galaxy Estates Properties", desc="The page you were looking for could not be found.", page="404"),
  "virtual-tours":dict(title="Virtual Tours & 3D Renderings | Galaxy Estates Properties", desc="Sample flat walkthroughs, drone tours and 3D renderings of Adani Shantigram projects, plus interactive 3D models of Shantigram and GIFT City.", page="virtual-tours"),
  "about":        dict(title="Real Estate Agent in Kalol & Ahmedabad – Er. Samir Dabhi | Galaxy Estates Properties", desc="Galaxy Estates Properties, Kalol: property advisor Er. Samir Dabhi for luxury homes, offices, land and industrial plots in Ahmedabad and Gandhinagar, and property abroad.", page="about"),
  "contact":      dict(title="Contact a Property Advisor in Kalol & Ahmedabad | Galaxy Estates Properties", desc="Call or WhatsApp +91 84880 62309 to book a site visit for flats, offices or land in Ahmedabad, Gandhinagar and GIFT City. Office in Kalol, Gujarat.", page="contact"),
}

# ---------------------------------------------------------------- one page per project (for Google: each project name can rank)
AREA_SLUG = {"shantigram": "adani-shantigram-ahmedabad", "gift": "gift-city-gandhinagar"}
AREA_NAME = {"shantigram": "Adani Shantigram, Ahmedabad", "gift": "GIFT City, Gandhinagar"}
AHD_AREA = {"maruti-360": ("bodakdev-ahmedabad", "Bodakdev, Ahmedabad"), "gala-ikebana": ("sindhu-bhavan-road-ahmedabad", "Sindhu Bhavan Road, Ahmedabad"),
            "navratna-gulmohar": ("iscon-satellite-ahmedabad", "Iscon Cross Road, Ahmedabad"), "trogon-centre-court": ("sp-ring-road-ahmedabad", "S.P. Ring Road, Ahmedabad"),
            "trogon-twin-towers": ("sg-highway-ahmedabad", "S.G. Highway, Ahmedabad"), "shivalik-wave": ("sg-highway-ahmedabad", "S.G. Highway, Ahmedabad"),
            "antonia": ("sg-highway-ahmedabad", "S.G. Highway, Ahmedabad"),
            "anamika-high-point": ("sg-highway-bodakdev-ahmedabad", "S.G. Highway, Bodakdev, Ahmedabad"), "ashridhar-wynn": ("sindhu-bhavan-road-ahmedabad", "Sindhu Bhavan Road, Ahmedabad"),
            "suryam-the-banyan": ("bodakdev-ahmedabad", "Bodakdev, Ahmedabad"),
            "ashridhar-kalrav-seasons": ("thol-ahmedabad", "Thol, Ahmedabad"), "ashridhar-kalrav-nest": ("north-ahmedabad", "Govindpura, North Ahmedabad"),
            "arvind-forreste": ("nasmed-gandhinagar", "Nasmed, Gandhinagar"), "arvind-uplands-3": ("nal-sarovar-ahmedabad", "Nal Sarovar Road, Ahmedabad"),
            "arvind-aqua-city": ("kadi-thol-road-ahmedabad", "Kadi–Thol Road, Ahmedabad"), "bsafal-rethal-greens": ("sanand-ahmedabad", "Sanand, Ahmedabad"),
            "suryam-repose": ("thol-ahmedabad", "Greater Thol, Ahmedabad"), "suryam-the-sage": ("thol-ahmedabad", "Greater Thol, Ahmedabad"),
            "shivalik-farmland": ("sanand-viramgam-ahmedabad", "Sanand–Viramgam, Ahmedabad"),
            "godrej-altus": ("vastrapur-ahmedabad", "Vastrapur, Ahmedabad"), "venus-the-universe": ("nehru-nagar-ahmedabad", "Nehru Nagar, Ahmedabad"),
            "venus-pashmina": ("bodakdev-ahmedabad", "Bodakdev, Ahmedabad"), "venus-stratum": ("nehru-nagar-ahmedabad", "Nehru Nagar, Ahmedabad"),
            "shilp-business-gateway": ("sg-highway-ahmedabad", "S.G. Highway, Ahmedabad")}
def slugify(t): return re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')
def area_of(p):
    if p["market"] in AREA_SLUG: return AREA_SLUG[p["market"]], AREA_NAME[p["market"]]
    if p["market"] == "ahmedabad": return AHD_AREA[p["id"]]
    return slugify(p["city"]), (p["city"] + ", " + p["country"] if p["city"] != p["country"] else p["country"])
def page_url(p):
    a, _ = area_of(p)
    return f"{p['id']}-{a}.html"
for p in ALL: p["page"] = page_url(p)

def kind_words(p):
    if "Commercial" in p["cats"] and p["id"] != "navratna-gulmohar": return "offices and showrooms" if p["market"] != "abroad" else "offices"
    if p["id"] == "navratna-gulmohar": return "homes, offices and shops"
    if "Weekend villas & plots" in p["cats"]: return "weekend villas and plots" if "Villas & townhouses" in p["cats"] else "weekend and farm plots"
    if "Villas & townhouses" in p["cats"] and p["market"] != "abroad": return "villas"
    return p["label"].lower().replace("bhk", "BHK") + (" flats" if p["market"] != "abroad" and "BHK" in p["label"] else "")

# floor-by-floor 3D explorers (towers laid out from the published site plan; metres east / north of the plot centre)
def _sh_stack():
    st = [dict(label="Ground floor", kind="M", use="Double-height entrance lobbies with reception, plus the ground-floor amenities: club, swimming pool, café, banquet and business lounge"),
          dict(label="Floor 1", kind="M", use="Amenity deck: gym, yoga room, spa and saunas, bowling alley, golf simulator, sports bar, lounge and two guest suites")]
    for f in range(2, 28):
        if f == 16:
            st.append(dict(label="Floor 16 (skip floor)", kind="S", use="Skip floor: no home on this level, as per the developer’s sheet"))
        else:
            st.append(dict(label=f"Floor {f}", kind="A", **({"terrace": True} if f == 2 else {})))
    st.append(dict(label="Floors 28–31 (penthouse)", kind="P", levels=4))
    return st

T3D = {
  "shivalik-shantigram": dict(project="Shivalik Shantigram", interest="4 & 5 BHK simplex and 6 BHK penthouses", floorH=4.3, height=138.5, stack=_sh_stack(), style="bronze", camR=300, camY=70,
      areaLabel="RERA area", plot=dict(w=112, d=95), faces="North-east, over the golf course to the Narmada canal (living room and deck)",
      geo=dict(name="GEO_SHANTIGRAM", file="assets/geo-shantigram.js", x=-1293, y=1089, rot=-52, radius=950),
      towers=[dict(id="T1", x=-32.9, y=7.4, w=23, d=37, type="5", terrace="574 sq.ft. carpet (this floor only)"), dict(id="T2", x=-11.2, y=-0.9, w=20.5, d=37, type="4", terrace="1,377 sq.ft. carpet (this floor only)"),
              dict(id="T3", x=11.5, y=-10.5, w=23.5, d=37.5, type="5", terrace="1,582 sq.ft. carpet (this floor only)"), dict(id="T4", x=34.0, y=-19.0, w=19.5, d=37, type="4", terrace="1,377 sq.ft. carpet (this floor only)")],
      units={"4": dict(name="4 BHK simplex", short="4 BHK", area="4,147.57 sq.ft.", extra="3,637.73 sq.ft. RERA carpet + 413.22 sq.ft. deck + 96.92 sq.ft. utility",
                       sba="8,294 sq.ft.", parking=4, price="Price on call", avail="Ask for live availability"),
             "5": dict(name="5 BHK simplex", short="5 BHK", area="5,174.65 sq.ft.", extra="4,620.13 sq.ft. RERA carpet + 457.90 sq.ft. deck + 96.92 sq.ft. utility",
                       sba="10,348 sq.ft.", parking=5, price="Price on call", avail="Ask for live availability"),
             "P4": dict(name="6 BHK Penthouse I, four levels", short="6 BHK PH I", area="9,627.43 sq.ft. (four levels combined)", extra="Terraces: 888 sq.ft. on level 3 and 1,988 sq.ft. on level 4",
                        sba="19,255 sq.ft.", parking=7, price="Price on call", avail="Ask for live availability"),
             "P5": dict(name="6 BHK Penthouse II, four levels", short="6 BHK PH II", area="11,953.54 sq.ft. (four levels combined)", extra="Terraces: 981 sq.ft. on level 3 and 1,785 sq.ft. on level 4",
                        sba="23,867 sq.ft.", parking=7, price="Price on call", avail="Ask for live availability")}),
}
import t3d_auto as _TA
_TA.load_gift(os.path.join(OUT, "assets", "geo-gift.js"))
_TA.write_geo(os.path.join(OUT, "assets"))
for _k, _v in _TA.make(ALL).items():
    T3D.setdefault(_k, _v)
# Shivalik Wave: model built from the developer's brochure floor plans (tools/shivalik_wave/README.md); replaces the generic form
_SW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shivalik_wave", "t3d.json")
if os.path.exists(_SW):
    T3D["shivalik-wave"] = json.load(open(_SW, encoding="utf-8"))
T3D["shivalik-shantigram"]["note"] = ("Model drawn from the developer’s brochure (V4.0, Oct 2026): tower positions from the typical-floor site plan, 4.3 m floor to floor, 138.5 m tall, two amenity floors, "
    "skip floor 16 and the four-level penthouse on top. Sizes are to scale; facade finishes are simplified. Surroundings (golf course, township roads, Narmada canal, nearby buildings) are from OpenStreetMap; "
    "the site position follows the brochure’s aerial plan and is approximate. Prices are shared on call. RERA registration is not yet received.")

def write_town_sites():
    """assets/town-sites.js: every Shantigram and GIFT City project's registered plot and buildings, from the same data as its 3D explorer, for the township maps."""
    import math as _m
    E_, D_ = 6378137.0, _m.pi / 180
    out = {"GEO_SHANTIGRAM": {}, "GEO_GIFT": {}}
    for pid, c in T3D.items():
        g = c.get("geo") or {}
        if g.get("name") not in out or pid == "shivalik-shantigram": continue
        la0, lo0 = _TA.ORIGIN[g["name"]]
        lat = la0 + g["y"] / (D_ * E_); lon = lo0 + g["x"] / (D_ * E_ * _m.cos(la0 * D_))
        r = _m.radians(g.get("rot") or 0); cs, sn = _m.cos(r), _m.sin(r)
        rotp = lambda x, y: [round(x * cs - y * sn, 1), round(x * sn + y * cs, 1)]
        towers = []
        for t in c["towers"]:
            st = t.get("stack") or c["stack"]
            h = sum(L.get("h") or L.get("levels", 1) * c["floorH"] for L in st)
            if len(c["towers"]) == 1 and c.get("height"): h = max(h, c["height"])
            x, y = rotp(t["x"], t["y"])
            towers.append([x, y, t["w"], t["d"], round((g.get("rot") or 0) + (t.get("ang") or 0), 1), round(h, 1), len(st) - 1])
        poly = [rotp(*q) for q in c["plotPoly"]] if c.get("plotPoly") else None
        n = len(towers); top = max(t[6] for t in towers)
        word = "building" if n == 1 else "buildings"
        info = f"{n} {word} · up to ground + {top} floors"
        out[g["name"]][pid] = dict(lat=round(lat, 7), lon=round(lon, 7), towers=towers, poly=poly, info=info, floors=top, commercial=c.get("kind") == "commercial")
    js = ("/* Registered plots (Gujarat RERA map service) and buildings for the township maps, from the same data as each project's 3D floor explorer. Built " + "18 Oct 2026. */\n"
          "window.TOWN_SITES=" + json.dumps(out, separators=(",", ":"), ensure_ascii=False) + ";\n")
    open(os.path.join(OUT, "assets", "town-sites.js"), "w").write(js)
write_town_sites()

def t3d_section(p):
    c = T3D.get(p["id"])
    if not c: return ""
    return f"""<section class="section bg-alt" id="floors">
  <div class="container">
    <div class="section-header seq"><span class="section-tag">3D floor explorer</span><h2>{"Pick any floor" if len(c["towers"]) == 1 else "Pick any tower and floor"}</h2>
      <p>Tap or click a floor in the model, or choose it from the lists, to see {'that floor’s offices and shops' if c.get('kind') == 'commercial' else 'the homes on that floor'}, with sizes, prices and height. Drag to turn the model, pinch or scroll to zoom.</p></div>
    <div class="t3d reveal" data-t3d="t3d-{p['id']}">
      <div class="t3d-stage" aria-label="3D model of {E(p['name'])}"></div>
      <div class="t3d-side">
        <div class="t3d-pick">
          <label>Tower<select name="t3d-tower"></select></label>
          <label>Floor<select name="t3d-floor"></select></label>
          <div class="t3d-steps"><button type="button" class="cta-btn ghost small" data-t3d-step="1" aria-label="One floor up"><i class="fas fa-arrow-up"></i></button><button type="button" class="cta-btn ghost small" data-t3d-step="-1" aria-label="One floor down"><i class="fas fa-arrow-down"></i></button></div>
        </div>
        <div class="t3d-panel" aria-live="polite"></div>
      </div>
    </div>
    <p class="detail-source">{E(c["note"])}</p>
  </div>
</section>
<script type="application/json" id="t3d-{p['id']}">{json.dumps(c, ensure_ascii=False)}</script>"""

def property_page(p):
    _, area = area_of(p)
    words = kind_words(p)
    title = f"{p['name']}, {area} – {p['label']}, Price & RERA | Galaxy Estates Properties"
    desc = (f"{p['name']} by {p['developer']}: {words} in {area}. {p['price']} {p['priceLabel']}. Sizes {p['size']}. "
            f"Possession {p['possession']}. Call +91 84880 62309.")[:300]
    rows = "".join(f"<tr><th scope=\"row\">{E(r[0])}</th><td>{E(r[1])}</td><td>{E(r[2])}</td><td>{E(r[3] or 'Ask us')}</td></tr>" for r in p["mix"])
    near = [q for q in ALL if q["market"] == p["market"] and q["id"] != p["id"]][:3]
    if len(near) < 3: near += [q for q in ALL if q["id"] != p["id"] and q not in near][:3 - len(near)]
    import urllib.parse as _u
    gopen = "https://www.google.com/maps/search/?api=1&query=" + _u.quote_plus(p["mapq"])
    loc = p["location"] + ("" if p["country"] == "India" or p["country"] in p["location"] else ", " + p["country"])
    mapsec = ""
    if p["country"] == "India":
        mapsec = '<section class="section bg-alt" id="location"><div class="container">' + map_block(
            f"Where {E(p['name'])} is", f"{E(loc)}. Pick a view to see it on the live Google map, or the route from our office in Kalol.",
            [("fa-map-marker-alt", p["name"], area, "q", p["mapq"], None, 15), ("fa-route", "Route from our office", "Drive from Kalol", "d", "Kalol, Gujarat", p["mapq"])],
            "Location from Google Maps. Ask us to arrange a site visit.") + '</div></section>'
    ld = {"@context": "https://schema.org", "@type": "RealEstateListing", "name": p["name"], "url": SITE_URL + p["page"],
          "image": SITE_URL + p["img"], "description": desc,
          "about": {"@type": "Place", "name": p["name"], "address": {"@type": "PostalAddress", "streetAddress": p["location"], "addressLocality": p["city"], "addressCountry": "IN" if p["country"] == "India" else p["country"]}},
          "provider": {"@type": "RealEstateAgent", "name": "Galaxy Estates Properties", "telephone": "+91-84880-62309", "url": SITE_URL}}
    cpage = CB.page_for(p["country"]) if p["market"] == "abroad" else None
    cname = next((c["title"] for c in CB.COUNTRIES if c["slug"] + ".html" == cpage), "")
    sep = '<i class="fas fa-chevron-right"></i>'
    crumbs = (f'<a href="index.html">Home</a>{sep}<a href="global.html">Global</a>{sep}<a href="{cpage}">{E(cname)}</a>{sep}' if cpage
              else f'<a href="index.html">Home</a>{sep}<a href="projects.html">Properties</a>{sep}')
    guide = (f'<p class="detail-source reveal"><a href="{cpage}"><i class="fas fa-book-open" aria-hidden="true"></i> Buying in {E(cname)} from India: rules, costs, developers and ongoing projects</a></p>' if cpage else '')
    body = f"""<section class="page-hero prop-hero">
  <div class="page-hero-bg" style="background-image:url('{p['img']}')"></div>
  <div class="page-hero-overlay"></div>
  <div class="container page-hero-content">
    <div class="breadcrumb hs">{crumbs}<span>{E(p['name'])}</span></div>
    <span class="section-tag hs">{E(p['label'])} · {E(area)}</span>
    <h1>{E(p['name'])}</h1>
    <p class="hs">{E(words[0].upper() + words[1:])} in {E(area)} by {E(p['developer'])}. {E(p['build'])}.</p>
  </div>
</section>

<section class="section">
  <div class="container prop-layout">
    <figure class="prop-photo reveal"><img src="{p['img']}" alt="{E(p['name'])} exterior, {E(area)}" width="1000" height="600" loading="eager"/><figcaption>{E(p.get("imgnote", "Official exterior render from the developer."))}</figcaption></figure>
    <div class="prop-facts reveal" style="--d:.08s">
      <p class="project-location"><i class="fas fa-map-marker-alt"></i> <span>{E(loc)}</span> <a class="project-map" href="{E(gopen)}" target="_blank" rel="noopener noreferrer">View on Google Maps</a></p>
      <p class="project-dev">by <span>{E(p['developer'])}</span></p>
      <div class="price">{E(p['price'])}</div><span class="price-label">{E(p['priceLabel'])}</span>
      <dl class="unit-strip big">
        <div><dt>Total units</dt><dd>{E(p['total'])}</dd></div>
        <div><dt>Available</dt><dd>{E(p['available'])}</dd></div>
        <div><dt>Possession</dt><dd>{E(p['possession'])}</dd></div>
      </dl>
      <div class="detail-specs">
        <div class="wide"><small>Sizes</small><strong>{E(p['size'])}</strong></div>
        <div class="wide"><small>{E(p['regLabel'])}</small><strong style="font-size:.8rem;word-break:break-word">{E(p['rera'])}</strong></div>
      </div>
      {('<p class="travel-refund"><i class="fas fa-plane"></i> <span><strong>Travel cost refunded.</strong> Fly out to see it before you buy: when your purchase completes through us, we refund your travel cost for the visit.</span></p>') if p['market'] == 'abroad' else ''}
      <div class="btn-row">
        <button type="button" class="cta-btn primary" data-enquire="{p['id']}"><i class="fas fa-calendar-alt"></i> Book a site visit</button>{('<a class="cta-btn ghost" href="#floors"><i class="fas fa-cube"></i> 3D floor explorer</a>' if p['id'] in T3D else '')}
        <a class="cta-btn wa" data-whatsapp="Hello, I'd like the price sheet and availability for {E(p['name'])} ({E(area)})." href="#" target="_blank" rel="noopener noreferrer"><i class="fab fa-whatsapp"></i> WhatsApp</a>
      </div>
    </div>
  </div>
  <div class="container">
    <h2 class="detail-h reveal">{E(p['name'])} unit types, sizes and prices</h2>
    <div class="mix-wrap reveal"><table class="mix-table"><thead><tr><th scope="col">Unit type</th><th scope="col">Size</th><th scope="col">Price</th><th scope="col">Available</th></tr></thead><tbody>{rows}</tbody></table></div>
    <p class="detail-source reveal">{E(p['blurb'])}</p>
    {OFF.block(p, E)}
    {guide}
  </div>
</section>
{t3d_section(p)}
{mapsec}
<section class="section">
  <div class="container">
    <div class="contact-grid">
      <div class="panel reveal"><h2 class="detail-h" style="margin-top:0">Ask about {E(p['name'])}</h2><p class="lead">Get the current price sheet, floor plans and a private site visit. Your enquiry goes straight to our team.</p>{form('pp', p['name'])}</div>
      <div class="panel reveal" style="--d:.1s"><h2 class="detail-h" style="margin-top:0">More properties like this</h2><div class="prop-more">{''.join(f'<a href="{q["page"]}" class="prop-more-item"><img src="{q["img"]}" alt="{E(q["name"])}" loading="lazy" width="160" height="110"/><span><strong>{E(q["name"])}</strong><small>{E(q["label"])} · {E(area_of(q)[1])}</small></span></a>' for q in near)}</div>
      <p style="margin-top:18px"><a class="cta-btn ghost small" href="projects.html">See all properties</a></p></div>
    </div>
  </div>
</section>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>"""
    interest = ("Global property" if p["market"] == "abroad" else ("GIFT City — Commercial" if "Commercial" in p["cats"] else "GIFT City — Residential") if p["market"] == "gift"
                else "Offices &amp; showrooms — Ahmedabad" if "Commercial" in p["cats"] else "5 BHK &amp; penthouses" if "5 BHK" in p["cats"]
                else "Land in Gujarat — Buy" if "Weekend villas & plots" in p["cats"] and "Villas & townhouses" not in p["cats"] else "Villas" if "Villas & townhouses" in p["cats"] else "4 BHK Apartments" if "4 BHK" in p["cats"]
                else "3 BHK Apartments" if "3 BHK" in p["cats"] else "2 BHK Apartments")
    body = body.replace("<option selected>3 BHK Apartments</option>", "<option>3 BHK Apartments</option>").replace(f"<option>{interest}</option>", f"<option selected>{interest}</option>", 1)
    return head(title, desc, "projects", fname=p["page"][:-5]) + nav() + '<main id="main">\n' + enhance(body) + '\n</main>\n' + footer() + overlays() + scripts((THREE + f'<script src="{T3D[p["id"]]["geo"]["file"]}"></script>\n<script src="assets/tower3d.js"></script>\n') if p['id'] in T3D else '')

# ---------------------------------------------------------------- search-friendly content (home page)
def plink(pid, text=None):
    q = next(x for x in ALL if x["id"] == pid)
    return f'<a href="{q["page"]}">{E(text or q["name"])}</a>'
HOME_FAQ = [
  ("Which are the best areas to buy property in Ahmedabad?",
   "For luxury flats, buyers look most at S.G. Highway, Bodakdev, Sindhu Bhavan Road and Adani Shantigram. For offices and showrooms, Vaishnodevi Circle on S.G. Highway and Iscon Cross Road. GIFT City in Gandhinagar suits buyers who want to be close to the financial centre."),
  ("Are these projects RERA registered?",
   "Every listing shows its Gujarat RERA number, and we check it on the GujRERA portal before you book. Where a developer has not published the number (Antonia, some weekend-plot projects and pre-launches), the listing says so and we confirm the registration with you before any booking."),
  ("Where can I buy a weekend home or plot near Ahmedabad?",
   "Most weekend villas and plots are around Thol, Kadi Road and Sanand, 30 to 60 minutes from S.G. Highway: Kalrav Seasons and Kalrav Nest by A. Shridhar, Arvind Aqua City and Arvind Uplands 3.0, Suryam Repose and The Sage, Safal Rethal Greens and Shivalik Farmland. Arvind Forreste in Nasmed is close to Gandhinagar and Kalol. Plots start at about ₹50 Lakh."),
  ("What does a 4 BHK flat in Ahmedabad cost?",
   "On our current list, 4 BHK homes start at about ₹2.23 Cr* at Skyline in Adani Shantigram and ₹2.77 Cr* at Trogon Centre Court. Prices marked * are as published by the developer and change often, so ask us for the latest price sheet."),
  ("Can NRIs buy property in Ahmedabad?",
   "Yes. NRIs can buy flats, villas, offices and shops in India. Agricultural land, plantations and farmhouses are the exception under FEMA rules. We help with site videos, documents and registration while you are abroad."),
  ("How do I book a site visit?",
   "Call or WhatsApp +91 84880 62309, or send the enquiry form on any page. We arrange private visits on weekdays and weekends, and video walkthroughs if you cannot visit in person."),
]
# PIN codes checked against India Post listings (Oct 2026)
AHD_AREAS = [("Bodakdev", "380054"), ("Thaltej", "380059"), ("Bopal, Ambli & Shela", "380058"), ("Satellite & Jodhpur", "380015"),
             ("Navrangpura", "380009"), ("Ellisbridge", "380006"), ("Paldi", "380007"), ("Memnagar", "380052"), ("Naranpura", "380013"),
             ("Ghatlodia", "380061"), ("Sola", "380060"), ("Gota", "382481"), ("Chandkheda", "382424"), ("Motera & Sabarmati", "380005"),
             ("Maninagar", "380008"), ("Shahibag", "380004"), ("Vaishnodevi & Shantigram", "382421"), ("Kalol", "382721")]
GUJ_CITIES = ["Gandhinagar", "Surat", "Vadodara", "Rajkot", "Bhavnagar", "Jamnagar", "Mehsana", "Anand", "Nadiad", "Bharuch", "Vapi", "Kutch"]
IND_CITIES = ["Mumbai", "Pune", "Delhi NCR", "Bengaluru", "Hyderabad", "Chennai", "Kolkata", "Indore", "Jaipur", "Udaipur"]
NRI_PLACES = ["USA (New Jersey, New York, California, Texas)", "UK (London, Leicester)", "Canada (Toronto, Brampton)", "Australia (Sydney, Melbourne)",
              "New Zealand (Auckland)", "UAE (Dubai, Abu Dhabi)", "Singapore", "Kenya", "Tanzania", "Uganda"]
NRI_COUNTRIES = ["United States", "United Kingdom", "Canada", "Australia", "New Zealand", "United Arab Emirates", "Singapore", "Kenya", "Tanzania", "Uganda"]
def area_served_ld():
    """Areas and PIN codes for search engines only (schema.org areaServed); not shown on the page."""
    out = ["Ahmedabad", "GIFT City", "Gujarat", "India"]
    for name, pin in AHD_AREAS:
        city = "Kalol" if name == "Kalol" else "Ahmedabad"
        out.append({"@type": "Place", "name": f"{name}, {city}",
                    "address": {"@type": "PostalAddress", "addressLocality": city, "postalCode": pin, "addressRegion": "Gujarat", "addressCountry": "IN"}})
    out += [{"@type": "City", "name": c} for c in GUJ_CITIES + IND_CITIES]
    out += [{"@type": "Country", "name": c} for c in NRI_COUNTRIES]
    return out

SHOW_AREAS_ON_PAGE = False   # owner asked (Oct 2026) not to show the areas / PIN codes to visitors

def areas_block():
    if not SHOW_AREAS_ON_PAGE:
        return ""
    chips ="".join(f'<li><span>{E(a)}</span><small>{p}</small></li>' for a, p in AHD_AREAS)
    return f"""<div class="areas reveal">
  <h3 class="seo-faq-h" style="margin-top:56px">Buyers we work with</h3>
  <p class="areas-lead">Most of our buyers already live in Ahmedabad and are moving up to a bigger home, or are investing near S.G. Highway, Shantigram and GIFT City. We meet them in their own area for the first conversation.</p>
  <ul class="area-chips" aria-label="Ahmedabad areas and PIN codes">{chips}</ul>
  <p class="areas-lead"><strong>Across Gujarat:</strong> {E(", ".join(GUJ_CITIES))}. <strong>Elsewhere in India:</strong> {E(", ".join(IND_CITIES))}, for buyers relocating to Ahmedabad or GIFT City.</p>
  <p class="areas-lead"><strong>NRI buyers:</strong> {E("; ".join(NRI_PLACES))}. We handle video site visits, documents and registration while you are abroad.</p>
</div>"""

def seo_home():
    cols = [
      ("Luxury flats in Ahmedabad", f"Large 4 and 5 BHK homes are concentrated along S.G. Highway: {plink('maruti-360')}, {plink('anamika-high-point')}, {plink('gala-ikebana')}, {plink('venus-pashmina')} and {plink('suryam-the-banyan')} in Bodakdev, {plink('godrej-altus')} in Vastrapur, {plink('venus-the-universe')} at Nehru Nagar, and {plink('trogon-centre-court')} on S.P. Ring Road near Vaishnodevi Circle."),
      ("Luxury properties in Shantigram", f"Adani Shantigram is a gated township between Ahmedabad and Gandhinagar with a golf course and a lake. Compare {plink('belrosa')}, {plink('shilp-skyline')} and {plink('ambrosia')}, or villas at {plink('north-park')}, in the <a href=\"shantigram.html\">3D township map</a>."),
      ("Offices and showrooms on S.G. Highway", f"Vaishnodevi Circle is the city's newest business address, with {plink('shivalik-wave')}, {plink('trogon-twin-towers')} and the upcoming {plink('antonia')}; {plink('shilp-business-gateway')} near Nirma University; on Sindhu Bhavan Road, {plink('ashridhar-wynn')}; at Nehru Nagar, {plink('venus-stratum')}. At Iscon Cross Road, {plink('navratna-gulmohar')} combines offices, shops and homes."),
      ("New projects in GIFT City", f"Homes near India's first international financial centre: {plink('sobha-elysia')}, {plink('shivalik-presente')}, {plink('savvy-marina')}, {plink('bakeri-stella')}, {plink('shivalik-skyview')}, {plink('shilp-north-sky')} and {plink('nila-vida')}, with prices and RERA numbers. See the <a href=\"gift-city.html\">GIFT City 3D map</a>."),
      ("Weekend homes, plots and land", f"Weekend villas and plots near Thol, Kadi and Sanand: {plink('ashridhar-kalrav-seasons')}, {plink('arvind-aqua-city')}, {plink('suryam-repose')} and {plink('shivalik-farmland')} (<a href=\"projects.html#weekend-villas-plots\">all weekend homes</a>). We also handle residential plots, farm land, industrial and commercial land in all 34 districts, with title and document checks before you pay. See <a href=\"land.html\">land for sale in Gujarat</a>."),
      ("Property abroad for Indian buyers", f"Dubai, Singapore, Monaco, Phuket, Pattaya and Kuala Lumpur, from developers such as Emaar, Binghatti, Danube and CDL. Start with {plink('binghatti-burj-jacob')}, {plink('danube-bayz-101')} and {plink('emaar-valo')}, or browse <a href=\"global.html\">all markets</a>."),
    ]
    grid = "".join(f'<article class="seo-col reveal" style="--d:{(i % 3) * .06:.2f}s"><h3>{E(t)}</h3><p>{b}</p></article>' for i, (t, b) in enumerate(cols))
    faq = "".join(f'<details class="seo-faq reveal"><summary>{E(q)}</summary><p>{E(a)}</p></details>' for q, a in HOME_FAQ)
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in HOME_FAQ]}
    return f"""<section class="section seo-section">
  <div class="container">
    <div class="section-header seq">
      <span class="section-tag">Property in Ahmedabad</span>
      <h2>Finding the right property in Ahmedabad and Gandhinagar</h2>
      <p>From our office in Kalol we cover new projects, resale and land across the twin cities. Here is where each kind of property is, and the projects we can show you now.</p>
    </div>
    <div class="seo-grid">{grid}</div>
    <h3 class="seo-faq-h reveal">Questions buyers ask us</h3>
    <div class="seo-faqs">{faq}</div>
    {areas_block()}
  </div>
</section>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>"""

BUSINESS_LD = {"@context": "https://schema.org", "@type": "RealEstateAgent", "name": "Galaxy Estates Properties",
  "url": "https://galaxyestatesproperties.co.in/", "logo": "https://galaxyestatesproperties.co.in/assets/logo.svg",
  "image": "https://galaxyestatesproperties.co.in/assets/img/p/belrosa.webp", "telephone": "+91-84880-62309", "email": "director@galaxyestatesproperties.co.in",
  "address": {"@type": "PostalAddress", "addressLocality": "Kalol", "addressRegion": "Gujarat", "addressCountry": "IN"},
  "areaServed": area_served_ld(),
  "founder": {"@type": "Person", "name": "Er. Samir Dabhi"},
  "description": "Property advisors for luxury flats, offices and land in Ahmedabad, Gandhinagar and GIFT City, and property abroad."}

def split_words(inner):
    """Wrap each word of a headline in a mask-reveal span. A <span class="highlight|shimmer"> keeps its own gradient per word."""
    out, i = [], 0
    for t in re.findall(r'<span class="(?:highlight|shimmer)">.*?</span>|[^<]+', inner, flags=re.S):
        m = re.match(r'<span class="(highlight|shimmer)">(.*?)</span>$', t, flags=re.S)
        words = m.group(2).split() if m else t.split()
        for w in words:
            core = f'<span class="{m.group(1)}">{w}</span>' if m else w
            out.append(f'<span class="w"><span class="wi" style="--i:{i}">{core}</span></span>')
            i += 1
    return ' '.join(out)

def enhance(body):
    """Build-time animation hooks: split every <h1> into words and give each .hs element its own start delay."""
    body = re.sub(r'<h1>(.*?)</h1>', lambda m: '<h1 class="hs-split">' + split_words(m.group(1)) + '</h1>', body, flags=re.S)
    n = [0]
    def tag(m):
        name, attrs = m.group(1), m.group(2)
        cm = re.search(r'\sclass="([^"]*)"', attrs)
        if not cm or not ({'hs', 'hs-split'} & set(cm.group(1).split())):
            return m.group(0)
        d = round(0.1 + 0.09 * n[0], 2)
        n[0] += 1
        if 'style="' in attrs:
            attrs = attrs.replace('style="', f'style="--hd:{d};', 1)
        else:
            attrs += f' style="--hd:{d}"'
        return f'<{name}{attrs}>'
    return re.sub(r'<(\w+)((?:\s[^<>]*)?)>', tag, body)

def build():
    os.makedirs(os.path.join(OUT, 'assets'), exist_ok=True)
    keys = ("id", "name", "developer", "market", "city", "country", "location", "cats", "label", "price", "priceLabel", "size", "possession",
            "rera", "regLabel", "total", "available", "build", "mix", "source", "img", "color", "hue", "blurb", "mapq", "page")
    data = [{k: p[k] for k in keys} for p in ALL]
    with open(os.path.join(OUT, 'assets', 'data.js'), 'w', encoding='utf-8') as f:
        f.write("/* Property data for every listing (India and abroad). The cards and the detail pop-up read from here.\n   To show live stock, edit \"available\" (and the 4th value in each \"mix\" row) and reload the page. */\nwindow.SITE_PROJECTS = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n")
    ctx = {
        "CARDS_ALL": cards(),
        "SEO_HOME": seo_home(), "CARDS_HOME": cards(["belrosa", "maruti-360", "trogon-centre-court", "sobha-elysia", "shivalik-wave", "emaar-valo"]),
        "FILTERS": filters(), "CARDS_SH": cards([p["id"] for p in PROJECTS]), "CARDS_GIFT": cards([p["id"] for p in PB.GIFT]),
        "FILTERS_SH": '<div class="project-filters reveal" role="group" aria-label="Filter residences">' + "".join(
            f'<button type="button" class="filter-btn{" active" if v == "All" else ""}" data-filter="{E(v)}" aria-pressed="{"true" if v == "All" else "false"}">{t}</button>'
            for v, t in [("All", "All"), ("1-2 BHK / studio", "1–2 BHK"), ("3 BHK", "3 BHK"), ("4 BHK", "4 BHK"), ("Villas & townhouses", "Villas"), ("Commercial", "Commercial")]) + '</div>', "MORE_MARKETS": more_markets(),
        "DEV_NAMES": "\n".join(f'      <div class="developer-logo"><span>{E(d)}</span></div>' for d in ["Sobha", "Nila Spaces", "Emaar", "Frasers Property", "CDL", "Banyan Group", "Sansiri", "Lendlease", "Alliance Group"]), "N_ALL": str(len(ALL)), "N_ABROAD": str(len(PB.INTL)),
        "RENDERS": renders(),
        "CTA": cta(),
        "CTA_LAND": cta("Ready to talk about your land?", "Call or message us with the district and the kind of land. We reply during working hours.",
                        label="Buy or sell land", icon="fa-signs-post", enquire="Land in Gujarat", interest="Land in Gujarat — Buy",
                        wa="Hello, I would like to buy or sell land in Gujarat.", tag="Land desk"),
        "LAND_MAP": L.hero_map(), "LAND_TICKER": L.ticker(), "LAND_REGIONS": L.region_cards(), "LAND_FAQ": L.faq(),
        "HOME_TICKER": L.ticker(["Adani Shantigram", "GIFT City", "Land across Gujarat", "Dubai", "London", "Singapore", "Phuket", "Monaco", "Documents checked first", "Kalol · Gandhinagar · Ahmedabad"], "What we do"),
        "FORM_LAND": L.land_form('l'), "LAND_MARKET": L.land_market(), "LAND_SELL": L.land_sell(), "LAND_CARD": L.home_land_card(), "LAND_PROMO": L.projects_land_banner(),
        "MAP_LAND": map_block("Land areas across Gujarat",
            "Pick an area to open the live Google map, then use the button to explore it full screen. Ask us for a site visit once you have a shortlist.",
            L.LAND_CHIPS_MAP, "Maps are live from Google Maps. Place names are indicative; ask us to confirm exact locations."),
        "FORM_CONTACT": form('c', 'General enquiry'),
        "G_MAP": G.hero_map(), "G_TICKER": L.ticker(G.TICKER, "Cities we cover abroad"), "G_FILTERS": G.filters(), "G_CARDS": G.market_cards(),
        "G_DEVCOLS": G.developer_columns(), "G_FAQ": G.faq(), "G_FORM": G.global_form('g'),
        "G_MARKETS": str(len(G.MARKETS)), "G_DEVS": str(G.DEV_COUNT),
        "GLOBAL_CARD": G.home_global_card(), "GLOBAL_PROMO": G.projects_global_banner(),
        "CTA_GLOBAL": cta("Ready to look beyond India?", "Tell us the market and budget. We will send a shortlist with prices, ownership rules and the paperwork from India.",
                        label="Get a shortlist", icon="fa-paper-plane", enquire="Global property", interest="Global property",
                        wa="Hello, I would like to explore property abroad.", tag="Global desk"),
        "EXPLORER_SHANTIGRAM": explorer_ui("Adani Shantigram", "Tap any residence or landmark", views=(("aerial", "Aerial"), ("golf", "Golf & lake"), ("villas", "Villas"))),
        "EXPLORER_GIFT": explorer_ui("GIFT City", "Tap a tower or landmark", modes=("night", "dusk", "day"), views=(("skyline", "Skyline"), ("river", "Riverfront"), ("top", "Top-down"))),
        "MAP_SHANTIGRAM": map_block("Location & connectivity",
            "Adani Shantigram sits on S.G. Highway between Ahmedabad and Gandhinagar. Pick a destination to see the live Google route.",
            [("fa-map-marker-alt", "Adani Shantigram", "Township location", "q", "Adani Shantigram, Ahmedabad", None),
             ("fa-plane", "SVPI Airport", "Route from the township", "d", "Adani Shantigram, Ahmedabad", "Sardar Vallabhbhai Patel International Airport, Ahmedabad"),
             ("fa-city", "GIFT City", "Route to the financial district", "d", "Adani Shantigram, Ahmedabad", "GIFT City, Gandhinagar"),
             ("fa-train", "Sabarmati Railway Station", "Route from the township", "d", "Adani Shantigram, Ahmedabad", "Sabarmati Railway Station, Ahmedabad"),
             ("fa-golf-ball", "Belvedere Golf & Country Club", "Inside the township", "q", "The Belvedere Golf and Country Club, Shantigram, Ahmedabad", None)],
            "Routes and travel times come live from Google Maps and change with traffic."),
        "MAP_GIFT": map_block("GIFT City on the map",
            "GIFT City lies on the Sabarmati riverbank in Gandhinagar district. Pick a destination to see the live Google route.",
            [("fa-map-marker-alt", "GIFT City", "Gandhinagar, Gujarat", "q", "GIFT City, Gandhinagar, Gujarat", None),
             ("fa-building", "GIFT One Tower", "The first IFSC tower", "q", "GIFT One Tower, GIFT City, Gandhinagar", None),
             ("fa-subway", "GIFT City metro station", "Ahmedabad Metro link", "q", "GIFT City Metro Station, Gandhinagar", None),
             ("fa-plane", "SVPI Airport", "Route to GIFT City", "d", "Sardar Vallabhbhai Patel International Airport, Ahmedabad", "GIFT City, Gandhinagar"),
             ("fa-tree", "Adani Shantigram", "Route from GIFT City", "d", "GIFT City, Gandhinagar", "Adani Shantigram, Ahmedabad")],
            "Routes and travel times come live from Google Maps and change with traffic."),
        "MAP_CONTACT": map_block("Where we meet you",
            "Our office is in Kalol, Gujarat. Most site visits start at Adani Shantigram. Tell us where you are coming from and we will plan the route.",
            [("fa-building", "Our office", "Kalol, Gujarat", "q", "Kalol, Gujarat", None),
             ("fa-map-marker-alt", "Adani Shantigram", "Site visits", "q", "Adani Shantigram, Ahmedabad", None),
             ("fa-city", "GIFT City", "Gandhinagar", "q", "GIFT City, Gandhinagar, Gujarat", None),
             ("fa-route", "Office to Shantigram", "Drive from Kalol", "d", "Kalol, Gujarat", "Adani Shantigram, Ahmedabad")],
            "Routes and travel times come live from Google Maps."),
    }
    for name, meta in PAGES.items():
        with open(os.path.join(SRC, name + '.html'), encoding='utf-8') as f:
            body = f.read()
        missing = set(re.findall(r'<!--@(\w+)-->', body)) - set(ctx)
        if missing:
            sys.exit(f"{name}: unknown placeholders {missing}")
        body = re.sub(r'<!--@(\w+)-->', lambda m: ctx[m.group(1)], body)
        body = enhance(body)
        doc = head(meta['title'], meta['desc'], meta['page'], extra=meta.get('extra_head', ''), fname=name) + nav() + '<main id="main">\n' + body + '\n</main>\n' + footer() + overlays() + scripts(meta.get('scripts', ''))
        with open(os.path.join(OUT, name + '.html'), 'w', encoding='utf-8') as f:
            f.write(doc)
        print("built", name + ".html", len(doc))
    for p in ALL:
        with open(os.path.join(OUT, p["page"]), 'w', encoding='utf-8') as f:
            f.write(property_page(p))
    for c in CB.COUNTRIES:
        body = enhance(CB.build_body(c, ALL, card))
        doc = (head(c['seo'], c['desc'], c['slug'], extra='<link rel="stylesheet" href="assets/vendor/leaflet/leaflet.css"/>\n', fname=c['slug']) + nav() + '<main id="main">\n' + body + '\n</main>\n'
               + footer() + overlays() + scripts('<script src="assets/land.js"></script>\n<script src="assets/vendor/leaflet/leaflet.js"></script>\n<script src="assets/country.js"></script>\n'))
        with open(os.path.join(OUT, c['slug'] + '.html'), 'w', encoding='utf-8') as f:
            f.write(doc)
    print("built", len(CB.COUNTRIES), "country pages")
    print("built", len(ALL), "project pages")
    # host files: GitHub Pages serves files as-is with .nojekyll; _headers is read by Netlify / Cloudflare Pages
    open(os.path.join(OUT, '.nojekyll'), 'w').close()
    with open(os.path.join(OUT, '_headers'), 'w') as f:
        f.write("/*\n  Content-Security-Policy: " + CSP + "; frame-ancestors 'none'\n"
                "  X-Content-Type-Options: nosniff\n  X-Frame-Options: DENY\n"
                "  Referrer-Policy: strict-origin-when-cross-origin\n"
                "  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=()\n"
                "  Strict-Transport-Security: max-age=31536000; includeSubDomains\n"
                "/assets/*\n  Cache-Control: public, max-age=604800\n")

if __name__ == '__main__':
    build()

with open(OUT + '/assets/overlays.js', 'w', encoding='utf-8') as _f:
    _f.write("/* Shared pop-ups (enquiry form, property details), added to every page. Generated by build.py. */\n"
             "document.body.insertAdjacentHTML('beforeend', " + json.dumps(modals().strip(), ensure_ascii=False) + ");\n")
print('wrote overlays.js')
