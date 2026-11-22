"""Upper bound on accessible L1 launch sites with only CPU lands and frozen byte copper fixed."""
import argparse
import json
import runpy
from pathlib import Path

from shapely import union_all
from shapely.geometry import LineString, Point

root = Path(__file__).resolve().parents[2]
copper = runpy.run_path(str(root / "checks/audit-copper-contacts.py"))["copper"]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("board", type=Path)
parser.add_argument("balls", nargs="+")
args = parser.parse_args()
board = json.loads(args.board.read_bytes())
ids = {e.get(e["type"] + "_id"): e for e in board}
lands = copper(board)["top"]
locked = {s["subcircuit_connectivity_map_key"] for s in board if s["type"] == "source_trace"
          and (s.get("name") or "").startswith("DDR_D")}
cpu, = [c for c in board if c["type"] == "pcb_component" and ids[c["source_component_id"]].get("name") == "U1"]
via_diameter = {(v["x"], v["y"]): v["outer_diameter"] for v in board if v["type"] == "pcb_via"}
footprints = []
for trace in board:
    if trace["type"] != "pcb_trace" or ids[trace["source_trace_id"]].get("subcircuit_connectivity_map_key") not in locked:
        continue
    section = []
    for p in trace["route"]:
        section.append(p)
        if p["route_type"] != "via" and p is not trace["route"][-1]:
            continue
        if section[0].get("layer", section[0].get("to_layer")) == "top":
            strokes = []
            for a, b in zip(section, section[1:]):
                u, v = (a["x"], a["y"]), (b["x"], b["y"])
                if u != v:
                    width = a["width"] if "width" in a else b["width"]
                    strokes.append(LineString([u,v]).buffer(width/2, cap_style="flat"))
            shape = union_all(strokes)
            for end in (section[0], section[-1]):
                if end["route_type"] == "via":
                    xy = (end["x"],end["y"])
                    shape = shape.difference(Point(xy).buffer(via_diameter[xy]/2 + .16, quad_segs=128))
            footprints.append(shape)
        section = [p]
for ball in args.balls:
    port, = [p for p in board if p["type"] == "pcb_port" and p["pcb_component_id"] == cpu["pcb_component_id"]
             and ids[p["source_port_id"]]["name"] == ball]
    pad, = [shape for o, k, shape in lands if ids[o]["type"] == "pcb_smtpad" and ids[o].get("pcb_port_id") == port["pcb_port_id"]]
    search = pad.centroid.buffer(10)
    wire_blocked, via_blocked = [], []
    for o, k, shape in lands:
        e = ids[o]
        fixed_pad = e["type"] == "pcb_smtpad" and e.get("pcb_component_id") == cpu["pcb_component_id"]
        if not (fixed_pad or k in locked) or e.get("pcb_port_id") == port["pcb_port_id"] or not shape.intersects(search.buffer(1)):
            continue
        wire_blocked.append(shape.buffer(.051 + (.1524 if e["type"] == "pcb_via" else .102), quad_segs=96))
        via_blocked.append(shape.buffer(.14 + (.1524 if e["type"] == "pcb_trace" else .102), quad_segs=96))
    free = search.difference(union_all(wire_blocked))
    pieces = [p for p in getattr(free, "geoms", [free]) if p.distance(pad) <= .051001]
    reachable = union_all(pieces)
    metal = union_all([reachable.buffer(.051001), pad])
    landing = metal.buffer(.140001).difference(union_all(via_blocked))
    # Omitting drill spacing, inner-layer copper and movable components favors finding an escape.
    shadow = union_all([shape.buffer(.14 + .16, quad_segs=96) for shape in footprints if shape.intersects(search.buffer(1))])
    surviving = landing.difference(shadow)
    print(f"U1.{ball}: edge of search {reachable.distance(search.boundary):.4f} mm away; "
          f"candidate via-center area {landing.area:.8f} mm²; with full-width L2 return {surviving.area:.8f} mm²")
