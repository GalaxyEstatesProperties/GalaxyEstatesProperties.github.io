"""One guide page per country where we list property abroad: why Indian investors buy there, how to buy from India,
our listings on a map, each developer's ongoing projects (official registers where they exist) and an FAQ.
Facts checked 18 Oct 2026; every figure carries its source on the page."""
import html, json, os
E = html.escape
HERE = os.path.dirname(os.path.abspath(__file__))
DLD_DEV = json.load(open(os.path.join(HERE, 't3dall', 'dld_dev.json')))
CHECKED = '18 Oct 2026'

# ---------------------------------------------------------------- India-side rules (same for every country)
INDIA_STEPS = [
  ('fa-indian-rupee-sign', 'Send the money under LRS',
   'Each resident Indian can remit up to USD 250,000 a financial year under the RBI’s Liberalised Remittance Scheme, and buying property abroad is a permitted purpose. Family members can pool their limits for one property only if each is a co-owner of it.',
   ('HSBC India LRS FAQ', 'https://www.hsbc.bank.in/help/faqs/lrs/')),
  ('fa-receipt', 'Plan for TCS at the bank',
   'Banks collect 20% TCS on LRS remittances above ₹10 lakh in a financial year (other than education and medical). It is not an extra cost: you claim it back as a credit against your income tax or as a refund.',
   ('RBL Bank, TCS on LRS (revised 1 Apr 2026)', 'https://www.rbl.bank.in/personal-banking/forex-services/tax-collected-at-source')),
  ('fa-file-signature', 'Buy under local rules',
   None, None),
  ('fa-scale-balanced', 'Report it in your Indian return',
   'Resident Indians are taxed in India on worldwide income, so rent and sale gains abroad go in your Indian return, with credit for tax paid abroad under the tax treaty. The property itself must be shown in Schedule FA (foreign assets) every year. We work with your CA on this.',
   None),
]

