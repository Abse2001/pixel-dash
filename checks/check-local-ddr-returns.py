"""Verify every shortened DDR ground escape from pad through finished L2 copper."""
import json
import math
import sys
from pathlib import Path
from shapely.geometry import Point, Polygon, box
from shapely import affinity

a = json.loads(Path(sys.argv[1]).read_text())
def rows(t):
    return [e for e in a if e["type"] == t]
def xy(e):
    return e["x"], e["y"]
parts = {e["name"]:e for e in rows("source_component")}
pins = {(e["source_component_id"],e["name"]):e for e in rows("source_port")}
pads = {p["source_port_id"]:p for p in rows("pcb_port") if "source_port_id" in p}
ground, = [n for n in rows("source_net") if n["name"] == "GND"]
key = ground["subcircuit_connectivity_map_key"]
pour, = [p for p in rows("pcb_copper_pour") if p["source_net_id"] == ground["source_net_id"] and p["layer"]=="inner1"]
shape = pour["brep_shape"]
ring = lambda r: [xy(p) for p in r["vertices"]]
plane = Polygon(ring(shape["outer_ring"]),[ring(r) for r in shape["inner_rings"]])
locations = set()
for ref, terminal in [("U1","H6"),("U1","H7"),("U1","G8"),("U_DDR","D8"),
                      ("U_DDR","E8"),("U_DDR","T1"),("C_DDR12","pin2")]:
    p = pins[parts[ref]["source_component_id"],terminal]
    pp = pads[p["source_port_id"]]
    land, = [v for v in rows("pcb_smtpad") if v.get("pcb_port_id") == pp["pcb_port_id"]]
    x,y = xy(land)
    if land["shape"] == "circle":
        copper = Point(x,y).buffer(land["radius"],quad_segs=128)
    else:
        w,h = land["width"]/2,land["height"]/2
        copper = affinity.rotate(box(x-w,y-h,x+w,y+h),land.get("ccw_rotation",0),origin=(x,y))
    ends = []
    for s in rows("source_trace"):
        if p["source_port_id"] not in s["connected_source_port_ids"] or s.get("subcircuit_connectivity_map_key")!=key:
            continue
        for t in rows("pcb_trace"):
            if t.get("source_trace_id")!=s["source_trace_id"]:
                continue
            route = t["route"]
            if not all(n["route_type"]=="wire" and n["layer"]=="top" for n in route):
                continue
            for start,end in [(route[0],route[-1]), (route[-1],route[0])]:
                if pp["pcb_port_id"] in (start.get("start_pcb_port_id"),start.get("end_pcb_port_id")) and copper.distance(Point(*xy(start))) < start["width"]/2:
                    ends.append(xy(end))
    vias = [v for v in rows("pcb_via") if set(v["layers"])=={"top","inner1"}
            and v.get("subcircuit_connectivity_map_key")==key and v["hole_diameter"]==0.125
            and any(math.dist(xy(v),q)<1e-5 for q in ends)]
    via, = vias
    assert plane.covers(Point(*xy(via)).buffer(via["outer_diameter"]/2)), (ref, terminal)
    locations.add(xy(via))
assert len(locations)==6
print("Seven DDR ground terminals reach the L2 ground plane through six 0.125 mm laser holes.")
