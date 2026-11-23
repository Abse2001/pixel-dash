"""Measure existing A6/A7 copper conflicts if the isolated A10 path is overlaid."""
import csv
import json
import runpy
import sys
from pathlib import Path


checks = Path(__file__).resolve().parents[3] / "checks"
geometry = runpy.run_path(str(checks / "audit-copper-contacts.py"))["copper"]

def routes(path, names):
    board = json.loads(Path(path).read_bytes())
    ids = {e.get(e["type"] + "_id"): e for e in board}
    keys = {e["subcircuit_connectivity_map_key"]: e["name"] for e in board
            if e["type"] == "source_trace" and e.get("name") in names}
    return {layer: [(keys[k], o, ids[o]["type"], shape) for o, k, shape in group
                    if k in keys and ids[o]["type"] in ("pcb_trace", "pcb_via")]
            for layer, group in geometry(board).items()}

baseline = routes(sys.argv[1], {"DDR_A6", "DDR_A7"})
trial = routes(sys.argv[2], {"DDR_A10"})
writer = csv.writer(sys.stdout, lineterminator="\n")
writer.writerow(("layer", "retained_net", "retained_object", "trial_object", "edge_gap_mm",
                 "required_mm", "overlap_mm2"))
for layer, shapes in baseline.items():
    for name, identity, kind, shape in shapes:
        for _, new_id, new_kind, new_shape in trial[layer]:
            clearance = .1524 if {kind, new_kind} == {"pcb_trace", "pcb_via"} else .102
            gap = shape.distance(new_shape)
            if gap < clearance:
                writer.writerow((layer, name, identity, new_id, round(gap, 6), clearance,
                                 round(shape.intersection(new_shape).area, 6)))
