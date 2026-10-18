"""3D floor-explorer configs for every project whose tower count and floor count are published.
Positions: Google Maps place pins (checked 17 Oct 2026) or the township-map pins already on the site.
Surroundings: OpenStreetMap (assets/geo-*.js). Tower footprints and spacing are approximate unless noted."""
import json, math, os

E = 6378137.0
D = math.pi / 180
HERE = os.path.dirname(os.path.abspath(__file__))
PINS = json.load(open(os.path.join(HERE, 't3dall', 'pins.json')))
GEO_DIR = os.path.join(HERE, 't3dall', 'geo')

ORIGIN = {'GEO_SHANTIGRAM': (23.161, 72.5375), 'GEO_GIFT': (23.16, 72.6835)}
GEO_FILE = {'GEO_SHANTIGRAM': 'assets/geo-shantigram.js', 'GEO_GIFT': 'assets/geo-gift.js'}

def xy(origin, lat, lon):
    la0, lo0 = origin
    return ((lon - lo0) * D * E * math.cos(la0 * D), (lat - la0) * D * E)

# ------------------------------------------------------------------ Shantigram (same pins and blocks as the township map)
ROAD = -60
SH = {
  'aster-neo':     (23.1644097, 72.5421493, ROAD, ['Tower A', 'Tower B', 'Tower G', 'Tower H'], [[-22, -18, 26, 20], [22, -18, 26, 20], [-22, 18, 26, 20], [22, 18, 26, 20]], [110, 90]),
  'embrace':       (23.1618923, 72.5427326, ROAD, ['Tower A', 'Tower B', 'Tower C', 'Tower D', 'Tower E'], [[-16, -40, 17, 24], [-16, 0, 17, 24], [-16, 40, 17, 24], [16, -20, 17, 24], [16, 20, 17, 24]], [64, 112]),
  'elysium-novus': (23.1609967, 72.5426492, ROAD, ['Block C', 'Block D', 'Block E', 'Block F', 'Block G', 'Block J'], [[-15, -38, 16, 22], [-15, 0, 16, 22], [-15, 38, 16, 22], [15, -38, 16, 22], [15, 0, 16, 22], [15, 38, 16, 22]], [60, 104]),
  'greenfield':    (23.1620315, 72.5417188, ROAD, ['Tower 1', 'Tower 2', 'Tower 3'], [[-34, 0, 26, 20], [0, 0, 26, 20], [34, 0, 26, 20]], [110, 40]),
  'ambrosia':      (23.167227, 72.5383094, ROAD, ['Wing A', 'Wing B', 'Wing C'], [[-32, 0, 24, 22], [0, 0, 24, 22], [32, 0, 24, 22]], [104, 40]),
  'paarijat':      (23.165278, 72.5394248, ROAD, ['Tower 1', 'Tower 2'], [[-17, 0, 26, 22], [17, 0, 26, 22]], [76, 40]),
  'shilp-skyline': (23.168336, 72.5391398, ROAD, ['Block A', 'Block B', 'Block C'], [[-32, 0, 24, 22], [0, 0, 24, 22], [32, 0, 24, 22]], [104, 40]),
  'belrosa':       (23.1681202, 72.537639, ROAD, ['Belrosa'], [[0, 0, 40, 28]], [64, 48]),
}

def stack(above, ground='Ground floor', ground_use='Entrance lobby and common areas', start=1, label='Floor', unit=None, top=None):
    st = [dict(label=ground, kind='M', use=ground_use)] if ground else []
    for f in range(start, start + above):
        e = dict(label=f'{label} {f}', kind='A')
        if unit: e['unit'] = unit
        st.append(e)
    return st

