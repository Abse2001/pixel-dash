"""Screen solid mechanical through-hole escapes and length-constrained command paths."""
import collections
import json
import math
import re
import sys
from pathlib import Path

from shapely import STRtree
from shapely.affinity import rotate,translate
from shapely.geometry import Point,LineString,box

geometry=json.loads(Path(sys.argv[1]).read_text())
def shape(o):
    if o["kind"]=="track":return LineString((o["start"],o["end"])).buffer(o["width"]/2)
    x,y=o["pos"]
    if o["kind"]=="via":return Point(x,y).buffer(o["diam"]/2)
    a,b=o["size"]
    if o["shape"]==0:return Point(x,y).buffer(a/2)
    if o["shape"]==2:
        axis=((-(a-b)/2,0),((a-b)/2,0)) if a>=b else ((0,-(b-a)/2),(0,(b-a)/2))
        g=LineString(axis).buffer(min(a,b)/2)
    else:g=box(-a/2,-b/2,a/2,b/2)
    return translate(rotate(g,-o["rot"]),x,y)
shapes=[shape(o) for o in geometry];tree=STRtree(shapes)
def endpoint(p,n):
    origin=Point(p);out=[]
    nearby=tree.query(origin.buffer(1.8).envelope)
    for hole,land in ((.2,.45),(.15,.3)):
        for r in (0,.40,.51,.5657,.66,.8,1.0):
            if r==0 and land>.3:continue
            for j in range(32 if r else 1):
                theta=j*math.tau/32
                x,y=p[0]+r*math.cos(theta),p[1]+r*math.sin(theta)
                q=Point(x,y);wire=LineString([p,(x,y)])
                legal=True
                for i in nearby:
                    o=geometry[i];g=shapes[i];dist=q.distance(g)
                    if o["kind"]=="pad" and r and dist<land/2+.08:legal=False;break
                    if o["kind"]=="via" and q.distance(Point(o["pos"]))<.251+(hole+o["drill"])/2:legal=False;break
                    if o["net"]==n: continue
                    limit=max(land/2+(.1534 if o["kind"]=="track" else .103),hole/2+.201)
                    if dist<limit:legal=False;break
                    if (o.get("layer")=="F.Cu" or o["kind"]=="via") and wire.distance(g)<.051+(.1534 if o["kind"]=="via" else .103):
                        legal=False;break
                if legal:out.append((x,y,hole,land,r))
    return out
pads=collections.defaultdict(list)
for o in geometry:
    if o.get("ref") in ("U1","U_DDR") and re.fullmatch(r'DDR_(?:A\d+|BA\d+|CKE|CSn0|CASn|WEn|RASn|RESETn|ODT)',o["net"]):
        pads[o["net"]].append(o["pos"])
routed={o["net"] for o in geometry if o["kind"]=="track"}
pairs={}
for n,ends in pads.items():
    if n not in routed:
        options=[endpoint(p,n) for p in ends]
        pairs[n]=(ends,options); print(n,*(len(f) for f in options),flush=True)
vias=[shape(o) for o in geometry if o["kind"]=="via"]
foreign={l:[] for l in ("In2.Cu","In3.Cu")}
extra=[];saved=[]
for n,(ends,options) in sorted(pairs.items(),key=lambda v:math.prod(len(x) for x in v[1][1])):
    chosen=None
    for a in options[0]:
        for b in options[1]:
            q,z=a[:2],b[:2];ab=math.dist(q,z)
            if any(Point(v[:2]).distance(g)<v[3]/2+.154 for v in (a,b) for g in extra):continue
            if any(Point(v[:2]).distance(g)<v[3]/2+.154 for v in (a,b) for gs in foreign.values() for g in gs):continue
            target=ab if n=="DDR_RESETn" else 36.7-a[4]-b[4]
            if target<ab:continue
            for fac in (0.5,.35,.65,.2,.8):
                # Elliptical locus bounds the total two-segment length.
                f=ab/2;maj=target/2;local=(2*fac-1)*f
                mag=math.sqrt(max(0,(maj*maj-f*f)*(1-(local/maj)**2)))
                for side in (-1,1):
                    mid=((q[0]+z[0])/2+(z[0]-q[0])*local/ab-side*(z[1]-q[1])*mag/ab,
                         (q[1]+z[1])/2+(z[1]-q[1])*local/ab+side*(z[0]-q[0])*mag/ab)
                    if not (.5<=mid[0]<=36.5 and .5<=mid[1]<=45.5):continue
                    path=LineString([q,mid,z])
                    if any(path.distance(g)<.205 for g in vias+extra):continue
                    for layer,items in foreign.items():
                        if any(path.distance(g)<.2045 for g in items):continue
                        chosen=dict(net=n,ends=ends,vias=[a,b],inner=layer,path=[q,mid,z]);break
                    if chosen:break
                if chosen:break
            if chosen:break
        if chosen:break
    if chosen:
        saved.append(chosen);foreign[chosen["inner"]].append(LineString(chosen["path"]).buffer(.051))
        extra.extend(Point(v[:2]).buffer(v[3]/2) for v in chosen["vias"])
        print("reserved",n,flush=True)
Path(sys.argv[2]).write_text(json.dumps(saved,indent=2)+"\n")