COUNTRIES = [
 dict(slug='dubai-uae-property', key='uae', name='United Arab Emirates', short='Dubai', flag='🇦🇪', title='Dubai, UAE',
      seo='Dubai Property for Indian Investors – Golden Visa, Yields & New Projects | Galaxy Estates Properties',
      desc='Why Indian investors buy in Dubai: no tax on rent in the UAE, 10-year Golden Visa from AED 2 million, regulated escrow. New projects by Emaar, Binghatti, Danube, Sobha and DAMAC with DLD progress.',
      hero_pid='binghatti-burj-jacob',
      lead='Indians were the largest group of buyers in Dubai in 2025. Rent is not taxed in the UAE, a property worth AED 2 million can lead to a 10-year Golden Visa, and off-plan payments go into escrow accounts regulated by the Dubai Land Department.',
      facts=[('22%', 'of Dubai property buyers in 2025 were Indian, the largest group', 'Anarock, via Khaleej Times, 19 Jul 2026'),
             ('5.53%', 'average gross rental yield on Dubai apartments', 'Global Property Guide, May 2026'),
             ('AED 2M', 'property value for the 10-year Golden Visa', 'DLD rules, as summarised by Betterhomes'),
             ('0%', 'personal income tax in the UAE on rent', 'UAE has no personal income tax')],
      fact_src=[('Khaleej Times', 'https://www.khaleejtimes.com/business/property/dubai-property-market-deals-indians-britons-top-buyers'),
                ('Global Property Guide', 'https://globalpropertyguide.com/middle-east/united-arab-emirates/rental-yields'),
                ('Betterhomes: Golden Visa through property', 'https://www.bhomes.com/en/blog/betterinformed/everything-you-need-to-know-about-obtaining-a-dubai-real-estate-investor-visa')],
      why=[('fa-percent', 'Rent you keep', 'The UAE has no personal income tax, so rent and resale gains are not taxed there. As a resident Indian you still declare them in India, with no foreign tax to credit.'),
           ('fa-passport', 'A 10-year Golden Visa', 'Property worth AED 2 million or more, alone or combined, qualifies. Off-plan homes in DLD-approved projects count, and since early 2026 mortgaged homes qualify with a bank NOC.'),
           ('fa-vault', 'Escrow-protected off-plan', 'Payments for off-plan homes go into project escrow accounts registered with the Dubai Land Department, and every project’s construction progress is public on the DLD register.'),
           ('fa-plane', 'Close to home', 'Dubai is about three hours by air from Ahmedabad and Mumbai, with daily direct flights, so site visits and handovers are easy.'),
           ('fa-chart-line', 'Deep rental demand', 'Average gross yields on apartments were 5.53% in May 2026, from 7.80% for studios to 3.76% for 4+ bedroom homes (Global Property Guide). Net yields are usually 1.5 to 2 points lower.'),
           ('fa-calendar-check', 'Payment plans', 'Most off-plan towers are sold on staged plans (for example 20% on booking, 50% during construction, 30% on handover), so the LRS remittances can be spread over several financial years.')],
      local='Buy as a foreigner in a freehold area. You sign a sale agreement, register it with the DLD (Oqood for off-plan) and pay the 4% DLD transfer fee. The title deed is issued in your name; for off-plan, check the project’s DLD number and escrow account first.',
      rules=[('Ownership', 'Freehold for foreigners in designated areas'), ('Transfer fee', '4% of the price to the Dubai Land Department'),
             ('Visa', '10-year Golden Visa from AED 2 million; 2-year visa for completed homes with a title deed'), ('Tax in the UAE', 'No tax on rent or resale gains for individuals')],
      faq=[('Can an Indian resident buy property in Dubai?', 'Yes. Foreigners, including resident Indians, can buy freehold property in designated areas of Dubai. The money goes from India under the Liberalised Remittance Scheme, up to USD 250,000 per person per financial year.'),
           ('Does buying in Dubai give a visa?', 'Property worth AED 2 million or more can qualify for the 10-year Golden Visa. Off-plan homes in DLD-approved projects count, and mortgaged homes qualify with a bank NOC. A 2-year investor visa is available for completed homes with a title deed.'),
           ('Is rental income from Dubai taxed in India?', 'For a resident Indian, yes: rent from Dubai is part of your worldwide income and is taxed in India. The UAE does not tax it, so there is no foreign tax credit. Declare the property in Schedule FA of your return.'),
           ('How do I check an off-plan project is genuine?', 'Search its project number on the Dubai Land Department’s Project Status Enquiry. It shows the developer, the registered units, construction progress and the escrow account. Every Dubai project on our site lists its DLD number.')],
      map_center=[25.15, 55.27], map_zoom=10),
 dict(slug='singapore-property', key='sg', name='Singapore', short='Singapore', flag='🇸🇬', title='Singapore',
      seo='Singapore Property for Indian Investors – ABSD, Rules & New Launches | Galaxy Estates Properties',
      desc='Buying a Singapore condo from India: 60% ABSD for foreigners, which homes you can buy, LRS and TCS, and 2026 new launches by CDL, GuocoLand, Frasers, UOL, CapitaLand and Keppel.',
      hero_pid='newport-residences',
      lead='Singapore is the place for wealth that wants safety first: a AAA-rated city-state with a strict, transparent new-launch market. It is not cheap to enter as a foreigner, so it suits buyers who value stability over yield.',
      facts=[('AAA', 'credit rating from all three major agencies', 'S&P, Moody’s and Fitch'),
             ('60%', 'Additional Buyer’s Stamp Duty for foreigners, unchanged since 27 Apr 2023', 'IRAS rates, summarised by SmartCalculator'),
             ('246', 'freehold homes at Newport Residences, expected TOP 2030', '99.co new launch list'),
             ('99 / ∞', 'most new launches are 99-year leasehold; some are freehold', 'URA-licensed developer sales')],
      fact_src=[('SmartCalculator: ABSD rates 2026', 'https://www.smartcalculator.sg/articles/absd-rates-singapore-2026'),
                ('99.co: new condo launches 2026', 'https://www.99.co/singapore/insider/new-condo-launches-2026/')],
      why=[('fa-shield-halved', 'Stability first', 'A AAA-rated government, rule of law and a currency that has held its value against the rupee for decades make Singapore a wealth-preservation market.'),
           ('fa-building-columns', 'Tightly regulated launches', 'New launches are sold by developers licensed under the Housing Developers Act, with standard sale agreements and progress payments tied to construction stages.'),
           ('fa-briefcase', 'Expatriate rental demand', 'Central condos near the business district and Orchard rent to the professionals who work for regional headquarters in the city.'),
           ('fa-graduation-cap', 'Family base in Asia', 'Many Indian families use a Singapore home as a base for children studying there or for business across Southeast Asia.')],
      local='Foreigners can buy condominium units freely; landed homes need government approval. The 60% ABSD applies to Indian citizens (only US, Swiss, Norwegian, Icelandic and Liechtenstein citizens are treated as Singaporeans for ABSD). New launches are paid in stages as the building rises.',
      rules=[('Ownership', 'Condos open to foreigners; landed homes need approval'), ('ABSD', '60% for foreigners on any residential purchase'),
             ('Tenure', '99-year leasehold or freehold, project by project'), ('Payments', 'Progress payments as construction advances')],
      faq=[('Can Indians buy property in Singapore?', 'Yes, condominium units can be bought by foreigners without approval. Landed homes need approval from the Singapore Land Authority.'),
           ('Do Indian citizens pay ABSD in Singapore?', 'Yes. Foreigners pay 60% Additional Buyer’s Stamp Duty on residential property. Indian citizens are not among the five nationalities (US, Switzerland, Norway, Iceland, Liechtenstein) that are treated as Singaporeans under free-trade agreements.'),
           ('Is a Singapore condo a good rental investment?', 'Singapore is bought mainly for stability and capital preservation. With 60% ABSD the entry cost is high, so rental yield on the total cost is modest; we show you the numbers for each unit before you decide.')],
      map_center=[1.30, 103.83], map_zoom=12),
 dict(slug='thailand-property', key='th', name='Thailand', short='Thailand', flag='🇹🇭', title='Thailand: Phuket & Pattaya',
      seo='Thailand Property for Indian Investors – Phuket & Pattaya Condos, Rules | Galaxy Estates Properties',
      desc='Phuket and Pattaya condos for Indian buyers: freehold within the 49% foreign quota, how to send money (FET), costs, 30-day visa-free travel, and projects by Sansiri and Banyan Group.',
      hero_pid='skypark-elara-lakelands',
      lead='Thailand offers sea-view condos and resort residences at a fraction of global prices, a short flight from India. Foreigners can own a condo freehold within each building’s 49% foreign quota, and Indian tourists can visit visa-free for 30 days.',
      facts=[('49%', 'of a condo building’s floor area can be foreign-owned freehold', 'Condominium Act, section 19'),
             ('30 days', 'visa-free stay for Indian tourists from 15 Sep 2026', 'All India Radio News, 9 Sep 2026'),
             ('2%', 'transfer fee on appraised value, often split with the developer', 'The Thaiger legal guide'),
             ('3 hours', 'Sansiri sold the foreign quota of PTY Residence Sai 1, Pattaya, in 3 hours', 'Sansiri release, 17 Mar 2025')],
      fact_src=[('The Thaiger: buying property in Thailand', 'https://thethaiger.com/legal/property/buying/'),
                ('All India Radio News: 30-day visa-free entry', 'https://newsonair.gov.in/thailand-allows-visa-free-entry-and-stay-up-to-30-days-for-indian-tourists/'),
                ('Royal Thai Embassy, New Delhi', 'https://newdelhi.thaiembassy.org/en/content/latest-update-on-revision-to-thailand-s-visa-exemp'),
                ('Sansiri PTY Residence Sai 1 release', 'https://www.malaymail.com/news/money/mediaoutreach/2025/03/17/sansiris-pty-residence-sai-1-sells-out-foreign-quota-in-3-hrs-global-online-booking-hit-record-sales-in-pattaya/368027')],
      why=[('fa-umbrella-beach', 'Holiday-rental demand', 'Phuket and Pattaya draw tourists all year, so resort-managed condos and pool villas can earn holiday-rental income when you are not using them.'),
           ('fa-tags', 'Low entry prices', 'Sea-view condos start well below Dubai or Singapore prices: Sansiri’s PTY Residence Sai 1 on Pattaya beach started at THB 6.99 million for a one-bedroom.'),
           ('fa-plane-arrival', 'Easy to visit', 'Indian tourists can stay 30 days visa-free (from 15 Sep 2026), and Phuket has an international airport with direct flights from India.'),
           ('fa-house-chimney', 'Freehold condos', 'Condos are owned freehold within the 49% foreign quota. Villas are usually bought as the building plus a registered 30-year land lease.')],
      local='Buy a condo within the building’s foreign quota (ask for written confirmation first). The money must come from abroad in foreign currency in your name; transfers of USD 50,000 or more get a Foreign Exchange Transaction form, which you keep to send sale proceeds home later. Register the transfer at the Land Office.',
      rules=[('Ownership', 'Freehold condos within the 49% foreign quota; land by lease of up to 30 years'), ('Money in', 'Foreign currency from abroad; FET form for USD 50,000+'),
             ('Transfer fee', '2% of appraised value, split by negotiation'), ('Annual tax', '0.02% of appraised value for a second home')],
      faq=[('Can Indians buy property in Thailand?', 'Yes, condominium units, freehold, as long as the building’s foreign quota (49% of the saleable area) is not full. Land cannot be owned by foreigners; villas are bought through a registered lease of up to 30 years.'),
           ('How do I send money for a Thai condo from India?', 'Under LRS, in foreign currency, from your own account to your own name, stating the purpose as condominium purchase. The Thai bank issues a Foreign Exchange Transaction form for USD 50,000 or more; keep it to repatriate sale proceeds.'),
           ('Do Indians need a visa to visit Thailand?', 'From 15 Sep 2026 Indian tourists can stay up to 30 days visa-free. For longer stays, apply for the right e-visa at thaievisa.go.th.')],
      map_center=[10.4, 99.6], map_zoom=6),
 dict(slug='malaysia-property', key='my', name='Malaysia', short='Malaysia', flag='🇲🇾', title='Kuala Lumpur, Malaysia',
      seo='Malaysia Property for Indian Investors – Kuala Lumpur Rules & New Projects | Galaxy Estates Properties',
      desc='Buying in Kuala Lumpur from India: RM1 million minimum for foreigners, freehold titles, visa-free travel to 31 Dec 2026, and projects by Lendlease, Pavilion, Mah Sing and Sunway.',
      hero_pid='trx-residences',
      lead='Kuala Lumpur offers luxury condos near the Petronas Towers and the TRX financial district at a fraction of Singapore prices, with freehold titles open to foreigners above a minimum price.',
      facts=[('RM1M', 'minimum price for foreign buyers in Kuala Lumpur, condos and landed', 'Far Capital, 24 Aug 2026'),
             ('30 days', 'visa-free stay for Indian citizens, extended to 31 Dec 2026', 'Malaysia Home Ministry, via Human Resources Online'),
             ('Freehold', 'titles are available to foreign buyers', 'National Land Code; state approval needed'),
             ('Early 2029', 'completion target of Pavilion Damansara Heights’ final towers', 'SuperHomes, Oct 2026')],
      fact_src=[('Far Capital: price thresholds for foreigners', 'https://farcapital.com.my/?p=40875'),
                ('Human Resources Online: visa exemption to 31 Dec 2026', 'https://humanresourcesonline.net/malaysia-extends-visa-exemption-for-india-citizens-to-31-december-2026'),
                ('SuperHomes: new launches 2026', 'https://www.superhomes.my/resources/new-property-launches-malaysia-2026')],
      why=[('fa-scale-balanced', 'Value next to Singapore', 'Luxury condos in KLCC and the TRX district cost a fraction of similar homes in Singapore, without a 60% foreign buyer’s stamp duty.'),
           ('fa-file-contract', 'Freehold and common law', 'Many projects are freehold, the legal system is based on English common law and English is widely used in business.'),
           ('fa-plane', 'Visa-free visits', 'Indian citizens can visit for up to 30 days without a visa until 31 Dec 2026, and the MM2H programme offers long-stay options.'),
           ('fa-city', 'A growing financial district', 'TRX (Tun Razak Exchange) brings offices, a large mall and an MRT interchange next to the homes built there.')],
      local='Foreigners buy above each state’s minimum price (RM1 million in Kuala Lumpur) and need state consent for the transfer, which your lawyer applies for. Low-cost and bumiputera-reserved units are not open to foreigners.',
      rules=[('Minimum price', 'RM1,000,000 in Kuala Lumpur; RM2,000,000 in most of Selangor'), ('Ownership', 'Freehold or leasehold, with state consent'),
             ('Visa', '30 days visa-free for Indians to 31 Dec 2026; MM2H for long stays'), ('Not open to foreigners', 'Low-cost and bumiputera-reserved units')],
      faq=[('Can Indians buy property in Malaysia?', 'Yes, above the minimum price set by each state (RM1 million in Kuala Lumpur), with state consent for the transfer. Freehold titles are available.'),
           ('Do Indians need a visa for Malaysia?', 'Indian citizens can stay up to 30 days without a visa under an exemption extended to 31 Dec 2026. For long stays, the MM2H programme has its own deposit and property rules; we confirm the current tiers before you apply.'),
           ('Is the RM1 million limit the same across Malaysia?', 'No. Each state sets its own. Most of Selangor is RM2 million; Penang mainland and some states allow certain condos from RM500,000.')],
      map_center=[3.15, 101.71], map_zoom=12),
 dict(slug='monaco-property', key='mc', name='Monaco', short='Monaco', flag='🇲🇨', title='Monaco',
      seo='Monaco Property for Indian Investors – Residency, Tax & New Builds | Galaxy Estates Properties',
      desc='Monaco for Indian wealth: no personal income tax for residents (except French nationals), residence through a home and financial means, Mareterra and the private new builds due by 2027.',
      hero_pid='mareterra',
      lead='Monaco is one of the smallest and most valuable property markets in the world. Residents pay no personal income tax (French nationals excepted), and very little new supply comes to market, which is why it is bought for wealth preservation and residence.',
      facts=[('0%', 'personal income tax for residents, except French nationals', 'KPMG Monaco relocation guide'),
             ('6 ha', 'Mareterra, the new seafront district inaugurated on 3 Dec 2024', 'Real Asset Insight, 4 Dec 2024'),
             ('50', 'apartments of 400 sq m or more in Le Renzo, Mareterra’s main building', 'Real Asset Insight'),
             ('4.5%', 'registration duty on a direct transfer; 7.5% through a non-transparent company', 'KPMG Monaco relocation guide')],
      fact_src=[('KPMG: Relocation to Monaco', 'https://assets.kpmg.com/content/dam/kpmg/mc/images/mfo/pdf/KPMG-MFO_Relocation_to_the_Principality_of_Monaco.pdf'),
                ('Real Asset Insight: Mareterra launched', 'https://realassetinsight.com/2024/12/04/e2bn-mareterra-waterfront-project-launched-in-monaco/'),
                ('Petrini: Monaco developments to 2030', 'https://www.petrini.mc/en/real-estate-developments-monaco-2030.html')],
      why=[('fa-gem', 'Scarcity', 'Two square kilometres of land and very few new buildings keep Monaco among the most expensive and resilient property markets.'),
           ('fa-hand-holding-dollar', 'No personal income tax', 'Monaco residents, except French nationals, pay no personal income tax and no tax on capital gains or dividends there.'),
           ('fa-id-card', 'A route to residence', 'A home in Monaco, owned or rented, plus proof of financial means and a reference from a Monegasque bank are the core conditions for a residence card.'),
           ('fa-anchor', 'A new seafront district', 'Mareterra added six hectares on the sea at Larvotto, with buildings by Renzo Piano, Norman Foster, Stefano Boeri and Tadao Ando.')],
      local='There is no restriction on foreign buyers. Non-EU nationals, including Indians, first obtain a long-stay (type D) visa from the French consulate, then apply for a Monaco residence card with proof of housing and means. Most purchases are resales because new supply is so small.',
      rules=[('Ownership', 'No restriction on foreign buyers'), ('Duty', '4.5% registration duty on a direct transfer; 7.5% via a non-transparent company'),
             ('Residence', 'Type D visa from France, then a Monaco residence card'), ('Tax', 'No personal income tax for residents, except French nationals')],
      faq=[('Can Indians buy property in Monaco?', 'Yes, there is no restriction on foreign buyers. Supply is very small, so most homes are resales; we work with Monaco agents to source them.'),
           ('Does buying in Monaco give residency?', 'A home in Monaco is one of the conditions for a residence card, alongside proof of financial means and a Monegasque bank reference. Indians first need a type D visa from the French consulate.'),
           ('Does a Monaco resident Indian still pay tax in India?', 'That depends on your residential status under Indian law. If you remain a resident of India, your worldwide income is taxed in India. Speak to your CA before you move.')],
      map_center=[43.738, 7.424], map_zoom=15),
]

