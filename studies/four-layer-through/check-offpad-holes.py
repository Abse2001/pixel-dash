"""Measure moved through holes against every component hole and slot in matched Excellon."""
import csv
import json
import runpy
import sys
from pathlib import Path
from zipfile import ZipFile

from shapely.geometry import LineString, Point

board_path, package, *lists = map(Path, sys.argv[1:])
board = json.loads(board_path.read_text())
helpers = runpy.run_path(str(Path(__file__).resolve().parents[2] / "checks/audit-channel-drills.py"))
drills = helpers["expected_drills"](board)
with ZipFile(package) as archive:
    for name, values in drills.items():
        helpers["compare"](name, archive.read(name).decode().splitlines(), values.copy())

holes = []
for e in board:
    if e["type"] in ("pcb_plated_hole", "pcb_hole"):
        [(diameter, ends)] = next(iter(helpers["expected_drills"]([e]).values()))
        centerline = Point(ends[0]) if len(ends) == 1 else LineString(ends)
        holes.append((centerline, diameter / 2, e[e["type"] + "_id"]))
vias = {e["pcb_via_id"]: e for e in board if e["type"] == "pcb_via"}
writer = csv.writer(sys.stdout, lineterminator="\n")
writer.writerow(("through_via", "closest_component_hole_or_slot", "drill_edge_gap_mm"))
for manifest in lists:
    with manifest.open() as stream:
        for row in csv.DictReader(stream):
            via = vias[row["ground_via"]]
            assert {via["from_layer"], via["to_layer"]} == {"top", "bottom"}
            center = Point(float(row["new_x_mm"]), float(row["new_y_mm"]))
            assert center.distance(Point(via["x"], via["y"])) < 0.00001
            distance, nearest = min((center.distance(line) - r - via["hole_diameter"] / 2, label)
                                    for line, r, label in holes)
            writer.writerow((via["pcb_via_id"], nearest, round(distance, 5)))
