"""Flats cut from developers' typical floor plans (19 Oct 2026): each flat is the part of the building reached first from its own
label position (geodesic partition inside the plan outline), after the lift / stair core and open voids are taken out.
Output sat/plan_cells.json: per plan, cells (flat number -> polygon) and cores, in the plan image's pixels."""
import json, numpy as np, cv2
from PIL import Image
from en_cells import partition, poly_of, fill
def mask_poly(shape, P): return fill(shape, P)
def mask_img(n, bbox):
    a = np.array(Image.open(f'newimg/{n}.webp').convert('RGB')).astype(int)
    m = (a.min(2) < 235).astype(np.uint8)
    x0, y0, x1, y1 = map(int, bbox); k = np.zeros_like(m); k[y0:y1 + 1, x0:x1 + 1] = 1; m *= k
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE); c = max(cs, key=cv2.contourArea)
    f = np.zeros_like(m); cv2.fillPoly(f, [c], 1); return f
R = lambda x0, y0, x1, y1: [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
SPEC = {}
def run(key, img, region, seeds, cores=(), holes=()):
    im = Image.open(f'newimg/{img}.webp'); shape = (im.height, im.width)
    m = mask_img(img, region['bbox']) if 'bbox' in region else mask_poly(shape, region['poly'])
    out_cores = []
    for P in cores: c = fill(shape, P) * m; out_cores.append(poly_of(c)); m = m * (1 - fill(shape, P))
    for P in holes: m = m * (1 - fill(shape, P))
    names = list(seeds); lab = partition(m, [seeds[k] for k in names])
    cells = {k: poly_of((lab == i).astype(np.uint8)) for i, k in enumerate(names)}
    return dict(img=img, cells=cells, cores=out_cores, core_rects=[list(map(list, P)) for P in cores])
def debug(name, res):
    dbg = np.array(Image.open(f'newimg/{res["img"]}.webp').convert('RGB'))
    for k, P in res['cells'].items():
        cv2.polylines(dbg, [np.array(P, np.int32)], True, (255, 0, 0), 4); cx, cy = np.mean(P, 0)
        cv2.putText(dbg, k, (int(cx) - 30, int(cy)), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (220, 0, 0), 4)
    for P in res['cores']: cv2.polylines(dbg, [np.array(P, np.int32)], True, (0, 0, 255), 4)
    im = Image.fromarray(dbg); im.thumbnail((1100, 900)); im.save(f'gm/{name}_cells.png')
if __name__ == '__main__':
    OUT = {}
    # Greenfield typical floor (Adani Realty / Shivalik): 202 top-left, 201 bottom-left, 203 top-right, 204 bottom-right (door labels)
    OUT['gf'] = run('gf', 'gf_fp2', dict(bbox=[95, 250, 1504, 979]),
                    {'02': (384, 416), '01': (384, 816), '03': (1216, 416), '04': (1216, 816)},
                    cores=[R(680, 256, 920, 976), R(576, 576, 680, 648), R(920, 576, 1024, 648)],
                    holes=[R(104, 560, 344, 664), R(1256, 560, 1496, 664)])
    # Paarijat typical floor: Block B (left) 101 TL, 102 TR, 104 BL, 103 BR; Block A (right) 103 TL, 104 TR, 102 BL, 101 BR
    OUT['pjB'] = run('pjB', 'pj_fp1', dict(bbox=[26, 150, 504, 790]),
                     {'01': (110, 250), '02': (420, 250), '04': (110, 700), '03': (420, 700)},
                     cores=[R(210, 345, 312, 590)], holes=[R(312, 437, 480, 502), R(40, 384, 136, 552)])
    OUT['pjA'] = run('pjA', 'pj_fp1', dict(bbox=[1105, 150, 1583, 790]),
                     {'03': (1190, 250), '04': (1500, 250), '02': (1190, 700), '01': (1500, 700)},
                     cores=[R(1290, 345, 1387, 590)], holes=[R(1462, 385, 1550, 555), R(1120, 437, 1290, 502)])
    # Skyline typical floor (2nd to 21st), Shilp: block A 203 TL, 204 TR, 202 BL, 201 BR; blocks B and C 201 TL, 202 TR, 204 BL, 203 BR (labels "201-2101" etc.)
    OUT['skyA'] = run('skyA', 'sk_typ', dict(bbox=[1055, 140, 1260, 655]), {'03': (1105, 307), '04': (1208, 307), '02': (1105, 480), '01': (1208, 480)},
                      cores=[R(1058, 370, 1258, 415), R(1105, 350, 1202, 437), R(1132, 288, 1180, 350), R(1132, 437, 1180, 497)])
    OUT['skyC'] = run('skyC', 'sk_typ', dict(bbox=[180, 140, 385, 655]), {'01': (230, 307), '02': (333, 307), '04': (230, 480), '03': (333, 480)},
                      cores=[R(183, 370, 383, 415), R(237, 350, 330, 437), R(257, 288, 305, 350), R(257, 437, 305, 497)])
    OUT['skyB'] = run('skyB', 'sk_typ', dict(bbox=[490, 405, 940, 660]), {'01': (594, 460), '02': (823, 460), '04': (594, 610), '03': (823, 610)},
                      cores=[R(615, 514, 840, 558), R(638, 489, 798, 583), R(696, 470, 740, 489), R(696, 583, 740, 602)])
    # Amogha master layout (Adani Realty; m_amogha = the layout at 1600 px): flat numbers per wing as printed; the open court between each pair is left out
    seg = json.load(open('sat/plan_amogha_seg.json')); pick = lambda x0: next(o for o in seg if abs(o['bb'][0] - x0) < 10)['poly']
    def amo(off, k, pts): return {n: (round((off[0] + x / k) * 1600 / 1920), round((off[1] + y / k) * 1600 / 1920)) for n, (x, y) in pts.items()}
    def amoR(off, k, x0, y0, x1, y1): (a, b), (c, d) = amo(off, k, {'p': (x0, y0)})['p'], amo(off, k, {'q': (x1, y1)})['q']; return R(a, b, c, d)
    o, k = (240, 168), 2.2388
    OUT['amoAB'] = run('amoAB', 'm_amogha', dict(poly=pick(211)), amo(o, k, {'A04': (105, 105), 'A01': (360, 105), 'A03': (105, 330), 'A02': (360, 330), 'B03': (105, 570), 'B02': (360, 570), 'B04': (105, 810), 'B01': (360, 810)}),
                       cores=[amoR(o, k, 185, 100, 270, 345), amoR(o, k, 185, 555, 270, 800)], holes=[amoR(o, k, 150, 345, 300, 555)])
    o, k = (540, 384), 2.2388
    OUT['amoCD'] = run('amoCD', 'm_amogha', dict(poly=pick(455)), amo(o, k, {'C01': (85, 85), 'C02': (340, 85), 'C04': (85, 350), 'C03': (340, 350), 'D02': (565, 85), 'D01': (815, 85), 'D03': (565, 350), 'D04': (815, 350)}),
                       cores=[amoR(o, k, 95, 165, 345, 290), amoR(o, k, 555, 165, 800, 290)], holes=[amoR(o, k, 345, 140, 555, 295)])
    o, k = (1146, 384), 2.2727
    OUT['amoEF'] = run('amoEF', 'm_amogha', dict(poly=pick(959)), amo(o, k, {'E01': (75, 85), 'E02': (335, 85), 'E04': (75, 350), 'E03': (335, 350), 'F02': (560, 85), 'F01': (815, 85), 'F03': (560, 350), 'F04': (815, 350)}),
                       cores=[amoR(o, k, 90, 170, 345, 290), amoR(o, k, 555, 170, 800, 290)], holes=[amoR(o, k, 345, 140, 555, 295)])
    o, k = (1644, 168), 2.2388
    OUT['amoGH'] = run('amoGH', 'm_amogha', dict(poly=pick(1377)), amo(o, k, {'H01': (90, 105), 'H04': (345, 105), 'H02': (90, 330), 'H03': (345, 330), 'G02': (90, 570), 'G03': (345, 570), 'G01': (90, 810), 'G04': (345, 810)}),
                       cores=[amoR(o, k, 175, 100, 260, 345), amoR(o, k, 175, 555, 260, 800)], holes=[amoR(o, k, 145, 345, 290, 555)])
    # Embrace (Adani Realty): towers A-B / D-E typical floor (two towers round an open void; numbers 1-4 at the flat doors), tower C floors 1-11 (flat 2 left, 1 right)
    OUT['emAB'] = run('emAB', 'em_fp_abde', dict(bbox=[102, 185, 1485, 886]),
                      {'L01': (262, 320), 'L02': (582, 320), 'L04': (262, 684), 'L03': (582, 684), 'R03': (1004, 320), 'R04': (1309, 320), 'R02': (1004, 684), 'R01': (1309, 684)},
                      cores=[R(218, 480, 611, 589), R(989, 480, 1367, 589)], holes=[R(611, 480, 989, 589)])
    OUT['emC'] = run('emC', 'em_fp_c', dict(bbox=[150, 125, 1401, 914]), {'C02': (436, 611), 'C01': (1164, 611)}, cores=[R(541, 134, 1142, 349)])
    # Ambrosia (Adani Realty complex layout, m_ambrosia = layout at 1600 px): numbers 1-4 per wing as printed; wing outlines from the wing floor plans placed as in shgeom
    import shgeom as SG
    amb = lambda n, rect: [list(map(round, q)) for q in SG.place(SG.outline(n), rect, rot90=(n != 'am_wb'))]
    OUT['ambA'] = run('ambA', 'm_ambrosia', dict(poly=amb('am_wa', (1008, 400, 1265, 842))), {'A02': (1050, 515), 'A03': (1215, 515), 'A01': (1050, 732), 'A04': (1215, 732)},
                      cores=[R(1102, 521, 1154, 712), R(1076, 587, 1181, 652)])
    OUT['ambB'] = run('ambB', 'm_ambrosia', dict(poly=amb('am_wb', (520, 200, 902, 485))), {'B03': (605, 272), 'B04': (800, 272), 'B02': (605, 430), 'B01': (800, 430)},
                      cores=[R(612, 321, 810, 370), R(675, 294, 742, 397)])
    OUT['ambC'] = run('ambC', 'm_ambrosia', dict(poly=amb('am_wc', (178, 400, 432, 842))), {'C02': (220, 515), 'C03': (385, 515), 'C01': (220, 732), 'C04': (385, 732)},
                      cores=[R(272, 521, 324, 712), R(246, 587, 351, 652)])
    # Gala Ikebana typical floor (odd), Gala Group: lobby entries 01 (north wing), 02 (bar), 03 (south wing) at cores A and C; B 01 west of core B
    ikP = json.load(open('sat/ike_outline_px.json'))
    OUT['ike'] = run('ike', 'ike_typ', dict(poly=ikP), {'A01': (790, 90), 'A02': (700, 235), 'A03': (790, 395), 'B01': (522, 235), 'C01': (290, 90), 'C02': (380, 235), 'C03': (290, 395)},
                     cores=[R(225, 177, 302, 303), R(589, 177, 625, 303), R(778, 177, 858, 303)])
    for k, v in OUT.items(): debug(k, v); print(k, {c: len(p) for c, p in v['cells'].items()}, [len(c) for c in v['cores']])
    json.dump(OUT, open('sat/plan_cells.json', 'w'))
