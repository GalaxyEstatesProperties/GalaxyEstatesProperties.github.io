"""Bakeri Stella 3D explorer config from the developer's brochure (52-page CAD brochure, floor plans GF to terrace) and Google/Esri imagery.

Model frame: the brochure page frame (x = page right, y = page up), metres, 7.22 pt per metre (stair treads, checked on the shop sizes).
Page right is south-south-east on site; the map rotation is -72.9 deg (fitted to the site hoarding and the tower blocks on Google imagery).
"""
import json, math, re, sys
import numpy as np
from shapely.geometry import Polygon, MultiPolygon, box, LineString, Point
from shapely.ops import unary_union, split
from shapely import affinity
sys.path.insert(0, '/home/claude/stella')
from geom import mask, polys, to_m
import neighbors as NB

PAGE = '/home/claude/gep/bakeri-stella-gift-city-gandhinagar.html'
K = 2.0855                                      # brochure display px (2000-wide view of the 150 dpi page) -> 300 dpi px
def disp(pts): return [tuple(p) for p in to_m(np.array(pts, float) * K)]

GX, GY, ROT = -29.1, -268.5, -72.9              # model origin in the GEO_GIFT frame, map rotation (deg)

def R2(P, tol=0.15):
    p = P if hasattr(P, 'geom_type') else Polygon(P)
    if not p.is_valid: p = p.buffer(0)
    if isinstance(p, MultiPolygon): p = max(p.geoms, key=lambda g: g.area)
    q = p.simplify(tol, preserve_topology=True)
    return [[round(x, 2), round(y, 2)] for x, y in list(q.exterior.coords)[:-1]]

# ------------------------------------------------------------------ heights (estimated: G 4.75, 1st 4.5, 2nd 4.2, 3rd-33rd 3.4 m -> 118.85 m terrace, as on the fire NOC)
H = {0: 4.75, 1: 4.5, 2: 4.2}
for f in range(3, 34): H[f] = 3.4
Z = {}; z = 0.0
for f in range(34): Z[f] = round(z, 3); z += H[f]
TOP = round(z, 2)
assert abs(TOP - 118.85) < 0.01, TOP
SOLTOP = Z[21]                                   # Sol (tower B) roof: 74.65 m

# ------------------------------------------------------------------ footprints
# Skye (A) and Sygnus (C): rectangles from the 22nd-floor and terrace plans (identical on floors 3-33)
SKYE = dict(x=-39.2, y=0.05, w=39.55, d=26.52, ang=6.98)
SYG = dict(x=34.6, y=-5.89, w=38.85, d=26.43, ang=-32.02)
def rect(t, grow=0.0):
    return affinity.translate(affinity.rotate(box(-t['w'] / 2 - grow, -t['d'] / 2 - grow, t['w'] / 2 + grow, t['d'] / 2 + grow), t['ang'], origin=(0, 0)), t['x'], t['y'])
RS, RC = rect(SKYE), rect(SYG)
# Sol (B): the river-facing row, the garden-facing row and the corridor between them (4th-20th floor plans); it runs into Skye and Sygnus
SOL = unary_union([box(-20.5, 3.2, 21.6, 15.1), box(-17.2, -7.0, 10.5, 2.1), box(-20.5, 1.6, 15.0, 3.7)])
SOLC = SOL.centroid
SOLT = dict(x=round(SOLC.x, 2), y=round(SOLC.y, 2), ang=0)

# podium (ground and 1st floor: shops on the river front, parking and lobbies behind), from the GF and 1st-floor plans
POD = Polygon(disp([(78, 455), (240, 440), (240, 400), (560, 395), (640, 395), (1310, 392), (1800, 688), (1745, 800), (1680, 878), (1615, 985), (140, 985)])).buffer(0)
# 2nd floor (amenity floor: mini-plex, gym, cafeteria, banquet hall, spa) from the 2nd-floor plan
F2 = [q for q in polys(mask(18)) if q.area > 150]
F2 = unary_union([q for q in F2 if q.bounds[1] > -26.7 and q.area > 200 and not (q.bounds[3] < -9)])

# slices between the towers
CUT1 = LineString([(-19.6, -60), (-19.6, 60)])
a, b = (11.15, -6.8), (25.2, 15.6)
dx, dy = b[0] - a[0], b[1] - a[1]
CUT2 = LineString([(a[0] - dx * 3, a[1] - dy * 3), (b[0] + dx * 3, b[1] + dy * 3)])
def slices(P):
    left, right = [], []
    for g in split(P, CUT1).geoms:
        (left if g.centroid.x < -19.6 else right).append(g)
    mid, east = [], []
    for g in split(unary_union(right), CUT2).geoms:
        c = g.centroid
        side = (dx * (c.y - a[1]) - dy * (c.x - a[0]))           # >0: west of the cut line (Sol side)
        (mid if side > 0 else east).append(g)
    return unary_union(left), unary_union(mid), unary_union(east)
