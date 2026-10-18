"""Registered plot outlines from the Gujarat RERA map service -> site frame for the 3D explorer."""
import json, math, os
HERE = os.path.dirname(os.path.abspath(__file__))
POLY = json.load(open(os.path.join(HERE, 't3dall', 'rera_poly.json')))
R = json.load(open(os.path.join(HERE, 't3dall', 'rera.json')))
RN = json.load(open(os.path.join(HERE, 't3dall', 'rera_new.json')))
E = 6378137.0; D = math.pi / 180

def xy(origin, lat, lon):
    la0, lo0 = origin
    return ((lon - lo0) * D * E * math.cos(la0 * D), (lat - la0) * D * E)

def area(P):
    return abs(sum(P[i][0] * P[(i + 1) % len(P)][1] - P[(i + 1) % len(P)][0] * P[i][1] for i in range(len(P)))) / 2

def hull(P):
    P = sorted(set(map(tuple, P)))
    if len(P) < 3: return P
    def cr(o, a, b): return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in P:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    for p in reversed(P):
        while len(up) >= 2 and cr(up[-2], up[-1], p) <= 0: up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]

def mbr(P):
    """minimum-area bounding rectangle: (angle deg of long side, w, d, centre)"""
    H = hull(P); best = None
    for i in range(len(H)):
        x1, y1 = H[i]; x2, y2 = H[(i + 1) % len(H)]
        a = math.atan2(y2 - y1, x2 - x1); c, s = math.cos(a), math.sin(a)
        us = [x * c + y * s for x, y in H]; vs = [-x * s + y * c for x, y in H]
        w, d = max(us) - min(us), max(vs) - min(vs)
        if best is None or w * d < best[0]:
            uc, vc = (max(us) + min(us)) / 2, (max(vs) + min(vs)) / 2
            best = (w * d, a, w, d, (uc * c - vc * s, uc * s + vc * c))
    _, a, w, d, cen = best
    if d > w: a += math.pi / 2; w, d = d, w
    deg = math.degrees(a)
    while deg > 90: deg -= 180
    while deg <= -90: deg += 180
    return deg, w, d, cen

def land_of(key):
    if key.startswith('new:'):
        return (RN.get(key[4:]) or {}).get('land')
    v = R.get(key) or {}
    return ((v.get('pick') or {}).get('pd') or {}).get('land')

def site(key, origin):
    """-> dict(x, y, rot, poly(local), w, d, area, ok) in the frame of `origin` (lat, lon), or None"""
    v = POLY.get(key)
    if not v or not v.get('poly') or len(v['poly']) < 3: return None
    P = [xy(origin, la, lo) for la, lo in v['poly']]
    A = area(P); land = land_of(key)
    ok = A > 400 and (not land or 0.45 <= A / land <= 2.3)
    rot, w, d, (cx, cy) = mbr(P)
    r = math.radians(rot); c, s = math.cos(r), math.sin(r)
    loc = [[round((x - cx) * c + (y - cy) * s, 1), round(-(x - cx) * s + (y - cy) * c, 1)] for x, y in P]
    return dict(x=round(cx, 1), y=round(cy, 1), rot=round(rot, 1), poly=loc, w=round(w, 1), d=round(d, 1), area=round(A), land=land, ok=ok)

def centroid(key):
    v = POLY.get(key)
    if not v or not v.get('poly'): return None
    return (sum(p[0] for p in v['poly']) / len(v['poly']), sum(p[1] for p in v['poly']) / len(v['poly']))
