"""Bound the placement gate for each byte over every legal DQ permutation."""
import argparse
import csv
import gzip
import json
import sys
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("board", type=Path)
parser.add_argument("timing", type=Path)
args = parser.parse_args()
opener = gzip.open if args.board.suffix == ".gz" else open
with opener(args.board, "rt") as source:
    board = json.load(source)
ports = {p["source_port_id"]: p for p in board if p["type"] == "pcb_port" and p.get("source_port_id")}
components = {c["source_component_id"]: c["name"] for c in board if c["type"] == "source_component"}
owners = {p["source_port_id"]: components.get(p["source_component_id"]) for p in board if p["type"] == "source_port"}
ends = {}
for t in board:
    if t["type"] != "source_trace" or not t.get("name", "").startswith("DDR_"):
        continue
    ids = t["connected_source_port_ids"]
    if len(ids) == 2 and {owners[k] for k in ids} == {"U1", "U_DDR"}:
        ends[t["name"]] = {owners[k]: ports[k] for k in ids}

def distance(a, b):
    return abs(a["x"] - b["x"]) + abs(a["y"] - b["y"])

with args.timing.open() as f:
    lengths = {row["signal"]: row for row in csv.DictReader(f)}
writer = csv.writer(sys.stdout, lineterminator="\n")
writer.writerow(["signal","length_mm","current_project_gate_mm","largest_gate_any_legal_remap_mm","minimum_excess_holding_length_mm"])
for lane in (0, 1):
    data = [f"DDR_D{i}" for i in range(8*lane, 8*lane+8)]
    fixed = [f"DDR_{stem}{lane}" for stem in ("DQM","DQS","DQSn")]
    # Each CPU/RAM DQ pair occurs in at least one complete bijection within the byte.
    choices = [(i,j) for i in data for j in data] + [(i,i) for i in fixed]
    ceiling = max(distance(ends[i]["U1"], ends[j]["U_DDR"]) for i,j in choices)
    gate = max(distance(ends[i]["U1"], ends[i]["U_DDR"]) for i in data + fixed)
    for i in data + fixed:
        if lengths[i]["current_length_mm"]:
            length = float(lengths[i]["current_length_mm"])
            assert abs(float(lengths[i]["placement_nominal_max_mm"]) - gate) < .0001
            writer.writerow([i, f"{length:.4f}", f"{gate:.5f}", f"{ceiling:.5f}", f"{max(0, length-ceiling):.5f}"])
