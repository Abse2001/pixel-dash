"""Map through bores intersecting exposed component copper; mark planned Type VII sites."""
import csv
import gzip
import json
import runpy
import sys
from pathlib import Path

from shapely import STRtree
from shapely.geometry import Point

study = Path(__file__).resolve().parent
path = Path(sys.argv[1])
opener = gzip.open if path.suffix == ".gz" else open
with opener(path, "rt") as stream:
    board = json.load(stream)
ids = {e.get(e["type"] + "_id"): e for e in board}
copper = runpy.run_path(str(study.parents[1] / "checks/audit-copper-contacts.py"))["copper"](board)
with (study / "capped-vias.csv").open() as stream:
    specified = {(row["via"], row["solder_land"]) for row in csv.DictReader(stream)}
pads = [(side, oid, shape) for side in ("top", "bottom") for oid, _, shape in copper[side]
        if ids[oid]["type"] == "pcb_smtpad" and not ids[oid].get("is_covered_with_solder_mask")]
tree = STRtree([shape for _, _, shape in pads])
writer = csv.writer(sys.stdout, lineterminator="\n")
writer.writerow(("via_id", "x_mm", "y_mm", "hole_mm", "land_mm", "side", "pad_id", "component", "pin",
                 "center_offset_mm", "nominal_bore_containment_mm", "nominal_land_containment_mm", "disposition"))
for via in sorted((e for e in board if e["type"] == "pcb_via" and {e["from_layer"], e["to_layer"]} == {"top", "bottom"}),
                  key=lambda e: e["pcb_via_id"]):
    center = Point(via["x"], via["y"])
    radius = via["hole_diameter"] / 2
    for idx in sorted(tree.query(center.buffer(radius).envelope)):
        side, oid, shape = pads[idx]
        if shape.distance(center) >= radius:
            continue
        pad = ids[oid]
        part = ids[ids[pad["pcb_component_id"]]["source_component_id"]].get("name", "")
        pcb_port = ids.get(pad.get("pcb_port_id"), {})
        pin = ids.get(pcb_port.get("source_port_id"), {}).get("name", "")
        edge = center.distance(shape.boundary) if shape.covers(center) else -shape.distance(center)
        offset = center.distance(shape.centroid)
        known = (via["pcb_via_id"], oid) in specified
        ram_a1 = part == "U_DDR" and pin == "A1" and via["pcb_via_id"] == "channel_pcb_via_1"
        if known or ram_a1:
            assert offset < .001
            decision = "Type VII specified; process acceptance open"
        elif offset < .001:
            decision = "hold: inherited centered site; tolerances and fill disposition open"
        else:
            decision = "hold: off-center bore; redesign or qualify"
        writer.writerow((via["pcb_via_id"], via["x"], via["y"], via["hole_diameter"], via["outer_diameter"],
                         side, oid, part, pin, round(offset, 6), round(edge-radius, 6),
                         round(edge-via["outer_diameter"]/2, 6), decision))
