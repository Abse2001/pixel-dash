"""Cross-check the assembly tables, centroids, sides and rotations against the board."""
import csv
import io
import json
import math
import sys
from pathlib import Path
from zipfile import ZipFile


def table(archive, name):
    rows = list(csv.DictReader(io.StringIO(archive.read(name).decode("utf-8-sig"))))
    result = {row["Designator"]: row for row in rows}
    if len(rows) != len(result):
        raise ValueError(f"Duplicate designator in {name}")
    return result


def verify(board, archive):
    parts = {e["source_component_id"]: e for e in board if e["type"] == "source_component"}
    mounted = {}
    for footprint in board:
        if footprint["type"] != "pcb_component" or footprint.get("do_not_place"):
            continue
        part = parts.get(footprint.get("source_component_id"))
        if not part or part.get("ftype") in ("part", "printedpart", "simple_test_point"):
            continue
        mounted[part["name"]] = (footprint, part)
    bom = table(archive, "bom.csv")
    placements = table(archive, "pick_and_place.csv")
    for name, rows in (("BOM", bom), ("placement", placements)):
        if rows.keys() != mounted.keys():
            raise ValueError(f"{name} missing {sorted(mounted.keys()-rows.keys())}, unexpected {sorted(rows.keys()-mounted.keys())}")
    for ref, row in placements.items():
        footprint, part = mounted[ref]
        if row["Layer"].lower() != footprint["layer"]:
            raise ValueError(f"{ref} has the wrong assembly side")
        for axis in ("x", "y"):
            exported = float(row["Mid " + axis.upper()])
            if not math.isfinite(exported) or abs(exported - footprint["center"][axis]) > 0.000501:
                raise ValueError(f"{ref} has the wrong {axis} centroid")
        angle = float(row["Rotation"])
        expected = footprint.get("rotation", 0)
        if not math.isfinite(angle) or abs((angle - expected + 180) % 360 - 180) > 0.001:
            raise ValueError(f"{ref} rotation is {angle} degrees, expected {expected}")
        codes = part.get("supplier_part_numbers", {}).get("jlcpcb", [])
        if codes and bom[ref]["JLCPCB Part #"] not in codes:
            raise ValueError(f"{ref} BOM code differs from the selected JLCPCB part")
    print(f"{len(mounted)} fitted designators match across circuit, BOM and placement. Centroids, sides and rotations match CAD.")


if __name__ == "__main__":
    with ZipFile(sys.argv[2]) as archive:
        verify(json.loads(Path(sys.argv[1]).read_text()), archive)
