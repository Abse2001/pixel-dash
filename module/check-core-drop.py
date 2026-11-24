"""Screen forward DC drop on the six-layer module's routed DCDC1 CORE tree."""
import csv
import json
import math
import sys
from collections import defaultdict

import numpy as np
from shapely.geometry import LineString, Point

geometry = json.load(open(sys.argv[1]))
copper = [item for item in geometry if item["net"] == "VDD_CORE"]
tracks = [item for item in copper if item["kind"] == "track"]
vias = [item for item in copper if item["kind"] == "via"]
pads = {item["ref"]+"."+item["pin"]: item for item in copper if item["kind"] == "pad"}
thickness = {"F.Cu": .035, "In2.Cu": .0152, "In3.Cu": .0152, "B.Cu": .035}
depth = {"F.Cu": 0., "In2.Cu": .6667, "In3.Cu": .8923, "B.Cu": 1.5590}
sites = defaultdict(set)
def key(point):
    return tuple(round(c, 5) for c in point)
for item in tracks:
    sites[item["layer"]].update([key(item["start"]), key(item["end"])])
for pad in pads.values():
    sites[pad["layer"]].add(key(pad["pos"]))
edges = []
rho = 1.724e-5  # ohm mm at 20 C
for trace in tracks:
    layer = trace["layer"]
    line = LineString([trace["start"], trace["end"]])
    cuts = sorted((line.project(Point(p)), p) for p in sites[layer] if line.distance(Point(p)) < .00002)
    for (a,p),(b,q) in zip(cuts, cuts[1:]):
        if p != q:
            edges.append(((layer,p), (layer,q), rho*(b-a)/(trace["width"]*thickness[layer])))
for via in vias:
    p = key(via["pos"])
    layers = sorted((layer for layer, points in sites.items() if p in points),key=depth.get)
    assert len(layers) >= 2, p
    # Assumes a 20 um wall around the finished hole. Resin carries no current.
    bore = via["drill"]
    barrel_area = math.pi*((bore/2+.020)**2-(bore/2)**2)
    for a,b in zip(layers,layers[1:]):
        edges.append(((a,p), (b,p), rho*(depth[b]-depth[a])/barrel_area))
nodes = sorted({n for a,b,_ in edges for n in (a,b)})
ids = {n:i for i,n in enumerate(nodes)}
def padid(label):
    pad = pads[label]
    return ids[pad["layer"], key(pad["pos"])]
G = np.zeros((len(nodes),len(nodes)))
for a,b,r in edges:
    assert r > 0
    i,j = ids[a],ids[b]
    G[i,i] += 1/r
    G[j,j] += 1/r
    G[i,j] -= 1/r
    G[j,i] -= 1/r
source = padid("L_PMIC_CORE.pin2")
fb = padid("U_PMIC.FB1")
balls = sorted(label for label in pads if label.startswith("U1."))
assert len(balls) == 20
live = np.arange(len(nodes)) != source
amps = np.zeros(len(nodes))
for ball in balls:
    amps[padid(ball)] = -.1/len(balls)
voltage = np.zeros(len(nodes))
voltage[live] = np.linalg.solve(G[np.ix_(live,live)], amps[live])
assert abs((G @ voltage)[source]-.1)<1e-8
out=csv.writer(sys.stdout,lineterminator="\n")
out.writerow(["ball","share_mA","inductor_to_ball_mV_at_20C","FB1_to_ball_mV_at_20C","FB1_to_ball_mV_at_85C"])
for ball in balls:
    v = voltage[padid(ball)]
    drop = 1000*(voltage[fb]-v)
    out.writerow([ball,5,round(-1000*v,4),round(drop,4),round(drop*(1+.00393*65),4)])
