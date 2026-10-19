"""Elysium Novus: flats, lift cores and the open void, cut from Adani Realty's typical floor plans (block C-D-E-F, G, J).
Every flat is the part of the building reached first from its own label position (geodesic partition inside the plan outline),
so its shape follows the walls of the drawing; cores and the central void are taken out first."""
import json, numpy as np, cv2
from PIL import Image
from collections import deque
def mask(n, bbox):
    a = np.array(Image.open(f'newimg/{n}.webp').convert('RGB')).astype(int)
    m = (a.min(2) < 235).astype(np.uint8)
    x0, y0, x1, y1 = map(int, bbox); k = np.zeros_like(m); k[y0:y1 + 1, x0:x1 + 1] = 1; m *= k
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE); c = max(cs, key=cv2.contourArea)
    f = np.zeros_like(m); cv2.fillPoly(f, [c], 1); return f
def poly_of(m):
    cs, _ = cv2.findContours(m.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE); c = max(cs, key=cv2.contourArea)
    return cv2.approxPolyDP(c, 4.0, True)[:, 0, :].tolist()
def partition(m, seeds):
    H, W = m.shape; lab = np.full((H, W), -1, int); q = deque()
    for i, (x, y) in enumerate(seeds): lab[y, x] = i; q.append((x, y))
    while q:
        x, y = q.popleft(); l = lab[y, x]
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            u, v = x + dx, y + dy
            if 0 <= u < W and 0 <= v < H and m[v, u] and lab[v, u] < 0: lab[v, u] = l; q.append((u, v))
    return lab
def fill(shape, P): z = np.zeros(shape, np.uint8); cv2.fillPoly(z, [np.array(P, np.int32)], 1); return z
OUT = {}
SPEC = {
  'en_fp_cdef': dict(bbox=[225, 129, 1529, 829],
     cores={'CF': [(480, 345), (590, 345), (590, 410), (645, 410), (645, 545), (590, 545), (590, 605), (480, 605), (480, 530), (355, 530), (355, 415), (480, 415)]},
     holes=[[(750, 352), (998, 352), (998, 602), (750, 602)]],
     seeds={'L101': (330, 290), 'L102': (650, 270), 'L104': (330, 665), 'L103': (650, 690), 'R103': (1100, 270), 'R104': (1420, 290), 'R102': (1100, 690), 'R101': (1420, 665)}),
  'en_fp_g': dict(bbox=[160, 60, 1539, 999],
     cores={'G': [(780, 340), (915, 340), (915, 560), (1030, 600), (1030, 705), (650, 705), (650, 600), (780, 560)]}, holes=[],
     seeds={'106': (560, 260), '105': (380, 580), '104': (680, 860), '103': (1020, 860), '102': (1320, 580), '101': (1140, 260)}),
  'en_fp_j': dict(bbox=[470, 70, 1449, 944],
     cores={'J': [(800, 240), (1135, 240), (1135, 670), (800, 670)]}, holes=[],
     seeds={'104': (640, 300), '101': (1290, 300), '103': (640, 700), '102': (1290, 700)}),
}
for n, S in SPEC.items():
    m = mask(n, S['bbox']); shape = m.shape
    cores = {}
    for k, P in S['cores'].items():
        Ps = [P]
        if n == 'en_fp_cdef': Ps.append([(1749 - x, y) for x, y in P])          # D&E core: mirror of C&F (plan symmetric about x = 874.5)
        for j, P2 in enumerate(Ps):
            c = fill(shape, P2) * m; cores[k + str(j)] = poly_of(c); m = m * (1 - fill(shape, P2))
    for P in S['holes']: m = m * (1 - fill(shape, P))
    names = list(S['seeds']); lab = partition(m, [S['seeds'][k] for k in names])
    cells = {k: poly_of((lab == i).astype(np.uint8)) for i, k in enumerate(names)}
    x0, y0, x1, y1 = S['bbox']; nz = lambda P: [[round((x - x0) / (x1 - x0), 4), round((y - y0) / (y1 - y0), 4)] for x, y in P]
    OUT[n] = dict(cells={k: nz(v) for k, v in cells.items()}, cores={k: nz(v) for k, v in cores.items()})
    dbg = np.array(Image.open(f'newimg/{n}.webp').convert('RGB'))
    rng = np.random.RandomState(1)
    for i, k in enumerate(names):
        col = rng.randint(60, 255, 3).tolist(); cv2.polylines(dbg, [np.array(cells[k], np.int32)], True, col, 5); cx, cy = np.mean(cells[k], 0); cv2.putText(dbg, k, (int(cx) - 30, int(cy)), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 0, 0), 4)
    for k, P in cores.items(): cv2.polylines(dbg, [np.array(P, np.int32)], True, (0, 0, 255), 5)
    Image.fromarray(dbg).resize((800, 565)).save(f'gm/{n}_cells.png')
    print(n, {k: len(v) for k, v in cells.items()}, list(cores))
json.dump(OUT, open('sat/en_cells.json', 'w'))
