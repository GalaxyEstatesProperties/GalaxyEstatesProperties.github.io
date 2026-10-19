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
        FH = 3.25
        st = [dict(label='Ground floor', kind='M', h=6.5, use='The Earth Level: entrance lobbies of blocks A, B and C with the play, social, functional, entertainment and fitness zones '
                   '(box cricket, cafeteria, library, pilates, pool table, rock climbing, outdoor party lounge), and the swimming pool in the south court (Gala’s earth-level plan); basements below for parking (606 covered spaces, Gujarat RERA)')]
        for f_ in range(1, 22):
            st.append(dict(label=f'Floor {f_}', kind='A', h=FH, nos=[k[0] + '-' + k[1:] for k in order],
                           plan=dict(cells=None), note='Typical floor (Gala Group plan): 7 homes, flats 01–03 round the lift lobbies of blocks A and C and flat 01 of block B'))
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
                             [['Homes', '119 in all (Gujarat RERA), carpet 308 – 628.51 sq m (3,318 – 6,765 sq.ft.)'],
                              ['Plans', 'Block A odd floor (flats 01 and 03 in the wings): 377.88 sq m carpet + 25.82 sq m balcony; block B odd floor (flat 01): 308.29 sq m carpet + 43.61 sq m balcony (Gala unit plans)'],
                              ['Possession', 'RERA completion date 1 July 2027'], rera], perFloor='7 homes (typical floor)')}
    plotPoly = base.get('plotPoly') if base else None
    note = ('Ikebana (Gala Group): one H-shaped tower, not three: blocks A (east wing, on Sindhu Bhavan Road), B (the central bar) and C (west wing) are its three lift cores. '
            'The outline, cores and the seven flats of a typical floor are cut from Gala’s typical-floor plan (flats 01, 02 and 03 off the A and C lobbies — north wing, bar, south wing — and flat 01 off the B lobby). '
            'The plan is fitted to the roof in current satellite imagery and moved to the building’s foot; position within about 3 m. '
            'Height: 21 floors (Gala) at about 3.25 m floor to floor, scaled on Gala’s October 2025 construction photo against the 58 m east face of the plan, over a tall ground floor (about 6.5 m, estimated); '
            'the roof is the Sky Level: dining space, wellness garden, party court and senior-citizen garden with green walkways (Gala’s sky-level plan). Gujarat RERA registers 119 homes (fewer than 7 on every floor, as some are larger sky-villa homes); the floor-by-floor list from the RERA filing is being added. '
            'Plot: the site boundary on Gala’s ground-floor plan. Surroundings are from OpenStreetMap.')
    C = json.loads(json.dumps(base))
    # plot: the site boundary of Gala's ground-floor plan, carried onto the typical plan through the three lift cores (they line up on both drawings)
    g2t = lambda x, y: ((x - (121 - 251 * 0.751)) / 0.751, (y - (304 - 187 * 0.764)) / 0.764)
    site = [[58, 147], [652, 117], [622, 547], [56, 556]]
    with pin_origin('gala-ikebana'):
        pp = [[round(a, 1), round(b, 1)] for a, b in (SH.loc(fr, *ll(*g2t(*q))) for q in site)]
    C.update(towers=T, units=units, stack=st, floorH=FH, note=note, geo=proj_geo('gala-ikebana', base, fr), flatWord='Flat', perFloor='7 homes (typical floor)',
             startFloor='Floor 10', camStay=True, cellsNote='Flat positions follow Gala’s typical floor plan; the RERA floor-by-floor list is being added.')
    C['plotPoly'] = pp; C['clear'] = [pp]
    xs = [a for a, b in pp]; ys = [b for a, b in pp]
    C['plot'] = dict(w=round(max(xs) - min(xs), 1), d=round(max(ys) - min(ys), 1))
    C['height'] = round(6.5 + 21 * FH, 1)
    return C

PIDS = ('gala-ikebana',)
BUILD = {'gala-ikebana': ikebana}
def build(pid, p, base): return BUILD[pid](p, base or {'geo': {}})
