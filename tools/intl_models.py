"""Dubai towers drawn to their published form (27 Oct 2026): Burj Binghatti Jacob & Co Residences, Valo (Emaar) and Shahrukhz by Danube.
Floor counts and heights are the published ones; the plan shapes, setbacks and crowns are read from the developers' renders, because
floor plates are not published. Each config from t3d_auto is reshaped here (tiers = footprint by floor, crown = what stands on the roof)."""
import math

def stadium(w, d):                  # rounded-end plan (as on the renders)
    return dict(w=w, d=d, shape='round', r=min(w, d) / 2, pts=None)

def octagon(w, d, c):
    x, y = w / 2, d / 2
    return [[-x + c, -y], [x - c, -y], [x, -y + c], [x, y - c], [x - c, y], [-x + c, y], [-x, y - c], [-x, -y + c]]

def burj_jacob(cfg):
    t = cfg['towers'][0]
    t.update(w=42, d=42, pts=octagon(42, 42, 6), crown=dict(type='jewel', n=40, low=0.25, pow=3, flare=0.1))
    t['height'] = 557
    cfg['camY'] = 250
    cfg['note'] = ('Model built from published figures: 104 floors and 557 m to the top of the crown (Binghatti, via Wikipedia). The crown is drawn as on the developer’s renders: '
                   'a ring of slender rods rising from the roof edge, hung with diamond-cut crystals and tallest at two opposite corners, taking the tower from its roof '
                   '(about 416 m at 4 m floor to floor) to 557 m. The roof height and the floor plate are not published, so the square plan with cut corners is approximate. '
                   'Position: the project’s Google Maps pin in Business Bay (checked 17 Oct 2026). Surroundings (roads, water, parks, existing buildings) are from OpenStreetMap.')
    return cfg

def valo(cfg):
    t = cfg['towers'][0]
    st = cfg['stack']
    # slab tower with glazed corners and balconies; the lobby storey is taller with a bronze canopy; an open silver frame stands above the roof
    t.update(w=34, d=22, pts=None, shape='rect', crown=dict(type='frame', h=7, c='#e8eaec'))
    cfg['note'] = ('Model built from published figures: a 37-storey residential building with about 291 homes (Propsearch; Dubai Land Department project #3033: 122 one-bedroom, '
                   '129 two-bedroom and 40 three-bedroom homes). Form as on Emaar’s renders: a glass slab tower with silver mullions, balconies on the long faces and corners, '
                   'and an open frame above the roof. The floor plate is not published, so the 34 × 22 m plan is approximate. '
                   'Position: the map pin on Propsearch’s Valo page in Dubai Creek Harbour. Surroundings (roads, water, parks, existing buildings) are from OpenStreetMap.')
    return cfg

def shahrukhz(cfg):
    t = cfg['towers'][0]
    st = cfg['stack']
    n = len(st)                          # 55 office storeys (Danube)
    # footprint by floor, read from Danube's renders: a wide podium, a lower shaft that narrows towards a waist, a wide sky-pool deck,
    # the slim open lounge storey above it, the upper shaft, and a glass crown that sweeps up from the helipad deck
    tiers = [dict({'from': 0}, **stadium(60, 44))]
    for k in range(6, 31):               # lower shaft: 50 m at the podium, narrowing to 44 m at the waist
        u = (k - 6) / 24
        tiers.append(dict({'from': k}, **stadium(round(50 - 6 * u, 1), round(33 - 3 * u, 1))))
    tiers.append(dict({'from': 31}, **stadium(56, 40)))     # sky-pool deck
    tiers.append(dict({'from': 32}, **stadium(34, 22)))     # open lounge storey (Lounge 33)
    tiers.append(dict({'from': 33}, **stadium(40, 26)))
    for k in range(34, n):               # upper shaft, widening slightly towards the top
        u = (k - 34) / max(1, n - 35)
        tiers.append(dict({'from': k}, **stadium(round(44 + 4 * u, 1), round(30 + 2 * u, 1))))
    t.update(w=60, d=44, shape='round', r=22, pts=None, tiers=tiers, crown=dict(type='wave', h=16))
    cfg['camY'] = 105
    # the sky pool on the deck round the lounge storey
    z = sum(L.get('h') or L.get('levels', 1) * cfg['floorH'] for L in st[:32]) + 0.4
    pool = [[round(18 * math.cos(a), 1), round(-13 + 5.5 * math.sin(a), 1)] for a in (math.pi + math.pi * i / 24 for i in range(25))] + [[16, -12.2], [-16, -12.2]]
    cfg.setdefault('context', []).append(dict(t='flat', p=pool, c='#36a8d8', z=round(z, 2)))
    cfg['note'] = ('Model built from published figures: a 55-storey office tower with 615 offices, a sky pool, Lounge 33, Lounge 55 and a helipad (Danube Properties). '
                   'Form as on Danube’s renders: a wide podium with a garden roof, a rounded shaft that narrows to a waist, the sky-pool deck with the slim lounge storey above it, '
                   'the upper shaft, and a glass crown that sweeps up from the helipad deck, with gold bands at every floor. Floor heights and floor plates are not published: '
                   '4 m floor to floor is assumed and the plan sizes are read from the renders, so they are approximate. '
                   'Position: the project’s Google Maps pin on Sheikh Zayed Road (checked 17 Oct 2026). Surroundings (roads, water, parks, existing buildings) are from OpenStreetMap.')
    return cfg

BUILD = {'binghatti-burj-jacob': burj_jacob, 'emaar-valo': valo, 'danube-shahrukhz': shahrukhz}
PIDS = tuple(BUILD)
def build(pid, p, cfg): return BUILD[pid](cfg)
