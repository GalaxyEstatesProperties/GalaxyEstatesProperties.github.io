"""Antonia (Antonia Infra LLP, Vaishnodevi Circle) 3D explorer from the developer's brochure (SPIRAL BOOK, 22-06-26).

Plans: brochure pages 7 (ground), 8 (1st & 2nd), 9 (3rd-20th), 10 (21st skip), 11 (22nd-31st), 12 (32nd-42nd),
rendered at 300 dpi (br/x-NN.png). All plan pages share one page frame (site plan in the same place).
Heights: the section on page 13 (to scale; checked by measuring the drawing).
Scale: 13.25 px per foot at 300 dpi (checked: 12'6" foyer = 164 px; 14'0" offices = 184-185 px; 28'3" = 377 px).
Plot frame: x along page-right (north on the brochure compass), y along page-up (west); origin at the centre of the
typical floor plate. Map rotation 84.0 deg: the brochure's 12 m road (page-vertical) and 60 m road (S.G. Highway) are
then parallel to the OpenStreetMap roads (both within 0.5 deg).
"""
import json, math, sys
import numpy as np, cv2
from shapely.geometry import Polygon, MultiPolygon, box, LineString
from shapely.ops import unary_union, split

K = 13.25 / 0.3048                       # page px per metre
X0, Y0 = 1860.5, 2811.5                  # centre of the typical floor plate (page px)
CROP = (1240, 2158, 2480, 3447)

def to_plot(P):
    P = np.asarray(P, float)
    return np.stack([(P[:, 0] - X0) / K, -(P[:, 1] - Y0) / K], axis=1)

def page(p):
    return cv2.imread(f'br/x-{p:02d}.png')[:, :, ::-1].copy()

def bmask(p):
    im = page(p).astype(int)
    mx = im.max(axis=2); mn = im.min(axis=2)
    m = (~((mx - mn <= 8) & (mn >= 200))).astype(np.uint8)
    x0, y0, x1, y1 = CROP; k = np.zeros_like(m); k[y0:y1, x0:x1] = 1; m &= k
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((13, 13), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, connectivity=4)
    m = (lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))).astype(np.uint8)
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    f = np.zeros_like(m); cv2.drawContours(f, cs, -1, 1, -1)
    return f

def comps(p, color=(233, 226, 205), tol=8, min_area=20000):
    im = page(p)
    d = np.abs(im.astype(int) - np.array(color)).max(axis=2)
    m = (d <= tol).astype(np.uint8); x0, y0, x1, y1 = CROP; k = np.zeros_like(m); k[y0:y1, x0:x1] = 1; m &= k
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m, connectivity=4)
    out = []
    for i in range(1, n):
        if st[i, 4] < min_area: continue
        c = (lab == i).astype(np.uint8)
        c = cv2.morphologyEx(c, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
        out.append(dict(mask=c, cx=float(cen[i][0]), cy=float(cen[i][1]), bbox=st[i, :4].tolist()))
    return out

def grow(L, F, ring_px=40, wall_px=14, steps=60):
    inside = cv2.distanceTransform(F, cv2.DIST_L2, 5)
    unit = (L > 0).astype(np.uint8)
    near = cv2.distanceTransform(1 - unit, cv2.DIST_L2, 5)
    allow = (F > 0) & (L == 0) & ((inside <= ring_px) | (near <= wall_px))
    G = L.copy(); k = np.ones((3, 3), np.uint8)
    for _ in range(steps):
        ch = False
        for j in np.unique(G[G > 0]):
            d = cv2.dilate((G == j).astype(np.uint8), k) & allow.astype(np.uint8) & (G == 0)
            if d.any(): G[d > 0] = j; ch = True
        if not ch: break
        allow &= (G == 0)
    return G

def poly_of(mask, eps=3.0):
    cs, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cs, key=cv2.contourArea)
    a = cv2.approxPolyDP(c, eps, True)[:, 0, :].astype(float)
    P = Polygon(to_plot(a))
    if not P.is_valid: P = P.buffer(0)
    if isinstance(P, MultiPolygon): P = max(P.geoms, key=lambda g: g.area)
    return P.simplify(0.05)

# unit numbers by position, left to right on the page (page-left = south)
ORDER = {8: ['04', '03', '02', '01'], 11: ['05', '04', '03', '02', '01'], 12: ['03', '02', '01']}

def floor(p):
    F = bmask(p)
    outline = poly_of(F, 2.5)
    units = {}
    if p in ORDER:
        cs = sorted(comps(p), key=lambda c: c['cx'])
        assert len(cs) == len(ORDER[p]), (p, len(cs))
        L = np.zeros(F.shape, np.int32)
        for j, c in enumerate(cs, start=1): L[c['mask'] > 0] = j
        G = grow(L, F)
        for j, no in enumerate(ORDER[p], start=1):
            u = poly_of(G == j, 2.5).intersection(outline)
            if isinstance(u, MultiPolygon): u = max(u.geoms, key=lambda g: g.area)
            units[no] = u
    return outline, units

def gf_outline():
    # ground floor: the outer wall rectangle (walls x 1277-2440, y 2225 to the slab edge at 3405)
    return Polygon(to_plot([[1277, 2225], [2440, 2225], [2440, 3405], [1277, 3405]]))

if __name__ == '__main__':
    out = {}
    for key, p in (('1-2', 8), ('3-20', 11), ('21', 10), ('22-31', 11), ('32-42', 12)):
        o, u = floor(p)
        out[key] = dict(outline=list(o.exterior.coords)[:-1], units={k: list(v.exterior.coords)[:-1] for k, v in u.items()})
        print(key, 'outline %.1f m2' % o.area, [round(b, 2) for b in o.bounds], {k: round(v.area, 1) for k, v in u.items()})
    g = gf_outline(); out['G'] = dict(outline=list(g.exterior.coords)[:-1], units={})
    print('G', round(g.area, 1), [round(b, 2) for b in g.bounds])
    json.dump(out, open('antonia_geom.json', 'w'))
