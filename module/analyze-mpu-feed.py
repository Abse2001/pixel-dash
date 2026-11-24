"""Solve the hot forward feed from exported copper. Run with CAM directory and geom.json."""
import math
import runpy
from pathlib import Path

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components, laplacian
from scipy.sparse.linalg import splu
from shapely import intersects_xy, union_all

# Reuse the drilled-film ownership walk and electrical assertions.
cam = runpy.run_path(str(Path(__file__).with_name("check-cam.py")))
rail = "VDD_MPU"
layers = cam["layers"]
vias = [v for v in cam["vias"] if v["net"] == rail]
pads = [p for p in cam["geom"] if p["kind"] == "pad" and p["net"] == rail]
source = next(p for p in pads if p["ref"] == "L_PMIC_MPU")
feedback = next(p for p in pads if p["pin"] == "FB2")
balls = [p for p in pads if p["ref"] == "U1"]
assert len(balls) == 7
copper = [union_all([p for j, p in enumerate(cam["pieces"][layer])
                     if cam["owners"].get(cam["root"]((layer, j))) == {rail}])
          for layer in layers]

# Millimetres. Layout dielectric distances, copper center to copper center.
z = np.cumsum([0, .1015, .5652, .2256, .5652, .1015])
thickness = [.028, .012, .012, .012, .012, .028]
rho = .00001724 * (1 + .00393 * (105 - 20))
wall = .018

def screen(step):
    x = np.arange(0, 38.4, step)
    y = np.arange(-.6, 46.1, step)
    X, Y = np.meshgrid(x, y)
    edges = []
    terminals = {}
    n = 0
    def link(a, b, conductance):
        edges.append((a, b, np.full(len(a), conductance)))

    barrel = [[] for _ in vias]
    node_xy = []
    for layer, film in enumerate(copper):
        if film.is_empty:
            continue
        mask = intersects_xy(film, X, -Y)
        px, py = X[mask], Y[mask]
        ids = np.full(mask.shape, -1, dtype=int)
        idx = ids[mask] = np.arange(n, n + len(px))
        n += len(px)
        node_xy.extend(zip(px, py, [layer] * len(px)))
        for a, b in [(ids[1:], ids[:-1]), (ids[:, 1:], ids[:, :-1])]:
            valid = (a >= 0) & (b >= 0)
            link(a[valid], b[valid], thickness[layer] / rho)
        for i, via in enumerate(vias):
            vx, vy = via["pos"]
            r = via["drill"] / 2
            rim = idx[np.hypot(px-vx, py-vy) <= r + step]
            if not len(rim):
                continue
            hub = n
            n += 1
            node_xy.append((vx, vy, layer))
            link(rim, np.full(len(rim), hub), 1e5)
            barrel[i].append((layer, hub))
        if layer == 0:
            for pad in [source, feedback, *balls]:
                tx, ty = pad["pos"]
                terminals[pad["pin"]] = idx[np.hypot(px-tx, py-ty) < min(pad["size"])*.44]
                assert len(terminals[pad["pin"]])
    for via, hits in zip(vias, barrel):
        section = math.pi * wall * (via["drill"] + wall)
        for (a, i), (b, j) in zip(hits, hits[1:]):
            link([i], [j], section / ((z[b] - z[a]) * rho))
    a, b, g = (np.concatenate(parts) for parts in zip(*edges))
    graph = coo_matrix((g, (a, b)), shape=(n, n)).tocsr()
    graph += graph.T
    _, labels = connected_components(graph)
    src = terminals[source["pin"]]
    free = labels == labels[src[0]]
    assert all(free[ids].all() for ids in terminals.values())
    free[src] = False
    matrix = laplacian(graph).tocsr()[free][:,free]
    solve = splu(matrix.tocsc()).solve
    current = np.zeros((n, len(balls)))
    for k, ball in enumerate(balls):
        ids = terminals[ball["pin"]]
        current[ids, k] = 1 / len(ids)
    voltage = np.zeros_like(current)
    voltage[free, :] = solve(current[free, :])
    transfer = current.T @ voltage
    assert np.allclose(transfer, transfer.T, rtol=1e-7, atol=1e-9)
    feedback_drop = voltage[terminals[feedback["pin"]]].mean(axis=0)
    sensed = transfer - feedback_drop[None, :]
    k = np.argmax(np.diag(transfer))
    p = (voltage[a,k] - voltage[b,k])**2 * g
    assert np.isclose(p.sum(), transfer[k, k], rtol=1e-6), "Branch loss versus source power"
    # Aggregate local loss rather than using the hottest single grid cell.
    xy = np.array(node_xy)
    bucket = np.floor((xy[a,:2]+xy[b,:2])/2).astype(int)
    groups = {}
    for (x, y), loss in zip(bucket, p):
        groups[x,y] = groups.get((x,y), 0.) + loss
    hot = max(groups, key=groups.get)
    print(f"grid {step:.3f} mm. Concentrated ball loads, mOhm:",
          {p["pin"]: round(1000*r, 3) for p,r in zip(balls, np.diag(transfer).tolist())})
    print(f"worst {balls[k]['pin']}, 1.8 A drop {1800*transfer[k,k]:.3f} mV; "
          f"even split worst {1800*transfer.mean(axis=1).max():.3f} mV; "
          f"worst feedback-to-ball drop at 0.600 A {600*sensed.max():.3f} mV; "
          f"even split feedback-to-ball {600*sensed.mean(axis=1).max():.3f} mV; "
          f"peak 1 mm tile {tuple(map(int,hot))}, {100*groups[hot]/p.sum():.2f}% forward dissipation", flush=True)

for pitch in [.060, .045, .035, .025]:
    screen(pitch)
