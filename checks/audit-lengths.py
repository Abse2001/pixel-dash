"""Measure saved copper from a rendered tscircuit circuit JSON. Units are mm."""
import argparse
import csv
import json
import math
import sys
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("circuit", type=Path)
parser.add_argument("--through-span-mm", type=float, help="Estimate barrel contribution using the L1–L4 copper separation")
args = parser.parse_args()
if args.through_span_mm is not None and not (math.isfinite(args.through_span_mm) and args.through_span_mm > 0):
    parser.error("The through span must be finite and positive")
elements = json.loads(args.circuit.read_text())
names = {e["source_trace_id"]: e.get("name", "") for e in elements if e["type"] == "source_trace"}
source_traces = {e["source_trace_id"]: e for e in elements if e["type"] == "source_trace"}
pcb_ports = {e["pcb_port_id"]: e for e in elements if e["type"] == "pcb_port"}
ball_pads = {e["pcb_port_id"]: e for e in elements if e["type"] == "pcb_smtpad"
             and e["shape"] == "circle" and e.get("pcb_port_id")}
rows = {}
for trace in elements:
    if trace["type"] != "pcb_trace":
        continue
    name = names.get(trace.get("source_trace_id"), "")
    if not name.startswith("DDR_"):
        continue
    if name in rows:
        raise ValueError(f"{name} has multiple copper paths")
    path = trace["route"]
    a, b = path[0], path[-1]
    if not a.get("start_pcb_port_id") or not b.get("end_pcb_port_id"):
        raise ValueError(f"{name} has an unconnected endpoint")
    endpoints = ((a, a["start_pcb_port_id"]), (b, b["end_pcb_port_id"]))
    landed = set()
    for vertex, port_id in endpoints:
        pad = ball_pads.get(port_id)
        if pad is None or pad["layer"] != vertex.get("layer"):
            raise ValueError(f"{name} endpoint has no BGA land on its signal layer")
        if math.hypot(vertex["x"] - pad["x"], vertex["y"] - pad["y"]) > pad["radius"]:
            raise ValueError(f"{name} trace endpoint falls outside its BGA land")
        landed.add(pcb_ports[port_id]["source_port_id"])
    if landed != set(source_traces[trace["source_trace_id"]]["connected_source_port_ids"]):
        raise ValueError(f"{name} copper lands on different ports from its schematic")
    length = sum(math.hypot(v["x"] - u["x"], v["y"] - u["y"]) for u, v in zip(path, path[1:]))
    direct = abs(a["x"] - b["x"]) + abs(a["y"] - b["y"])
    transitions = [v for v in path if v["route_type"] == "via"]
    if args.through_span_mm is not None and any({v["from_layer"], v["to_layer"]} != {"top", "bottom"}
                                                 for v in transitions):
        raise ValueError(f"{name} has a partial-depth via. Its barrel requires the actual layer span.")
    rows[name] = length, direct, len(transitions)

lanes = [{f"DDR_D{i}" for i in range(8 * n, 8 * n + 8)} |
         {f"DDR_{p}{n}" for p in ("DQM", "DQS", "DQSn")} for n in range(2)]
control = {"DDR_" + p for p in ("CK", "CKn", "CKE", "ODT", "WEn", "CASn", "RASn", "CSn0")}
control.update(f"DDR_A{i}" for i in range(16))
control.update(f"DDR_BA{i}" for i in range(3))
expected = control | lanes[0] | lanes[1] | {"DDR_RESETn"}
ports = {e["source_port_id"]: e for e in elements if e["type"] == "pcb_port" and "source_port_id" in e}
spans = {}
for trace in elements:
    if trace["type"] != "source_trace" or trace.get("name") not in expected:
        continue
    a, b = (ports[key] for key in trace["connected_source_port_ids"])
    spans[trace["name"]] = abs(a["x"] - b["x"]) + abs(a["y"] - b["y"])
