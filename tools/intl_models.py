"""Dubai towers drawn to their published form (27 Oct 2026): Burj Binghatti Jacob & Co Residences, Valo (Emaar) and Shahrukhz by Danube.
Floor counts and heights are the published ones; the plan shapes, setbacks and crowns are read from the developers' renders, because
floor plates are not published. Each config from t3d_auto is reshaped here (tiers = footprint by floor, crown = what stands on the roof)."""
import math

def stadium(w, d):                  # rounded-end plan (as on the renders)
    return dict(w=w, d=d, shape='round', r=min(w, d) / 2, pts=None)

def octagon(w, d, c):
    x, y = w / 2, d / 2
    return [[-x + c, -y], [x - c, -y], [x, -y + c], [x, y - c], [x - c, y], [-x + c, y], [-x, y - c], [-x, -y + c]]

# ---------------------------------------------------------------- Burj Binghatti Jacob & Co Residences
# Sources: Jacob & Co. (jacobandco.com/real-estate/binghatti, Oct 2026): quarter-floor villas (Emerald, Sapphire, Ruby), Diamond and Fleurs de Jardin
# Sky Mansions, Astronomia Sky Penthouses, amenities "near the summit, just below the Sky Penthouses"; the developer's project factsheet
# (as circulated to agents): 6 basements + ground + 5 podium levels + 98 floors + roof, 4.2 m floor to floor, floor plate 18,700 sq ft,
# 1 to 4 homes a floor, the sky mansions on levels 83–96 (half floors), the Billionaire penthouse on the top two floors, unit sizes;
# Dubai Land Department project #2480: 325 homes (144 two-bed, 150 three-bed, 16 four-bed, 14 six-bed, 1 other); Wikipedia: 557 m.
# what each side of the tower looks out on: landmarks by their bearing from the tower (degrees anticlockwise from east, from map coordinates)
BJ_MARKS = [(148.6, 'Burj Khalifa'), (139.0, 'Downtown Dubai'), (180.0, 'the Business Bay canal'), (97.0, 'Za’abeel'), (49.0, 'Dubai Creek and Al Jaddaf'),
            (14.9, 'Dubai Creek Harbour'), (1.0, 'Dubai Design District'), (-11.5, 'Ras Al Khor Wildlife Sanctuary'), (-76.6, 'Meydan'), (-100.0, 'Al Khail Road')]