# ------------------------------------------------------------------ what is published for each project
# levels: floors above the ground floor; 'total' means the published count includes the ground floor
S = {
  # Shantigram
  'aster-neo':     dict(above=22, per_floor='4 homes', src='Adani Realty: towers A, B, G and H, ground + 22 floors; Gujarat RERA: 352 homes (176 in A+B, 176 in G+H), so 4 homes per floor'),
  'embrace':       dict(per=[13, 13, 12, 13, 13], src='Adani Realty: 5 towers of 13 and 14 floors; Gujarat RERA: 56 homes each in towers A, B, D and E and 24 in tower C, so the model shows C as the shorter tower'),
  'elysium-novus': dict(above=13, height=44.8, src='Gujarat RERA: 44.8 m tall, 364 homes in blocks C to J'),
  'greenfield':    dict(above=21, src='Adani Realty / Housiey: 3 towers, ground + 21 floors'),
  'ambrosia':      dict(above=13, per_floor='4 homes', src='Adani Realty: wings A, B and C, ground + 13 floors; Gujarat RERA: 52 homes in each wing, so 4 homes per floor'),
  'paarijat':      dict(above=14, per_floor='4 homes', src='Adani Realty: 2 towers, ground + 14 floors; Gujarat RERA: 56 homes in each block, so 4 homes per floor'),
  'shilp-skyline': dict(above=24, height=79, src='Gujarat RERA: 79 m tall, 256 homes in blocks A, B and C'),
  'belrosa':       dict(above=31, height=125, src='Adani Realty: 32 floors and 125 m; 100 apartments + 8 duplexes (which floors hold the duplexes is not published)'),
  # GIFT City
  'sobha-elysia':  dict(n=2, above=35, podium=True, fp=(34, 26), src='Sobha: 2 towers, 35 floors above the podium; Gujarat RERA: 572 homes, numbered on floors 3 to 38 in both towers'),
  'nila-vida':     dict(n=2, above=31, labels=['Tower A', 'Tower B'], src='Gujarat RERA: 496 homes in blocks A and B', fp=(36, 24)),
  'shivalik-presente': dict(n=3, above=20, src='Shivalik: 3 towers of 21 floors; Gujarat RERA: 54 residences in blocks A, B and C', fp=(28, 24)),
  'shivalik-skyview':  dict(n=1, above=34, src='Shivalik: G+34 tower with 12 duplex penthouses (which floors is not published)', fp=(42, 28)),
  'shilp-north-sky':   dict(n=3, above=24, labels=['Block A', 'Block B', 'Block C'], src='Gujarat RERA: blocks A (224 units), B (223) and C (221): 646 homes and 22 shops; 25 storeys per the GharPe listing', fp=(34, 24)),
  'savvy-marina':  dict(n=3, above=32, labels=['T1', 'T2', 'T3'], src='Gujarat RERA: towers T1 (78 units), T2 (110) and T3 (82): 262 apartments and 8 shops; Savvy: 3 basements + ground + 32', fp=(34, 26)),
  'bakeri-stella': dict(n=3, above=33, src='Bakeri: 3 interconnected towers, 3 basements + ground + 33', fp=(32, 24), gap=6),
  'shilp-twin-towers': dict(n=2, above=27, height=120, kind='commercial', labels=['West tower', 'East Block'], src='Shilp / INI Design Studio: twin towers of 28 floors, 120 m. Gujarat RERA: only the East Block is registered so far (275 offices, 4 shops)', fp=(40, 32)),
  # Ahmedabad
  'maruti-360':    dict(n=2, above=40, height=152.7, src='Maruti 360: 2 towers, 41 storeys, 501 ft (152.7 m), 124 homes', fp=(36, 28)),
  'gala-ikebana':  dict(n=3, above=20, src='Gala Group: 21 floors, 119 homes; Gujarat RERA: 119 homes in blocks A, B and C', fp=(30, 24)),
  'navratna-gulmohar': dict(n=1, above=38, height=161.5, kind='mixed', src='Gujarat RERA: 161.5 m, 40 homes, 125 offices and 5 shops; INI Design Studio: 39 floors', fp=(44, 34)),
  'trogon-centre-court': dict(centre_court=True, src='Trogon Centre Court brochure (site plan, floor plans, 4 homes per floor, terrace floors) and the Gujarat RERA register (286 flats and 56 shops; blocks A+B 182 units, C 80, D 80)'),
  'shivalik-wave': dict(n=1, above=29, height=122, kind='commercial', src='Shivalik: G+29, about 400 ft (122 m)', fp=(48, 32)),
  'antonia':       dict(n=1, kind='commercial', antonia=True, src="Antonia Infra: 42 floors; showrooms on floors 1–2, offices on floors 3–42", fp=(46, 34)),
  'anamika-high-point': dict(n=5, above=31, labels=['Tower A', 'Tower B', 'Tower C', 'Tower D', 'Tower E'], src='Constera: towers A–E, 3 basements + ground + 31 floors, 580 homes', fp=(30, 24)),
  'ashridhar-wynn': dict(n=1, above=33, kind='commercial', src='A. Shridhar: 34-floor glass commercial tower', fp=(44, 30)),
  'godrej-altus':  dict(n=4, above=18, labels=['T1', 'T2', 'T3', 'T4'], src='Gujarat RERA: 131 homes and 17 shops in towers T1 to T4 (a Housiey listing says G+17/18, but the registered unit numbers stop at floor 11)', fp=(40, 24)),
  'venus-the-universe': dict(n=10, above=22, per_floor='4 homes', src='Venus: 10 towers on 7 acres, 4 homes per floor (listed as G+22 by Housiey; the Gujarat RERA unit numbers stop at floor 21 in towers A and B and floor 20 in towers C to J)', fp=(32, 24)),
  'venus-pashmina': dict(n=5, above=21, src='GharPe listing: 5 blocks of 22 floors, 126 homes', fp=(28, 22)),
  'venus-stratum': dict(n=1, kind='commercial', stratum=True, src='Masters PMC: one building, 3 retail floors + 14 office floors, 5 basements', fp=(60, 40)),
  'shilp-business-gateway': dict(n=1, above=11, kind='commercial', src='Shilp: ground + 11 floors', fp=(44, 30)),
  # Abroad
  'newport-residences': dict(n=1, newport=True, src='CDL: Newport Residences are levels 23–45 of the 45-storey Newport Plaza', fp=(40, 28)),
  'dcondo-vite':   dict(n=2, levels_total=8, intl=True, src='Sansiri: 2 buildings of 8 floors', fp=(48, 18)),
  'binghatti-burj-jacob': dict(n=1, levels_total=104, height=557, intl=True, floorH=4.0, src='Wikipedia (from Binghatti): 104 floors, 557 m with the crown', fp=(46, 40)),
  'danube-bayz-101': dict(n=1, levels_total=101, intl=True, src='Danube: 101 storeys (height not published)', fp=(46, 40)),
  'danube-diamondz': dict(n=1, levels_total=65, intl=True, src='Homes4Life listing: 65-storey tower', fp=(44, 34)),
  'binghatti-mercedes-city': dict(n=1, vision=True, intl=True, height=341, src='Binghatti Vision Iconic brochure: ground + mezzanine + 5 podium levels + 67 residential floors + 4 mechanical levels + roof; Dubai Land Department project #4544: 1,426 homes and 27 shops; height about 341 m as marketed; Mercedes-Benz Places | Binghatti City: 12 towers, Vision Iconic plus 11 staggered towers that fall in height away from it (Dezeen, 15 Jan 2026)', fp=(64, 30)),
  'trx-residences': dict(n=2, levels_total=57, intl=True, src='GDP Architects: twin towers of 53 and 57 storeys; OpenStreetMap: tower A 53 levels and 443 homes, tower B 57 levels and 453 homes, with both tower outlines', fp=(40, 30)),
  'emaar-valo':    dict(n=1, levels_total=37, intl=True, src='Propsearch: a 37-storey residential building with about 291 homes; Dubai Land Department project #3033: 291 homes (122 one-bedroom, 129 two-bedroom, 40 three-bedroom), 66% built', fp=(42, 30)),
  'danube-shahrukhz': dict(n=1, levels_total=55, intl=True, kind='commercial', src='Danube: 55-storey office tower', fp=(46, 36)),
}

