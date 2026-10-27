import json, re, math, glob
from shapely.geometry import Polygon, box
from shapely import affinity
def cfg(slug):
    f = [g for g in glob.glob('/home/claude/gep/*.html') if re.search(r'id="t3d-%s"' % re.escape(slug), open(g).read())][0]
    s = open(f).read()
    return json.loads(re.search(r'<script type="application/json" id="t3d-%s">(.*?)</script>' % re.escape(slug), s, re.S).group(1)), f
def footprints(c):
    out = []
    fh = c.get('floorH', 3.2)
    for t in c['towers']:
        st = t.get('stack') or c['stack']
        H = sum(e.get('h') or e.get('levels', 1) * fh for e in st)
        H = max(H, t.get('height') or 0)
        if t.get('pts'): P = Polygon(t['pts'])
        else: P = box(-t['w'] / 2, -t['d'] / 2, t['w'] / 2, t['d'] / 2)
        if t.get('ang'): P = affinity.rotate(P, t['ang'], origin=(0, 0))
        P = affinity.translate(P, t.get('x', 0), t.get('y', 0))
        out.append((P, H, t.get('label', t['id'])))
    return out
def to_geo(P, g):
    P = affinity.rotate(P, g.get('rot', 0), origin=(0, 0))
    return affinity.translate(P, g['x'], g['y'])
if __name__ == '__main__':
    for slug in ['shilp-north-sky', 'savvy-marina', 'shivalik-skyview', 'sangath-accolade', 'nila-prana', 'shivalik-presente', 'shilp-twin-towers', 'shilp-centrica', 'shivalik-curv']:
        c, f = cfg(slug)
        fp = footprints(c)
        print(slug, f.split('/')[-1], c.get('project'), [(round(P.area), round(H, 1), l) for P, H, l in fp][:8], 'plot', c.get('plot'))
