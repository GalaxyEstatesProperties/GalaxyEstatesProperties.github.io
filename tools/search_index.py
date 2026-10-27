"""assets/search-index.json: every page of the site (and its main sections) for the site search, built from the generated HTML."""
import re, json, glob, os, html
WORK = os.environ.get('GALAXY_WORKDIR', os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))  # folder holding the site folders
SRC = os.path.join(WORK, 'galaxy-estates-properties')
SKIP = {'404.html', 'search.html'}
def text(h): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', h))).strip()
def run(projects):
    P = {p['page']: p for p in projects if p.get('page')}
    out = []
    for f in sorted(glob.glob(SRC + '/*.html')):
        n = os.path.basename(f)
        if n in SKIP: continue
        h = open(f, encoding='utf-8').read()
        title = text(re.search(r'<title>(.*?)</title>', h, re.S).group(1)).split(' | ')[0].split(' – ')[0].strip()
        desc = (re.search(r'<meta name="description" content="([^"]*)"', h) or [None, ''])[1]
        main = re.search(r'<main[^>]*>(.*)</main>', h, re.S); body = main.group(1) if main else h
        body = re.sub(r'<(script|style|svg|noscript|form)\b.*?</\1>', ' ', body, flags=re.S)
        h1 = text((re.search(r'<h1[^>]*>(.*?)</h1>', body, re.S) or [None, ''])[1]) if re.search(r'<h1', body) else ''
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
        if not p:     # sections of the guide pages, so "golf course" or "visa" lands on the right part of the page
            for m in re.finditer(r'<section[^>]*\bid="([a-z0-9-]+)"[^>]*>(.*?)</section>', body, re.S):
                hh = re.search(r'<h2[^>]*>(.*?)</h2>', m.group(2), re.S)
                if not hh: continue
                t = text(hh.group(1))
                if len(t) < 4: continue
                out.append(dict(t=t, u=n + '#' + m.group(1), k='Section', s=(h1 or title), d='', h='', x=text(m.group(2))[:500]))
    json.dump(out, open(SRC + '/assets/search-index.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    return len(out)
