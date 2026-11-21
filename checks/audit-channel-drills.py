"""Match every round hole and slot to its Excellon tool, position, plating and span."""
import argparse
import json
import math
import re
from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile

layers = ["top", "inner1", "inner2", "bottom"]
coord = re.compile(r"X(-?[\d.]+)Y(-?[\d.]+)")

def expected_drills(elements):
    files = defaultdict(list)
    for item in elements:
        kind = item["type"]
        if kind not in {"pcb_via", "pcb_hole", "pcb_plated_hole"}:
            continue
        name = "drill_npth.drl" if kind == "pcb_hole" else "drill-L1-L4.drl"
        if kind == "pcb_via":
            first, last = sorted(layers.index(item[k])+1 for k in ("from_layer","to_layer"))
            name = f"drill-L{first}-L{last}.drl"
        x, y = item["x"], item["y"]
        if "hole_diameter" in item:
            size = item["hole_diameter"]
            ends = [(x,y)]
        else:
            w, h = item["hole_width"], item["hole_height"]
            size = min(w,h)
            angle = math.radians(item.get("hole_ccw_rotation",item.get("ccw_rotation",0)) + (90 if h>w else 0))
            half = abs(w-h)/2
            ends = [(x,y)] if half == 0 else [(x+k*half*math.cos(angle), y+k*half*math.sin(angle)) for k in (-1,1)]
        files[name].append((size,ends))
    return files

def compare(name, lines, holes):
    if "METRIC" not in lines or "G90" not in lines or "M30" not in lines:
        raise ValueError(f"Incomplete absolute metric program in {name}")
    function = "NonPlated,1,4,NPTH" if name=="drill_npth.drl" else "Plated," + ",".join(re.findall(r"L(\d+)",name)) + ",PTH"
    if "; #@! TF.FileFunction,"+function not in lines:
        raise ValueError(f"Wrong plating or span in {name}")
    tools = {m[1]:float(m[2]) for l in lines if (m:=re.fullmatch(r"(T\d+)C([\d.]+)", l))}
    tool = None
    count = len(holes)
    slots = 0
    i = lines.index("G90")+1
    while i < len(lines):
        cmd = lines[i]
        i += 1
        if cmd in tools:
            tool = tools[cmd]
            continue
        if cmd in ("G05","M30",""):
            continue
        hit = coord.fullmatch(cmd)
        if not hit or tool is None:
            raise ValueError(f"Unexpected drill command {cmd} in {name}")
        actual = [tuple(map(float,hit.groups()))]
        if i<len(lines) and lines[i].startswith("G85"):
            end = coord.fullmatch(lines[i][3:])
            if not end:
                raise ValueError(f"Invalid slot endpoint {lines[i]}")
            actual.append(tuple(map(float,end.groups())))
            i += 1
            slots += 1
        def matches(expected):
            if len(expected)!=len(actual):
                return False
            # The exporter writes four decimal places for hits and three for G85 endpoints.
            return any(all(math.dist(p,q)<tol for p,q,tol in zip(actual,order,(0.000072,0.00072)))
                       for order in (expected, list(reversed(expected))))
        candidates = [h for h in holes if abs(tool-h[0])<=0.00000051 and matches(h[1])]
        if len(candidates)!=1:
            raise ValueError(f"{name} tool {tool}, {actual}: {len(candidates)} matching design holes")
        holes.remove(candidates[0])
    if holes:
        raise ValueError(f"{name}: {len(holes)} missing drills")
    print(f"{name} matches {count-slots} round hits and {slots} slots")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("circuit", type=Path)
    parser.add_argument("gerbers", type=Path)
    args = parser.parse_args()
    expected = expected_drills(json.loads(args.circuit.read_text()))
    with ZipFile(args.gerbers) as package:
        names = {n for n in package.namelist() if n.endswith(".drl")}
        if set(expected) != names:
            raise ValueError(f"Unexpected drill files: {names ^ set(expected)}")
        for name in sorted(names):
            compare(name, package.read(name).decode().splitlines(), expected[name])
