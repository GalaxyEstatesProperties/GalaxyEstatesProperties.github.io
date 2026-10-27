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
    ('eu', 'Europe', 'fa-landmark'),
    ('as', 'Asia', 'fa-umbrella-beach'),
]
REGION_NAME = {k: n for k, n, _ in REGIONS}

# label offset (dx, dy, anchor) keeps crowded pins readable
MARKETS = [
  dict(id='dubai', city='Dubai', country='United Arab Emirates', region='me', lon=55.27, lat=25.2, lab=(-8, -10, 'end'),
       areas='Downtown, Dubai Marina, Palm Jumeirah, Dubai Hills; Abu Dhabi', tier='Premium', hue=38,
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
  dict(id='thailand', city='Thailand', country='Thailand', region='as', lon=100.88, lat=12.93, lab=(-9, -6, 'end'),
       areas='Phuket (Bang Tao, Laguna, Patong, Kamala) and Pattaya (Jomtien, Pratumnak, Wong Amat)', tier='Accessible to premium', hue=180,
       lead='One country, two coasts: beach-front condos in Pattaya near Bangkok, and branded residences and pool villas on Phuket, Thailand\u2019s largest island.',
       best=['Rental income', 'Holiday home', 'Branded residences'],
       usps=['Year-round tourist and expat rental demand on both coasts',
             'Freehold condo ownership within the 49% foreign quota',
             'Pattaya is two hours from Bangkok; Phuket has an international airport with flights across Asia'],
       types=['Sea-view condos in Pattaya', 'Branded resort residences in Phuket', 'Pool villas on lease'],
       own='Foreigners can own condos freehold within a building\u2019s 49% foreign quota; funds must arrive from abroad in foreign currency. Villas are usually bought as the building plus a registered 30-year land lease.',
       devs=['Sansiri', 'AP Thailand', 'Origin Property', 'Supalai', 'Land & Houses', 'Banyan Tree Group (Laguna Phuket)']),
  dict(id='indonesia', city='Jakarta', country='Indonesia', region='as', lon=106.85, lat=-6.21, lab=(-9, 12, 'end'),
       areas='Jakarta, Tangerang (BSD City), Bekasi, Karawang, Surabaya', tier='Mid-market', hue=160,
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
]

DEV_COUNT = len({d for m in MARKETS for d in m['devs'] if not d.startswith('Mostly')})

# ---------------------------------------------------------------- current projects (checked 27 Oct 2026)
# One or more projects per developer named in each market card: under construction, newly launched, or newly completed.
# st: 'launch' new launch · 'build' under construction · 'sale' on sale (stage not published) · 'ready' newly completed
# page: our own listing page (linked instead of the outside source); note: a developer with nothing that qualifies right now.
ST = {'launch': 'New launch', 'build': 'Under construction', 'sale': 'Now selling', 'ready': 'Newly completed'}
PROJECTS = {
  'dubai': [
    dict(dev='Emaar', name='Fior 1, Rashid Yachts & Marina', where='Mina Rashid, Dubai', st='build', price='from AED 2.2M', when='Handover Q4 2029', page='emaar-fior-1-dubai.html'),
    dict(dev='Emaar', name='Valo, Dubai Creek Harbour', where='The Lagoons, Dubai', st='build', price='launched from AED 1.79M', when='Handover Sep 2028', page='emaar-valo-dubai.html'),
    dict(dev='DAMAC', name='DAMAC Islands 2', where='Off Emirates Road (E611), Dubai', st='launch', price='4-bed townhouses from AED 2.7M', when='Handover 2030 · plan 20/55/25',
         src='https://www.bayut.com/mybayut/damac-islands-2/'),
    dict(dev='Nakheel', name='Palm Central Private Residences', where='Palm Jebel Ali, Dubai', st='launch', price='1–4 bed apartments from AED 2.7M', when='Launched Jun 2026 · completion Sep 2030',
         src='https://www.thenationalnews.com/business/property/2026/06/24/nakheel-launches-222-homes-for-sale-at-palm-jebel-ali-with-prices-from-dh27m/'),
    dict(dev='Sobha Realty', name='Sobha SeaHaven, Tower B', where='Dubai Marina', st='build', price='launch price from AED 3.1M', when='Completion late 2026 · plan 80/20',
         src='https://metropolitan.realestate/media/news/tower-b-sobha-seahaven-new-launch-in-dubai/'),
    dict(dev='Meraas', name='Nad Al Sheba Gardens, phases 5 & 6', where='Nad Al Sheba, Dubai', st='build', price='3-bed townhouses from AED 4.18M', when='Completion 2027',
         src='https://metropolitan.realestate/media/news/nad-al-sheba-gardens-5-6-exciting-new-launch-in-dubai/'),
    dict(dev='Binghatti', name='Burj Binghatti Jacob & Co Residences', where='Business Bay, Dubai', st='build', price='2-bed from AED 8.4M', when='Handover Q2 2027', page='binghatti-burj-jacob-dubai.html'),
    dict(dev='Binghatti', name='Mercedes-Benz Places | Binghatti City', where='Nad Al Sheba, Meydan, Dubai', st='build', price='studios from AED 1.35M', when='Built in 3 phases', page='binghatti-mercedes-city-dubai.html'),
    dict(dev='Aldar', name='Fahid Beach Residences', where='Fahid Island, Abu Dhabi', st='build', price='1-bed from AED 3.5M', when='Handover Q1 2029 · plan 10/55/35',
         src='https://insiderealty.ae/en/projects/aldar-fahid-beach-residences-abu-dhabi'),
  ],
  'london': [
    dict(dev='Berkeley Group', name='Bermondsey Place (The Art Mill & The Art House)', where='Bermondsey, SE1', st='build', price='1-bed from £475,000', when='Completion 2027',
         src='https://www.edgeprop.sg/property-news/berkeley-group-launch-sales-london-se1-residential-project-prices-824000'),
    dict(dev='Barratt Redrow', name='Bermondsey Heights (Barratt London)', where='Bermondsey, SE16', st='ready', price='2-bed from £596,000', when='Completed 2025',
         src='https://www.edgeprop.sg/amp/property-news/bermondsey-heights-london-launched-sale'),
    dict(dev='Taylor Wimpey', name='Hertford Mill', where='Hackney Wick, E9', st='sale', price='apartments from £399,000', when='Selling now',
         src='https://www.new-builds.co.uk/taylor-wimpey-in/london'),
    dict(dev='Canary Wharf Group', name='One Park Drive, Wood Wharf', where='Canary Wharf, E14', st='ready', price='duplex penthouses from £4.1M', when='Completed; final homes on sale',
         src='https://www.knightfrank.co.uk/new-homes-for-sale/canary-wharf'),
    dict(dev='Lendlease', name='Park & Sayer, Elephant Park', where='Elephant & Castle, SE17', st='ready', price='1-bed from £599,950', when='Completed 2024 · 229 homes',
         src='https://blog.icompareloan.com/londons-most-desirable/'),
  ],
  'paris': [
    dict(dev='Nexity', name='Replay', where='Gennevilliers (92)', st='sale', price='studio to 5-room from €170,000', when='Selling now',
         src='https://www.plan-immobilier.fr/immobilier-neuf/gennevilliers-92230/replay/1022625'),
    dict(dev='Bouygues Immobilier', name='15ème Merveille', where='Paris 15e', st='sale', price='from €1,050,000', when='Delivery Q2 2029',
         src='https://www.bouygues-immobilier.com/logements-neufs-ile-de-france-0'),
    dict(dev='Vinci Immobilier', name='Plurielles', where='Colombes (92)', st='sale', price='2 to 5-room from €259,000', when='Selling now',
         src='https://www.plan-immobilier.fr/immobilier-neuf/colombes-92700/plurielles-4/1027141'),
    dict(dev='Kaufman & Broad', name='New homes at the gates of Paris', where='Courbevoie (92)', st='sale', price='studio to 4-room from €286,000', when='Selling now',
         src='https://www.plan-immobilier.fr/immobilier-neuf/courbevoie-92400/une-agreable-vie-de-quartier-aux-portes-de-paris/1034096'),
    dict(dev='Icade', name='Métamorphose', where='Épinay-sur-Seine (93)', st='ready', price='65 homes', when='Inaugurated May 2026',
         src='https://www.icade.fr/newsroom/communiques/icade-inaugure-metamorphose-a-epinay-sur-seine-93.pdf'),
  ],
  'monaco': [
    dict(dev='Groupe Marzocco', name='Bay House', where='Larvotto, Monaco', st='ready', price='56 apartments and 5 villas · price on request', when='Inaugurated Dec 2024',
         src='https://www.monacoproperties.mc/en/bay-house-monaco-residences-luxury-living.html'),
    dict(dev='SAM L’Anse du Portier', name='Mareterra', where='Larvotto, Monaco', st='ready', price='apartments, townhouses and villas · resale only', when='Inaugurated Dec 2024', page='mareterra-monaco.html'),
    dict(dev='Caroli Group', note='No new homes on sale at present; we track its next Monaco launch and resale homes in its buildings.'),
  ],
  'morocco': [
    dict(dev='Addoha', name='Résidence Al Anouar', where='Tit Mellil, Casablanca', st='sale', price='from MAD 435,000', when='Selling now',
         src='https://www.groupeaddoha.com/fr/projet/residence-al-anouar/'),
    dict(dev='Alliances', name='Al Maaden Collections', where='Marrakech', st='ready', price='golf-resort villas and apartments', when='Delivered in 2026',
         src='https://boursenews.ma/web-tv/detail/marches/alliances-projets-2026-2027'),
    dict(dev='CGI', name='Panorama 16', where='Casablanca', st='launch', price='2 to 6-room apartments from 50 sq m', when='Brochure Jul 2026',
         src='https://cgi.ma/sites/default/files/2026-07/Brochure%20Panorama%2016%20modifie%CC%81e.pdf'),
    dict(dev='Palmeraie Development', name='Ocean Palm, phase 3', where='Dar Bouazza, Casablanca', st='build', price='56 duplex villas', when='Phases 1–2 delivered; phase 3 on sale',
         src='https://boursenews.ma/web-tv/detail/maroc/palmeraie-immobilier-livraison-des-deux-premieres-tranches-du-projet-ocean-palm'),
    dict(dev='Résidences Dar Saada', note='Builds mainly social and economy housing at present; nothing suited to overseas buyers right now.'),
  ],
  'thailand': [
    dict(dev='Sansiri', name='BRISA Patong', where='Patong, Phuket', st='launch', price='from ฿3.9M, fully furnished', when='Bookings from 25 Nov 2026 · 389 units',
         src='https://buro.co.th/en/news/buro-brisa-patong'),
    dict(dev='Sansiri', name='dcondo vite', where='North Pattaya', st='build', price='studio to 2-bed', when='Completion Nov 2027', page='dcondo-vite-pattaya.html'),
    dict(dev='Banyan Tree Group', name='Skypark Elara Lakelands', where='Laguna Lakelands, Phuket', st='build', price='1–3 bed condos, 54–186 sq m', when='Phase 1 of about 220 homes', page='skypark-elara-lakelands-phuket.html'),
    dict(dev='Origin Property', name='SO Origin Bangtao Beach', where='Bang Tao, Phuket', st='ready', price='from ฿4.34M', when='Completed Jun 2026',
         src='https://www.fazwaz.com/property-developers/origin-property-d174'),
    dict(dev='Origin Property', name='SO Origin Pattaya', where='Na Kluea, Pattaya', st='ready', price='from ฿2.57M', when='Completed Jun 2026',
         src='https://www.fazwaz.com/property-developers/origin-property-d174'),
    dict(dev='AP Thailand', name='LIFE Charoennakhon–Sathorn', where='Riverside, Bangkok', st='ready', price='from ฿3.89M', when='Completed; transfers from Aug 2026',
         src='https://www.thaipr.net/en/estate_en/3750736'),
    dict(dev='Supalai', name='Supalai Primo Pattaya', where='Thung Klom–Tan Man Road, Pattaya', st='sale', price='semi-detached and townhomes from ฿2.22M', when='154 homes',
         src='https://www.supalai.com/en/project/house-townhome/supalai-primo-pattaya'),
    dict(dev='Land & Houses', name='Nantawan Prestige Ratchaphruek–Prannok', where='Bangkok', st='launch', price='detached houses ฿60–100M', when='Launch Q1 2026 · 34 houses',
         src='https://investor.lh.co.th/en/updates/press-releases/477/land-and-houses-unveils-2026-business-plan-targeting-thb-15-billion-in-bookings-thb-17-billion-in-property-transfers-and-thb-99-billion-in-rental-property-revenue'),
  ],
  'indonesia': [
    dict(dev='Ciputra', name='The Forestine, Cluster Lacewood', where='CitraGarden City, West Jakarta', st='launch', price='houses from Rp 1.8 billion', when='Launched Jul 2026',
         src='https://ekonomi.bisnis.com/read/20260728/47/1991754/ciputra-ctra-kejar-penjualan-400-unit-the-forestine-di-jakarta-barat'),
    dict(dev='Sinar Mas Land', name='Island Villa, NavaPark', where='BSD City, Tangerang', st='launch', price='35 villas from Rp 80 billion', when='Launched Jun 2026',
         src='https://ekonomi.bisnis.com/read/20260604/47/1978326/sinar-mas-land-luncurkan-proyek-hunian-mewah-mulai-rp80-miliar-di-bsd'),
    dict(dev='Agung Podomoro Land', name='Kota Kertabumi and other “Living in Style” estates', where='Karawang and Greater Jakarta', st='sale', price='homes from about Rp 300 million', when='Selling now',
         src='https://industri.kontan.co.id/news/agung-podomoro-apln-tawarkan-hunian-mulai-rp-300-jutaan-dengan-konsep-lifestyle'),
    dict(dev='Summarecon', name='Cluster Chelia, Summarecon Crown Gading', where='Bekasi, near Kelapa Gading', st='sale', price='houses from about Rp 983 million', when='Selling now',
         src='https://www.analisproperti.com/2025/07/cluster-chelia-summarecon-crown-gading.html'),
    dict(dev='Lippo Karawaci', name='Brentwood Villas, Rolling Hills', where='Karawang, West Java', st='launch', price='villas from Rp 1.15 billion (early bird)', when='Launched Oct 2026',
         src='https://market.bisnis.com/read/20261026/192/2015835/grup-lippo-lpkr-penetrasi-pasar-properti-di-karawang'),
    dict(dev='Pakuwon', name='Beverly Terrace, Pakuwon City', where='Surabaya', st='launch', price='shophouses from Rp 4.9 billion', when='Ground broken Oct 2026',
         src='https://surabaya.bisnis.com/read/20261023/531/2015170/pakuwon-pwon-rilis-ruko-beverly-terrace-harga-mulai-rp49-miliar'),
  ],
  'kl': [
    dict(dev='Sunway Property', name='Sunway Flora Residences', where='Bukit Jalil, Kuala Lumpur', st='build', price='freehold, from RM 807,000', when='Completion 2026 · 748 units',
         src='https://www.metproperty.com/new-launches/kuala-lumpur/sunway-flora-residences-bukit-jalil/'),
    dict(dev='SP Setia', name='Aurora, phase 1', where='Setia Bayuemas South, Klang', st='launch', price='terrace homes from RM 880,000', when='Launched Feb 2026 · 82 homes',
         src='https://www.thestar.com.my/business/business-news/2026/02/11/setia-to-launch-aurora-phase-1-at-setia-bayuemas-in-klang'),
    dict(dev='Sime Darby Property', name='Tiara Residences', where='Bukit Jelutong, Selangor', st='launch', price='freehold link homes from RM 1.5M', when='Launched Jun 2026',
         src='https://theedgemalaysia.com/node/807174'),
    dict(dev='IOI Properties', name='2Rio Residence, IOI Rio City', where='Bandar Puteri Puchong', st='launch', price='serviced apartments from RM 605,000', when='Newly launched · 632 units',
         src='https://theedgemalaysia.com/content/advertise/2rio-residence-live-work-and-shop-epicentre-bandar-puteri-puchong'),
    dict(dev='Eco World', name='Eco Radiance, Astrea Collection', where='Semenyih, Klang Valley', st='launch', price='freehold terrace homes from about RM 598,000', when='Preview from 19 Oct 2026',
         src='https://www.everydayonsales.com/947076/19-october-2026-onwards-ecoworld-eco-radiance-astrea-collection-freehold-2-storey-terrace-homes-from-rm598k-exclusive-property-preview-at-klang-valley/'),
    dict(dev='Mah Sing', name='M Aria', where='Sentul, Kuala Lumpur', st='launch', price='freehold 3-bed from RM 498,000', when='606 units',
         src='https://www.edgeprop.my/content/1914461/mah-sing-opens-m-aria-sales-gallery-sentul-indicative-selling-price-starts-rm498000'),
    dict(dev='Gamuda Land', name='Haus on 15', where='SS15, Subang Jaya', st='launch', price='614 serviced residences · price on request', when='Launched Jul 2026 · completion by 2029',
         src='https://gslglobal.com/2026/07/03/gamuda-land-and-taylors-assets-launch-rm540-million-development-in-ss15/'),
  ],
  'singapore': [
    dict(dev='CapitaLand Development', name='Thomson Reserve (with UOL and SingLand)', where='Bright Hill Drive, Upper Thomson', st='launch', price='from S$2,608 psf; 2-bed from S$1.544M', when='Sales launch 31 Oct 2026 · 1,268 units',
         src='https://stackedhomes.com/thomson-reserve-launch-2608-psf/'),
    dict(dev='City Developments (CDL)', name='Newport Residences', where='Anson Road, CBD', st='build', price='1-bed from S$1.298M', when='Freehold · launched Jan 2026', page='newport-residences-singapore.html'),
    dict(dev='UOL Group', name='UpperHouse at Orchard Boulevard', where='Orchard Boulevard', st='build', price='about S$3,350 psf at launch', when='Launched Jul 2025 · 301 units',
         src='https://www.edgeprop.sg/property-news/uol-singland-moves-53-units-upperhouse-orchard-boulevard-launch-day-3350-psf'),
    dict(dev='GuocoLand', name='Tengah Garden Residences', where='Tengah Garden Avenue (District 24)', st='launch', price='1-bed from S$980,000', when='Launched Apr 2026 · 863 units',
         src='https://stackedhomes.com/new-launch-condos-2026-singapore-complete-guide/'),
    dict(dev='Frasers Property', name='Dunearn House', where='Dunearn Road, Bukit Timah', st='build', price='2-bed from S$1.46M', when='Expected 2029–2030', page='dunearn-house-singapore.html'),
    dict(dev='Keppel', name='Gladia Heights (with Khang Dien)', where='Ho Chi Minh City, Vietnam', st='launch', price='616 apartments and 23 shophouses', when='Launched Aug 2026 · Keppel’s latest home launch is in Vietnam',
         src='https://www.keppel.com/realestate/vn/en/News-Library/08-2026-Keppel-and-Khang-Dien-achieve-strong-sales-at-Gladia-Heights-launch'),
  ],
}
PROJECT_COUNT = sum(1 for v in PROJECTS.values() for p in v if 'name' in p)

NUMW = {n: w for n, w in enumerate('zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen'.split())}

def projects_list(mid):
    rows = []
    for p in PROJECTS.get(mid, []):
        if 'note' in p:
            rows.append(f'<li class="mp-row mp-none"><span class="mp-dev">{E(p["dev"])}</span><span class="mp-meta">{E(p["note"])}</span></li>')
            continue
        name = (f'<a class="mp-name" href="{p["page"]}">{E(p["name"])} <i class="fas fa-arrow-right" aria-hidden="true"></i></a>' if p.get('page')
                else f'<span class="mp-name">{E(p["name"])}</span>')
        src = ('' if p.get('page') else
               f' <a class="mp-src" href="{E(p["src"])}" target="_blank" rel="noopener nofollow">Source <i class="fas fa-arrow-up-right-from-square" aria-hidden="true"></i></a>')
        rows.append(f'<li class="mp-row"><span class="mp-top"><span class="mp-dev">{E(p["dev"])}</span><span class="mp-st st-{p["st"]}">{ST[p["st"]]}</span></span>'
                    f'{name}<span class="mp-meta">{E(p["where"])} · {E(p["price"])} · {E(p["when"])}</span>{src}</li>')
    n = sum(1 for p in PROJECTS.get(mid, []) if 'name' in p)
    return (f'<h4>Current projects <span class="mp-count">{n}</span></h4><ul class="mkt-projects">{"".join(rows)}</ul>'
            '<p class="mp-foot">Prices and dates as published by the developer or the linked source (checked Oct 2026). Ask us for live availability.</p>') if rows else ''


def world_svg(cls='gmap wmap', labels=True, interactive=True):
    vw, vh = W['W'], W['H']
    hx, hy = proj(HUB['lon'], HUB['lat'])
    o = [f'<svg class="{cls}" viewBox="0 0 {vw} {vh}" ' +
         (f'role="group" aria-label="World map with routes from Gujarat to {NUMW[len(MARKETS)]} property markets"' if interactive else 'aria-hidden="true"') +
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
      <span>Gold routes run from Gujarat to the {NUMW[len(MARKETS)]} markets we cover. Tap a pin to see why investors buy there.</span>
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


GUIDES = {'dubai': ('dubai-uae-property.html', 'Dubai'), 'singapore': ('singapore-property.html', 'Singapore'), 'thailand': ('thailand-property.html', 'Thailand'),
          'kl': ('malaysia-property.html', 'Malaysia'), 'monaco': ('monaco-property.html', 'Monaco')}
def guide_link(mid):
    g = GUIDES.get(mid)
    return f'<a class="cta-btn ghost small mkt-guide" href="{g[0]}"><i class="fas fa-book-open" aria-hidden="true"></i> Open the {E(g[1])} guide</a>' if g else ''

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
    {projects_list(m['id'])}
    <details class="mkt-more">
      <summary>Ownership rules and developers <i class="fas fa-plus" aria-hidden="true"></i></summary>
      <div class="mkt-more-body">
        <p>{E(m['own'])}</p>
        <h5>Developers active here</h5>
        {devs}
      </div>
    </details>
    {guide_link(m['id'])}
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


TICKER = ['Dubai', 'Abu Dhabi', 'London', 'Paris', 'Monaco', 'Marrakech', 'Casablanca', 'Phuket', 'Pattaya', 'Bangkok',
          'Jakarta', 'Kuala Lumpur', 'Singapore']


FAQ = [
    ("Can a resident Indian buy property abroad?",
     "Yes. Under the RBI’s Liberalised Remittance Scheme (LRS) each resident individual can send up to USD 250,000 abroad per financial year, through an authorised bank, and this can be used to buy property. Family members buying together can each use their own limit. Your bank will ask for the sale agreement and Form A2. Confirm the current limit and paperwork with your bank before you sign."),
    ("Will I pay tax in India on rent or gains from a property abroad?",
     "If you are resident in India for tax, your worldwide income is taxable here. Tax paid in the other country can usually be credited under the double taxation agreement between India and that country. Overseas property must also be declared in Schedule FA of your income tax return. Speak to your chartered accountant before you buy."),
    ("Is TCS deducted when I send money for a property?",
     "Banks collect Tax Collected at Source on LRS remittances above a yearly threshold. It is not an extra cost: you can adjust it against your income tax or claim it back in your return. Rates and thresholds change with each budget, so check the current figures with your bank."),
    ("Does buying property give me a visa?",
     "In some places. Dubai gives a 10-year Golden Visa for AED 2 million of property. Malaysia has a long-stay visa programme (MM2H), and Monaco asks for a home there before granting residence. Thailand does not give a visa for buying property. Rules change, so we confirm the current position for your market."),
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
  <p class="form-note"><i class="fas fa-lock"></i> Your data is secure. We never share your details with anyone without your consent. Every enquiry is checked only to make sure it comes from a genuine buyer, not a fake one. To stop spam, we also note your device type and approximate location with the enquiry.</p>
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
    <p>Dubai, London, Paris, Monaco, Singapore, Phuket, Kuala Lumpur and more. We shortlist homes and investments abroad and guide you through LRS remittance and paperwork from India.</p>
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
    <p>Homes and investments in Dubai, London, Paris, Singapore, Thailand and {NUMW[len(MARKETS) - 5]} more markets, shortlisted for Indian buyers.</p>
    <span class="go">See the markets <i class="fas fa-arrow-right"></i></span>
  </div>
</a>"""
