#!/usr/bin/env python3
"""Make the deployable copy of the site in /home/claude/site-dist:
   - copies the built site
   - trims Font Awesome to the icons actually used (CSS rules + font glyphs)
   - minifies CSS and JS with esbuild
   - stamps asset URLs with a version so browsers fetch fresh files after each update
"""
import os, re, shutil, subprocess, glob, hashlib, sys
SRC = '/home/claude/vr-realtors'
OUT = '/home/claude/galaxyestatesproperties.github.io'
SKIP = {'preview.bat', 'preview.sh', 'serve.ps1', 'serve.py'}   # local-preview helpers, not needed online

if os.path.isdir(OUT):
    keep_git = os.path.join(OUT, '.git')
    for n in os.listdir(OUT):
        if n == '.git' or n == 'CNAME': continue
        p = os.path.join(OUT, n)
        shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
else:
    os.makedirs(OUT)
for n in os.listdir(SRC):
    if n in SKIP: continue
    s, d = os.path.join(SRC, n), os.path.join(OUT, n)
    shutil.copytree(s, d) if os.path.isdir(s) else shutil.copy2(s, d)

# ---------- Font Awesome: keep only used icons ----------
text = ''
for f in glob.glob(OUT + '/*.html') + glob.glob(OUT + '/assets/*.js'):
    text += open(f, encoding='utf-8').read()
used = set(re.findall(r'\bfa-([a-z0-9-]+)', text))
cssp = OUT + '/assets/vendor/fa/all.min.css'
css = open(cssp, encoding='utf-8').read()
codes = set()
def keep(m):
    names = [s[4:] for s in m.group(1).split(',') if s]
    if any(n in used for n in names):
        codes.add(m.group(2)); return m.group(0)
    return ''
css2 = re.sub(r'((?:\.fa-[a-z0-9-]+,?)+)\{--fa:"([^"]*)"\}', keep, css)
open(cssp, 'w', encoding='utf-8').write(css2)
unis = []
for c in codes:
    for part in re.findall(r'\\([0-9a-fA-F]+)', c):
        unis.append('U+' + part)
    for ch in re.sub(r'\\[0-9a-fA-F]+', '', c):
        unis.append('U+%04X' % ord(ch))
unis = sorted(set(unis))
for font in glob.glob(OUT + '/assets/vendor/webfonts/*.woff2'):
    tmp = font + '.sub'
    subprocess.run(['pyftsubset', font, '--unicodes=' + ','.join(unis), '--flavor=woff2',
                    '--layout-features=*', '--output-file=' + tmp], check=True, capture_output=True)
    os.replace(tmp, font)
print(f'icons kept: {len(codes)} (css {len(css)//1024}KB -> {len(css2)//1024}KB)')

# ---------- self-host pictures that were linked from another website (faster, and they cannot disappear) ----------
import urllib.request, io
from PIL import Image as _Im
EXT_HOST = 'https://township.homedeliveryrealtors.com'
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ext_cache'); os.makedirs(CACHE, exist_ok=True)
os.makedirs(OUT + '/assets/img/ext', exist_ok=True)
files = glob.glob(OUT + '/*.html') + glob.glob(OUT + '/assets/*.js') + glob.glob(OUT + '/assets/*.css')
urls = set()
for f in files: urls |= set(re.findall(re.escape(EXT_HOST) + r'/wp-content/[^"\'\s)<>]+', open(f, encoding='utf-8').read()))
local = {}
for u in sorted(urls):
    slug = re.sub(r'[^a-z0-9]+', '-', os.path.splitext(u.split('/uploads/')[-1])[0].lower()).strip('-')
    raw = os.path.join(CACHE, slug)
    if not os.path.exists(raw):
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        open(raw, 'wb').write(urllib.request.urlopen(req, timeout=60).read())
    im = _Im.open(raw); im = im.convert('RGBA') if im.mode in ('P', 'LA', 'RGBA') else im.convert('RGB')
    if im.width > 1600: im = im.resize((1600, round(im.height * 1600 / im.width)), _Im.LANCZOS)
    im.save(OUT + f'/assets/img/ext/{slug}.webp', 'WEBP', quality=80, method=6)
    j = im.convert('RGB'); j.thumbnail((1200, 1200)); j.save(OUT + f'/assets/img/ext/{slug}.jpg', 'JPEG', quality=82, optimize=True, progressive=True)
    local[u] = slug
def _swap(t):
    t = re.sub(r'(<meta (?:property|name)="(?:og:image|twitter:image)" content=")' + re.escape(EXT_HOST) + r'/wp-content/[^"]+', lambda m: m.group(1) + 'https://galaxyestatesproperties.co.in/assets/img/ext/' + local[m.group(0)[len(m.group(1)):]] + '.jpg', t)
    t = re.sub(r'("image"\s*:\s*")' + re.escape(EXT_HOST) + r'/wp-content/[^"]+', lambda m: m.group(1) + 'https://galaxyestatesproperties.co.in/assets/img/ext/' + local[m.group(0)[len(m.group(1)):]] + '.jpg', t)
    for u, slug in local.items(): t = t.replace(u, 'assets/img/ext/' + slug + '.webp')
    t = t.replace(' ' + EXT_HOST + ' ', ' ')          # no longer needed in the content-security policy
    return t.replace('<link rel="preconnect" href="' + EXT_HOST + '"/>\n', '').replace('<link rel="preconnect" href="' + EXT_HOST + '"/>', '')
for f in files:
    t = open(f, encoding='utf-8').read(); t2 = _swap(t)
    if f.endswith('.css'): t2 = t2.replace('assets/img/ext/', 'img/ext/')     # stylesheet paths are relative to assets/
    if t2 != t: open(f, 'w', encoding='utf-8').write(t2)
