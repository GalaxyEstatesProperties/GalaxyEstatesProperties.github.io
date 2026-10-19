"""Segment unit regions (beige fill) on the floor-plan pages and draw an overlay with component ids."""
import sys, json
import numpy as np, cv2

BEIGE = np.array([210, 202, 191])

def unit_mask(im, tol=14):
    d = np.abs(im.astype(int) - BEIGE).max(axis=2)
    return (d <= tol).astype(np.uint8)

def components(path, min_area=4000, tol=14, crop=None):
    im = cv2.imread(path)[:, :, ::-1]
    if crop:
        x0, y0, x1, y1 = crop
        m = np.zeros(im.shape[:2], np.uint8); m[y0:y1, x0:x1] = 1
    else:
        m = 1
    mask = unit_mask(im, tol) * m
    # close small gaps from text and grid dots inside units, but keep walls (walls are >= 3 px dark lines)
    k = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k)
    n, lab, stats, cent = cv2.connectedComponentsWithStats(mask, connectivity=4)
    out = []
    for i in range(1, n):
        x, y, w, h, a = stats[i]
        if a < min_area: continue
        comp = (lab == i).astype(np.uint8)
        comp = cv2.morphologyEx(comp, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
        cs, _ = cv2.findContours(comp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        c = max(cs, key=cv2.contourArea)
        out.append(dict(id=len(out), bbox=[int(x), int(y), int(w), int(h)], area=int(a), cx=float(cent[i][0]), cy=float(cent[i][1]),
                        contour=c[:, 0, :].tolist()))
    return im, out

def overlay(im, comps, path):
    o = im.copy()
    rng = np.random.default_rng(1)
    for c in comps:
        col = tuple(int(v) for v in rng.integers(60, 230, 3))
        cv2.drawContours(o, [np.array(c['contour']).reshape(-1, 1, 2)], -1, col, 3)
        cv2.putText(o, str(c['id']), (int(c['cx']) - 20, int(c['cy']) + 12), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (220, 0, 0), 4)
    cv2.imwrite(path, o[:, :, ::-1])

if __name__ == '__main__':
    src, dst, js = sys.argv[1], sys.argv[2], sys.argv[3]
    crop = json.loads(sys.argv[4]) if len(sys.argv) > 4 else None
    im, comps = components(src, crop=crop)
    overlay(im, comps, dst)
    json.dump(comps, open(js, 'w'))
    for c in comps: print(c['id'], c['bbox'], c['area'])
