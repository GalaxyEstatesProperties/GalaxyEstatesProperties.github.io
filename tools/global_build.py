"""Global property page: world route map, market cards, developers, investor notes.
Copy is general information. Ownership rules and visa thresholds change; every card says to confirm before buying."""
import html, json, math, os

E = html.escape
HERE = os.path.dirname(os.path.abspath(__file__))
W = json.load(open(os.path.join(HERE, 'geo', 'world.json')))

def _r(v):
    s = '%.1f' % v
    return s[:-2] if s.endswith('.0') else s

def _miller(la):
    return 1.25 * math.log(math.tan(math.pi / 4 + 0.4 * la * math.pi / 180))

_K = W['W'] / (W['LON1'] - W['LON0']) * 180 / math.pi
_YT = _miller(W['LAT0'])

def proj(lon, lat):
    return ((lon - W['LON0']) * math.pi / 180 * _K, (_YT - _miller(lat)) * _K)

HUB = dict(id='gujarat', name='Gujarat', lon=72.5, lat=23.2)

REGIONS = [
    ('me', 'Middle East & Africa', 'fa-sun'),
    ('eu', 'Europe & Caucasus', 'fa-landmark'),
    ('as', 'Asia', 'fa-umbrella-beach'),
    ('oc', 'Oceania', 'fa-mountain-sun'),
]
REGION_NAME = {k: n for k, n, _ in REGIONS}

