"""Intersect the placed component courtyards on each board side."""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

from shapely import STRtree, affinity
from shapely.geometry import Polygon, box
from shapely.ops import unary_union


def courtyards(board):
    names = {e["source_component_id"]: e["name"] for e in board if e["type"] == "source_component"
             and e.get("ftype") not in ("part", "printedpart", "simple_test_point")}
    placed = {e["pcb_component_id"]: (e["layer"], names[e["source_component_id"]]) for e in board
              if e["type"] == "pcb_component" and not e.get("do_not_place")
              and e.get("source_component_id") in names}
    rings = defaultdict(list)
    for e in board:
        if not e["type"].startswith("pcb_courtyard_") or e["type"].endswith("_error"):
            continue
        if e.get("pcb_component_id") not in placed:
            continue
        if e["type"] == "pcb_courtyard_outline":
            shape = Polygon([(p["x"], p["y"]) for p in e["outline"]])
        elif e["type"] == "pcb_courtyard_rect":
            x, y = e["center"]["x"], e["center"]["y"]
            w, h = e["width"]/2, e["height"]/2
            shape = affinity.rotate(box(x-w, y-h, x+w, y+h), e.get("ccw_rotation", 0), origin=(x, y))
        else:
            raise ValueError(f"Unknown courtyard geometry {e['type']}")
        side, ref = placed[e["pcb_component_id"]]
        if e["layer"] != side or shape.is_empty or not shape.is_valid or shape.area <= 0:
            raise ValueError(f"Invalid courtyard for {ref} on {side}")
        rings[side, ref].append(shape)
    missing = set(placed.values()) - rings.keys()
    if missing:
        raise ValueError(f"Fitted components missing courtyards: {sorted(missing)}")
    return {key: unary_union(shapes) for key, shapes in rings.items()}


if __name__ == "__main__":
    shapes = courtyards(json.loads(Path(sys.argv[1]).read_text()))
    writer = csv.writer(sys.stdout)
    writer.writerow(("side", "part_a", "part_b", "intersection_mm2"))
    failures = 0
    for side in ("top", "bottom"):
        items = [(ref, shape) for (layer, ref), shape in shapes.items() if layer == side]
        tree = STRtree([g for _, g in items])
        for i, (ref, shape) in enumerate(items):
            for j in tree.query(shape, predicate="intersects"):
                if j <= i:
                    continue
                other, peer = items[j]
                area = peer.intersection(shape).area
                if area > 1e-6:
                    writer.writerow((side, ref, other, f"{area:.6f}"))
                    failures += 1
    print(f"Screened {len(shapes)} placed courtyards. Found {failures} overlaps.", file=sys.stderr)
    sys.exit(bool(failures))