print('self-hosted pictures:', len(local))

# ---------- minify our own CSS / JS ----------
own = [f for f in glob.glob(OUT + '/assets/*.js') + glob.glob(OUT + '/assets/*.css')]
for f in own:
    before = os.path.getsize(f)
    r = subprocess.run(['npx', '--yes', 'esbuild@0.28.2', f, '--minify', ('--target=safari13,ios13,chrome80,firefox78,edge88' if f.endswith('.css') else '--target=es2019'), '--legal-comments=inline', '--log-level=error', '--outfile=' + f, '--allow-overwrite'],
                       capture_output=True, text=True)
    if r.returncode: sys.exit('minify failed for ' + f + ': ' + r.stderr)
    print(f'{os.path.basename(f):22} {before//1024:4}KB -> {os.path.getsize(f)//1024}KB')

# ---------- cache-busting: ?v=<content hash> on every local css/js/font reference ----------
def ver(path):
    return hashlib.sha1(open(os.path.join(OUT, path), 'rb').read()).hexdigest()[:8]
for f in glob.glob(OUT + '/*.html'):
    h = open(f, encoding='utf-8').read()
    h = re.sub(r'<img(?![^>]*decoding=)', '<img decoding="async"', h)   # decode images off the main thread
    h = re.sub(r'(src|href)="(assets/[^"?#]+\.(?:js|css))"', lambda m: f'{m.group(1)}="{m.group(2)}?v={ver(m.group(2))}"', h)
    open(f, 'w', encoding='utf-8').write(h)
# ---------- 404: works at any depth and sends visitors home after a few seconds ----------
p404 = OUT + '/404.html'
h = open(p404, encoding='utf-8').read()
if '<base href' not in h:
    h = h.replace('<meta charset="UTF-8"/>', '<meta charset="UTF-8"/>\n<base href="/"/>\n<meta http-equiv="refresh" content="6;url=/"/>', 1)
    open(p404, 'w', encoding='utf-8').write(h)

# ---------- custom domain for GitHub Pages ----------
open(OUT + '/CNAME', 'w').write('galaxyestatesproperties.co.in\n')

# ---------- sitemap + robots for search engines ----------
import datetime
URL = 'https://galaxyestatesproperties.co.in/'
today = datetime.date.today().isoformat()
pages = sorted(os.path.basename(f) for f in glob.glob(OUT + '/*.html') if not f.endswith(('404.html', 'search.html')))
with open(OUT + '/sitemap.xml', 'w') as sm:
    sm.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for pgf in pages:
        loc = URL if pgf == 'index.html' else URL + pgf
        sm.write(f'  <url><loc>{loc}</loc><lastmod>{today}</lastmod><priority>{"1.0" if pgf == "index.html" else "0.8"}</priority></url>\n')
    sm.write('</urlset>\n')
with open(OUT + '/robots.txt', 'w') as rb:
    rb.write('User-agent: *\nAllow: /\nDisallow: /tools/\n\nSitemap: ' + URL + 'sitemap.xml\n')
for n in ('README.txt',):   # internal notes stay off the public site
    if os.path.exists(os.path.join(OUT, n)): os.remove(os.path.join(OUT, n))
# ---------- site source (Python build scripts) kept in the repo, so the site can be rebuilt from it ----------
TOOLS = OUT + '/tools'
os.makedirs(TOOLS, exist_ok=True)
SPD = os.path.dirname(os.path.abspath(__file__))
for n in ('build.py', 'props_build.py', 'land_build.py', 'global_build.py', 't3d_auto.py', 'official.py', 'bmc_city.py', 'country_build.py', 'new_listings.py', 'sitegeo.py', 'forms.py', 'rera_floors.py', 'shgeom.py', 'sh_models.py', 'gm_models.py', 'gmfit.py', 'facades.py', 'gj_models.py', 'plan_cells.py', 'en_cells.py', 'search_index.py', 'satfetch.py', 'make_dist.py', 'land-listings-apps-script.gs'):
    shutil.copy2(os.path.join(SPD, n), os.path.join(TOOLS, n))
if os.path.isdir(os.path.join(SPD, 'shivalik_wave')):
    shutil.copytree(os.path.join(SPD, 'shivalik_wave'), TOOLS + '/shivalik_wave', dirs_exist_ok=True)
open(TOOLS + '/README.md', 'w').write("""# Site source

The pages of this website are generated by these Python scripts:

- `build.py` builds every page from the HTML templates and the project data
- `props_build.py` holds the project listings (prices, sizes, RERA numbers, sources)
- `land_build.py` builds the land-for-sale page
- `global_build.py` builds the property-abroad page
- `make_dist.py` minifies CSS/JS, trims icons, stamps cache versions and writes the sitemap
- `land-listings-apps-script.gs` is the free Google Sheet back end for land posted by owners (setup steps inside)
""")
open(OUT + '/.gitattributes', 'w').write("""# GitHub language statistics: count our own (minified) CSS and JavaScript, and the Python build source
assets/*.js linguist-generated=false linguist-detectable=true
assets/*.css linguist-generated=false linguist-detectable=true
tools/*.py linguist-detectable=true
assets/vendor/** linguist-vendored
""")
total = sum(os.path.getsize(os.path.join(dp, n)) for dp, _, ns in os.walk(OUT) if os.sep + '.git' not in dp for n in ns)
print(f'dist size {total//1024}KB')
open(OUT + '/.gitignore', 'w').write('tools/__pycache__/\n')
