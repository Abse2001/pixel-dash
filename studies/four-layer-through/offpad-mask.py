"""Measure moved through-via lands and bores against both exported solder-mask openings."""
import csv
import json
import sys
from pathlib import Path
from zipfile import ZipFile

from shapely.geometry import Point

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "checks"))
from ddr_cam import artwork

board_path, archive, ground_sites = map(Path, sys.argv[1:])
board = json.loads(board_path.read_bytes())
vias = {e["pcb_via_id"]: e for e in board if e["type"] == "pcb_via"}
with ground_sites.open() as stream:
    moved = ["pcb_system_KEY_L_via_1", *(row["ground_via"] for row in csv.DictReader(stream))]
writer = csv.writer(sys.stdout, lineterminator="\n")
writer.writerow(("via", "x_mm", "y_mm", "hole_mm", "land_mm", "mask", "bore_to_opening_mm", "land_to_opening_mm"))
for member in ("F_Mask.gbr", "B_Mask.gbr"):
    with ZipFile(archive) as files:
        assert b"%TF.FilePolarity,Negative*%" in files.read(member)
    openings = artwork(archive, member)
    for name in moved:
        v = vias[name]
        distance = openings.distance(Point(v["x"], v["y"]))
        hole, land = v["hole_diameter"], v["outer_diameter"]
        if distance <= land/2:
            raise ValueError(f"{name} land intersects {member} opening")
        writer.writerow((name, v["x"], v["y"], hole, land, member,
                         round(distance-hole/2, 6), round(distance-land/2, 6)))
