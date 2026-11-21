"""Compare an engineering channel export's Excellon hits to its tscircuit vias."""
import argparse
import json
import math
import re
from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("circuit", type=Path)
parser.add_argument("gerbers", type=Path)
args = parser.parse_args()
elements = json.loads(args.circuit.read_text())
layers = ["top", "inner1", "inner2", "bottom"]
expected = defaultdict(list)
for item in elements:
    if item["type"] in {"pcb_plated_hole", "pcb_hole"}:
        raise ValueError("This audit supports via-only channels")
    if item["type"] != "pcb_via":
        continue
    first, last = sorted(layers.index(layer) + 1 for layer in (item["from_layer"], item["to_layer"]))
    expected[f"drill-L{first}-L{last}.drl"].append((item["x"], item["y"], item["hole_diameter"]))

with ZipFile(args.gerbers) as package:
    drill_files = {name for name in package.namelist() if name.endswith(".drl")}
    if set(expected) != drill_files:
        raise ValueError(f"Unexpected drill file set {drill_files ^ set(expected)}")
    for name in sorted(drill_files):
        holes = expected[name]
        count = len(holes)
        lines = package.read(name).decode().splitlines()
        if "METRIC" not in lines or "G90" not in lines:
            raise ValueError(f"Expected absolute metric coordinates in {name}")
        tools = {}
        diameter = None
        for line in lines:
            if match := re.fullmatch(r"(T\d+)C([\d.]+)", line):
                tools[match[1]] = float(match[2])
            elif line in tools:
                diameter = tools[line]
            elif line.startswith(("X", "Y")):
                match = re.fullmatch(r"X(-?[\d.]+)Y(-?[\d.]+)", line)
                if not match or diameter is None:
                    raise ValueError(f"Unsupported drill command in {name}: {line}")
                x, y = float(match[1]), float(match[2])
                # Exported locations have four decimal places in mm.
                hits = [p for p in holes if math.dist((x, y), p[:2]) <= 0.000071
                        and abs(diameter - p[2]) < 0.000001]
                if len(hits) != 1:
                    raise ValueError(f"Expected one matching via in {name} for {line}, found {len(hits)}")
                holes.remove(hits[0])
        if holes:
            raise ValueError(f"{len(holes)} missing via drills in {name}")
        print(f"{name} matches all {count} via locations and diameters")
