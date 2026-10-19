"""Shivalik Wave 3D model from the developer's brochure floor plans.

Input : floor-plan pages (fp/h-N.png, 220 dpi) and the brochure ground floor page (br/gf-12.png),
        unit regions found by seg.py (seg/cN.json) and labelled in labels.py.
Output: geometry in metres, plot frame (x along the building's long side, towards Vaishnodevi Circle / north-north-east;
        y across it, towards S.G. Highway / west-north-west), origin at the centre of the first-floor outline.
"""
import json, math, sys
import numpy as np, cv2
from shapely.geometry import Polygon, MultiPolygon, LineString, box
from shapely.ops import unary_union, split
from labels import MAP

PX_PER_FT = 5.45
K = PX_PER_FT / 0.3048            # page pixels per metre (220 dpi floor-plan pages)
CROP = (150, 200, 2420, 1000)     # drawing area on the floor-plan pages

# ------------------------------------------------------------------ masks
def load(p):
    return cv2.imread(f'fp/h-{p}.png')[:, :, ::-1].copy()

def building_mask(im):
    x0, y0, x1, y1 = CROP
    a = im.astype(int)
    white = (a.min(axis=2) >= 238)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    green = (g > r + 8) & (g > b + 8)
    terr = cv2.morphologyEx(green.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    terr = cv2.morphologyEx(terr, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8)) > 0     # terraces: green fill with hatching
    m = (~white & ~green & ~terr).astype(np.uint8)
    keep = np.zeros_like(m); keep[y0:y1, x0:x1] = 1; m &= keep
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))      # drop the thin plot-boundary line
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, connectivity=4)
    big = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    m = (lab == big).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((11, 11), np.uint8))    # drop parapet lines left around terraces
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, connectivity=4)
    m = (lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))).astype(np.uint8)
    inv = 1 - m                                                               # fill small holes only (text, symbols)
    n, lab, st, _ = cv2.connectedComponentsWithStats(inv, connectivity=4)
    for i in range(1, n):
        x, y, w, h, a = st[i]
        if a < 6000 and x > 0 and y > 0 and x + w < m.shape[1] and y + h < m.shape[0]: m[lab == i] = 1
    H = np.zeros_like(m)                                                      # large holes left = terraces inside a parapet line
    n, lab, st, _ = cv2.connectedComponentsWithStats(1 - m, connectivity=4)
    for i in range(1, n):
        x, y, w, h, a = st[i]
        if a >= 6000 and x > 0 and y > 0 and x + w < m.shape[1] and y + h < m.shape[0]: H[lab == i] = 1
    if H.any():
        disk = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (51, 51))
        Hd = cv2.dilate(H, disk)
        m2 = m & (1 - Hd)
        n, lab, st, _ = cv2.connectedComponentsWithStats(m2, connectivity=4)
        m2 = (lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))).astype(np.uint8)
        m = cv2.dilate(m2, disk) & m & (1 - H)
        n, lab, st, _ = cv2.connectedComponentsWithStats(m, connectivity=4)
        m = (lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))).astype(np.uint8)
    return m

def unit_labels(shape, comps, mapping):
    L = np.zeros(shape[:2], np.int32)
    names = {}
    for j, (cid, no) in enumerate(sorted(mapping.items(), key=lambda kv: kv[1]), start=1):
        c = np.array(comps[cid]['contour']).reshape(-1, 1, 2)
        cv2.drawContours(L, [c], -1, j, -1)
        names[j] = no
    return L, names

def grow(L, F, ring_px=26, wall_px=8, steps=40):
    """give each unit its share of the facade band and of the walls next to it (geodesic growth, limited distance)"""
    inside = cv2.distanceTransform(F, cv2.DIST_L2, 5)               # distance to the outside of the building
    unit = (L > 0).astype(np.uint8)
    near_unit = cv2.distanceTransform(1 - unit, cv2.DIST_L2, 5)
    allow = (F > 0) & (L == 0) & ((inside <= ring_px) | (near_unit <= wall_px))
    G = L.copy()
    k = np.ones((3, 3), np.uint8)
    for _ in range(steps):
        changed = False
        for j in np.unique(G[G > 0]):
            m = (G == j).astype(np.uint8)
            d = cv2.dilate(m, k) & allow.astype(np.uint8) & (G == 0)
            if d.any():
                G[d > 0] = j; changed = True
        if not changed: break
        allow &= (G == 0)
    return G

