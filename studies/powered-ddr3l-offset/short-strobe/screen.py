"""Evaluate mapped byte-zero copper using the repository's pinned delay modes."""
import argparse
import csv
import json
from pathlib import Path
import runpy
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("circuit", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
checks = Path(__file__).resolve().parents[3] / "checks"
sys.path.insert(0, str(checks))
model = runpy.run_path(str(checks / "audit-ddr-flight.py"))
board = json.loads(args.circuit.read_text())
objects = {row.get(row["type"] + "_id"): row for row in board}
ports = {p["source_port_id"]: p for p in board if p["type"] == "pcb_port" and p.get("source_port_id")}
sources = {s["name"]: s for s in board if s["type"] == "source_trace" and (s.get("name") or "").startswith("DDR_")}
installed = {s["source_trace_id"] for s in board if s["type"] == "pcb_trace"}
missing = [n for n, s in sources.items() if s["source_trace_id"] not in installed]
rows = model["flights"](board, .42, missing)
single, odd, barrel = (model[k] for k in ("SINGLE", "ODD", "BARREL"))
limit = .635 * single
data = [f"DDR_D{i}" for i in range(8)] + ["DDR_DQM0"]
pair = ["DDR_DQS0", "DDR_DQSn0"]
pins = {}
distances = {}
for n in data + pair:
    a, z = sources[n]["connected_source_port_ids"]
    pins[n] = [objects[a]["name"], objects[z]["name"]]
    distances[n] = sum(abs(ports[a][axis] - ports[z][axis]) for axis in ("x", "y"))
cap = max(distances.values())
lengths = [rows[n][0] for n in pair]
modes = [value for n in pair for value in (rows[n][4], rows[n][5], rows[n][4] - (single-odd)*rows[n][0])]
lo, hi = max(lengths)-.635, min(cap, min(lengths)+.635)
fmin, fmax = max(modes)-limit, min(modes)+limit
print(f"Placement cap {cap:.6f} mm. TI planar data interval plus cap {lo:.6f} to {hi:.6f} mm.")
print(f"Data flight interval across both legs and all modeled cases {fmin:.6f} to {fmax:.6f} ps.")
if lo <= hi:
    print(f"Permitted total data barrel depth across that interval {max(0,(fmin-hi*single)/barrel):.6f} to {(fmax-lo*single)/barrel:.6f} mm.")
else:
    print("No barrel depth can repair the planar interval.")
depths = model["DEPTH"]
for label, destination in [("outer-layer only", "top"), ("two L1-L2 transitions", "inner1"),
                           ("two composite L1-L3 transitions", "inner2"), ("two L1-L4 transitions", "bottom")]:
    depth = 2 * abs(depths[destination] - depths["top"])
    low, high = max(lo,(fmin-depth*barrel)/single), min(hi,(fmax-depth*barrel)/single)
    print(f"{label}: {depth:.3f} mm, data length {low:.6f} to {high:.6f} mm, feasible {low<=high}.")
with args.output.open("w") as output:
    writer = csv.writer(output)
    writer.writerow(["net","CPU_ball","RAM_ball","Manhattan_mm","planar_mm","barrels_mm","flight_mixed_ps",
                     "early_ps_vs_DQS","late_ps_vs_DQS","TI_max_present_data_peer_delta_mm","TI_max_strobe_delta_mm",
                     "800_write_setup_needed_ps","800_write_hold_needed_ps","1866_write_setup_needed_ps",
                     "1866_write_hold_needed_ps","800_read_open_latest_from_DQS_ps","800_read_close_earliest_from_DQS_ps"])
    for n in data+pair:
        prefix = [n,*pins[n],round(distances[n],6)]
        if n not in rows:
            writer.writerow(prefix + ["OPEN"])
            continue
        length, count, span, coupled, isolated, mixed = rows[n]
        basic = [*prefix,round(length,6),round(span,6),round(mixed,6)]
        if n in pair:
            writer.writerow(basic)
            continue
        early,late = isolated-max(modes),isolated-min(modes)
        mismatch = max(abs(length-rows[m][0]) for m in data if m!=n and m in rows)
        strobe = max(abs(length-v) for v in lengths)
        # A late data edge consumes write setup. On reads, shift the two DRAM output
        # limits by the respective board skew extremes. DM is not a read output.
        values = [early,late,mismatch,strobe,140+late,160-early,70+late,75-early]
        if n!="DDR_DQM0":
            values += [200+late,.38*2500+early]
        writer.writerow([*basic,*[round(v,6) for v in values]])
