"""Facade colours and treatment for every 3D explorer, read from each project's official render (19 Oct 2026).
style: punched = walls with windows · glass = curtain wall with mullions · piers = glass between solid piers.
balc: share of the long faces that carry balconies; balcD: balcony depth (m); fins: coloured fins either side of balconies."""
def F(wall, frame, glass='#33475b', style='punched', balc=0.6, **k):
    d = dict(wall=wall, frame=frame, glass=glass, style=style, balc=balc); d.update(k); return d
G = lambda glass, frame, **k: F(k.pop('wall', '#cfd5db'), frame, glass, k.pop('style', 'glass'), k.pop('balc', 0), **k)
FACADE = {
  # Adani Shantigram
  'aster-neo': F('#d8d2c8', '#efebe5', '#3a4654', accent='#d98b3a', fins=True),
  'amogha': F('#e4e0da', '#f3f0eb', accent='#b0563a', fins=True),
  'embrace': F('#d9b39c', '#f1e6db', '#3d4b58'),
  'elysium-novus': F('#a7735b', '#ebe3d8', '#2f3c49', accent='#d9cdbd', fins=True),
  'greenfield': F('#7b5d49', '#cdbca6', '#2c3946', accent='#c9a27a', fins=True),
  'ambrosia': F('#d9c5a5', '#efe6d5', '#3c5063', accent='#8a6a48', fins=True),
  'paarijat': F('#ece7df', '#f5f1eb', '#3b4c5c', accent='#a85a38', fins=True, balc=0.8),
  'shilp-skyline': F('#efebe4', '#ded6c9', '#3b4a59', accent='#8a6e52'),
  'belrosa': F('#e6dac8', '#c9a77c', '#3a4b5b', balc=0.9, balcD=2.0),
  'north-park': F('#5e6062', '#ece6dc', '#3c4f60', balc=0.4, accent='#9a6b45'),
  'west-park': F('#f2efe9', '#3d4045', '#40566a', balc=0.3),
  'amora': F('#b4573f', '#f1ece4', '#2e4256', balc=0.7),
  'storeys-golf-coast': F('#8c7e86', '#d0c6ca', '#3a4656', balc=0.9, balcD=2.2),
  'the-storeys': F('#9aa3a8', '#e9ebec', '#4b6174', style='piers', balc=0.9, balcD=2.2),
  'storeys-infinity': F('#a58b6d', '#d9ccb9', '#3a4654', balc=0.8, balcD=2.0),
  'ikaria': F('#8d9094', '#c7c9cb', '#34414e', balc=0.5),
  'adani-center-point': G('#2c4d68', '#d8d2c8', wall='#c9b79c', style='piers'),
  'inspire-corporate-capital': G('#6f94b3', '#c9a46a'),
  'inspire-business-park': G('#5b88a8', '#d7dde2'),
  'inspire-edge': G('#2c3a46', '#5a5c60', wall='#55585d', style='piers'),
  'shivalik-shantigram': F('#9a6440', '#8c5a38'),
  # GIFT City
  'shivalik-skyview': F('#ebe9e5', '#f4f3f0', '#26364a', style='piers', balc=0.6),
  'shivalik-presente': F('#f2efea', '#e9e3da', '#4b5f72', balc=1.0, balcD=2.4, accent='#b78a5c'),
  'shivalik-curv': G('#7ea0bd', '#eef1f4'),
  'sobha-elysia': F('#c98a68', '#eadac7', '#34414e', balc=0.6),
  'sobha-avalon': F('#e7e2da', '#cfc7ba', '#3b4b5b'),
  'savvy-marina': F('#d9d4cc', '#ebe7e1', '#2b3a49'),
  'bakeri-stella': F('#f0eee9', '#e2ddd3', '#55697b'),
  'shilp-north-sky': F('#d3a46f', '#f0e8dc', '#3a4655'),
  'shilp-twin-towers': G('#8ea7bd', '#e4e8ec'),
  'shilp-centrica': G('#4a4d5a', '#b9a07a'),
  'nakshatra-regalia': G('#2c3e57', '#9aa6b4'),
  'nakshatra-regalia-ii': G('#5e88a8', '#dfe4e8'),
  'the-identity': G('#3b6a99', '#c9a46a'),
  'kaavyaratna-narmada': G('#7fa4c4', '#d9c8a8', style='piers', wall='#d9c8a8'),
  'kaavyaratna-the-ganga': G('#2f5e9a', '#cfd8e2'),
  'kaavyaratna-reva': F('#e8e4dc', '#6d5a48', '#3a4a5a', balc=0.6),
  'wtc-gift-city': F('#eef0f2', '#d9dde1', '#5b84a8', balc=0),
  'sangath-accolade': F('#efece6', '#d6d0c6', '#3a4a5a'),
  'united-siban': F('#d8c3a0', '#5a4a3c', '#33414e'),
  'nila-prana': F('#b98a5e', '#e7ddcf', '#38454f'),
  'nila-vida': F('#efece6', '#d9d3c9', '#3b4b58', accent='#5f8a4f', fins=True),
  # Ahmedabad
  'navratna-gulmohar': G('#34495d', '#c9ced4'),
  'trogon-twin-towers': G('#3c4c62', '#d2d7dd'),
  'trogon-centre-court': F('#efece6', '#d4cfc6', '#3a4a5a', accent='#55595e'),
  'shivalik-wave': G('#3a4a58', '#b08a52'),
  'antonia': G('#2c3f52', '#cfd6dd'),
  'ashridhar-wynn': G('#4f7fa8', '#dfe5ea'),
  'anamika-high-point': F('#c9b49a', '#8a6b4f', '#33414f'),
  'godrej-altus': F('#46503f', '#d8d0c4', '#3c4b58', accent='#8a6040', balc=0.9),
  'gala-ikebana': F('#a5503a', '#6e4a3c', '#384451', accent='#3a3733', fins=True, rail='#5f8a4f', balc=0.9, balcD=1.8),   # terracotta tiles, dark planter balconies with hanging green (Gala render)
  'maruti-360': F('#f1eee8', '#f6f4f0', '#35424e', accent='#8f6a48', fins=True, balc=0.8),
  'venus-pashmina': F('#a87a5a', '#dcc8ac', '#34414e'),
  'venus-stratum': G('#2a3c52', '#cfd3d8'),
  'venus-the-universe': F('#cbbcab', '#e6ddd1', '#3a4855'),
  'shilp-business-gateway': G('#5a7f9f', '#c9a46a'),
  # abroad
  'binghatti-burj-jacob': G('#7da2c4', '#e7eef4'),
  'danube-bayz-101': G('#8fa9c0', '#e5ebf0'),
  'danube-diamondz': G('#a9c3d8', '#f2f4f6'),
  'danube-shahrukhz': G('#3b4e63', '#c9a46a'),
  'emaar-valo': F('#e8e4dc', '#d2ccc1', '#2b3a48', balc=0.7),
  'dcondo-vite': F('#e7dccb', '#f3ede4', '#3c4b58'),
  'newport-residences': G('#4d6177', '#c9b48f', balc=0.4),
  'trx-residences': F('#e9e9e6', '#d6d7d4', '#3e5366', balc=0.6),
}
# per-level treatment where one tower has different parts
LEVEL = {
  'navratna-gulmohar': lambda L: {'style': 'glass', 'balc': 0.7, 'balcD': 2.2} if L.get('unit') == 'home' or L['label'].startswith('Floors 37') else None,
  'storeys-golf-coast': lambda L: None,
}
def apply(pid, cfg):
    fc = FACADE.get(pid)
    if fc: cfg['facade'] = dict(fc)
    f = LEVEL.get(pid)
    if f:
        for st in [cfg.get('stack') or []] + [t.get('stack') or [] for t in cfg.get('towers', [])]:
            for L in st:
                v = f(L)
                if v: L['fac'] = v