def road_angle(G, x0, y0, maxd=220):
    """Bearing (deg, CCW from east) of the nearest OSM road segment to (x0, y0)."""
    best = None
    for cls, wgt in (('major', 0.7), ('mid', 0.85), ('minor', 1.0)):
        for a in (G.get('roads', {}).get(cls) or []):
            for i in range(0, len(a) - 3, 2):
                x1, y1, x2, y2 = a[i] - x0, a[i + 1] - y0, a[i + 2] - x0, a[i + 3] - y0
                dx, dy = x2 - x1, y2 - y1; L2 = dx * dx + dy * dy
                if L2 < 4: continue
                t = max(0, min(1, -(x1 * dx + y1 * dy) / L2))
                d = math.hypot(x1 + t * dx, y1 + t * dy) * wgt
                if d < maxd and (best is None or d < best[0]): best = (d, math.degrees(math.atan2(dy, dx)))
    if not best: return 0.0
    a = best[1]
    while a > 90: a -= 180
    while a < -90: a += 180
    return round(a, 1)

def face_road(G, x0, y0, maxd=250):
    """Rotation (deg) that turns the site's local south edge toward the nearest major / mid road."""
    best = None
    for cls in ('major', 'mid'):
        for a in (G.get('roads', {}).get(cls) or []):
            for i in range(0, len(a) - 3, 2):
                x1, y1, x2, y2 = a[i] - x0, a[i + 1] - y0, a[i + 2] - x0, a[i + 3] - y0
                dx, dy = x2 - x1, y2 - y1; L2 = dx * dx + dy * dy
                if L2 < 4: continue
                t = max(0, min(1, -(x1 * dx + y1 * dy) / L2))
                px, py = x1 + t * dx, y1 + t * dy; d = math.hypot(px, py)
                if d < maxd and (best is None or d < best[0]): best = (d, px, py, dx, dy)
    if not best: return 0.0
    d, px, py, dx, dy = best
    road = math.degrees(math.atan2(dy, dx))           # local x runs along the road
    # local -y must point toward the road: (sin r, -cos r) . (px, py) > 0
    if math.sin(math.radians(road)) * px - math.cos(math.radians(road)) * py < 0: road += 180
    while road > 180: road -= 360
    while road < -180: road += 360
    return round(road, 1)

def layout(n, w, d, gap=14):
    cols = n if n <= 5 else math.ceil(n / 2)
    rows = math.ceil(n / cols)
    out = []
    for i in range(n):
        r, c = divmod(i, cols)
        inrow = min(cols, n - r * cols)
        u = (c - (inrow - 1) / 2) * (w + gap)
        v = ((rows - 1) / 2 - r) * (d + gap + 6)
        out.append([round(u, 1), round(v, 1), w, d])
    span_u = cols * w + (cols - 1) * gap
    span_v = rows * d + (rows - 1) * (gap + 6)
    return out, [round(span_u + 24), round(span_v + 24)]


def _inpoly(u, v, P):
    ins = False; j = len(P) - 1
    for i in range(len(P)):
        if (P[i][1] > v) != (P[j][1] > v) and u < (P[j][0] - P[i][0]) * (v - P[i][1]) / (P[j][1] - P[i][1]) + P[i][0]: ins = not ins
        j = i
    return ins

def _corners(t, s, fs, ox, oy, pad=1.5):
    x, y = t['x'] * s + ox, t['y'] * s + oy
    w, d = t['w'] * fs / 2 + pad, t['d'] * fs / 2 + pad
    a = math.radians(t.get('ang') or 0); c, n = math.cos(a), math.sin(a)
    pts = [(-w, -d), (w, -d), (w, d), (-w, d), (0, -d), (0, d), (-w, 0), (w, 0)]
    if t.get('lean'): pts += [(px + t['lean'][0], py + t['lean'][1]) for px, py in pts[:4]]
    return [(x + px * c - py * n, y + px * n + py * c) for px, py in pts]

def fit_towers(towers, ctx, P):
    """Keep the arrangement read from the renders but scale / shift it (and if needed shrink the footprints a little) so every building stands inside the registered plot."""
    xs = [q[0] for q in P]; ys = [q[1] for q in P]
    W, Dd = max(xs) - min(xs), max(ys) - min(ys)
    def ok(s, fs, ox, oy):
        return s >= fs - 1e-9 and all(_inpoly(u, v, P) for t in towers for u, v in _corners(t, s, fs, ox, oy)) and \
               all(_inpoly(u, v, P) for o in (ctx or []) if o.get('t') == 'pod' for u, v in _corners(o, s, fs, ox, oy, 0.5))
    offs = sorted(((dx, dy) for dx in range(-int(W / 2), int(W / 2) + 1, 2) for dy in range(-int(Dd / 2), int(Dd / 2) + 1, 2)), key=lambda q: q[0] ** 2 + q[1] ** 2)
    for fs in (1.0, 0.92, 0.84, 0.76, 0.68, 0.6):
        for s in (1.0, 0.95, 1.05, 0.9, 1.1, 0.85, 1.15, 0.8, 1.2, 0.75, 0.7, 0.65, 0.6, 0.55, 0.5):
            for ox, oy in offs:
                if ok(s, fs, ox, oy):
                    for t in towers + [o for o in (ctx or []) if 'x' in o]:
                        t['x'] = round(t['x'] * s + ox, 1); t['y'] = round(t['y'] * s + oy, 1)
                        if fs != 1:
                            t['w'] = round(t['w'] * fs, 1); t['d'] = round(t['d'] * fs, 1)
                            if t.get('pts'): t['pts'] = [[round(a * fs, 1), round(b * fs, 1)] for a, b in t['pts']]
                            for q in t.get('tiers') or []:
                                for k in ('w', 'd', 'dx', 'dy'):
                                    if k in q: q[k] = round(q[k] * fs, 1)
                    return (s, fs, ox, oy)
    return None

