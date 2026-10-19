"""Building outlines for the Shantigram 3D explorers (18 Oct 2026), in lat/lon.

Method: each project's official master plan / ground-floor plan (Adani Realty, Shivalik / Housiey for Greenfield) was georeferenced
onto current satellite imagery with a similarity transform (control points at tower centres, refined so the footprints sit on the
visible roofs and slabs) -> fitplan.py results in sat/<name>_fit.json. Tower outlines are the official typical-floor-plan outlines
(outline.py) placed into each tower's rectangle on the master plan, then split into the registered blocks / wings.
North Park villas: building footprints as drawn on Google Maps (fpseg.py), assigned to the Gujarat RERA phase outlines."""
import json, math, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))

def _load(name):
    fit = json.load(open(os.path.join(HERE, 'sat', name + '_fit.json')))
    spec = json.load(open(os.path.join(HERE, 'sat', 'spec_' + name + '.json')))
    meta = json.load(open(os.path.join(HERE, 'newimg', spec['sat'] + '.meta.json')))
    return fit['prm'], meta

def plan2ll(name, pts):
    (a, b, tx, ty), meta = _load(name)
    W = 256 * 2 ** meta['z']; out = []
    for x, y in pts:
        X = meta['X0'] + a * x - b * y + tx; Y = meta['Y0'] + b * x + a * y + ty
        out.append([round(math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * Y / W)))), 7), round(X / W * 360 - 180, 7)])
    return out

def outline(name):
    return json.load(open(os.path.join(HERE, 'sat', name + '_outline.json')))['norm']

def clip(poly, a, b, c):
    """keep the part of polygon with a*u + b*v <= c (Sutherland-Hodgman)"""
    out = []; n = len(poly)
    for i in range(n):
        P, Q = poly[i], poly[(i + 1) % n]
        fp, fq = a * P[0] + b * P[1] - c, a * Q[0] + b * Q[1] - c
        if fp <= 0: out.append(P)
        if (fp <= 0) != (fq <= 0):
            t = fp / (fp - fq); out.append([P[0] + t * (Q[0] - P[0]), P[1] + t * (Q[1] - P[1])])
    return out

def urange(norm, u0, u1):
    p = clip(norm, 1, 0, u1)
    return clip(p, -1, 0, -u0)

def vrange(norm, v0, v1):
    p = clip(norm, 0, 1, v1)
    return clip(p, 0, -1, -v0)

GF_RECTS = {'Block A': (315, 478, 490, 820), 'Block B': (765, 478, 938, 820), 'Block C': (1215, 478, 1388, 820)}
GF_TURN = dict(rot90=True, flipx=True, flipy=True)

def place(norm, rect, rot90=False, flipx=False, flipy=False):
    """normalised outline (u, v in 0..1) into plan rectangle (x0, y0, x1, y1); rot90 turns a horizontal drawing upright"""
    x0, y0, x1, y1 = rect; out = []
    for u, v in norm:
        if rot90: u, v = v, 1 - u
        if flipx: u = 1 - u
        if flipy: v = 1 - v
        out.append([x0 + u * (x1 - x0), y0 + v * (y1 - y0)])
    return out

def box_split(box, n, order):
    """split a (rotated) rectangle given by 4 corners into n parts along its long side; order: 'x' / '-x' / 'y' / '-y' sorts the parts by centre"""
    B = np.array(box, float); c = B.mean(0)
    e1 = B[1] - B[0]; e2 = B[2] - B[1]
    L, S = (e1, e2) if np.linalg.norm(e1) >= np.linalg.norm(e2) else (e2, e1)
    parts = []
    for i in range(n):
        f0, f1 = -0.5 + i / n, -0.5 + (i + 1) / n
        q = [c + L * f0 - S / 2, c + L * f1 - S / 2, c + L * f1 + S / 2, c + L * f0 + S / 2]
        parts.append([list(map(float, p)) for p in q])
    key = {'x': lambda p: np.mean([q[0] for q in p]), '-x': lambda p: -np.mean([q[0] for q in p]),
           'y': lambda p: np.mean([q[1] for q in p]), '-y': lambda p: -np.mean([q[1] for q in p])}[order]
    return sorted(parts, key=key)

