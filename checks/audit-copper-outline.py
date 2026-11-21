"""Measure finished copper clearance to the routed outline and internal cutouts."""
import argparse
import csv
import json
import math
import runpy
import sys
from pathlib import Path

from shapely import prepare
from shapely.geometry import Polygon

geometry = runpy.run_path(str(Path(__file__).with_name("audit-copper-contacts.py")))


def outline(element, field):
    return Polygon([geometry["xy"](point) for point in element[field]])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("circuit", type=Path)
    parser.add_argument("--clearance-mm", required=True, type=float)
    args = parser.parse_args()
    if not math.isfinite(args.clearance_mm) or args.clearance_mm <= 0:
        parser.error("Clearance must be finite and positive")
    board = json.loads(args.circuit.read_text())
    edge, = [e for e in board if e["type"] == "pcb_board"]
    substrate = outline(edge, "outline")
    for cut in board:
        if cut["type"] == "pcb_cutout":
            substrate = substrate.difference(outline(cut, "points"))
    prepare(substrate)
    boundary = substrate.boundary
    findings = 0
    writer = csv.writer(sys.stdout)
    writer.writerow(("layer", "copper", "gap_mm", "outside_substrate"))
    for layer, items in geometry["copper"](board).items():
        for element, _, shape in items:
            outside = not substrate.covers(shape)
            gap = shape.distance(boundary)
            if outside or gap < args.clearance_mm - 1e-6:
                findings += 1
                writer.writerow((layer, element, f"{gap:.6f}", outside))
    print(f"{findings} routed-profile clearance findings at {args.clearance_mm} mm.", file=sys.stderr)
    return bool(findings)


if __name__ == "__main__":
    sys.exit(main())
