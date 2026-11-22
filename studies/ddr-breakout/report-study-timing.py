"""Compare routed study signals to the unchanged strobes on the complete reference board."""
import argparse
import csv
import json
import math
import runpy
import sys
from pathlib import Path

checks = Path(__file__).resolve().parents[2] / "checks"
sys.path.insert(0, str(checks))
audit = runpy.run_path(str(checks / "audit-ddr-flight.py"))
p = argparse.ArgumentParser(description=__doc__)
p.add_argument("complete_board", type=Path)
p.add_argument("study_board", type=Path)
args = p.parse_args()
baseline, study = [json.loads(f.read_text()) for f in (args.complete_board, args.study_board)]


def routes(board):
    sources = {s["source_trace_id"]: s.get("name") for s in board if s["type"] == "source_trace"}
    return {sources[t["source_trace_id"]]: t["route"] for t in board if t["type"] == "pcb_trace"
            and (sources.get(t.get("source_trace_id")) or "").startswith("DDR_")}


def points(route):
    return [(v["x"], v["y"], v.get("width"), v.get("layer"), v.get("from_layer"), v.get("to_layer"))
            for v in route]


old, new = map(routes, (baseline, study))
reference = audit["flights"](baseline, .42)
single, odd, barrel = [audit[name] for name in ("SINGLE", "ODD", "BARREL")]
depth = audit["DEPTH"]
writer = csv.writer(sys.stdout, lineterminator="\n")
writer.writerow(["signal", "baseline_mm", "study_mm", "baseline_vias", "study_vias", "study_spans",
                 "study_traversed_mm", "baseline_flight_ps", "study_flight_ps", "worst_signed_skew_ps",
                 "model_limit_ps", "model_excess_ps", "max_delta_to_strobes_mm", "TI_limit_mm",
                 "TI_excess_mm", "placement_gate_mm", "placement_excess_mm"])
for name in ("DDR_D1", "DDR_D2", "DDR_D5", "DDR_D6", "DDR_D12", "DDR_D13", "DDR_D14", "DDR_D15"):
    if name not in new:
        continue
    lane = int(int(name[5:]) >= 8)
    strobes = [f"DDR_DQS{lane}", f"DDR_DQSn{lane}"]
    assert all(points(old[n]) == points(new[n]) for n in strobes)
    route = new[name]
    length = sum(math.hypot(a["x"] - b["x"], a["y"] - b["y"]) for a, b in zip(route, route[1:]))
    vias = [v for v in route if v["route_type"] == "via"]
    traversed = sum(abs(depth[v["from_layer"]] - depth[v["to_layer"]]) for v in vias)
    flight = length * single + traversed * barrel
    times = [time for n in strobes for time in (reference[n][4], reference[n][5],
             reference[n][4] - (single - odd) * reference[n][0])]
    skew = max((flight - t for t in times), key=abs)
    delta = max(abs(length - reference[n][0]) for n in strobes)
    limit = .635 * single
    gate = (20.600, 23.000)[lane]
    span = " ".join(f"{v['from_layer']}-{v['to_layer']}" for v in vias)
    row = [name, reference[name][0], length, reference[name][1], len(vias), span,
           traversed, reference[name][5], flight, skew, limit, max(0, abs(skew) - limit),
           delta, .635, max(0, delta - .635), gate, max(0, length - gate)]
    writer.writerow([f"{v:.4f}" if isinstance(v, float) else v for v in row])
