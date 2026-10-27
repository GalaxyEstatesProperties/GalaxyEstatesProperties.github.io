"""Bakeri Stella: floor-plate outlines traced from the developer's brochure (52-page CAD brochure, pages 16-50 = GF to terrace).
All plan pages share one page frame. Scale from the stair treads (300 mm) and checked against the shop sizes: 7.22 pt per metre."""
import json, math
import numpy as np, cv2
from PIL import Image
from shapely.geometry import Polygon, MultiPolygon, LineString
from shapely.ops import split, unary_union

DPI = 300
S = 7.22 * DPI / 72                      # px per metre at 300 dpi (30.08)
CROP = (100, 700, 3990, 2130)            # x0, y0, x1, y1 (300 dpi px) inside the setback box and the building
U0, V0 = 2000.0, 1250.0                  # page px origin of the model frame (re-centred later)

def page(p):
    return np.asarray(Image.open(f'br/p{p}-{p}.png').convert('RGB')).astype(int)

def to_m(P):
    P = np.asarray(P, float)
    return np.stack([(P[:, 0] - U0) / S, -(P[:, 1] - V0) / S], axis=1)

def to_px(P):
    P = np.asarray(P, float)
    return np.stack([P[:, 0] * S + U0, -P[:, 1] * S + V0], axis=1)

def mask(p, close=31, opn=9):
    im = page(p)
    mx = im.max(2); mn = im.min(2)
    m = (~((mx - mn <= 10) & (mn >= 225))).astype(np.uint8)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    m[(b > 200) & (r < 140) & (g < 210)] = 0            # blue plot lines
    k = np.zeros_like(m); x0, y0, x1, y1 = CROP; k[y0:y1, x0:x1] = 1; m &= k
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((close, close), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((opn, opn), np.uint8))
    return m

def polys(m, min_area_m2=60, eps=4.0):
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    out = []
    for c in cs:
        if cv2.contourArea(c) < min_area_m2 * S * S: continue
        a = cv2.approxPolyDP(c, eps, True)[:, 0, :]
        P = Polygon(to_m(a)).buffer(0)
        if isinstance(P, MultiPolygon): P = max(P.geoms, key=lambda g: g.area)
        out.append(P)
    return out