PS, PM, PC = slices(POD)
FS, FM, FC = slices(F2)

def local(P, t):
    """model-frame polygon -> tower-local points (tower at x, y, turned by ang)"""
    q = affinity.rotate(affinity.translate(P, -t['x'], -t['y']), -t.get('ang', 0), origin=(0, 0))
    return R2(q)

# ------------------------------------------------------------------ stacks: keep the Gujarat RERA unit numbers and carpet areas already on the page
so = open('/home/claude/stella/old_page.html', encoding='utf-8').read()     # the page before this model (RERA unit lists)
OLD = json.loads(re.search(r'<script type="application/json" id="t3d-bakeri-stella">(.*?)</script>', so, re.S).group(1))
s = open(PAGE, encoding='utf-8').read()
m = re.search(r'(<script type="application/json" id="t3d-bakeri-stella">)(.*?)(</script>)', s, re.S)
OT = {t['id']: t for t in OLD['towers']}

USE = {0: 'Shops on the river-front road (Stella Shops), entrance lobbies of Skye, Sol and Sygnus, drop-off and ramps',
       1: 'Shops (Stella Shops, upper level) and podium parking',
       2: 'Amenity floor: mini-plex theatre, gym, yoga studio, indoor games, cafeteria, banquet hall, spa, day-care; pool and river-view deck on the podium roof'}
FAC_SHOP = {'style': 'glass', 'glass': '#2e4256', 'frame': '#d8d2c6', 'wall': '#e9e5dc', 'balc': 0}
FAC_AMEN = {'style': 'glass', 'glass': '#3a5368', 'frame': '#e4e0d8', 'wall': '#efece6', 'balc': 0}
FAC_SKIP = {'wall': '#e7e3da', 'frame': '#6d7f45', 'glass': '#4d5a3c', 'balc': 0}

def stack_for(tid, top):
    old = OT[tid]['stack']
    out = []
    for f in range(top + 1):
        e = dict(old[f]) if f < len(old) else {'label': f'Floor {f}', 'kind': 'A'}
        e['h'] = H[f]
        if f in (0, 1):
            nos = e.get('nos')
            e.update(kind='M', use=USE[f], fac=FAC_SHOP)
            if f == 0: e['sub'] = 'Shops and entrance lobby'
            if f == 0 and tid == 'T1':
                e['note'] = 'Gujarat RERA registers 24 shops on the ground level across the project; the brochure shows 12 shops on the ground floor and 12 on the 1st floor'
            for k in ('nos', 'frows'): e.pop(k, None)
        elif f == 2:
            e['fac'] = FAC_AMEN
            e['sub'] = 'Amenity floor'
            e.setdefault('use', USE[2])
            if e.get('kind') == 'A': e['note'] = (e.get('note', '') + '. This is the amenity floor: ' + USE[2][len('Amenity floor: '):]).lstrip('. ')
        elif f == 21 and tid != 'T2':
            e.update(kind='S', fac=FAC_SKIP, sub='Skip (refuge) floor',
                     use='Skip floor with a planted band around the tower; the safe corridor across the roof of Sol links Skye and Sygnus on this level')
            for k in ('nos', 'frows', 'note'): e.pop(k, None)
        out.append(e)
    return out

towers = [
  dict(id='T1', label='Stella Skye · A', x=SKYE['x'], y=SKYE['y'], w=SKYE['w'], d=SKYE['d'], ang=SKYE['ang'], type='skye',
       tiers=[{'from': 0, 'pts': local(PS, SKYE)}, {'from': 2, 'pts': local(unary_union([FS, RS]), SKYE)}, {'from': 3, 'pts': None}],
       crown={'type': 'none'}, height=TOP, stack=stack_for('T1', 33)),
  dict(id='T2', label='Stella Sol · B', x=SOLT['x'], y=SOLT['y'], w=round(SOL.bounds[2] - SOL.bounds[0], 1), d=round(SOL.bounds[3] - SOL.bounds[1], 1), ang=0, type='sol',
       pts=local(SOL, SOLT),
       tiers=[{'from': 0, 'pts': local(PM, SOLT)}, {'from': 2, 'pts': local(unary_union([FM, SOL]), SOLT)}, {'from': 3, 'pts': local(SOL, SOLT)}],
       crown={'type': 'none'}, height=SOLTOP, stack=stack_for('T2', 20)),
  dict(id='T3', label='Stella Sygnus · C', x=SYG['x'], y=SYG['y'], w=SYG['w'], d=SYG['d'], ang=SYG['ang'], type='syg',
       tiers=[{'from': 0, 'pts': local(PC, SYG)}, {'from': 2, 'pts': local(unary_union([FC, RC]), SYG)}, {'from': 3, 'pts': None}],
       crown={'type': 'none'}, height=TOP, stack=stack_for('T3', 33)),
]

