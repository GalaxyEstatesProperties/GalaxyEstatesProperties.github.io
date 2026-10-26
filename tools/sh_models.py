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
ASTER_SLABS = {   # slab -> (towers in order along the slab, end of the slab with flats 1 and 2, outer face with flats 1 and 4), read off Adani Realty's master layout
  'AB': ('AB', 'W', 'S'), 'CD': ('CD', 'W', 'S'), 'GH': ('GH', 'NE', 'NW'), 'IJ': ('IJ', 'SE', 'NE'), 'KLM': ('KLM', 'SE', 'NE')}

MROOM = dict(label='Roof', kind='M', use='Lift machine room and staircase head above the roof')

def aster_towers(fr):
    """every Aster / Aster NEO tower as on the typical floor plan: four 2 BHK flats round a central lift core (01 and 04 on the outer face,
    02 and 03 on the courtyard face, 01 / 02 at one end and 03 / 04 at the other, exactly as numbered on the master layout); the core
    is set back from both faces, which gives the recesses seen on the renders"""
    import shgeom as SG_, numpy as np
    spec = json.load(open(os.path.join(HERE, 'sat', 'spec_aster.json')))
    dirs = {'W': (-1, 0), 'S': (0, 1), 'NE': (1, -1), 'NW': (-1, -1), 'SE': (1, 1)}   # plan pixels: x right, y down
    out = []
    for key, (letters, end12, outer) in ASTER_SLABS.items():
        B = np.array(spec['polys'][key], float); c = B.mean(0)
        e1, e2 = B[1] - B[0], B[2] - B[1]
        Lv, Sv = (e1, e2) if np.linalg.norm(e1) >= np.linalg.norm(e2) else (e2, e1)
        d12 = np.array(dirs[end12], float); dout = np.array(dirs[outer], float)
        if Lv @ d12 < 0: Lv = -Lv              # Lv: from the 3/4 end to the 1/2 end
        if Sv @ dout < 0: Sv = -Sv             # Sv: from the courtyard face to the outer face
        n = len(letters)
        order = sorted(range(n), key=lambda i: (i + 0.5) / n)
        # towers along the slab, ordered as printed (A west of B, G south-west of H, I north-west of J, K..M north-west to south-east)
        cents = [c + Lv * ((i + 0.5) / n - 0.5) for i in range(n)]
        pick = {'AB': lambda q: q[0], 'CD': lambda q: q[0], 'GH': lambda q: q[0], 'IJ': lambda q: q[0], 'KLM': lambda q: q[0]}[key]
        cents = sorted(cents, key=pick)
        for L_, cc in zip(letters, cents):
            P = lambda t, s_: list(map(float, cc + Lv / n * (t - 0.5) + Sv * (s_ - 0.5)))
            R = lambda t0, t1, s0, s1: [P(t0, s0), P(t1, s0), P(t1, s1), P(t0, s1)]
            cells = {'03': R(0, 0.40, 0, 0.5), '04': R(0, 0.40, 0.5, 1), '02': R(0.60, 1, 0, 0.5), '01': R(0.60, 1, 0.5, 1)}
            core = R(0.40, 0.60, 0.08, 0.92)       # lift lobby + stair, 0.19 of the length on the plan, set back ~1 m from both faces
            outline = [P(0, 0), P(0.40, 0), P(0.40, 0.08), P(0.60, 0.08), P(0.60, 0), P(1, 0), P(1, 1), P(0.60, 1), P(0.60, 0.92), P(0.40, 0.92), P(0.40, 1), P(0, 1)]
            out.append((L_, {k: SG_.plan2ll('aster', v) for k, v in cells.items()}, SG_.plan2ll('aster', core), SG_.plan2ll('aster', outline)))
    return out