def poly_split(poly, n, axis, order):
    """split a plan polygon into n equal slices across its bounding box along axis 'x' or 'y'"""
    xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
    lo, hi = (min(xs), max(xs)) if axis == 'x' else (min(ys), max(ys))
    out = []
    for i in range(n):
        a0, a1 = lo + (hi - lo) * i / n, lo + (hi - lo) * (i + 1) / n
        if axis == 'x': q = clip(clip(poly, 1, 0, a1), -1, 0, -a0)
        else: q = clip(clip(poly, 0, 1, a1), 0, -1, -a0)
        out.append(q)
    return out if order in ('x', 'y') else out[::-1]

def R(x0, y0, x1, y1): return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]

def build():
    G = {}
    # ---------------- Aster + Aster Neo (Adani master layout of Aster NEO; tower letters as printed on it)
    seg = json.load(open(os.path.join(HERE, 'sat', 'plan_aster_seg.json')))
    AB = box_split(seg['neo'][0]['box'], 2, 'x'); GH = box_split(seg['neo'][1]['box'], 2, 'x')        # G lower-left, H upper-right
    CD = box_split(seg['aster'][0]['box'], 2, 'x'); IJ = box_split(seg['aster'][2]['box'], 2, 'x')    # I upper-left, J lower-right
    KLM = box_split(seg['aster'][1]['box'], 3, 'x')                                                     # K upper-left ... M lower-right
    G['aster-neo'] = dict(towers={**{f'Tower {k}': plan2ll('aster', p) for k, p in zip('AB', AB)}, **{f'Tower {k}': plan2ll('aster', p) for k, p in zip('GH', GH)},
                                  **{f'Tower {k}': plan2ll('aster', p) for k, p in zip('CD', CD)}, **{f'Tower {k}': plan2ll('aster', p) for k, p in zip('IJ', IJ)},
                                  **{f'Tower {k}': plan2ll('aster', p) for k, p in zip('KLM', KLM)}})
    # ---------------- Amogha (Adani master layout: wings A/B, C/D, E/F, G/H in joined pairs)
    sa = json.load(open(os.path.join(HERE, 'sat', 'plan_amogha_seg.json')))
    pick = lambda x0: next(o for o in sa if abs(o['bb'][0] - x0) < 10)['poly']
    ab = poly_split(pick(211), 2, 'y', 'y'); cd = poly_split(pick(455), 2, 'x', 'x'); ef = poly_split(pick(959), 2, 'x', 'x'); gh = poly_split(pick(1377), 2, 'y', 'y')
    G['amogha'] = dict(towers={'Wing A': plan2ll('amo', ab[0]), 'Wing B': plan2ll('amo', ab[1]), 'Wing C': plan2ll('amo', cd[0]), 'Wing D': plan2ll('amo', cd[1]),
                               'Wing E': plan2ll('amo', ef[0]), 'Wing F': plan2ll('amo', ef[1]), 'Wing H': plan2ll('amo', gh[0]), 'Wing G': plan2ll('amo', gh[1])},
                       ctx=[dict(t='prism', h=7.0, ll=plan2ll('amo', [[790, 122], [1003, 122], [1003, 265], [790, 265]]), label='Clubhouse')])
    # ---------------- Embrace (Adani master layout; A-B and D-E typical floor = two towers joined; block C plan)
    ab = outline('em_fp_abde')
    A_half, B_half = urange(ab, 0.0, 0.5), urange(ab, 0.5, 1.0)     # after turning upright: u < 0.5 lands at the bottom, u > 0.5 at the top
    rAB, rDE = (1085, 178, 1335, 680), (215, 183, 465, 688)
    # drawing turned upright: u (0..1 along the slab) runs top -> bottom of the master plan; B and D are the upper towers
    G['embrace'] = dict(towers={'Tower A': plan2ll('embrace', place(A_half, rAB, rot90=True)), 'Tower B': plan2ll('embrace', place(B_half, rAB, rot90=True)),
                                'Tower C': plan2ll('embrace', place(outline('em_fp_c'), (565, 98, 830, 250))),
                                'Tower D': plan2ll('embrace', place(B_half, rDE, rot90=True)), 'Tower E': plan2ll('embrace', place(A_half, rDE, rot90=True))})
    # ---------------- Elysium Novus (Adani master plan; floor plans of C&F / D&E pairs, G and J)
    cdef = outline('en_fp_cdef'); left, right = urange(cdef, 0, 0.5), urange(cdef, 0.5, 1)
    rEF, rCD = (963, 213, 1216, 345), (963, 548, 1216, 682)
    G['elysium-novus'] = dict(towers={'Block C': plan2ll('ely', place(left, rCD)), 'Block D': plan2ll('ely', place(right, rCD)),
                                      'Block E': plan2ll('ely', place(right, rEF)), 'Block F': plan2ll('ely', place(left, rEF)),
                                      'Block G': plan2ll('ely', place(outline('en_fp_g'), (690, 225, 895, 375))),
                                      'Block J': plan2ll('ely', place(outline('en_fp_j'), (1178, 393, 1310, 513)))})
    # ---------------- Greenfield (Adani / Shivalik ground plan; Block A nearest the 34.5 m road, B, then C at the back)
    gfo = outline('gf_fp2')
    # typical-floor drawing turned so that its top faces north-east, as its compass rose shows (N at the top-left of the sheet)
    G['greenfield'] = dict(towers={'Block A': plan2ll('gf', place(gfo, GF_RECTS['Block A'], **GF_TURN)),
                                   'Block B': plan2ll('gf', place(gfo, GF_RECTS['Block B'], **GF_TURN)),
                                   'Block C': plan2ll('gf', place(gfo, GF_RECTS['Block C'], **GF_TURN))})
    # ---------------- Ambrosia (Adani master layout; wing floor plans A, B, C)
    G['ambrosia'] = dict(towers={'Wing A': plan2ll('amb', place(outline('am_wa'), (1008, 400, 1265, 842), rot90=True)),
                                 'Wing B': plan2ll('amb', place(outline('am_wb'), (520, 200, 902, 485))),
                                 'Wing C': plan2ll('amb', place(outline('am_wc'), (178, 400, 432, 842), rot90=True))})
    # ---------------- Paarijat (Adani first-floor plan: Block B left, Block A right)
    sp = json.load(open(os.path.join(HERE, 'sat', 'spec_pj.json')))
    G['paarijat'] = dict(towers={'Block A': plan2ll('pj', sp['polys']['A']), 'Block B': plan2ll('pj', sp['polys']['B'])},
                         ctx=[dict(t='prism', h=4.0, ll=plan2ll('pj', sp['polys']['amen']), label='Society amenity')])
    # ---------------- Skyline (Adani ground floor + typical floor plans): two parking levels joined under all blocks, towers above
    pod = [[185, 148], [1250, 148], [1250, 658], [1048, 658], [1048, 430], [940, 430], [940, 658], [495, 658], [495, 430], [380, 430], [380, 658], [185, 658]]
    tw = {'Block A': R(1055, 140, 1260, 655), 'Block B': R(490, 410, 940, 660), 'Block C': R(182, 140, 385, 655)}
    # each block takes the part of the podium nearest to it (A: x > 1000, B: 420..1000 below the deck, C: x < 420)
    podA = clip(pod, -1, 0, -1000); podC = clip(pod, 1, 0, 440)
    podB = clip(clip(clip(pod, -1, 0, -440), 1, 0, 1000), 0, -1, -400)
    deck = R(440, 148, 1000, 400)
    G['shilp-skyline'] = dict(towers={k: plan2ll('sky', v) for k, v in tw.items()},
                              pods={'Block A': plan2ll('sky', podA), 'Block B': plan2ll('sky', podB), 'Block C': plan2ll('sky', podC)},
                              ctx=[dict(t='prism', h=7.2, ll=plan2ll('sky', deck), label='Podium amenity deck')])
    # ---------------- Belrosa (Adani typical floor plan: one slab of four blocks, 5 BHK blocks on the left, 4 BHK on the right)
    bo = outline('bl_typ'); rS = (330, 389, 1270, 605)
    cuts = [0, (490 - 136) / 1328, (840 - 136) / 1328, (1150 - 136) / 1328, 1]
    names = ['Block D', 'Block C', 'Block B', 'Block A']
    G['belrosa'] = dict(towers={names[i]: plan2ll('bl', place(urange(bo, cuts[i], cuts[i + 1]), rS)) for i in range(4)})
    json.dump(G, open(os.path.join(HERE, 't3dall', 'sh_geom.json'), 'w'))
    return G

if __name__ == '__main__':
    G = build()
    for k, v in G.items(): print(k, list(v['towers']))
