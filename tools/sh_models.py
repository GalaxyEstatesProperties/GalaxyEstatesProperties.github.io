"""Shantigram 3D explorers rebuilt from the official plans (18 Oct 2026): Aster + Aster NEO, Amogha, Embrace, Elysium Novus,
Greenfield, Ambrosia, Paarijat, Skyline, Belrosa and The North Park (all registered phases).
Geometry: shgeom.py (official master / floor plans georeferenced on satellite imagery; villa footprints from Google Maps).
Floors and homes per floor: Gujarat RERA unit lists and inventories, and Adani Realty's floor plans (cited per project)."""
import json, math, os
HERE = os.path.dirname(os.path.abspath(__file__))
GEOM = json.load(open(os.path.join(HERE, 't3dall', 'sh_geom.json')))
POLYS = json.load(open(os.path.join(HERE, 'adani', 'polys.json')))          # Gujarat RERA map outlines by RERA project id
E = 6378137.0; D = math.pi / 180
ORIGIN = (23.161, 72.5375)
PIDS = ('aster-neo', 'amogha', 'embrace', 'elysium-novus', 'greenfield', 'ambrosia', 'paarijat', 'shilp-skyline', 'belrosa', 'north-park')
RERA_KEY = {'aster-neo': '19001', 'amogha': '11373', 'embrace': '19621', 'elysium-novus': '25357', 'greenfield': '26054', 'ambrosia': '17965',
            'paarijat': '17678', 'shilp-skyline': '24007', 'belrosa': '27447', 'north-park': '9208'}

def xy(la, lo):
    return ((lo - ORIGIN[1]) * D * E * math.cos(ORIGIN[0] * D), (la - ORIGIN[0]) * D * E)

def area(P): return abs(sum(P[i][0] * P[i - 1][1] - P[i - 1][0] * P[i][1] for i in range(len(P)))) / 2

def frame(pid, extra_pts=()):
    """site frame: centre and orientation from the registered plot (minimum-area rectangle), as the other explorers"""
    import sitegeo as SG
    P = [xy(*q) for q in POLYS[RERA_KEY[pid]]] + [xy(*q) for q in extra_pts]
    rot, w, d, (cx, cy) = SG.mbr(P)
    return cx, cy, rot

def loc(fr, la, lo):
    cx, cy, rot = fr; x, y = xy(la, lo); r = math.radians(rot); c, s = math.cos(r), math.sin(r)
    return (x - cx) * c + (y - cy) * s, -(x - cx) * s + (y - cy) * c

def tower(fr, tid, label, ll, stack, typ, **k):
    P = [loc(fr, *q) for q in ll]
    if len(P) > 3 and abs(P[0][0] - P[-1][0]) + abs(P[0][1] - P[-1][1]) < 0.3: P = P[:-1]
    A = sum(P[i][0] * P[i - 1][1] - P[i - 1][0] * P[i][1] for i in range(len(P))) / 2
    if A > 0: P = P[::-1]            # clockwise in plot coordinates, like the other footprints
    cx = sum(p[0] for p in P) / len(P); cy = sum(p[1] for p in P) / len(P)
    pts = [[round(a - cx, 2), round(b - cy, 2)] for a, b in P]
    us = [a for a, b in pts]; vs = [b for a, b in pts]
    t = dict(id=tid, label=label, x=round(cx, 2), y=round(cy, 2), w=round(max(us) - min(us), 1), d=round(max(vs) - min(vs), 1), ang=0, pts=pts, stack=stack, type=typ)
    t.update(k); return t

def tier_pts(fr, t, ll):
    P = [loc(fr, *q) for q in ll]
    if area(P) < 1: return None
    return [[round(a - t['x'], 2), round(b - t['y'], 2)] for a, b in P]

def homes(n_from, n_to, per, word='homes', note=None, lab='Floor'):
    return [dict(label=f'{lab} {f}', kind='A', note=note or f'{per} {word} on this floor') for f in range(n_from, n_to + 1)]

def ground(use='Entrance lobby and common areas'):
    return [dict(label='Ground floor', kind='M', use=use)]

def plot_local(fr, key):
    return [[round(a, 1), round(b, 1)] for a, b in (loc(fr, *q) for q in POLYS[key])]

def ctx_items(fr, items):
    out = []
    for o in items or []:
        P = [[round(a, 1), round(b, 1)] for a, b in (loc(fr, *q) for q in o['ll'])]
        out.append(dict(t='prism', p=P, h=o['h'], z=o.get('z', 0), label=o.get('label'), c=o.get('c')))
    return out