def aster(p, base):
    fr = frame('aster-neo', POLYS['10307'])
    T = []
    for i, (L_, cells, core, outline) in enumerate(sorted(aster_towers(fr), key=lambda x: 'ABGHCDIJKLM'.index(x[0]))):
        neo = L_ in 'ABGH'
        st = ground() + homes(1, 22, 4)
        for Lv in st[1:]:
            f_ = int(Lv['label'].split()[-1]); Lv['nos'] = [f'{L_}-{f_}{k}' for k in ('01', '02', '03', '04')]
        t = tower(fr, f'T{i+1}', f'Tower {L_}' + (' · Aster NEO' if neo else ' · Aster'), outline, st, 'neo' if neo else 'aster')
        t['plan'] = dict(cells=[[[round(a_ - t['x'], 2), round(b_ - t['y'], 2)] for a_, b_ in (loc(fr, *q) for q in cells[k])] for k in ('01', '02', '03', '04')])
        t['nolift'] = True
        T.append(t)
        k_ = tower(fr, f'K{i+1}', f'Tower {L_} lift core', core, [dict(label=Lv['label'], kind='M', use='Lift lobby, two lifts and the staircase (Adani Realty typical floor plan)') for Lv in st] + [MROOM], 'neo' if neo else 'aster',
                   nolabel=True, solid=True, nolift=True, crown=dict(type='cap', h=1.5))
        T.append(k_)
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
            'floors and homes per floor from the Gujarat RERA unit lists (4 homes on every floor from 1 to 22). Each tower is drawn as on the typical floor plan: '
            'four 2 BHK flats round a central lift core that rises above the roof, flats 01 and 04 on the outer face and 02 and 03 on the courtyard face, '
            'with 01 / 02 at the end shown on the master layout (unit numbers <tower>-<floor><flat>, as in the RERA unit list).' + GEO_NOTE +
            ' The gold area is Aster NEO’s registered plot; the thin gold line is Aster phase 1’s.' + SURR)
    ph1 = [[round(a, 1), round(b, 1)] for a, b in (loc(fr, *q) for q in POLYS['10307'])]
    cfg = base_cfg('aster-neo', p, base, fr, T, units, st, 3.1, note, extra=dict(context=[dict(t='line', p=ph1, c='#c9a962', z=0.8)], clear=[ph1]))
    cfg['perFloor'] = '4 homes'
    return cfg

def amogha(p, base):
    g = GEOM['amogha']; fr = frame('amogha')
    st = ground('Double-height entrance foyer and lobby') + homes(1, 14, 4)
    BL = wing_blocks(fr, ['amoAB', 'amoCD', 'amoEF', 'amoGH'], 'amo')
    T = []
    for i, W in enumerate('ABCDEFGH'):
        b = BL[W]; ks = list(b['cells'])
        stW = ground('Double-height entrance foyer and lobby') + homes(1, 14, 4)
        for Lv in stW[1:]:
            f_ = int(Lv['label'].split()[-1]); Lv['nos'] = [f'{W}-{f_}{k}' for k in ks]
        t = _local_tower(f'T{i+1}', f'Wing {W}', b['outline'], stW, 'all', nolift=True)
        t['plan'] = dict(cells=[[[round(a_ - t['x'], 2), round(b_ - t['y'], 2)] for a_, b_ in b['cells'][k]] for k in ks])
        T += [t, core_tower(f'K{i+1}', f'Wing {W} lift core', b['core'], t, 'all')]
    units = {'all': u('Amogha · 3 BHK apartments', '3 BHK',
                      [['Size', '624.09 – 776.40 sq.ft. RERA carpet (Gujarat RERA: 57.98 – 72.13 sq m); Adani Realty’s unit plans (types A, B, C) list 812.35 – 826.13 sq.ft.'],
                       ['Wings', '8 wings (A–H) in joined pairs · ground + 14 floors · 4 homes per floor (Gujarat RERA: 448 homes)'],
                       ['Status', 'Completed (Adani Realty)'], ['RERA', 'PR/GJ/AHMEDABAD/DASKROI/AUDA/RAA08011/EX1/260224/280225']], perFloor='4 homes')}
    note = ('Amogha: 8 wings (A–H) built as four joined pairs, ground + 14 floors, 448 homes (Gujarat RERA: 112 homes in each pair, unit numbers on floors 1 to 14). '
            'Wing letters, positions and flat numbers as printed on Adani Realty’s master layout (e.g. wing C: 1 and 2 on the row away from the 34.5 m road, 4 and 3 on the road side; '
            'each pair of wings is built round an open court with its own lift core); the clubhouse is drawn from the same plan.' + GEO_NOTE + SURR)
    return base_cfg('amogha', p, base, fr, T, units, st, 3.1, note, extra=dict(context=ctx_items(fr, g.get('ctx'))))

