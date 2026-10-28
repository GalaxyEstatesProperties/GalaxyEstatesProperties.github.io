"""Rebuild assets/search-index.json and sitemap.xml straight from the published site (the HTML files in the repo root and assets/data.js).

Needs nothing but Python 3 (and Node, only to read assets/data.js). Run it from anywhere:
    python3 tools/site_search.py
It runs automatically on every push (.github/workflows/site-search.yml), so a page or project added by any route is searchable
and in the sitemap without a separate step. The browser search also reads sitemap.xml and picks up any page still missing here.
"""
import glob, html, json, os, re, subprocess, sys, datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SITE = 'https://galaxyestatesproperties.co.in/'
SKIP_INDEX = {'404.html', 'search.html', 'home.html'}           # not searchable: error page, the results page, the old redirect
SKIP_MAP = {'404.html', 'search.html', 'home.html', 'index.html'}  # index.html is listed as the bare domain

def text(h):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', h))).strip()

def projects():
    js = os.path.join(ROOT, 'assets', 'data.js')
    if not os.path.exists(js): return []
    try:
        out = subprocess.run(['node', '-e', 'global.window={};require(process.argv[1]);process.stdout.write(JSON.stringify(window.SITE_PROJECTS||[]))', js],
                             capture_output=True, text=True, timeout=60, check=True).stdout
        return json.loads(out)
    except Exception as e:
        print('could not read assets/data.js:', e, file=sys.stderr)
        return []

def entries():
    P = {p['page']: p for p in projects() if p.get('page')}
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, '*.html'))):
        n = os.path.basename(f)
        if n in SKIP_INDEX: continue
        h = open(f, encoding='utf-8').read()
        if re.search(r'<meta[^>]+name="robots"[^>]+noindex', h): continue
        tm = re.search(r'<title>(.*?)</title>', h, re.S)
        title = text(tm.group(1)).split(' | ')[0].split(' – ')[0].strip() if tm else n
        desc = (re.search(r'<meta name="description" content="([^"]*)"', h) or [None, ''])[1]
        main = re.search(r'<main[^>]*>(.*)</main>', h, re.S); body = main.group(1) if main else h
        body = re.sub(r'<(script|style|svg|noscript|form)\b.*?</\1>', ' ', body, flags=re.S)
        h1m = re.search(r'<h1[^>]*>(.*?)</h1>', body, re.S); h1 = text(h1m.group(1)) if h1m else ''
        p = P.get(n)
        kind = 'Property' if p else ('Guide' if n.endswith('-property.html') or n == 'global.html' else 'Page')
        e = dict(t=(p['name'] if p else (h1 or title)), u=n, k=kind, d=html.unescape(desc)[:180])
        if p:
            e['s'] = ' · '.join(x for x in [p.get('label'), p.get('location'), p.get('price') if p.get('price') and p.get('price') != 'On request' else None] if x)
            kw = [p.get('developer'), p.get('location'), p.get('city'), p.get('country'), p.get('market'), p.get('label'), p.get('size'), p.get('rera'), p.get('possession')] + list(p.get('cats') or [])
            e['w'] = ' '.join(str(x) for x in kw if x)
        heads = [text(m.group(2)) for m in re.finditer(r'<h([23])[^>]*>(.*?)</h\1>', body, re.S)]
        e['h'] = ' | '.join(x for x in heads if x)[:600]
        e['x'] = text(body)[:900]
        out.append(e)
        if not p:          # sections of guide pages, so "golf course" or "visa" lands on the right part of the page
            for m in re.finditer(r'<section[^>]*\bid="([a-z0-9-]+)"[^>]*>(.*?)</section>', body, re.S):
                hh = re.search(r'<h2[^>]*>(.*?)</h2>', m.group(2), re.S)
                if not hh: continue
                t = text(hh.group(1))
                if len(t) < 4: continue
                out.append(dict(t=t, u=n + '#' + m.group(1), k='Section', s=(h1 or title), d='', h='', x=text(m.group(2))[:500]))
    return out

def sitemap():
    path = os.path.join(ROOT, 'sitemap.xml')
    old = open(path, encoding='utf-8').read() if os.path.exists(path) else ''
    have = dict(re.findall(r'<loc>([^<]+)</loc><lastmod>([^<]+)</lastmod>', old))
    pri = dict(re.findall(r'<loc>([^<]+)</loc><lastmod>[^<]+</lastmod><priority>([^<]+)</priority>', old))
    today = datetime.date.today().isoformat()
    rows = []
    home = SITE
    rows.append((home, have.get(home, today), pri.get(home, '1.0')))
    for f in sorted(glob.glob(os.path.join(ROOT, '*.html'))):
        n = os.path.basename(f)
        if n in SKIP_MAP: continue
        h = open(f, encoding='utf-8').read()
        if re.search(r'<meta[^>]+name="robots"[^>]+noindex', h): continue
        u = SITE + n
        rows.append((u, have.get(u, today), pri.get(u, '0.8')))
    body = '\n'.join(f'  <url><loc>{u}</loc><lastmod>{d}</lastmod><priority>{p}</priority></url>' for u, d, p in rows)
    new = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + '\n</urlset>\n'
    if new != old: open(path, 'w', encoding='utf-8').write(new)
    return len(rows), new != old

if __name__ == '__main__':
    E = entries()
    path = os.path.join(ROOT, 'assets', 'search-index.json')
    new = json.dumps(E, ensure_ascii=False, separators=(',', ':'))
    old = open(path, encoding='utf-8').read() if os.path.exists(path) else ''
    if new != old: open(path, 'w', encoding='utf-8').write(new)
    n, ch = sitemap()
    print(f'search index: {len(E)} entries ({"updated" if new != old else "unchanged"}); sitemap: {n} URLs ({"updated" if ch else "unchanged"})')