def base_cfg(pid, p, base, fr, towers, units, st, floorH, note, plot_key=None, extra=None):
    cx, cy, rot = fr
    plotPoly = plot_local(fr, plot_key or RERA_KEY[pid])
    xs = [t['x'] + a for t in towers for a, b in t['pts']] + [a for a, b in plotPoly]
    ys = [t['y'] + b for t in towers for a, b in t['pts']] + [b for a, b in plotPoly]
    plot = dict(w=round(max(xs) - min(xs), 1), d=round(max(ys) - min(ys), 1))
    geo = dict(base['geo']); geo.update(name='GEO_SHANTIGRAM', file='assets/geo-shantigram.js', x=round(cx, 1), y=round(cy, 1), rot=round(rot, 1), radius=800)
    mid = st[min(len(st) - 1, max(1, len(st) // 2))]['label']
    cfg = dict(project=p['name'], interest=p['label'], floorH=floorH, stack=st, towers=towers, units=units, plot=plot, geo=geo, kind='residential',
               startFloor=mid, enqLabel='Enquire about this floor', plotPoly=plotPoly, note=note)
    if extra: cfg.update(extra)
    return cfg

SURR = ' Surroundings (roads, water, parks, other buildings) are from OpenStreetMap; finishes are simplified.'
GEO_NOTE = (' Building outlines: the developer’s official master plan and typical-floor plans, georeferenced on current satellite imagery '
            '(each outline is placed where the tower stands today). Plot: the boundary registered on the Gujarat RERA map service.')

def u(name, short, rows, avail='Ask for live availability', **k):
    d = dict(name=name, short=short, rows=rows, avail=avail); d.update(k); return d

# ------------------------------------------------------------------ project builders
def aster(p, base):
    g = GEOM['aster-neo']; fr = frame('aster-neo', POLYS['10307'])
    st = ground() + homes(1, 22, 4)
    T = []
    for i, (lab, ll) in enumerate(g['towers'].items()):
        neo = lab.split()[-1] in 'ABGH'
        T.append(tower(fr, f'T{i+1}', lab + (' · Aster NEO' if neo else ' · Aster'), ll, st, 'neo' if neo else 'aster'))
    units = {'neo': u('Aster NEO · 2 BHK #Smartments', '2 BHK (NEO)',
                      [['Size', '634.85 sq.ft. RERA carpet (58.98 sq m) · 1,205 sq.ft. saleable'], ['Price', '₹78 Lakhs* onwards, all inclusive'],
                       ['Towers', 'A, B, G and H · ground + 22 floors (Gujarat RERA: 176 homes in A+B, 176 in G+H)'], ['Status', 'Completed, BU received (Adani Realty)'],
                       ['RERA', 'PR/GJ/AHMEDABAD/AHMEDABAD CITY/AUDA/RAA11924/070623']], perFloor='4 homes'),
             'aster': u('Aster (phase 1) · 2 BHK apartments', '2 BHK (Aster)',
                        [['Size', '634.85 – 641.52 sq.ft. RERA carpet (Gujarat RERA: 58.98 – 59.60 sq m); Adani Realty’s unit plan for towers I–M shows 697.83 sq.ft.'],
                         ['Towers', 'C, D, I, J, K, L and M · ground + 22 floors (Gujarat RERA: 616 homes, 4 per floor)'],
                         ['Status', 'Completed; ask us for resale availability'], ['RERA', 'PR/GJ/AHMEDABAD/AHMEDABAD CITY/AUDA/RAA07338/140820']], perFloor='4 homes')}
    note = ('Aster and Aster NEO together: 11 towers of ground + 22 floors on the 18,994 sq m Aster site (Adani Realty). Aster NEO is towers A, B, G and H; '
            'Aster (phase 1) is towers C, D, I, J, K, L and M. Tower letters and positions are as printed on Adani Realty’s Aster NEO master layout; '
            'floors and homes per floor from the Gujarat RERA unit lists (4 homes on every floor from 1 to 22).' + GEO_NOTE +
            ' The gold area is Aster NEO’s registered plot; the thin gold line is Aster phase 1’s.' + SURR)
    ph1 = [[round(a, 1), round(b, 1)] for a, b in (loc(fr, *q) for q in POLYS['10307'])]
    cfg = base_cfg('aster-neo', p, base, fr, T, units, st, 3.1, note, extra=dict(context=[dict(t='line', p=ph1, c='#c9a962', z=0.8)], clear=[ph1]))
    cfg['perFloor'] = '4 homes'
    return cfg

def amogha(p, base):
    g = GEOM['amogha']; fr = frame('amogha')
    st = ground('Double-height entrance foyer and lobby') + homes(1, 14, 4)
    T = [tower(fr, f'T{i+1}', lab, ll, st, 'all') for i, (lab, ll) in enumerate(sorted(g['towers'].items()))]
    units = {'all': u('Amogha · 3 BHK apartments', '3 BHK',
                      [['Size', '624.09 – 776.40 sq.ft. RERA carpet (Gujarat RERA: 57.98 – 72.13 sq m); Adani Realty’s unit plans (types A, B, C) list 812.35 – 826.13 sq.ft.'],
                       ['Wings', '8 wings (A–H) in joined pairs · ground + 14 floors · 4 homes per floor (Gujarat RERA: 448 homes)'],
                       ['Status', 'Completed (Adani Realty)'], ['RERA', 'PR/GJ/AHMEDABAD/DASKROI/AUDA/RAA08011/EX1/260224/280225']], perFloor='4 homes')}
    note = ('Amogha: 8 wings (A–H) built as four joined pairs, ground + 14 floors, 448 homes (Gujarat RERA: 112 homes in each pair, unit numbers on floors 1 to 14). '
            'Wing letters and positions as printed on Adani Realty’s master layout; the clubhouse is drawn from the same plan.' + GEO_NOTE + SURR)
    return base_cfg('amogha', p, base, fr, T, units, st, 3.1, note, extra=dict(context=ctx_items(fr, g.get('ctx'))))

def embrace(p, base):
    g = GEOM['embrace']; fr = frame('embrace')
    st4 = ground('Stilt: entrance lobby and parking') + homes(1, 14, 4)
    stC = ground('Stilt: entrance lobby; amenities next to the tower') + homes(1, 11, 2) + [dict(label='Floors 12–13 (penthouses)', kind='P', levels=2, unit='ph', note='2 duplex penthouses (lower level on floor 12, upper level on floor 13)')]
    T = []
    for i, lab in enumerate(['Tower A', 'Tower B', 'Tower C', 'Tower D', 'Tower E']):
        T.append(tower(fr, f'T{i+1}', lab, g['towers'][lab], stC if lab == 'Tower C' else st4, 'c' if lab == 'Tower C' else 'all'))
    sizes = ['Sizes', '987.91 sq.ft. (smallest registered home, Gujarat RERA 91.78 sq m) · 1,082.31 sq.ft. (Adani Realty) · 1,205 sq.ft. (Housiey price sheet) · penthouses up to 2,238.14 sq.ft. (Gujarat RERA 207.93 sq m); all RERA carpet']
    units = {'all': u('Embrace · 3 BHK (towers A, B, D, E)', '3 BHK',
                      [['Type', '3 BHK lifestyle homes: corner (type 1) and internal (type 2) plans, 4 homes per floor'], sizes, ['Price', 'From ₹1.42 Cr*, all inclusive'],
                       ['RERA', 'PR/GJ/AHMEDABAD/AHMEDABAD CITY/AUDA/RAA12526/251023']], perFloor='4 homes'),
             'c': u('Embrace · Tower C', '3 BHK (C)',
                    [['Type', '3 BHK, 2 homes per floor, each with two balconies (plan 1 on floors 1, 2, 4, 6, 8, 10, 11; plan 2 on floors 3, 5, 7, 9)'], sizes,
                     ['RERA', 'PR/GJ/AHMEDABAD/AHMEDABAD CITY/AUDA/RAA12526/251023']], perFloor='2 homes'),
             'ph': u('Embrace · Tower C duplex penthouses', 'Penthouse',
                     [['Type', '3 BHK duplex penthouse: lower level on floor 12, upper level on floor 13 (Adani Realty plans)'], ['Size', 'Up to 2,238.14 sq.ft. RERA carpet (largest home registered)'],
                      ['RERA', 'PR/GJ/AHMEDABAD/AHMEDABAD CITY/AUDA/RAA12526/251023']], perFloor='2 penthouses')}
    note = ('Embrace: towers A and B are one joined building facing the main road, D and E a second joined building at the back, and tower C stands between them on the side, '
            'as on Adani Realty’s master layout. Homes: 112 in A+B, 112 in D+E and 24 in C (Gujarat RERA), i.e. 4 per floor on floors 1–14 in A, B, D, E; '
            'C has 2 homes per floor on floors 1–11 and 2 duplex penthouses on floors 12–13 (Adani Realty floor plans). '
            'Adani Realty describes the towers as “13 and 14 floors”; the floor counts here are those that hold the registered homes.' + GEO_NOTE + SURR)
    return base_cfg('embrace', p, base, fr, T, units, st4, 3.2, note)

def elysium(p, base):
    g = GEOM['elysium-novus']; fr = frame('elysium-novus')
    st4 = ground() + homes(1, 14, 4); st6 = ground() + homes(1, 14, 6)
    T = []
    for i, lab in enumerate(['Block C', 'Block D', 'Block E', 'Block F', 'Block G', 'Block J']):
        k = lab.split()[-1]
        T.append(tower(fr, f'T{i+1}', lab, g['towers'][lab], st6 if k == 'G' else st4, 'g' if k == 'G' else 'j' if k == 'J' else 'cdef'))
    sizes = ['Sizes in the project', '2 BHK: 717.42 sq.ft. · 3 BHK: 973.93 – 1,103.63 sq.ft. (Adani Realty); RERA carpet 668.44 – 1,016 sq.ft. (Gujarat RERA 62.10 – 94.39 sq m)']
    rera = ['RERA', 'PR/GJ/AHMEDABAD/AHMEDABAD CITY/Ahmedabad Urban Development Authority/RAA14729/270125/311228']
    units = {'cdef': u('Elysium Novus · blocks C, D, E, F', '3 BHK (C–F)', [['Plans', 'Types 1 and 2 (Adani Realty), 4 homes per floor; blocks C+D and E+F are joined pairs'], sizes, rera], perFloor='4 homes'),
             'g': u('Elysium Novus · block G', 'Block G', [['Plans', 'Types 3 and 4 (Adani Realty): Y-shaped block, 6 homes per floor'], sizes, rera], perFloor='6 homes'),
             'j': u('Elysium Novus · block J', 'Block J', [['Plans', 'Type 5 (Adani Realty): H-shaped block, 4 homes per floor'], sizes, rera], perFloor='4 homes')}
    note = ('Elysium Novus: blocks C+D and E+F are joined pairs, G is a Y-shaped block with 6 homes per floor and J an H-shaped block with 4, each from Adani Realty’s typical-floor plans. '
            'All blocks are ground + 14 floors (Gujarat RERA unit numbers 101–1406; 364 homes) and 44.8 m tall (Gujarat RERA).' + GEO_NOTE + SURR)
    return base_cfg('elysium-novus', p, base, fr, T, units, st4, 2.99, note, extra=dict(height=44.8))

def greenfield(p, base):
    g = GEOM['greenfield']; fr = frame('greenfield')
    st = ground('Ground floor amenities (gym, mini theatre, library and more, per the developer’s ground-floor plan)') + homes(1, 19, 4) + \
         [dict(label='Floors 20–21 (penthouses)', kind='P', levels=2, unit='ph', note='4 duplex penthouses: lower level on floor 20, upper level on floor 21')]
    T = [tower(fr, f'T{i+1}', lab, g['towers'][lab], st, 'all') for i, lab in enumerate(['Block A', 'Block B', 'Block C'])]
    rera = ['RERA', 'PR/GJ/AHMEDABAD/AHMEDABAD CITY/AUDA/RAA14879/250225/311229']
    units = {'all': u('Greenfield · 3 BHK apartments', '3 BHK',
                      [['Size', 'From 1,277.89 sq.ft. RERA carpet; e.g. unit 101 (first floor, blocks A–C): 1,379 sq.ft. carpet + 110 sq.ft. terrace'], ['Price', 'From ₹1.73 Cr*, all inclusive'], rera], perFloor='4 homes'),
             'ph': u('Greenfield · 4 BHK duplex penthouses', '4 BHK PH', [['Size', 'Up to 2,163.33 sq.ft. RERA carpet'], ['Levels', 'Lower level on floor 20, upper level on floor 21 (units 2001–2004)'], rera], perFloor='4 penthouses')}
    note = ('Greenfield: three blocks in a row, Block A nearest the 34.5 m road at the entrance, then B and C, as labelled on the developer’s ground-floor plan and on the key plans '
            'of Adani Realty’s unit plans. Ground + 21 floors: 4 apartments per floor on floors 1–19 and 4 duplex penthouses on floors 20–21 (Gujarat RERA: 80 homes per block, unit numbers 101–2004).'
            + GEO_NOTE + SURR)
    return base_cfg('greenfield', p, base, fr, T, units, st, 3.2, note)

def ambrosia(p, base):
    g = GEOM['ambrosia']; fr = frame('ambrosia')
    st = ground() + homes(1, 13, 4)
    T = [tower(fr, f'T{i+1}', lab, g['towers'][lab], st, 'all') for i, lab in enumerate(['Wing A', 'Wing B', 'Wing C'])]
    units = {'all': u('Ambrosia · 4 BHK #Uberments', '4 BHK',
                      [['Types', '4 BHK Classic and 4 BHK Deluxe (Adani Realty unit plans)'], ['Size', '1,671.60 – 1,902.19 sq.ft. RERA carpet (Adani Realty)'],
                       ['Price', 'From ₹2.49 Cr*, all inclusive'], ['RERA', 'PR/GJ/GANDHINAGAR/GANDHINAGAR/AUDA/RAA10833/201022']], perFloor='4 homes')}
    note = ('Ambrosia: wings A, B and C around a central garden, B at the back and A and C on either side, as on Adani Realty’s master layout; each wing is the X-shaped plan of its typical floor. '
            'Ground + 13 floors, 4 homes per floor (Gujarat RERA: 52 homes per wing, 156 in all).' + GEO_NOTE + SURR)
    return base_cfg('ambrosia', p, base, fr, T, units, st, 3.2, note)

def paarijat(p, base):
    g = GEOM['paarijat']; fr = frame('paarijat', [q for ll in g['towers'].values() for q in ll])
    st = ground() + homes(1, 14, 4)
    T = [tower(fr, f'T{i+1}', lab, g['towers'][lab], st, 'all') for i, lab in enumerate(['Block A', 'Block B'])]
    units = {'all': u('Paarijat · 4 BHK premium homes', '4 BHK',
                      [['Size', '1,405 – 1,608 sq.ft. RERA carpet (Adani Realty)'], ['Status', 'BU received (Adani Realty)'], ['RERA', 'PR/GJ/GANDHINAGAR/GANDHINAGAR/AUDA/RAA10759/121022']], perFloor='4 homes')}
    note = ('Paarijat: Block A (towards the main road) and Block B, with the society amenity block between them, from Adani Realty’s floor plan (block names as printed) and its north arrow. '
            'Ground + 14 floors, 4 homes per floor (Gujarat RERA: 56 homes per block). The plot outline on the RERA map is a thin strip that does not match the 6,203 sq m registered land, '
            'so the gold outline here is drawn around the buildings.' + GEO_NOTE.replace(' Plot: the boundary registered on the Gujarat RERA map service.', '') + SURR)
    cfg = base_cfg('paarijat', p, base, fr, T, units, st, 3.2, note, extra=dict(context=ctx_items(fr, g.get('ctx'))))
    xs = [t['x'] + a for t in T for a, b in t['pts']]; ys = [t['y'] + b for t in T for a, b in t['pts']]
    m = 8; x0, x1, y0, y1 = min(xs) - m, max(xs) + m, min(ys) - m, max(ys) + m
    cfg['plotPoly'] = [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]; cfg['plot'] = dict(w=round(x1 - x0, 1), d=round(y1 - y0, 1))
    return cfg

def skyline(p, base):
    g = GEOM['shilp-skyline']; fr = frame('shilp-skyline')
    pod = [dict(label='Ground floor', kind='M', use='Podium: entrance foyer and parking (ground, first floor and the deck above join all three blocks)'),
           dict(label='Floor 1', kind='M', use='Podium: parking level joined across all blocks')]
    stAC = pod + homes(2, 22, 4) + [dict(label='Floors 23–24 (penthouses)', kind='P', levels=2, unit='ph', note='2 duplex penthouses: lower level on floor 23, upper level on floor 24')]
    stB = pod + homes(2, 22, 4)
    T = []
    for i, lab in enumerate(['Block A', 'Block B', 'Block C']):
        t = tower(fr, f'T{i+1}', lab, g['towers'][lab], stB if lab == 'Block B' else stAC, 'all')
        pp = tier_pts(fr, t, g['pods'][lab])
        if pp:   # the joined podium (ground + first floor) under each block, then the tower outline from floor 2
            t['tiers'] = [dict({'from': 0}, pts=pp, w=t['w'], d=t['d']), dict({'from': 2}, pts=t['pts'])]
        T.append(t)
    rera = ['RERA', 'PR/GJ/AHMEDABAD/AHMEDABAD CITY/Ahmedabad Urban Development Authority/RAA14084/020924/300929']
    units = {'all': u('Skyline · 4 BHK', '4 BHK', [['Size', 'From 1,479.28 sq.ft. (RERA area)'], ['Price', 'From ₹2.23 Cr*, all inclusive'], rera], perFloor='4 homes'),
             'ph': u('Skyline · duplex penthouses', 'Penthouse', [['Size', 'Up to 2,349.76 sq.ft. (RERA area)'], ['Levels', 'Lower level on floor 23, upper on floor 24, in blocks A and C (Adani Realty plans)'], rera], perFloor='2 penthouses')}
    ctx = ctx_items(fr, g.get('ctx'))
    for o in ctx: o.update(h=0.6, z=7.2, c='#5f8f5a')      # landscaped amenity deck (pool, deck, lawn) on top of the podium
    note = ('Skyline: blocks A, B and C stand on a two-level podium (ground and first floor, parking) that joins all three; the amenity deck with pool, deck and lawn is on the podium roof '
            'between A and C, as on Adani Realty’s ground-floor and typical-floor plans. Block A is at the entrance on the 120 ft road. Homes: 4 per floor on floors 2–22; '
            'blocks A and C also have 2 duplex penthouses on floors 23–24 (Gujarat RERA: 86 homes in A, 84 in B, 86 in C; 79 m tall).' + GEO_NOTE + SURR)
    return base_cfg('shilp-skyline', p, base, fr, T, units, stAC, 3.16, note, extra=dict(context=ctx, height=79))

def belrosa(p, base):
    g = GEOM['belrosa']; fr = frame('belrosa')
    st = [dict(label='Ground floor', kind='M', use='Entrance lobbies, drop-off and ground-floor amenities'),
          dict(label='Sky Lounge level', kind='M', use='Sky Lounge: banquet hall, gym, swimming pools, spa, sky club café and event lawn (Adani Realty’s Sky Lounge floor plan)')]
    st += homes(1, 18, 1, word='home', note='1 home per block on this floor (4 on the floor; refuge areas on floors 6, 10, 14 and 18)')
    st += [dict(label='Floor 19', kind='S', use='No home is registered on floor 19 in the Gujarat RERA register (services / refuge level)')]
    st += homes(20, 26, 1, word='home', note='1 home per block on this floor (4 on the floor)')
    st += [dict(label='Floors 27–28 (duplexes)', kind='P', levels=2, note='Duplex: lower level on floor 27, upper level on floor 28'),
           dict(label='Floors 29–30 (duplexes)', kind='P', levels=2, note='Duplex: lower level on floor 29, upper level on floor 30')]
    rera = ['RERA', 'PR/GJ/GANDHINAGAR/GANDHINAGAR/Ahmedabad Urban Development Authority/RAA15538/180725/310530']
    T = []
    for i, lab in enumerate(['Block A', 'Block B', 'Block C', 'Block D']):
        k = lab.split()[-1]
        T.append(tower(fr, f'T{i+1}', lab, g['towers'][lab], st, 'ab' if k in 'AB' else k.lower(), crown=dict(type='frame', h=7)))
    units = {'ab': u('Belrosa · 4 BHK (blocks A and B)', '4 BHK', [['Size', '2,942.23 sq.ft. (RERA carpet + exclusive area)'], ['Plan', 'Master suites, family room/dining 38′7″ × 15′, patio'], rera], perFloor='1 home per block'),
             'c': u('Belrosa · 5 BHK (block C)', '5 BHK', [['Size', '3,664.60 sq.ft. (RERA carpet + exclusive area)'], rera], perFloor='1 home per block'),
             'd': u('Belrosa · 5 BHK (block D)', '5 BHK', [['Size', '5 BHK: 3,664.60 – 5,092.77 sq.ft. across the 5 BHK homes (RERA carpet + exclusive area)'], rera], perFloor='1 home per block'),
             'Pab': u('Belrosa · 5 BHK duplex (blocks A and B)', '5 BHK duplex', [['Size', 'Up to 5,092.77 sq.ft.'], ['Levels', 'Floors 27–28 and 29–30'], rera], perFloor='1 duplex per block'),
             'Pc': u('Belrosa · 5 BHK duplex (block C)', '5 BHK duplex', [['Size', 'Up to 5,092.77 sq.ft.'], ['Levels', 'Floors 27–28 and 29–30'], rera], perFloor='1 duplex per block'),
             'Pd': u('Belrosa · 6 BHK duplex (block D)', '6 BHK duplex', [['Size', '6,911.46 sq.ft.'], ['Levels', 'Floors 27–28 and 29–30'], rera], perFloor='1 duplex per block')}
    note = ('Belrosa: one 125 m tower in which the four blocks A–D are joined side by side along the front facade (Adani Realty’s typical-floor plan); the two 5 BHK blocks (C, D) and '
            'the two 4 BHK blocks (A, B) are drawn in the order shown on that plan, which does not print the block letters. 32 floors: ground, the Sky Lounge amenity level, 100 apartments '
            '(one per block on floors 1–18 and 20–26) and 8 duplexes (floors 27–28 and 29–30): Gujarat RERA, 108 homes. The roof pergola is drawn from the developer’s render.' + GEO_NOTE + SURR)
    return base_cfg('belrosa', p, base, fr, T, units, st, round(125 / 32, 2), note, extra=dict(height=125))

# ------------------------------------------------------------------ The North Park: every registered phase, villa by villa
NP = [('997', 'Phases 2 & 3', 'PR/GJ/GANDHINAGAR/GANDHINAGAR/Ahmedabad Urban Development Authority/RAA01824/A1R/EX1/240726/300627', 42, 40,
       '4 BHK (types C1, C2, M2), 5 BHK (C1, C2, M2) and 6 BHK (C1, C2)', '304.80 – 1,017.33 sq m (3,281 – 10,950 sq.ft.)'),
      ('1106', 'Phases 4 & 7', 'PR/GJ/AHMEDABAD/AHMEDABAD CITY/Ahmedabad Urban Development Authority/RAA01901/A1R/EX1/270726/300627', 50, 36,
       '4 BHK (types C1, C2, M1, M2)', '304.80 – 551.01 sq m (3,281 – 5,931 sq.ft.)'),
      ('1110', 'Phase 5', 'PR/GJ/GANDHINAGAR/GANDHINAGAR/Ahmedabad Urban Development Authority/RAA00268/A1R/EX1/240726/300627', 38, 38,
       '4 BHK (35 of type A, which are joined in rows, and types C1, M2)', '276.07 – 384.62 sq m (2,972 – 4,140 sq.ft.)'),
      ('1104', 'Phase 6', 'PR/GJ/GANDHINAGAR/AHMEDABAD CITY/Ahmedabad Urban Development Authority/RAA00303/A1R/EX1/240726/300627', 36, 18,
       '5 BHK (types M1, C2) and 6 BHK (C1, C2)', 'up to 746.22 sq m (8,032 sq.ft.)'),
      ('9208', 'Phase 8 · The North Park', 'PR/GJ/AHMEDABAD/GANDHINAGAR/Ahmedabad Urban Development Authority/RAA06343/A1R/EX1/100726/300627', 33, 10,
       '4 BHK villas (type A; Adani Realty plans B, C, C1, D, E)', '313.53 – 352.22 sq m (3,374.81 – 3,791.26 sq.ft.)')]

def north_park(p, base):
    fp = json.load(open(os.path.join(HERE, 'sat', 'npm_all_fp.json')))
    allpts = [q for k, *_ in NP for q in POLYS[k]]
    import sitegeo as SG
    P = [xy(*q) for q in allpts]; rot, w, d, (cx, cy) = SG.mbr(P); fr = (cx, cy, rot)
    # centre the view on the villas themselves (centre of the mapped villas), keeping the plot orientation
    V = [xy(*q) for f in fp if f.get('ph') in {k for k, *_ in NP} for q in f['poly']]
    r_ = math.radians(rot); c_, s_ = math.cos(r_), math.sin(r_)
    us = [(x - cx) * c_ + (y - cy) * s_ for x, y in V]; vs = [-(x - cx) * s_ + (y - cy) * c_ for x, y in V]
    mu, mv = sum(us) / len(us), sum(vs) / len(vs)        # centre of mass of the built villas
    cx, cy = cx + mu * c_ - mv * s_, cy + mu * s_ + mv * c_; fr = (cx, cy, rot)
    units = {}; T = []; ctx = []; clear = []
    lvl = dict(label='Ground floor', kind='A', note='Ground floor: living, dining, kitchen, a bedroom and the garden (Adani Realty villa plans)')
    for k, name, reg, n, booked, types, size in NP:
        units[k] = u(f'The North Park · {name}', name, [['Villas', types], ['Villa size (RERA carpet)', size], ['Registered', f'{n} villas · {booked} booked (Gujarat RERA progress report)'],
                                                       ['Built as', 'Ground + 2 floors with a lift; second floor partly a terrace'], ['RERA', reg]], perFloor='1 villa')
        pl = [[round(a, 1), round(b, 1)] for a, b in (loc(fr, *q) for q in POLYS[k])]
        ctx.append(dict(t='line', p=pl, c='#c9a962', z=0.8)); clear.append(pl)
    st = [lvl, dict(label='First floor', kind='A', note='Bedrooms with dressing areas and balconies'), dict(label='Second floor', kind='A', note='Bedroom suite, family lounge and open terrace')]
    i = 0
    counts = {k: 0 for k, *_ in NP}
    for f in fp:
        ph = f.get('ph')
        if ph not in counts: continue
        counts[ph] += 1; i += 1
        name = next(x[1] for x in NP if x[0] == ph)
        rowlike = f['A'] > 900
        t = tower(fr, f'V{i}', f'{name} · {"villa row" if rowlike else "villa"} {counts[ph]}', f['poly'], st, ph, nolabel=True, crown=dict(h=0.7))
        sc = 0.72      # the second floor covers part of the plan; the rest is an open terrace (Adani Realty plans)
        t['tiers'] = [dict({'from': 2}, pts=[[round(a * sc, 2), round(b * sc, 2)] for a, b in t['pts']])]
        T.append(t)
    # villas standing on the map between / beside the registered phases (no RERA record ties them to a phase): grey, not clickable
    extra = 0
    for f in fp:
        if f.get('ph') or f['A'] < 150 or f['A'] > 1000: continue
        cxp = sum(q[0] for q in f['px']) / len(f['px']) if isinstance(f['px'][0], list) else f['px'][0]
        if cxp < 900: continue          # far-west cluster: township service buildings, not villas
        pl = [[round(a_, 1), round(b_, 1)] for a_, b_ in (loc(fr, *q) for q in f['poly'])]
        ctx.append(dict(t='prism', p=pl, h=9.5, c='#9aa3ae')); extra += 1
    # phase names floating over each phase
    for k, name, *_ in NP:
        pl = [loc(fr, *q) for q in POLYS[k]]
        cxp = sum(a for a, b in pl) / len(pl); cyp = sum(b for a, b in pl) / len(pl)
        ctx.append(dict(t='label', text=name, x=round(cxp, 1), y=round(cyp, 1), z=34, size=13))
    built = sum(counts.values())
    note = ('The North Park: every villa phase registered on Gujarat RERA, 199 villas on 174,439 sq m (43.1 acres) of registered land: North Park phases 2 & 3 (42 villas), '
            '4 & 7 (50), 5 (38) and 6 (36), and The North Park, phase 8 (33). Gold lines are the registered phase boundaries (Gujarat RERA map service). '
            f'Villas: the {built} buildings standing today, with footprints as drawn on Google Maps; plots with no building yet are left empty, and the phase-5 type A villas are joined in rows. '
            f'Grey villas ({extra}) stand on the map beside the registered phases, but no RERA record ties them to a phase (they may be the earlier phase 1, completed before RERA began), so they are shown without details. '
            'Each villa is ground + 2 floors (Adani Realty villa plans), the second floor partly an open terrace. Sizes and villa types per phase are from the Gujarat RERA register.' + SURR)
    plotPoly = [[round(a, 1), round(b, 1)] for a, b in (loc(fr, *q) for q in POLYS['9208'])]
    xs = [t['x'] + a for t in T for a, b in t['pts']]; ys = [t['y'] + b for t in T for a, b in t['pts']]
    geo = dict(base['geo']) if base else {}
    geo.update(name='GEO_SHANTIGRAM', file='assets/geo-shantigram.js', x=round(cx, 1), y=round(cy, 1), rot=round(rot, 1), radius=900)
    cfg = dict(project=p['name'], interest=p['label'], floorH=3.4, stack=st, towers=T, units=units, plot=dict(w=round(max(xs) - min(xs), 1), d=round(max(ys) - min(ys), 1)),
               geo=geo, kind='residential', startFloor='First floor', enqLabel='Enquire about this villa', note=note, plotPoly=plotPoly, context=ctx, clear=clear,
               camR=760, camY=6, camTurn=0.57, camPh=0.9, perFloorLabel='Villas', villas=True)
    return cfg

BUILD = {'aster-neo': aster, 'amogha': amogha, 'embrace': embrace, 'elysium-novus': elysium, 'greenfield': greenfield, 'ambrosia': ambrosia,
         'paarijat': paarijat, 'shilp-skyline': skyline, 'belrosa': belrosa, 'north-park': north_park}

RSH = json.load(open(os.path.join(HERE, 'adani', 'rera_sh.json')))

def attach_nos(pid, cfg):
    """flat numbers registered on each floor of each tower (Gujarat RERA unit lists), so the model shows one block per flat"""
    import re, copy
    if pid == 'north-park': return
    keys = [RERA_KEY[pid]] + (['10307'] if pid == 'aster-neo' else [])
    B = {}
    for k in keys:
        b = RSH.get(k, {}).get('blk') or {}
        for name, L in b.items():
            if isinstance(L, list): B[(k, name)] = L
    if not B: return
    for t in cfg['towers']:
        me = t['label'].split('·')[0].strip().split()[-1].upper()
        mine = []
        for (k, name), L in B.items():
            parts = [x.strip().upper().replace('BLOCK-', '').replace('BLOCK', '').strip() for x in re.split(r'[+&]', name)]
            if me not in parts: continue
            for u_ in L:
                m = re.match(r'\s*([A-Z])\s*[- ]\s*(\d+)\s*$', u_)
                if m and m.group(1) != me: continue
                n = int(re.findall(r'\d+', u_)[-1]); mine.append((n // 100, re.sub(r'\s+', ' ', u_.strip())))
        if not mine: continue
        by = {}
        for f, u_ in mine: by.setdefault(f, []).append(u_)
        st = copy.deepcopy(t.get('stack') or cfg['stack'])
        hit = 0
        for L in st:
            if L.get('kind') not in ('A', 'P'): continue
            m = re.search(r'(\d+)', L['label'])
            f = int(m.group(1)) if m else (0 if L['label'].startswith('Ground') else None)
            if f in by:
                L['nos'] = sorted(by[f], key=lambda x: int(re.findall(r'\d+', x)[-1])); hit += 1
        if hit: t['stack'] = st

def build(pid, p, base):
    cfg = BUILD[pid](p, base or {'geo': {}})
    attach_nos(pid, cfg)
    cfg['camStay'] = True          # open on the whole site
    return cfg