def embrace(p, base):
    g = GEOM['embrace']; fr = frame('embrace')
    st4 = ground('Stilt: entrance lobby and parking') + homes(1, 14, 4)
    stC = ground('Stilt: entrance lobby; amenities next to the tower') + homes(1, 11, 2) + [dict(label='Floors 12–13 (penthouses)', kind='P', levels=2, unit='ph', note='2 duplex penthouses (lower level on floor 12, upper level on floor 13)')]
    import shgeom as SG_, copy as _cp
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    D = json.load(open(os.path.join(HERE, 'sat', 'plan_cells.json')))
    def place_ll(P, bbox, rect, **kw):
        return SG_.plan2ll('embrace', SG_.place([[(x - bbox[0]) / (bbox[2] - bbox[0]), (y - bbox[1]) / (bbox[3] - bbox[1])] for x, y in P], rect, **kw))
    simp = lambda P, tol: [list(q) for q in Polygon(P).buffer(0).simplify(tol).exterior.coords[:-1]]
    # towers A-B and D-E: the drawing turned upright (left tower of the drawing at the bottom); numbering is the same whichever way it is turned (each tower is the other turned half round)
    pairs = {'Tower A': ('L', (1085, 178, 1335, 680)), 'Tower B': ('R', (1085, 178, 1335, 680)), 'Tower E': ('L', (215, 183, 465, 688)), 'Tower D': ('R', (215, 183, 465, 688))}
    T = []
    for i, lab in enumerate(['Tower A', 'Tower B', 'Tower C', 'Tower D', 'Tower E']):
        if lab == 'Tower C':
            d = D['emC']; bb = [150, 125, 1401, 914]; rect = (565, 98, 830, 250); kw = {}; side = 'C'; core_i = 0; st = _cp.deepcopy(stC); fl = range(1, 12); typ = 'c'
        else:
            d = D['emAB']; bb = [102, 185, 1485, 886]; side, rect = pairs[lab]; kw = dict(rot90=True); core_i = 0 if side == 'L' else 1; st = _cp.deepcopy(st4); fl = range(1, 15); typ = 'all'
        # tower C: the master layout draws it about 13 m further towards the plot edge than it stands; it is placed on its roof in the satellite image
        sh = (lambda la, lo: (la + 6.0 / 111320, lo - 12.0 / (111320 * math.cos(math.radians(la))))) if lab == 'Tower C' else (lambda la, lo: (la, lo))
        cells = {k[-1]: simp([loc(fr, *sh(*q)) for q in place_ll(P, bb, rect, **kw)], 0.3) for k, P in d['cells'].items() if k[0] == side}
        core = [loc(fr, *sh(*q)) for q in place_ll(d['core_rects'][core_i], bb, rect, **kw)]
        U = unary_union([Polygon(P).buffer(0.3, join_style=2) for P in list(cells.values()) + [core]]).buffer(-0.3, join_style=2).simplify(0.35)
        if U.geom_type != 'Polygon': U = max(U.geoms, key=lambda g_: g_.area)
        ks = sorted(cells)
        W = lab.split()[-1]
        for Lv in st:
            if Lv['kind'] == 'A' and int(Lv['label'].split()[-1]) in fl:
                f_ = int(Lv['label'].split()[-1]); Lv['nos'] = [f'{W}-{f_}{k.zfill(2)}' for k in ks]      # as in the Gujarat RERA unit list (A-101 ...)
        t = _local_tower(f'T{i+1}', lab, [list(q) for q in U.exterior.coords[:-1]], st, typ, nolift=True)
        cl = [[[round(a_ - t['x'], 2), round(b_ - t['y'], 2)] for a_, b_ in cells[k]] for k in ks]
        for Lv in st:
            if Lv.get('nos'): Lv['plan'] = dict(cells=cl)
            if Lv['kind'] == 'P' and lab == 'Tower C': Lv['nos'] = ['C-1201', 'C-1202']     # duplex penthouses (Gujarat RERA), positions not drawn
        T += [t, core_tower(f'K{i+1}', f'{lab} lift core', core, t, typ)]
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
            'Adani Realty describes the towers as “13 and 14 floors”; the floor counts here are those that hold the registered homes. '
            'Each flat is where Adani Realty’s typical-floor plans place it, labelled with the number printed at its door (1–4 in A, B, D, E round the lift lobby and the open void between each pair; '
            '1 and 2 in C), which are the last two digits of the Gujarat RERA unit numbers (A-101 … E-1404, C-101 … C-1102).' + GEO_NOTE + SURR)
    return base_cfg('embrace', p, base, fr, T, units, st4, 3.2, note)

