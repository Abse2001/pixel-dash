"""Check the local DAT2 return copper between its antipad edge and the stitching barrel."""
import csv
import json
import math
import sys
from pathlib import Path

from shapely.geometry import LineString, Point

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "checks"))
from ddr_cam import reference

board_path, archive = map(Path, sys.argv[1:])
board = json.loads(board_path.read_bytes())
vias = {v["pcb_via_id"]: v for v in board if v["type"] == "pcb_via"}
signal = vias["mmc0_dat2_ref_via_1"]
stitch = vias["mmc0_dat2_stitch_1"]
signal_xy = (signal["x"], signal["y"])
return_xy = (stitch["x"], stitch["y"])
span = math.dist(signal_xy, return_xy)
direction = [(b-a) / span for a, b in zip(signal_xy, return_xy)]
# Survey 0.10 mm of copper across the return direction. Start beyond the
# design signal antipad and end outside the 0.20 mm stitching drill.
start = signal["outer_diameter"] / 2 + .16 + .005
stop = span - stitch["hole_diameter"] / 2 - .005
ends = [[a + d*r for a, d in zip(signal_xy, direction)] for r in (start, stop)]
strip = LineString(ends).buffer(.05, cap_style="flat")
writer = csv.writer(sys.stdout, lineterminator="\n")
writer.writerow(("member", "center_distance_mm", "strip_area_mm2", "uncovered_mm2"))
for layer, member in (("inner1", "In1_Cu.gbr"), ("inner2", "In2_Cu.gbr")):
    copper = reference(archive, member, Point(return_xy))
    for via in vias.values():
        if layer in via["layers"] and math.dist(return_xy, (via["x"], via["y"])) < 2:
            bore = Point(via["x"], via["y"]).buffer(via["hole_diameter"]/2, quad_segs=64)
            copper = copper.difference(bore)
    missing = strip.difference(copper).area
    writer.writerow((member, round(span, 6), round(strip.area, 8), round(missing, 10)))
    if missing > 1e-8:
        raise SystemExit(f"{member} has an interruption across the local return strip")
