"""Verify every reported DDR length belongs to one end-to-end routed centerline."""
import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

from shapely import STRtree
from shapely.geometry import LineString, Point

tolerance = 0.000005  # mm, absorbs the KiCad coordinate rounding at imported joins
geometry = json.loads(Path(sys.argv[1]).read_text())
with Path(sys.argv[2]).open() as stream:
    timing = {r["net"]: r for r in csv.DictReader(stream)}

def inspect(name, row):
    parts = [o for o in geometry if o["net"] == name]
    tracks = [o for o in parts if o["kind"] == "track"]
    pads = [o for o in parts if o["kind"] == "pad"]
    assert {o["ref"] for o in pads} == {"U1", "U_DDR"}
    nodes = defaultdict(list)
    neighbors = defaultdict(list)

    def node(layer, xy):
        for key in nodes[layer]:
            if math.dist(key[1:], xy) <= tolerance:
                return key
        key = (layer, *xy)
        nodes[layer].append(key)
        return key

    def connect(a, b, length):
        neighbors[a].append((b, length))
        neighbors[b].append((a, length))

    lines = defaultdict(list)
    for t in tracks:
        a, b = node(t["layer"], t["start"]), node(t["layer"], t["end"])
        connect(a, b, math.dist(t["start"], t["end"]))
        lines[t["layer"]].append(LineString([t["start"], t["end"]]))
    for v in (o for o in parts if o["kind"] == "via"):
        contacts = [key for group in nodes.values() for key in group
                    if math.dist(key[1:], v["pos"]) <= tolerance]
        if len(contacts) == 2:
            connect(*contacts, 0.)
        else:
            assert len(contacts) == 1 and any(math.dist(p["pos"], v["pos"]) <= min(p["size"])/2
                                              for p in pads), (name, "unexpected barrel contacts", contacts)

    ends = [key for key, links in neighbors.items() if len(links) == 1]
    assert len(ends) == 2 and all(len(n) <= 2 for n in neighbors.values()), (name, "branch", ends)
    assert all(sum(math.dist(end[1:], p["pos"]) <= min(p["size"])/2 for end in ends) == 1
               for p in pads), (name, "endpoints outside assigned balls", ends)
    visited, location, planar = set(), ends[0], 0.
    while location not in visited:
        visited.add(location)
        steps = [(q, length) for q, length in neighbors[location] if q not in visited]
        if not steps:
            break
        (location, length), = steps
        planar += length
    assert visited == set(neighbors) and location == ends[1], (name, "detached copper")
    assert abs(planar - float(row["length_mm"])) < .000006, (name, planar, row["length_mm"])

    for layer, layer_lines in lines.items():
        tree = STRtree(layer_lines)
        for i, first in enumerate(layer_lines):
            for j in tree.query(first, predicate="intersects"):
                if j <= i:
                    continue
                second = layer_lines[j]
                intersection = first.intersection(second)
                common_end = intersection.geom_type == "Point" and all(
                    min(intersection.distance(Point(line.coords[k])) for k in (0, -1)) <= tolerance
                    for line in (first, second))
                assert common_end, (name, "same-net crossing or overlap", layer, intersection.wkt)

assert len(timing) == 50
for signal, result in timing.items():
    inspect(signal, result)
print("All 50 centerlines are single end-to-end paths. Each matches its reported planar length.")
print("No centerline branch, detached loop, same-layer self-crossing or collinear overlap.")
