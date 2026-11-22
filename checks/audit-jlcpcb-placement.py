"""Compare the exported placement angle to the supplier's numbered copper lands."""
import csv
import io
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile


def pad_number(hints):
    for hint in hints:
        match = re.fullmatch(r"(?:pin)?(\d+)", str(hint), re.I)
        if match:
            return int(match[1])
    return None


def center(points):
    return tuple(sum(p[axis] for p in points) / len(points) for axis in (0, 1))


def land_center(land):
    if "x" in land and "y" in land:
        return land["x"], land["y"]
    return center([(p["x"], p["y"]) for p in land["points"]])


def offsets(lands, pins):
    centers = {pin: center(lands[pin]) for pin in pins}
    cx, cy = center(list(centers.values()))
    return {pin: (x - cx, y - cy) for pin, (x, y) in centers.items()}


def compare(local, supplier, placement_angle, side):
    common = local.keys() & supplier.keys()
    if len(common) < 2:
        return "", "", len(common), "insufficient"
    board = offsets(local, common)
    catalog = offsets(supplier, common)
    angles = []
    for correction in (0, 90, 180, 270):
        angle = (placement_angle + correction) % 360
        co, si = math.cos(math.radians(angle)), math.sin(math.radians(angle))
        errors = []
        for pin, (x, y) in catalog.items():
            if side == "bottom":
                x = -x
            errors.append(math.dist((co*x - si*y, si*x + co*y), board[pin]))
        angles.append((max(errors), angle))
    worst, best_angle = min(angles)
    if local.keys() != supplier.keys() or any(len(local[k]) != len(supplier[k]) for k in common):
        status = "land_set_differs"
    elif worst > 0.075:
        status = "geometry_differs"
    elif abs((best_angle - placement_angle + 180) % 360 - 180) > 0.001:
        status = "rotation_differs"
    else:
        status = "matches"
    return best_angle, round(worst, 4), len(common), status


def main():
    board = json.loads(Path(sys.argv[1]).read_text())
    library = json.loads(Path(__file__).with_name("jlcpcb-placement-lands.json").read_text())
    with ZipFile(sys.argv[2]) as archive:
        table = list(csv.DictReader(io.StringIO(archive.read("pick_and_place.csv").decode("utf-8-sig"))))
    placements = {row["Designator"]: row for row in table}
    if len(placements) != len(table):
        raise ValueError("Duplicate placement designator")
    parts = {e["source_component_id"]: e for e in board if e["type"] == "source_component"}
    geometry = defaultdict(lambda: defaultdict(list))
    for land in board:
        if land["type"] in ("pcb_smtpad", "pcb_plated_hole"):
            pin = pad_number(land.get("port_hints", []))
            if pin is not None:
                geometry[land["pcb_component_id"]][pin].append(land_center(land))
    writer = csv.writer(sys.stdout)
    writer.writerow(("part", "jlcpcb", "side", "export_deg", "best_deg", "max_error_mm", "matched", "status"))
    findings = 0
    tested = set()
    for footprint in board:
        if footprint["type"] != "pcb_component" or footprint.get("do_not_place"):
            continue
        part = parts.get(footprint.get("source_component_id"), {})
        name = part.get("name")
        if name not in placements:
            continue
        row = placements[name]
        side = footprint["layer"]
        angle = float(row["Rotation"])
        if row["Layer"].lower() != side or not math.isfinite(angle):
            raise ValueError(f"Invalid side or rotation for {name}")
        code, = part["supplier_part_numbers"]["jlcpcb"]
        supplier = defaultdict(list)
        for hints, x, y in library[code]["lands"]:
            pin = pad_number(hints)
            if pin is not None and x is not None and y is not None:
                supplier[pin].append((x, y))
        result = compare(geometry[footprint["pcb_component_id"]], supplier, angle, side)
        writer.writerow((name, code, side, angle, *result))
        tested.add(name)
        findings += result[-1] != "matches"
    if tested != placements.keys():
        raise ValueError(f"Missing CAD geometry for {sorted(placements.keys() - tested)}")
    print(f"{len(tested)} placements screened. {findings} require review.", file=sys.stderr)
    return bool(findings)


if __name__ == "__main__":
    sys.exit(main())