# ---------------------------------------------------------------- developers and their ongoing projects
def dld_rows(key, limit=None):
    rows = sorted(DLD_DEV.get(key, []), key=lambda r: -float(r['pct'].rstrip('%') or 0))
    return [(r['name'], f"DLD #{r['no']}", f"{r['pct']} built") for r in rows[:limit]]

DEVS = {
 'uae': [
  dict(name='Emaar Properties', usp='Developer of Burj Khalifa and The Dubai Mall; master developer of Downtown Dubai, Dubai Creek Harbour, The Valley and The Oasis.', listed=['emaar-valo', 'emaar-fior-1', 'emaar-greenway', 'emaar-palmiera2'],
       rows=dld_rows('Emaar'), src='Dubai Land Department Project Status Enquiry (name search “Emaar”), 17 Oct 2026', note='Not a complete list. Emaar also builds through subsidiaries such as Dubai Creek Harbour LLC and Mina Rashid Properties, so the register search does not catch every Emaar project (Valo and Fior 1 are two).'),
  dict(name='Binghatti Developers', usp='Known for sculpted façades and branded towers with Bugatti, Mercedes-Benz and Jacob & Co.; builds Burj Binghatti, planned as the world’s tallest residential tower.', listed=['binghatti-burj-jacob', 'binghatti-mercedes-city', 'binghatti-tilal'],
       rows=dld_rows('Binghatti'), src='Dubai Land Department Project Status Enquiry (name search “Binghatti”), 17 Oct 2026'),
  dict(name='Danube Properties', usp='Founded by Indian-born Rizwan Sajan; known for its 1% monthly payment plans and amenity-heavy towers.', listed=['danube-bayz-101', 'danube-diamondz', 'danube-shahrukhz'],
       rows=dld_rows('Danube'), src='Dubai Land Department Project Status Enquiry (name search “Danube”), 17 Oct 2026'),
  dict(name='Sobha Realty', usp='Founded by Indian-born P.N.C. Menon; builds with its own in-house design, engineering and fit-out teams, from Sobha Hartland to Sobha Central.', listed=[],
       rows=dld_rows('Sobha'), src='Dubai Land Department Project Status Enquiry (name search “Sobha”), 17 Oct 2026'),
  dict(name='DAMAC Properties', usp='One of Dubai’s largest private developers, building large villa and lagoon communities: DAMAC Hills, DAMAC Lagoons, DAMAC Islands and Riverside.', listed=[],
       rows=dld_rows('Damac'), src='Dubai Land Department Project Status Enquiry (name search “Damac”), 17 Oct 2026'),
  dict(name='Nakheel', usp='Master developer of Palm Jumeirah; now building Dubai Islands.', listed=[],
       rows=dld_rows('Nakheel'), src='Dubai Land Department Project Status Enquiry (name search “Nakheel”), 17 Oct 2026',
       note='Only projects with “Nakheel” in the registered name appear here; the full Nakheel pipeline (including Palm Jebel Ali) is larger.'),
 ],
 'sg': [
  dict(name='City Developments (CDL)', usp='One of Singapore’s largest listed developers, with homes, hotels and offices across the island.', listed=['newport-residences'],
       rows=[('Newport Residences', 'Anson Road, District 2 · 246 units · freehold', 'Expected TOP 2030'), ('Lucerne Grand', 'Lakeside Drive · 575 units · 99-year', 'Launch 2026'),
             ('Woodlands Drive 17 (EC)', '420 units · 99-year (executive condo, not for foreigners)', 'Launch Q4 2026'), ('Senja Close (EC)', '295 units · 99-year (executive condo, not for foreigners)', 'Launch Q4 2026')],
       src='99.co, Full list of new condo launches in 2026'),
  dict(name='GuocoLand', usp='Builder of integrated city-centre developments such as Guoco Tower and Midtown Bay.', listed=[],
       rows=[('River Modern', 'River Valley Green, District 9 · 455 units · 99-year', 'Expected TOP 2030'), ('Tengah Garden Residences', 'With Hong Leong and CSC Land · 860 units · 99-year', 'Launched Apr 2026')],
       src='99.co, Full list of new condo launches in 2026'),
  dict(name='Frasers Property', usp='Singapore-listed developer with homes, malls and industrial assets across Asia, Australia and Europe.', listed=['dunearn-house'],
       rows=[('Dunearn House', 'Dunearn Road (prime district) · 360 units · 99-year, with CSC Land', 'Launch 2026')], src='99.co, Full list of new condo launches in 2026'),
  dict(name='UOL Group, CapitaLand and Singapore Land Group', usp='Three of Singapore’s largest developers, often bidding together for government land sites.', listed=[],
       rows=[('Thomson Reserve', 'Bright Hill Drive · 1,240 units · 99-year', 'Launch Sep 2026'), ('Dorset Road site', 'UOL, Singapore Land Group and Kheng Leong · 428 units · 99-year', 'Launch Q4 2026')],
       src='99.co, Full list of new condo launches in 2026'),
  dict(name='Keppel', usp='Developer of Keppel Bay and Reflections at Keppel Bay on the southern waterfront.', listed=[],
       rows=[('Keppel Bay Plot 6', 'Keppel Island · 86 units · 99-year', 'Launch date to be announced')], src='99.co, Full list of new condo launches in 2026'),
 ],
 'th': [
  dict(name='Sansiri', usp='One of Thailand’s largest listed developers, active in Bangkok, Pattaya, Phuket, Hua Hin and Chiang Mai.', listed=['dcondo-vite'],
       rows=[('PTY Residence Sai 1', 'Pattaya Beach Road · 327 freehold units · THB 3.2 billion', 'Foreign quota sold in 3 hours (Mar 2025)'),
             ('THE BASE Cherngtalay', 'Cherngtalay, Phuket · pet-friendly condo · THB 1.3 billion', '90% sold (Dec 2025)'),
             ('New Surin Beach condominium', 'Surin Beach, Phuket', 'Launching 2026'), ('New Cherngtalay Soi 3 project', 'Cherngtalay – Bang Tao, Phuket', 'Launching 2026')],
       src='Sansiri release (17 Mar 2025) and The Thaiger (29 Dec 2025)'),
  dict(name='Banyan Group', usp='The group behind Banyan Tree and the Laguna Phuket integrated resort, selling branded and resort-managed homes.', listed=['skypark-elara-lakelands'],
       rows=[('Skypark Elara Lakelands', 'Laguna Lakelands, Phuket · three 7-storey blocks, about 220 units in phase 1 · from THB 8 million', 'Selling'),
             ('Laguna Lakeside Residences', 'Laguna Phuket, near Boat Avenue · 1–3 bedrooms with rooftop pools · from THB 9 million', 'Later blocks selling; first block completed Jun 2024'),
             ('Skypark Lucean Jomtien', 'Jomtien, Pattaya', 'Selling (2026)')],
       src='Banyan Group news (17 Oct 2024) and Lazudi Pattaya 2026 guide'),
 ],
 'my': [
  dict(name='Lendlease and TRX City', usp='Lendlease built the residential towers at Tun Razak Exchange, Kuala Lumpur’s new financial district, with TRX City.', listed=['trx-residences'],
       rows=[('TRX Residences', 'Tun Razak Exchange, above the TRX mall and MRT interchange', 'See the project page')], src='Lendlease and TRX City'),
  dict(name='Pavilion Group', usp='Developer of Pavilion KL and Pavilion Damansara Heights.', listed=[],
       rows=[('Pavilion Damansara Heights, phase 2', 'Damansara Heights · Imperial Residences RM5.07 – 10.2 million', 'Towers due early 2029')], src='SuperHomes, new property launches 2026 (checked 1 Oct 2026)'),
  dict(name='Mah Sing', usp='One of Malaysia’s largest listed residential developers.', listed=[],
       rows=[('M Aurora', 'Old Klang Road · Tower A (747 units) still to launch', 'Launched 4 Mar 2026')], src='SuperHomes, new property launches 2026'),
  dict(name='Sunway Property', usp='Builder of integrated townships such as Sunway City and Sunway Velocity.', listed=[],
       rows=[('Sunway Velocity 3 (Tower C)', 'Cheras', 'In the 2026 launch pipeline')], src='SuperHomes, new property launches 2026'),
 ],
 'mc': [
  dict(name='SAM L’Anse du Portier', usp='The company that reclaimed and built Mareterra, Monaco’s six-hectare seafront extension.', listed=['mareterra'],
       rows=[('Le Renzo, Mareterra', '50 apartments of 400 sq m or more, by Renzo Piano', 'Inaugurated 3 Dec 2024'),
             ('Mareterra villas and townhouses', '10 seafront villas and 4 hillside townhouses by Foster, Boeri and Ando', 'Inaugurated 3 Dec 2024')],
       src='Real Asset Insight, 4 Dec 2024'),
  dict(name='Private new builds in Monaco', usp='The few private buildings under way, as listed by Monaco agency Petrini.', listed=[],
       rows=[('Villa Ninetta', '3 Rue Malbousquet · 27 luxury apartments', 'Delivery scheduled 2026'), ('Villa Lucia', '35 Pont Sainte-Dévote · one apartment per floor on the first nine levels', 'Delivery scheduled 2026'),
             ('Tour CMB Red', '23 Avenue de la Costa · 25 apartments', 'Around 2026–2027'), ('Villa du Pont (Groupe Marzocco)', 'Sainte-Dévote · to be rebuilt', 'Works expected from 2026')],
       src='Petrini, Real estate developments in Monaco to 2030', note='State-owned housing such as Bel Air and Upper Larvotto is reserved for Monegasque nationals and is not listed.'),
 ],
}

