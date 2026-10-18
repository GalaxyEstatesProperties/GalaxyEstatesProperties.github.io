"""Official registration records, read from the government registers on 17 Oct 2026:
Gujarat RERA public register (gujrera.gujarat.gov.in) and Dubai Land Department Project Status Enquiry (dubailand.gov.ae).
Only public project data is kept (no personal details of promoters, engineers or agents)."""
import json, os, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, 't3dall', 'rera.json')))
DLD = json.load(open(os.path.join(HERE, 't3dall', 'dld.json')))
CHECKED = '17 Oct 2026'
GUJ_URL = 'https://gujrera.gujarat.gov.in/'
DLD_URL = 'https://dubailand.gov.ae/en/eservices/real-estate-project-status-landing/real-estate-project-status/'

# records found by name after the registration number on the developer's material did not match
EXTRA = {
  'nila-vida': dict(regNo='PR/GJ/GANDHINAGAR/GANDHINAGAR/GIFT Urban Development Authority/RN209AA10109/011022', name='VIDA', ptype='Residential/Group Housing', promoter='Nila Spaces Limited',
                    inv=[('A+B', 496)], dev=[('Residential', 496)], start='27-09-2022', end='30-10-2028', ext='', land=5128, auth='GIFT Urban Development Authority'),
  'shilp-business-gateway': dict(regNo='PR/GJ/AHMEDABAD/AHMEDABAD CITY/Ahmedabad Municipal Corporation/CN63AA09963/A1C/030123', name='SHILP BUSINESS GATEWAY', ptype='Commercial', promoter='Shilp Organizers',
                    inv=[('1', 175)], dev=[('Shop', 61), ('Office', 114)], start='01-04-2022', end='31-03-2026', ext='', land=5281, auth='Ahmedabad Municipal Corporation'),
  'shilp-twin-towers': dict(regNo='PR/GJ/GANDHINAGAR/GANDHINAGAR/GIFT Urban Development Authority/CAA15149/280425/311231', name='SHILP TWIN TOWERS EAST BLOCK', ptype='Commercial', promoter='Artesania Infraprojects LLP',
                    inv=[('A (East Block)', 295)], dev=[('Office', 275), ('Shop', 4), ('Other', 16)], start='25-12-2024', end='30-04-2032', ext='', land=5008, auth='GIFT Urban Development Authority',
                    note='Only the East Block is registered so far. The number Shilp published earlier (MAA08006) belongs to another project, Shilp Ananta.'),
}
NOT_FOUND = {
  'shivalik-shantigram': 'Not yet registered on Gujarat RERA (searched 17 Oct 2026). We confirm the registration before any booking',
  'savvy-oryx': 'Not found on Gujarat RERA (searched 17 Oct 2026). We confirm the registration before any booking',
  'antonia': 'Not yet registered on Gujarat RERA (searched 17 Oct 2026). We will share prices once it is registered',
  'arvind-uplands-3': 'Not found on Gujarat RERA under this name (searched 17 Oct 2026); the earlier reference MAA06869 belongs to Uplands Two. We confirm the registration before any booking',
}
WRONG_PICK = {'nila-vida', 'shilp-business-gateway', 'shilp-twin-towers', 'arvind-uplands-3'}
KEEP_POSSESSION = {'aster-neo', 'venus-stratum', 'suryam-the-banyan', 'north-park', 'shilp-business-gateway', 'inspire-business-park', 'adani-center-point', 'ikaria', 'wtc-gift-city'}
KEEP_TOTAL = {'wtc-gift-city', 'amora', 'storeys-golf-coast'}

def dstr(s):
    if not s: return ''
    s = s.strip().split(' ')[0]
    for f in ('%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y'):
        try: return datetime.datetime.strptime(s, f).strftime('%-d %b %Y')
        except ValueError: pass
    return s

def plural(t, n):
    t = t.strip().lower()
    t = {'flat': 'flats', 'shop': 'shops', 'office': 'offices', 'residential': 'homes', 'bungalow': 'bungalows', 'showroom': 'showrooms', 'commercial': 'commercial units', 'apartments': 'apartments',
         'residential flats': 'flats', 'residential luxurios housing unit': 'homes', 'other': 'other units', 'shops': 'shops',
         'mixed development': 'homes and shops', 'residential flats and shops': 'flats and shops'}.get(t, t)
    return f'{n:,} {t}'

