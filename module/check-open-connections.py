"""List physical opens found by tracing six copper films and the plated drill file."""
import csv
import json
import re
from collections import Counter
import sys
from pathlib import Path

islands_path, drc_path, *options = sys.argv[1:]
islands = json.loads(Path(islands_path).read_text())
native = json.loads(Path(drc_path).read_text())["unconnected_items"]
writer = csv.writer(sys.stdout, lineterminator="\n")
writer.writerow(("net", "islands", "pads_on_each_island"))
physical_by_net = Counter()
for net, groups in sorted(islands.items()):
    if len(groups) > 1:
        physical_by_net[net] = len(groups) - 1
        writer.writerow((net, len(groups), " | ".join(" ".join(sorted(g)) for g in sorted(groups))))

native_by_net = Counter()
for finding in native:
    nets = set()
    for item in finding["items"]:
        match = re.search(r"\[([^\]]+)\]", item["description"])
        if not match:
            raise SystemExit(f"Cannot resolve the native net on {item['description']}")
        nets.add(match.group(1))
    if len(nets) != 1:
        raise SystemExit(f"Ambiguous native missing connection: {sorted(nets)}")
    native_by_net[nets.pop()] += 1

if native_by_net != physical_by_net:
    for net in sorted(native_by_net.keys() | physical_by_net.keys()):
        if native_by_net[net] != physical_by_net[net]:
            print(f"{net}: {physical_by_net[net]} drilled, {native_by_net[net]} native", file=sys.stderr)
    raise SystemExit("Drilled and native open connections differ by net")

physical_opens = sum(physical_by_net.values())
print(f"{physical_opens} missing physical joins, {len(native)} native unconnected items", file=sys.stderr)
if "--require-connected" in options and (physical_opens or native):
    raise SystemExit("Whole-module connectivity is incomplete")
