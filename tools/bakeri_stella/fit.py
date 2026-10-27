import json, math, sys
import numpy as np
from PIL import Image, ImageDraw
from geom import *
G = json.load(open('geo_gift.json'))
la0, lo0 = G['origin']['lat'], G['origin']['lon']
E_ = 6378137.0; D = math.pi / 180
def ll(x, y): return la0 + y / (D * E_), lo0 + x / (D * E_ * math.cos(la0 * D))
def pxl(lat, lon, z, X0, Y0):
    Sz = 256 * 2 ** z; X = (lon + 180) / 360 * Sz; Y = (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * Sz
    return X - X0, Y - Y0
K = 2.0855
PLOT = to_m(np.array([(25, 215), (1545, 215), (1985, 635), (1480, 1165), (140, 1165)]) * K)
SETB = to_m(np.array([(58, 365), (1483, 365), (1868, 735), (1615, 995), (133, 995)]) * K)
def model_to_geo(P, gx, gy, rot):
    t = rot * D; c, s = math.cos(t), math.sin(t)
    return [(x * c - y * s + gx, x * s + y * c + gy) for x, y in P]
def draw(name, gx, gy, rot, out, extra=()):
    m = json.load(open(f'sat/newimg/{name}.meta.json')); im = Image.open(f'sat/newimg/{name}.webp').convert('RGB'); d = ImageDraw.Draw(im)
    def poly(P, col, w=3):
        q = [pxl(*ll(x, y), m['z'], m['X0'], m['Y0']) for x, y in model_to_geo(P, gx, gy, rot)]
        d.line(q + [q[0]], fill=col, width=w)
    poly(PLOT, (0, 120, 255)); poly(SETB, (255, 255, 0), 2)
    for P, col in extra: poly(P, col)
    im.save(out)
if __name__ == '__main__':
    gx, gy, rot = map(float, sys.argv[1:4])
    ex = []
    for p in (20, 38):
        for q in polys(mask(p)): ex.append((list(q.exterior.coords), (255, 0, 0) if p == 20 else (255, 0, 255)))
    draw('g19w', gx, gy, rot, sys.argv[4], ex)