PINS = {  # Google Maps pins; "approx" marks a community-level pin
  'binghatti-burj-jacob': (25.186862, 55.2929523, ''), 'danube-bayz-101': (25.1924811, 55.2630161, ''), 'danube-diamondz': (25.063857, 55.14095, ''),
  'danube-shahrukhz': (25.1084375, 55.1791875, ''), 'emaar-fior-1': (25.2597639, 55.2793893, ''), 'binghatti-mercedes-city': (25.1633125, 55.3256875, ''),
  'emaar-greenway': (24.8497428, 55.1591238, ''), 'emaar-palmiera2': (25.0083703, 55.2135338, 'approx: The Oasis community'), 'emaar-valo': (25.201923, 55.3422432, 'approx: Dubai Creek Harbour'),
  'binghatti-tilal': (25.1226089, 55.4387125, ''), 'newport-residences': (1.272964, 103.8436292, ''), 'dunearn-house': (1.3198209, 103.8205197, 'approx: sales gallery'),
  'dcondo-vite': (12.9560833, 100.8971943, ''), 'skypark-elara-lakelands': (8.0244388, 98.3137402, 'approx: Laguna Lakelands'), 'trx-residences': (3.1436347, 101.719198, ''),
  'mareterra': (43.74338, 7.4306993, 'approx: Le Portier'),
}
CODE = {'United Arab Emirates': 'uae', 'Singapore': 'sg', 'Thailand': 'th', 'Malaysia': 'my', 'Monaco': 'mc'}

