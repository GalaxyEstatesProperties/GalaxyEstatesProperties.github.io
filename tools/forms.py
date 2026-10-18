"""Real building forms for the 3D explorers (18 Oct 2026).
Plot: the outline registered on the Gujarat RERA map service (position, orientation and shape) where it matches the registered land area.
Towers: counts and floors from Gujarat RERA (unit numbers per floor, blocks) and the developers; shapes, setbacks, crowns and podiums
read from each project's official renders. Positions are metres in the plot frame: x along the plot's long side, y across it,
origin at the plot centre. Anything estimated from a render is said so in the page note."""
import math, json, os
TRX = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "t3dall", "trx_geom.json")))

def T(label, x, y, w, d, above=None, **k):
    t = dict(label=label, x=x, y=y, w=w, d=d); t.update(k)
    if above is not None: t['above'] = above
    return t

def pod(x, y, w, d, h, r=6, ang=0):            # podium / low context block (not interactive)
    return dict(t='pod', x=x, y=y, w=w, d=d, h=h, r=r, ang=ang)

def bridge(x, y, w, d, z, h=6):                 # sky bridge between towers
    return dict(t='slab', x=x, y=y, w=w, d=d, h=h, z=z, r=1)

def chevron(wing, depth, spread):              # V-shaped plan (two wings meeting at a point)
    a = math.radians(spread); c, s = math.cos(a), math.sin(a)
    L, D = wing, depth
    return [[0, -D / 2], [L * c, L * s - D / 2], [L * c - D * s, L * s + D * c - D / 2], [0, D * 1.1 - D / 2],
            [-(L * c - D * s), L * s + D * c - D / 2], [-L * c, L * s - D / 2]]

