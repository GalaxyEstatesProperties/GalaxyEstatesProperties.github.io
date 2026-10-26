"""3D explorers rebuilt from official plans, 19 Oct 2026 (second round of corrections):
The West Park, Inspire Corporate Capital, Center Point, Amora, The Storeys Golf Coast, The Storeys (golf living), The Storeys Infinity,
Shivalik Presente, Shivalik Skyview, Shivalik Curv and Navratna Gulmohar Park.
Plot outlines: Gujarat RERA map service. Building outlines: the developers' official master / floor plans, georeferenced on the RERA plot
(and on satellite imagery where the buildings stand). Floors and flats: Gujarat RERA unit lists; flat types and sizes from the developers' plans."""
import json, math, os
HERE = os.path.dirname(os.path.abspath(__file__))
import sh_models as SH
RERA = json.load(open(os.path.join(HERE, 'gm', 'rera.json')))
SURR = SH.SURR

def frame_ll(poly):
    import sitegeo as SG
    P = [SH.xy(*q) for q in poly]; rot, w, d, (cx, cy) = SG.mbr(P); return cx, cy, rot

def local(fr, ll): return [[round(a, 2), round(b, 2)] for a, b in (SH.loc(fr, *q) for q in ll)]

def cfg_base(p, base, fr, towers, units, st, floorH, note, plotPoly, kind='residential', **extra):
    cx, cy, rot = fr
    xs = [t['x'] + a for t in towers for a, b in t['pts']] + [a for a, b in plotPoly]
    ys = [t['y'] + b for t in towers for a, b in t['pts']] + [b for a, b in plotPoly]
    geo = dict((base or {}).get('geo') or {})
    gname = extra.pop('geo_name', 'GEO_SHANTIGRAM')
    geo.update(name=gname, file='assets/geo-shantigram.js' if gname == 'GEO_SHANTIGRAM' else 'assets/geo-gift.js', x=round(cx, 1), y=round(cy, 1), rot=round(rot, 1), radius=extra.pop('radius', 800))
    mid = st[min(len(st) - 1, max(1, len(st) // 2))]['label']
    cfg = dict(project=p['name'], interest=p['label'], floorH=floorH, stack=st, towers=towers, units=units, plot=dict(w=round(max(xs) - min(xs), 1), d=round(max(ys) - min(ys), 1)),
               geo=geo, kind=kind, startFloor=mid, enqLabel='Enquire about this floor', plotPoly=plotPoly, note=note, camStay=True)
    cfg.update(extra); return cfg

# ------------------------------------------------------------------ The West Park (61 build-to-suit villa plots)
def west_park(p, base):
    R = RERA['west-park']; fr = frame_ll(R['poly'])
    PL = json.load(open(os.path.join(HERE, 'gm', 'wp_plots.json')))
    st = [dict(label='Villa', kind='A')]
    T = []; units = {}; ctx = []
    for k in sorted(PL, key=int):
        v = PL[k]; n = int(k)
        big = n == 48
        lab = f'Plot {n:02d}'
        t = SH.tower(fr, f'P{n}', lab, v['villa'], [dict(label='Villa', kind='A', nos=[f'Villa {n:02d}'])], 'p' + k, nolabel=True, crown=dict(type='none'))
        T.append(t)      # plot n = VILLA- n on the Gujarat RERA list (the one type-B villa is 48 in both)
        rows = [['Plot', f'{lab} on Adani Realty’s master layout'],
                ['Plot size', f'about {v["area"]:,} sq m as drawn on the master layout (Adani Realty: plots run from 358 to 1,765 sq m; ask us for this plot’s exact figure)'],
                ['Villa', 'The larger built-to-suit villa on the layout (registered as type B, one villa)' if big else '1 BHK starter villa built by Adani Realty (ground floor), which the owner can expand and design (built to suit)'],
                ['Registered', '61 villas: 60 of type A and 1 of type B; 31 booked (Gujarat RERA progress report)'],
                ['Possession', 'April 2028 (RERA completion date 30 Apr 2028)'], ['RERA', 'PR/GJ/GANDHINAGAR/GANDHINAGAR/AUDA/RAA11300/020323']]
        units['p' + k] = SH.u(f'The West Park · {lab}', lab, rows, perFloor='1 villa')
        ctx.append(dict(t='line', p=local(fr, v['plot']), c='#c9a962', z=0.7))
    plotPoly = local(fr, R['poly'])
    note = ('The West Park: 61 build-to-suit villa plots on 38,827.5 sq m in Shantigram (Gujarat RERA: 61 villas, 60 of type A and 1 of type B). '
            'Plot numbers, plot lines and villa outlines are traced from Adani Realty’s official master layout, fitted to the plot registered on the Gujarat RERA map service (they agree within about 3 m). '
            'Each villa is drawn as built today: a single-storey 1 BHK villa that its owner can extend upwards and outwards (Adani Realty project photos, June 2026); '
            'plot sizes are measured on the layout and are approximate. The plot numbers on the layout are the villa numbers on the Gujarat RERA list (villa 48, the one type-B villa, is the large plot in both), '
            'so each villa shows its registered carpet area.' + SURR)
    club = json.load(open(os.path.join(HERE, 'gm', 'wp_ctx.json')))['club']
    ctx.append(dict(t='prism', p=local(fr, club), h=7, c='#b9c2cf', label='Clubhouse', size=9))
    return cfg_base(p, base, fr, T, units, st, 4.2, note, plotPoly, context=ctx, perFloorLabel='Villas', villas=True, camR=330, camY=4, camPh=1.05,
                    startFloor='Villa', enqLabel='Enquire about this plot', clear=[plotPoly])

# ------------------------------------------------------------------ Inspire Corporate Capital
def notch(pts, side, frac0, frac1, depth):
    """cut a rectangular recess into one long face of a 4-corner footprint (side = index of the face's first corner)"""
    from shapely.geometry import Polygon
    import numpy as np
    P = np.array(pts, float); A, B = P[side], P[(side + 1) % 4]; n = P.mean(0) - (A + B) / 2; n /= np.linalg.norm(n)
    a, b = A + (B - A) * frac0, A + (B - A) * frac1
    cut = Polygon([a - n * 2, b - n * 2, b + n * depth, a + n * depth])
    g = Polygon(P).difference(cut)
    return [[round(x, 2), round(y, 2)] for x, y in list(g.exterior.coords)[:-1]]

def icc(p, base):
    R = RERA['icc']; fr = frame_ll(R['poly']); L = json.load(open(os.path.join(HERE, 'gm', 'icc_ll.json')))
    st = [dict(label='Ground floor', kind='A', note='Entrance lobby, retail and the drop-off under the curved canopy')] + [dict(label=f'Floor {f}', kind='A') for f in range(1, 12)]
    T = []
    for i, (key, lab, side) in enumerate((('north', 'North block', 1), ('south', 'South block', 3))):
        t = SH.tower(fr, f'T{i+1}', lab, L[key], st, 'all', crown=dict(type='cap', h=1.2))
        # the stepped top of each block: a recessed terrace on the courtyard face over the top floors (Adani Realty renders)
        t['tiers'] = [dict({'from': 10}, pts=notch(t['pts'], side, 0.55 if key == 'north' else 0.36, 0.85 if key == 'north' else 0.64, 6.0))]
        T.append(t)
    w = SH.tower(fr, 'W', 'Low wing', L['wing'], [dict(label='Ground floor', kind='A'), dict(label='Floor 1', kind='A', note='Landscaped terrace on its roof')], 'all', nolabel=True, crown=dict(type='none'))
    T.append(w)
    units = {'all': SH.u('Inspire Corporate Capital · offices and retail', 'Offices & retail',
        [['Spaces', 'Corporate houses, designer work floors (a whole floor each), signature boutique offices and retail (Adani Realty)'],
         ['Size', '274.47 – 12,013.28 sq.ft. RERA carpet; price from ₹3.03 Cr* all inclusive (Adani Realty)'],
         ['Registered', '105 units: 43 in block A and 62 in block B; 23,259 sq m carpet in all (Gujarat RERA)'],
         ['Floor height', '11’6” internal floor height, DGU glass facade, district cooling (Adani Realty brochure)'],
         ['Completion', 'April 2027 (RERA)'], ['RERA', 'PR/GJ/GANDHINAGAR/GANDHINAGAR/AUDA/CAA12523/251023']], avail='Ask for live availability')}
    note = ('Inspire Corporate Capital: two glass office blocks joined by a low two-storey wing with a landscaped roof, a curved drop-off canopy and a courtyard, '
            'on the 8,603.72 sq m plot registered on the Gujarat RERA map service. Block outlines are traced on current satellite imagery of the site '
            '(together about 3,700 sq m on the ground, matching the 3,724 sq m registered as covered area). Floors: ground + 11 in each block, counted on Adani Realty’s '
            'renders and its August site photos (no floor-wise unit list is filed on RERA); 11’6” internal floor height. The recessed terraces at the top of each block follow the renders. '
            'RERA registers 43 units in block A and 62 in block B but does not say which block is which on the plot, so they are named north and south here.' + SURR)
    return cfg_base(p, base, fr, T, units, st, 4.2, note, local(fr, R['poly']), kind='commercial', perFloorLabel='Units on each floor', height=51,
                    startFloor='Floor 6', enqLabel='Enquire about this floor', clear=[local(fr, R['poly'])])

# ------------------------------------------------------------------ Center Point
CP_SHOPS = {   # ground-floor shops on Adani Realty's ground-floor plan (plan pixels, 10 px = 1 m), numbered as on the plan and the RERA unit list
  '01': (418, 468, 575, 520), '02': (418, 413, 575, 468), '03': (418, 358, 617, 413), '04': (418, 302, 617, 358), '05': (418, 245, 617, 302),
  '06': (418, 195, 617, 245), '07': (418, 143, 617, 195), '08': (418, 92, 550, 143), '09': (714, 130, 797, 192), '10': (797, 92, 832, 198),
  '11': (832, 92, 868, 198), '12': (868, 92, 905, 198), '13': (940, 195, 1140, 540), '14': (770, 467, 930, 522), '15': (770, 412, 930, 467),
  '16': (770, 360, 930, 412), '17': (770, 305, 930, 360), '18': (770, 255, 935, 305)}
CP_SIZE = {'01': '15.24 × 5.48 m', '02': '15.37 × 5.48 m', '03': '19.85 × 5.20 m', '04': '19.85 × 5.20 m', '05': '19.85 × 5.53 m', '06': '19.90 × 4.88 m',
           '07': '19.90 × 5.13 m', '08': '13.25 × 5.13 m + 6.65 × 3.33 m', '09': '8.55 × 6.00 m', '10': '3.38 × 10.61 m', '11': '3.51 × 10.61 m', '12': '3.85 × 10.61 m',
           '13': 'large hall on the south-west side (about 19.5 × 19.6 m plus its wings)', '14': '10.05 × 5.48 m + 5.94 × 5.58 m', '15': '16.09 × 5.48 m', '16': '16.40 × 5.20 m',
           '17': '16.40 × 5.20 m', '18': '16.40 × 5.58 m'}

def center_point(p, base):
    import gmfit as G
    R = RERA['center-point']; P = R['poly']; o = tuple(P[0])
    prm, res = G.fit([[325, 25, *P[2]], [1275, 25, *P[3]], [1275, 695, *P[0]], [325, 695, *P[1]]], o)
    ll = lambda q: G.to_ll(prm, o, *q)
    fr = frame_ll(P)
    U = [(405, 85), (1140, 85), (1140, 545), (770, 545), (770, 245), (625, 245), (625, 545), (405, 545)]
    rect = lambda r: [(r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3])]
    st = [dict(label='Ground floor', kind='A', h=5.0), dict(label='Floor 1', kind='A', h=5.0), dict(label='Floor 2', kind='A', h=5.0), dict(label='Floor 3', kind='A', h=5.0)]
    t = SH.tower(fr, 'T1', 'Center Point', [ll(q) for q in U], st, 'all', crown=dict(type='cap', h=0.8))
    cl = lambda poly_px: to_tower_local(fr, t, [ll(q) for q in poly_px])
    from shapely.geometry import Polygon, box
    g0 = [k for k in sorted(CP_SHOPS)]
    st[0]['plan'] = dict(cells=[cl(rect(CP_SHOPS[k])) for k in g0], ft=['g' + k for k in g0]); st[0]['nos'] = ['Shop-' + k for k in g0]
    # floors 1-3: the brochure plans predate the 2025 revision registered on RERA, so shops sit indicatively in the U-shaped floor
    upper = Polygon(U); mplex = box(405, 85, 625, 545); rest = upper.difference(mplex)
    # the latest quarterly unit list on Gujarat RERA (Form 3, Oct 2026): shops 101-120 on floor 1, 201-212 and 301-312 beside the multiplex on floors 2 and 3
    f1 = split_cells(list(upper.exterior.coords)[:-1], 20)
    st[1]['plan'] = dict(cells=[cl(c) for c in f1]); st[1]['nos'] = [f'Shop-1{i:02d}' for i in range(1, 21)]
    rest_pts = list(rest.exterior.coords)[:-1]
    f2 = [rect((405, 85, 625, 545))] + split_cells(rest_pts, 12)
    st[2]['plan'] = dict(cells=[cl(c) for c in f2], ft=['mx'] + [None] * 12); st[2]['nos'] = ['Multiplex 1–4'] + [f'Shop-2{i:02d}' for i in range(1, 13)]
    f3 = [rect((405, 85, 625, 545))] + split_cells(rest_pts, 12)
    st[3]['plan'] = dict(cells=[cl(c) for c in f3], ft=['mx'] + [None] * 12); st[3]['nos'] = ['Multiplex 1–4 (upper level)'] + [f'Shop-3{i:02d}' for i in range(1, 13)]
    MX = 4 * 289.5825      # four multiplex units of 289.58 sq m carpet each, registered across floors 2 and 3
    for L_ in (st[2], st[3]):
        L_['frows'] = [[['RERA carpet (4 screens together)', f'{MX:,.2f} sq m ({MX * 10.7639:,.0f} sq.ft.)'], ['Registered as', 'Multiplex 1, 2, 3 and 4, each 289.58 sq m, across floors 2 and 3 (Gujarat RERA)']]] + [None] * 12
    t['stack'] = st
    ftypes = {('g' + k): dict(name=f'Shop {k} · ground floor', short='G', exact=True, rows=[['Shop', f'Shop-{k} on Adani Realty’s ground-floor plan'], ['Size on the plan', CP_SIZE[k]], ['Offered', 'On long lease (Adani Realty)']]) for k in g0}
    ftypes.update(mx=dict(name='Multiplex (4 screens)', short='Cinema', rows=[['Use', 'Multiplex 1–4, registered across the second and third floors (Gujarat RERA)'], ['Where', 'The cinema block on the road corner, as on the Adani Realty renders']]),
)
    units = {'all': SH.u('Center Point · shops and showrooms', 'Shops & showrooms',
        [['Size', '273.83 – 6,742.29 sq.ft. RERA carpet'], ['Offered', 'On long lease only (Adani Realty)'],
         ['Registered', 'Shops 01–18 (ground), 101–120 (first), 201–212 (second), 301–312 (third) and multiplex screens 1–4 across the second and third floors: 66 units (Gujarat RERA quarterly unit list, Oct 2026)'],
         ['Status', 'BU received (Adani Realty)'], ['RERA', 'PR/GJ/AHMEDABAD/AHMEDABAD CITY/Ahmedabad Urban Development Authority/CAA13080/A1C/EX1/080725/300925']])}
    ctx = [dict(t='flat', p=to_tower_local(fr, dict(x=0, y=0), [ll(q) for q in rect((625, 245, 770, 545))]), c='#8d97a6', z=0.6),
           dict(t='label', text='Atrium', **dict(zip(('x', 'y'), [round(v, 1) for v in SH.loc(fr, *ll((697, 395)))])), z=8, size=7)]
    note = ('Center Point: a ground + 3 retail building on the 6,484 sq m plot registered on the Gujarat RERA map service, laid out from Adani Realty’s ground-floor plan '
            '(fitted to the RERA plot, which it matches within about 1 m): shops on three sides of the open atrium facing the 24 m road, the 34.5 m road on the cinema side. '
            'Ground-floor shops are drawn exactly as on that plan. The upper floors follow the latest quarterly unit list on Gujarat RERA (20 first-floor shops, 12 shops each on floors 2 and 3 '
            'and the four-screen multiplex across floors 2 and 3, 66 units in all); the brochure’s older upper-floor plans no longer match it, so those units are placed indicatively.' + SURR)
    return cfg_base(p, base, fr, [t], units, st, 5.0, note, local(fr, P), kind='commercial', perFloorLabel='Units on each floor', ftypes=ftypes, flatWord='',
                    startFloor='Ground floor', enqLabel='Enquire about this unit', context=ctx, clear=[local(fr, P)],
                    cellsNote='Indicative position: Adani Realty has not published plans for the revised upper floors.')

# ------------------------------------------------------------------ Amora
def amora(p, base):
    import gmfit as G, numpy as np
    from shapely.geometry import Polygon
    R = RERA['amora']; fr = frame_ll(R['poly'])
    M = json.load(open(os.path.join(HERE, 'newimg', 'sat_amora20.meta.json')))
    c_ll = G.px2ll(M, 434, 292)                       # centre of the cleared site on current satellite imagery
    o = tuple(c_ll); ang = math.radians(30); ca, sa = math.cos(ang), math.sin(ang); S = 1 / 22.0
    def f3(q):                                        # third-floor plan px -> lat/lon
        x, y = (q[0] - 746) * S, -(q[1] - 610) * S
        return G.ll(o, x * ca - y * sa, x * sa + y * ca)
    # typical floor plan -> third-floor plan (both lift cores)
    A1, A2 = np.array([242, 357.]), np.array([865, 945.]); B1, B2 = np.array([447, 392.]), np.array([989, 902.])
    va, vb = A2 - A1, B2 - B1; k = np.linalg.norm(vb) / np.linalg.norm(va); th = math.atan2(vb[1], vb[0]) - math.atan2(va[1], va[0])
    def ft(q):
        d = (np.array(q, float) - A1) * k; d = np.array([d[0] * math.cos(th) - d[1] * math.sin(th), d[0] * math.sin(th) + d[1] * math.cos(th)]); return f3(B1 + d)
    rect = lambda r: [(r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3])]
    BO = [(120, 50), (580, 50), (580, 330), (520, 330), (520, 425), (580, 425), (580, 715), (120, 715), (120, 425), (215, 425), (215, 335), (120, 335)]
    AO = [(540, 595), (815, 595), (815, 670), (915, 670), (915, 620), (1195, 620), (1195, 1085), (915, 1085), (915, 960), (815, 960), (815, 1085), (540, 1085)]
    CB = {'03': rect((120, 50, 345, 330)), '04': rect((345, 50, 580, 330)), '02': rect((120, 425, 345, 715)), '01': rect((345, 425, 580, 715))}
    CA = {'04': rect((540, 595, 815, 860)), '01': rect((915, 620, 1195, 860)), '03': rect((540, 860, 815, 1085)), '02': rect((915, 860, 1195, 1085))}
    arc = [(228 + 400 - 400 * math.cos(a_), 1095 - 400 + 400 * math.sin(a_)) for a_ in np.linspace(0, math.pi / 2, 9)][::-1]
    POD = [(228, 125), (740, 125), (740, 575), (950, 575), (950, 610), (1265, 610), (1265, 1095)] + arc[:-1] + [(228, 680)]
    POD = [(228, 125), (740, 125), (740, 575), (950, 575), (950, 610), (1265, 610), (1265, 1095), (628, 1095)] + [(228 + 400 - 400 * math.sin(t), 695 + 400 * math.cos(t)) for t in np.linspace(0, math.pi / 2, 10)] + [(228, 125)][:0]
    hP = 4.5
    def stack_for(blk, cells):
        st = [dict(label='Ground floor', kind='M', h=hP, use=f'Block {blk} entrance lobby (residential entry and drop-off on the plot’s north side)')]
        one = '101' if blk == 'A' else '104'; pos = '01' if blk == 'A' else '04'
        for f in (1, 2):
            no = f'{blk}-{f}{one[1:]}'
            st.append(dict(label=f'Floor {f}', kind='A', h=hP, nos=[no], plan=dict(cells=[cells[pos]], ft=['h3']), note='One home of this block on this floor, above the shops'))
        three = ['01', '02', '03'] if blk == 'A' else ['02', '03', '04']
        st.append(dict(label='Floor 3', kind='A', nos=[f'{blk}-3{x}' for x in three], plan=dict(cells=[cells[x] for x in three], ft=['h3'] * 3),
                       note='Podium terrace level: ' + ('gym' if blk == 'A' else 'games room') + ' in the fourth corner of the block, open-air terrace with lawn, plaza and outdoor gym (Adani Realty plan)'))
        for f in range(4, 14):
            st.append(dict(label=f'Floor {f}', kind='A', nos=[f'{blk}-{f}{x}' for x in ('01', '02', '03', '04')], plan=dict(cells=[cells[x] for x in ('01', '02', '03', '04')], ft=['h3'] * 4)))
        return st
    T = []
    for blk, out, cells in (('A', AO, CA), ('B', BO, CB)):
        ll = [ft(q) for q in out]
        t = SH.tower(fr, 'T' + blk, f'Block {blk}', ll, None, 'res', crown=dict(type='cap', h=2.5))
        cl = {k_: to_tower_local(fr, t, [ft(q) for q in v]) for k_, v in cells.items()}
        t['stack'] = stack_for(blk, cl)
        # inside the podium (ground to floor 2) a block is its lift lobby plus, on floors 1 and 2, its one home; the full block starts at floor 3
        core = to_tower_local(fr, t, [ft(q) for q in (rect((215, 330, 520, 425)) if blk == 'B' else rect((815, 670, 915, 960)))])
        home = Polygon(core).union(Polygon(cl['01' if blk == 'A' else '04']).buffer(0.01)).convex_hull
        full = t['pts']
        t['pts'] = core
        t['tiers'] = [{'from': 1, 'pts': [[round(x, 2), round(y, 2)] for x, y in list(home.exterior.coords)[:-1]]}, {'from': 3, 'pts': full}]
        T.append(t)
    # retail podium: ground + 2 shop floors around the blocks' cores
    pod = Polygon(POD).buffer(0)
    for t in T: pod = pod.difference(Polygon([(t['x'] + a_, t['y'] + b_) for a_, b_ in t['pts']]).buffer(0.3)) if False else pod
    pod_ll = [f3(q) for q in list(pod.exterior.coords)[:-1]]
    tp = SH.tower(fr, 'TP', 'Retail podium', pod_ll, None, 'shop', nolabel=True, crown=dict(type='none'))
    # remove the residential blocks' ground floors from the podium outline (in the site frame)
    loc_pts = [(a_, b_) for a_, b_ in tp['pts']]
    sh = lambda n: [[[round(x, 2), round(y, 2)] for x, y in c] for c in split_cells(loc_pts, n)]
    tp['stack'] = [dict(label='Ground floor', kind='A', h=hP, nos=[str(i) for i in range(1, 15)], plan=dict(cells=sh(14))),
                   dict(label='Floor 1', kind='A', h=hP, nos=[str(100 + i) for i in range(1, 13)], plan=dict(cells=sh(12))),
                   dict(label='Floor 2', kind='A', h=hP, nos=[str(200 + i) for i in range(1, 13)], plan=dict(cells=sh(12)))]
    T.append(tp)
    ftypes = dict(h3=dict(name='3 BHK apartment', short='3 BHK', exact=True, rows=[['Home', '3 BHK: living room, dining, kitchen with utility, three bedrooms, three toilets, balcony (Adani Realty unit plans)'],
                  ['Size', '1,042.17 – 1,088.35 sq.ft. (RERA carpet + exclusive area); Adani Realty does not publish the size flat by flat'], ['Price', 'From ₹1.45 Cr* all inclusive (Adani Realty)']]))
    units = {'res': SH.u('Amora · 3 BHK apartments', '3 BHK', [['Homes', '90 × 3 BHK in blocks A and B (Gujarat RERA)']]),
             'shop': SH.u('Amora · high-street retail', 'Retail', [['Shops', '38: 14 on the ground floor, 12 each on floors 1 and 2 (Gujarat RERA unit list)'], ['Size', '268.02 – 1,237 sq.ft. (RERA carpet + exclusive area)'],
                                                                  ['Access', 'Separate retail entry and basement (Adani Realty)']])}
    note = ('Amora: two residential blocks (A and B, ground + 13) set as an L on a three-level retail podium with a curved corner at the road junction, '
            'and an open-air terrace with lawn, plaza and outdoor gym on the podium roof (floor 3). Block outlines and the position of every flat are from Adani Realty’s typical floor plan '
            '(floors 5, 7, 9, 11, 13) and third-floor plan; flat numbers from the Gujarat RERA unit list (4 homes per floor on floors 4–13, three on floor 3, one per block on floors 1 and 2). '
            'The building is placed on the site cleared for it on current satellite imagery (the plot drawn on the RERA map service also takes in the roadside). '
            'Shop positions on the podium floors are indicative.' + SURR)
    ctx = []
    st0 = T[0]['stack']
    return cfg_base(p, base, fr, T, units, st0, 3.15, note, local(fr, R['poly']), ftypes=ftypes, height=48, startFloor='Floor 8', clear=[local(fr, R['poly'])], flatWord='Flat',
                    cellsNote='Indicative position: the retail floor plans are not georeferenced flat by flat.')

# ------------------------------------------------------------------ The Storeys Golf Coast
def golf_coast(p, base):
    from shapely.geometry import Polygon, box
    from shapely import affinity
    R = RERA['golf-coast']; fr = frame_ll(R['poly']); L = json.load(open(os.path.join(HERE, 'gm', 'gc_ll.json')))
    rows_s = [['Home', '4 BHK simplex: the whole floor is one home, with private lift foyer (Adani Realty)'],
              ['Size', 'RERA carpet 3,501 sq.ft.; balcony 297 and wash area 67; total RERA area 3,865 sq.ft. (Adani Realty unit plan)'], ['Parking', '4 car parks per home (Adani Realty)']]
    ftypes = dict(s4=dict(name='4 BHK simplex (South tower)', short='4 BHK', exact=True, rows=rows_s),
                  dA=dict(name='5 BHK duplex, type A (west half)', short='5 BHK duplex A', exact=True,
                          rows=[['Home', '5 BHK duplex over two floors (lower and upper level), the west half of the North tower, facing the Narmada canal and the golf course'],
                                ['Size', 'RERA carpet 4,664 sq.ft.; balcony 211 and wash area 104; total RERA area 4,979 sq.ft. (Adani Realty unit plan)']]),
                  dB=dict(name='5 BHK duplex, type B (east half)', short='5 BHK duplex B', exact=True,
                          rows=[['Home', '5 BHK duplex over two floors (lower and upper level), the east half of the North tower, facing the Narmada canal and the golf course'],
                                ['Size', 'RERA carpet 4,509 sq.ft.; balcony 212 and wash area 99; total RERA area 4,820 sq.ft. (Adani Realty unit plan)']]),
                  ph=dict(name='Penthouse over floors 19 and 20 (South tower)', short='Penthouse', exact=True,
                          rows=[['Home', 'B-19, the top home of the South tower: its registered carpet area is larger than a whole typical floor and the fire-safety opinion lists floor 20 as residential, so it is drawn over floors 19 and 20']]))
    T = []
    # South tower (RERA block B): one 4 BHK per floor, B-02 to B-19
    GC = dict(g=4.65, f1=4.45, t=3.45)      # AMC fire-safety opinion (both towers): ground 4.65 m, floor 1 4.45 m, floors 2-20 3.45 m; 74.65 m to the top slab
    stS = [dict(label='Ground floor', kind='M', h=GC['g'], use='Entrance foyer with owner and guest lifts; parking and meter room; one basement of parking below'),
           dict(label='Floor 1 (podium)', kind='M', h=GC['f1'], use='Podium amenities around the green podium garden (Adani Realty podium plan)')]
    stS += [dict(label=f'Floor {f}', kind='A', h=GC['t'], nos=[f'B-{f:02d}'], plan=dict(ft=['s4'])) for f in range(2, 19)]
    stS += [dict(label='Floors 19–20 (penthouse)', kind='P', levels=2, h=2 * GC['t'], nos=['B-19'], plan=dict(ft=['ph']))]
    tS = SH.tower(fr, 'TB', 'South tower (B)', L['south'], stS, 'all', crown=dict(type='cap', h=2.5)); T.append(tS)
    # North tower (RERA block A): 5 BHK duplexes, type A on the west half and type B on the east half of each floor
    poly = Polygon(SH.tower(fr, 'x', 'x', L['north'], [], 'all')['pts'])
    tN = SH.tower(fr, 'TA', 'North tower (A)', L['north'], None, 'all', crown=dict(type='cap', h=2.5))
    P = Polygon(tN['pts']); x0, y0, x1, y1 = P.bounds
    # the tower's long axis runs east-west in the site frame: split it across the middle into west and east halves
    import math as _m
    rot = _m.radians(fr[2]); ex = (_m.cos(rot), -_m.sin(rot))      # east in the site frame
    def half(sign):
        big = 200; nx, ny = ex
        hp = Polygon([(0, 0), (sign * nx * big - ny * big, sign * ny * big + nx * big), (sign * nx * big + ny * big, sign * ny * big - nx * big)]).buffer(0)
        hp = Polygon([(-ny * big, nx * big), (ny * big, -nx * big), (ny * big + sign * nx * big, -nx * big + sign * ny * big), (-ny * big + sign * nx * big, nx * big + sign * ny * big)])
        g = P.intersection(hp); g = g if g.geom_type == 'Polygon' else max(g.geoms, key=lambda q: q.area)
        return [[round(a_, 2), round(b_, 2)] for a_, b_ in list(g.exterior.coords)[:-1]]
    W, Ehalf = half(-1), half(1)
    stN = [dict(label='Ground floor', kind='M', h=GC['g'], use='Entrance foyer with owner and guest lifts; parking and meter room; one basement of parking below'),
           dict(label='Floor 1 (podium)', kind='M', h=GC['f1'], use='Podium amenities: pool deck, gym, spa (Adani Realty podium plan)')]
    stN += [dict(label=f'Floor {f}', kind='A', h=GC['t'], nos=['Type A duplex (west)', 'Type B duplex (east)'], plan=dict(cells=[W, Ehalf], ft=['dA', 'dB']),
                 note='Each 5 BHK duplex spans two floors. The register numbers them A-02 to A-18 over floors 2–20 but does not publish which floor pair each number is on.') for f in range(2, 21)]
    tN['stack'] = stN; T.append(tN)
    hull = Polygon([(t['x'] + a_, t['y'] + b_) for t in T for a_, b_ in t['pts']]).convex_hull
    hull = Polygon([(t['x'] + a_, t['y'] + b_) for t in T for a_, b_ in t['pts']])
    from shapely.geometry import MultiPoint
    hull = MultiPoint([(t['x'] + a_, t['y'] + b_) for t in T for a_, b_ in t['pts']]).convex_hull.buffer(-0.6)
    ctx = [dict(t='prism', p=[[round(a_, 2), round(b_, 2)] for a_, b_ in list(hull.exterior.coords)[:-1]], h=7.0, c='#5f7766', label='Podium garden and amenities', size=7)]
    units = {'all': SH.u('The Storeys Golf Coast', '4 & 5 BHK', [['Homes', '35: in the South tower 17 × 4 BHK simplex (B-02 to B-18) and the penthouse B-19 over floors 19–20; in the North tower 17 × 5 BHK duplexes (A-02 to A-18) (Gujarat RERA unit list)'],
             ['RERA', 'PR/GJ/AHMEDABAD/AHMEDABAD CITY/Ahmedabad Urban Development Authority/RAA14971/170325/311228']])}
    note = ('The Storeys Golf Coast: two towers on a shared podium beside the Narmada canal and the Belvedere golf course. The North tower (RERA block A) holds the 5 BHK duplexes '
            'and faces the canal; the South tower (block B) has one 4 BHK simplex on each floor. Tower outlines and the 22 m gap between them are measured on current satellite imagery '
            '(the towers are standing; roofs are shifted back for the camera’s lean) and agree with Adani Realty’s site and podium plans; floors from the RERA unit numbers '
            '(homes on floors 2 to 20 above the entrance level and the podium amenity floor; the South tower’s top home, B-19, is larger than a whole floor and is drawn over floors 19 and 20). '
            'Floor heights are from the Ahmedabad fire-safety opinion filed on Gujarat RERA (the same for both towers): ground floor 4.65 m, floor 1 4.45 m and 3.45 m for each of floors 2 to 20, '
            '74.65 m from ground level to the top slab. Sizes from Adani Realty’s unit plans.' + SURR)
    return cfg_base(p, base, fr, T, units, stS, GC['t'], note, local(fr, R['poly']), ftypes=ftypes, flatWord='', startFloor='Floor 10', clear=[local(fr, R['poly'])],
                    enqLabel='Enquire about this home', context=ctx, height=74.65, hSrc='AMC fire-safety opinion filed on Gujarat RERA')

# ------------------------------------------------------------------ The Storeys (the golf-view towers, completed)
def storeys(p, base):
    import gmfit as G
    R = RERA['storeys']; fr = frame_ll(R['poly'])
    M = json.load(open(os.path.join(HERE, 'newimg', 'sat_storeys20b.meta.json' if os.path.exists(os.path.join(HERE, 'newimg', 'sat_storeys20b.meta.json')) else 'sat_st20b.meta.json')))
    mid = tuple(G.px2ll(M, 399.5, 418)); ang = math.radians(-32); ca, sa = math.cos(ang), math.sin(ang)
    def f(q):
        x, y = (q[0] - 608.5) / 15.0, -(q[1] - 493.5) / 15.0
        return G.ll(mid, x * ca - y * sa, x * sa + y * ca)
    rect = lambda r: [(r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3])]
    W_, E_ = (180, 365, 555, 625), (695, 365, 1020, 625)
    tW = SH.tower(fr, 'TA', 'West tower (A)', [f(q) for q in rect(W_)], None, 'all', crown=dict(type='cap', h=2.5))
    tE = SH.tower(fr, 'TB', 'East tower (B)', [f(q) for q in rect(E_)], None, 'all', crown=dict(type='cap', h=2.5))
    cl = lambda t, r: to_tower_local(fr, t, [f(q) for q in rect(r)])
    left, right = cl(tW, (W_[0], W_[1], (W_[0] + W_[2]) / 2, W_[3])), cl(tW, ((W_[0] + W_[2]) / 2, W_[1], W_[2], W_[3]))
    s01 = [(2, 3), (4, 5), (6, 7), (8, 9), (10, 11), (12, 13), (14, 15), (16, 17, 18)]
    s02 = [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10), (11, 12), (13, 14), (15, 16), (17, 18)]
    name = lambda fl: 'A-' + '-'.join(f'{x}0{1 if fl in s01 else 2}' for x in fl)
    stW = [dict(label='Ground floor', kind='M', use='Entrance lobby, double-height pool, gym, deck and multipurpose hall (Adani Realty master layout)')]
    for fno in range(1, 19):
        a1 = next((u for u in s01 if fno in u), None); a2 = next((u for u in s02 if fno in u), None)
        nos, cells, ft = [], [], []
        if a2: nos.append(name(a2) if a2 in s02 else ''); cells.append(left); ft.append('tri' if len(a2) == 3 else 'dup')
        if a1: nos[len(nos):] = [ 'A-' + '-'.join(f'{x}01' for x in a1)]; cells.append(right); ft.append('tri' if len(a1) == 3 else 'dup')
        nos = [n.replace('A-', 'A-') for n in nos]
        stW.append(dict(label=f'Floor {fno}', kind='A', nos=nos, plan=dict(cells=cells, ft=ft)))
    for L in stW[1:]:
        L['nos'] = [n if n else '' for n in L['nos']]
    # rebuild 02-side names correctly (the helper above names both sides from the 01 list)
    for L in stW[1:]:
        fno = int(L['label'].split()[-1]); a2 = next((u for u in s02 if fno in u), None); a1 = next((u for u in s01 if fno in u), None)
        L['nos'] = ([ 'A-' + '-'.join(f'{x}02' for x in a2)] if a2 else []) + ([ 'A-' + '-'.join(f'{x}01' for x in a1)] if a1 else [])
    tW['stack'] = stW
    tE['stack'] = [dict(label='Ground floor', kind='M', use='Entrance foyer with lifts; stilt parking')] + [dict(label=f'Floor {fno}', kind='A', nos=[f'B-{fno}01'], plan=dict(ft=['sim'])) for fno in range(1, 19)]
    for L in stW + tE['stack']: L['h'] = 3.65      # AMC fire-safety opinion (both towers): ground and floors 1-18 3.65 m each; 75.15 m to the top slab
    ftypes = dict(dup=dict(name='Duplex home (West tower)', short='Duplex', exact=True, rows=[['Home', 'Duplex over two floors with a 23 ft double-height living room; the two duplexes of the tower interlock floor by floor (Gujarat RERA unit numbers)']]),
                  tri=dict(name='Top home over three floors (West tower)', short='Triplex', exact=True, rows=[['Home', 'A-1601-1701-1801: the top home of the West tower runs over floors 16, 17 and 18 (Gujarat RERA)']]),
                  sim=dict(name='Single-storey home (East tower)', short='Simplex', exact=True, rows=[['Home', 'One home on the whole floor, with private lift foyer (Adani Realty)']]))
    units = {'all': SH.u('The Storeys', '4 & 5 BHK', [['Homes', '35: 18 single-storey homes in the East tower (B-101 to B-1801) and 17 duplex homes in the West tower (Gujarat RERA unit list)'],
             ['Size', '3,541.76 – 5,997.76 sq.ft. RERA carpet; 6,560 and 7,575 sq.ft. super built-up (Adani Realty)'], ['Status', 'Completed (Adani Realty)'],
             ['RERA', 'PR/GJ/AHMEDABAD/AHMEDABAD CITY/AUDA/RAA08162/090321']], avail='Ask for resale availability')}
    note = ('The Storeys by Adani Realty and UB Heritage: two towers of ground + 18 floors beside the 34.5 m road on the golf course, 35 homes. The West tower holds 17 interlocking duplexes '
            '(each RERA unit number names its floors, e.g. A-201-301, and the top home A-1601-1701-1801 spans three floors); the East tower has one home per floor. '
            'Tower outlines and the gap between them are from Adani Realty’s master layout; their position and alignment are taken from current satellite imagery of the completed towers '
            '(the plot drawn on the RERA map service sits about 25 m north-west of them). Which side of the West tower carries the 01 and 02 numbers is not marked on the published plans. '
            'Floor heights are from the Ahmedabad fire-safety opinion filed on Gujarat RERA (the same for both towers): 3.65 m for the ground floor and each of floors 1 to 18, so the roof of floor 18 is 69.35 m up; '
            'the opinion gives 75.15 m from ground level to the top slab.' + SURR)
    return cfg_base(p, base, fr, [tW, tE], units, stW, 3.65, note, local(fr, R['poly']), ftypes=ftypes, flatWord='', startFloor='Floor 9', enqLabel='Enquire about this home',
                    cellsNote='The 01 / 02 sides of the West tower are drawn indicatively.', hSrc='AMC fire-safety opinion filed on Gujarat RERA')

