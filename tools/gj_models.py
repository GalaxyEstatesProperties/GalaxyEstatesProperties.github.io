"""3D explorers rebuilt from the developers' official plans for projects outside Shantigram (20 Oct 2026).
Each building outline and flat is cut from the developer's typical-floor plan, georeferenced on current satellite imagery
(the roof outline is fitted to the plan, then moved to the building's foot, since satellite pictures of tall buildings lean)."""
import json, math, os
from contextlib import contextmanager
import sh_models as SH, gmfit as G
HERE = os.path.dirname(os.path.abspath(__file__))
PINS = json.load(open(os.path.join(HERE, 't3dall', 'pins.json')))

@contextmanager
def pin_origin(pid):
    old = SH.ORIGIN; SH.ORIGIN = tuple(PINS[pid])
    try: yield
    finally: SH.ORIGIN = old

def plan2sat(fit, cx, cy):
    s, th, tx, ty = fit; c, sn = math.cos(th), math.sin(th)
    return lambda x, y: (tx + s * (c * (x - cx) - sn * (y - cy)), ty + s * (sn * (x - cx) + c * (y - cy)))

def georef(sat, fit, centre, lean=(0, 0)):
    """plan pixel -> [lat, lon]: plan fitted to the roof in satellite image <sat>, then shifted by <lean> pixels to the building's foot"""
    meta = json.load(open(os.path.join(HERE, 'newimg', sat + '.meta.json'))); f = plan2sat(fit, *centre)
    def ll(x, y):
        X, Y = f(x, y); return G.px2ll(meta, X + lean[0], Y + lean[1])
    return ll

def clip_cells(outline_px, rects):
    from shapely.geometry import Polygon, box
    O = Polygon(outline_px).buffer(0)
    out = {}
    for k, (x0, y0, x1, y1) in rects.items():
        g = O.intersection(box(x0, y0, x1, y1))
        if g.geom_type != 'Polygon': g = max(g.geoms, key=lambda q: q.area)
        out[k] = [list(p) for p in g.simplify(1.0).exterior.coords[:-1]]
    return out

def proj_geo(pid, base, fr):
    geo = dict((base or {}).get('geo') or {})
    geo.update(x=round(fr[0], 1), y=round(fr[1], 1), rot=round(fr[2], 1))
    return geo

# ------------------------------------------------------------------ Gala Ikebana (Sindhu Bhavan Road)
# Sanctioned plans filed on Gujarat RERA (AMC, 15 Jun 2022: "1-12 Plan_merged.pdf" sheets 01-12/19 and "Plan_QC4.pdf" 13-17/19), read 21 Oct 2026:
#  - RERA carpet-area key plans for odd floors (3, 5 ... 17) and even floors (4, 6 ... 16) print every unit number in place:
#    x01 in the south wings, x03 in the north wings, C-x02 / B-x01 / A-x02 along the central bar (B-x01 just west of the B core);
#  - balconies, wash yards and the planter ledge are hatched on the same key plans (pixel boxes below, in each key plan's own pixels);
#  - the AMC fire-safety opinion (OPN852329122021, 29 Dec 2021) gives every floor height and 87.2 m from ground level to the top slab;
#  - the area table: 3 basements, ground and floor 1 parking, floor 2 podium with the society amenities, 7 homes on each of floors 3-17,
#    duplexes with their lower levels on floors 18 and 20 (upper levels 19 and 21), 119 homes.
IKE_KEY = {   # key-plan pixels -> brochure typical-plan pixels (the frame of sat/ike_outline_px.json): outer corners of the four wings
  'odd': dict(x0=133, x1=1990, y0=42, y1=1243), 'even': dict(x0=113, x1=1975, y0=42, y1=1243)}