COMPASS8 = ['east', 'north-east', 'north', 'north-west', 'west', 'south-west', 'south', 'south-east']
def _bearing(local_deg, rot): return (local_deg + rot) % 360
def _compass(a, n=4):
    return (['east', 'north', 'west', 'south'][int(((a + 45) % 360) // 90)] if n == 4 else COMPASS8[int(((a + 22.5) % 360) // 45)])
def _outlook(a, span=55):
    d = lambda b: abs((b - a + 180) % 360 - 180)
    near = sorted([m for m in BJ_MARKS if d(m[0]) <= span], key=lambda m: d(m[0]))
    names = [n for _, n in near[:3]] or [min(BJ_MARKS, key=lambda m: d(m[0]))[1]]
    return ' and '.join([', '.join(names[:-1]), names[-1]] if len(names) > 1 else names)

def burj_jacob(cfg):
    t = cfg['towers'][0]
    # turn the plan to the building outline mapped on OpenStreetMap at the site (its sides run at -31.8 and 58.2 degrees from east)
    t['ang'] = round(-31.8 - (cfg['geo'].get('rot') or 0), 1)
    rot = -31.8
    A, C, K = 21.5, 6.0, 7.5            # half width of the 43 m square plan (18,700 sq ft floor plate), cut corners, half width of the core
    plan = [[-A + C, -A], [A - C, -A], [A, -A + C], [A, A - C], [A - C, A], [-A + C, A], [-A, A - C], [-A, -A + C]]
    # quarter floors: one L-shaped home round each corner of the core; half floors: two homes; full floors: one
    q = {'NE': [[0, K], [0, A], [A - C, A], [A, A - C], [A, 0], [K, 0], [K, K]],
         'NW': [[0, K], [-K, K], [-K, 0], [-A, 0], [-A, A - C], [-A + C, A], [0, A]],
         'SW': [[0, -K], [-K, -K], [-K, 0], [-A, 0], [-A, -A + C], [-A + C, -A], [0, -A]],
         'SE': [[0, -K], [0, -A], [A - C, -A], [A, -A + C], [A, 0], [K, 0], [K, -K]]}
    qdeg = {'NE': 45, 'NW': 135, 'SW': 225, 'SE': 315}
    halves = {'W': [[0, A], [-A + C, A], [-A, A - C], [-A, -A + C], [-A + C, -A], [0, -A], [0, -K], [-K, -K], [-K, K], [0, K]],
              'E': [[0, A], [0, K], [K, K], [K, -K], [0, -K], [0, -A], [A - C, -A], [A, -A + C], [A, A - C], [A - C, A]]}
    hdeg = {'W': 180, 'E': 0}
    # Developer's brochure (Burj Binghatti Jacob & Co Residences, 68 pages): the vertical diagram gives every floor (GF, podium 1-5, pool, service,
    # sky garden, 83 residential floors R-01 to R-83, 6 mechanical floors, sky lounge, spa, gym, penthouses; 560 m total height) and the unit pages
    # give levels, bedrooms, areas, parking and prices. The unit pages count levels one higher than the diagram's floor numbers
    # (Billionaire: diagram floors 101-102 = levels 102 & 103); levels here follow the unit pages, so they match the price sheet.
    U = {'E': dict(n='Emerald Villa', bed='2 bedrooms, 3 bathrooms', area='1,738 sq ft suite + 1,599 sq ft terrace & pool = 3,337 sq ft', park=2, price='AED 8,200,000 to 11,920,000 (average 9,964,000)'),
         'S': dict(n='Sapphire Villa', bed='2.5 bedrooms (with study and storage room), 3 bathrooms', area='1,732 sq ft suite + 1,602 sq ft terrace & pool = 3,335 sq ft', park=2, price='AED 8,400,000 to 10,980,000 (average 9,679,000)'),
         'R': dict(n='Ruby Villa', bed='3 bedrooms, 4 bathrooms', area='2,090 sq ft suite + 1,209 sq ft terrace & pool = 3,299 sq ft', park=2, price='AED 13,999,999 to 17,239,999 (average 15,494,999)'),
         'D': dict(n='Diamond Sky Mansion', bed='4 bedrooms, 7 bathrooms', area='5,176 sq ft suite + 1,800 sq ft terrace & pool = 6,976 sq ft', park=4, price='On request'),
         'F': dict(n='Fleurs de Jardin Sky Mansion', bed='6 bedrooms, 9 bathrooms', area='5,176 sq ft suite + 1,800 sq ft terrace & pool = 6,976 sq ft', park=4, price='AED 31,000,000 to 36,100,000 (average 33,716,667)'),
         'A': dict(n='Astronomia Sky Penthouse', bed='5 bedrooms, 7 bathrooms', area='10,290 sq ft suite + 1,517 sq ft terrace & pool = 11,807 sq ft', park=6, price='AED 175,000,000'),
         'B': dict(n='The Billionaire Sky Penthouse', bed='7 bedrooms, 10 bathrooms', area='20,788 sq ft suite + 1,681 sq ft balcony = 22,469 sq ft', park=12, price='AED 750,000,000')}
    def rows(k, extra):
        u = U[k]
        return [['Home', f"{u['n']}: {u['bed']}, private infinity pool"], ['Area', u['area']], ['Price (brochure)', u['price']], ['Parking', f"{u['park']} bays"]] + extra
    def villa_floor(lv, kinds):
        order = sorted(q, key=lambda k: ['north', 'east', 'south', 'west'].index(_compass(_bearing(qdeg[k], rot))))
        bear = [_bearing(qdeg[k], rot) for k in order]
        if kinds == 'R':
            fr = [rows('R', [['Outlook', f'Faces {_compass(a, 8)}, towards {_outlook(a)}']]) for a in bear]
            nos = [f'{_compass(a).capitalize()} Ruby Villa' for a in bear]
        else:
            fr = [[['Home', 'Emerald Villa (2 bedrooms, 3 bathrooms) or Sapphire Villa (2.5 bedrooms with study, 3 bathrooms); each with its own infinity pool. '
                            'The brochure has two of each per floor: one facing Downtown and Burj Khalifa, one facing Dubai Creek Harbour'],
                   ['Area', 'Emerald 3,337 sq ft · Sapphire 3,335 sq ft (suite + terrace & pool)'], ['Price (brochure)', 'Emerald from AED 8.2M · Sapphire from AED 8.4M'],
                   ['Parking', '2 bays'], ['Outlook', f'Faces {_compass(a, 8)}, towards {_outlook(a)}']] for a in bear]
            nos = [f'{_compass(a).capitalize()} villa' for a in bear]
        return dict(label=f'Level {lv}', kind='A', unit='villa' if kinds != 'R' else 'ruby', nos=nos, plan=dict(cells=[q[k] for k in order]), frows=fr)
    def mansion_floor(lv):
        order = sorted(halves, key=lambda k: COMPASS8.index(_compass(_bearing(hdeg[k], rot), 8)))
        bear = [_bearing(hdeg[k], rot) for k in order]
        fr = [[['Home', 'Diamond Sky Mansion (4 bedrooms, 7 bathrooms) or Fleurs de Jardin Sky Mansion (6 bedrooms, 9 bathrooms), half a floor, private infinity pool'],
               ['Area', '5,176 sq ft suite + 1,800 sq ft terrace & pool = 6,976 sq ft'], ['Price (brochure)', 'Fleurs de Jardin AED 31M to 36.1M · Diamond on request'],
               ['Parking', '4 bays'], ['Outlook', f'180° views facing {_compass(a, 8)}, towards {_outlook(a, 80)}']] for a in bear]
        return dict(label=f'Level {lv}', kind='A', unit='mansion', nos=[f'{_compass(a, 8).capitalize()} sky mansion' for a in bear],
                    plan=dict(cells=[halves[k] for k in order]), frows=fr)
    MECH = 'Mechanical floor (brochure vertical diagram): no homes'
    st = [dict(label='Ground floor', kind='M', use='Grand lobby with lobby lounge, concierge and valet arrival', h=6.0)]
    st += [dict(label=f'Podium {i}', kind='M', use='Podium (brochure vertical diagram): parking and building services; there are also 6 basement levels') for i in range(1, 6)]
    st.append(dict(label='Level 7: swimming pool', kind='M', use='Swimming Pool 01: 34 × 9 m pool and 9 × 9 m kids’ pool (brochure vertical diagram)', fac={'slab': '#7fe9ff', 'slabGlow': 1}))
    st.append(dict(label='Level 8: services', kind='M', use='Service floor (brochure vertical diagram)'))
    st.append(dict(label='Level 9: sky garden', kind='M', use='Sky Garden 1 (brochure vertical diagram)'))
    plan_ = ([('ES', lv) for lv in range(10, 19)] + [('X', 19)] + [('ES', lv) for lv in range(20, 44)] + [('X', 44), ('X', 45)] + [('ES', lv) for lv in range(46, 49)] +
             [('R', lv) for lv in range(49, 70)] + [('X', 70), ('X', 71)] + [('R', lv) for lv in range(72, 83)] + [('M', lv) for lv in range(83, 86)] +
             [('X', 86), ('X', 87)] + [('M', lv) for lv in range(88, 97)])
    for k, lv in plan_:
        if k == 'X': st.append(dict(label=f'Level {lv}', kind='M', sub='Mechanical floor', use=MECH)); continue
        e = villa_floor(lv, 'R' if k == 'R' else 'ES') if k in ('ES', 'R') else mansion_floor(lv)
        if lv in (48, 82, 96): e['fac'] = {'slab': '#7fe9ff', 'slabGlow': 1}
        st.append(e)
    st.append(dict(label='Level 97: VIP Sky Lounge', kind='M', use='VIP Sky Lounge, 643 sq m (6,921 sq ft) (brochure vertical diagram)'))
    st.append(dict(label='Level 98: spa & pool', kind='M', use='Spa and Swimming Pool 02, 1,200 sq m (12,916 sq ft): the stratospheric infinity pool (brochure)'))
    st.append(dict(label='Level 99: gym', kind='M', use='Gym, 897 sq m (9,655 sq ft) (brochure vertical diagram)'))
    for lv, nm in ((100, 'Penthouse 01'), (101, 'Penthouse 02')):
        st.append(dict(label=f'Level {lv}', kind='A', unit='astro', nos=[f'Astronomia Sky Penthouse ({nm})'], plan=dict(cells=[plan]),
                       frows=[rows('A', [['Outlook', '360° views: Burj Khalifa, Downtown, Dubai Creek Harbour, the Dubai Water Canal and Dubai Design District']])]))
    st.append(dict(label='Levels 102–103', kind='P', levels=2, unit='bill', nos=['The Billionaire Sky Penthouse (Penthouse 03)'], plan=dict(cells=[plan]),
                   frows=[rows('B', [['Outlook', '360° views over Burj Khalifa, Downtown, Business Bay, Dubai Creek Harbour, the Water Canal and Dubai Design District']])],
                   fac={'slab': '#7fe9ff', 'slabGlow': 1}))
    for L in st:
        if L.get('fac') is None: L.pop('fac', None)
    cfg['stack'] = st; t.pop('stack', None)
    cfg['floorH'] = 4.2
    t.update(w=43, d=43, pts=plan, shape='rect', type='villa', crown=dict(type='lattice', rw=4.6, rh=9.0, low=0.42, corner=1.0, mid=0.88))
    t['height'] = 560
    cfg['height'] = 560
    cfg['hSrc'] = None
    cfg['flatWord'] = ''; cfg['homeWord'] = 'Home'
    cfg['startFloor'] = 'Level 60'
    cfg['camY'] = 250
    cfg['cellsNote'] = ('Drawn from the developer’s brochure: quarter-floor villas sit one round each corner of the lift core, the sky mansions take half a floor each and the '
                        'penthouses whole floors; the brochure’s floor plans for each type are in the gallery below. Which corner each type takes is indicative.')
    AV = 'Ask for live availability'
    cfg['units'] = {
        'villa': dict(name='Emerald and Sapphire Villas (quarter floors)', short='Emerald & Sapphire villas', perFloor='4 homes',
                      rows=[['Emerald Villa', '2 bed · 3,337 sq ft · from AED 8.2M'], ['Sapphire Villa', '2.5 bed · 3,335 sq ft · from AED 8.4M'], ['Levels', '12 to 48 (brochure)']], avail=AV),
        'ruby': dict(name='Ruby Villas (quarter floors)', short='Ruby villas', perFloor='4 homes',
                     rows=[['Ruby Villa', '3 bed · 3,299 sq ft · from AED 13,999,999'], ['Levels', '49 to 82 (brochure)']], avail=AV),
        'mansion': dict(name='Sky Mansions: Diamond and Fleurs de Jardin', short='Sky Mansions', perFloor='2 homes',
                        rows=[['Diamond Sky Mansion', '4 bed · 6,976 sq ft · on request'], ['Fleurs de Jardin Sky Mansion', '6 bed · 6,976 sq ft · from AED 31M'], ['Levels', '83 to 96 (brochure)']], avail=AV),
        'astro': dict(name='Astronomia Sky Penthouse', short='Sky Penthouse', perFloor='1 home (the whole floor)',
                      rows=[['Astronomia Sky Penthouse', '5 bed · 11,807 sq ft · AED 175M'], ['Levels', '100 and 101']], avail=AV),
        'bill': dict(name='The Billionaire Sky Penthouse', short='Sky Penthouse', perFloor='1 home over two floors',
                     rows=[['The Billionaire Sky Penthouse', '7 bed · 22,469 sq ft · AED 750M'], ['Levels', '102 and 103']], avail=AV),
    }
    cfg['note'] = ('Model built from the developer’s brochure. Stack: its vertical diagram, floor by floor: ground, podium levels 1–5, the swimming pool, service and sky-garden '
                   'floors, 83 residential floors (Emerald and Sapphire Villas, then Ruby Villas, then the Diamond and Fleurs de Jardin Sky Mansions), six mechanical floors, '
                   'the VIP Sky Lounge, the spa and pool, the gym, two Astronomia Sky Penthouses and the two-floor Billionaire Sky Penthouse; 560 m total height. '
                   'Levels are numbered as on the brochure’s unit pages, one higher than the floor numbers on its diagram. Areas, parking and prices: the brochure’s unit pages. '
                   'Floor to floor 4.2 m (developer’s factsheet). The crown is drawn as on the renders: a lattice of diamond-shaped frames, lit at night. '
                   'The plan is turned to the building outline mapped on OpenStreetMap; views are named from the bearings of the landmarks from the tower. '
                   'Position: the project’s Google Maps pin in Business Bay. Surroundings are from OpenStreetMap.')
    return cfg

def valo(cfg):
    t = cfg['towers'][0]
    st = cfg['stack']
    # slab tower with glazed corners and balconies; the lobby storey is taller with a bronze canopy; an open silver frame stands above the roof
    t.update(w=34, d=22, pts=None, shape='rect', crown=dict(type='frame', h=7, c='#e8eaec'))
    cfg['note'] = ('Model built from published figures: a 37-storey residential building with about 291 homes (Propsearch; Dubai Land Department project #3033: 122 one-bedroom, '
                   '129 two-bedroom and 40 three-bedroom homes). Form as on Emaar’s renders: a glass slab tower with silver mullions, balconies on the long faces and corners, '
                   'and an open frame above the roof. The floor plate is not published, so the 34 × 22 m plan is approximate. '
                   'Position: the map pin on Propsearch’s Valo page in Dubai Creek Harbour. Surroundings (roads, water, parks, existing buildings) are from OpenStreetMap.')
    return cfg

def shahrukhz(cfg):
    t = cfg['towers'][0]
    st = cfg['stack']
    n = len(st)                          # 55 office storeys (Danube)
    # footprint by floor, read from Danube's renders: a wide podium, a lower shaft that narrows towards a waist, a wide sky-pool deck,
    # the slim open lounge storey above it, the upper shaft, and a glass crown that sweeps up from the helipad deck
    tiers = [dict({'from': 0}, **stadium(60, 44))]
    for k in range(6, 31):               # lower shaft: 50 m at the podium, narrowing to 44 m at the waist
        u = (k - 6) / 24
        tiers.append(dict({'from': k}, **stadium(round(50 - 6 * u, 1), round(33 - 3 * u, 1))))
    tiers.append(dict({'from': 31}, **stadium(56, 40)))     # sky-pool deck
    tiers.append(dict({'from': 32}, **stadium(34, 22)))     # open lounge storey (Lounge 33)
    tiers.append(dict({'from': 33}, **stadium(40, 26)))
    for k in range(34, n):               # upper shaft, widening slightly towards the top
        u = (k - 34) / max(1, n - 35)
        tiers.append(dict({'from': k}, **stadium(round(44 + 4 * u, 1), round(30 + 2 * u, 1))))
    t.update(w=60, d=44, shape='round', r=22, pts=None, tiers=tiers, crown=dict(type='wave', h=16))
    cfg['camY'] = 105
    # the sky pool on the deck round the lounge storey
    z = sum(L.get('h') or L.get('levels', 1) * cfg['floorH'] for L in st[:32]) + 0.4
    pool = [[round(18 * math.cos(a), 1), round(-13 + 5.5 * math.sin(a), 1)] for a in (math.pi + math.pi * i / 24 for i in range(25))] + [[16, -12.2], [-16, -12.2]]
    cfg.setdefault('context', []).append(dict(t='flat', p=pool, c='#36a8d8', z=round(z, 2)))
    cfg['note'] = ('Model built from published figures: a 55-storey office tower with 615 offices, a sky pool, Lounge 33, Lounge 55 and a helipad (Danube Properties). '
                   'Form as on Danube’s renders: a wide podium with a garden roof, a rounded shaft that narrows to a waist, the sky-pool deck with the slim lounge storey above it, '
                   'the upper shaft, and a glass crown that sweeps up from the helipad deck, with gold bands at every floor. Floor heights and floor plates are not published: '
                   '4 m floor to floor is assumed and the plan sizes are read from the renders, so they are approximate. '
                   'Position: the project’s Google Maps pin on Sheikh Zayed Road (checked 17 Oct 2026). Surroundings (roads, water, parks, existing buildings) are from OpenStreetMap.')
    return cfg

BUILD = {'binghatti-burj-jacob': burj_jacob, 'emaar-valo': valo, 'danube-shahrukhz': shahrukhz}
PIDS = tuple(BUILD)
def build(pid, p, cfg): return BUILD[pid](cfg)