# ------------------------------------------------------------------ The Storeys Infinity
def infinity(p, base):
    import gmfit as G
    R = RERA['infinity']; P = R['poly']; o = tuple(P[0]); fr = frame_ll(P)
    prm, res = G.fit([[187, 215, *P[2]], [905, 140, *P[1]], [905, 745, *P[5]], [187, 745, *P[4]]], o)
    f = lambda q: G.to_ll(prm, o, *q)
    rect = lambda r: [(r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3])]
    def H(x0, y0, x1, y1, ty1, by0, cx0, cx1):      # H-shaped tower: top wing, bottom wing, core between
        return [(x0, y0), (x1, y0), (x1, ty1), (cx1, ty1), (cx1, by0), (x1, by0), (x1, y1), (x0, y1), (x0, by0), (cx0, by0), (cx0, ty1), (x0, ty1)]
    D = {'East tower': ((240, 365, 480, 625, 465, 520, 318, 405), 'TE'), 'West tower': ((610, 270, 850, 525, 380, 428, 683, 775), 'TW')}
    ftypes = dict(h4=dict(name='4 BHK apartment', short='4 BHK', exact=True, rows=[['Home', '4 BHK, one of four on the floor, lift opening into a private foyer, staff quarters, 11 ft slab height (Adani Realty)'], ['Size', 'From 2,422 sq.ft. (Adani Realty: unit sizes 2,422 – 5,019 sq.ft.)'], ['Price', 'From ₹3.5 Cr* all inclusive (Adani Realty)']]),
                  cy=dict(name='4 BHK courtyard home', short='Courtyard', exact=True, rows=[['Home', '4 BHK courtyard home at podium level with a private garden; two in the project, both in the East tower (Adani Realty; RERA units 103 and 104)']]),
                  ph=dict(name='5 BHK penthouse', short='5 BHK PH', exact=True, rows=[['Home', '5 BHK penthouse with a private terrace; eight in all, four on top of each tower (Adani Realty)'], ['Size', 'Up to 5,019 sq.ft. (Adani Realty)']]))
    T = []
    for lab, (g, tid) in D.items():
        x0, y0, x1, y1, ty1, by0, cx0, cx1 = g; xm = (x0 + x1) / 2
        t = SH.tower(fr, tid, lab, [f(q) for q in H(*g)], None, 'all', crown=dict(type='frame', h=5))
        c = {'01': rect((x0, y0, xm, ty1)), '02': rect((xm, y0, x1, ty1)), '04': rect((x0, by0, xm, y1)), '03': rect((xm, by0, x1, y1))}
        cl = {k: to_tower_local(fr, t, [f(q) for q in v]) for k, v in c.items()}
        pre = 'E' if lab.startswith('East') else 'W'
        st = [dict(label='Ground floor', kind='M', h=4.5, use='Entrance, reception and stilt parking (Adani Realty site plan)')]
        if pre == 'E': st.append(dict(label='Floor 1 (podium)', kind='A', nos=['E-103', 'E-104'], plan=dict(cells=[cl['03'], cl['04']], ft=['cy', 'cy']), note='Podium level: the two courtyard homes; the green podium garden is beside them'))
        else: st.append(dict(label='Floor 1 (podium)', kind='M', use='Podium level: amenities beside the 25,000 sq.ft. green podium (pool, gym, games room, theatre, crèche: Adani Realty)'))
        floors = list(range(2, 13)) + ['12A'] + list(range(14, 20))
        for fl in floors:
            n = '12' if fl == '12A' else str(fl); suf = 'A' if fl == '12A' else ''
            st.append(dict(label=f'Floor {fl}', kind='A', nos=[f'{pre}-{n}0{k}{suf}' for k in '1234'], plan=dict(cells=[cl[k] for k in ('01', '02', '03', '04')], ft=['h4'] * 4),
                           **({'note': 'Floor 12A: the register numbers this floor 1201A–1204A, as there is no floor 13'} if fl == '12A' else {})))
        st.append(dict(label='Floors 20–21 (penthouses)', kind='P', levels=2, unit='all', nos=[f'{pre}-200{k}' for k in '1234'], plan=dict(cells=[cl[k] for k in ('01', '02', '03', '04')], ft=['ph'] * 4)))
        st.append(dict(label='Terrace', kind='M', use='Developed terrace with the crown frame (15,500 sq.ft. across the towers, Adani Realty)'))
        t['stack'] = st; T.append(t)
    units = {'all': SH.u('The Storeys Infinity', '4 BHK + 5 BHK PH', [['Homes', '154: 4 BHK apartments, two courtyard homes and eight 5 BHK penthouses in the East and West towers (Gujarat RERA)'],
             ['Architect', 'Apurva Amin Architects (Adani Realty)'], ['Completion', 'December 2031 (RERA)']])}
    note = ('The Storeys Infinity: twin H-shaped towers (East and West) beside The Storeys Golf Coast, laid out from Adani Realty’s block plans, which fit the plot registered on the Gujarat RERA map service within about 5 m. '
            'Each tower has two wings of two homes joined by the lift core: four 4 BHK homes on every floor from 2 to 19 (the register calls the 13th floor 12A), the two courtyard homes on the East tower’s podium level, '
            'four 5 BHK penthouses over floors 20 and 21 of each tower, and the developed terrace with its crown frame on top, as on the renders. Flat numbers and positions are from the block plans and the RERA unit list.' + SURR)
    return cfg_base(p, base, fr, T, units, T[0]['stack'], 3.35, note, local(fr, P), ftypes=ftypes, flatWord='', startFloor='Floor 10', enqLabel='Enquire about this home', clear=[local(fr, P)])

