"""plan image <-> lat/lon similarity transform (plan y down, metres y north), fitted on control points"""
import numpy as np, math
from PIL import Image, ImageDraw
E=6378137.0; D=math.pi/180
def m(o, la, lo): return np.array([(lo-o[1])*D*E*math.cos(o[0]*D), (la-o[0])*D*E])
def ll(o, x, y): return [o[0]+y/(D*E), o[1]+x/(D*E*math.cos(o[0]*D))]
def fit(pairs, o):
    """pairs: [[px,py,lat,lon]] -> (a,b,tx,ty) for x=a*px - b*(-py) ..., residuals (m)"""
    P=np.array([[p[0],-p[1]] for p in pairs],float); Q=np.array([m(o,p[2],p[3]) for p in pairs])
    pc=P.mean(0); qc=Q.mean(0); A=P-pc; B=Q-qc
    a=(A[:,0]*B[:,0]+A[:,1]*B[:,1]).sum()/(A**2).sum(); b=(A[:,0]*B[:,1]-A[:,1]*B[:,0]).sum()/(A**2).sum()
    prm=(a,b,qc[0]-(a*pc[0]-b*pc[1]),qc[1]-(b*pc[0]+a*pc[1]))
    res=[float(np.hypot(*(fwd(prm,p[0],p[1])-Q[i]))) for i,p in enumerate(pairs)]
    return prm,res
def fwd(prm,px,py):
    a,b,tx,ty=prm; X,Y=px,-py; return np.array([a*X-b*Y+tx, b*X+a*Y+ty])
def inv(prm,x,y):
    a,b,tx,ty=prm; x-=tx; y-=ty; d=a*a+b*b; X=(a*x+b*y)/d; Y=(-b*x+a*y)/d; return np.array([X,-Y])
def to_ll(prm,o,px,py): x,y=fwd(prm,px,py); return ll(o,x,y)
def overlay(img, out, prm, o, polys, col=(255,0,0), w=3, scale=1.0):
    im=Image.open(img).convert('RGB'); d=ImageDraw.Draw(im)
    for P in polys:
        q=[tuple(inv(prm,*m(o,la,lo))*scale) for la,lo in P]; d.line(q+[q[0]],fill=col,width=w)
    im.save(out); return im

def px2ll(meta, x, y):
    """pixel in a __mos capture -> [lat, lon]"""
    W=256*2**meta['z']; X=meta['X0']+x; Y=meta['Y0']+y
    return [math.degrees(math.atan(math.sinh(math.pi*(1-2*Y/W)))), X/W*360-180]
def ll2px(meta, la, lo):
    W=256*2**meta['z']; s=math.sin(math.radians(la))
    return [(lo+180)/360*W-meta['X0'], (0.5-math.log((1+s)/(1-s))/(4*math.pi))*W-meta['Y0']]
