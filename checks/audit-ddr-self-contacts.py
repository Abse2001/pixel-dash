"""Find shortcuts where distant parts of one DDR path touch on the same layer."""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

from shapely.geometry import LineString, Point
from shapely.ops import nearest_points
from shapely.strtree import STRtree


def self_contacts(trace, vias):
    pieces = defaultdict(list)
    distance = 0
    path = trace["route"]
    for index, (a, b) in enumerate(zip(path, path[1:])):
        start, end = [(p["x"], p["y"]) for p in (a, b)]
        if start != end:
            line = LineString([start, end])
            layer = a.get("layer", a.get("to_layer"))
            width = a["width"] if "width" in a else b["width"]
            pieces[layer].append((index, line, width / 2, distance))
            distance += line.length
        if b["route_type"] == "via":
            via = vias[end]
            for layer in ("top", "bottom"):
                pieces[layer].append((index, Point(end), via["outer_diameter"] / 2, distance))
    for layer, spans in pieces.items():
        outlines = [s.buffer(r, quad_segs=32) for _, s, r, _ in spans]
        tree = STRtree(outlines)
        for i, (index, a, ra, sa) in enumerate(spans):
            for j in tree.query(outlines[i], predicate="intersects"):
                if j <= i:
                    continue
                other, b, rb, sb = spans[j]
                overlap = a.intersection(b.buffer(ra + rb, quad_segs=32))
                if overlap.is_empty:
                    samples = [nearest_points(a, b)[0]]
                else:
                    # Parallel segments can meet along an interval. The first nearest
                    # point alone can land at the bend and miss the distant shortcut.
                    samples = [Point(xy) for xy in overlap.coords]
                separation = 0
                for first in samples:
                    second = nearest_points(first, b)[1]
                    left = sa + (a.project(first) if a.geom_type == "LineString" else 0)
                    right = sb + (b.project(second) if b.geom_type == "LineString" else 0)
                    separation = max(separation, right - left)
                # Ignore the normal union of copper around a bend or its own via launch.
                if separation > 2 * (ra + rb) + 0.001:
                    yield layer, index, other, round(separation, 5)


def main():
    board = json.loads(Path(sys.argv[1]).read_text())
    names = {e["source_trace_id"]: e.get("name") or "" for e in board if e["type"] == "source_trace"}
    vias = {(e["x"], e["y"]): e for e in board if e["type"] == "pcb_via"}
    out = csv.writer(sys.stdout)
    out.writerow(("signal", "layer", "first_segment", "second_segment", "path_separation_mm"))
    count = 0
    for trace in board:
        if trace["type"] != "pcb_trace" or not names[trace["source_trace_id"]].startswith("DDR_"):
            continue
        for finding in self_contacts(trace, vias):
            out.writerow((names[trace["source_trace_id"]], *finding))
            count += 1
    print(f"{count} nonlocal same-net DDR copper contacts", file=sys.stderr)
    return bool(count)


if __name__ == "__main__":
    sys.exit(main())
