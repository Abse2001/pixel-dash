"""Check the five frozen BA0 reliefs against the accepted L2 Gerber polygon."""
import csv
import json
import sys
from pathlib import Path

from shapely.geometry import LineString, Point
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "checks"))
import runpy

from shapely import get_parts
from shapely.geometry import box

board = json.loads(Path(sys.argv[1]).read_bytes())
physical_sheet = runpy.run_path(str(ROOT / "checks/measure-return-plane-path.py"))["physical_sheet"]
sheet = physical_sheet(board, Path(sys.argv[2]), "inner1", "GND", box(-130, -60, 130, 60))
via = next(e for e in board if e.get("pcb_via_id") == "channel_pcb_via_0")
land = Point(via["x"], via["y"]).buffer(via["outer_diameter"] / 2)
writer = csv.writer(sys.stdout)
writer.writerow(["study", "length_mm", "window_low_mm", "window_high_mm", "via_land_island_mm2", "result"])
for route_file in sorted(Path(__file__).parent.glob("bank-*.json")):
    legs = json.loads(route_file.read_bytes())["DDR_BA0"]
    assert [layer for layer, points in legs] == [0, 1, 0]
    length = sum(LineString(points).length for layer, points in legs)
    assert 36.14999 <= length <= 38.68999
    inner = LineString(legs[1][1])
    pads = [Point(point).buffer(.14 + .16, quad_segs=192) for point in (inner.coords[0], inner.coords[-1])]
    relief = unary_union([inner.buffer(.051 + .16, quad_segs=96), *pads])
    islands = sorted(get_parts(sheet.difference(relief)), key=lambda p: -p.area)
    contacts = [island for island in islands if island.intersection(land).area > 1e-6]
    assert len(contacts) == 1 and contacts[0] is not islands[0], "Expected a grounded-land regression"
    writer.writerow([route_file.stem, f"{length:.5f}", 36.14999, 38.68999,
                     f"{contacts[0].area:.6f}", "REJECT"])