# ------------------------------------------------------------------ Navratna Gulmohar Park (mixed-use tower, Iscon Cross Road)
def gulmohar(p, base):
    C = json.loads(json.dumps(base))
    rect = lambda w, d, dx=0, dy=0: [[round(dx - w / 2, 2), round(dy - d / 2, 2)], [round(dx + w / 2, 2), round(dy - d / 2, 2)], [round(dx + w / 2, 2), round(dy + d / 2, 2)], [round(dx - w / 2, 2), round(dy + d / 2, 2)]]
    P = C['plotPoly']; cx = sum(q[0] for q in P) / len(P); cy = sum(q[1] for q in P) / len(P)
    base_w, base_d = 70, 40; off_w, off_d = 48, 34; res_w, res_d = 32, 30
    import shapely.geometry as SG_
    sp = lambda pts: [[round(x, 2), round(y, 2)] for x, y in pts]
    st = [dict(label='Ground floor', kind='A', h=5.0, nos=['Shop 1', 'Shop 2', 'Shop 3', 'Shop 4'], plan=dict(cells=split_cells(rect(base_w, base_d), 4, rows=1)), unit='shop',
               note='Retail frontage on the main road with the commercial lobby (INI Design Studio)'),
          dict(label='Floor 1', kind='A', h=4.5, nos=['Shop 101'], plan=dict(cells=[rect(base_w, base_d)]), unit='shop', note='Retail podium'),
          dict(label='Floor 2', kind='A', h=4.5, nos=[f'{200 + i}' for i in range(1, 6)], plan=dict(cells=split_cells(rect(base_w, base_d), 5, rows=1)), unit='office', note='Retail podium level with five offices (Gujarat RERA)'),
          dict(label='Floor 3', kind='A', h=4.2, nos=[f'{300 + i}' for i in range(1, 11)], plan=dict(cells=split_cells(rect(base_w, base_d), 10)), unit='office', note='Top of the four-level (G+3) podium')]
    for f_ in range(4, 17):
        if f_ == 9: st.append(dict(label='Floor 9', kind='S', h=4.2, use='No unit is registered on floor 9: refuge / services floor')); continue
        if f_ == 16: st.append(dict(label='Floor 16', kind='S', h=4.2, use='No unit is registered on floor 16: services / transfer floor below the amenity level')); continue
        st.append(dict(label=f'Floor {f_}', kind='A', h=4.2, unit='office', nos=[f'{f_}{i:02d}' for i in range(1, 11)], plan=dict(cells=split_cells(rect(off_w, off_d), 10))))
    st.append(dict(label='Floor 17 (amenities)', kind='M', h=5.0, use='Amenity floor: reception and waiting lounge, banquet, indoor swimming pool, gym, game room (INI Design Studio), with the terrace on the office block’s roof'))
    for f_ in range(18, 37):
        st.append(dict(label=f'Floor {f_}', kind='A', h=3.6, unit='home', nos=[f'{f_}01', f'{f_}02'], plan=dict(cells=split_cells(rect(res_w, res_d), 2))))
    st.append(dict(label='Floors 37–38 (sky villas)', kind='P', levels=2, h=8.2, unit='home', nos=['3701', '3702'], plan=dict(cells=split_cells(rect(res_w, res_d), 2), ft=['sv', 'sv']),
                   note='The pair of sky villas at the top: double-height spaces, private terraces and glass pavilions (INI Design Studio); RERA lists them as 3701 and 3702'))
    t = dict(id='T1', label='Gulmohar Park', x=round(cx, 1), y=round(cy, 1), w=base_w, d=base_d, ang=0, pts=rect(base_w, base_d), type='office', stack=st,
             tiers=[{'from': 4, 'pts': rect(off_w, off_d)}, {'from': 17, 'pts': rect(res_w, res_d)}], crown=dict(type='cap', h=3))
    units = {'office': SH.u('Gulmohar Park · offices', 'Offices', [['Offices', '125, about 1,410 sq.ft. average RERA carpet; floors 2–8 and 10–15 (Gujarat RERA unit list)']], avail=p.get('available'), word='offices'),
             'shop': SH.u('Gulmohar Park · retail', 'Retail', [['Shops', '5, about 4,930 sq.ft. average RERA carpet: four on the ground floor, one on floor 1 (Gujarat RERA unit list)']], avail=p.get('available'), word='shops'),
             'home': SH.u('Gulmohar Park · residences', 'Residences', [['Homes', '40, about 5,640 sq.ft. average RERA carpet: two per floor on floors 18–36 and the two sky villas on top (Gujarat RERA unit list)']], avail=p.get('available'))}
    ftypes = dict(sv=dict(name='Sky villa', short='Sky villa', exact=True, rows=[['Home', 'Double-height sky villa with private terrace and glass pavilion, one of the pair on top of the tower (INI Design Studio)']]))
    C.update(towers=[t], units=units, stack=st, ftypes=ftypes, flatWord='', startFloor='Floor 10', kind='mixed', height=161.5, floorH=4.2, camStay=True,
             note=('Navratna Gulmohar Park: one stepped mixed-use tower, 161.5 m (RERA) and 39 storeys (INI Design Studio): a four-level retail podium (ground to floor 3), '
                   'offices on floors 2–15 (floor 9 a refuge floor, floor 16 services), the amenity floor 17 with pool, banquet and gym, homes from floor 18 (two per floor) and a pair of double-height sky villas on top. '
                   'Floors and unit numbers are from the Gujarat RERA unit list (5 shops, 125 offices, 40 homes) and the uses per level from the architect, INI Design Studio. '
                   'Plot: the boundary registered on the RERA map service. The developer has not published floor plates, so the three volumes are sized from the registered carpet areas '
                   'in the proportions of the architect’s renders, and units sit indicatively on each floor. Surroundings are from OpenStreetMap.'),
             cellsNote='Indicative position: the developer has not published floor plans.', enqLabel='Enquire about this unit')
    for k in ('perFloor',): C.pop(k, None)
    C['plot'] = C.get('plot')
    return C