RERA_R = json.load(open(os.path.join(HERE, 't3dall', 'rera.json')))
RERA_N = json.load(open(os.path.join(HERE, 't3dall', 'rera_new.json')))

def rera_area(pid):
    """(carpet sq m, covered sq m) registered on Gujarat RERA for this listing"""
    import new_listings as NL
    if pid in NL.RERA_ID:
        v = RERA_N.get(str(NL.RERA_ID[pid])) or {}
        return v.get('carpet'), v.get('covered')
    pd = ((RERA_R.get(pid) or {}).get('pick') or {}).get('pd') or {}
    return pd.get('carpet'), pd.get('covered')

def _parea(q): return abs(sum(q[i][0] * q[i - 1][1] - q[i - 1][0] * q[i][1] for i in range(len(q)))) / 2

def foot_area(t):
    if t.get('pts'): return _parea(t['pts'])
    if t.get('shape') == 'round':
        r = t['r'] if t.get('r') is not None else min(t['w'], t['d']) / 2
        return t['w'] * t['d'] - (4 - math.pi) * r * r
    return t['w'] * t['d']

def scale_tower(t, k, pos=True):
    for key in ('w', 'd', 'r'):
        if t.get(key) is not None: t[key] = round(t[key] * k, 1)
    if pos: t['x'] = round(t['x'] * k, 1); t['y'] = round(t['y'] * k, 1)
    if t.get('pts'): t['pts'] = [[round(a * k, 1), round(b * k, 1)] for a, b in t['pts']]
    for q in t.get('tiers') or []:
        for key in ('w', 'd', 'dx', 'dy'):
            if q.get(key) is not None: q[key] = round(q[key] * k, 1)
    if t.get('lean'): pass

def size_from_carpet(pid, towers, kind, ctx, st=None):
    """Scale the footprints so a typical floor plate holds the carpet area registered on Gujarat RERA (carpet about 68% of a floor plate for homes, 72% for offices)."""
    carpet, covered = rera_area(pid)
    if not carpet: return None
    homes = sum(sum(1 for L in (t.get('stack') or st or []) if L.get('kind') == 'A') for t in towers)
    if not homes: return None
    eff = 0.72 if kind == 'commercial' else 0.68
    target = carpet / homes / eff                     # floor plate of one tower floor
    cur = sum(foot_area(t) for t in towers) / len(towers)
    if covered: target = min(target, covered * 0.9 / len(towers))      # all buildings stand within the registered ground coverage
    k = max(0.6, min(2.0, math.sqrt(target / cur)))
    if abs(k - 1) < 0.06: return 1.0
    for t in towers: scale_tower(t, k)
    for o in ctx or []:
        if o.get('t') == 'pod': o['w'] = round(o['w'] * k, 1); o['d'] = round(o['d'] * k, 1); o['x'] = round(o['x'] * k, 1); o['y'] = round(o['y'] * k, 1)
        elif o.get('t') == 'slab': o['x'] = round(o['x'] * k, 1); o['y'] = round(o['y'] * k, 1); o['w'] = round(o['w'] * k, 1)
    return k

def osm_inside(G, geo, P):
    """OpenStreetMap building outlines whose centre lies inside the registered plot, in plot coordinates, largest first"""
    r = math.radians(geo.get('rot') or 0); c, sn = math.cos(r), math.sin(r); out = []
    for b in (G or {}).get('bld', []):
        p = b['p'] if isinstance(b, dict) else b
        q = [((p[i] - geo['x']) * c + (p[i + 1] - geo['y']) * sn, -(p[i] - geo['x']) * sn + (p[i + 1] - geo['y']) * c) for i in range(0, len(p) - 1, 2)]
        if len(q) > 3 and abs(q[0][0] - q[-1][0]) + abs(q[0][1] - q[-1][1]) < 0.5: q = q[:-1]
        if len(q) < 3: continue
        A = _parea(q)
        cx = sum(u for u, v in q) / len(q); cy = sum(v for u, v in q) / len(q)
        if A > 150 and _inpoly(cx, cy, P): out.append(dict(a=A, x=cx, y=cy, q=q, h=b.get('h') if isinstance(b, dict) else None))
    return sorted(out, key=lambda o: -o['a'])

def use_osm(towers, B, order):
    """Give towers their real OpenStreetMap footprints: the labels in `order` take the largest outlines in turn, the rest the nearest one left."""
    B = list(B); done = set()
    def put(t, o):
        t['x'], t['y'] = round(o['x'], 1), round(o['y'], 1)
        t['pts'] = [[round(u - o['x'], 1), round(v - o['y'], 1)] for u, v in o['q']]
        us = [a for a, b in t['pts']]; vs = [b for a, b in t['pts']]
        t['w'], t['d'] = round(max(us) - min(us), 1), round(max(vs) - min(vs), 1)
        t.pop('shape', None); t.pop('r', None); t['ang'] = 0; t['_osm'] = True
        if t.get('tiers'): t['tiers'] = [dict(q, pts=q.get('pts')) for q in t['tiers'] if q.get('from', 0) > 0]
        B.remove(o); done.add(t['id'])
    for lab in order:
        t = next((t for t in towers if t['label'] == lab), None)
        if t and B: put(t, B[0])
    for t in towers:
        if t['id'] not in done and B:
            put(t, min(B, key=lambda o: (o['x'] - t['x']) ** 2 + (o['y'] - t['y']) ** 2))

