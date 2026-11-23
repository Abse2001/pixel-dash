"""Locate through vias whose land or hole intersects a component solder land."""
import csv
import json
import sys
from shapely import STRtree
from shapely.affinity import rotate,translate
from shapely.geometry import Point,LineString,box
from pathlib import Path

objects=json.loads(Path(sys.argv[1]).read_text())
pads=[o for o in objects if o["kind"]=="pad"]
def surface(o):
    w,h=o["size"]
    if o["shape"]==0:s=Point(0,0).buffer(w/2,quad_segs=64)
    elif o["shape"]==2:
        dx,dy=max(w-h,0)/2,max(h-w,0)/2
        s=LineString(((-dx,-dy),(dx,dy))).buffer(min(w,h)/2,quad_segs=64)
    else:s=box(-w/2,-h/2,w/2,h/2)
    return translate(rotate(s,-o["rot"]),*o["pos"])
copper=[surface(p) for p in pads];tree=STRtree(copper)
out=csv.writer(sys.stdout,lineterminator="\n")
out.writerow(("x_mm","y_mm","net","hole_mm","land_mm","solder_land","face","nominal_bore_to_land_boundary_mm","classification"))
for v in sorted((o for o in objects if o["kind"]=="via"),key=lambda v:v["pos"]):
    p=Point(v["pos"]);hits=tree.query(p.buffer(v["diam"]/2),predicate="intersects")
    if not len(hits):out.writerow([*v["pos"],v["net"],v["drill"],v["diam"],"","","","off-pad"])
    for i in hits:
        pad=pads[i];s=copper[i];clear=(s.boundary.distance(p) if s.covers(p) else -s.distance(p))-v["drill"]/2
        category="centered" if p.distance(Point(pad["pos"]))<.001 else "contained off-center" if clear>=0 else "bore crosses edge" if s.distance(p)<v["drill"]/2 else "annulus only"
        out.writerow([*v["pos"],v["net"],v["drill"],v["diam"],pad["ref"]+"."+pad["pin"],pad["layer"],round(clear,5),category])
