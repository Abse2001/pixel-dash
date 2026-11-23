"""Locate nominal through-hole and land overlap with exposed processor and memory balls."""
import csv
import gzip
import json
import math
import sys
from pathlib import Path

board_path = Path(sys.argv[1])
opener = gzip.open if board_path.suffix == ".gz" else open
with opener(board_path, "rt") as stream:
    board = json.load(stream)
items = {e.get(e["type"] + "_id"): e for e in board}
parts = {e["source_component_id"]: e["name"] for e in board
         if e["type"] == "source_component" and e.get("name") in ("U1", "U_DDR")}
pads = []
for pad in board:
    if pad["type"] != "pcb_smtpad":
        continue
    part = parts.get(items[pad["pcb_component_id"]]["source_component_id"])
    if not part:
        continue
    assert pad["shape"] == "circle" and not pad["is_covered_with_solder_mask"]
    source_port = items[items[pad["pcb_port_id"]]["source_port_id"]]
    pads.append((part + "." + source_port["name"], pad))
vias = [e for e in board if e["type"] == "pcb_via" and {e["from_layer"], e["to_layer"]} == {"top", "bottom"}]
rows = []
for name, pad in pads:
    for via in vias:
        offset = math.hypot(pad["x"]-via["x"], pad["y"]-via["y"])
        via_radius, bore_radius = via["outer_diameter"]/2, via["hole_diameter"]/2
        if offset >= pad["radius"] + via_radius:
            continue
        edge = pad["radius"] - offset - bore_radius
        if offset >= pad["radius"] + bore_radius:
            contact = "copper land only"
        elif edge < 0:
            contact = "bore crosses solder land edge"
        elif offset > .001:
            contact = "off-center bore inside solder land"
        else:
            contact = "centered bore"
        rows.append((name, via["pcb_via_id"], round(via["x"], 6), round(via["y"], 6),
                     round(offset, 6), via["hole_diameter"], via["outer_diameter"],
                     round(edge, 6), round(pad["radius"]-offset-via_radius, 6), contact))
writer = csv.writer(sys.stdout, lineterminator="\n")
writer.writerow(("ball", "through_via", "via_x_mm", "via_y_mm", "center_offset_mm", "drill_mm", "land_mm",
                 "nominal_bore_containment_mm", "nominal_via_land_containment_mm", "contact"))
writer.writerows(sorted(rows))
