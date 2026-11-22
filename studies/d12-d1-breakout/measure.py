"""Bound the supply escape using the retained DDR envelope and fixed BGA pads."""
import argparse
import json
import runpy
from pathlib import Path

from shapely import STRtree, union_all
from shapely.geometry import LineString, Point

args = argparse.ArgumentParser()
args.add_argument("board", type=Path)
args = args.parse_args()
board = json.loads(args.board.read_bytes())
root = Path(__file__).resolve().parents[2]
copper = runpy.run_path(str(root / "checks/audit-copper-contacts.py"))["copper"](board)
ids = {x.get(x["type"] + "_id"): x for x in board}
nets = {t["subcircuit_connectivity_map_key"]: t["name"] for t in board
        if t["type"] == "source_trace" and t.get("name", "").startswith("DDR_")}
ram = next(x["pcb_component_id"] for x in board if x["type"] == "pcb_component"
           and ids[x["source_component_id"]].get("name") == "U_DDR")
pads = {}
parts = []
for layer in ("top", "bottom"):
    for oid, key, shape in copper[layer]:
        obj = ids[oid]
        net = nets.get(key)
        if net or obj.get("pcb_component_id") == ram:
            parts.append((net or "DRAM footprint", obj["type"], shape.convex_hull))
        if obj["type"] == "pcb_smtpad" and obj.get("pcb_port_id"):
            port = ids[obj["pcb_port_id"]]
            source = ids.get(port.get("source_port_id"), {})
            component = ids.get(source.get("source_component_id"), {})
            if component.get("name") == "U1" and source["name"] in ("N5", "P5"):
                pads[source["name"]] = shape

def measure(removed):
    retained = [(name, shape) for name, kind, shape in parts
                if name not in removed or kind not in ("pcb_trace", "pcb_via")]
    shapes = [shape for _, shape in retained]
    lookup = STRtree(shapes)
    region = union_all(shapes).convex_hull
    margin = region.buffer(.408, quad_segs=64)
    ring = list(region.exterior.coords)
    edges = [LineString([a, z]) for a, z in zip(ring, ring[1:])]
    for ball, pad in sorted(pads.items()):
        p = pad.centroid
        edge = min(edges, key=p.distance)
        owners = [retained[lookup.nearest(Point(q))][0] for q in edge.coords]
        dist = p.distance(margin.boundary) * (-1 if margin.covers(p) else 1)
        print(f"{'+'.join(sorted(removed)) or 'none'},{ball},{dist:.6f},"
              f"{pad.difference(margin).area:.8f},{owners[0]},{owners[1]}")

print("suppressed_routes,ball,signed_center_clearance_mm,pad_area_outside_mm2,edge_start,edge_end")
for paths in [set(), {"DDR_D12"}, {"DDR_D1"}, {"DDR_D12", "DDR_D1"}]:
    measure(paths)

commands = set(nets.values()) - {n for n in nets.values() if n.startswith("DDR_D") or n in ("DDR_CK", "DDR_CKn")}
for paths in [{"DDR_D1", "DDR_D12", "DDR_A10", "DDR_A14"}, commands | {"DDR_D1", "DDR_D12"}]:
    measure(paths)