# label offset (dx, dy, anchor) keeps crowded pins readable
MARKETS = [
  dict(id='dubai', city='Dubai', country='United Arab Emirates', region='me', lon=55.27, lat=25.2, lab=(-8, -10, 'end'),
       areas='Downtown, Dubai Marina, Palm Jumeirah, Dubai Hills', tier='Premium', hue=38,
       lead='Tax-free rental income, payment plans and a 10-year visa route make Dubai the first stop for most Indian investors.',
       best=['Rental income', 'Residency', 'Off-plan'],
       usps=['No personal income tax in the UAE on rent or resale gains',
             '10-year renewable Golden Visa with AED 2 million of property; off-plan and mortgaged homes can count',
             'Off-plan payments go into regulated escrow accounts, often spread over construction'],
       types=['Branded waterfront apartments', 'Off-plan towers on payment plans', 'Palm and golf-course villas'],
       own='Foreigners can buy freehold in designated areas. The Dubai Land Department charges a 4% transfer fee.',
       devs=['Emaar', 'DAMAC', 'Nakheel', 'Sobha Realty', 'Meraas', 'Binghatti', 'Aldar (Abu Dhabi)']),
  dict(id='london', city='London', country='United Kingdom', region='eu', lon=-0.13, lat=51.51, lab=(-8, -9, 'end'),
       areas='Central London, Canary Wharf, Battersea, Nine Elms', tier='Premium', hue=215,
       lead='A pound-denominated asset in a global city with steady demand from students and professionals.',
       best=['Capital preservation', 'Education', 'Rental income'],
       usps=['Deep tenant demand from universities and the financial district',
             'Freehold and long-leasehold titles under English law',
             'Mortgages available to many overseas buyers'],
       types=['Riverside new-build apartments', 'Homes near top universities', 'Prime central residences'],
       own='No restriction on foreign buyers. Non-residents pay a stamp duty surcharge on top of standard rates.',
       devs=['Berkeley Group', 'Barratt Redrow', 'Taylor Wimpey', 'Canary Wharf Group', 'Lendlease']),
  dict(id='paris', city='Paris & Riviera', country='France', region='eu', lon=2.35, lat=48.86, lab=(-8, 14, 'end'),
       areas='Paris, Nice, Cannes, Antibes', tier='Ultra-luxury', hue=330,
       lead='Haussmann apartments in Paris and villas on the Côte d’Azur: heritage assets with lasting global demand.',
       best=['Lifestyle', 'Heritage', 'Long-term value'],
       usps=['No restriction on foreign ownership',
             'Euro asset inside the European single market',
             'Limited supply of period buildings in central Paris'],
       types=['Haussmann apartments', 'Riviera sea-view villas', 'New-build homes near Paris'],
       own='Foreigners can buy freely. Notary fees and transfer taxes add several percent to resale prices; furnished short lets are tightly regulated in Paris.',
       devs=['Nexity', 'Bouygues Immobilier', 'Vinci Immobilier', 'Kaufman & Broad', 'Icade']),
  dict(id='monaco', city='Monaco', country='Principality of Monaco', region='eu', lon=7.42, lat=43.74, lab=(8, 12, 'start'),
       areas='Monte-Carlo, Fontvieille, Larvotto', tier='Ultra-luxury', hue=350,
       lead='One of the smallest and most valuable property markets in the world, for wealth that wants safety and prestige.',
       best=['Wealth preservation', 'Residency', 'Prestige'],
       usps=['No personal income tax for residents, except French nationals',
             'Very little new supply, which supports long-term values',
             'A home in Monaco is one of the conditions for residence'],
       types=['Sea-view apartments in Monte-Carlo', 'Penthouses', 'Rare new-build residences'],
       own='No restriction on foreign buyers. Supply is very small, so most purchases are resales.',
       devs=['Groupe Marzocco', 'Caroli Group']),
  dict(id='morocco', city='Morocco', country='Kingdom of Morocco', region='me', lon=-7.99, lat=31.63, lab=(-8, 4, 'end'),
       areas='Marrakech, Casablanca, Tangier, Rabat', tier='Accessible', hue=18,
       lead='Riads, golf-resort villas and city apartments at lower prices than southern Europe, a short flight from it.',
       best=['Holiday homes', 'Value', 'Tourism growth'],
       usps=['Co-host of the 2030 FIFA World Cup, with new transport and hotels planned',
             'Popular with European holidaymakers all year',
             'Foreigners can own urban property freehold'],
       types=['Marrakech riads and villas', 'Golf-resort homes', 'Casablanca city apartments'],
       own='Foreigners can buy urban property freehold. Agricultural land is restricted.',
       devs=['Addoha', 'Alliances', 'CGI', 'Palmeraie Development', 'Résidences Dar Saada']),
  dict(id='pattaya', city='Pattaya', country='Thailand', region='as', lon=100.88, lat=12.93, lab=(-9, -6, 'end'),
       areas='Jomtien, Pratumnak, Wong Amat', tier='Accessible', hue=190,
       lead='Beach-front condos at a fraction of global prices, close to Bangkok and the Eastern Economic Corridor.',
       best=['Rental income', 'Holiday home', 'Low entry'],
       usps=['Year-round tourist and expat rental demand',
             'Freehold condo ownership within the foreign quota',
             'Two hours from Bangkok by road'],
       types=['Sea-view condos', 'Resort-managed apartments', 'Pool villas on lease'],
       own='Foreigners can own condos freehold within a building’s 49% foreign quota. Funds must arrive from abroad in foreign currency.',
       devs=['Sansiri', 'AP Thailand', 'Origin Property', 'Supalai', 'Land & Houses']),
  dict(id='phuket', city='Phuket', country='Thailand', region='as', lon=98.39, lat=7.88, lab=(-9, 10, 'end'),
       areas='Bang Tao, Laguna, Kamala, Rawai', tier='Premium', hue=170,
       lead='Branded resort residences and pool villas on Thailand\u2019s largest island, with an international airport.',
       best=['Villa rentals', 'Branded residences', 'Lifestyle'],
       usps=['International airport with flights across Asia',
             'Branded residences with managed rental programmes',
             'Strong winter-season demand from Europe and Asia'],
       types=['Branded resort residences', 'Pool villas', 'Sea-view condos'],
       own='Condos can be owned freehold within the 49% quota. Villas are usually bought as the building plus a registered 30-year land lease.',
       devs=['Banyan Tree Group (Laguna Phuket)', 'Sansiri', 'Origin Property', 'AP Thailand']),
  dict(id='bali', city='Bali', country='Indonesia', region='as', lon=115.19, lat=-8.41, lab=(9, 12, 'start'),
       areas='Canggu, Uluwatu, Ubud, Seminyak', tier='Accessible', hue=150,
       lead='Leasehold villas with holiday-rental demand from travellers, remote workers and the wellness crowd.',
       best=['Villa rentals', 'Lifestyle', 'Low entry'],
       usps=['Strong holiday-rental demand from global travellers',
             'Leasehold villas cost far less than freehold beach markets',
             'Growing remote-work and wellness economy'],
       types=['Leasehold pool villas', 'Boutique resort units', 'Land for villa projects'],
       own='Foreigners cannot hold freehold (Hak Milik). Common routes are long leaseholds, the Hak Pakai right-of-use title, or a foreign-owned company (PT PMA).',
       devs=['Mostly boutique villa developers: we check each one’s licences, land title and delivery record']),
  dict(id='indonesia', city='Jakarta', country='Indonesia', region='as', lon=106.85, lat=-6.21, lab=(-9, 12, 'end'),
       areas='Jakarta, Surabaya, Batam', tier='Mid-market', hue=160,
       lead='Southeast Asia’s largest economy, with large integrated townships built by listed developers.',
       best=['Growth market', 'Townships', 'Long-term'],
       usps=['Largest economy in Southeast Asia, with a young population',
             'Integrated townships with malls, schools and offices',
             'New capital city, Nusantara, under development'],
       types=['City-centre apartments', 'Township homes', 'Commercial units'],
       own='Foreigners can hold apartments and houses under the Hak Pakai title, subject to minimum prices.',
       devs=['Ciputra', 'Sinar Mas Land', 'Agung Podomoro Land', 'Summarecon', 'Lippo Karawaci', 'Pakuwon']),
  dict(id='kl', city='Kuala Lumpur', country='Malaysia', region='as', lon=101.69, lat=3.14, lab=(-9, 4, 'end'),
       areas='KLCC, Bukit Bintang, Mont Kiara, Bangsar', tier='Accessible', hue=200,
       lead='Luxury condos near the Petronas Towers at a fraction of Singapore prices, with freehold titles open to foreigners.',
       best=['Value', 'Long-stay visa', 'Rental income'],
       usps=['Freehold titles available to foreign buyers',
             'Long-stay MM2H visa programme',
             'English widely used; common-law legal system'],
       types=['KLCC luxury condos', 'Serviced residences', 'Family homes in Mont Kiara'],
       own='Foreigners can buy above a minimum price set by each state; the bar is higher in Kuala Lumpur than in many states.',
       devs=['Sunway Property', 'SP Setia', 'Sime Darby Property', 'IOI Properties', 'Eco World', 'Mah Sing', 'Gamuda Land']),
  dict(id='singapore', city='Singapore', country='Republic of Singapore', region='as', lon=103.82, lat=1.35, lab=(9, 5, 'start'),
       areas='Orchard, Marina Bay, River Valley, Sentosa', tier='Ultra-luxury', hue=0,
       lead='A AAA-rated, rule-of-law hub for buyers who put safety and liquidity first.',
       best=['Wealth preservation', 'Stability', 'Prime assets'],
       usps=['AAA credit rating from all three major agencies',
             'Transparent, tightly regulated new-launch market',
             'Strong rental demand from expatriate professionals'],
       types=['Prime condos in the city centre', 'Freehold apartments', 'Sentosa Cove residences'],
       own='Foreigners can buy condos but pay 60% Additional Buyer’s Stamp Duty. Landed homes need government approval.',
       devs=['CapitaLand Development', 'City Developments (CDL)', 'UOL Group', 'GuocoLand', 'Frasers Property', 'Keppel']),
  dict(id='nz', city='New Zealand', country='New Zealand', region='oc', lon=174.76, lat=-36.85, lab=(-9, 4, 'end'),
       areas='Auckland, Queenstown, Wellington', tier='Premium', hue=140,
       lead='A stable democracy with a transparent land registry and lifestyle markets such as Queenstown.',
       best=['Lifestyle', 'Investor visa', 'Long-term'],
       usps=['Transparent, government-backed land titles',
             'Active Investor Plus visa for large investments',
             'Lifestyle demand in Queenstown and Auckland'],
       types=['Auckland apartments', 'Queenstown lifestyle homes', 'New-build developments'],
       own='Most overseas buyers cannot buy existing homes. Exemptions exist (for example Australian and Singaporean citizens) and rules for investor-visa holders are changing; we confirm before you commit.',
       devs=['Fletcher Living', 'Willis Bond', 'Todd Property', 'Ockham Group']),
  dict(id='georgia', city='Georgia', country='Georgia', region='eu', lon=44.79, lat=41.72, lab=(9, 4, 'start'),
       areas='Tbilisi, Batumi, Gudauri', tier='Accessible', hue=12,
       lead='Low entry prices in Tbilisi and the Black Sea resort of Batumi, with fast registration.',
       best=['Low entry', 'Rental income', 'Residency'],
       usps=['Foreigners can own non-agricultural property freehold',
             'Fast registration at the Public Service Hall',
             'Buying property can support a residence permit'],
       types=['Batumi sea-view apartments', 'Tbilisi city apartments', 'Gudauri ski-resort units'],
       own='Foreigners can buy non-agricultural property freehold. Agricultural land is restricted.',
       devs=['Archi', 'Orbi Group', 'M2 Real Estate', 'Alliance Group']),
  dict(id='germany', city='Germany', country='Federal Republic of Germany', region='eu', lon=13.4, lat=52.52, lab=(8, -8, 'start'),
       areas='Berlin, Munich, Frankfurt, Hamburg', tier='Premium', hue=230,
       lead='Europe’s largest economy, where about half of households rent, keeping rental demand deep.',
       best=['Stability', 'Rental income', 'Euro asset'],
       usps=['Europe’s largest economy',
             'Roughly half of households rent their home',
             'Long fixed-rate mortgages are common'],
       types=['Berlin rental apartments', 'Munich and Frankfurt new-builds', 'Small apartment blocks'],
       own='Foreigners can buy freely. Property transfer tax is set by each state.',
       devs=['Vonovia', 'Instone Real Estate', 'Bonava']),
]

