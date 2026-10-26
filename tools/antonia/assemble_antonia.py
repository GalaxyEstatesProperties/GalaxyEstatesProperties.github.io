"""Write the Antonia 3D explorer config (t3d.json) from antonia_geom.json and the brochure tables."""
import json, math, re, sys
from shapely.geometry import Polygon, MultiPolygon, LineString, box
from shapely.ops import unary_union, split

G = json.load(open('antonia_geom.json'))
K = 13.25 / 0.3048; X0, Y0 = 1860.5, 2811.5
def P2(X, Y): return [round((X - X0) / K, 2), round(-(Y - Y0) / K, 2)]
def disp(x, y): return P2(x * 2.48, y * 2.48)          # brochure page coordinates at 150 dpi display (1414 px wide) -> plot metres

def R2(P, tol=0.05):
    p = Polygon(P)
    if not p.is_valid: p = p.buffer(0)
    if isinstance(p, MultiPolygon): p = max(p.geoms, key=lambda g: g.area)
    q = p.simplify(tol, preserve_topology=True)
    return [[round(x, 2), round(y, 2)] for x, y in list(q.exterior.coords)[:-1]]

def hole_free(geom):
    out, todo = [], list(geom.geoms) if hasattr(geom, 'geoms') else [geom]
    while todo:
        g = todo.pop()
        if g.is_empty or g.area < 0.3: continue
        if not g.interiors: out.append(g); continue
        hx = g.interiors[0].centroid.x
        todo += list(split(g, LineString([(hx, g.bounds[1] - 1), (hx, g.bounds[3] + 1)])).geoms)
    return out

# ------------------------------------------------------------------ heights (section, brochure page 13)
H = {0: 4.5}
for f in (1, 2): H[f] = 4.275
for f in range(3, 21): H[f] = 3.2
for f in range(21, 32): H[f] = 3.35
for f in range(32, 43): H[f] = 3.65
Z = {}; z = 0.0
for f in range(43): Z[f] = round(z, 3); z += H[f]
ROOF = round(z, 3)                                     # 147.65 m: terrace level
assert abs(ROOF - 147.65) < 0.01, ROOF

# ------------------------------------------------------------------ unit tables (brochure pages 8, 9, 11, 12)
SBA = {'1-2': {'01': 2576, '02': 1281, '03': 1210, '04': 2482},
       '3-20': {'01': 1692, '02': 1542, '03': 1471, '04': 1400, '05': 2479},
       '22-31': {'01': 1692, '02': 1542, '03': 1471, '04': 1400, '05': 2479},
       '32-42': {'01': 3234, '02': 2871, '03': 2479}}
SIZE = {'1-2': {'01': "28'10\" × 47'5\"", '02': "14'0\" × 43'8\"", '03': "14'0\" × 41'2\"", '04': "28'3\" × 40'4\""},
        '3-20': {'01': "14'6\" × 55'2\"", '02': "14'0\" × 52'8\"", '03': "14'0\" × 50'3\"", '04': "14'0\" × 47'9\"", '05': "28'3\" × 40'4\""},
        '32-42': {'01': "28'10\" × 54'0\"", '02': "28'3\" × 49'0\"", '03': "28'3\" × 40'4\""}}
SIZE['22-31'] = SIZE['3-20']
BAND = {'1-2': (1, 2), '3-20': (3, 20), '22-31': (22, 31), '32-42': (32, 42)}
def sqft(n): return f'{n:,} sq ft ({n * 0.092903:,.1f} sq m)'

ftypes = {}
plans = {}
for band, (a, b) in BAND.items():
    shop = band == '1-2'
    sfx = sorted(G[band]['units'])
    cells = [R2(G[band]['units'][q]) for q in sfx]
    fts = []
    for q in sfx:
        key = f'{band}:{q}'
        h = H[a]
        ftypes[key] = dict(name='Showroom' if shop else 'Office', exact=True, rows=[
            ['Super built-up area', sqft(SBA[band][q])],
            ['Size (brochure plan)', SIZE[band][q]],
            ['Floor to floor', f'{h:.3f} m'.rstrip('0').rstrip('.') + ' (section drawing)'],
            ['Same unit on', f'floors {a} and {b}' if b - a == 1 else f'floors {a} to {b}'],
            ['Position', 'As drawn on the developer’s floor plan for these floors']])
        fts.append(key)
    plans[band] = dict(cells=cells, ft=fts)