EN_RECTS = {'C': ('en_fp_cdef', 'L', (963, 548, 1216, 682)), 'D': ('en_fp_cdef', 'R', (963, 548, 1216, 682)),
            'E': ('en_fp_cdef', 'R', (963, 213, 1216, 345)), 'F': ('en_fp_cdef', 'L', (963, 213, 1216, 345)),
            'G': ('en_fp_g', '', (690, 225, 895, 375)), 'J': ('en_fp_j', '', (1178, 393, 1310, 513))}

def elysium_blocks(fr):
    """each Elysium Novus block from Adani Realty's typical floor plans: the flats as numbered on the plans (C / F: 101 top-left, 102 top inner,
    103 bottom inner, 104 bottom-left; D / E: 103 top inner, 104 top-right, 102 bottom inner, 101 bottom-right; J: 104 / 101 top, 103 / 102 bottom;
    G: 106 / 105 / 104 left wing, 103 / 102 / 101 right wing), the lift and stair core, and the open central void between the C+D and E+F pairs.
    The block outline is the union of its flats and core, so the void stays open."""
    import shgeom as SG_
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    C = json.load(open(os.path.join(HERE, 'sat', 'en_cells.json')))
    toL = lambda name, rect, P: [loc(fr, *q) for q in SG_.plan2ll('ely', SG_.place(P, rect))]
    out = {}
    for B, (name, side, rect) in EN_RECTS.items():
        d = C[name]
        simp = lambda P, tol: [list(q) for q in Polygon(P).buffer(0).simplify(tol).exterior.coords[:-1]]
        cells = {k[-2:]: simp(toL(name, rect, P), 0.45) for k, P in d['cells'].items() if k.startswith(side) or not side}
        core = simp(next(toL(name, rect, P) for k, P in d['cores'].items() if (k.endswith('0') if side != 'R' else k.endswith('1'))), 0.3)
        U = unary_union([Polygon(P).buffer(0.25, join_style=2) for P in list(cells.values()) + [core]]).buffer(-0.25, join_style=2).simplify(0.45)
        if U.geom_type != 'Polygon': U = max(U.geoms, key=lambda g_: g_.area)
        out[B] = dict(cells={k: cells[k] for k in sorted(cells)}, core=core, outline=[list(p) for p in U.exterior.coords[:-1]])
    return out

def _local_tower(tid, label, P, stack, typ, **k):
    """tower() for an outline already in plot metres"""
    A = sum(P[i][0] * P[i - 1][1] - P[i - 1][0] * P[i][1] for i in range(len(P))) / 2
    if A > 0: P = P[::-1]
    cx = sum(p[0] for p in P) / len(P); cy = sum(p[1] for p in P) / len(P)
    pts = [[round(a - cx, 2), round(b - cy, 2)] for a, b in P]
    us = [a for a, b in pts]; vs = [b for a, b in pts]
    t = dict(id=tid, label=label, x=round(cx, 2), y=round(cy, 2), w=round(max(us) - min(us), 1), d=round(max(vs) - min(vs), 1), ang=0, pts=pts, stack=stack, type=typ)
    t.update(k); return t