# ------------------------------------------------------------------ context: podium roof, planted bands, roofs
ctx = []
def prism(P, z, h, c, label=None, size=None):
    for g in (P.geoms if hasattr(P, 'geoms') else [P]):
        if g.is_empty or g.area < 0.2: continue
        e = dict(t='prism', p=R2(g, 0.05), z=round(z, 2), h=round(h, 2), c=c)
        if label: e['label'] = label; label = None
        if size: e['size'] = size
        ctx.append(e)
def flat(P, z, c):
    for g in (P.geoms if hasattr(P, 'geoms') else [P]):
        if g.is_empty or g.area < 0.2: continue
        ctx.append(dict(t='flat', p=R2(g, 0.05), z=round(z, 2), c=c))
def band(P, z, h, c, out=0.55, inner=0.05):
    ring = P.buffer(out, join_style=2).difference(P.buffer(-inner, join_style=2))
    # a ring has a hole; cut it into four pieces across the polygon so every piece is a simple prism
    cx, cy = P.centroid.x, P.centroid.y
    for ln in (LineString([(cx - 200, cy), (cx + 200, cy)]), LineString([(cx, cy - 200), (cx, cy + 200)])):
        ring = unary_union(list(split(ring, ln).geoms))
    prism(ring, z, h, c)

GREEN, HEDGE, WHITE, STONE, WATER, DECK, NAVY = '#5f7f3e', '#4f6f34', '#efece6', '#d9d3c7', '#3e8fc6', '#a07a55', '#1f3550'
ZP = Z[2]                                                     # podium roof = 2nd-floor level, 9.25 m
# podium roof (2nd floor, open part): lawns, river-view deck and the swimming pool, from the 2nd-floor plan
lawnL = Polygon(disp([(125, 820), (560, 778), (605, 830), (605, 980), (125, 985)]))
lawnR = Polygon(disp([(1140, 790), (1180, 752), (1560, 980), (1140, 985)]))
deck = Polygon(disp([(630, 760), (1115, 760), (1115, 985), (630, 985)]))
pool = Polygon(disp([(688, 870), (1070, 870), (1070, 962), (688, 962)]))
flat(lawnL, ZP + 0.08, GREEN); flat(lawnR, ZP + 0.08, GREEN); flat(deck, ZP + 0.1, DECK); flat(pool, ZP + 0.14, WATER)
# glass railing / parapet along the podium edge (1.1 m), as on the renders
for i, (p, q) in enumerate(zip(list(POD.exterior.coords)[:-1], list(POD.exterior.coords)[1:])):
    seg = LineString([p, q])
    if seg.length < 2: continue
    edge = seg.buffer(0.18, cap_style=2)
    if edge.intersection(unary_union([RS, RC, SOL, F2]).buffer(0.2)).area > edge.area * 0.5: continue
    prism(edge, ZP, 1.1, '#cfe1ea')
# planted bands: on the skip floor of Skye and Sygnus, on the roof of Sol and round both tower tops (the green ledges on the renders)
for P in (RS, RC):
    band(P, Z[21] - 0.4, 1.3, HEDGE)
    band(P, TOP, 1.4, HEDGE)
