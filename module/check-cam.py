"""Walk plated copper on six exported films. Measure return voids under full DDR trace widths."""
import collections
import json
import math
import re
import sys
from pathlib import Path
from shapely import STRtree,union_all
from shapely.geometry import Point,LineString
from gerbonara import ExcellonFile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"checks"))
from itertools import groupby
from gerbonara import GerberFile
from gerbonara.graphic_primitives import Circle,Line
from gerbonara.utils import MM
from shapely import make_valid
from shapely.geometry import GeometryCollection,Polygon

def artwork(path):
    film=GerberFile.open(path)
    copper=GeometryCollection()
    primitives=(g for obj in film.objects for g in obj.to_primitives(unit=MM))
    for polarity,items in groupby(primitives,lambda g:g.polarity_dark):
        shapes=[]
        for g in items:
            if isinstance(g,Circle):s=Point(g.x,g.y).buffer(g.r,quad_segs=96)
            elif isinstance(g,Line):s=LineString([(g.x1,g.y1),(g.x2,g.y2)]).buffer(g.width/2,quad_segs=96)
            else:
                contour=g.to_arc_poly()
                if any(contour.arc_centers):contour=contour.approximate_arcs(max_error=.000005)
                s=Polygon(contour.outline)
                # KiCad emits Gerber cut-in regions. Node the repeated boundary
                # and retain areal faces; verify conservation of signed area.
                if not s.is_valid:
                    valid=make_valid(s)
                    assert abs(valid.area-s.area)<1e-6, (path,s.area,valid.area)
                    s=union_all(polygons(valid))
            shapes.append(s)
        mask=union_all(shapes)
        copper=copper.union(mask) if polarity else copper.difference(mask)
    return copper

cam=Path(sys.argv[1]);geom=json.loads(Path(sys.argv[2]).read_text())
layers=["F.Cu","In1.Cu","In2.Cu","In3.Cu","In4.Cu","B.Cu"]
drillfile,=cam.glob("*.drl")
assert "TF.FileFunction,MixedPlating,1,6" in drillfile.read_text()
flashes=ExcellonFile.open(drillfile).objects
drills=[(Point(f.x,f.y),f.aperture.diameter/2) for f in flashes]
vias=[o for o in geom if o["kind"]=="via"]
assert len(vias)==len(drills)
def point(p): return Point(p[0],-p[1])
assignments={}
for v in vias:
    matches=[i for i,(p,r) in enumerate(drills) if p.distance(point(v["pos"]))<.00072 and abs(r*2-v["drill"])<1e-6]
    idx,=matches
    assert idx not in assignments
    assignments[idx]=v
def polygons(g):
    if g.geom_type=="Polygon":return [g]
    return [p for s in g.geoms for p in polygons(s)] if hasattr(g,"geoms") else []
parents={}
def root(a):
    parents.setdefault(a,a)
    while parents[a]!=a:
        parents[a]=parents[parents[a]];a=parents[a]
    return a
pieces={};trees={};annuli=collections.defaultdict(list)
bores=union_all([p.buffer(r,quad_segs=48) for p,r in drills])
for layer,ext in zip(layers,("gtl","g1","g2","g3","g4","gbl")):
    f,=cam.glob("*."+ext)
    pg=pieces[layer]=polygons(artwork(f).difference(bores))
    tree=trees[layer]=STRtree(pg)
    for idx,(p,r) in enumerate(drills):
        ring=p.buffer(r+.003,quad_segs=48).difference(p.buffer(r,quad_segs=48))
        for j in tree.query(ring,predicate="intersects"):
            if pg[j].intersection(ring).area>1e-6:annuli[idx].append((layer,j))
for i in assignments:
    hits=annuli[i]
    assert len(hits)>=2,(i,hits)
    for h in hits[1:]:parents[root(h)]=root(hits[0])
pads=collections.defaultdict(list);owners=collections.defaultdict(set)
for e in geom:
    if e["kind"]!="pad" or not e["net"]:continue
    p=point(e["pos"]);l=e["layer"]
    # Also works if a centered plated hole removes copper at the pad center.
    radius=min(e["size"])*.47
    nodes={root((l,j)) for j in trees[l].query(p.buffer(radius),predicate="intersects") if pieces[l][j].intersection(p.buffer(radius)).area>1e-6}
    n,=nodes;owners[n].add(e["net"]);pads[e["net"]].append((e["ref"],e["pin"],n))
for i,v in assignments.items():
    owners[root(annuli[i][0])].add(v["net"])
assert all(len(n)==1 for n in owners.values()),[n for n in owners.values() if len(n)>1]
signals={n:ends for n,ends in pads.items() if len(ends)==2 and {a for a,b,c in ends}=={"U1","U_DDR"} and n.startswith("DDR_")}
assert len(signals)==50
opens=sorted(n for n,ends in signals.items() if ends[0][2]!=ends[1][2])
print(f"{50-len(opens)}/50 independent drilled DDR pairs. Open: {', '.join(opens)}")
assert len({ends[0][2] for n,ends in signals.items() if n not in opens})==50-len(opens)
print(f"{len(drills)} plated through drills. No shorts between mapped lands or vias.")
print("Drill diameters:",dict(collections.Counter(v["drill"] for v in vias)))
planes={}
for l in ("In1.Cu","In4.Cu"):
    plane=max(enumerate(pieces[l]),key=lambda a:a[1].area)
    assert owners[root((l,plane[0]))]=={"GND_INTERNAL"}
    planes[l]=plane[1]
miss=collections.Counter()
for n in signals:
    launches=union_all([point(v["pos"]).buffer(v["diam"]/2+.155,quad_segs=64) for v in vias if v["net"]==n])
    for t in geom:
        if t["kind"]!="track" or t["net"]!=n:continue
        l=t["layer"];ref="In1.Cu" if l in ("F.Cu","In2.Cu") else "In4.Cu"
        s=LineString([point(t["start"]),point(t["end"])]).buffer(t["width"]/2,quad_segs=48).difference(launches)
        lost=s.difference(planes[ref]).area
        if lost>1e-8:miss[n]+=lost
print("Full-width ground reference losses outside own launches (mm²):",dict(sorted(miss.items())))

if miss:
    raise SystemExit("DDR ground coverage failed")

if len(sys.argv) > 3:
    # Identify individual pads on each physical island for targeted routing.
    # Stable component/pin labels make the report independent of polygon order.
    by_island = collections.defaultdict(list)
    for net_name, endpoints in pads.items():
        for ref, pin, node in endpoints:
            by_island[net_name, node].append(f"{ref}.{pin}")
    islands = collections.defaultdict(list)
    for (net_name, node), pins in by_island.items():
        islands[net_name].append(sorted(pins))
    Path(sys.argv[3]).write_text(json.dumps(
        {name: sorted(groups) for name, groups in sorted(islands.items())},
        indent=2
    ) + "\n")
