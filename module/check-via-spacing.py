"""Audit finished through-hole land edge to unrelated track edge on every signal layer."""
import csv
import json
import sys
from pathlib import Path

from shapely.geometry import LineString, Point
from shapely.strtree import STRtree

MIN_EDGE_MM = 0.1524
items = json.loads(Path(sys.argv[1]).read_text())
tracks = [item for item in items if item["kind"] == "track"]
centers = [LineString([t["start"], t["end"]]) for t in tracks]
tree = STRtree(centers)
max_track_radius = max(t["width"] for t in tracks) / 2
out = csv.writer(sys.stdout, lineterminator="\n")
out.writerow(["via_x_mm", "via_y_mm", "via_net", "trace_net", "layer", "clearance_mm", "target_mm"])
errors = []
for via in items:
    if via["kind"] != "via":
        continue
    point = Point(via["pos"])
    radius = via["diam"] / 2
    nearby = tree.query(point.buffer(radius + MIN_EDGE_MM + max_track_radius).envelope)
    for index in nearby:
        track = tracks[index]
        if track["net"] == via["net"]:
            continue
        edge = point.distance(centers[index]) - radius - track["width"] / 2
        if edge < MIN_EDGE_MM - 1e-9:
            errors.append((*via["pos"], via["net"], track["net"], track["layer"], round(edge, 7), MIN_EDGE_MM))
out.writerows(sorted(errors))
sys.exit(bool(errors))
