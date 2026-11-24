"""Screen uniform DDR inner-layer width changes on the module's installed centerlines."""
import csv
import json
import math
import runpy
import sys
from pathlib import Path

from shapely import STRtree
from shapely.geometry import LineString, Point

module = Path(__file__).resolve().parent
geometry = json.loads(Path(sys.argv[1]).read_text())
with (module / "timing.csv").open() as stream:
    ddr = {row["net"] for row in csv.DictReader(stream)}

# All solder lands are on the two outer layers. Inner obstacles are traces and
# through barrels. Filled zones would require a separate re-export after edits.
limits = {}
for layer in ("In2.Cu", "In3.Cu"):
    items = [o for o in geometry if o.get("layer") == layer or o["kind"] == "via"]
    axes = []
    for o in items:
        if o["kind"] == "via":
            axes.append(Point(o["pos"]))
        elif o["kind"] == "track":
            axes.append(LineString([o["start"], o["end"]]))
        else:
            raise ValueError(f"Unsupported inner-layer object: {o}")
    tree = STRtree(axes)
    for trace, axis in zip(items, axes):
        if trace["kind"] != "track" or trace["net"] not in ddr:
            continue
        net = trace["net"]
        limits.setdefault(net, math.inf)
        for index in tree.query(axis.buffer(.65).envelope):
            peer = items[index]
            if net == peer["net"]:
                continue
            distance = axis.distance(axes[index])
            if peer["kind"] == "via":
                width = 2 * (distance - .1524) - peer["diam"]
            elif peer["net"] in ddr:
                # Both centerlines widen by the same amount.
                width = distance - .102
            else:
                width = 2 * (distance - .102) - peer["width"]
            limits[net] = min(limits[net], width)

with (module / "impedance-screen.csv").open() as stream:
    outer = [r for r in csv.DictReader(stream) if r["section"] == "outer"]
capacitance = runpy.run_path(str(module / "check-impedance.py"))["inner_capacitance"]
writer = csv.writer(sys.stdout, lineterminator="\n")
writer.writerow(["inner_width_mm", "mesh_mm", "inner_ideal_ohm", "outer_model_ohm",
                 "common_nominal_min_ohm", "common_nominal_max_ohm", "window_exists",
                 "conflicting_inner_nets", "total_inner_nets"])
for outer_row in sorted(outer, key=lambda r: float(r["mesh_mm"]), reverse=True):
    pitch = float(outer_row["mesh_mm"])
    outer_z = float(outer_row["line_Z_ohm"])
    for width in (.102, .140, .160, .200):
        filled, air = [capacitance(width, pitch, vacuum) for vacuum in (False, True)]
        inner_z = 1 / (299792458 * math.sqrt(filled * air))
        lower = max(50., inner_z - 5, outer_z - 5)
        upper = min(75., inner_z + 5, outer_z + 5)
        writer.writerow([width, pitch, round(inner_z, 3), outer_z, round(lower, 3),
                         round(upper, 3), lower <= upper,
                         sum(width > limit + 1e-6 for limit in limits.values()), len(limits)])