def page_for(country):
    k = CODE.get(country)
    return next((c['slug'] + '.html' for c in COUNTRIES if c['key'] == k), None)

def build_body(c, ALL, card):
    ps = [p for p in ALL if CODE.get(p['country']) == c['key']]
    hero = next((p for p in ps if p['id'] == c['hero_pid']), ps[0])
    facts = ''.join(f'<div class="fact"><strong>{E(v)}</strong><span>{E(t)}</span><small>{E(s)}</small></div>' for v, t, s in c['facts'])
    fsrc = ' · '.join(f'<a href="{E(u)}" target="_blank" rel="noopener noreferrer">{E(n)}</a>' for n, u in c['fact_src'])
    why = ''.join(f'<div class="expertise-item reveal" style="--d:{i * .06:.2f}s"><div class="icon-ring"><i class="fas {ic}"></i></div><h3>{E(h)}</h3><p>{E(t)}</p></div>' for i, (ic, h, t) in enumerate(c['why']))
    steps = []
    for i, (ic, h, t, src) in enumerate(INDIA_STEPS):
        txt = c['local'] if t is None else t
        s = f' <a class="step-src" href="{E(src[1])}" target="_blank" rel="noopener noreferrer">{E(src[0])}</a>' if src else ''
        steps.append(f'<li class="buy-step reveal" style="--d:{i * .06:.2f}s"><span class="buy-n">{i + 1}</span><div><h3><i class="fas {ic}" aria-hidden="true"></i> {E(h)}</h3><p>{E(txt)}{s}</p></div></li>')
    rules = ''.join(f'<div><dt>{E(a)}</dt><dd>{E(b)}</dd></div>' for a, b in c['rules'])
    pins = [dict(id=p['id'], name=p['name'], dev=p['developer'], price=p['price'], page=p['page'], lat=PINS[p['id']][0], lon=PINS[p['id']][1], approx=PINS[p['id']][2])
            for p in ps if p['id'] in PINS]
    devs = []
    for d in DEVS.get(c['key'], []):
        listed = [p for p in ps if p['id'] in d['listed']]
        lk = (' <span class="dev-ours">On our site: ' + ', '.join(f'<a href="{p["page"]}">{E(p["name"])}</a>' for p in listed) + '</span>') if listed else ''
        rows = ''.join(f'<tr><th scope="row">{E(a)}</th><td>{E(b)}</td><td>{E(s)}</td></tr>' for a, b, s in d['rows'])
        n = len(d['rows'])
        table = f'<div class="mix-wrap"><table class="mix-table dev-table"><thead><tr><th scope="col">Project</th><th scope="col">Details</th><th scope="col">Status</th></tr></thead><tbody>{rows}</tbody></table></div>'
        body = (f'<details class="dev-more"{" open" if n <= 6 else ""}><summary>Show all {n} projects on the register <i class="fas fa-plus" aria-hidden="true"></i></summary>{table}</details>' if n > 6 else table)
        note = f'<p class="detail-source">{E(d["note"])}</p>' if d.get('note') else ''
        devs.append(f'<article class="dev-card reveal"><header><h3>{E(d["name"])}</h3><p>{E(d["usp"])}{lk}</p></header>{body}{note}<p class="detail-source">Source: {E(d["src"])}.</p></article>')
    faq = ''.join(f"""<div class="faq-item reveal"><button type="button" class="faq-q" aria-expanded="false" aria-controls="cfaq-a{i}" id="cfaq-q{i}"><span>{E(q)}</span><i class="fas fa-plus" aria-hidden="true"></i></button><div class="faq-a" id="cfaq-a{i}" role="region" aria-labelledby="cfaq-q{i}"><div><p>{E(a)}</p></div></div></div>""" for i, (q, a) in enumerate(c['faq']))
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in c['faq']]}
    other = ' '.join(f'<a class="cta-btn ghost small" href="{o["slug"]}.html">{E(o["flag"])} {E(o["short"])}</a>' for o in COUNTRIES if o['key'] != c['key'])
    return f"""<section class="page-hero country-hero">
  <div class="page-hero-bg" style="background-image:url('{hero['img']}')"></div>
  <div class="page-hero-overlay"></div>
  <div class="container page-hero-content">
    <div class="breadcrumb hs"><a href="index.html">Home</a><i class="fas fa-chevron-right"></i><a href="global.html">Global</a><i class="fas fa-chevron-right"></i><span>{E(c['title'])}</span></div>
    <span class="section-tag hs">Property guide for Indian investors</span>
    <h1>{E(c['title'])}</h1>
    <p class="hs">{E(c['lead'])}</p>
    <div class="btn-row hs">
      <button type="button" class="cta-btn primary" data-enquire="Global property — {E(c['short'])}" data-interest="Global property"><i class="fas fa-paper-plane"></i> Get a {E(c['short'])} shortlist</button>
      <a href="#projects-here" class="cta-btn secondary"><i class="fas fa-arrow-down"></i> See projects</a>
    </div>
  </div>
</section>

<section class="section" id="why">
  <div class="container">
    <div class="section-header seq"><span class="section-tag">At a glance</span><h2>{E(c['short'])} in four numbers</h2></div>
    <div class="facts-band reveal stagger">{facts}</div>
    <p class="explorer-note">Sources: {fsrc}. Checked {CHECKED}; rules change, and we confirm them before you commit.</p>
  </div>
</section>

<section class="section bg-alt">
  <div class="container">
    <div class="section-header seq"><span class="section-tag">For Indian investors</span><h2>Why buy in {E(c['short'])}</h2></div>
    <div class="expertise-grid{' why-6' if len(c['why']) == 6 else ''}">{why}</div>
  </div>
</section>

<section class="section" id="how-to-buy">
  <div class="container">
    <div class="section-header seq"><span class="section-tag">From India, step by step</span><h2>How to buy in {E(c['short'])}</h2>
      <p>The Indian rules are the same for every country; the local step is specific to {E(c['short'])}.</p></div>
    <div class="buy-layout">
      <ol class="buy-steps">{''.join(steps)}</ol>
      <aside class="panel buy-rules reveal"><h3>{E(c['short'])} rules in brief</h3><dl class="rule-list">{rules}</dl>
        <p class="detail-source">General information, not legal or tax advice. We confirm every rule with a local lawyer and your CA before you pay.</p></aside>
    </div>
  </div>
</section>

<section class="section bg-alt" id="projects-here">
  <div class="container">
    <div class="section-header seq"><span class="section-tag">On our site</span><h2>Projects we offer in {E(c['short'])}</h2>
      <p>Tap a pin for the project, or open any card for prices, sizes and the official registration record.</p></div>
    <div class="country-map reveal" id="country-map" data-center="{c['map_center'][0]},{c['map_center'][1]}" data-zoom="{c['map_zoom']}" aria-label="Map of our projects in {E(c['short'])}"></div>
    <script type="application/json" id="country-pins">{json.dumps(pins, ensure_ascii=False)}</script>
    <p class="explorer-note">Pins from Google Maps; “approx.” marks a community-level pin. Map © OpenStreetMap contributors.</p>
    <div class="projects-grid">{''.join(card(p, (i % 3) * .08) for i, p in enumerate(ps))}</div>
  </div>
</section>

<section class="section" id="developers">
  <div class="container">
    <div class="section-header seq"><span class="section-tag">Who builds here</span><h2>Developers and their ongoing projects</h2>
      <p>{'For Dubai, every project below is from the Dubai Land Department’s official register, with its construction progress.' if c['key'] == 'uae' else 'From the developers and published launch lists; we confirm each one before you book.'}</p></div>
    <div class="dev-list">{''.join(devs)}</div>
  </div>
</section>

<section class="section bg-alt">
  <div class="container">
    <div class="section-header seq"><span class="section-tag">Questions</span><h2>Buying in {E(c['short'])}: common questions</h2></div>
    <div class="faq">{faq}</div>
    <div class="btn-row center" style="margin-top:28px">{other}</div>
  </div>
</section>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>"""