DEV_COUNT = sum(len(m['devs']) for m in MARKETS if not m['devs'][0].startswith('Mostly'))


def world_svg(cls='gmap wmap', labels=True, interactive=True):
    vw, vh = W['W'], W['H']
    hx, hy = proj(HUB['lon'], HUB['lat'])
    o = [f'<svg class="{cls}" viewBox="0 0 {vw} {vh}" ' +
         ('role="group" aria-label="World map with routes from Gujarat to fourteen property markets"' if interactive else 'aria-hidden="true"') +
         ' focusable="false" data-wmap>']
    if interactive:
        # graticule every 30 degrees
        g = []
        for lon in range(0, 181, 30):
            x = proj(lon, 0)[0]
            g.append(f'M{_r(x)} 0V{vh}')
        for lat in (-30, 0, 30, 60):
            y = proj(0, lat)[1]
            g.append(f'M0 {_r(y)}H{vw}')
        o.append(f'<g class="gm-grat" aria-hidden="true"><path d="{"".join(g)}"/></g>')
    o.append(f'<path class="gm-fill" aria-hidden="true" d="{W["d"]}"/>')
    o.append(f'<path class="gm-outline" aria-hidden="true" pathLength="1" d="{W["d"]}"/>')
    o.append('<g class="gm-arcs" aria-hidden="true">')
    for i, m in enumerate(MARKETS):
        x, y = proj(m['lon'], m['lat'])
        mx, my = (hx + x) / 2, (hy + y) / 2
        dist = math.hypot(x - hx, y - hy)
        cx, cy = mx, my - dist * .32
        o.append(f'<path class="gm-arc" data-market="{m["id"]}" style="--i:{i}" pathLength="1" d="M{_r(hx)} {_r(hy)}Q{_r(cx)} {_r(cy)} {_r(x)} {_r(y)}"/>')
    o.append('</g><g class="gm-pins">')
    for i, m in enumerate(MARKETS):
        x, y = proj(m['lon'], m['lat'])
        dx, dy, anc = m['lab']
        attrs = (f' data-market="{m["id"]}" data-region="{m["region"]}" tabindex="0" role="button" aria-label="{E(m["city"])}, {E(m["country"])}"'
                 if interactive else '')
        lab = f'<text class="gm-label" x="{dx}" y="{dy}" text-anchor="{anc}">{E(m["city"])}</text>' if labels else ''
        hit = '<circle class="hit" r="11"/>' if interactive else ''
        o.append(f'<g class="gm-pin" style="--i:{i}" transform="translate({_r(x)} {_r(y)})"{attrs}><circle class="ring" r="4"/><circle class="dot" r="3.6"/>{hit}{lab}</g>')
    lab = '<text class="gm-label hub-label" x="0" y="20" text-anchor="middle">Gujarat · our base</text>' if labels else ''
    o.append(f'<g class="gm-pin hub" transform="translate({_r(hx)} {_r(hy)})"><circle class="ring" r="4"/><circle class="ring r2" r="4"/><circle class="dot" r="5"/>{lab}</g>')
    o.append('</g></svg>')
    return ''.join(o)