FORMS = {
  # ---------------------------------------------------------------- Adani Shantigram
  'aster-neo': dict(site='aster-neo', towers=[T('Tower A', -30, -20, 26, 20), T('Tower B', 30, -20, 26, 20), T('Tower G', -30, 20, 26, 20), T('Tower H', 30, 20, 26, 20)],
                    osm_split=[['Tower A', 'Tower B'], ['Tower G', 'Tower H']],
                    osm_note='the towers are registered as two joined blocks, A + B and G + H; each mapped slab is drawn as its two towers, and which slab is A + B is approximate'),
  'embrace': dict(site='embrace', towers=[T('Tower A', -45, 18, 18, 24), T('Tower B', 0, 18, 18, 24), T('Tower C', 45, 18, 18, 24), T('Tower D', -24, -20, 18, 24), T('Tower E', 24, -20, 18, 24)]),
  'elysium-novus': dict(site='elysium-novus', above=14, towers=[T(f'Block {b}', x, y, 16, 22) for b, x, y in (('C', -32, 22), ('D', 0, 22), ('E', 32, 22), ('F', -32, -22), ('G', 0, -22), ('J', 32, -22))],
                        floors_note='Gujarat RERA unit numbers run to floor 14 in every block (44.8 m).'),
  'greenfield': dict(site='greenfield', top=21, towers=[T('Tower A', -42, -12, 26, 20), T('Tower B', 0, 0, 26, 20), T('Tower C', 42, 12, 26, 20)], note='Towers staggered along the plot as on the developer render.'),
  'ambrosia': dict(site='ambrosia', towers=[T('Wing A', -38, 0, 24, 22), T('Wing B', 0, 0, 24, 22), T('Wing C', 38, 0, 24, 22)]),
  'shilp-skyline': dict(site='shilp-skyline', above=23, towers=[T('Block A', -36, 0, 24, 22), T('Block B', 0, 0, 24, 22), T('Block C', 36, 0, 24, 22)],
                        floors_note='Gujarat RERA unit numbers run to floor 23 (79 m).'),
  'belrosa': dict(site='belrosa', towers=[T('Belrosa', 0, 0, 40, 28, crown=dict(type='frame', h=8))], note='Crown frame as on the Adani Realty render.'),
  'inspire-business-park': dict(site='new:8530', kind='commercial', floorH=3.8, osm=['Crown 2', 'Crown 1', 'Crown 3'], osm_note='the three office towers are matched to the three largest outlines by floor count; which corporate house stands on which outline is approximate', towers=[
        T('Crown 2', -62, 48, 40, 24, 12, blk='commercial tower'), T('Crown 1', -16, 48, 36, 22, 10, blk='BTS1'), T('Crown 3', 30, 48, 34, 22, 8, blk='BTS2'),
        T('Crest CH 1', -70, -8, 18, 22, 4, blk='CH1'), T('Crest CH 2', -44, -8, 18, 22, 4, blk='CH2'), T('Crest CH 3', -18, -8, 18, 22, 4, blk='CH3'), T('Crest CH 4 & 5', 12, -8, 30, 22, 4, blk='CH4&5'),
        T('Crest CH 6', -62, -50, 20, 24, 5, blk='CH6'), T('Crest CH 7', -32, -50, 20, 24, 5, blk='CH7'), T('Crest CH 8', -2, -50, 20, 24, 5, blk='CH8'), T('Crest CH 9', 28, -50, 20, 24, 5, blk='CH9')],
        note='Buildings and floors from Adani Realty (Crown 1 G+10, Crown 2 G+12, Crown 3 G+8, corporate houses G+4 and G+5); their arrangement follows the photo of the park.'),
  'inspire-corporate-capital': dict(site='new:19626', kind='commercial', towers=[T('Block A', -30, 0, 44, 30, 9), T('Block B', 34, 0, 40, 30, 9)],
        note='Two blocks as on the Adani Realty render; their floor count is not published, so the model shows ground + 9 floors read from the render.'),
  'inspire-edge': dict(site='new:22138', kind='commercial', towers=[T('Inspire Edge', 0, 0, 30, 24, 10)], floors_note='Gujarat RERA unit list: ground-floor shops, offices on floors 1 to 4, one work floor per level on floors 5 to 10.'),
  'adani-center-point': dict(site='new:20011', kind='commercial', floorH=5.0, osm=[], towers=[T('Center Point', 0, 0, 78, 40, 3)], floors_note='Shops on the ground, first and second floors and multiplex screens on floors 2–3 (Gujarat RERA unit list).'),
  'amora': dict(site='new:29423', towers=[T('Tower A', -18, 14, 26, 18, 13), T('Tower B', 18, 14, 26, 18, 13)], context=[pod(0, -8, 70, 46, 11)],
        floors_note='Gujarat RERA unit numbers: homes to floor 13 in both towers; shops on the ground, first and second floors (shown as the low retail block).'),
  'storeys-golf-coast': dict(site='new:26302', towers=[T('Tower A', -34, 0, 22, 22, 18), T('Tower B', 34, 0, 22, 22, 19)], context=[pod(0, 0, 96, 50, 4)],
        floors_note='One home per floor: Gujarat RERA unit numbers run from floor 2 to floor 18 in tower A and to floor 19 in tower B.'),
  'storeys-infinity': dict(site='new:31253', towers=[T('West Tower', -26, -10, 40, 24, 20, crown=dict(type='frame', h=7), pts=[[-20, -12], [6, -12], [6, -6], [20, -6], [20, 12], [-20, 12]]),
                                                    T('East Tower', 28, 12, 40, 24, 20, crown=dict(type='frame', h=7), pts=[[-20, -12], [6, -12], [6, -6], [20, -6], [20, 12], [-20, 12]])],
        floors_note='Gujarat RERA unit numbers run to floor 20 in both towers; each tower is two stepped wings with a crown frame, as on the Adani Realty render.'),
  'ikaria': dict(site='new:17462', towers=[T('Ikaria', 0, 0, 62, 18, 13)], floors_note='Ground + 13 floors (Adani Realty floor plans).'),
  # ---------------------------------------------------------------- GIFT City
  'sobha-elysia': dict(site='sobha-elysia', towers=[
        T('Tower A', -40, 0, 30, 24, tiers=[dict(from_=0, w=56, dx=12), dict(from_=3, w=30, dx=0)]),
        T('Tower B', 40, 0, 30, 24, tiers=[dict(from_=0, w=56, dx=-12), dict(from_=3, w=30, dx=0)])],
        note='Two towers on a shared podium as on the Sobha render: homes on floors 3 to 38 (8 per floor in each tower, from the RERA unit numbers), podium and amenity levels below.'),
  'shivalik-presente': dict(site='shivalik-presente', towers=[T('Tower A', -34, 0, 28, 24), T('Tower B', 0, 0, 28, 24), T('Tower C', 34, 0, 28, 24)]),
  'shivalik-skyview': dict(site='shivalik-skyview', towers=[T('Shivalik Skyview', 0, -6, 60, 40, pts=chevron(30, 15, 25))], note='V-shaped plan as on the Shivalik render.'),
  'savvy-marina': dict(site='savvy-marina', towers=[T('T1', -38, 0, 30, 24), T('T2', 0, 0, 30, 24), T('T3', 38, 0, 30, 24)]),
  'shilp-twin-towers': dict(site='shilp-twin-towers', no_size=True, towers=[
        T('West tower', -30, 8, 40, 32, tiers=[dict(from_=8, dx=-4, dy=3), dict(from_=15, dx=4, dy=-2), dict(from_=22, dx=-3, dy=-4)]),
        T('East Block', 30, -8, 40, 32, tiers=[dict(from_=8, dx=4, dy=-3), dict(from_=15, dx=-4, dy=2), dict(from_=22, dx=3, dy=4)])],
        note='Stacked, shifted office volumes as on the INI Design Studio renders.'),
  'shivalik-curv': dict(site='new:19668', kind='commercial', floorH=3.75, height=120, towers=[T('Shivalik Curv', 0, 0, 50, 36, 31, shape='round', twist=1.2, lean=[25, 0])],
        note='Oval plan that turns about 1° per floor and leans 25 m over its height, from the INI Design Studio renders and The Realty Today (32 storeys, 120 m).'),
  'shilp-centrica': dict(site='new:19680', site_pos_only=True, kind='commercial', towers=[T('Shilp Centrica', 0, 0, 50, 36, 30, r=6, shape='round', tiers=[dict(from_=26, w=44, d=30)])], context=[pod(0, 0, 70, 52, 9)],
        note='G+30 from the GIFT City Project listing; the outline drawn on the RERA map is larger than the registered land, so only its centre is used.'),
  'nakshatra-regalia': dict(site='new:17488', kind='commercial', towers=[T('Regalia', 0, 0, 42, 30, 29)], floors_note='Gujarat RERA unit numbers run to floor 29.'),
  'nakshatra-regalia-ii': dict(site='new:24736', kind='commercial', towers=[T('Block A', -26, 6, 34, 26, 28), T('Block B', 26, 6, 34, 26, 28)], context=[pod(0, -4, 100, 50, 14, r=24)],
        floors_note='Gujarat RERA unit numbers run to floor 28; the towers stand on a curved retail podium as on the Regalia render.'),
  'the-identity': dict(site='new:24889', kind='commercial', floorH=4.0, towers=[T('The Identity', 0, 0, 66, 28, 29, pts=[[-33, -14], [-3, -14], [-3, -8], [3, -8], [3, -14], [33, -14], [33, 14], [3, 14], [3, 8], [-3, 8], [-3, 14], [-33, 14]])],
        context=[pod(0, -30, 80, 18, 10)],
        floors_note='Twin glass towers joined by a recessed core, offices to floor 29 (Gujarat RERA unit numbers). The register lists the building at 183 m including its parking podium; the model shows the office floors at 4 m each.'),
  'kaavyaratna-narmada': dict(site='new:16677', kind='commercial', towers=[T('Narmada', 0, 0, 42, 22, 28, shape='round', r=11)], floors_note='29 storeys (Kaavyaratna), offices to floor 27 in the RERA unit list.'),
  'kaavyaratna-the-ganga': dict(site='new:28376', kind='commercial', towers=[T('The Ganga', 0, 0, 42, 28, 27, crown=dict(type='arch', h=21))], context=[pod(0, 0, 64, 44, 8)],
        floors_note='G+27 with an arched glass crown, as on the Kaavyaratna render.'),
  'wtc-gift-city': dict(site='new:978', kind='commercial', osm=['Tower B', 'Tower C'], osm_note='heights mapped there match towers B (27 floors), C (18) and the two 6-floor towers; which of the two low curved buildings is A and which is D is approximate', towers=[T('Tower A', -110, 0, 40, 30, 6), T('Tower B', -40, 0, 42, 32, 27), T('Tower D', 30, 0, 40, 30, 6), T('Tower C', 105, 0, 40, 30, 18)],
        note='Towers A, B and D (one registration) and Tower C (a second registration); floors from the RERA unit numbers.'),
  'sangath-accolade': dict(site='new:19015', towers=[T('Tower A', -28, 0, 26, 20, 33), T('Tower B', 28, 0, 26, 20, 33)], context=[bridge(0, 0, 32, 7, 33 * 3.2 - 8)],
        floors_note='3 basements + ground + 33 floors (Housiey); the sky bridge between the towers is drawn from the developer render.'),
  'kaavyaratna-reva': dict(site='new:14674', towers=[T('Reva', 0, 0, 70, 22, 34, pts=[[-35, -4], [-17, -10], [0, -12], [17, -10], [35, -4], [35, 12], [17, 6], [0, 4], [-17, 6], [-35, 12]])],
        floors_note='G+34 (Gujarat RERA); the two wings form a curved front, as on the Kaavyaratna render.'),
  'united-siban': dict(site='new:25408', towers=[T(f'Tower {c}', x, y, 26, 22, 34) for c, x, y in (('A', -62, -10), ('B', -31, 6), ('C', 0, 12), ('D', 31, 6), ('E', 62, -10))],
        floors_note='5 towers, 4 basements + ground + 34 floors (Housiey; RERA unit numbers run to floor 34). Arrangement from the developer render.'),
  'nila-prana': dict(site='new:27689', towers=[T('Tower A', -12, 8, 44, 20, 28), T('Tower B', 16, -14, 20, 40, 28)], floors_note='2 towers, 3 basements + ground + 28 floors (Housiey; RERA unit numbers run to floor 28).'),
  'sobha-avalon': dict(site='new:12616', towers=[T('Sobha Avalon', 0, 6, 40, 26, 34)], context=[pod(0, -6, 64, 46, 10)],
        floors_note='2 basements + ground + 3 podium levels + 31 floors (Housiey).'),
  # ---------------------------------------------------------------- Ahmedabad
  # ---------------------------------------------------------------- abroad
  'trx-residences': dict(towers=[T('Tower A', -30, 0, 36, 30, levels=53), T('Tower B', 30, 0, 36, 30, levels=57)],
        ll_towers={'Tower A': TRX['TRX Residences - Tower A']['ll'], 'Tower B': TRX['TRX Residences - Tower B']['ll']},
        pos_note='Position and tower outlines: as mapped on OpenStreetMap (TRX Residences towers A and B, beside the TRX mall and park).', camTurn=3.1416),
  'emaar-valo': dict(pos_note='Position: the map pin on Propsearch’s Valo page in Dubai Creek Harbour (The Lagoons). The tower’s footprint is not published, so its outline is approximate.'),
  'maruti-360': dict(towers=[T('Tower A', -22, 0, 30, 22, crown=dict(type='dome', h=9)), T('Tower B', 22, 0, 30, 22, crown=dict(type='dome', h=9))], note='Round crowns on both towers, as on the Maruti 360 render.'),
  'gala-ikebana': dict(site='gala-ikebana', towers=[T('Block A', -36, 0, 22, 44), T('Block B', 0, 12, 50, 20), T('Block C', 36, 0, 22, 44)], note='U-shaped arrangement of blocks A, B and C, as on the Gala render.'),
  'navratna-gulmohar': dict(site='navratna-gulmohar', osm=[], osm_note='the office block; the residential tower above it is drawn at its centre', towers=[T('Gulmohar Park', 0, 0, 28, 24, tiers=[dict(from_=0, w=64, d=44, dx=12), dict(from_=16, w=28, d=24, dx=0)])],
        note='Slender residential tower above a wide office block, as on the INI Design Studio render: the RERA unit numbers put offices on floors 3 to 15 (10 per floor) and homes on floors 18 to 37 (2 per floor).'),
  'trogon-twin-towers': dict(site='trogon-twin-towers', kind='commercial', height=125, towers=[T('Tower A', -24, 6, 30, 26, 32, crown=dict(type='slope', h=14)), T('Tower B', 24, 6, 30, 26, 32, crown=dict(type='slope', h=14, dir=-1))],
        context=[pod(0, -10, 110, 46, 12, r=20)],
        note='Twin towers with sloping tops on a curved showroom podium, as on the Trogon render; 125 m and offices to floor 32 (Gujarat RERA unit numbers).'),
  'shivalik-wave': dict(site='shivalik-wave', towers=[T('Shivalik Wave', 0, 6, 50, 32, shape='round')], context=[pod(0, -6, 72, 50, 12, r=14)], note='Rounded glass tower on a podium, as on the Shivalik render.'),
  'antonia': dict(towers=[T('Antonia', 0, 0, 34, 24, crown=dict(type='slope', h=16))], note='Slender tower with a sloping crown, as on the Antonia render.'),
  'ashridhar-wynn': dict(site='ashridhar-wynn', towers=[T('Wynn', 0, 8, 44, 30, tiers=[dict(from_=30, w=34, d=24)])], context=[pod(0, -6, 80, 56, 12)], note='Glass tower with a stepped top on a podium, as on the A. Shridhar render.'),
  'godrej-altus': dict(site='godrej-altus', above=11, towers=[T('T1', -36, 22, 40, 24), T('T2', 36, 22, 40, 24), T('T3', -36, -22, 40, 24), T('T4', 36, -22, 40, 24)],
        floors_note='Gujarat RERA unit numbers run to floor 11 in towers T1 to T4.'),
  'venus-the-universe': dict(site='venus-the-universe', towers=[T(f'Tower {chr(65 + i)}', -88 + (i % 5) * 44, 40 if i < 5 else -30, 32, 24) for i in range(10)], context=[pod(0, -78, 200, 22, 8)]),
  'venus-stratum': dict(site='venus-stratum', osm=[]),
  'anamika-high-point': dict(site='anamika-high-point'),
  'trogon-centre-court': dict(),
  'shivalik-shantigram': dict(),
}