# ------------------------------------------------------------------ GIFT City projects (geometry relative to the GIFT City map origin)
from contextlib import contextmanager
@contextmanager
def gift_origin():
    old = SH.ORIGIN; SH.ORIGIN = (23.16, 72.6835)
    try: yield
    finally: SH.ORIGIN = old

def skyview(p, base):
    import gmfit as G, numpy as np
    from shapely.geometry import Polygon
    F = json.load(open(os.path.join(HERE, 'gm', 'sv_fit.json'))); prm, o = F['prm'], tuple(F['o'])
    ll = lambda q: G.to_ll(prm, o, *q)
    def arm(root, tip, w):
        r = np.array(root, float); t = np.array(tip, float); v = t - r; n = np.array([-v[1], v[0]]) / np.linalg.norm(v) * w / 2
        return [tuple(r + n), tuple(t + n), tuple(t - n), tuple(r - n)], (r, t, n)
    def halves(root, tip, w):
        r = np.array(root, float); t = np.array(tip, float); m = (r + t) / 2; v = t - r; n = np.array([-v[1], v[0]]) / np.linalg.norm(v) * w / 2
        inner = [tuple(r + n), tuple(m + n), tuple(m - n), tuple(r - n)]; outer = [tuple(m + n), tuple(t + n), tuple(t - n), tuple(m - n)]
        return inner, outer
    rect = lambda r: [(r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3])]
    ARMS = {'C': ((395, 228), (280, 140), 78), 'D': ((605, 228), (720, 140), 78), 'B': ((390, 405), (225, 510), 80), 'A': ((610, 405), (775, 500), 80)}
    MID = {'C': rect((410, 195, 500, 262)), 'D': rect((500, 195, 590, 262)), 'B': rect((390, 375, 500, 445)), 'A': rect((500, 375, 610, 445))}
    CORE = {'west': rect((320, 240, 425, 380)), 'east': rect((575, 240, 680, 380))}
    with gift_origin():
        allp = [ll(q) for q in rect((225, 140, 775, 510))]
        fr = frame_ll(allp)
        ftypes = dict(t3=dict(name='3 BHK (arm end)', short='3 BHK', rows=[['Home', '3 BHK at the end of an arm, the largest homes on the floor (the 3 BHK position is read from the plan; the developer’s unit plans published so far are the 2 BHK types)'],
                                                                         ['Size', 'About 1,335 sq.ft. carpet (Housiey); up to 1,524 sq.ft. RERA area (Shivalik)']]),
                      t1=dict(name='2 BHK · type 01 (arm, inner)', short='2 BHK', exact=True, rows=[['Home', '2 BHK on the inner half of an arm, balcony access from every room (Shivalik unit plan, type 01: B-202 and its mirror positions)'],
                                                                                          ['Size', '870.01 sq.ft. RERA carpet + balcony + wash; 1,582 sq.ft. indicative super built-up']]),
                      t4=dict(name='2 BHK · type 04 (central block)', short='2 BHK', exact=True, rows=[['Home', '2 BHK on the central block beside the open void (Shivalik unit plan, type 04: C-203 and its mirror positions)'],
                                                                                            ['Size', '880.25 sq.ft. RERA carpet + balcony + wash; 1,600 sq.ft. indicative super built-up']]),
                      ph=dict(name='Duplex penthouse', short='PH', rows=[['Home', 'One of 12 duplex penthouses over floors 33 and 34, with private terraces (Shivalik: terraces up to 650 sq.ft.)'], ['Size', 'About 2,164 sq.ft. carpet (Housiey)']]))
        T = []
        for wing, letters in (('Back wing (cores C and D)', 'CD'), ('Front wing (cores A and B)', 'BA')):
            parts = []
            cells, nos, ft = [], [], []
            for L in letters:
                inner, outer = halves(*ARMS[L]); parts += [Polygon(inner), Polygon(outer), Polygon(MID[L])]
            outline = Polygon()
            from shapely.ops import unary_union
            outline = unary_union([q.buffer(0.6) for q in parts]).buffer(-0.6)
            if outline.geom_type != 'Polygon': outline = max(outline.geoms, key=lambda g: g.area)
            t = SH.tower(fr, 'T' + letters, wing, [ll(q) for q in list(outline.exterior.coords)[:-1]], None, 'all', crown=dict(type='cap', h=2))
            def cl(poly): return to_tower_local(fr, t, [ll(q) for q in poly])
            order = []
            for L in letters:
                inner, outer = halves(*ARMS[L]); order += [(f'{L}-x01', outer, 't3'), (f'{L}-x02', inner, 't1'), (f'{L}-x03', MID[L], 't4')]
            st = [dict(label='Ground floor', kind='M', h=5.0, use='Entrance lounges, reception and waiting lounge; parking (Shivalik ground-level plan)'),
                  dict(label='Floor 1 (podium)', kind='M', h=5.0, use='Recreational podium: gym, spa and salon, sports court (INI Design Studio)')]
            for f_ in list(range(2, 22)) + ['22'] + list(range(23, 33)):
                if f_ == '22': st.append(dict(label='Floor 22 (skip floor)', kind='S', use='Skip (refuge) floor: no homes (Shivalik typical-floor plan)')); continue
                st.append(dict(label=f'Floor {f_}', kind='A', nos=[n.replace('x', str(f_)) for n, _, _ in order], plan=dict(cells=[cl(c) for _, c, _ in order], ft=[k for _, _, k in order])))
            st.append(dict(label='Floors 33–34 (penthouses)', kind='P', levels=2, unit='all', plan=dict(cells=[cl(c) for _, c, _ in order], ft=['ph'] * 6)))
            t['stack'] = st; T.append(t)
        for side, poly in CORE.items():
            tc = SH.tower(fr, 'K' + side, f'Lift core ({"B and C" if side == "west" else "A and D"})', [ll(q) for q in poly], None, 'all', nolabel=True, crown=dict(type='cap', h=4))
            tc['stack'] = [dict(label=L['label'], kind='M' if L['kind'] != 'S' else 'S', h=L.get('h'), levels=L.get('levels', 1), use='Lift lobby, lifts and stairs') for L in T[0]['stack']]
            for L in tc['stack']:
                if L['h'] is None: L.pop('h')
            T.append(tc)
        units = {'all': SH.u('Shivalik Skyview', '2 & 3 BHK + PH', [['Homes', '372: 12 per floor on floors 2–21 and 23–32 and 12 duplex penthouses on top (Gujarat RERA count; Shivalik plans)'],
                 ['RERA', 'PR/GJ/GANDHINAGAR/GANDHINAGAR/Others/RAA11515/240323']])}
        note = ('Shivalik Skyview: the “drone” tower by INI Design Studio, 120 m and 34 storeys: a central block around an open void with four arms reaching to the corners, '
                'traced from Shivalik’s typical-floor plan and placed on the tower now rising on site (current satellite imagery, where the arms and the void are visible; the plot drawn on the RERA map service sits about 40 m to its west). '
                'Every floor from 2 to 21 and 23 to 32 has 12 homes, three on each of the lift cores A, B, C and D (numbered x01 at the end of the arm, x02 on the arm and x03 on the central block, '
                'as on the developer’s key plans); floor 22 is the skip floor and floors 33–34 hold the 12 duplex penthouses. Tap a home to see its type and size.' + SURR)
        return cfg_base(p, base, fr, T, units, T[0]['stack'], 3.3, note, local(fr, allp), ftypes=ftypes, flatWord='', startFloor='Floor 12', geo_name='GEO_GIFT', height=120,
                        enqLabel='Enquire about this home', cellsNote='Penthouse numbers are not published; positions follow the typical floor.')