def hero_map():
    chips = ''.join(f'<button type="button" class="rchip" data-region="{k}" aria-pressed="false"><i class="fas {ic}" aria-hidden="true"></i><span>{E(n)}</span></button>'
                    for k, n, ic in REGIONS)
    return f"""<figure class="gmap-wrap wmap-wrap" data-wmap-wrap>
  <div class="gmap-frame">{world_svg()}</div>
  <div class="gmap-info" aria-live="polite">
    <div class="gmap-info-idle">
      <strong>Pick a market on the map</strong>
      <span>Gold routes run from Gujarat to the fourteen markets we cover. Tap a pin to see why investors buy there.</span>
    </div>
    <div class="gmap-info-live" hidden>
      <strong data-i="title"></strong>
      <span data-i="meta"></span>
      <a class="gmap-info-link" data-i="link" href="#markets">See this market <i class="fas fa-arrow-down" aria-hidden="true"></i></a>
    </div>
  </div>
</figure>
<div class="rchips wchips" role="group" aria-label="Highlight a region">{chips}</div>"""


def market_data_js():
    d = {m['id']: dict(city=m['city'], country=m['country'], tier=m['tier'], best=m['best'], region=REGION_NAME[m['region']]) for m in MARKETS}
    return '<script>window.GLOBAL_MARKETS=' + json.dumps(d, ensure_ascii=False) + ';</script>'