IKE_FEATS = {
  'odd': [('balc', 135, 175, 183, 343), ('balc', 520, 92, 557, 170), ('balc', 466, 945, 518, 1100), ('balc', 518, 1058, 552, 1100),
          ('balc', 575, 730, 695, 808), ('balc', 928, 730, 1050, 808), ('balc', 1428, 730, 1548, 808),
          ('balc', 742, 458, 808, 483), ('balc', 770, 425, 810, 458), ('balc', 815, 458, 898, 483), ('balc', 865, 425, 905, 458),
          ('balc', 1318, 458, 1400, 483), ('balc', 1365, 425, 1405, 458),
          ('balc', 1943, 185, 1990, 343), ('balc', 1568, 293, 1605, 365), ('balc', 1943, 945, 1990, 1100), ('balc', 1568, 1025, 1605, 1105),
          ('planter', 410, 808, 1600, 825),
          ('wash', 448, 374, 520, 412), ('wash', 135, 862, 185, 905), ('wash', 1898, 425, 1990, 458), ('wash', 1605, 868, 1668, 905)],
  'even': [('balc', 113, 183, 163, 340), ('balc', 503, 180, 537, 258), ('balc', 452, 945, 502, 1100), ('balc', 502, 940, 540, 985),
           ('balc', 557, 730, 680, 808), ('balc', 910, 730, 1032, 808), ('balc', 1413, 728, 1535, 806),
           ('balc', 705, 455, 790, 480), ('balc', 703, 422, 742, 455), ('balc', 795, 455, 885, 480), ('balc', 797, 422, 838, 455),
           ('balc', 1300, 455, 1385, 480), ('balc', 1302, 420, 1340, 455),
           ('balc', 1923, 178, 1972, 335), ('balc', 1550, 172, 1585, 250), ('balc', 1925, 940, 1975, 1095), ('balc', 1555, 1105, 1592, 1190),
           ('planter', 395, 806, 1585, 823),
           ('wash', 428, 368, 502, 410), ('wash', 117, 868, 188, 910), ('wash', 1888, 420, 1975, 455), ('wash', 1590, 865, 1660, 905)]}
IKE_FLOORS = [('Ground floor', 5.08), ('Floor 1', 3.90), ('Floor 2', 4.20)] + [(f'Floor {f}', 3.46) for f in range(3, 22)]   # AMC fire opinion