stack = [dict(label='Ground floor', kind='M', h=H[0], sub='Entrance level',
              use='Entrance foyer (46\'2" × 45\'10") with a coffee bar and lounge; meter room, BMS room and fire command room; drop-off on the driveway')]
NOTE_OF = {'1-2': 'Showroom floor: 4 showrooms off a 12\'6" foyer, with a 6\'0" passage along the S.G. Highway front',
           '3-20': '5 offices off a 12\'6" foyer', '22-31': '5 offices off a 12\'6" foyer', '32-42': '3 large offices off a 12\'6" foyer'}
for f in range(1, 43):
    if f == 21:
        stack.append(dict(label='Floor 21', kind='S', h=H[f], sub='Skip floor', use='Skip (refuge) floor: no units on this level'))
        continue
    band = next(k for k, (a, b) in BAND.items() if a <= f <= b)
    sfx = sorted(G[band]['units'])
    e = dict(label=f'Floor {f}', kind='A', h=H[f], nos=[f'{f}{q}' for q in sfx], note=NOTE_OF[band])
    if band not in ('3-20', '22-31'): e['plan'] = plans[band]
    if band == '1-2': e['unit'] = 'shop'
    stack.append(e)

# footprints per band (the refuge and ground floors are drawn whole; the roof uses the top band)
tiers = []
for key, frm in (('G', 0), ('1-2', 1), ('3-20', 3), ('21', 21), ('22-31', 22), ('32-42', 32)):
    pts = R2(G[key]['outline'])
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    tiers.append({'from': frm, 'pts': pts, 'w': round(max(xs) - min(xs), 1), 'd': round(max(ys) - min(ys), 1)})

# ------------------------------------------------------------------ context
context = []
CORE, BLADE, CROWN, GREEN, RAMP = '#5b6578', '#2a2622', '#2b2f38', '#5a7d4c', '#8a9099'
def prism(poly, z, h, c):
    for piece in hole_free(poly):
        context.append(dict(t='prism', p=R2(list(piece.exterior.coords)[:-1]), z=round(z, 2), h=round(h, 2), c=c))
# service core and foyer inside each band (everything that is not a sold unit)
for key, (a, b) in BAND.items():
    F = Polygon(G[key]['outline']).buffer(0)
    U = unary_union([Polygon(u).buffer(0) for u in G[key]['units'].values()])
    core = F.difference(U).buffer(-0.05).buffer(0.05)
    prism(core, Z[a], Z[b] + H[b] - Z[a] - 0.35, CORE)
# roof parapet (1.2 m, section) over the top floor plate
top = Polygon(G['32-42']['outline']).buffer(0)
prism(top, ROOF, 1.2, CORE)
# the dark ribbed blade along the south face, rising into the crown frame (renders)
TOPZ = 163.5                                            # crown frame top, estimated from the renders (about 16 m above the terrace)
south_x = min(x for x, y in G['3-20']['outline'])
blade = box(south_x - 0.9, -9.0, south_x + 0.05, 13.75)
prism(blade, 0, TOPZ, BLADE)
# crown frame over the service core: two posts, a top beam and the stair cabin / water tank block between them (section: 9.8 m)
north_x = max(x for x, y in G['32-42']['outline'])
cy0, cy1 = 3.4, 13.75
prism(box(south_x + 0.05, cy0, south_x + 2.6, cy1 - 0.1), ROOF, TOPZ - ROOF - 0.05, CROWN)   # behind the blade: no shared faces
prism(box(north_x - 3.0, cy0, north_x + 0.1, cy1), ROOF, TOPZ - ROOF, CROWN)
prism(box(south_x + 0.05, cy0, north_x + 0.1, cy1 - 0.1), TOPZ - 3.5, 3.45, CROWN)
prism(box(south_x + 2.6, cy0 + 1.0, north_x - 3.0, cy1 - 1.0), ROOF, 3.65 * 2, CROWN)
# common open plot (landscaped garden with pergola seating) and the 6 m ramp to the basements, from the ground floor plan
cop = [disp(*q) for q in [(300, 585), (575, 610), (780, 632), (1040, 662), (1048, 700), (1010, 745), (960, 765), (860, 752), (650, 758), (560, 752), (460, 728), (300, 745)]]
context.append(dict(t='flat', p=cop, c=GREEN, z=0.55))
ramp = [disp(*q) for q in [(600, 492), (1195, 548), (1195, 685), (1085, 680), (1050, 645), (600, 606)]]
context.append(dict(t='flat', p=ramp, c=RAMP, z=0.5))