def filters():
    out = ['<button type="button" class="filter-btn active" data-gfilter="all" aria-pressed="true">All markets <span>' + str(len(MARKETS)) + '</span></button>']
    for k, n, _ in REGIONS:
        c = sum(1 for m in MARKETS if m['region'] == k)
        out.append(f'<button type="button" class="filter-btn" data-gfilter="{k}" aria-pressed="false">{E(n)} <span>{c}</span></button>')
    return '<div class="project-filters gfilters reveal" role="group" aria-label="Filter markets by region">' + ''.join(out) + '</div>'


def market_cards():
    out = []
    for i, m in enumerate(MARKETS):
        best = ''.join(f'<li>{E(b)}</li>' for b in m['best'])
        usps = ''.join(f'<li><i class="fas fa-check" aria-hidden="true"></i> {E(u)}</li>' for u in m['usps'])
        types = ''.join(f'<li>{E(t)}</li>' for t in m['types'])
        if m['devs'][0].startswith('Mostly'):
            devs = f'<p class="mkt-note">{E(m["devs"][0])}.</p>'
        else:
            devs = '<ul class="dev-pills">' + ''.join(f'<li>{E(d)}</li>' for d in m['devs']) + '</ul>'
        name = m['city'] if m['city'] == m['country'] else m['city']
        place = m['country'] if m['city'] != m['country'] else ''
        out.append(f"""<article class="mkt-card spot reveal" id="market-{m['id']}" data-region="{m['region']}" data-market="{m['id']}" style="--hue:{m['hue']};--d:{(i % 3) * .08:.2f}s">
  <header class="mkt-band">
    <span class="mkt-region">{E(REGION_NAME[m['region']])}</span>
    <span class="mkt-tier">{E(m['tier'])}</span>
    <h3>{E(name)}</h3>
    <p class="mkt-where">{E(place + (' · ' if place else '') + m['areas'])}</p>
  </header>
  <div class="mkt-body">
    <p class="mkt-lead">{E(m['lead'])}</p>
    <ul class="mkt-best" aria-label="Best for">{best}</ul>
    <h4>Why investors buy</h4>
    <ul class="check-list mkt-usps">{usps}</ul>
    <h4>Properties we source</h4>
    <ul class="mkt-types">{types}</ul>
    <details class="mkt-more">
      <summary>Ownership rules and developers <i class="fas fa-plus" aria-hidden="true"></i></summary>
      <div class="mkt-more-body">
        <p>{E(m['own'])}</p>
        <h5>Developers active here</h5>
        {devs}
      </div>
    </details>
    <button type="button" class="cta-btn primary small mkt-cta" data-enquire="Global property — {E(m['city'])}" data-interest="Global property"><i class="fas fa-paper-plane" aria-hidden="true"></i> Get a {E(m['city'])} shortlist</button>
  </div>
</article>""")
    return '\n'.join(out)


