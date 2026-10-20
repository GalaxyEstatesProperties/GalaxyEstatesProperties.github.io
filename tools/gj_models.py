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
def ikebana(p, base):
    from shapely.geometry import Polygon
    P = json.load(open(os.path.join(HERE, 'sat', 'ike_outline_px.json')))
    fit = json.load(open(os.path.join(HERE, 'sat', 'ike_roof_fit.json')))['p']
    ll = georef('g_ikebana', fit, (540, 240), lean=(-62, 100))
    O = Polygon(P).buffer(0).simplify(2.0)
    outline = [list(q) for q in O.exterior.coords[:-1]]
    rects = {'C01': (0, 0, 361, 177), 'C02': (302, 165, 455, 320), 'C03': (0, 303, 361, 470), 'B01': (455, 150, 589, 320),
             'A02': (625, 150, 778, 320), 'A01': (718, 0, 900, 177), 'A03': (718, 303, 900, 470)}
    cells = clip_cells(outline, rects)
    cores = {'C': [[225, 177], [302, 177], [302, 303], [225, 303]], 'B': [[589, 177], [625, 177], [625, 303], [589, 303]], 'A': [[778, 177], [858, 177], [858, 303], [778, 303]]}
    order = ['A01', 'A02', 'A03', 'B01', 'C01', 'C02', 'C03']
    with pin_origin('gala-ikebana'):
        fr = SH.frame_from_poly([ll(*q) for q in outline]) if hasattr(SH, 'frame_from_poly') else None
        import sitegeo as SG
        Pm = [SH.xy(*ll(*q)) for q in outline]; rot, w, d, (cx, cy) = SG.mbr(Pm); fr = (cx, cy, rot)
        # heights measured on Gala's drone photo of 8 Oct 2025 (floor numbers painted on the slab edges of the east face, which is 58.2 m wide on the plan):
        # typical floor to floor 3.27 m; the terracotta base (ground floor and floor 1) is 13.6 m to the floor-2 slab
        FH = 3.27
        TYP = 'Typical floor (Gala Group plan, odd and even floors): 7 homes: flats 01, 02 and 03 off the lobbies of blocks A and C, flat 01 off the block B lobby'
        st = [dict(label='Ground floor', kind='M', h=7.0, use='Entrance foyers of blocks A, B and C, drop-off and parking, with the ramps to the basement and podium (Gala’s ground-floor plan); basements below (606 covered parking spaces, Gujarat RERA)'),
              dict(label='Floor 1 · Earth Level', kind='M', h=6.6, use='The Earth Level amenity floor at the courtyard: play, social, functional, entertainment and fitness zones (box cricket, cafeteria, library, pilates, pool table, rock climbing, outdoor party lounge) and the swimming pool in the south court (Gala’s earth-level plan)')]
        for f_ in range(2, 22):
            st.append(dict(label=f'Floor {f_}', kind='A', h=FH, nos=[k[0] + '-' + k[1:] for k in order], plan=dict(cells=None), note=TYP))
        t = SH.tower(fr, 'T1', 'Ikebana', [ll(*q) for q in outline], st, 'all', nolift=True, crown=dict(type='cap', h=1.5))
        cl = [[[round(a - t['x'], 2), round(b - t['y'], 2)] for a, b in (SH.loc(fr, *ll(*q)) for q in cells[k])] for k in order]
        for L in st:
            if L.get('plan'): L['plan'] = dict(cells=cl)
        T = [t]
        for i, k in enumerate('ABC'):
            T.append(SH._local_tower(f'K{i+1}', f'Block {k} lift core', [SH.loc(fr, *ll(*q)) for q in cores[k]],
                                     [dict(label=L['label'], kind='M', h=L.get('h'), use='Lifts, service lift and staircases (Gala typical floor plan)') for L in st] + [dict(SH.MROOM, use='Lift and staircase heads serving the Sky Level roof terrace')],
                                     'all', nolabel=True, solid=True, nolift=True, crown=dict(type='cap', h=1.5)))
        rera = ['RERA', 'PR/GJ/AHMEDABAD/DASKROI/AUDA/RAA10949/191122']
        units = {'all': SH.u('Ikebana · 5 BHK residences', '5 BHK',
                             [['Homes', '119 in all (Gujarat RERA), carpet 308.29 – 628.51 sq m (3,318 – 6,765 sq.ft.); the typical floor has 7, so some floors hold fewer, larger homes'],
                              ['Plans', 'Block A odd floor (flats 01 and 03 in the wings): 377.88 sq m carpet + 25.82 sq m balcony; block B odd floor (flat 01): 308.29 sq m carpet + 43.61 sq m balcony (Gala unit plans)'],
                              ['Possession', 'RERA completion date 1 Nov 2027'], rera], perFloor='7 homes (typical floor)')}
    plotPoly = base.get('plotPoly') if base else None
    note = ('Ikebana (Gala Group): one H-shaped tower, not three: blocks A (east wing, on Sindhu Bhavan Road), B (the central bar) and C (west wing) are its three lift cores. '
            'The outline, cores and the seven flats of a typical floor are cut from Gala’s typical-floor plan (flats 01, 02 and 03 off the A and C lobbies, and flat 01 off the B lobby). '
            'The plan is fitted to the roof in current satellite imagery and moved to the building’s foot; position within about 3 m. '
            'Floors: ground floor with the entrance foyers and parking, floor 1 the Earth Level amenity floor, homes from floor 2 to floor 21 (Gala: 21 floors), and the Sky Level gardens on the roof. '
            'Heights are measured on Gala’s drone photo of 8 October 2025, which shows the floor numbers painted on the slabs: 3.27 m floor to floor, and a 13.6 m terracotta base for the ground floor and floor 1. '
            'Gujarat RERA registers 119 homes (carpet 308.29 to 628.51 sq m), fewer than 7 on every floor, so some floors hold fewer, larger homes; Gala does not publish those plans, '
            'so every home floor is drawn with the typical plan. Plot: the site boundary on Gala’s ground-floor plan. Surroundings are from OpenStreetMap.')
    C = json.loads(json.dumps(base))
    # plot: the site boundary of Gala's ground-floor plan, carried onto the typical plan through the three lift cores (they line up on both drawings)
    g2t = lambda x, y: ((x - (121 - 251 * 0.751)) / 0.751, (y - (304 - 187 * 0.764)) / 0.764)
    site = [[58, 147], [652, 117], [622, 547], [56, 556]]
    with pin_origin('gala-ikebana'):
        pp = [[round(a, 1), round(b, 1)] for a, b in (SH.loc(fr, *ll(*g2t(*q))) for q in site)]
    C.update(towers=T, units=units, stack=st, floorH=FH, note=note, geo=proj_geo('gala-ikebana', base, fr), flatWord='Flat', perFloor='7 homes (typical floor)', typicalOnly=True, perFloorLabel='Typical floor',
             startFloor='Floor 10', camStay=True, cellsNote='Position as on Gala’s typical floor plan. Some floors hold fewer, larger homes (119 in all, Gujarat RERA), so ask us which homes are on this floor.')
    C['plotPoly'] = pp; C['clear'] = [pp]
    xs = [a for a, b in pp]; ys = [b for a, b in pp]
    C['plot'] = dict(w=round(max(xs) - min(xs), 1), d=round(max(ys) - min(ys), 1))
    C['height'] = round(13.6 + 20 * FH, 1)
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
    FH = 3.72
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
            st = [dict(label='Ground floor', kind='M', h=6.0, use='Entrance lobby and drop-off on the road side (north); the podium deck with the swimming pool, garden, play area and clubhouse lies behind the towers (Maruti typical site plan)')]
            for f_ in range(1, 41):
                st.append(dict(label=f'Floor {f_}', kind='A', h=FH, nos=[f'{n} east residence', f'{n} west residence'],
                               note=f'Typical floor (Maruti 360 plans): two {typ} residences, east and west of the lift lobby, each with its own lifts, personal foyer and verandah on the south side'))
            t = SH.tower(fr, f'T{i+1}', f'Tower {n} · {typ}', [f(*q) for q in outline], st, 'all', nolift=True, crown=dict(type='cap', h=2))
            cl = [[[round(a - t['x'], 2), round(b - t['y'], 2)] for a, b in (SH.loc(fr, *f(*q)) for q in c)] for c in cells]
            for L in st:
                if L.get('nos'): L['plan'] = dict(cells=cl)
            T.append(t)
            T.append(SH._local_tower(f'K{i+1}', f'Tower {n} lift core', [SH.loc(fr, *f(*q)) for q in cpoly],
                                     [dict(label=L['label'], kind='M', h=L.get('h'), use='Private lifts, service lift and staircases (Maruti typical floor plan)') for L in st] + [SH.MROOM],
                                     'all', nolabel=True, solid=True, nolift=True, crown=dict(type='cap', h=1.5)))
        pp = [[round(a, 1), round(b, 1)] for a, b in (SH.loc(fr, *q) for q in LL['plot'])]
    rera = ['RERA', 'PR/GJ/AHMEDABAD/AHMEDABAD CITY/AUDA/RAA12039/280623']
    units = {'all': SH.u('Maruti 360 · 4 and 5 BHK residences', '4 & 5 BHK',
                         [['Towers', 'Tower A: 4 BHK; tower B: 5 BHK (typical site plan). Duplex and penthouse homes in both (Maruti floor plans)'],
                          ['Homes', '124 in all, 62 in each tower (Gujarat RERA); carpet 40,007.72 sq m in total'], ['Possession', 'RERA completion date 31 Dec 2028'], rera])}
    note = ('Maruti 360: two towers on the plot next to Karnavati Club, from the developer’s plans brochure: tower A (east, 4 BHK) and tower B (west, 5 BHK), each with two residences per typical floor '
            '(east and west of the lift lobby, verandahs facing south), the lift and stair core on the road side, and the podium with pool, garden and clubhouse behind. '
            'The site plan is fitted to the plot walls in satellite imagery (north edge on the road, east edge on the S.G. Highway service road) and agrees with the towers now built. '
            'Height: 501 ft (152.7 m) over 41 storeys (Maruti 360 website; its plans brochure says 37 storeys). Gujarat RERA registers 62 homes per tower, fewer than two on every floor: '
            'some levels hold the duplexes and penthouses (the developer publishes their plans, but not which floors they are on), so every floor is drawn with the typical plan. Surroundings are from OpenStreetMap.')
    C = json.loads(json.dumps(base))
    st0 = T[0]['stack']
    C.update(towers=T, units=units, stack=st0, floorH=FH, note=note, geo=proj_geo('maruti-360', base, fr), flatWord='', perFloor='2 homes (typical floor)', typicalOnly=True, perFloorLabel='Typical floor', startFloor='Floor 20', camStay=True,
             plotPoly=pp, clear=[pp], height=152.7, cellsNote='Position as on Maruti’s typical floor plan. Some levels hold duplexes and penthouses (62 homes per tower, Gujarat RERA), so ask us which homes are on this floor.')
    xs = [a for a, b in pp]; ys = [b for a, b in pp]
    C['plot'] = dict(w=round(max(xs) - min(xs), 1), d=round(max(ys) - min(ys), 1))
    return C

PIDS = ('gala-ikebana', 'maruti-360')
BUILD = {'gala-ikebana': ikebana, 'maruti-360': maruti}
def build(pid, p, base): return BUILD[pid](p, base or {'geo': {}})
