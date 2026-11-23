"""Write a per-net, per-location inventory of non-through drills in the saved board."""
import csv
import gzip
import json
import sys
from collections import defaultdict
from pathlib import Path

board = Path(sys.argv[1])
opener = gzip.open if board.suffix == ".gz" else open
with opener(board, "rt") as stream:
    items = json.load(stream)
names = defaultdict(set)
traces = defaultdict(set)
for item in items:
    if item["type"] in ("source_net", "source_trace") and item.get("name"):
        table = names if item["type"] == "source_net" else traces
        table[item.get("subcircuit_connectivity_map_key")].add(item["name"])
layers = {"top": 1, "inner1": 2, "inner2": 3, "bottom": 4}
writer = csv.writer(sys.stdout, lineterminator="\n")
writer.writerow(("net_names", "connectivity_key", "via_id", "span", "x_mm", "y_mm", "drill_mm", "land_mm"))
rows = []
for via in items:
    if via["type"] != "pcb_via":
        continue
    start, end = sorted((layers[via["from_layer"]], layers[via["to_layer"]]))
    if (start, end) == (1, 4):
        continue
    key = via["subcircuit_connectivity_map_key"]
    rows.append(("|".join(sorted(names[key] or traces[key])) or key, key, via["pcb_via_id"], f"L{start}-L{end}",
                 via["x"], via["y"], via["hole_diameter"], via["outer_diameter"]))
writer.writerows(sorted(rows))