def developer_columns():
    out = []
    for k, n, ic in REGIONS:
        rows = []
        for m in MARKETS:
            if m['region'] != k:
                continue
            ds = m['devs']
            txt = 'Boutique developers, vetted one by one' if ds[0].startswith('Mostly') else ', '.join(ds)
            rows.append(f'<li><strong>{E(m["city"])}</strong><span>{E(txt)}</span></li>')
        out.append(f"""<div class="dev-col reveal">
  <h3><i class="fas {ic}" aria-hidden="true"></i> {E(n)}</h3>
  <ul>{''.join(rows)}</ul>
</div>""")
    return '\n'.join(out)


TICKER = ['Dubai', 'London', 'Paris', 'Monaco', 'Marrakech', 'Pattaya', 'Phuket', 'Bali', 'Jakarta',
          'Kuala Lumpur', 'Singapore', 'Auckland', 'Tbilisi', 'Batumi', 'Berlin', 'Munich']


FAQ = [
    ("Can a resident Indian buy property abroad?",
     "Yes. Under the RBI’s Liberalised Remittance Scheme (LRS) each resident individual can send up to USD 250,000 abroad per financial year, through an authorised bank, and this can be used to buy property. Family members buying together can each use their own limit. Your bank will ask for the sale agreement and Form A2. Confirm the current limit and paperwork with your bank before you sign."),
    ("Will I pay tax in India on rent or gains from a property abroad?",
     "If you are resident in India for tax, your worldwide income is taxable here. Tax paid in the other country can usually be credited under the double taxation agreement between India and that country. Overseas property must also be declared in Schedule FA of your income tax return. Speak to your chartered accountant before you buy."),
    ("Is TCS deducted when I send money for a property?",
     "Banks collect Tax Collected at Source on LRS remittances above a yearly threshold. It is not an extra cost: you can adjust it against your income tax or claim it back in your return. Rates and thresholds change with each budget, so check the current figures with your bank."),
    ("Does buying property give me a visa?",
     "In some places. Dubai gives a 10-year Golden Visa for AED 2 million of property. Georgia and Malaysia have residence routes linked to property or long stays, and Monaco asks for a home there before granting residence. Thailand does not give a visa for buying property. Rules change, so we confirm the current position for your market."),
    ("Are you the developers’ agents?",
     "Developer names on this page show who is active in each market; they are not a list of our partners. We tell you clearly when we are an authorised channel partner for a project, and we share the developer’s registration and escrow details for every off-plan unit we put in front of you."),
    ("How do I see a property without flying out?",
     "We arrange video walkthroughs, developer presentations and independent inspections. When you are ready to travel, we plan a short viewing trip around your shortlist."),
]


def faq():
    out = []
    for i, (q, a) in enumerate(FAQ):
        out.append(f"""<div class="faq-item reveal">
  <button type="button" class="faq-q" aria-expanded="false" aria-controls="gfaq-a{i}" id="gfaq-q{i}"><span>{E(q)}</span><i class="fas fa-plus" aria-hidden="true"></i></button>
  <div class="faq-a" id="gfaq-a{i}" role="region" aria-labelledby="gfaq-q{i}"><div><p>{E(a)}</p></div></div>
</div>""")
    return '\n'.join(out)