def plan_cells(fr, t, key, conv, levels, nos_pfx=None):
    """flats and lift core from a typical floor plan (plan_cells.py -> sat/plan_cells.json, plan pixels; conv: plan pixels -> lat/lon).
    Only the floors the plan covers get the cells; the rest stay indicative. Returns the core outline in plot metres."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    d = json.load(open(os.path.join(HERE, 'sat', 'plan_cells.json')))[key]
    toL = lambda P: [loc(fr, *q) for q in conv(P)]
    simp = lambda P, tol: [list(q) for q in Polygon(P).buffer(0).simplify(tol).exterior.coords[:-1]]
    ks = sorted(d['cells'])
    cells = [[[round(a - t['x'], 2), round(b - t['y'], 2)] for a, b in simp(toL(d['cells'][k]), 0.35)] for k in ks]
    for L in t['stack']:
        if L['label'] in levels: L['plan'] = dict(cells=cells)
    core = unary_union([Polygon(toL(P)).buffer(0.05) for P in d['cores']]).buffer(-0.05)
    if core.geom_type != 'Polygon': core = max(core.geoms, key=lambda g_: g_.area)
    return [list(q) for q in core.simplify(0.2).exterior.coords[:-1]]

def core_tower(tid, label, P, t, typ):
    return _local_tower(tid, label, P, [dict(label=L['label'], kind='M', use='Lifts, lobby and staircase (developer’s typical floor plan)', **({'levels': L['levels']} if L.get('levels') else {}), **({'h': L['h']} if L.get('h') else {}))
                                         for L in t['stack']] + [MROOM], typ, nolabel=True, solid=True, nolift=True, crown=dict(type='cap', h=1.5))

def wing_blocks(fr, keys, fit):
    """wings cut from a master layout / floor plan (plan_cells.py): flats as numbered on the drawing (cell names '<wing><nn>'),
    each wing's lift core, and the outline = flats + core, so open courts between wings stay open"""
    import shgeom as SG_
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    D = json.load(open(os.path.join(HERE, 'sat', 'plan_cells.json')))
    toL = lambda P: [loc(fr, *q) for q in SG_.plan2ll(fit, P)]
    simp = lambda P, tol: [list(q) for q in Polygon(P).buffer(0).simplify(tol).exterior.coords[:-1]]
    out = {}
    for key in keys:
        d = D[key]; wings = sorted({k[:-2] for k in d['cells']})
        for W in wings:
            cells = {k[-2:]: simp(toL(P), 0.35) for k, P in d['cells'].items() if k[:-2] == W}
            cx = sum(sum(p[0] for p in P) / len(P) for P in cells.values()) / len(cells); cy = sum(sum(p[1] for p in P) / len(P) for P in cells.values()) / len(cells)
            cores = [toL(P) for P in d['core_rects']]
            core = min(cores, key=lambda P: (sum(p[0] for p in P) / len(P) - cx) ** 2 + (sum(p[1] for p in P) / len(P) - cy) ** 2)
            U = unary_union([Polygon(P).buffer(0.3, join_style=2) for P in list(cells.values()) + [core]]).buffer(-0.3, join_style=2).simplify(0.4)
            if U.geom_type != 'Polygon': U = max(U.geoms, key=lambda g_: g_.area)
            out[W] = dict(cells={k: cells[k] for k in sorted(cells)}, core=core, outline=[list(p) for p in U.exterior.coords[:-1]])
    return out

def elysium(p, base):
    fr = frame('elysium-novus')
    BL = elysium_blocks(fr)
    T = []
    for i, B in enumerate('CDEFGJ'):
        b = BL[B]; ks = list(b['cells']); n = len(ks)
        st = ground('Stilt parking and entrance lobby (hollow plinth); two basements of parking below') + homes(1, 14, n)
        st[0]['h'] = 3.15                                    # AMC fire-safety opinion: hollow plinth / ground floor 3.15 m, floors 1-14 2.96 m
        for Lv in st[1:]:
            f_ = int(Lv['label'].split()[-1]); Lv['nos'] = [f'{B}-{f_}{k}' for k in ks]; Lv['h'] = 2.96
        typ = 'g' if B == 'G' else 'j' if B == 'J' else 'cdef'
        t = _local_tower(f'T{i+1}', f'Block {B}', b['outline'], st, typ, nolift=True)
        t['plan'] = dict(cells=[[[round(a_ - t['x'], 2), round(b_ - t['y'], 2)] for a_, b_ in b['cells'][k]] for k in ks])
        T.append(t)
        T.append(_local_tower(f'K{i+1}', f'Block {B} lift core', b['core'],
                              [dict(label=Lv['label'], kind='M', h=Lv['h'], use='Lifts, lobby and staircase (Adani Realty typical floor plan)') for Lv in st] + [MROOM], typ,
                              nolabel=True, solid=True, nolift=True, crown=dict(type='cap', h=1.5)))
    sizes = ['Sizes in the project', '2 BHK: 717.42 sq.ft. · 3 BHK: 973.93 – 1,103.63 sq.ft. (Adani Realty); RERA carpet 668.44 – 1,016 sq.ft. (Gujarat RERA 62.10 – 94.39 sq m)']
    rera = ['RERA', 'PR/GJ/AHMEDABAD/AHMEDABAD CITY/Ahmedabad Urban Development Authority/RAA14729/270125/311228']
    units = {'cdef': u('Elysium Novus · blocks C, D, E, F', '3 BHK (C–F)', [['Plans', 'Types 1 and 2 (Adani Realty), 4 homes per floor; blocks C+D and E+F are joined pairs round an open central void'], sizes, rera], perFloor='4 homes'),
             'g': u('Elysium Novus · block G', 'Block G', [['Plans', 'Types 3 and 4 (Adani Realty): two angled wings round the core, 6 homes per floor'], sizes, rera], perFloor='6 homes'),
             'j': u('Elysium Novus · block J', 'Block J', [['Plans', 'Type 5 (Adani Realty): H-shaped block, 4 homes per floor'], sizes, rera], perFloor='4 homes')}
    note = ('Elysium Novus: blocks C+D and E+F are joined pairs built round an open central void, G has two angled wings with 6 homes per floor and J is H-shaped with 4, '
            'each drawn from Adani Realty’s typical-floor plans with the flats where the plans number them (C and F: 101 top-left, 102 top inner, 103 bottom inner, 104 bottom-left; '
            'D and E mirrored; J: 104 and 101 at the top, 103 and 102 below; G: 106, 105, 104 on the left wing and 103, 102, 101 on the right). '
            'Lift cores rise above the roofs. All blocks are ground (stilt) + 14 floors (Gujarat RERA unit numbers <block>-101 to 1406; 364 homes). '
            'Floor heights are from the Ahmedabad fire-safety opinion filed on Gujarat RERA: hollow plinth / ground floor 3.15 m and 2.96 m for each of floors 1 to 14 '
            '(so the roof of floor 14 is 44.59 m up); the opinion gives 44.95 m from ground level to the top slab for every block, over two basements of parking (3.75 m and 4.65 m).'
            + GEO_NOTE + ' The registered plot outline on the Gujarat RERA map sits slightly north-west of the buildings now under construction; the buildings are placed on the satellite image.' + SURR)
    st4 = ground() + homes(1, 14, 4)
    st4[0]['h'] = 3.15
    for Lv in st4[1:]: Lv['h'] = 2.96
    return base_cfg('elysium-novus', p, base, fr, T, units, st4, 2.96, note, extra=dict(height=44.95, hSrc='AMC fire-safety opinion filed on Gujarat RERA'))