band(SOL.intersection(box(-17.5, -8, 16, 16)), SOLTOP - 0.2, 1.2, HEDGE)
# Sol roof (21st-floor level): water-tank rooms and the enclosed safe corridor that links Skye and Sygnus, from the 21st-floor plan
F21 = [q for q in polys(mask(37)) if q.area < 120]
safe = max(F21, key=lambda g: g.area) if F21 else box(-20.5, -1.4, 18.6, 4.2)
prism(safe, SOLTOP, 3.4, WHITE)
tanks = box(-13.5, 6.0, 12.5, 14.0)
prism(tanks, SOLTOP, 3.0, STONE)
flat(SOL.buffer(-0.6).difference(unary_union([safe.buffer(0.2), tanks.buffer(0.2)])), SOLTOP + 0.15, GREEN)
# tower roofs (terrace level 118.85 m): white parapet, roof garden, stair and lift rooms over the cores (terrace plan)
for t, P in ((SKYE, RS), (SYG, RC)):
    flat(P.buffer(-0.4), TOP + 0.12, GREEN)
    # cores: two stair cabins at the river-side corners and the lift block in the middle (terrace-level plan)
    for (lx, ly, w, d, h) in ((-12.5, 9.0, 6.5, 7.5, 4.2), (12.0, 9.0, 6.5, 7.5, 4.2), (0.0, 1.5, 12.0, 5.5, 5.2)):
        cbox = affinity.translate(affinity.rotate(box(lx - w / 2, ly - d / 2, lx + w / 2, ly + d / 2), t['ang'], origin=(0, 0)), t['x'], t['y'])
        prism(cbox, TOP, h, WHITE)
    # trees along the roof edge (the planted crowns on the renders)
    for k in range(9):
        u = -t['w'] / 2 + 2.2 + k * (t['w'] - 4.4) / 8
        for v in (-t['d'] / 2 + 1.8, t['d'] / 2 - 1.8):
            if abs(v - 9.0) < 4 and (abs(u - 12) < 4.5 or abs(u + 12.5) < 4.5): continue
            c = affinity.translate(affinity.rotate(Point(u, v).buffer(1.25, 6), t['ang'], origin=(0, 0)), t['x'], t['y'])
            prism(c, TOP + 0.1, 3.2, '#3f6b2f')
# the Bakeri sign on Skye's roof, facing the river (renders)
sign = affinity.translate(affinity.rotate(box(-7, -13.0, 7, -12.4), SKYE['ang'], origin=(0, 0)), SKYE['x'], SKYE['y'])
prism(sign, TOP + 1.4, 3.6, NAVY)
# shop-front signage band on the river front ("BAKERI STELLA" on the renders)
front = LineString(disp([(330, 990), (1470, 990)])).buffer(0.25, cap_style=2)
prism(front, Z[1] - 1.3, 1.3, NAVY)

# ------------------------------------------------------------------ surroundings: the river, the metro, GIFT One & Two and the projects next door
def geo_to_model(P):
    q = affinity.translate(P, -GX, -GY)
    return affinity.rotate(q, -ROT, origin=(0, 0))
G = json.load(open('/home/claude/stella/geo_gift.json'))
w0 = G['water'][0]
river = Polygon([(w0[i], w0[i + 1]) for i in range(0, len(w0), 2)]).buffer(0).intersection(Point(GX, GY).buffer(1250))
rv = geo_to_model(river)
flat(rv, 0.16, '#2f78a8')
lab = geo_to_model(Point(-790, -300))
prism(lab.buffer(2, 4), 0.2, 0.3, '#2f78a8', label='Sabarmati River', size=18)
# GIFT City metro station (OpenStreetMap: railway station "GIFT City", 23.15336 N 72.68555 E); platform roof about 150 m x 24 m, as on the satellite image
sc, ax_ = (240.0, -738.0), (0.50, 0.866)
station = LineString([(sc[0] - 75 * ax_[0], sc[1] - 75 * ax_[1]), (sc[0] + 75 * ax_[0], sc[1] + 75 * ax_[1])]).buffer(12, cap_style=2)
prism(geo_to_model(station), 0, 13, '#b7bec8', label='GIFT City metro station', size=14)
# GIFT One and GIFT Two (OpenStreetMap buildings, 122 m): label only
for b_ in G['bld']:
    if b_.get('n') == 'GIFT One':
        q = Polygon([(b_['p'][i], b_['p'][i + 1]) for i in range(0, len(b_['p']), 2)])
        prism(geo_to_model(q.centroid.buffer(1.5, 4)), b_['h'], 0.3, '#8e94a3', label='GIFT One & GIFT Two', size=15)
# projects next door: simple blocks from their own explorers on this site
NEAR = [('shilp-north-sky', 'Shilp North Sky'), ('savvy-marina', 'Savvy Marina'), ('shivalik-skyview', 'Shivalik Skyview'), ('sangath-accolade', 'Sangath Accolade'),
        ('nila-prana', 'Prana by Nila'), ('shivalik-presente', 'Shivalik Présenté'), ('shilp-twin-towers', 'Shilp Twin Towers'), ('shilp-centrica', 'Shilp Centrica'),
        ('shivalik-curv', 'Shivalik Curv')]
