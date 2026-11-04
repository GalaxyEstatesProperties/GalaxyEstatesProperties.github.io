"""Kalrav site maps: trees along the roads and in the gardens, the compound wall, and on the villa schemes a villa (and its pool) on every plot,
as in A. Shridhar's renders and drone photos. Writes "dress" into tools/kalrav/t3d/<id>.json and into the page's 3D config."""
import json, math, os, re, sys, random
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
from shapely import affinity
from shapely.prepared import prep

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..')
PAGES = {'ashridhar-kalrav-nest': 'ashridhar-kalrav-nest-north-ahmedabad.html', 'ashridhar-kalrav-seasons': 'ashridhar-kalrav-seasons-thol-ahmedabad.html',
         'ashridhar-kalrav-alpines': 'ashridhar-kalrav-alpines-nandoli-ahmedabad.html', 'ashridhar-kalrav-farms': 'ashridhar-kalrav-farms-jhaloda-ahmedabad.html',
         'ashridhar-kalrav-trails': 'ashridhar-kalrav-trails-chandrasan-ahmedabad.html', 'ashridhar-kalrav-treasure': 'ashridhar-kalrav-treasure-bhavanpur-ahmedabad.html'}
# villa schemes (villas built by the developer on every plot): body colour, roof colour and form, from the renders
VILLAS = {'ashridhar-kalrav-nest': dict(hc=0xc8a882, rc=0x4a3b33, roof='hip', h=6.8, share=0.11, lo=150, hi=330),
          'ashridhar-kalrav-seasons': dict(hc=0xbdb5a8, rc=0x55524d, roof='flat', h=6.4, share=0.13, lo=75, hi=210)}

def fix(P):
    P = P.buffer(0)
    return max(P.geoms, key=lambda g: g.area) if P.geom_type == 'MultiPolygon' else P