def greenfield(p, base):
    g = GEOM['greenfield']; fr = frame('greenfield')
    st = ground('Ground floor amenities (gym, mini theatre, library and more, per the developer’s ground-floor plan); two basements of parking below') + homes(1, 19, 4) + \
         [dict(label='Floors 20–21 (penthouses)', kind='P', levels=2, unit='ph', note='4 duplex penthouses: lower level on floor 20, upper level on floor 21')]
    st[0]['h'] = 3.62                                        # AMC fire-safety opinion (every block): ground 3.62 m, floors 1-20 3.15 m, floor 21 3.23 m; 69.85 m to the top slab
    for Lv in st[1:-1]: Lv['h'] = 3.15
    st[-1].update(h=6.38, hs=[3.15, 3.23])
    import copy as _cp, shgeom as SG_
    gfb = json.load(open(os.path.join(HERE, 'sat', 'gf_fp2_outline.json')))['bbox']
    T = []
    for i, lab in enumerate(['Block A', 'Block B', 'Block C']):
        t = tower(fr, f'T{i+1}', lab, g['towers'][lab], _cp.deepcopy(st), 'all', nolift=True)
        conv = lambda P, lab=lab: SG_.plan2ll('gf', SG_.place([[(x - gfb[0]) / (gfb[2] - gfb[0]), (y - gfb[1]) / (gfb[3] - gfb[1])] for x, y in P], SG_.GF_RECTS[lab], **SG_.GF_TURN))
        core = plan_cells(fr, t, 'gf', conv, {f'Floor {f}' for f in range(1, 20)})
        T += [t, core_tower(f'K{i+1}', f'{lab} lift core', core, t, 'all')]
    rera = ['RERA', 'PR/GJ/AHMEDABAD/AHMEDABAD CITY/AUDA/RAA14879/250225/311229']
    units = {'all': u('Greenfield · 3 BHK apartments', '3 BHK',
                      [['Size', 'From 1,277.89 sq.ft. RERA carpet; e.g. unit 101 (first floor, blocks A–C): 1,379 sq.ft. carpet + 110 sq.ft. terrace'], ['Price', 'From ₹1.73 Cr*, all inclusive'], rera], perFloor='4 homes'),
             'ph': u('Greenfield · 4 BHK duplex penthouses', '4 BHK PH', [['Size', 'Up to 2,163.33 sq.ft. RERA carpet'], ['Levels', 'Lower level on floor 20, upper level on floor 21 (units 2001–2004)'], rera], perFloor='4 penthouses')}
    note = ('Greenfield: three blocks in a row, Block A nearest the 34.5 m road at the entrance, then B and C, as labelled on the developer’s ground-floor plan and on the key plans '
            'of Adani Realty’s unit plans. Ground + 21 floors: 4 apartments per floor on floors 1–19 and 4 duplex penthouses on floors 20–21 (Gujarat RERA: 80 homes per block, unit numbers 101–2004). '
            'On floors 1–19 each flat sits where the developer’s first-floor and typical-floor plans number it (x01 and x02 on one side of the lift core, x03 and x04 on the other; the drawing is turned to its compass rose); '
            'the penthouse floors have no published plan, so their positions are indicative. '
            'Floor heights are from the Ahmedabad fire-safety opinion filed on Gujarat RERA (the same for blocks A, B and C): ground floor 3.62 m, floors 1 to 20 3.15 m each and floor 21 3.23 m, '
            '69.85 m from ground level to the top slab, over two basements of parking (4.20 m and 3.65 m).'
            + GEO_NOTE + SURR)
    return base_cfg('greenfield', p, base, fr, T, units, st, 3.15, note, extra=dict(height=69.85, hSrc='AMC fire-safety opinion filed on Gujarat RERA'))