def ikebana(p, base):
    from shapely.geometry import Polygon, box
    from shapely.ops import unary_union
    P = json.load(open(os.path.join(HERE, 'sat', 'ike_outline_px.json')))
    fit = json.load(open(os.path.join(HERE, 'sat', 'ike_roof_fit.json')))['p']
    ll = georef('g_ikebana', fit, (540, 240), lean=(-62, 100))
    O = Polygon(P).buffer(0).simplify(2.0)
    outline = [list(q) for q in O.exterior.coords[:-1]]
    # flats as numbered on the sanctioned RERA key plans (wings y < 176 north, > 304 south; bar between the lift cores)
    rects = {'C03': (0, 0, 400, 176), 'C01': (0, 304, 400, 470), 'C02': (316, 150, 454, 330), 'B01': (454, 150, 590, 330),
             'A02': (625, 150, 765, 330), 'A03': (700, 0, 900, 176), 'A01': (700, 304, 900, 470)}
    cores = {'C': [[221, 176], [316, 176], [316, 304], [221, 304]], 'B': [[590, 176], [625, 176], [625, 304], [590, 304]],
             'A': [[765, 176], [860, 176], [860, 304], [765, 304]]}
    order = ['A01', 'A02', 'A03', 'B01', 'C01', 'C02', 'C03']
    k2b = lambda key: (lambda x, y: (221 + (x - IKE_KEY[key]['x0']) * 637 / (IKE_KEY[key]['x1'] - IKE_KEY[key]['x0']),
                                     31 + (y - IKE_KEY[key]['y0']) * 419 / (IKE_KEY[key]['y1'] - IKE_KEY[key]['y0'])))
    INV = {u[1]: u for u in json.load(open(os.path.join(HERE, 'rera_live', '17770_inv.json')))['units']}
    with pin_origin('gala-ikebana'):
        import sitegeo as SG
        Pm = [SH.xy(*ll(*q)) for q in outline]; rot, w, d, (cx, cy) = SG.mbr(Pm); fr = (cx, cy, rot)
        L_ = lambda q: SH.loc(fr, *ll(*q))
        body = Polygon([L_(q) for q in outline]).buffer(0)
        feats = {}
        for key, F in IKE_FEATS.items():
            f2b = k2b(key); out = []
            for t_, x0, y0, x1, y1 in F:
                Q = Polygon([L_(f2b(x, y)) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))])
                if Q.distance(body.exterior) > 0.8: continue          # only on the facade
                pts = [[round(a, 2), round(b, 2)] for a, b in Q.exterior.coords[:-1]]
                # edges lying against the building body get no railing (recessed: the edges inside the floor plate; projecting: the edge on the wall)
                from shapely.geometry import Point
                inside = body.contains(Q.centroid)
                open_ = []
                for i in range(len(pts)):
                    m = Point((pts[i][0] + pts[i - 1][0]) / 2, (pts[i][1] + pts[i - 1][1]) / 2)
                    if (body.buffer(-0.35).contains(m) if inside else body.buffer(0.3).contains(m)):
                        open_.append([round(m.x, 2), round(m.y, 2)])
                out.append(dict(t=t_, p=pts, poly=Q, open=open_))
            feats[key] = out
        cut = {key: unary_union([f['poly'] for f in feats[key] if f['t'] in ('balc', 'wash')]) for key in feats}
        def cells_for(key):
            res = []
            for k in order:
                g = Polygon(outline).buffer(0).intersection(box(*rects[k]))
                if g.geom_type != 'Polygon': g = max(g.geoms, key=lambda q: q.area)
                G_ = Polygon([L_(q) for q in g.simplify(1.0).exterior.coords[:-1]]).difference(cut[key].buffer(0.05)) if key else Polygon([L_(q) for q in g.simplify(1.0).exterior.coords[:-1]])
                if G_.geom_type != 'Polygon': G_ = max(G_.geoms, key=lambda q: q.area)
                res.append([list(q) for q in G_.simplify(0.15).exterior.coords[:-1]])
            return res
        def frows(nos):
            out = []
            for n in nos:
                u_ = INV.get(n)
                if not u_: out.append(None); continue
                c_, b_ = float(u_[2]), float(u_[3])
                out.append([['RERA carpet', f'{c_:,.2f} sq m ({c_ * 10.7639:,.0f} sq.ft.)'], ['Exclusive balcony', f'{b_:,.2f} sq m ({b_ * 10.7639:,.0f} sq.ft.)']])
            return out
        TYP = '7 homes: x01 in the south wing and x03 in the north wing off the A and C lobbies, C-x02, B-x01 and A-x02 along the central bar (Gujarat RERA key plans)'
        st = [dict(label='Ground floor', kind='M', h=5.08, wall=True, use='Entrance foyers of blocks A, B and C, drop-off, parking and the ramps; three basements of parking below (606 covered spaces, Gujarat RERA)'),
              dict(label='Floor 1', kind='M', h=3.90, wall=True, use='Parking (sanctioned area table)'),
              dict(label='Floor 2 · Earth Level', kind='M', h=4.20, use='Podium with the society amenities: play, social, functional, entertainment and fitness zones and the swimming pool in the south court (sanctioned area table; Gala’s earth-level plan)')]
        for f_ in range(3, 18):
            nos = [k[0] + '-' + str(f_) + k[1:] for k in order]
            st.append(dict(label=f'Floor {f_}', kind='A', h=3.46, nos=nos, frows=frows(nos), feat='odd' if f_ % 2 else 'even', note=TYP))
        for lo in (18, 20):
            nos = [k[0] + '-' + str(lo) + k[1:] for k in order]
            st.append(dict(label=f'Floors {lo}–{lo + 1} (duplexes)', kind='P', levels=2, h=6.92, nos=nos, frows=frows(nos), unit='dup',
                           note=f'7 duplexes: lower level on floor {lo}, upper level on floor {lo + 1}; each with a large deck (Gujarat RERA: 129–173 sq m exclusive balcony per home)'))
        t = SH.tower(fr, 'T1', 'Ikebana', [ll(*q) for q in outline], st, 'all', nolift=True, crown=dict(type='cap', h=1.5))
        for L in st:
            if L.get('nos'):
                key = L.get('feat')
                L['plan'] = dict(cells=[[[round(a - t['x'], 2), round(b - t['y'], 2)] for a, b in c] for c in cells_for(key)])
        t['feats'] = {key: [dict(t=f['t'], p=[[round(a - t['x'], 2), round(b - t['y'], 2)] for a, b in f['p']],
                                 open=[[round(a - t['x'], 2), round(b - t['y'], 2)] for a, b in f['open']]) for f in feats[key]] for key in feats}
        T = [t]
        for i, k in enumerate('ABC'):
            T.append(SH._local_tower(f'K{i+1}', f'Block {k} lift core', [L_(q) for q in cores[k]],
                                     [dict(label=L['label'], kind='M', h=L.get('h'), use='Lifts, service lift and staircases (sanctioned plans)') for L in st]
                                     + [dict(SH.MROOM, h=87.2 - sum(L['h'] for L in st), use='Stair cabin, lift machine room and overhead water tank: the top slab is 87.2 m above ground level (AMC fire opinion)')],
                                     'all', nolabel=True, solid=True, nolift=True, crown=dict(type='cap', h=0.6)))
        rera = ['RERA', 'PR/GJ/AHMEDABAD/DASKROI/AUDA/RAA10949/191122']
        units = {'all': SH.u('Ikebana · 5 BHK residences', '5 BHK',
                             [['Homes', '7 on each of floors 3 to 17 (105) and 14 duplexes on floors 18–21: 119 in all (Gujarat RERA)'], ['Plans', 'Gala Group unit plans for blocks A and B; sanctioned AMC plans filed on Gujarat RERA'],
                              ['Possession', 'RERA completion date 1 Jul 2027'], rera], perFloor='7 homes'),
                 'dup': SH.u('Ikebana · 5 BHK duplexes', '5 BHK duplex',
                             [['Size', '495.93 – 628.51 sq m RERA carpet (5,338 – 6,765 sq.ft.) with 129 – 173 sq m exclusive decks'], rera], perFloor='7 duplexes')}
    note = ('Ikebana (Gala Group): one H-shaped tower with three lift cores, A (east wing, on Sindhu Bhavan Road), B (central bar) and C (west wing). '
            'Every floor height is from the Ahmedabad fire-safety opinion filed on Gujarat RERA: ground floor 5.08 m, floor 1 3.90 m, floor 2 (podium) 4.20 m and 3.46 m for each of floors 3 to 21; '
            '87.2 m from ground level to the top slab. Floor uses are from the sanctioned area table: parking on the ground floor and floor 1 (and three basements), the Earth Level amenity podium on floor 2, '
            '7 homes on each of floors 3 to 17 and 14 duplexes on floors 18–21 (119 homes). Flat numbers, balconies, wash yards and the planter ledge are placed as on the RERA carpet-area key plans '
            '(odd and even floors differ slightly); tap a flat for its RERA carpet and balcony area. The outline is Gala’s typical-floor plan fitted to the roof in current satellite imagery. '
            'Surroundings are from OpenStreetMap.')
    C = json.loads(json.dumps(base))
    g2t = lambda x, y: ((x - (121 - 251 * 0.751)) / 0.751, (y - (304 - 187 * 0.764)) / 0.764)
    site = [[58, 147], [652, 117], [622, 547], [56, 556]]
    with pin_origin('gala-ikebana'):
        pp = [[round(a, 1), round(b, 1)] for a, b in (SH.loc(fr, *ll(*g2t(*q))) for q in site)]
    C.update(towers=T, units=units, stack=st, floorH=3.46, note=note, geo=proj_geo('gala-ikebana', base, fr), flatWord='Flat', perFloor='7 homes', perFloorLabel='Homes on a floor',
             startFloor='Floor 10', camStay=True, cellsNote='Position as on the RERA carpet-area key plan of the sanctioned drawings.')
    C.pop('typicalOnly', None)
    C['plotPoly'] = pp; C['clear'] = [pp]
    xs = [a for a, b in pp]; ys = [b for a, b in pp]
    C['plot'] = dict(w=round(max(xs) - min(xs), 1), d=round(max(ys) - min(ys), 1))
    C['height'] = 87.2; C['hSrc'] = 'AMC fire-safety opinion filed on Gujarat RERA'
    return C

