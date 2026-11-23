"""Check the saved off-pad socket returns against the mask openings and both ground planes."""
import csv
import json
import sys
from pathlib import Path

from shapely.geometry import Point

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "checks"))
from ddr_cam import artwork

board, archive = map(Path, sys.argv[1:])
vias = {e["pcb_via_id"]: e for e in json.loads(board.read_bytes()) if e["type"] == "pcb_via"}
sites = json.loads((Path(__file__).resolve().parents[2] / "production/ground-land-vias.json").read_text())
films = [artwork(archive, member) for member in ("F_Mask.gbr", "B_Mask.gbr", "In1_Cu.gbr", "In2_Cu.gbr")]
out = csv.writer(sys.stdout, lineterminator="\n")
out.writerow(("terminal", "via", "x_mm", "y_mm", "front_mask_land_clear_mm", "back_mask_land_clear_mm",
              "L2_annular_copper_fraction", "L3_annular_copper_fraction"))
for index, site in enumerate(sites):
    if not site.get("through"):
        continue
    name = f"pcb_handheld_ground_land_{index}"
    via = vias[name]
    assert via["layers"] == ["top", "inner1", "inner2", "bottom"]
    assert (via["hole_diameter"], via["outer_diameter"]) == (.2, .45)
    center = Point(via["x"], via["y"])
    margin = [mask.distance(center) - .225 for mask in films[:2]]
    annulus = center.buffer(.225, quad_segs=96).difference(center.buffer(.1, quad_segs=96))
    coverage = [annulus.intersection(film).area / annulus.area for film in films[2:]]
    assert min(margin) > .10 and min(coverage) > .99, (name, margin, coverage)
    out.writerow((site["terminal"], name, via["x"], via["y"], *(round(v, 6) for v in margin + coverage)))