def ambrosia(p, base):
    g = GEOM['ambrosia']; fr = frame('ambrosia')
    st = ground() + homes(1, 13, 4)
    BL = wing_blocks(fr, ['ambA', 'ambB', 'ambC'], 'amb')
    T = []
    for i, W in enumerate('ABC'):
        b = BL[W]; ks = list(b['cells'])
        stW = ground() + homes(1, 13, 4)
        for Lv in stW[1:]:
            f_ = int(Lv['label'].split()[-1]); Lv['nos'] = [f'{W}-{f_}{k}' for k in ks]      # flat k on the layout = unit x0k in the Gujarat RERA list
        t = _local_tower(f'T{i+1}', f'Wing {W}', b['outline'], stW, 'all', nolift=True)
        t['plan'] = dict(cells=[[[round(a_ - t['x'], 2), round(b_ - t['y'], 2)] for a_, b_ in b['cells'][k]] for k in ks])
        T += [t, core_tower(f'K{i+1}', f'Wing {W} lift core', b['core'], t, 'all')]
    units = {'all': u('Ambrosia · 4 BHK #Uberments', '4 BHK',
                      [['Types', '4 BHK Classic and 4 BHK Deluxe (Adani Realty unit plans)'], ['Size', '1,671.60 – 1,902.19 sq.ft. RERA carpet (Adani Realty)'],
                       ['Price', 'From ₹2.49 Cr*, all inclusive'], ['RERA', 'PR/GJ/GANDHINAGAR/GANDHINAGAR/AUDA/RAA10833/201022']], perFloor='4 homes')}
    note = ('Ambrosia: wings A, B and C around a central garden, B at the back and A and C on either side, as on Adani Realty’s master layout; each wing is the X-shaped plan of its typical floor. '
            'Ground + 13 floors, 4 homes per floor (Gujarat RERA: 52 homes per wing, 156 in all). Each flat is where the complex layout numbers it (1–4 in every wing, two flats either side of '
            'the cross-shaped lift lobby, with open courts between them), matching the Gujarat RERA unit numbers A-101 … C-1304.' + GEO_NOTE + SURR)
    return base_cfg('ambrosia', p, base, fr, T, units, st, 3.2, note)

