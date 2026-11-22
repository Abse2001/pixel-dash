"""Check rejected full-path candidates against the reserved DDR copper on c28dc8c."""
import argparse
import csv
import json
import sys
from pathlib import Path

from shapely.geometry import LineString, MultiPoint
from shapely.ops import unary_union

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("native_circuit", type=Path)
args = parser.parse_args()
board = json.loads(args.native_circuit.read_text())
names = {e["source_trace_id"]: e.get("name") for e in board if e["type"]=="source_trace"}

def geometry(sections):
    layers = [unary_union([LineString(s) for i,s in enumerate(sections) if i%2==l and len(s)>1]) for l in (0,1)]
    return layers, MultiPoint([s[-1] for s in sections[:-1]])

def collision(first, second):
    a,h = first
    b,k = second
    # Compare centerlines: 0.102 mm signal width, 0.300 mm via land, 0.150 mm drill.
    return (any(x.distance(y) < .204-1e-6 for x,y in zip(a,b))
            or any(x.distance(k)<.3534-1e-6 or y.distance(h)<.3534-1e-6 for x,y in zip(a,b))
            or h.distance(k)<max(.300+.102,.150+.200)-1e-6)

baseline = {}
endpoints = {}
for t in board:
    if t["type"]!="pcb_trace" or not (names[t["source_trace_id"]] or "").startswith("DDR_"):
        continue
    name = names[t["source_trace_id"]]
    sections = [[]]
    for point in t["route"]:
        xy = point["x"],point["y"]
        sections[-1].append(xy)
        if point["route_type"]=="via":
            sections.append([xy])
    baseline[name] = geometry(sections)
    endpoints[name] = [sections[0][0],sections[-1][-1]]
assert len(baseline)==50
trials = json.loads(Path(__file__).with_name("trial-paths.json").read_text())
out = csv.writer(sys.stdout,lineterminator="\n")
out.writerow(["trial","candidate","baseline_DDR_conflicts"])
for group,routes in trials.items():
    for name,sections in routes.items():
        assert all(abs(a-b)<1e-6 for pt,ref in zip([sections[0][0],sections[-1][-1]],endpoints[name]) for a,b in zip(pt,ref))
        trial = geometry(sections)
        out.writerow([group,name," ".join(sorted(n for n,g in baseline.items() if n!=name and collision(trial,g)))])