# ------------------------------------------------------------------ vectorise
def poly_from_mask(m, eps=2.5):
    cs, _ = cv2.findContours(m.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not cs: return None
    c = max(cs, key=cv2.contourArea)
    a = cv2.approxPolyDP(c, eps, True)[:, 0, :].astype(float)
    return a

# page pixel -> p6-frame pixel transforms (affine: x' = sx*x + tx, y' = sy*y + ty)
def fit_axis(src, dst):
    A = np.vstack([src, np.ones_like(src)]).T
    s, t = np.linalg.lstsq(A, dst, rcond=None)[0]
    return float(s), float(t)

def bbox_pairs(pa, ca, ma, pb, cb, mb, nos):
    ia = {v: k for k, v in ma.items()}; ib = {v: k for k, v in mb.items()}
    xs, xd, ys, yd = [], [], [], []
    for no in nos:
        x, y, w, h = ca[ia[no]]['bbox']; X, Y, W, H = cb[ib[no]]['bbox']
        xs += [x, x + w]; xd += [X, X + W]; ys += [y, y + h]; yd += [Y, Y + H]
    return np.array(xs, float), np.array(xd, float), np.array(ys, float), np.array(yd, float)

def to_plot(pts, T, origin):
    """page px -> plot metres: x grows to the left of the page (north), y grows down the page (front, highway side)"""
    (sx, tx), (sy, ty) = T
    X = pts[:, 0] * sx + tx; Y = pts[:, 1] * sy + ty
    return np.stack([-(X - origin[0]) / K, (Y - origin[1]) / K], axis=1)

def clean(P):
    P = Polygon(P)
    if not P.is_valid: P = P.buffer(0)
    if isinstance(P, MultiPolygon): P = max(P.geoms, key=lambda g: g.area)
    return P.simplify(0.08)

def hole_free(geom):
    """split polygons with holes into hole-free pieces (the viewer's prisms take a single outline)"""
    out = []
    todo = list(geom.geoms) if hasattr(geom, 'geoms') else [geom]
    while todo:
        g = todo.pop()
        if g.is_empty or g.area < 0.5: continue
        if not g.interiors:
            out.append(g); continue
        hx = g.interiors[0].centroid.x
        miny, maxy = g.bounds[1] - 1, g.bounds[3] + 1
        parts = split(g, LineString([(hx, miny), (hx, maxy)]))
        todo += [p for p in parts.geoms]
    return out


# ------------------------------------------------------------------ driver
FLOOR_PAGES = {'1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6-17': 6, '18': 7, '19-24': 8, '25-29': 9}

def page_transform(p):
    """axis fits from page pixels to the 6th-17th floor page (the reference); pages 1-4 and 7-9 share its frame"""
    if p != 5: return ((1.0, 0.0), (1.0, 0.0))
    c5 = json.load(open('seg/c5.json')); c6 = json.load(open('seg/c6.json'))
    nos = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '14', '15', '16', '17']
    xs, xd, ys, yd = bbox_pairs(5, c5, MAP[5], 6, c6, MAP[6], nos)
    return fit_axis(xs, xd), fit_axis(ys, yd)

def gf_transform():
    """brochure ground floor (north at the bottom of the page) -> reference page: rotate a quarter turn, then fit the axes"""
    cg = json.load(open('seg/cgf.json')); c1 = json.load(open('seg/c1.json'))
    inv1 = {v: k for k, v in MAP[1].items()}
    xs, xd, ys, yd = [], [], [], []
    for i in range(12):                                   # brochure components 0..11 are showrooms 1..12, above 101..112
        x, y, w, h = cg[i]['bbox']; X, Y, W, H = c1[inv1['%02d' % (i + 1)]]['bbox']
        # rotated: X' = -y, Y' = x
        xs += [-(y + h), -y]; xd += [X, X + W]; ys += [x, x + w]; yd += [Y, Y + H]
    return fit_axis(np.array(xs, float), np.array(xd, float)), fit_axis(np.array(ys, float), np.array(yd, float))

GF_MAP = {i: str(i + 1) for i in range(12)}; GF_MAP.update({14: '14', 13: '15', 12: '16'})

def process(key, origin):
    p = FLOOR_PAGES[key]
    im = load(p); F = building_mask(im)
    T = page_transform(p)
    outline = clean(to_plot(poly_from_mask(F, 2.0), T, origin))
    units = {}
    if p in MAP:
        comps = json.load(open(f'seg/c{p}.json'))
        L, names = unit_labels(im.shape, comps, MAP[p])
        G = grow(L, F)
        for j, no in names.items():
            P = poly_from_mask(G == j, 2.0)
            u = clean(to_plot(P, T, origin)).intersection(outline)
            if isinstance(u, MultiPolygon): u = max(u.geoms, key=lambda g: g.area)
            units[no] = u
    return outline, units

def process_gf(origin, outline1):
    comps = json.load(open('seg/cgf.json'))
    (sx, tx), (sy, ty) = gf_transform()
    units = {}
    for cid, no in GF_MAP.items():
        c = np.array(comps[cid]['contour'], float)
        c = cv2.approxPolyDP(c.reshape(-1, 1, 2).astype(np.float32), 2.0, True)[:, 0, :].astype(float)
        rot = np.stack([-c[:, 1], c[:, 0]], axis=1)            # quarter turn into the floor-plan page orientation
        P = to_plot(rot, ((sx, tx), (sy, ty)), origin)
        u = clean(P).buffer(0.35, join_style=2).intersection(outline1)
        if isinstance(u, MultiPolygon): u = max(u.geoms, key=lambda g: g.area)
        units[no] = u
    # trim overlaps between neighbours created by the buffer
    names = sorted(units, key=int)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if units[a].intersects(units[b]):
                ov = units[a].intersection(units[b])
                if ov.area > 0.01:
                    units[b] = units[b].difference(ov.buffer(0.01))
    return units

def run():
    # origin: centre of the first-floor outline on the reference page
    F1 = building_mask(load(1))
    x, y, w, h = cv2.boundingRect(F1)
    origin = (x + w / 2, y + h / 2)
    out = {'origin_px': origin, 'px_per_m': K, 'floors': {}}
    o1 = None
    for key in FLOOR_PAGES:
        outline, units = process(key, origin)
        if key == '1': o1 = outline
        out['floors'][key] = dict(outline=list(outline.exterior.coords)[:-1], units={k: list(v.exterior.coords)[:-1] for k, v in units.items()})
        print(key, 'outline %.0f m2' % outline.area, 'bounds', [round(b, 1) for b in outline.bounds], 'units', len(units),
              'unit area %.0f m2' % sum(v.area for v in units.values()))
    gf = process_gf(origin, o1)
    out['floors']['G'] = dict(outline=out['floors']['1']['outline'], units={k: list(v.exterior.coords)[:-1] for k, v in gf.items()})
    print('G units', len(gf), 'area %.0f' % sum(v.area for v in gf.values()))
    json.dump(out, open('wave_geom.json', 'w'))

if __name__ == '__main__':
    run()