def global_form(idp='g'):
    opts = ''.join(f'<option>{E(m["city"] + (" (" + m["country"] + ")" if m["city"] != m["country"] and m["country"] not in m["city"] else ""))}</option>' for m in MARKETS)
    return f"""<div class="form-shell">
<form class="inquiry-form" novalidate data-project="Global property">
  <div class="form-row">
    <div class="form-group"><input id="{idp}-name" name="name" type="text" placeholder=" " autocomplete="name" required/><label for="{idp}-name">Full name *</label><span class="field-error" aria-live="polite"></span></div>
    <div class="form-group"><input id="{idp}-phone" name="phone" type="tel" inputmode="tel" placeholder=" " autocomplete="tel" required/><label for="{idp}-phone">Phone *</label><span class="field-error" aria-live="polite"></span></div>
  </div>
  <div class="form-group"><input id="{idp}-email" name="email" type="email" placeholder=" " autocomplete="email"/><label for="{idp}-email">Email (optional)</label><span class="field-error" aria-live="polite"></span></div>
  <div class="form-row">
    <div class="form-group"><select id="{idp}-market" name="market" data-label="Market">{opts}<option>More than one / not sure</option><option>Another country</option></select><label for="{idp}-market">Market</label></div>
    <div class="form-group"><select id="{idp}-goal" name="goal" data-label="Main goal"><option selected>Rental income</option><option>Capital growth</option><option>Residency or visa</option><option>Holiday home</option><option>Children’s education</option><option>Diversification</option></select><label for="{idp}-goal">Main goal</label></div>
  </div>
  <div class="form-row">
    <div class="form-group"><select id="{idp}-budget" name="budget" data-label="Budget"><option>Up to USD 250,000</option><option selected>USD 250,000 – 500,000</option><option>USD 500,000 – 1 million</option><option>USD 1 – 5 million</option><option>Above USD 5 million</option></select><label for="{idp}-budget">Budget</label></div>
    <div class="form-group"><select id="{idp}-when" name="when" data-label="Timeline"><option>Within 3 months</option><option selected>3 – 12 months</option><option>Just exploring</option></select><label for="{idp}-when">Timeline</label></div>
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
  <div class="form-group"><textarea id="{idp}-message" name="message" rows="3" placeholder=" "></textarea><label for="{idp}-message">Anything else we should know (optional)</label></div>
  <div class="form-actions">
    <button type="submit" class="submit-btn wa-submit"><i class="fas fa-paper-plane"></i> <span class="btn-label">Send enquiry</span></button>
  </div>
  <p class="form-note">Your details go straight to our team, and WhatsApp opens so you can chat with an advisor right away. To stop spam, we also record your device type and approximate location with the enquiry.</p>
</form>
<div class="form-success" role="status">
  <i class="fas fa-check-circle"></i><h3>Enquiry sent</h3><p data-s="msg"></p>
  <button type="button" class="cta-btn ghost small" data-form-reset>Start a new enquiry</button>
</div>
</div>"""


def home_global_card():
    return f"""<a href="global.html" class="dest-card land-card global-card spot tilt reveal" data-tilt="2" data-rv="zoom">
  <div class="land-card-map" aria-hidden="true">{world_svg('gmap wmap mini', labels=False, interactive=False)}</div>
  <div class="dest-body land-card-body">
    <span class="section-tag">{len(MARKETS)} markets abroad</span>
    <h3>Global property</h3>
    <p>Dubai, London, Paris, Monaco, Singapore, Bali, Phuket and more. We shortlist homes and investments abroad and guide you through LRS remittance and paperwork from India.</p>
    <div class="dest-facts">
      <div><strong>{len(MARKETS)}</strong>markets</div>
      <div><strong>{len(REGIONS)}</strong>regions</div>
      <div><strong>{DEV_COUNT}</strong>developers tracked</div>
    </div>
    <span class="cta-btn primary small">Explore global property <i class="fas fa-arrow-right"></i></span>
  </div>
</a>"""


def projects_global_banner():
    return f"""<a href="global.html" class="promo-land spot reveal tilt" data-tilt="2">
  <div class="promo-land-map" aria-hidden="true">{world_svg('gmap wmap mini faint', labels=False, interactive=False)}</div>
  <div class="promo-land-body">
    <span class="section-tag">Global property</span>
    <h3>Looking beyond India?</h3>
    <p>Homes and investments in Dubai, London, Paris, Singapore, Bali and nine more markets, shortlisted for Indian buyers.</p>
    <span class="go">See the markets <i class="fas fa-arrow-right"></i></span>
  </div>
</a>"""