# tower and floor data for listings that had no 3D explorer before
NEW_S = {
  'inspire-business-park': dict(src='Adani Realty official project page and the Gujarat RERA register'),
  'inspire-corporate-capital': dict(src='Adani Realty official project page and the Gujarat RERA register (blocks A and B)'),
  'inspire-edge': dict(src='Adani Realty and the Gujarat RERA register'),
  'adani-center-point': dict(src='Adani Realty and the Gujarat RERA register'),
  'amora': dict(src='Adani Realty and the Gujarat RERA register (90 homes, 38 shops)'),
  'storeys-golf-coast': dict(src='Adani Realty (North and South towers, one home per floor) and the Gujarat RERA register (35 homes)'),
  'storeys-infinity': dict(src='Adani Realty and the Gujarat RERA register (154 homes in the East and West towers)'),
  'ikaria': dict(src='Adani Realty and the Gujarat RERA register (140 homes)'),
  'shivalik-curv': dict(src='Gujarat RERA register (453 units); INI Design Studio and The Realty Today (32 storeys, 120 m)'),
  'shilp-centrica': dict(src='Gujarat RERA register (492 units); GIFT City Project listing (G+30)'),
  'nakshatra-regalia': dict(src='Gujarat RERA register (190 units)'),
  'nakshatra-regalia-ii': dict(src='Gujarat RERA register (508 units in blocks A and B)'),
  'the-identity': dict(src='Gujarat RERA register (1,030 units)'),
  'kaavyaratna-narmada': dict(src='Kaavyaratna (29 storeys) and the Gujarat RERA register (304 units)'),
  'kaavyaratna-the-ganga': dict(src='Gujarat RERA register (offices, shops and a hotel); G+27 from the GIFT City Project listing'),
  'wtc-gift-city': dict(src='Gujarat RERA register (towers A, B, D: 1,188 units; tower C: 312 units)'),
  'sangath-accolade': dict(src='Gujarat RERA register (towers A and B, 242 units) and Housiey (3B + G + 33)'),
  'kaavyaratna-reva': dict(src='Gujarat RERA register (G+34, 486 units)'),
  'united-siban': dict(src='Gujarat RERA register (1,668 units in towers A–E) and Housiey (4B + G + 34)'),
  'nila-prana': dict(src='Gujarat RERA register (703 units in towers A and B) and Housiey (3B + G + 28)'),
  'sobha-avalon': dict(src='Gujarat RERA register (268 homes) and Housiey (2B + G + 3P + 31)'),
  'trogon-twin-towers': dict(src='Trogon (125 m) and the Gujarat RERA register (928 units in towers A and B, offices to floor 32)', kind='commercial'),
}