def presente(p, base):
    import gmfit as G
    from shapely.geometry import Polygon
    from shapely import affinity
    R = RERA['presente']; P = R['poly']; o = tuple(P[0])
    prm, res = G.fit([[415, 290, *P[3]], [1010, 330, *P[0]], [1010, 1095, *P[1]], [655, 1090, *P[2]]], o)
    ll = lambda q: G.to_ll(prm, o, *q)
    xw = lambda y: 448 + (y - 335) * (212 / 660)
    def wing(y0, y1, inset=0):
        g = Polygon([(xw(y0) + inset, y0), (910, y0), (910, y1), (xw(y1) + inset, y1)])
        return list(affinity.scale(g, 0.86, 1.0, origin='centroid').exterior.coords)[:-1]
    W = {'A': wing(345, 560), 'B': wing(560, 775, 30), 'C': wing(775, 990)}
    with gift_origin():
        fr = frame_ll(P)
        from shapely.ops import unary_union
        out = unary_union([Polygon(v).buffer(1) for v in W.values()]).buffer(-1)
        if out.geom_type != 'Polygon': out = max(out.geoms, key=lambda g: g.area)
        t = SH.tower(fr, 'T1', 'Présenté', [ll(q) for q in list(out.exterior.coords)[:-1]], None, 'all', crown=dict(type='cap', h=2.5))
        cl = {k: to_tower_local(fr, t, [ll(q) for q in v]) for k, v in W.items()}
        cells = [cl['A'], cl['B'], cl['C']]
        st = [dict(label='Ground floor', kind='M', h=5.0, use='Entrance lobby, residents’ lounges, home theatre and drop-off (Shivalik ground-floor plan); 3 basements below'),
              dict(label='Floor 1', kind='M', use='No homes registered on floor 1 (Gujarat RERA): amenity / service level')]
        for f_ in list(range(2, 16)) + [16] + list(range(17, 20)):
            if f_ == 16: st.append(dict(label='Floor 16', kind='S', use='No home is registered on floor 16: refuge floor')); continue
            st.append(dict(label=f'Floor {f_}', kind='A', nos=[f'A-{f_}01', f'B-{f_}01', f'C-{f_}01'], plan=dict(cells=cells, ft=['r4'] * 3)))
        st.append(dict(label='Floors 20–21 (penthouses)', kind='P', levels=2, unit='all', nos=['A-2001/L+2001/U', 'B-2001/L+2001/U', 'C-2001/L+2001/U'], plan=dict(cells=cells, ft=['ph'] * 3)))
        st.append(dict(label='Floor 22 (terrace)', kind='M', use='Landscaped roof terraces (Shivalik renders)'))
        t['stack'] = st
        ftypes = dict(r4=dict(name='4 BHK residence', short='4 BHK', rows=[['Home', 'One of the three 4 BHK residences on the floor, each with its own wing and wraparound balconies; riverfront and GIFT City views'],
                                                                      ['Size', '6,049, 6,398 or 6,811 sq.ft. carpet, depending on the residence (Housiey); which letter has which size is not published'], ['Price', 'From ₹17 Cr all inclusive (Housiey)']]),
                      ph=dict(name='6 BHK duplex penthouse', short='6 BHK PH', exact=True, rows=[['Home', 'Duplex penthouse over floors 20 and 21 (RERA: 2001/L + 2001/U), one in each wing'], ['Size', '6,000 – 6,500 sq.ft. carpet (Housiey)'], ['Price', 'From ₹48 Cr (Housiey)']]))
        units = {'all': SH.u('Shivalik Présenté', '4 BHK + 6 BHK PH', [['Homes', '54: three per floor (A, B and C) on floors 2–15 and 17–19, and three duplex penthouses over floors 20–21 (Gujarat RERA unit list)'],
                 ['RERA', 'PR/GJ/GANDHINAGAR/GANDHINAGAR/GIFT Urban Development Authority/RAA16602/160326/311230']])}
        note = ('Shivalik Présenté: one tower (3 basements + ground + 22, Housiey) on the riverfront in GIFT City, not three: the Gujarat RERA “blocks” A, B and C are the three residences on each floor. '
                'The tower is drawn as three staggered wings, one residence each, as on the Shivalik renders, over the ground-floor plan fitted to the plot registered on the RERA map service (within about 6 m). '
                'Floors and unit numbers are from the RERA list: homes on floors 2–15 and 17–19 (16 is the refuge floor) and three 6 BHK duplex penthouses over floors 20–21. '
                'Typical floor plates are not yet published, so each wing is sized from the registered carpet areas; which wing carries A, B or C is shown north to south.' + SURR)
        return cfg_base(p, base, fr, [t], units, st, 3.6, note, local(fr, P), ftypes=ftypes, flatWord='', startFloor='Floor 10', geo_name='GEO_GIFT', height=86,
                        enqLabel='Enquire about this residence', cellsNote='Wing positions of A, B and C are indicative.')

