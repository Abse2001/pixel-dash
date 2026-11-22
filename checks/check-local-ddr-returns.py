"""Verify shortened DDR ground and supply escapes against the finished L2 and L3 pours."""
import argparse
import json
import math
from pathlib import Path
from shapely.geometry import Point, Polygon, box
from shapely import affinity

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("circuit", type=Path)
parser.add_argument("--gerbers", type=Path, help="Verify complete via lands on the connected inner-layer Gerber polygons")
args = parser.parse_args()
a = json.loads(args.circuit.read_text())
def rows(t):
    return [e for e in a if e["type"] == t]
def xy(e):
    return e["x"], e["y"]
parts = {e["name"]:e for e in rows("source_component")}
pins = {(e["source_component_id"],e["name"]):e for e in rows("source_port")}
pads = {p["source_port_id"]:p for p in rows("pcb_port") if "source_port_id" in p}
root = Path(__file__).resolve().parents[1]
fanout = json.loads((root/"am3354/reference-fanout.json").read_text())
bypass = json.loads((root/"am3354/bypass-placement.json").read_text())
terminals = [(f["chip"], f["ball"], "top", "GND") for f in fanout if f["net"] == "GND"]
for i, part in enumerate(bypass, 1):
    side = part["layer"]
    if part["chip"] == "U1" and side == "bottom":
        # The switched supply lands now contact L4 directly.
        pin = pins[parts[f"C_DDR{i}"]["source_component_id"], "pin1"]
        land, = [p for p in rows("pcb_smtpad") if p.get("pcb_port_id") == pads[pin["source_port_id"]]["pcb_port_id"]]
        net, = [n for n in rows("source_net") if n["name"] == "VDDS_DDR_CPU"]
        faces = [p["brep_shape"] for p in rows("pcb_copper_pour") if p["layer"] == "bottom" and p["source_net_id"] == net["source_net_id"]]
        if not any(Polygon([xy(v) for v in f["outer_ring"]["vertices"]],
                           [[xy(v) for v in h["vertices"]] for h in f["inner_rings"]]).covers(Point(xy(land))) for f in faces):
            raise ValueError(f"C_DDR{i} does not contact the switched L4 supply")
        continue
    terminals.append((f"C_DDR{i}", "pin2" if side == "top" else "pin1", side,
                      "GND" if side == "top" else "VDDS_DDR"))
ring = lambda r: [xy(p) for p in r["vertices"]]
locations = set()
exported = {}
for ref, terminal, side, net in terminals:
    inner = "inner1" if side == "top" else "inner2"
    supply, = [n for n in rows("source_net") if n["name"] == net]
    key = supply["subcircuit_connectivity_map_key"]
    pour, = [e for e in rows("pcb_copper_pour") if e["source_net_id"] == supply["source_net_id"] and e["layer"] == inner]
    shape = pour["brep_shape"]
    plane = Polygon(ring(shape["outer_ring"]), [ring(r) for r in shape["inner_rings"]])
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
            if not all(n["route_type"]=="wire" and n["layer"]==side for n in route):
                continue
            for start,end in [(route[0],route[-1]), (route[-1],route[0])]:
                if pp["pcb_port_id"] in (start.get("start_pcb_port_id"),start.get("end_pcb_port_id")) and copper.distance(Point(*xy(start))) < start["width"]/2:
                    ends.append(xy(end))
    vias = [v for v in rows("pcb_via") if set(v["layers"])=={side,inner}
            and v.get("subcircuit_connectivity_map_key")==key and v["hole_diameter"]==0.125
            and any(math.dist(xy(v),q)<1e-5 for q in ends)]
    via, = vias
    assert plane.covers(Point(*xy(via)).buffer(via["outer_diameter"]/2)), (ref, terminal)
    if args.gerbers:
        from ddr_cam import reference

        if inner not in exported:
            member = {"inner1": "In1_Cu.gbr", "inner2": "In2_Cu.gbr"}[inner]
            exported[inner] = reference(args.gerbers, member, plane.representative_point())
        center = Point(*xy(via))
        face = exported[inner]
        # Compare against the inscribed radius used to polygonize Gerber round flashes.
        radius = via["outer_diameter"] / 2
        if not face.covers(center) or center.distance(face.boundary) < radius * math.cos(math.pi / 384) - 1e-7:
            raise ValueError(f"{ref}.{terminal} via annulus exceeds connected {inner} Gerber copper")
    locations.add(xy(via))
assert len(locations) == len(terminals) - sum("shareWith" in f for f in fanout if f["net"] == "GND")
if args.gerbers:
    print(f"Connected inner-layer Gerber copper covers all {len(locations)} blind-via lands.")
print(f"{len(terminals)} DDR terminals verified through {len(locations)} blind vias to their adjacent reference planes.")
