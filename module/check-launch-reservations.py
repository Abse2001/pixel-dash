"""Check the saved PCLK and USB launch reservations against extracted board geometry."""
import json
import math
import sys
from pathlib import Path

from shapely.affinity import rotate, translate
from shapely.geometry import LineString, Point, box

geometry = json.loads(Path(sys.argv[1]).read_text())
# Site XY, drill 0.150 and land 0.300 mm. Width is the pad-to-barrel trace width.
sites = [
    ("LCD_PCLK", "U1", "V5", (24.940058, 39.830088), .104),
    ("THROUGH_USB_DP_A", "J_CARRIER", "24", (27.220, 2.820), .115),
    ("THROUGH_USB_DM_A", "J_CARRIER", "25", (27.650, 2.775), .115),
]


def pad_shape(item):
    width, height = item["size"]
    if item["shape"] == 0:
        return Point(item["pos"]).buffer(width / 2)
    if item["shape"] == 2:
        delta = (width - height) / 2
        ends = [(-delta, 0), (delta, 0)] if delta >= 0 else [(0, delta), (0, -delta)]
        local = LineString(ends).buffer(min(width, height) / 2)
    else:
        local = box(-width / 2, -height / 2, width / 2, height / 2)
    return translate(rotate(local, -item["rot"], origin=(0, 0)), *item["pos"])


def check(actual, minimum, net, rule):
    if actual < minimum - 1e-6:
        raise SystemExit(f"{net} {rule} clearance {actual:.6f} mm requires {minimum:.6f} mm")


# Include the other reservations in the obstacle set even before copper is installed.
for net, ref, pin, xy, width in sites:
    pad = next(o for o in geometry if o.get("ref") == ref and o["pin"] == pin)
    geometry.extend([
        dict(kind="via", net=net, pos=xy, drill=.15, diam=.30),
        dict(kind="track", net=net, layer=pad["layer"], start=pad["pos"], end=xy, width=width),
    ])

for net, ref, pin, xy, width in sites:
    pad = next(o for o in geometry if o.get("ref") == ref and o["pin"] == pin)
    if pad["net"] != net:
        raise SystemExit(f"{ref}.{pin} no longer maps to {net}")
    site = Point(xy)
    lead = LineString([pad["pos"], xy])
    for o in geometry:
        if o["kind"] == "via":
            dist = math.dist(xy, o["pos"])
            if o["net"] == net and dist < .00001:
                continue
            check(dist - (.15 + o["drill"]) / 2, .250, net, "hole-to-hole")
            check(dist - (.30 + o["diam"]) / 2, .102, net, "land-to-land")
            check(lead.distance(Point(o["pos"])) - (width + o["diam"]) / 2,
                  .1524, net, "launch trace to via")
        elif o["kind"] == "track" and o["net"] != net:
            line = LineString([o["start"], o["end"]])
            check(site.distance(line) - (.30 + o["width"]) / 2, .1524, net, "via to trace")
            if o["layer"] == pad["layer"]:
                check(lead.distance(line) - (width + o["width"]) / 2, .102, net, "trace-to-trace")
        elif o["kind"] == "pad":
            shape = pad_shape(o)
            if o is not pad:
                check(site.distance(shape) - .15, .102, net, "via to pad")
                if o["layer"] == pad["layer"]:
                    check(lead.distance(shape) - width / 2, .102, net, "trace to pad")
            else:
                check(site.distance(shape) - .075, .075, net, "drill to source solder land")
    print(f"{net} {ref}.{pin} off-pad launch reservation passes")