if set(spans) != expected or set(rows) - expected:
    raise ValueError("DDR netlist differs from the expected AM3354 interface")
missing = expected - rows.keys()
failed = bool(missing)
print(f"{len(rows)}/{len(expected)} routed. Open: {', '.join(sorted(missing))}", file=sys.stderr)
for group, nets in enumerate([*lanes, control]):
    reference = max(spans[n] for n in nets)
    lo, hi = (0, reference) if group < 2 else (reference + 6.35, reference + 8.89)
    outside = sorted(n for n in nets & rows.keys() if not lo <= rows[n][0] <= hi)
    print(f"{['BYTE0','BYTE1','ADDR_CTRL_CK'][group]} [{lo:.3f}, {hi:.3f}] mm: "
          f"{len(outside)}/{len(nets & rows.keys())} routed outside ({', '.join(outside)})", file=sys.stderr)
    for name in outside:
        length = rows[name][0]
        correction = f"shorten by {length-hi:.3f}" if length > hi else f"lengthen by {lo-length:.3f}"
        print(f"  {name} {length:.3f} mm, {correction} mm to reach the window", file=sys.stderr)
    failed |= bool(outside)

for label, nets, limit in [
    ("BYTE0", lanes[0], 0.635), ("BYTE1", lanes[1], 0.635),
    *((p, (p, n), 0.127) for p, n in (("DDR_CK", "DDR_CKn"), ("DDR_DQS0", "DDR_DQSn0"),
                                        ("DDR_DQS1", "DDR_DQSn1"))),
]:
    lengths = [rows[n][0] for n in nets if n in rows]
    if len(lengths) < 2:
        print(f"{label} skew unavailable", file=sys.stderr)
        failed = True
        continue
    skew = max(lengths) - min(lengths)
    print(f"{label} skew across {len(lengths)}/{len(nets)} signals {skew:.3f} mm, limit {limit:.3f}", file=sys.stderr)
    failed |= skew > limit
    if args.through_span_mm is not None:
        physical = [rows[n][0] + rows[n][2] * args.through_span_mm for n in nets if n in rows]
        estimated_skew = max(physical) - min(physical)
        print(f"{label} geometric spread including {args.through_span_mm:g} mm per traversal: "
              f"{estimated_skew:.3f} mm, limit {limit:.3f}", file=sys.stderr)
        failed |= estimated_skew > limit

# TI SPRS717L Table 7-69 separates intra-DQ and DQ-to-strobe matching.
# Report the actual limiting pins so routing edits can target the right path.
for lane, nets in enumerate(lanes):
    strobes = {f"DDR_DQS{lane}", f"DDR_DQSn{lane}"}
    dq = sorted((nets - strobes) & rows.keys())
    if len(dq) < 2 or not strobes <= rows.keys():
        continue
    for span in [0, *([args.through_span_mm] if args.through_span_mm is not None else [])]:
        lengths = {n: rows[n][0] + span * rows[n][2] for n in dq + sorted(strobes)}
        shortest = min(dq, key=lengths.get)
        longest = max(dq, key=lengths.get)
        data, strobe = max(((d, s) for d in dq for s in sorted(strobes)),
                           key=lambda pair: abs(lengths[pair[0]] - lengths[pair[1]]))
        basis = f"estimated with {span:g} mm per traversal" if span else "planar"
        print(f"BYTE{lane} {basis}: DQ/DM spread {lengths[longest]-lengths[shortest]:.3f} mm "
              f"({longest} to {shortest}), worst DQ/DM-to-DQS mismatch "
              f"{abs(lengths[data]-lengths[strobe]):.3f} mm ({data} to {strobe}), "
              "limit 0.635 mm each", file=sys.stderr)

out = csv.writer(sys.stdout)
out.writerow(["Signal", "Planar length (mm)", "Through vias"])
for n, (length, _, vias) in sorted(rows.items()):
    out.writerow([n, f"{length:.5f}", vias])
sys.exit(int(failed))