import datetime as _dt
def dstr(s):
    if not s: return ''
    s = s.strip().split(' ')[0]
    for f in ('%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y'):
        try: return _dt.datetime.strptime(s, f).strftime('%-d %b %Y')
        except ValueError: pass
    return s

# projects added 18 Oct 2026, read from the register's public API (no personal data kept)
import new_listings as NL
RN = json.load(open(os.path.join(HERE, 't3dall', 'rera_new.json')))
POLY = json.load(open(os.path.join(HERE, 't3dall', 'rera_poly.json')))
for _pid, _eid in NL.RERA_ID.items():
    _r = RN.get(str(_eid))
    if not _r: continue
    EXTRA[_pid] = dict(regNo=_r['reg'], name=_r['name'], ptype=_r['type'], promoter=(_r.get('promoter') or '').title().replace('Llp', 'LLP'),
                       inv=[(b, n) for b, n in _r['inv']], dev=[(d['t'].strip().title(), d['n']) for d in _r['dev']], start=_r['start'], end=_r['end'],
                       ext=(_r.get('ext') or '').split(' ')[0] if _r.get('ext') and dstr(_r['ext']) != dstr(_r['end']) else '',
                       land=_r.get('land') or None, auth=_r.get('auth'), booked=[(d['t'].strip().title(), d['n'], d['booked']) for d in _r['dev'] if d.get('booked') is not None],
                       note=None)
    if _pid == 'wtc-gift-city':
        _c = RN.get('995')
        EXTRA[_pid]['note'] = (f"Tower C is registered separately: {_c['reg']}, {_c['inv'][0][1]} offices, completion {_c['end']}." if _c else None)
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
def progress(pid):
    """Latest construction progress from the RERA quarterly reports (ignores quarters dated after this check)."""
    key = ('new:' + str(NL.RERA_ID[pid])) if pid in NL.RERA_ID else pid
    v = POLY.get(key) or {}
    best = None
    for q, pct in v.get('prog') or []:
        try: m, y = q.split(); n = int(y) * 12 + MONTHS.index(m)
        except Exception: continue
        if n <= 2026 * 12 + 9 and (best is None or n >= best[0]): best = (n, q, pct)
    return best

def guj(pid):
    if pid in EXTRA:
        e = EXTRA[pid]
        return dict(regNo=e['regNo'], name=e['name'], ptype=e['ptype'], promoter=e['promoter'], inv=e['inv'], dev=e['dev'], start=e['start'], end=e['end'], ext=e['ext'], land=e['land'], auth=e['auth'], note=e.get('note'), booked=e.get('booked'))
    v = R.get(pid)
    if not v or not v.get('pick') or pid in WRONG_PICK: return None
    p = v['pick']; q = p.get('qpr') or {}; pd = p.get('pd') or {}
    seen, dev = set(), []
    for d in q.get('dev') or []:
        key = (d['t'].strip().lower(), d['n'], d.get('carpet'))
        if key in seen: continue
        seen.add(key); dev.append((d['t'], d['n']))
    inv_total = sum(int(i['cnt']) for i in q.get('inv') or [])
    if inv_total and sum(n for _, n in dev) > inv_total:      # the register keeps superseded rows after an alteration: keep the set that matches the block total
        acc, keep = 0, []
        for t, n in dev:
            keep.append((t, n)); acc += n
            if acc == inv_total: break
        if acc == inv_total: dev = keep
    return dict(regNo=p['regNo'], name=p['name'].strip(), ptype=p['ptype'], promoter=q.get('promoter'), inv=[(i['block_name'], int(i['cnt'])) for i in q.get('inv') or []],
                dev=dev, start=q.get('start'), end=q.get('end'), ext=q.get('ext'), land=pd.get('land'), auth=pd.get('auth'), note=None)

