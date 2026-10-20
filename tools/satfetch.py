"""Esri World Imagery mosaic around a point: newimg/<name>.webp + .meta.json (X0, Y0 = global pixel of the top-left corner at zoom z)."""
import math, sys, io, os, json, urllib.request
from PIL import Image
def fetch(name, lat, lon, z=19, w=1000, h=900, src='esri'):
    S = 256 * 2 ** z
    X = (lon + 180) / 360 * S; Y = (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * S
    X0, Y0 = X - w / 2, Y - h / 2
    im = Image.new('RGB', (w, h))
    for tx in range(int(X0 // 256), int((X0 + w) // 256) + 1):
        for ty in range(int(Y0 // 256), int((Y0 + h) // 256) + 1):
            cache = f'tiles/{src}_{z}_{tx}_{ty}.jpg' if src != 'esri' else f'tiles/{z}_{tx}_{ty}.jpg'
            if not os.path.exists(cache):
                os.makedirs('tiles', exist_ok=True)
                def qk(x, y, z):
                    s_ = ''
                    for i in range(z, 0, -1):
                        d_ = 0; m_ = 1 << (i - 1)
                        if x & m_: d_ += 1
                        if y & m_: d_ += 2
                        s_ += str(d_)
                    return s_
                u = {'esri': f'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{ty}/{tx}',
                     'google': f'https://mt1.google.com/vt/lyrs=s&x={tx}&y={ty}&z={z}',
                     'bing': f'https://ecn.t{(tx + ty) % 4}.tiles.virtualearth.net/tiles/a{qk(tx, ty, z)}.jpeg?g=1'}[src]
                import time
                for k in range(6):
                    try: data = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30).read(); break
                    except Exception:
                        if k == 5: raise
                        time.sleep(1.5 * (k + 1))
                open(cache, 'wb').write(data)
            try: tile = Image.open(cache).convert('RGB')
            except Exception:
                os.remove(cache); tile = Image.new('RGB', (256, 256), (40, 40, 40))     # tile not available at this zoom
            im.paste(tile, (int(tx * 256 - X0), int(ty * 256 - Y0)))
    im.save(f'newimg/{name}.webp', quality=90)
    json.dump(dict(name=name, z=z, X0=X0, Y0=Y0, w=w, h=h), open(f'newimg/{name}.meta.json', 'w'))
    return im
if __name__ == '__main__':
    a = sys.argv; fetch(a[1], float(a[2]), float(a[3]), *(int(x) for x in a[4:7]), **({'src': a[7]} if len(a) > 7 else {}))