for slug, name in NEAR:
    c, _ = NB.cfg(slug)
    fp = NB.footprints(c)
    tallest = max(fp, key=lambda x: x[1] * x[0].area)
    for P, Hh, l in fp:
        gp = NB.to_geo(P, c['geo'])
        mp = geo_to_model(gp)
        prism(mp, 0, Hh, '#7f8896', label=name if (P, Hh, l) == tallest else None, size=12)

# ------------------------------------------------------------------ plot (brochure site plan boundary) and the config
PLOT = Polygon(disp([(25, 215), (1545, 215), (1985, 635), (1480, 1165), (140, 1165)]))
plot = R2(PLOT)
R_ = {r[0]: r for r in OLD['units']['all']['rows']}
AV = OLD['units']['all'].get('avail', 'Ask for live availability')
units = {'skye': dict(name='Skye: 3 & 4 BHK homes and 4 BHK duplexes', short='3 & 4 BHK', rows=[R_['3 BHK'], R_['4 BHK'], R_['4 BHK duplex']], avail=AV),
         'sol': dict(name='Sol: 1, 1.5 & 2 BHK homes', short='1 – 2 BHK', rows=[R_['1 – 2.5 BHK']], avail=AV),
         'syg': dict(name='Sygnus: 2.5 & 3 BHK homes and 3 BHK duplexes', short='2.5 & 3 BHK', rows=[R_['1 – 2.5 BHK'], R_['3 BHK'], R_['3 BHK duplex']], avail=AV)}
cfg = dict(OLD)
cfg.update({
  'project': 'Bakeri Stella', 'floorH': 3.4, 'stack': [dict(label=e['label'], kind=e['kind']) for e in towers[0]['stack']],
  'towers': towers, 'units': units,
  'plot': dict(w=round(PLOT.bounds[2] - PLOT.bounds[0], 1), d=round(PLOT.bounds[3] - PLOT.bounds[1], 1)), 'plotPoly': plot,
  'geo': dict(name='GEO_GIFT', file='assets/geo-gift.js', x=GX, y=GY, rot=ROT, radius=1250),
  'context': ctx, 'height': TOP,
  'facade': {'wall': '#f1efea', 'frame': '#e3dfd7', 'glass': '#3c4c5c', 'rail': '#cfe3ee', 'style': 'punched', 'balc': 0.7},
  'startFloor': 'Floor 17', 'camStay': True, 'camR': 500, 'camY': 60,
  'note': ('Model built from the developer’s brochure for Stella (floor plans for every floor from the basements to the terrace, drawn to scale). '
           'Building form: three towers on a shared podium, bent to follow the plot: Skye (tower A, north) and Sygnus (tower C, south) rise to the 33rd floor, '
           'Sol (tower B, middle) to the 20th; the 21st floor is the skip floor, with an enclosed safe corridor across Sol’s roof linking Skye and Sygnus. '
           'The ground and 1st floors hold 24 shops on the river-front road with parking behind; the 2nd floor is the amenity floor, with the pool and river-view deck on the podium roof. '
           'Footprints are traced from the plans; the planted bands, roof gardens and the Bakeri sign follow the developer’s renders. '
           'Height: 118.85 m to the terrace (fire-safety opinion filed on Gujarat RERA); floor-to-floor heights are estimated (4.75 m ground, 4.5 m 1st, 4.2 m 2nd, 3.4 m above). '
           'Position and orientation: fitted to the site on current satellite imagery. Unit numbers and carpet areas are from the Gujarat RERA register; '
           'where each numbered home sits on its floor is indicative. Surroundings (Sabarmati river, roads, metro line and station, GIFT One and Two) are from OpenStreetMap; '
           'the projects next door are drawn as simple blocks from their own 3D explorers on this site.'),
})
cfg['camTurn'] = 3.35; cfg['camPh'] = 1.12
if __name__ == '__main__':
    out = json.dumps(cfg, ensure_ascii=False, separators=(',', ':'))
    s2 = s[:m.start()] + m.group(1) + out + m.group(3) + s[m.end():]
    s2 = re.sub(r'(<div class="t3d reveal" data-t3d="t3d-bakeri-stella">.*?</div>\s*</div>\s*</div>\s*<p class="detail-source">)(.*?)(</p>)',
                lambda mm: mm.group(1) + cfg['note'] + mm.group(3), s2, count=1, flags=re.S)
    open(PAGE, 'w', encoding='utf-8').write(s2)
    json.dump(cfg, open('/home/claude/stella/t3d.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('towers', [(t['id'], len(t['stack'])) for t in towers], 'context', len(ctx), 'kB', len(out) // 1024, 'F2 area', round(F2.area), 'POD', round(POD.area))
