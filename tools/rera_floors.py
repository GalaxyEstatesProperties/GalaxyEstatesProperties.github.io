"""Floor-by-floor unit counts from the unit numbers on the Gujarat RERA register (citizen-survey block lists, 18 Oct 2026).
Unit numbers are read as <floor><two-digit unit> (e.g. 1204 = floor 12) except where a project numbers its units differently (decoders below).
Floors with no unit number are kept as levels with no units: a refuge, services or amenity floor, or a floor number the developer skipped."""
import json, os, re, collections
HERE = os.path.dirname(os.path.abspath(__file__))
UNITS = json.load(open(os.path.join(HERE, 't3dall', 'rera_units.json')))

def _num(s):
    m = re.findall(r'\d+', s.split('-')[-1])
    return int(m[-1]) if m else None

def std(n): return n // 100
def low2(n): return n % 100
def sobha(s):                     # Sobha: <home 1|2><floor, 2 digits><position>, e.g. 2371 = floor 37
    t = s.split('-')[-1].strip()
    return int(t[1:3]) if len(t) == 4 and t.isdigit() else None

def counts(L, dec=std, raw=False):
    c = collections.Counter()
    for s in L:
        if raw:
            f = dec(s)
        else:
            n = _num(s)
            f = None if n is None else dec(n)
        if f is not None: c[f] += 1
    return c

def blocks_of(key):
    v = UNITS.get(key)
    return v if isinstance(v, dict) else {}

def _parts(name):
    return [x.strip().upper().replace('TOWER', '').replace('BLOCK', '').strip() for x in re.split(r'[+&]', name)]

def match(label, blocks):
    """the RERA block that holds this tower's units (block names such as 'A', 'A+B', 'Tower B', 'EAST TOWER+WEST TOWER')"""
    lab = label.upper().replace('TOWER', '').replace('BLOCK', '').replace('WING', '').strip()
    for b in blocks:
        if lab in _parts(b) or lab == b.upper().strip(): return b
    return None

GENERIC = {   # listing id -> RERA unit-list key; floors decoded with std()
  'aster-neo': None, 'elysium-novus': 'elysium-novus', 'greenfield': 'greenfield', 'paarijat': 'paarijat', 'shilp-skyline': 'shilp-skyline',
  'shivalik-presente': 'shivalik-presente', 'navratna-gulmohar': 'navratna-gulmohar', 'trogon-twin-towers': 'trogon-twin-towers', 'shivalik-wave': 'shivalik-wave',
  'anamika-high-point': 'anamika-high-point', 'ashridhar-wynn': 'ashridhar-wynn', 'godrej-altus': 'godrej-altus', 'venus-the-universe': 'venus-the-universe',
  'venus-pashmina': 'venus-pashmina', 'nila-vida': 'nila-vida', 'shilp-twin-towers': 'shilp-twin-towers',
  'amora': 'new:29423', 'storeys-infinity': 'new:31253', 'nakshatra-regalia': 'new:17488', 'nakshatra-regalia-ii': 'new:24736', 'the-identity': 'new:24889',
  'united-siban': 'new:25408', 'nila-prana': 'new:27689', 'kaavyaratna-reva': 'new:14674', 'kaavyaratna-narmada': 'new:16677', 'kaavyaratna-the-ganga': 'new:28376',
  'shivalik-curv': 'new:19668', 'inspire-edge': 'new:22138', 'adani-center-point': 'new:20011',
}
BLOCK_HINT = {'shilp-twin-towers': {'East Block': 'A', 'West tower': None}}

def tower_counts(pid, label, blk=None):
    """-> (Counter floor -> units, how many towers share that count, block name) or None"""
    if pid == 'wtc-gift-city':
        B = dict(blocks_of('new:978')); B.update(blocks_of('new:995'))
        b = match(label, B)
        return (counts(B[b]), 1, b) if b else None
    if pid == 'inspire-business-park':
        B = blocks_of('new:8530')
        if not blk or blk not in B: return None
        return (counts(B[blk], std if blk == 'commercial tower' else low2), 1, blk)
    if pid == 'storeys-golf-coast':
        B = blocks_of('new:26302')['A+B']; side = label.split()[-1]
        return (counts([u for u in B if u.startswith(side + '-')], lambda n: n), 1, side)
    if pid in ('sobha-elysia', 'sobha-avalon'):
        key = 'sobha-elysia' if pid == 'sobha-elysia' else 'new:12616'
        L = list(blocks_of(key).values())[0]
        if pid == 'sobha-elysia':     # first digit is the tower (1 = Tower A, 2 = Tower B)
            t = '1' if label.endswith('A') else '2'
            L = [u for u in L if u.split('-')[-1].strip().startswith(t)]
            return (counts(L, sobha, raw=True), 1, 'Tower ' + label[-1])
        return (counts(L, sobha, raw=True), 1, 'Sobha Avalon')
    key = GENERIC.get(pid)
    if not key: return None
    B = blocks_of(key)
    if not B: return None
    hint = BLOCK_HINT.get(pid, {})
    b = hint[label] if label in hint else (match(label, B) or (list(B)[0] if len(B) == 1 else None))
    if not b: return None
    share = len([x for x in _parts(b) if x]) if '+' in b or '&' in b else 1
    return (counts(B[b]), share, b)

def stack_from(c, share, block, top=None, start_label='Floor', kind='residential', ground_use=None):
    word = 'units' if kind != 'residential' else 'homes'
    across = f' across blocks {block}' if share > 1 else ''
    hi = max(c) if c else 0
    if top: hi = max(hi, top)
    st = []
    g = c.get(0, 0)
    if g: st.append(dict(label='Ground floor', kind='A', note=f'{g} {"unit" if g == 1 else "units"} registered at ground level{across} (Gujarat RERA)'))
    else: st.append(dict(label='Ground floor', kind='M', use=ground_use or 'Entrance lobby and common areas (no units registered at ground level)'))
    first = min([f for f in c if f > 0] or [1])
    for f in sorted(x for x in c if x > 0):          # start of the main run of floors with units (5 in a row); gaps below it are podium / parking levels
        if all(c.get(f + i) for i in range(5)): main = f; break
    else: main = first
    for f in range(1, hi + 1):
        n = c.get(f, 0)
        if not n and (f < first or f < main):
            st.append(dict(label=f'{start_label} {f}', kind='M', use='No units are registered on this floor: podium, parking or amenity level'))
        elif n:
            st.append(dict(label=f'{start_label} {f}', kind='A', note=f'{n} {word[:-1] if n == 1 else word} registered on this floor{across} (Gujarat RERA)'))
        else:
            st.append(dict(label=f'{start_label} {f}', kind='S', use='No unit is registered with this floor number in the Gujarat RERA register: a refuge, services or amenity floor, or a number the developer skipped'))
    return st
