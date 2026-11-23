"""Inventory existing non-through barrels on the original populated four-layer board."""
import csv
import json
import math
import runpy
import sys
from pathlib import Path

from shapely import STRtree
from shapely.geometry import Point

root = Path(__file__).resolve().parents[2]
board = json.loads(Path(sys.argv[1]).read_bytes())
objects = {e.get(e["type"] + "_id"): e for e in board}
copper = runpy.run_path(str(root / "checks/audit-copper-contacts.py"))["copper"](board)
trees = {layer: STRtree([shape for _, _, shape in items]) for layer, items in copper.items()}
vias = [e for e in board if e["type"] == "pcb_via"]
keys = {oid: key for items in copper.values() for oid, key, _ in items}
out = csv.writer(sys.stdout)
out.writerow(("via", "x_mm", "y_mm", "old_span", "drill_mm", "land_mm",
              "foreign_fixed_copper", "foreign_pours_to_relieve", "same_net_solder_lands",
              "drill_conflicts", "additional_same_net_land_contacts"))
for via in vias:
    if len(via["layers"]) == 4:
        continue
    oid = via["pcb_via_id"]
    point = Point(via["x"], via["y"])
    for drill, land in ((.2, .45), (.15, .30)):
        fixed, pours, solder, holes, contacts = (set() for _ in range(5))
        for layer, items in copper.items():
            for idx in trees[layer].query(point.buffer(land/2 + .161).envelope):
                other, key, geom = items[idx]
                if other == oid:
                    continue
                kind = objects[other]["type"]
                gap = geom.distance(point) - land/2
                if key == keys[oid]:
                    if gap <= 0:
                        if kind == "pcb_smtpad":
                            solder.add(other)
                        if layer not in via["layers"]:
                            contacts.add(other)
                    continue
                if kind == "pcb_copper_pour":
                    if gap < .16:
                        pours.add(other)
                elif gap < (.1524 if kind == "pcb_trace" else .102) - 1e-6:
                    fixed.add(other)
        for peer in vias:
            if peer is via:
                continue
            blind = len(peer["layers"]) == 2 and bool(set(peer["layers"]) & {"top", "bottom"})
            clearance = (.13 if keys[oid] == keys[peer["pcb_via_id"]] else .24) if blind else .20
            gap = math.hypot(via["x"]-peer["x"], via["y"]-peer["y"]) - (drill+peer["hole_diameter"])/2
            if gap < clearance - 1e-6:
                holes.add(peer["pcb_via_id"])
        out.writerow((oid, via["x"], via["y"], "-".join(via["layers"]), drill, land,
                      *("|".join(sorted(s)) for s in (fixed, pours, solder, holes, contacts))))