PIDS = ('west-park', 'inspire-corporate-capital', 'adani-center-point', 'amora', 'storeys-golf-coast', 'the-storeys', 'storeys-infinity', 'navratna-gulmohar', 'shivalik-skyview', 'shivalik-presente')
BUILD = {'west-park': west_park, 'inspire-corporate-capital': icc, 'adani-center-point': center_point, 'amora': amora, 'storeys-golf-coast': golf_coast, 'the-storeys': storeys, 'storeys-infinity': infinity, 'navratna-gulmohar': gulmohar, 'shivalik-skyview': skyview, 'shivalik-presente': presente}

def build(pid, p, base):
    return BUILD[pid](p, base or {'geo': {}})

# ------------------------------------------------------------------ helpers for plan-traced cells
def split_cells(P, n, rows=None):
    """split a (possibly concave) outline into n pieces of equal area: rows bands across the short side, equal strips along the long side"""
    from shapely.geometry import Polygon, box
    from shapely.ops import unary_union
    g = Polygon(P).buffer(0); x0, y0, x1, y1 = g.bounds
    long_x = (x1 - x0) >= (y1 - y0)
    rows = rows or (1 if n <= 3 else 2)
    def cut(geom, k, along_x):
        bx0, by0, bx1, by1 = geom.bounds; A = geom.area; out = []; lo = bx0 if along_x else by0; hi = bx1 if along_x else by1; prev = lo
        for i in range(1, k + 1):
            if i == k: c = hi + 1
            else:
                a, b = lo, hi
                for _ in range(40):
                    m = (a + b) / 2
                    part = geom.intersection(box(lo - 1, by0 - 1, m, by1 + 1) if along_x else box(bx0 - 1, lo - 1, bx1 + 1, m))
                    if part.area < A * i / k: a = m
                    else: b = m
                c = (a + b) / 2
            piece = geom.intersection(box(prev, by0 - 1, c, by1 + 1) if along_x else box(bx0 - 1, prev, bx1 + 1, c)); out.append(piece); prev = c
        return out
    bands = cut(g, rows, not long_x)
    per = [n // rows + (1 if i < n % rows else 0) for i in range(rows)]
    cells = []
    for i, bnd in enumerate(bands):
        parts = cut(bnd, per[i], long_x)
        if i % 2: parts = parts[::-1]          # number round the floor
        cells += parts
    out = []
    for c in cells:
        if c.geom_type != 'Polygon': c = max(getattr(c, 'geoms', [c]), key=lambda q: q.area)
        out.append([[round(x, 2), round(y, 2)] for x, y in list(c.exterior.coords)[:-1]])
    return out

def to_tower_local(fr, t, ll):
    return [[round(a - t['x'], 2), round(b - t['y'], 2)] for a, b in (SH.loc(fr, *q) for q in ll)]
