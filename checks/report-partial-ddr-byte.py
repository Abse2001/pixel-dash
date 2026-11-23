"""Report local data/strobe matching when the rest of a placement study is open."""
import argparse
import csv
import json
import runpy
import sys
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("board", type=Path)
p.add_argument("prior_csv", type=Path)
p.add_argument("--byte", type=int, choices=[0, 1], required=True)
p.add_argument("--study-open", nargs="+", required=True)
args = p.parse_args()
audit = runpy.run_path(str(Path(__file__).with_name("audit-ddr-flight.py")))
flight = audit["flights"](json.loads(args.board.read_text()), .42, args.study_open)
with args.prior_csv.open() as source:
    prior = {row["signal"]: row for row in csv.DictReader(source)}
pair = [f"DDR_DQS{args.byte}", f"DDR_DQSn{args.byte}"]
data = [f"DDR_D{bit}" for bit in range(8*args.byte, 8*args.byte+8)] + [f"DDR_DQM{args.byte}"]
single, odd = audit["SINGLE"], audit["ODD"]
out = csv.writer(sys.stdout)
out.writerow(("signal", "prior_mm", "current_mm", "vias", "total_barrel_mm", "near_mate_mm",
              "mixed_flight_ps", "prior_worst_skew_ps", "signed_worst_skew_ps", "model_limit_ps",
              "model_excess_ps", "TI_delta_to_strobe_mm", "TI_limit_mm", "TI_excess_mm",
              "max_present_data_peer_delta_mm", "peer_limit_mm", "status"))

def times(name):
    length, _, _, _, isolated, mixed = flight[name]
    return [isolated, mixed, isolated-length*(single-odd)] if name in pair else [isolated]*3

for name in data + pair:
    old = prior[name]
    start = [name, old["current_length_mm"]]
    if name not in flight:
        out.writerow(start + [""]*14 + ["OPEN"])
        continue
    length, vias, depth, near, _, mixed = flight[name]
    peers = [other for other in pair if other != name]
    limit = .127 if name in pair else .635
    model = limit*(odd if name in pair else single)
    signed = max((a-b for other in peers for a,b in zip(times(name),times(other))), key=abs)
    delta = max(abs(length-flight[other][0]) for other in peers)
    spread = max((abs(length-flight[d][0]) for d in data if d in flight), default=0) if name in data else None
    passed = abs(signed)<=model and delta<=limit and (spread is None or spread<=.635)
    vals = [length, vias, depth, near, mixed, old["current_signed_worst_scenario_ps"], signed, model,
            max(0,abs(signed)-model), delta, limit, max(0,delta-limit), spread, .635 if spread is not None else None]
    out.writerow(start + [round(v,5) if isinstance(v,float) else v for v in vals] + ["PASS (routed subset)" if passed else "FAIL"])