# ------------------------------------------------------------------ Maruti 360 (Bodakdev)
def maruti(p, base):
    """towers from the developer's plans brochure (typical site plan + 4 BHK and 5 BHK typical floors), the site plan fitted to the plot walls
    in Bing imagery (north edge on the road, east edge on the service road) and checked against the leaning towers in current Esri imagery"""
    from shapely.geometry import Polygon, box
    from shapely.ops import unary_union
    R = json.load(open(os.path.join(HERE, 'sat', 'maruti_outlines.json'))); LL = json.load(open(os.path.join(HERE, 'sat', 'maruti_ll.json')))
    meta = json.load(open(os.path.join(HERE, 'newimg', 'b_maruti.meta.json')))
    # the same fit as sat/maruti_ll.json, for cells and cores (typical-plan pixels -> lat/lon)
    import numpy as np
    NWp, NEp, NWb, NEb = np.array([1765, 915.]), np.array([230, 915.]), np.array([190, 157.]), np.array([775, 197.])
    vp, vb = NEp - NWp, NEb - NWb; sc = np.linalg.norm(vb) / np.linalg.norm(vp); th = math.atan2(vb[1], vb[0]) - math.atan2(vp[1], vp[0])
    Rm = np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]])
    SB = {'A': (375, 595, 794, 809), 'B': (925, 595, 1464, 808)}
    def tp2ll(n):
        x0, y0, x1, y1 = R[n]['bb']; X0, Y0, X1, Y1 = SB[n]
        def f(x, y):
            sp = np.array([X0 + (x - x0) * (X1 - X0) / (x1 - x0), Y0 + (y - y0) * (Y1 - Y0) / (y1 - y0)])
            return G.px2ll(meta, *(NWb + sc * Rm @ (sp - NWp)))
        return f
    # cores (plan pixels of each typical floor): lift lobbies with the personal foyers, and the stair / service block on the road side
    CORE = {'A': [(745, 668, 1240, 832), (595, 832, 1390, 1005)], 'B': [(670, 660, 1310, 800), (670, 790, 1320, 920)]}
    MID = {'A': 991, 'B': 990}
    FH = 3.6      # AMC fire-safety opinion (20 Sep 2022): ground 6.00 m, floor 1 4.20 m, 3.60 m for every floor above
    with pin_origin('maruti-360'):
        import sitegeo as SG
        Pm = [SH.xy(*q) for q in LL['plot']]; rot, w, d, (cx, cy) = SG.mbr(Pm); fr = (cx, cy, rot)
        T = []
        for i, n in enumerate('AB'):
            f = tp2ll(n)
            O = Polygon(R[n]['P']).buffer(0)
            core = unary_union([box(*b) for b in CORE[n]]).intersection(O)
            bb = O.bounds
            east = O.difference(core).intersection(box(bb[0] - 1, bb[1] - 1, MID[n], bb[3] + 1))      # plan left = east (the drawing has south at the top)
            west = O.difference(core).intersection(box(MID[n], bb[1] - 1, bb[2] + 1, bb[3] + 1))
            big = lambda g: max(g.geoms, key=lambda q: q.area) if g.geom_type != 'Polygon' else g
            cells = [[list(q) for q in big(g).simplify(4).exterior.coords[:-1]] for g in (east, west)]
            cpoly = big(core.buffer(0)); cpoly = [list(q) for q in cpoly.simplify(3).exterior.coords[:-1]]
            outline = [list(q) for q in O.simplify(3).exterior.coords[:-1]]
            typ = '4 BHK' if n == 'A' else '5 BHK'
            st = [dict(label='Ground floor', kind='M', h=6.0, use='Entrance lobby and drop-off on the road side (north), parking and foyer (Maruti typical site plan; AMC fire-safety opinion); three basements of parking below'),
                  dict(label='Floor 1', kind='M', h=4.2, use='Parking and amenities (AMC fire-safety opinion)'),
                  dict(label='Floor 2', kind='M', h=FH, use='No home is registered on this floor: the Gujarat RERA unit list starts at floor 3')]
            for f_ in range(3, 34):
                if f_ in (13, 21):
                    st.append(dict(label=f'Floor {f_}', kind='M', h=FH, use='No home is registered on this floor (Gujarat RERA unit list)'))
                else:
                    st.append(dict(label=f'Floor {f_}', kind='A', h=FH, nos=[f'{n}-{f_}01', f'{n}-{f_}02'],
                                   note=f'Two {typ} residences, east and west of the lift lobby, each with its own lifts, personal foyer and verandah on the south side (Maruti 360 typical plan)'))
            st.append(dict(label='Floors 34–35 (duplexes)', kind='P', levels=2, h=2 * FH, nos=[f'{n}-3401', f'{n}-3402'],
                           note='Two duplexes, each over floors 34 and 35 (Gujarat RERA: about twice the carpet area of a typical home)'))
            st.append(dict(label='Floors 36–37 (penthouses)', kind='P', levels=2, h=2 * FH, nos=[f'{n}-3601', f'{n}-3602'],
                           note='Two penthouses, each over floors 36 and 37, with the largest terraces in the tower (Gujarat RERA)'))
            t = SH.tower(fr, f'T{i+1}', f'Tower {n} · {typ}', [f(*q) for q in outline], st, 'all', nolift=True, crown=dict(type='cap', h=2))
            cl = [[[round(a - t['x'], 2), round(b - t['y'], 2)] for a, b in (SH.loc(fr, *f(*q)) for q in c)] for c in cells]
            for L in st:
                if L.get('nos'): L['plan'] = dict(cells=cl)
            T.append(t)
            T.append(SH._local_tower(f'K{i+1}', f'Tower {n} lift core', [SH.loc(fr, *f(*q)) for q in cpoly],
                                     [dict(label=L['label'], kind='M', h=L.get('h'), levels=L.get('levels', 1), use='Private lifts, service lift and staircases (Maruti typical floor plan)') for L in st]
                                     + [dict(SH.MROOM, h=round(153.33 - sum(L['h'] for L in st), 2), use='Lift machine rooms, staircase heads and the top of the tower: 153.33 m above ground level (AMC fire-safety opinion and environmental clearance)')],
                                     'all', nolabel=True, solid=True, nolift=True, crown=dict(type='cap', h=1.5)))
        pp = [[round(a, 1), round(b, 1)] for a, b in (SH.loc(fr, *q) for q in LL['plot'])]
    rera = ['RERA', 'PR/GJ/AHMEDABAD/AHMEDABAD CITY/AUDA/RAA12039/280623']
    units = {'all': SH.u('Maruti 360 · 4 and 5 BHK residences', '4 & 5 BHK',
                         [['Towers', 'Tower A: 4 BHK; tower B: 5 BHK (typical site plan). Duplex and penthouse homes in both (Maruti floor plans)'],
                          ['Homes', '124 in all, 62 in each tower (Gujarat RERA): two a floor on floors 3 to 33 (none registered on floors 13 and 21), two duplexes over floors 34–35 and two penthouses over floors 36–37'],
                          ['Possession', 'RERA completion date 31 Dec 2028'], rera], perFloor='2 homes')}
    note = ('Maruti 360: two towers on the plot next to Karnavati Club, from the developer’s plans brochure: tower A (east, 4 BHK) and tower B (west, 5 BHK), each with two residences per typical floor '
            '(east and west of the lift lobby, verandahs facing south), the lift and stair core on the road side, and the podium with pool, garden and clubhouse behind. '
            'The site plan is fitted to the plot walls in satellite imagery (north edge on the road, east edge on the S.G. Highway service road) and agrees with the towers now built. '
            'Floors and homes are from the Gujarat RERA unit list: homes on floors 3 to 37, two a floor, none registered on floors 13 and 21, duplexes over floors 34–35 and penthouses over 36–37 '
            '(3 basements + ground + 37 floors: the 41 storeys Maruti quotes). Floor heights are from the Ahmedabad fire-safety opinion of 20 Sep 2022 filed on Gujarat RERA: ground floor 6.00 m, floor 1 4.20 m '
            'and 3.60 m for every floor above, which puts the roof of floor 37 at 139.80 m; the towers are 153.33 m to the top (that opinion and the environmental clearance; Maruti quotes 501 ft). '
            'That opinion was issued for an earlier floor arrangement, so the levels above floor 1 follow its typical height. Which side of each tower carries the 01 and which the 02 numbers is not marked on the published plans. Surroundings are from OpenStreetMap.')
    C = json.loads(json.dumps(base))
    st0 = T[0]['stack']
    C.update(towers=T, units=units, stack=st0, floorH=FH, note=note, geo=proj_geo('maruti-360', base, fr), flatWord='Flat', perFloor='2 homes', perFloorLabel='Homes on a floor', startFloor='Floor 20', camStay=True,
             plotPoly=pp, clear=[pp], height=153.33, hSrc='AMC fire-safety opinion filed on Gujarat RERA',
             cellsNote='Positions as on Maruti’s typical floor plan; which side carries the 01 and which the 02 number is not marked on the published plans. Duplex and penthouse levels are drawn on the typical outline.')
    xs = [a for a, b in pp]; ys = [b for a, b in pp]
    C['plot'] = dict(w=round(max(xs) - min(xs), 1), d=round(max(ys) - min(ys), 1))
    return C

PIDS = ('gala-ikebana', 'maruti-360')
BUILD = {'gala-ikebana': ikebana, 'maruti-360': maruti}
def build(pid, p, base): return BUILD[pid](p, base or {'geo': {}})
