"""List physical opens found by tracing six copper films and the plated drill file."""
import csv
import json
import sys
from pathlib import Path

islands_path, drc_path, *options = sys.argv[1:]
islands = json.loads(Path(islands_path).read_text())
native = json.loads(Path(drc_path).read_text())["unconnected_items"]
writer = csv.writer(sys.stdout, lineterminator="\n")
writer.writerow(("net", "islands", "pads_on_each_island"))
physical_opens = 0
for net, groups in sorted(islands.items()):
    if len(groups) > 1:
        physical_opens += len(groups) - 1
        writer.writerow((net, len(groups), " | ".join(" ".join(sorted(g)) for g in sorted(groups))))

print(f"{physical_opens} missing physical joins, {len(native)} native unconnected items", file=sys.stderr)
if "--require-connected" in options and (physical_opens or native):
    raise SystemExit("Whole-module connectivity is incomplete")
