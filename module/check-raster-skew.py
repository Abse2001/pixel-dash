"""Track module-only LCD data-to-PCLK flight from drilled joins and routed layer spans."""
import csv
import json
import math
import sys
from collections import Counter
from pathlib import Path

geometry = json.loads(Path(sys.argv[1]).read_text())
islands = json.loads(Path(sys.argv[2]).read_text())

# Copper center depths on JLC06161H-1080, in mm. The routing delay constants
# match the nominal flight screen in check-timing.py. Neither includes pad loads.
depth = dict(zip(("F.Cu", "In1.Cu", "In2.Cu", "In3.Cu", "In4.Cu", "B.Cu"),
                 (0, .1015, .6667, .8923, 1.4575, 1.559)))
tolerance = .000005


def measure(name):
    pads = [o for o in geometry if o["kind"] == "pad" and o["net"] == name]
    by_ref = {p["ref"]: p for p in pads}
    ends = [by_ref[r] for r in ("U1", "J_CARRIER")]
    labels = [p["ref"] + "." + p["pin"] for p in ends]
    if not any(set(labels) <= set(group) for group in islands[name]):
        return labels, None

    tracks = [o for o in geometry if o["kind"] == "track" and o["net"] == name]
    vias = [o for o in geometry if o["kind"] == "via" and o["net"] == name]
    layers = Counter()
    for t in tracks:
        layers[t["layer"]] += math.dist(t["start"], t["end"])
    # For these unbranched display signals every intermediate land has exactly
    # two track ends, counting the pad as an end at a centered through launch.
    anchors = []
    neighbors = []
    def anchor(layer, pos):
        for i, (ly, xy) in enumerate(anchors):
            if ly == layer and math.dist(pos, xy) <= tolerance:
                return i
        anchors.append((layer, pos))
        neighbors.append([])
        return len(neighbors) - 1

    def join(a, b):
        neighbors[a].append(b)
        neighbors[b].append(a)

    for t in tracks:
        join(anchor(t["layer"], t["start"]), anchor(t["layer"], t["end"]))
    terminals = [anchor(p["layer"], p["pos"]) for p in ends]
    barrel = 0.
    for v in vias:
        contacts = [i for i, (_, xy) in enumerate(anchors) if math.dist(v["pos"], xy) <= tolerance]
        a, b = contacts
        join(a, b)
        barrel += abs(depth[anchors[a][0]] - depth[anchors[b][0]])
    node, end = terminals
    visited = set()
    while node != end:
        visited.add(node)
        step, = [i for i in neighbors[node] if i not in visited]
        node = step
    if len(visited) + 1 != len(anchors) or len(neighbors[end]) != 1 or len(neighbors[terminals[0]]) != 1:
        raise ValueError(f"{name} must be one unbranched path between the assigned pads")
    outer = layers["F.Cu"] + layers["B.Cu"]
    inner = sum(layers.values()) - outer
    return labels, (outer, inner, len(vias), barrel, outer * 5.884 + inner * 6.671 + barrel * 6.600)


clock = "LCD_PCLK"
rows = {n: measure(n) for n in [clock, *(f"LCD_D{i}" for i in range(16, 24))]}
clock_path = rows[clock][1]
out = csv.writer(sys.stdout, lineterminator="\n")
out.writerow(["net", "cpu", "contact", "drilled_join", "outer_mm", "inner_mm", "through_vias",
              "traversed_barrel_mm", "nominal_flight_ps", "data_minus_pclk_ps"])
for name, (labels, path) in rows.items():
    skew = ""
    if path and clock_path and name != clock:
        skew = round(path[-1] - clock_path[-1], 3)
    fields = [round(v, 6) for v in path] if path else [""] * 5
    out.writerow([name, *labels, "CONNECTED" if path else "OPEN", *fields, skew])
