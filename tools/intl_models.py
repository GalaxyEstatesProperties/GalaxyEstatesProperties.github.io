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
    VILLA = ('Emerald Villa (2 bedrooms, 3,347 sq ft), Sapphire Villa (2 bedrooms + study, 3,351 sq ft) or Ruby Villa (3 bedrooms, 3,314 sq ft); '
             'which of the three is on this floor is on the developer’s availability sheet')
    MANSION = 'Diamond Sky Mansion (4 bedrooms) or Fleurs de Jardin Sky Mansion (6 bedrooms), 7,032 sq ft each, half a floor'
    st = [dict(label='Ground floor', kind='M', use='Grand lobby with lobby lounge, concierge and valet arrival', h=6.0)]
    st += [dict(label=f'Podium level {i}', kind='M', use='Podium: parking and building services (there are also 6 basement levels of parking)') for i in range(1, 6)]
    for lv in range(6, 83):            # quarter-floor villas
        order = sorted(q, key=lambda k: ['north', 'east', 'south', 'west'].index(_compass(_bearing(qdeg[k], rot))))
        cells = [q[k] for k in order]; bear = [_bearing(qdeg[k], rot) for k in order]
        L = dict(label=f'Level {lv}', kind='A', unit='villa', nos=[f'{_compass(a).capitalize()}-facing villa' for a in bear],
                 plan=dict(cells=cells),
                 frows=[[['Home', VILLA], ['Outlook', f'Faces {_compass(a, 8)}, towards {_outlook(a)}'], ['Private pool', 'Each home has its own infinity pool (factsheet: private pools in all units)'],
                         ['Arrival', 'Opens from a private lift (Jacob & Co.)']] for a in bear])
        if lv % 8 == 6: L['fac'] = {'slab': '#7fe9ff', 'slabGlow': 1}     # lit lines framing the tall facade panels, as on the night renders
        st.append(L)
    for lv in range(83, 97):           # sky mansions, two a floor
        order = sorted(halves, key=lambda k: COMPASS8.index(_compass(_bearing(hdeg[k], rot), 8)))
        bear = [_bearing(hdeg[k], rot) for k in order]
        st.append(dict(label=f'Level {lv}', kind='A', unit='mansion', nos=[f'{_compass(a, 8).capitalize()} sky mansion' for a in bear],
                       plan=dict(cells=[halves[k] for k in order]),
                       frows=[[['Home', MANSION], ['Outlook', f'180° views facing {_compass(a, 8)}, towards {_outlook(a, 80)}'], ['Private pool', 'Private infinity pool']] for a in bear],
                       fac={'slab': '#7fe9ff', 'slabGlow': 1} if lv in (83, 90) else None))
    st.append(dict(label='Levels 97–99: sky amenities', kind='M', levels=3,
                   use='Near the summit, just below the Sky Penthouses (Jacob & Co.): a 900 sq m fitness centre, a 1,200 sq m spa and pool retreat and a 640 sq m VIP Sky Lounge. '
                       'Which of the three is on which of these levels is not published.'))
    for lv in (100, 101):
        st.append(dict(label=f'Level {lv}', kind='A', unit='astro', nos=['Astronomia Sky Penthouse'], plan=dict(cells=[plan]),
                       frows=[[['Home', 'Astronomia Sky Penthouse: a full floor, 5 bedrooms, 14,195 sq ft'], ['Outlook', '360° views: Burj Khalifa, Downtown, Business Bay, Dubai Creek Harbour, the Water Canal and Dubai Design District'],
                               ['Private pool', 'Private infinity pool']]]))
    st.append(dict(label='Levels 102–103', kind='P', levels=2, unit='bill', nos=['Billionaire Sky Penthouse'], plan=dict(cells=[plan]),
                   frows=[[['Home', 'The Billionaire Sky Penthouse: a duplex over the top two floors, 7 bedrooms, 27,800 sq ft'], ['Outlook', '360° views over all of Dubai']]],
                   fac={'slab': '#7fe9ff', 'slabGlow': 1}))
    for L in st:
        if L.get('fac') is None: L.pop('fac', None)
    cfg['stack'] = st; t.pop('stack', None)
    cfg['floorH'] = 4.2
    t.update(w=43, d=43, pts=plan, shape='rect', type='villa', crown=dict(type='lattice', rw=4.6, rh=9.0, low=0.42, corner=1.0, mid=0.88))
    t['height'] = 557
    cfg['height'] = 557
    cfg['hSrc'] = None
    cfg['flatWord'] = ''; cfg['homeWord'] = 'Home'
    cfg['startFloor'] = 'Level 60'
    cfg['camY'] = 250
    cfg['cellsNote'] = ('Drawn from the developer’s description: on the villa floors one home sits round each corner of the lift core, on the mansion floors one on each half, '
                        'and the penthouses take whole floors. Detailed floor plans are not published, so the outlines are indicative.')
    cfg['units'] = {
        'villa': dict(name='Quarter-floor villas: Emerald, Sapphire and Ruby', short='2 – 7 bedroom homes, 104 levels', perFloor='4 homes',
                      rows=[['Emerald Villa', '2 bedrooms · 3,347 sq ft · 70 homes'], ['Sapphire Villa', '2 bedrooms + study · 3,351 sq ft · 70 homes'],
                            ['Ruby Villa', '3 bedrooms · 3,314 sq ft · 132 homes'], ['Sky gardens', '4 in the tower (their levels are not published)']],
                      avail='Ask for live availability'),
        'mansion': dict(name='Sky Mansions: Diamond and Fleurs de Jardin', short='Sky Mansions', perFloor='2 homes',
                        rows=[['Diamond Sky Mansion', '4 bedrooms · 7,032 sq ft · half a floor'], ['Fleurs de Jardin Sky Mansion', '6 bedrooms · 7,032 sq ft · half a floor'],
                              ['Where', 'Levels 83 to 96']], avail='Ask for live availability'),
        'astro': dict(name='Astronomia Sky Penthouse', short='Sky Penthouse', perFloor='1 home (the whole floor)',
                      rows=[['Astronomia Sky Penthouse', '5 bedrooms · 14,195 sq ft · 2 in the tower']], avail='Ask for live availability'),
        'bill': dict(name='The Billionaire Sky Penthouse', short='Sky Penthouse', perFloor='1 home over two floors',
                     rows=[['Billionaire Sky Penthouse', '7 bedrooms · 27,800 sq ft · the top two floors']], avail='Ask for live availability'),
    }
    cfg['note'] = ('Model built from published figures. Jacob & Co. (official page) for the residences and amenities; the developer’s factsheet for the stack: ground + 5 podium levels + '
                   '98 floors (104 levels, 4.2 m floor to floor, about 437 m to the roof), the 18,700 sq ft floor plate, 1 to 4 homes a floor, the sky mansions on levels 83–96 and the '
                   'Billionaire penthouse on the top two floors; 557 m to the top of the crown (Wikipedia). Levels are counted from the ground, with the podium as levels 1–5. '
                   'The crown is drawn as on the renders: a lattice of diamond-shaped frames, lit at night, rising from the roof into points, highest at the corners. '
                   'The plan is turned to the building outline mapped on OpenStreetMap at the site; views are named from the bearings of the landmarks from the tower '
                   '(Burj Khalifa to the west-north-west, Dubai Creek Harbour to the east-north-east). '
                   'Position: the project’s Google Maps pin in Business Bay. Surroundings (roads, water, parks, existing buildings) are from OpenStreetMap.')
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
