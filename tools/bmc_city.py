"""Mercedes-Benz Places | Binghatti City, drawn around Vision Iconic for the 3D explorer.
Sources: Binghatti Vision Iconic brochure (Oct 2026): 341 m, plot 22,282 sq m, circular podium with a 2,966 sq m water plaza and
three-pointed star, a terraced curved spine that steps down from the tower; Dezeen (15 Jan 2026), Parametric Architecture and
Luxury Launches: 12 towers in all, Vision Iconic plus 11 staggered towers that fall in height away from it, central Grand Promenade.
Plan positions are read from the developer's aerial renders and fitted to the road loop around the Google Maps pin in Nad Al Sheba 1;
only Vision Iconic's height is published, so the other heights are estimated from the renders.
Coordinates: metres in the city's own frame (x towards Al Ain Road / E66, y towards the Vision Iconic end, turned 47 deg from north),
origin at the centre of Vision Iconic's round podium, which sits 262 m west and 224 m north of the pin."""
import math

ROT = 47
ORIGIN = (-262.5, 224.3)          # metres east / north of the Google Maps pin
PLOT_R = round(math.sqrt(22282.2 / math.pi), 1)   # Vision Iconic plot area as a circle: 84.2 m

def shape():
    a0, a1, n = math.radians(45), math.radians(215), 20
    steps = [round(190 - i * 150 / (n - 1), 1) for i in range(n)]
    return dict(podR=72, plazaR=round(math.sqrt(2966 / math.pi), 1),
                shaft=dict(x=round(50 * math.cos(math.radians(25)), 1), y=round(50 * math.sin(math.radians(25)), 1), w=34, d=24, ang=round(math.radians(-65), 4)),
                spine=dict(r1=40, r2=66, a0=round(a0, 4), a1=round(a1, 4), steps=steps))

PARCEL = [(-100, 85), (100, 85), (120, -195), (95, -485), (-135, -425), (-115, -245)]

def context():
    C = []
    C.append(dict(t='flat', p=PARCEL, c='#22382a', z=0.3))
    C.append(dict(t='line', p=PARCEL, c='#8a7a50', z=0.8))
    # Grand Promenade down the middle, with a water channel, and the park at the far end
    C.append(dict(t='flat', p=[(-48, -80), (42, -80), (42, -470), (-48, -440)], c='#2f5a35', z=0.5))
    C.append(dict(t='flat', p=[(-3, -95), (3, -95), (3, -450), (-3, -450)], c='#3aa6d8', z=0.7))
    for y in (-150, -260, -370): C.append(dict(t='disc', x=0, y=y, r=9, c='#3aa6d8', z=0.75))
    C.append(dict(t='flat', p=[(-125, -320), (-50, -320), (-50, -440), (-132, -420)], c='#356a3a', z=0.5))
    for (x, y) in ((-95, -350), (-75, -395), (-108, -400)): C.append(dict(t='disc', x=x, y=y, r=7, c='#4f8a52', z=0.7))
    # towers on the Al Ain Road side (7) and on the other side (4); each is a pair of rounded slabs on a podium
    ne = [(-97, 252), (-156, 224), (-215, 198), (-274, 176), (-333, 153), (-392, 131), (-451, 107)]
    sw = [(-110, 160), (-169, 145), (-228, 130), (-287, 115)]
    C.append(dict(t='pod', x=70, y=-217, w=60, d=290, h=14, r=14))
    C.append(dict(t='pod', x=-78, y=-198, w=58, d=236, h=14, r=14))
    for y in (-392, -451): C.append(dict(t='pod', x=70, y=y, w=64, d=44, h=10, r=20))
    for x0, row in ((70, ne), (-78, sw)):
        for y, h in row:
            base = 10 if y < -380 else 14
            C.append(dict(t='slab', x=x0, y=y + 9, w=40, d=16, r=8, h=h - base, z=base))
            C.append(dict(t='slab', x=x0 + 1.5, y=y - 9, w=40, d=16, r=8, h=h - base - 9, z=base))
    C.append(dict(t='label', text='Binghatti City: 11 more towers', x=10, y=-300, z=290, size=15))
    C.append(dict(t='label', text='Al Ain Road (E66)', x=330, y=-160, z=24, size=13))
    C.append(dict(t='label', text='Grand Promenade', x=0, y=-420, z=30, size=12))
    # Burj Khalifa, 6.0 km away towards Downtown, for orientation (25.1972 N, 55.2744 E)
    C.append(dict(t='far', x=-759, y=6000, label='Burj Khalifa · 6 km', tiers=[(30, 200), (24, 200), (18, 160), (12, 110), (6, 70), (1.5, 88)]))
    return C

def config():
    return dict(context=context(), clear=[PARCEL], plotShape='circle', camR=1050, camY=110, camTurn=2.24, camStay=True)
