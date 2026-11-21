"""Check the integrated L2 ground surface, NTC isolation and retained through-via clearances."""
import json
import sys
from pathlib import Path

from shapely.geometry import Point, Polygon, box

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "production"))
from connectivity import trace_net_keys

board = json.loads(Path(sys.argv[1]).read_text())
ground, = [e for e in board if e["type"] == "source_net" and e["name"] == "GND"]
pour, = [e for e in board if e["type"] == "pcb_copper_pour" and e["layer"] == "inner1"
         and e["source_net_id"] == ground["source_net_id"]]

def ring(outline):
    return [(p["x"], p["y"]) for p in outline]

shape = pour["brep_shape"]
plane = Polygon(ring(shape["outer_ring"]["vertices"]), [ring(r["vertices"]) for r in shape["inner_rings"]])
edge, = [e for e in board if e["type"] == "pcb_board"]
outline = Polygon(ring(edge["outline"]))
assert plane.is_valid and outline.buffer(-0.299).covers(plane)
# Check copper reaches both controller zones and the power-management block.
for x, y in [(-96, 0), (96, 0), (-20.5, 25)]:
    assert plane.covers(Point(x, y)), (x, y)
_, keys = trace_net_keys(board)
ground_count = isolated_count = 0
for e in board:
    if e["type"] == "pcb_cutout":
        assert plane.distance(Polygon(ring(e["points"]))) >= 0.298
    if e["type"] == "pcb_keepout" and "inner1" in e["layers"]:
        x, y = e["center"]["x"], e["center"]["y"]
        w, h = e["width"]/2, e["height"]/2
        assert plane.intersection(box(x-w, y-h, x+w, y+h)).area < 1e-8
    if e["type"] != "pcb_via" or "inner1" not in e["layers"] or e["pcb_via_id"].startswith("channel_"):
        continue
    key = e.get("subcircuit_connectivity_map_key") or keys[e["source_trace_id"]]
    center = Point(e["x"], e["y"])
    if key == ground["subcircuit_connectivity_map_key"]:
        assert plane.covers(center), e["pcb_via_id"]
        ground_count += 1
    else:
        assert plane.distance(center) - e["outer_diameter"]/2 >= 0.158, e["pcb_via_id"]
        isolated_count += 1
print(f"L2 ground covers {plane.area:.1f} mm². Verified {ground_count} retained ground vias and {isolated_count} unrelated via clearances.")
