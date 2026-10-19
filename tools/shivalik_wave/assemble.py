"""Assemble the Shivalik Wave 3D explorer config from wave_geom.json (brochure floor plans) and write it into the page."""
import json, math, re, sys
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
from build_model import hole_free
from labels import TABLES

G = json.load(open('wave_geom.json'))['floors']
def R2(P, tol=0.2):
    p = Polygon(P)
    if p.is_valid and len(P) > 8:
        q = p.simplify(tol, preserve_topology=True)
        if q.geom_type == 'Polygon' and not q.is_empty: P = list(q.exterior.coords)[:-1]
    return [[round(x, 1), round(y, 1)] for x, y in P]

GF_H, FH = 4.8, 3.9                       # ground floor and typical floor-to-floor heights (m), estimated
GROUPS = [('G', [0]), ('1', [1]), ('2', [2]), ('3', [3]), ('4', [4]), ('5', [5]), ('6-17', list(range(6, 18))), ('18', [18]),
          ('19-24', list(range(19, 25))), ('25-29', list(range(25, 30)))]
TABLE_OF = {'G': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6-17': 6, '19-24': 19, '25-29': 25}

def z_of(k): return 0.0 if k == 0 else GF_H + (k - 1) * FH
def h_of(k): return GF_H if k == 0 else FH

def poly(P):
    p = Polygon(P)
    return p if p.is_valid else p.buffer(0)

def fmt_ft(n): return f'{n:,} sq ft ({n * 0.092903:,.1f} sq m)'

ftypes, stack, tower_plan = {}, [], None
USE_POD = 'Podium (ground to 4th floor): showroom level; ask us whether a smaller unit is sold as an office'
USE_TWR = 'Tower (5th to 29th floor): offices'
for key, floors in GROUPS:
    g = G[key]
    tab = TABLES.get(TABLE_OF.get(key))
    if key == '18':
        stack.append(dict(label='Floor 18', kind='S', sub='Skip (refuge) floor',
                          use='Skip (refuge) floor: no office is sold on this level; open-to-sky terrace on the front'))
        continue
    sfx = sorted(g['units'], key=lambda q: int(q))
    cells = [R2(g['units'][q]) for q in sfx]
    fts = []
    for q in sfx:
        t = tab[q]; fk = f'{key}:{q}'
        rows = [['Carpet area (RERA)', fmt_ft(t['ca'])], ['Size (brochure)', t['size'].replace(' x ', ' \u00d7 ')]]
        if t.get('terrace'): rows.append(['Open terrace', fmt_ft(t['terrace'])])
        rows.append(['Use', USE_POD if floors[0] <= 4 else USE_TWR])
        rows.append(['Position', 'As drawn on the developer\u2019s floor plan for this floor'])
        ftypes[fk] = dict(name='Podium unit' if floors[0] <= 4 else 'Office', rows=rows, exact=True)
        fts.append(fk)
    plan = dict(cells=cells, ft=fts)
    if key == '6-17': tower_plan = plan
    for k in floors:
        nos = [(q if k == 0 else f'{k}{q}') for q in sfx]
        e = dict(label='Ground floor' if k == 0 else f'Floor {k}', kind='A', nos=nos,
                 note=f'{len(nos)} units on this floor, laid out as on the Shivalik Wave brochure floor plan; the unit numbers match the Gujarat RERA register')
        if key != '6-17': e['plan'] = plan
        stack.append(e)
for i, e in enumerate(stack):
    e['h'] = h_of(i)

# ------------------------------------------------------------------ footprints (used for the refuge floor and the roof)
tiers = []
for key, floors in GROUPS:
    P = G[key]['outline']
    xs = [p[0] for p in P]; ys = [p[1] for p in P]
    tiers.append({'from': floors[0], 'pts': R2(P), 'w': round(max(xs) - min(xs), 1), 'd': round(max(ys) - min(ys), 1)})
top = G['25-29']['outline']

# ------------------------------------------------------------------ context: cores, terraces, parapets
context = []
CORE = '#4a5670'
for key, floors in GROUPS:
    if key == '18': continue
    F = poly(G[key]['outline'])
    U = unary_union([poly(c) for c in G[key]['units'].values()])
    core = F.difference(U).buffer(-0.05).buffer(0.05)
    z0 = z_of(floors[0]); z1 = z_of(floors[-1]) + h_of(floors[-1]) - 0.35
    for piece in hole_free(core):
        if piece.area < 1.0: continue
        piece = piece.simplify(0.05)
        if piece.geom_type != 'Polygon' or piece.is_empty: continue
        context.append(dict(t='prism', p=R2(list(piece.exterior.coords)[:-1]), h=round(z1 - z0, 2), z=round(z0, 2), c=CORE))

GREEN = '#58794a'
def terrace(lower, upper, k):
    T = poly(G[lower]['outline']).difference(poly(G[upper]['outline']).buffer(0.3))
    for piece in hole_free(T):
        if piece.area < 4: continue
        context.append(dict(t='prism', p=R2(list(piece.simplify(0.05).exterior.coords)[:-1]), h=0.45, z=round(z_of(k) - 0.3, 2), c=GREEN))
terrace('2', '3', 3)          # podium step at the 3rd floor
terrace('4', '5', 5)          # podium roof: open-to-sky terraces around the tower on the 5th floor
terrace('6-17', '18', 18)     # skip floor terrace

# parapets above the roof: the facade rises above the 29th floor; taller at the north end (the 'diagonal silhouette' on the renders)
roof = z_of(29) + h_of(29) - 0.35
TOP = poly(top)
north = TOP.intersection(Polygon([(-2, -40), (80, -40), (80, 40), (-2, 40)]))
south = TOP.intersection(Polygon([(-80, -40), (-2, -40), (-2, 40), (-80, 40)]))
PAR = '#4a5f86'
for part, h in ((north, 5.0), (south, 3.0)):
    for piece in hole_free(part):
        context.append(dict(t='prism', p=R2(list(piece.simplify(0.05).exterior.coords)[:-1]), h=h, z=round(roof, 2), c=PAR))

# plot: traced from the brochure site plan (S.G. Highway service road on the west, the SP Ring Road junction to the north)
plot = [[-80.7, 38.5], [56.0, 38.5], [66.0, 34.5], [72.5, 26.0], [76.0, 12.0], [77.7, -31.7], [-57.0, -52.0]]
height = round(roof + 5.0, 1)

cfg_tower = dict(label='Shivalik Wave', x=0, y=0, w=tiers[0]['w'], d=tiers[0]['d'], id='T1', type='all', pts=R2(top),
                 tiers=tiers, crown=dict(type='none'), height=height, stack=stack, plan=tower_plan)

if __name__ == '__main__':
    page = sys.argv[1]
    s = open(page, encoding='utf-8').read()
    m = re.search(r'(<script type="application/json" id="t3d-shivalik-wave">)(.*?)(</script>)', s, re.S)
    cfg = json.loads(m.group(2))
    cfg['towers'] = [cfg_tower]
    cfg['floorH'] = FH
    cfg['stack'] = [dict(label=e['label'], kind=e['kind']) for e in stack]
    cfg['context'] = context
    cfg['plotPoly'] = plot
    xs = [p[0] for p in plot]; ys = [p[1] for p in plot]
    cfg['plot'] = dict(w=round(max(xs) - min(xs), 1), d=round(max(ys) - min(ys), 1))
    cfg['geo'] = dict(cfg['geo'], x=22.1, y=0.8, rot=75.5)
    cfg['height'] = height
    cfg['ftypes'] = ftypes
    cfg['flatWord'] = 'Unit'
    cfg['startFloor'] = 'Floor 10'
    cfg['perFloorLabel'] = 'Units on each floor'
    cfg['note'] = NOTE = (
        'Model built from the developer’s own drawings. Building form: the Shivalik Wave brochure floor plans for every floor '
        '(ground, 1st to 5th, 6th to 17th, the 18th skip floor, 19th to 24th and 25th to 29th), drawn to scale, and the official renders '
        '(two wave-shaped glass lobes facing S.G. Highway on a five-level podium, with the service core along the back). '
        'Units: each office and showroom is drawn where the brochure plan places it, with its RERA carpet area and size from the brochure; '
        'all 459 unit numbers match the Gujarat RERA register. Heights: G+29 and about 400 ft as published; floor-to-floor heights '
        '(4.8 m ground, 3.9 m above) and the parapets above the roof are estimated from the renders. Plot: traced from the brochure site plan. '
        'Surroundings (roads, buildings) are from OpenStreetMap.')
    cfg.pop('units_note', None)
    new = m.group(1) + json.dumps(cfg, ensure_ascii=False, separators=(',', ':')) + m.group(3)
    s = s[:m.start()] + new + s[m.end():]
    # the explanatory paragraph under the explorer
    s = re.sub(r'(<div class="t3d reveal" data-t3d="t3d-shivalik-wave">.*?</div>\s*</div>\s*</div>\s*<p class="detail-source">)(.*?)(</p>)',
               lambda mm: mm.group(1) + NOTE + mm.group(3), s, count=1, flags=re.S)
    open(page, 'w', encoding='utf-8').write(s)
    json.dump(cfg, open('t3d.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('cells', sum(len(e.get('nos', [])) for e in stack), 'context', len(context), 'height', height, 'json kB', len(new) // 1024)