def split_osm(towers, B, groups):
    """A mapped outline that holds two towers joined in one slab (registered as one block, e.g. 'A+B'): cut it in two along its length."""
    import sitegeo as SG
    for o, labs in zip(B, groups):
        deg, L, Dd, (cx, cy) = SG.mbr(o['q'])
        a = math.radians(deg); n = len(labs)
        for i, lab in enumerate(labs):
            t = next((t for t in towers if t['label'] == lab), None)
            if not t: continue
            off = (i - (n - 1) / 2) * L / n
            t.update(x=round(cx + off * math.cos(a), 1), y=round(cy + off * math.sin(a), 1), w=round(L / n - 1.0, 1), d=round(Dd, 1), ang=round(deg, 1), _osm=True)
            for k in ('shape', 'pts', 'r', 'tiers'): t.pop(k, None)

def mix_rows(p):
    rows = []
    for m in p['mix']:
        name, size, price = m[0], m[1], m[2]
        val = size if size and size != 'On request' else 'Size on request'
        if price and price not in ('On request', '') and not price.startswith('Ask'): val += ' · ' + price
        rows.append([name, val])
    return rows

def make(ALL):
    P = {p['id']: p for p in ALL}
    out = {}
    import forms as FM, sitegeo as SG, rera_floors as RF
    for pid in list(S) + [k for k in FM.NEW_S if k not in S]:
        if pid not in P: continue
        p = P[pid]
        s = S.get(pid) or dict(FM.NEW_S[pid])
        F = FM.FORMS.get(pid, {})
        kind = F.get('kind') or s.get('kind', 'residential')
        intl = s.get('intl')
        floorH = F.get('floorH') or s.get('floorH') or (4.0 if kind == 'commercial' else 3.6 if kind == 'mixed' else 3.2)
        plotPoly = None; G = None
        # ---- position, towers and surroundings
        if pid not in SH and pid not in PINS:     # listed from its Gujarat RERA plot only
            mk = 'GEO_SHANTIGRAM' if p['market'] == 'shantigram' else 'GEO_GIFT'
            G = SHG if mk == 'GEO_SHANTIGRAM' else GIFTG
            geo = dict(name=mk, file=GEO_FILE[mk], x=0, y=0, rot=0, radius=800)
            towers = []; plot = dict(w=60, d=40); pos_note = ''
        elif pid in SH:
            lat, lon, rot, labels, blocks, parcel = SH[pid]
            gx, gy = xy(ORIGIN['GEO_SHANTIGRAM'], lat, lon)
            geo = dict(name='GEO_SHANTIGRAM', file=GEO_FILE['GEO_SHANTIGRAM'], x=round(gx, 1), y=round(gy, 1), rot=rot, radius=800)
            towers = [dict(id=f'T{i+1}', label=labels[i], x=b[0], y=b[1], w=b[2], d=b[3]) for i, b in enumerate(blocks)]
            plot = dict(w=parcel[0], d=parcel[1])
            pos_note = 'Position: the same Google Maps pin as our Shantigram map. Tower blocks are laid out approximately.'
            G = SHG
        else:
            lat, lon = PINS[pid]
            n = s.get('n', 1)
            fw, fd = s.get('fp', (32, 24))
            if p['market'] == 'gift':
                gx, gy = xy(ORIGIN['GEO_GIFT'], lat, lon)
                G = GIFTG
                rot = road_angle(G, gx, gy)
                geo = dict(name='GEO_GIFT', file=GEO_FILE['GEO_GIFT'], x=round(gx, 1), y=round(gy, 1), rot=rot, radius=800)
            else:
                f = os.path.join(GEO_DIR, pid + '.json')
                if not os.path.exists(f):
                    print('t3d: no surroundings yet for', pid); continue
                G = json.load(open(f))
                gname = 'GEO_' + pid.upper().replace('-', '_')
                rot = road_angle(G, 0, 0)
                geo = dict(name=gname, file=f'assets/geo/{pid}.js', x=0, y=0, rot=rot, radius=650 if not intl else 550)
            blocks, parcel = layout(n, fw, fd, s.get('gap', 14))
            labels = s.get('labels') or ([p['name']] if n == 1 else [f'Tower {chr(65 + i)}' for i in range(n)])
            towers = [dict(id=f'T{i+1}', label=labels[i], x=b[0], y=b[1], w=b[2], d=b[3]) for i, b in enumerate(blocks)]
            plot = dict(w=parcel[0], d=parcel[1])
            pos_note = 'Position: the project’s Google Maps pin (checked 17 Oct 2026). Tower footprints and spacing are approximate; the row is lined up with the nearest road.'
            if s.get('centre_court'):   # site plan from the brochure: towers C and D at the back, A and B in front over the showroom podium on the ring road
                geo['rot'] = face_road(G, 0, 0)
                towers = [dict(id='T1', label='Tower A', x=28.6, y=-24, w=41, d=26), dict(id='T2', label='Tower B', x=-27.5, y=-24, w=41, d=26),
                          dict(id='T3', label='Tower C', x=-27.5, y=30.9, w=41, d=26), dict(id='T4', label='Tower D', x=28.6, y=30.9, w=41, d=26),
                          dict(id='T5', label='Showrooms', x=0.4, y=-49, w=97, d=22)]
                plot = dict(w=113, d=129)
                pos_note = 'Position: the project’s Google Maps pin (checked 17 Oct 2026), turned so the showroom front faces the ring road as on the brochure’s site plan; footprints are scaled from that plan.'
            if s.get('vision'):
                import bmc_city as BC
                geo.update(x=BC.ORIGIN[0], y=BC.ORIGIN[1], rot=BC.ROT, radius=1100)
                towers = [dict(id='T1', label='Vision Iconic', x=0, y=0, w=48, d=48, shape=BC.shape())]
                plot = dict(w=BC.PLOT_R * 2, d=BC.PLOT_R * 2)
                pos_note = ('Position and layout: Vision Iconic stands at the north-west end of Mercedes-Benz Places | Binghatti City, inside the road loop around the city’s Google Maps pin in Nad Al Sheba 1, '
                            'as shown on the developer’s aerial renders; exact plot boundaries are not published. The gold circle has the area of the registered plot (22,282 sq m). '
                            'The other 11 towers of the city are drawn for context from the renders: only Vision Iconic’s height (341 m) is published, so their heights are estimates. Vision Iconic’s curved wing is drawn as 20 steps falling from about 190 m to 40 m, read from the brochure renders; Burj Khalifa is marked 6 km away for orientation.')
        # ---- real site and building forms (forms.py): registered plot outline, tower positions, shapes, setbacks, crowns, podiums
        if F.get('site'):
            origin = ORIGIN.get(geo['name']) or ((G or {}).get('origin') and (G['origin']['lat'], G['origin']['lon'])) or tuple(PINS[pid])
            si = SG.site(F['site'], origin)
            if si and (si['ok'] or F.get('site_pos_only')):
                geo['x'], geo['y'] = si['x'], si['y']
                if si['ok'] and not F.get('site_pos_only'):
                    geo['rot'] = si['rot']; plotPoly = si['poly']; plot = dict(w=si['w'], d=si['d'])
                    pos_note = ('Plot: the boundary registered on the Gujarat RERA map service (its position, shape and orientation; '
                                f"{si['area']:,} sq m drawn against {si['land']:,.0f} sq m of registered land). " if si.get('land') else 'Plot: the boundary registered on the Gujarat RERA map service (position, shape and orientation). ')
                else:
                    geo['rot'] = road_angle(G, si['x'], si['y']) if G else 0
                    pos_note = 'Position: the centre of the plot drawn on the Gujarat RERA map service; the plot outline there does not match the registered land area, so the gold rectangle is a simplified outline lined up with the nearest road. '
            elif pid not in SH and pid not in PINS:
                print('t3d: no position for', pid); continue
        elif pid not in SH and pid not in PINS:
            print('t3d: no position for', pid); continue
        if F.get('towers'):
            towers = []
            for i, ft in enumerate(F['towers']):
                t = {k: v for k, v in ft.items() if k not in ('above', 'blk')}
                if 'tiers' in t: t['tiers'] = [{('from' if k == 'from_' else k): v for k, v in q.items()} for q in t['tiers']]
                t['id'] = f'T{i+1}'; t['_above'] = ft.get('above'); t['_blk'] = ft.get('blk')
                if t.get('levels'): t['stack'] = stack(t.pop('levels'), ground=None, start=1, label='Level')
                towers.append(t)
            pos_note += ('Layout: ' + F['note'] if F.get('note') else '')
            if not plotPoly:
                xs = [t['x'] + sx * t['w'] / 2 for t in towers for sx in (-1, 1)]; ys = [t['y'] + sy * t['d'] / 2 for t in towers for sy in (-1, 1)]
                plot = dict(w=round(max(xs) - min(xs) + 24), d=round(max(ys) - min(ys) + 24))
        elif F.get('note'):
            pos_note += 'Layout: ' + F['note']
        if F.get('ll_towers'):          # tower outlines mapped on OpenStreetMap (lat, lon)
            import sitegeo as SG2
            o0 = (G['origin']['lat'], G['origin']['lon']) if G and G.get('origin') else tuple(PINS[pid])
            allp = {lab: [xy(o0, la, lo) for la, lo in ll] for lab, ll in F['ll_towers'].items()}
            pts_all = [q for v in allp.values() for q in v]
            cx0 = sum(q[0] for q in pts_all) / len(pts_all); cy0 = sum(q[1] for q in pts_all) / len(pts_all)
            deg = SG2.mbr(next(iter(allp.values())))[0]; r0 = math.radians(deg); c0, s0 = math.cos(r0), math.sin(r0)
            geo.update(x=round(cx0, 1), y=round(cy0, 1), rot=round(deg, 1))
            loc = lambda q: ((q[0] - cx0) * c0 + (q[1] - cy0) * s0, -(q[0] - cx0) * s0 + (q[1] - cy0) * c0)
            for t in towers:
                if t['label'] in allp:
                    L = [loc(q) for q in allp[t['label']]]
                    if len(L) > 3 and abs(L[0][0] - L[-1][0]) + abs(L[0][1] - L[-1][1]) < 0.5: L = L[:-1]
                    tx = sum(q[0] for q in L) / len(L); ty = sum(q[1] for q in L) / len(L)
                    t.update(x=round(tx, 1), y=round(ty, 1), pts=[[round(a - tx, 1), round(b - ty, 1)] for a, b in L], ang=0, _osm=True)
                    us = [a for a, b in t['pts']]; vs = [b for a, b in t['pts']]; t['w'], t['d'] = round(max(us) - min(us), 1), round(max(vs) - min(vs), 1)
            xs = [t['x'] + a for t in towers for a, b in t.get('pts', [])]; ys = [t['y'] + b for t in towers for a, b in t.get('pts', [])]
            plot = dict(w=round(max(xs) - min(xs) + 30), d=round(max(ys) - min(ys) + 30))
            pos_note = F.get('pos_note', '') + ' '
        elif F.get('pos_note'): pos_note = F['pos_note'] + ' '
        ctx = json.loads(json.dumps(F['context'])) if F.get('context') else None
        # ---- units
        rows = mix_rows(p)
        short = p['label'] if len(p['label']) <= 26 else p['label'][:24].rstrip(' ,&') + '…'
        units = {'all': dict(name=p['label'], short=short, rows=rows, avail=p.get('available') or 'Ask for live availability')}
        for t in towers: t['type'] = 'all'
        # ---- floors
        lab = 'Level' if intl else 'Floor'
        if s.get('antonia'):
            units['shop'] = dict(name='Showrooms', short='Showrooms', rows=[['Use', 'Showrooms (floors 1–2)'], ['Price', 'On request']], avail=p.get('available'))
            units['office'] = dict(name='Offices', short='Offices', rows=[['Use', 'Offices (floors 3–42), 3 to 5 offices per floor'], ['Price', 'On request']], avail=p.get('available'))
            st = [dict(label='Ground floor', kind='M', use='Entrance lobby')] + [dict(label=f'Floor {f}', kind='A', unit='shop' if f <= 2 else 'office') for f in range(1, 43)]
        elif s.get('stratum'):
            units['shop'] = dict(name='Retail', short='Retail', rows=[['Use', 'Retail floors (ground to floor 2)']], avail=p.get('available'))
            units['office'] = dict(name='Offices', short='Offices', rows=rows or [['Use', 'Offices']], avail=p.get('available'))
            st = [dict(label='Ground floor', kind='A', unit='shop'), dict(label='Floor 1', kind='A', unit='shop'), dict(label='Floor 2', kind='A', unit='shop')] + [dict(label=f'Floor {f}', kind='A', unit='office') for f in range(3, 17)]
        elif s.get('centre_court'):
            units['all']['perFloor'] = '4 homes on typical floors'
            units['f1'] = dict(name='Homes + Centre Court club', short='Club level', rows=rows, perFloor='1 home (with a terrace), next to the Centre Court club: social room, game zone, society office', avail=p.get('available'))
            units['f2'] = dict(name='Homes over the showroom podium', short='Podium level', rows=rows, perFloor='2 homes (with terraces)', avail=p.get('available'))
            units['shop'] = dict(name='Showrooms', short='Showrooms', perFloor='', avail=p.get('available'),
                                 rows=[['Use', 'Showrooms facing the 60 m ring road'], ['Numbering', 'Ground 01–18, first floor 101–119, second floor 201–219 (as on the brochure plans)'], ['Registered', '56 shops in all (Gujarat RERA)'], ['Price', 'On request']])
            def cc_stack(top, terr, lower):
                st = [dict(label='Ground floor', kind='M', use='Entrance lobby with reception; ground-floor amenities: club lobby, gym, yoga, kids’ play, multi-sport court')]
                for f in range(1, top + 1):
                    e = dict(label=f'Floor {f}', kind='A')
                    if lower and f == 1: e['unit'] = 'f1'
                    elif lower and f == 2: e['unit'] = 'f2'
                    if f in terr: e.update(terrace=True)
                    st.append(e)
                return st
            ab = cc_stack(19, {4, 6, 10, 15, 19}, True); cd = cc_stack(21, {5, 7, 11, 16, 21}, False)
            for t in towers:
                if t['label'] in ('Tower A', 'Tower B'): t['stack'] = ab; t['terrace'] = '4 BHK homes with terraces on this floor (brochure: floors 4, 6, 10, 15 and 19 in A and B)'
                elif t['label'] in ('Tower C', 'Tower D'): t['stack'] = cd; t['terrace'] = '4 BHK homes with terraces on this floor (brochure: floors 5, 7, 11, 16 and 21 in C and D)'
                else: t['stack'] = [dict(label='Ground floor', kind='A', unit='shop'), dict(label='Floor 1', kind='A', unit='shop'), dict(label='Floor 2', kind='A', unit='shop')]; t['type'] = 'shop'
            st = cd; floorH = 3.6
        elif s.get('vision'):
            vis_rows = [['1 bedroom', '1,017 homes'], ['2 bedroom', '281 homes'], ['3 bedroom', '110 homes'], ['4 bedroom', '9 homes'], ['5 bedroom', '9 homes'], ['Price', 'On request']]
            units['all'] = dict(name='Vision Iconic residences', short='1 – 5 bedroom', rows=vis_rows, avail='DLD: 1,426 homes registered (project #4544)')
            units['shop'] = dict(name='High-street retail', short='Retail', rows=[['Use', '27 ground-floor high-street shops (DLD: 27 commercial units)']], perFloor='', avail='Ask for availability')
            st = ([dict(label='Ground floor', kind='A', unit='shop', pod=True), dict(label='Mezzanine', kind='M', use='Double-height grand lobby and valet drop-off', pod=True)]
                  + [dict(label=f'Podium {i}', kind='M', pod=True, use='Podium level: parking and amenities, with the circular podium deck and 2,966 sq m water plaza') for i in range(1, 6)]
                  + [dict(label=f'Residential floor {f}', kind='A') for f in range(1, 68)]
                  + [dict(label='Mechanical levels (4)', kind='X', use='Four mechanical service levels (their positions in the stack are not published; shown together here)', sub='Services', levels=4),
                     dict(label='Roof deck', kind='M', use='Dedicated roof deck with the illuminated beacon')])
            floorH = 3.6
        elif s.get('newport'):
            st = [dict(label=f'Level {f}', kind='X', use='Lower levels of Newport Plaza: other uses, not part of Newport Residences') for f in range(1, 23)] + [dict(label=f'Level {f}', kind='A') for f in range(23, 46)]
            floorH = 3.6
        elif s.get('levels_total'):
            st = stack(s['levels_total'], ground=None, start=1, label=lab)
        elif s.get('per'):
            for t, a in zip(towers, s['per']): t['stack'] = stack(a)
            st = stack(max(s['per']))
        elif 'above' not in s:
            st = None
        else:
            st = stack(s['above'])
            if s.get('podium'):
                st[0] = dict(label='Podium', kind='M', use='Podium with parking and amenities (number of podium levels not published)', h=9.0)
        # ---- floors from the unit numbers on the Gujarat RERA register (rera_floors.py), else the published floor count
        floors_src = ''
        if not any(s.get(k) for k in ('antonia', 'stratum', 'centre_court', 'vision', 'newport', 'levels_total')):
            for t in towers:
                rc = RF.tower_counts(pid, t['label'], t.get('_blk'))
                if rc and rc[0]:
                    t['stack'] = RF.stack_from(rc[0], rc[1], rc[2], top=F.get('top'), kind=kind)
                    floors_src = ' Floors: from the unit numbers on the Gujarat RERA register (each floor shows how many units are registered on it).'
                elif t.get('_above') is not None:
                    t['stack'] = stack(t['_above'])
                elif F.get('above') is not None:
                    t['stack'] = stack(F['above'])
            if st is None:
                st = next((t['stack'] for t in towers if t.get('stack')), None) or stack(F.get('above') or 10)
        # ---- footprints: real outlines from OpenStreetMap where the buildings are mapped, else sized from the registered carpet area, then fitted inside the plot
        if plotPoly and F.get('osm_split'):
            B = osm_inside(G, geo, plotPoly)
            if len(B) >= len(F['osm_split']):
                split_osm(towers, B, F['osm_split'])
                pos_note += ' Building outlines: as mapped on OpenStreetMap inside the registered plot' + (f" ({F['osm_note']})" if F.get('osm_note') else '') + '.'
        if plotPoly and F.get('osm') is not None:
            B = osm_inside(G, geo, plotPoly)
            if B:
                use_osm(towers, B, F['osm'])
                pos_note += ' Building outlines: as mapped on OpenStreetMap inside the registered plot' + (f" ({F['osm_note']})" if F.get('osm_note') else '') + '.'
        if not any(t.get('_osm') for t in towers) and not F.get('no_size') and not s.get('vision') and not s.get('centre_court'):
            k = size_from_carpet(pid, towers, kind, ctx, st)
            if k and k != 1.0: pos_note += ' Footprint sizes are estimated from the carpet area registered on Gujarat RERA (a floor plate holding each floor’s share, with carpet taken as about 70% of the plate).'
        if plotPoly and not all(t.get('_osm') for t in towers):
            fit = fit_towers([t for t in towers if not t.get('_osm')], ctx, plotPoly)
            if not fit: print('t3d: towers do not fit the plot of', pid)
            elif fit[1] < 1: pos_note += f' To fit the registered plot, footprints are drawn {round((1 - fit[1]) * 100)}% smaller.'
        for t in towers:
            t.pop('_above', None); t.pop('_blk', None); t.pop('_osm', None)
        if F.get('floors_note'): floors_src += ' ' + F['floors_note']
        if s.get('height') and not s.get('floorH'):
            tall = max((t.get('stack') or st for t in towers), key=len)
            levels = sum(L.get('levels', 1) for L in tall)
            floorH = round(s['height'] / levels, 2) if s['height'] / levels <= 4.6 else floorH
        cfg = dict(project=p['name'], interest=p['label'], floorH=floorH, stack=st, towers=towers, units=units, plot=plot, geo=geo, kind=kind,
                   startFloor=st[min(len(st) - 1, max(1, len(st) // 2))]['label'],
                   enqLabel='Enquire about this floor', note=f"Model built from published figures. {s['src']}.{floors_src} {pos_note} Surroundings (roads, water, parks, existing buildings) are from OpenStreetMap; buildings with no height in OpenStreetMap are shown low. Finishes are simplified.")
        if plotPoly: cfg['plotPoly'] = plotPoly
        if ctx: cfg['context'] = ctx
        if F.get('height') or s.get('height'): cfg['height'] = F.get('height') or s['height']
        if s.get('per_floor'): cfg['perFloor'] = s['per_floor']
        if s.get('centre_court'): cfg['camTurn'] = 3.1416
        if F.get('camTurn') is not None: cfg['camTurn'] = F['camTurn']
        if s.get('vision'):
            import bmc_city as BC
            cfg.update(BC.config())
        if kind == 'commercial': cfg['perFloorLabel'] = 'Units on each floor'
        out[pid] = cfg
    return out

GIFTG = None; SHG = None
def load_gift(path):
    global GIFTG, SHG
    s = open(path).read()
    GIFTG = json.loads(s[s.index('{'):s.rindex('}') + 1])
    s = open(path.replace('geo-gift.js', 'geo-shantigram.js')).read()
    SHG = json.loads(s[s.index('{'):s.rindex('}') + 1])

def write_geo(asset_dir):
    """Write assets/geo/<id>.js for each project that has its own OpenStreetMap extract."""
    os.makedirs(os.path.join(asset_dir, 'geo'), exist_ok=True)
    for f in sorted(os.listdir(GEO_DIR)):
        pid = f[:-5]
        g = json.load(open(os.path.join(GEO_DIR, f)))
        name = 'GEO_' + pid.upper().replace('-', '_')
        js = ('/* Map geometry from OpenStreetMap (© OpenStreetMap contributors, ODbL), metres east/north of the project pin. Extracted 17 Oct 2026. */\n'
              f'window.{name}=' + json.dumps(g, separators=(',', ':')) + ';\n')
        open(os.path.join(asset_dir, 'geo', pid + '.js'), 'w').write(js)
