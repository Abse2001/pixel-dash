"""Screen a centered via at each open DDR ball against the installed artwork."""
import csv
import json
import math
import runpy
import sys
from pathlib import Path

from shapely.geometry import Point

checks = Path(__file__).resolve().parent
board = json.loads(Path(sys.argv[1]).read_bytes())
copper = runpy.run_path(str(checks / "audit-copper-contacts.py"))["copper"](board)
ids = {e.get(e["type"] + "_id"): e for e in board}
sources = {e["source_trace_id"]: e for e in board if e["type"] == "source_trace"}
routed = {e["source_trace_id"] for e in board if e["type"] == "pcb_trace"}
ports = {e["source_port_id"]: e for e in board if e["type"] == "pcb_port" and e.get("source_port_id")}
lands = {e["pcb_port_id"]: e for e in board if e["type"] == "pcb_smtpad" and e.get("pcb_port_id")}
layers = ("top", "inner1", "inner2", "bottom")
references = ("inner1", "inner2", "inner1", "inner2")
writer = csv.writer(sys.stdout)
writer.writerow(("net", "component", "ball", "x_mm", "y_mm", "span", "hole_mm", "via_pad_mm",
                 "nominal_containment_mm", "foreign_copper_conflicts", "drill_conflicts",
                 "existing_DDR_projections_at_relief", "local_screen"))
for source in sorted(sources.values(), key=lambda e: e.get("name") or ""):
    name = source.get("name") or ""
    if not name.startswith("DDR_") or source["source_trace_id"] in routed:
        continue
    for pid in source["connected_source_port_ids"]:
        port = ports[pid]
        ball = ids[pid]
        pad = lands[port["pcb_port_id"]]
        point = Point(port["x"], port["y"])
        pad_geometry = next(s for o, _, s in copper["top"] if o == pad["pcb_smtpad_id"])
        span = layers
        for hole, diameter in ((.20, .45), (.15, .30)):
            copper_hits, drill_hits, projections = set(), set(), set()
            for layer in span:
                for oid, key, shape in copper[layer]:
                    if key == source["subcircuit_connectivity_map_key"] or ids[oid]["type"] == "pcb_copper_pour":
                        continue
                    gap = .1524 if ids[oid]["type"] == "pcb_trace" else .102
                    if shape.distance(point) < diameter / 2 + gap - 1e-6:
                        copper_hits.add(oid)
            for via in board:
                if via["type"] != "pcb_via" or not set(span).intersection(via["layers"]):
                    continue
                blind = len(via["layers"]) == 2 and bool({"top", "bottom"}.intersection(via["layers"]))
                gap = .24 if blind else .20
                if math.hypot(via["x"] - point.x, via["y"] - point.y) < (hole + via["hole_diameter"])/2 + gap - 1e-6:
                    drill_hits.add(via["pcb_via_id"])
            for layer, ref in zip(layers, references):
                if ref not in span:
                    continue
                for oid, _, shape in copper[layer]:
                    obj = ids[oid]
                    if obj["type"] == "pcb_trace" and shape.distance(point) < diameter/2 + .16:
                        peer = sources[obj["source_trace_id"]].get("name") or ""
                        if peer.startswith("DDR_"):
                            projections.add(peer)
            containment = pad_geometry.boundary.distance(point) - diameter/2
            ok = containment > 0 and not (copper_hits or drill_hits or projections)
            writer.writerow((name, ids[ball["source_component_id"]]["name"], ball["name"],
                             f"{point.x:.6f}", f"{point.y:.6f}", "-".join((span[0], span[-1])),
                             hole, diameter, f"{containment:.6f}", "|".join(sorted(copper_hits)),
                             "|".join(sorted(drill_hits)), "|".join(sorted(projections)),
                             "screen-clear" if ok else "conflict"))