def dress(pid, c):
    rnd = random.Random(pid)
    cells, labs = [], []
    for t in c['towers']:
        for L in t['stack']:
            for j, q in enumerate((L.get('plan') or {}).get('cells', [])):
                P = fix(affinity.translate(Polygon(q), t['x'], t['y']))
                lab = (L.get('lab') or [None] * (j + 1))[j]
                labs.append((lab[0] + t['x'], lab[1] + t['y']) if lab else (P.centroid.x, P.centroid.y))
                cells.append(P)
    plots = unary_union(cells)
    site = fix(Polygon(c['plotPoly']))
    green = unary_union([fix(Polygon(e['p'])) for e in c['context'] if e['t'] == 'flat' and e.get('c') == '#567f45'])
    water = unary_union([fix(Polygon(e['p'])) for e in c['context'] if e['t'] == 'flat' and e.get('c') == '#2f6fb0'])
    road = site.difference(plots.buffer(0.2)).difference(green).difference(water)
    R_, P_ = prep(road), prep(plots.buffer(1.0))
    taken, trees = {}, []
    def put(x, y, s, gap):
        k = (int(x // gap), int(y // gap))
        if k in taken: return
        taken[k] = 1; trees.extend([round(x, 1), round(y, 1), round(s, 2)])
    # avenue trees on the road verges, about 11 m apart, just off the plot edges
    for P in cells:
        ring = P.exterior
        n = max(1, int(ring.length // 11))
        for k in range(n):
            a = ring.interpolate((k + 0.5) * ring.length / n)
            b = ring.interpolate((k + 0.5) * ring.length / n + 0.5)
            dx, dy = b.x - a.x, b.y - a.y; L = math.hypot(dx, dy) or 1
            for sgn in (1, -1):
                x, y = a.x + sgn * dy / L * 2.2, a.y - sgn * dx / L * 2.2
                if R_.contains(Point(x, y)) and not P_.contains(Point(x, y)):
                    put(x, y, 1.6 + rnd.random() * 0.5, 9); break
    # gardens and forest: trees scattered about 14 m apart
    for G in (green.geoms if hasattr(green, 'geoms') else [green]):
        x0, y0, x1, y1 = G.bounds
        x = x0
        while x < x1:
            y = y0
            while y < y1:
                px, py = x + rnd.uniform(-4, 4), y + rnd.uniform(-4, 4)
                if G.buffer(-1.5).contains(Point(px, py)): put(px, py, 1.7 + rnd.random() * 0.9, 7)
                y += 14
            x += 14
    out = dict(trees=trees, wall=2.2, z=1.07)
    v = VILLAS.get(pid)
    if v:
        houses, pools = [], []
        for P, (lx, ly) in zip(cells, labs):
            R = P.minimum_rotated_rectangle; co = list(R.exterior.coords)[:4]
            e1 = (co[1][0] - co[0][0], co[1][1] - co[0][1]); e2 = (co[2][0] - co[1][0], co[2][1] - co[1][1])
            long_ = e1 if math.hypot(*e1) >= math.hypot(*e2) else e2
            ang = math.degrees(math.atan2(long_[1], long_[0]))
            area = max(v['lo'], min(v['hi'], P.area * v['share']))
            w = math.sqrt(area * 1.45); d = area / w
            ux, uy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            def fits(cx, cy, f):
                H = affinity.translate(affinity.rotate(box(-w * f / 2, -d * f / 2, w * f / 2, d * f / 2), ang, origin=(0, 0)), cx, cy)
                return P.buffer(-2.5).contains(H) and not H.buffer(2.2).contains(Point(lx, ly))
            # beside the plot number, so the number stays readable; centred and smaller if the plot is too tight
            spot = None
            for f in (1, .9, .8, .7, .6):
                for sgn in (1, -1):
                    cx, cy = lx + sgn * ux * (w * f / 2 + 3), ly + sgn * uy * (w * f / 2 + 3)
                    if fits(cx, cy, f): spot = (cx, cy, f, sgn); break
                if spot: break
            for f in (1, .9, .8, .7, .6):
                if spot: break
                H = affinity.translate(affinity.rotate(box(-w * f / 2, -d * f / 2, w * f / 2, d * f / 2), ang, origin=(0, 0)), P.centroid.x, P.centroid.y)
                if P.buffer(-2.5).contains(H): spot = (P.centroid.x, P.centroid.y, f, 1)
            if not spot: continue
            cx, cy, f, sgn = spot
            houses += [round(cx, 1), round(cy, 1), round(w * f, 1), round(d * f, 1), round(ang, 1), v['h']]
            off = w * f / 2 + 4.5
            pw, pd = 9, 4
            for ox, oy in ((sgn * ux * off, sgn * uy * off), (-uy * (d * f / 2 + 3.5), ux * (d * f / 2 + 3.5)), (uy * (d * f / 2 + 3.5), -ux * (d * f / 2 + 3.5))):
                px, py = cx + ox, cy + oy
                Q = affinity.translate(affinity.rotate(box(-pw / 2, -pd / 2, pw / 2, pd / 2), ang, origin=(0, 0)), px, py)
                if P.buffer(-1.5).contains(Q):
                    pools += [round(px, 1), round(py, 1), pw, pd, round(ang, 1)]; break
        out.update(houses=houses, pools=pools, hc=v['hc'], rc=v['rc'], roof=v['roof'])
    return out

def gate(pid, c):
    """Kalrav Nest's entrance: two dark stepped towers either side of the main entry (drone photo), on the boundary at the 'Main entry' label."""
    if pid != 'ashridhar-kalrav-nest': return []
    e = next(x for x in c['context'] if x.get('t') == 'label' and x.get('text') == 'Main entry')
    ring = Polygon(c['plotPoly']).exterior
    at = ring.interpolate(ring.project(Point(e['x'], e['y'])))
    b = ring.interpolate(ring.project(at) + 1)
    ux, uy = b.x - at.x, b.y - at.y; L = math.hypot(ux, uy); ux, uy = ux / L, uy / L
    out = []
    for sgn in (1, -1):
        x, y = at.x + sgn * ux * 11, at.y + sgn * uy * 11
        z = 0
        for side, h in ((7, 5), (6, 5), (5, 5), (3.6, 5)):
            sq = affinity.rotate(box(x - side / 2, y - side / 2, x + side / 2, y + side / 2), math.degrees(math.atan2(uy, ux)), origin=(x, y))
            out.append(dict(t='prism', p=[[round(px, 2), round(py, 2)] for px, py in list(sq.exterior.coords)[:-1]], z=z, h=h, c='#3b3632', gate=1))
            z += h
    return out

if __name__ == '__main__':
    for pid, page in PAGES.items():
        jf = os.path.join(HERE, 't3d', pid + '.json')
        c = json.load(open(jf, encoding='utf-8'))
        c['dress'] = dress(pid, c)
        c['context'] = [e for e in c['context'] if not e.get('gate')] + gate(pid, c)
        json.dump(c, open(jf, 'w', encoding='utf-8'), ensure_ascii=False)
        pf = os.path.join(ROOT, page); s = open(pf, encoding='utf-8').read()
        m = re.search(r'(<script type="application/json" id="t3d-%s">)(.*?)(</script>)' % re.escape(pid), s, re.S)
        pc = json.loads(m.group(2)); pc['dress'] = c['dress']; pc['context'] = c['context']
        s = s[:m.start()] + m.group(1) + json.dumps(pc, ensure_ascii=False, separators=(',', ':')) + m.group(3) + s[m.end():]
        open(pf, 'w', encoding='utf-8').write(s)
        D = c['dress']
        print(pid, 'trees', len(D['trees']) // 3, 'houses', len(D.get('houses', [])) // 6, 'pools', len(D.get('pools', [])) // 5)