def apply(ALL):
    for p in ALL:
        pid = p['id']
        if pid in NOT_FOUND:
            p['rera'] = NOT_FOUND[pid]
        g = guj(pid) if p['country'] == 'India' else None
        if g:
            order = lambda t: 0 if any(w in t.lower() for w in ('flat', 'resid', 'apart', 'bung', 'mixed')) else 1
            units = ', '.join(plural(t, n) for t, n in sorted(g['dev'], key=lambda x: order(x[0])))
            end = dstr(g['ext']) if g.get('ext') else dstr(g['end'])
            rows = [('Registration number', g['regNo']), ('Registered as', f"{g['name']} · {g['ptype']}"), ('Promoter', g['promoter'] or 'As registered'),
                    ('Registered units', units), ('Blocks', ' · '.join(f'{b}: {n}' for b, n in g['inv'])),
                    ('Land under registration', f"{g['land']:,.0f} sq m ({g['land'] / 4046.86:.2f} acres)" if g.get('land') else 'As registered'),
                    ('Plans approved by', g['auth'] or 'As registered'),
                    ('Registered dates', f"Start {dstr(g['start'])} · completion {dstr(g['end'])}" + (f" (extended to {dstr(g['ext'])})" if g.get('ext') else ''))]
            pr = progress(pid)
            if pr: rows.append(('Construction progress', f"{pr[2]:g}% (architect's certificate in the RERA quarterly report, {pr[1]})"))
            bk = [b for b in (g.get('booked') or []) if b[2] is not None]
            if bk: rows.append(('Booked so far', ', '.join(f"{b[2]:,} of {b[1]:,} {plural(b[0], 0).split(' ', 1)[1]}" for b in bk) + ' (RERA filing)'))
            p['official'] = dict(title='Gujarat RERA registration', rows=rows, note=g.get('note'), src=f'Gujarat RERA public register, checked {CHECKED}', url=GUJ_URL,
                                 how='Search the registration number on the Gujarat RERA portal to see the approved plans and quarterly progress reports.')
            p['rera'] = g['regNo']
            if pid not in KEEP_POSSESSION and not p['possession'].startswith('Ready'):
                p['possession'] = f'{end} (RERA completion date)'
            if pid not in KEEP_TOTAL: p['total'] = units + ' (Gujarat RERA)'
        d = DLD.get(pid)
        if d and p['country'] != 'India':
            rows = [('DLD project number', f"#{d['no']} · {d['name']}"), ('Developer (as registered)', d['dev']), ('Construction progress', f"{d['pct']} complete · {d['status']} (DLD, {CHECKED})")]
            if d.get('units'):
                rows.append(('Registered units', f"{d['units']:,} in all: {d['res']:,} homes" + (f", {d['com']:,} commercial" if d.get('com') else '') if d['res'] else f"{d['units']:,} commercial units"))
                rows.append(('Home types', d['mix']))
                rows.append(('Registered dates', f"Registered {d['reg']} · started {d['start']}" + (f" · completion {d['end']}" if d.get('end') else ' · completion date not shown')))
            p['official'] = dict(title='Dubai Land Department registration', rows=rows, note=None, src=f'Dubai Land Department, Project Status Enquiry, checked {CHECKED}', url=DLD_URL,
                                 how='Search the project number on the DLD Project Status Enquiry to see the latest progress and escrow details.')
            p['rera'] = f"DLD project #{d['no']}" + (f" ({d['name']})" if d['name'].lower()[:6] not in p['name'].lower() else '') + f", {d['pct']} complete ({CHECKED})"
            p['regLabel'] = 'Dubai Land Department'
            if d.get('units') and pid != 'binghatti-mercedes-city':
                p['total'] = f"{d['units']:,} (DLD)"
                if d.get('end') and pid in ('emaar-fior-1', 'danube-shahrukhz'): p['possession'] = f"{d['end'].split(' ', 1)[1]} (DLD completion date)"

def block(p, E):
    o = p.get('official')
    if not o: return ''
    rows = ''.join(f'<tr><th scope="row">{E(k)}</th><td>{E(v)}</td></tr>' for k, v in o['rows'])
    note = f'<p class="detail-source">{E(o["note"])}</p>' if o.get('note') else ''
    return (f'<h2 class="detail-h reveal">Official record: {E(o["title"])}</h2>'
            f'<div class="mix-wrap reveal"><table class="mix-table official-table"><tbody>{rows}</tbody></table></div>{note}'
            f'<p class="detail-source reveal">Source: <a href="{E(o["url"])}" target="_blank" rel="noopener noreferrer">{E(o["src"])}</a>. {E(o["how"])}</p>')
