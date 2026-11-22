"""Necessary length test with fixed ball contacts and fixed signal via positions."""
import argparse
import csv
import json
import math
import sys
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("board", type=Path)
parser.add_argument("--through-span-mm", required=True, type=float)
args = parser.parse_args()
if not math.isfinite(args.through_span_mm) or args.through_span_mm <= 0:
    parser.error("Expected a positive finite copper-to-copper span")
board = json.loads(args.board.read_text())
ports = {e["source_port_id"]: e for e in board if e["type"] == "pcb_port" and e.get("source_port_id")}
signals = {e["source_trace_id"]: e for e in board if e["type"] == "source_trace"
           and (e.get("name") or "").startswith("DDR_")}
groups = [{f"DDR_D{i}" for i in range(n*8, n*8 + 8)} |
          {f"DDR_{name}{n}" for name in ("DQM", "DQS", "DQSn")} for n in range(2)]
names = {s["name"] for s in signals.values()}
groups.append(names - groups[0] - groups[1] - {"DDR_RESETn"})
if [len(group) for group in groups] != [11, 11, 27] or len(signals) != 50:
    raise ValueError("Incomplete DDR bus")
def xy(vertex):
    return vertex["x"], vertex["y"]
limits = {}
for group_index, group in enumerate(groups):
    manhattan = []
    for sig in signals.values():
        if sig["name"] in group:
            a, b = (xy(ports[p]) for p in sig["connected_source_port_ids"])
            manhattan.append(sum(abs(i-j) for i, j in zip(a, b)))
    limits.update(dict.fromkeys(group, max(manhattan) + (8.89 if group_index == 2 else 0)))
writer = csv.writer(sys.stdout)
writer.writerow(["signal","fixed_vias","planar_chord_floor_mm","barrels_mm","upper_window_mm",
                 "minimum_excess_mm","routed_planar_minus_chords_mm","maximum_feasible_through_span_mm","best_one_via_relocation_saving_mm"])
seen = set()
for trace in sorted((t for t in board if t["type"] == "pcb_trace" and t.get("source_trace_id") in signals),
                    key=lambda t: signals[t["source_trace_id"]]["name"]):
    name = signals[trace["source_trace_id"]]["name"]
    if name in seen:
        raise ValueError(f"Duplicate path for {name}")
    seen.add(name)
    if name == "DDR_RESETn":
        continue
    path = trace["route"]
    vias = [p for p in path if p["route_type"] == "via"]
    if any({v["from_layer"],v["to_layer"]} != {"top","bottom"} for v in vias):
        raise ValueError(f"Partial-depth signal transition in {name}")
    anchors = [xy(path[0]), *map(xy, vias), xy(path[-1])]
    floor = sum(math.dist(a,b) for a,b in zip(anchors, anchors[1:]))
    length = sum(math.dist(xy(a),xy(b)) for a,b in zip(path,path[1:]))
    barrels = len(vias)*args.through_span_mm
    limit = limits[name]
    # Dropping one anchor gives the most any relocation of that one via can save.
    saving = max((math.dist(a,b) + math.dist(b,c) - math.dist(a,c)
                  for a,b,c in zip(anchors, anchors[1:], anchors[2:])), default=0)
    writer.writerow([name,len(vias),f"{floor:.4f}",f"{barrels:.4f}",f"{limit:.4f}",
                     f"{max(0, floor+barrels-limit):.4f}",f"{length-floor:.4f}",
                     f"{(limit-floor)/len(vias):.4f}" if vias else "",f"{saving:.4f}"])
if seen != names:
    raise ValueError(f"Missing routes for {names-seen}")