def paarijat(p, base):
    g = GEOM['paarijat']; fr = frame('paarijat', [q for ll in g['towers'].values() for q in ll])
    st = ground('Parking and society amenity (hollow plinth); one basement of parking below') + homes(1, 14, 4)
    st[0]['h'] = 3.15                                        # AMC fire-safety opinion (both blocks): ground 3.15 m, floors 1-14 2.975 m; 44.95 m to the top slab
    for Lv in st[1:]: Lv['h'] = 2.975
    import copy as _cp, shgeom as SG_
    T = []
    for i, lab in enumerate(['Block A', 'Block B']):
        t = tower(fr, f'T{i+1}', lab, g['towers'][lab], _cp.deepcopy(st), 'all', nolift=True)
        core = plan_cells(fr, t, 'pj' + lab[-1], lambda P: SG_.plan2ll('pj', P), {f'Floor {f}' for f in range(1, 15)})
        T += [t, core_tower(f'K{i+1}', f'{lab} lift core', core, t, 'all')]
    units = {'all': u('Paarijat · 4 BHK premium homes', '4 BHK',
                      [['Size', '1,405 – 1,608 sq.ft. RERA carpet (Adani Realty)'], ['Status', 'BU received (Adani Realty)'], ['RERA', 'PR/GJ/GANDHINAGAR/GANDHINAGAR/AUDA/RAA10759/121022']], perFloor='4 homes')}
    note = ('Paarijat: Block A (towards the main road) and Block B, with the society amenity block between them, from Adani Realty’s floor plan (block names as printed) and its north arrow. '
            'Ground + 14 floors, 4 homes per floor (Gujarat RERA: 56 homes per block), each flat where Adani Realty’s first-floor and typical-floor plans number it '
            '(block B: 01 and 02 at one end, 04 and 03 at the other; block A turned the other way round). The plot outline on the RERA map is a thin strip that does not match the 6,203 sq m registered land, '
            'so the gold outline here is drawn around the buildings. Floor heights are from the Ahmedabad fire-safety opinion filed on Gujarat RERA (the same for both blocks): '
            'hollow plinth / ground floor 3.15 m and 2.975 m for each of floors 1 to 14 (the roof of floor 14 is 44.80 m up); the opinion gives 44.95 m from ground level to the top slab, '
            'over a 5.28 m basement. The society amenity block between them is ground + 1 (3.05 m each), 6.55 m to its top slab.' + GEO_NOTE.replace(' Plot: the boundary registered on the Gujarat RERA map service.', '') + SURR)
    cfg = base_cfg('paarijat', p, base, fr, T, units, st, 2.975, note, extra=dict(context=ctx_items(fr, g.get('ctx')), height=44.95, hSrc='AMC fire-safety opinion filed on Gujarat RERA'))
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
    import copy as _cp, shgeom as SG_
    T = []
    for i, lab in enumerate(['Block A', 'Block B', 'Block C']):
        t = tower(fr, f'T{i+1}', lab, g['towers'][lab], stB if lab == 'Block B' else stAC, 'all')
        pp = tier_pts(fr, t, g['pods'][lab])
        if pp:   # the joined podium (ground + first floor) under each block, then the tower outline from floor 2
            t['tiers'] = [dict({'from': 0}, pts=pp, w=t['w'], d=t['d']), dict({'from': 2}, pts=t['pts'])]
        t['stack'] = _cp.deepcopy(t['stack']); t['nolift'] = True
        core = plan_cells(fr, t, 'sky' + lab[-1], lambda P: SG_.plan2ll('sky', P), {f'Floor {f}' for f in range(2, 22)})
        T += [t, core_tower(f'K{i+1}', f'{lab} lift core', core, t, 'all')]
    rera = ['RERA', 'PR/GJ/AHMEDABAD/AHMEDABAD CITY/Ahmedabad Urban Development Authority/RAA14084/020924/300929']
    units = {'all': u('Skyline · 4 BHK', '4 BHK', [['Size', 'From 1,479.28 sq.ft. (RERA area)'], ['Price', 'From ₹2.23 Cr*, all inclusive'], rera], perFloor='4 homes'),
             'ph': u('Skyline · duplex penthouses', 'Penthouse', [['Size', 'Up to 2,349.76 sq.ft. (RERA area)'], ['Levels', 'Lower level on floor 23, upper on floor 24, in blocks A and C (Adani Realty plans)'], rera], perFloor='2 penthouses')}
    ctx = ctx_items(fr, g.get('ctx'))
    for o in ctx: o.update(h=0.6, z=7.2, c='#5f8f5a')      # landscaped amenity deck (pool, deck, lawn) on top of the podium
    note = ('Skyline: blocks A, B and C stand on a two-level podium (ground and first floor, parking) that joins all three; the amenity deck with pool, deck and lawn is on the podium roof '
            'between A and C, as on Adani Realty’s ground-floor and typical-floor plans. Block A is at the entrance on the 120 ft road. Homes: 4 per floor on floors 2–22; '
            'blocks A and C also have 2 duplex penthouses on floors 23–24 (Gujarat RERA: 86 homes in A, 84 in B, 86 in C; 79 m tall). '
            'On floors 2–21 each flat sits where Shilp’s typical floor plan numbers it (block A: 03 and 04 on one side of the lift core, 02 and 01 on the other; blocks B and C: 01 and 02 on one side, 04 and 03 on the other); '
            'floor 22 and the penthouses have no published plan, so their positions are indicative.' + GEO_NOTE + SURR)
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