plot = [disp(*q) for q in [(302, 457), (1197, 546), (1197, 1632), (560, 1522), (500, 1510), (450, 1488), (400, 1452), (360, 1405), (330, 1345), (312, 1270), (304, 1180)]]

cfg = {
  'project': 'Antonia', 'interest': 'Offices & showrooms — Ahmedabad', 'floorH': 3.35, 'kind': 'commercial',
  'stack': [dict(label=e['label'], kind=e['kind']) for e in stack],
  'towers': [dict(label='Antonia', x=0, y=0, w=tiers[2]['w'], d=tiers[2]['d'], id='T1', type='office', pts=tiers[2]['pts'],
                  tiers=tiers, crown=dict(type='none'), height=TOPZ, stack=stack, plan=plans['3-20'])],
  'units': {
    'office': dict(name='Offices', short='Offices', rows=[['Offices (floors 3–42)', '1,400 – 3,234 sq ft super built-up'],
                                                           ['Showrooms (floors 1–2)', '1,210 – 2,576 sq ft super built-up']],
                   avail='Ask for live availability'),
    'shop': dict(name='Showrooms', short='Showrooms', rows=[['Showrooms (floors 1–2)', '1,210 – 2,576 sq ft super built-up'],
                                                             ['Floor to floor', '4.275 m']], avail='Ask for live availability')},
  'ftypes': ftypes, 'flatWord': 'Unit', 'perFloorLabel': 'Units on each floor',
  'plot': dict(w=round(max(p[0] for p in plot) - min(p[0] for p in plot), 1), d=round(max(p[1] for p in plot) - min(p[1] for p in plot), 1)),
  'plotPoly': plot,
  'geo': dict(name='GEO_ANTONIA', file='assets/geo/antonia.js', x=-4.5, y=21.9, rot=84.2, radius=650),
  'context': context, 'height': TOPZ, 'camStay': True, 'camR': 470, 'camY': 80, 'camTurn': 3.2, 'startFloor': 'Floor 21', 'enqLabel': 'Enquire about this floor',
  'facade': {'wall': '#cfd5db', 'frame': '#cfd6dd', 'glass': '#2c3f52', 'style': 'glass', 'balc': 0},
  'note': ('Model built from the developer’s brochure (June 2026). Floor plates and every showroom and office are traced to scale '
           'from its plans for the ground, 1st–2nd, 3rd–20th, 21st (skip), 22nd–31st and 32nd–42nd floors; super built-up areas '
           'and sizes are from its tables. Floor-to-floor heights are from its section drawing: 4.5 m ground, 4.275 m showroom floors, '
           '3.2 m on floors 3–20, 3.35 m on floors 21–31 and 3.65 m on floors 32–42, reaching the terrace at 147.65 m. '
           'The dark blade on the south face and the crown frame follow the renders; their exact sizes are estimated. '
           'Plot, garden and ramp: the brochure site plan, aligned with S.G. Highway and the 12 m road. Surroundings are from OpenStreetMap.'),
}
json.dump(cfg, open('t3d.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('floors', len(stack), 'units', sum(len(e.get('nos', [])) for e in stack), 'context', len(context), 'roof', ROOF, 'kB', len(json.dumps(cfg)) // 1024)
