"""Landing pages for "commercial office space in <area>" searches, built from the live projects.html (same shell and cards).
Run from the site folder: python3 tools/office_pages.py"""
import re, html

SITE = "https://galaxyestatesproperties.co.in/"
PAGES = [
    ("commercial-office-space-gift-city-gandhinagar.html", "GIFT City, Gandhinagar", "GIFT City",
     "Offices in GIFT City SEZ and the domestic tariff area, from Shilp, Savvy, Shivalik, Nakshatra, Kaavyaratna, The Identity and WTC.",
     ["shilp-twin-towers", "savvy-oryx", "shivalik-curv", "shilp-centrica", "nakshatra-regalia", "nakshatra-regalia-ii",
      "the-identity", "kaavyaratna-narmada", "kaavyaratna-the-ganga", "wtc-gift-city"]),
    ("commercial-office-space-sg-highway-ahmedabad.html", "S.G. Highway, Ahmedabad", "S.G. Highway",
     "Offices and showrooms on S.G. Highway and Sindhu Bhavan Road, from Trogon, Shivalik, Shilp and A. Shridhar.",
     ["trogon-twin-towers", "shivalik-wave", "antonia", "shilp-business-gateway", "ashridhar-wynn"]),
    ("commercial-office-space-adani-shantigram-ahmedabad.html", "Adani Shantigram, Ahmedabad", "Adani Shantigram",
     "Offices, corporate houses and showrooms by Adani Realty inside the Shantigram township on S.G. Highway.",
     ["inspire-business-park", "inspire-corporate-capital", "inspire-edge", "adani-center-point"]),
]

src = open("projects.html", encoding="utf-8").read()
head, rest = src.split('<main id="main">', 1)
tail = rest.split("</main>", 1)[1]
cards = {m.group(1): m.group(0) for m in re.finditer(r'<article class="project-card[^>]*data-pid="([^"]+)".*?</article>', src, re.S)}

def meta(h, old_title, title, desc, url):
    h = h.replace(old_title, title)
    h = re.sub(r'(<meta (?:name="description"|property="og:description") content=")[^"]*', lambda m: m.group(1) + desc, h)
    return re.sub(r'(<meta property="og:url" content="|<link rel="canonical" href=")[^"]*', lambda m: m.group(1) + url, h)

old_title = re.search(r"<title>(.*?)</title>", head).group(1)
for fname, area, short, intro, ids in PAGES:
    title = html.escape(f"Commercial Office Space in {area} – Offices for Sale & Lease | Galaxy Estates Properties", quote=False)
    desc = html.escape(f"Commercial office space in {area}: {len(ids)} projects with sizes, RERA numbers and availability. {intro} Call +91 84880 62309.")
    others = " · ".join(f'<a href="{f}">{s}</a>' for f, _, s, _, _ in PAGES if f != fname)
    body = f"""<main id="main">
<section class="page-hero">
  <div class="page-hero-overlay"></div>
  <div class="container page-hero-content">
    <div class="breadcrumb"><a href="/">Home</a><i class="fas fa-chevron-right"></i><a href="projects.html">All properties</a><i class="fas fa-chevron-right"></i><span>Offices in {short}</span></div>
    <span class="section-tag">Commercial</span>
    <h1>Commercial office space in {area}</h1>
    <p>{intro} Open any card for sizes, units and RERA details, or call us for the current price sheet and a site visit.</p>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="projects-grid">
{chr(10).join(cards[i] for i in ids)}
    </div>
    <p class="reveal" style="margin-top:32px;text-align:center">Offices in other areas: {others}</p>
  </div>
</section>
</main>"""
    open(fname, "w", encoding="utf-8").write(meta(head, old_title, title, desc, SITE + fname) + body + tail)
    print("built", fname, len(ids), "projects")
