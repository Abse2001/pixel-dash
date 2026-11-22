"""Estimate L4 spreading resistance on the two LS1 islands in the Gerber/drill export."""
import json
import runpy
import sys
from pathlib import Path
from zipfile import ZipFile

import numpy as np
from scipy.ndimage import label
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve
from shapely import intersects_xy, prepare
from shapely.geometry import LineString, Point
from shapely.ops import unary_union

from ddr_cam import artwork


def squares(shape, first, last, pitch):
    """Finite-volume sheet with one square per face link and equipotential via lands."""
    xmin, ymin, xmax, ymax = shape.bounds
    x = np.arange(xmin + pitch / 2, xmax, pitch)
    y = np.arange(ymin + pitch / 2, ymax, pitch)
    prepare(shape)
    mask = intersects_xy(shape, x[None, :], y[:, None])
    def contact(v):
        return mask & ((x[None, :] - v["x"])**2 + (y[:, None] - v["y"])**2 <= (v["outer_diameter"]/2)**2)
    high, low = contact(first), contact(last)
    pieces, _ = label(mask)
    ids = np.unique(pieces[high])
    if len(ids) != 1 or not low.any() or not np.all(pieces[low] == ids[0]):
        raise ValueError("Mesh does not connect both terminal annuli")
    mask &= pieces == ids[0]
    nodes = np.full(mask.shape, -1, dtype=int)
    nodes[mask] = np.arange(mask.sum())
    left, right = nodes[:, :-1], nodes[:, 1:]
    down, up = nodes[:-1, :], nodes[1:, :]
    horizontal = (left >= 0) & (right >= 0)
    vertical = (down >= 0) & (up >= 0)
    a = np.r_[left[horizontal], down[vertical]]
    b = np.r_[right[horizontal], up[vertical]]
    edge = np.ones(len(a))
    system = coo_matrix((np.r_[edge, edge, -edge, -edge], (np.r_[a, b, a, b], np.r_[a, b, b, a])),
                        shape=(mask.sum(), mask.sum())).tocsr()
    v = np.zeros(mask.sum())
    v[nodes[high]] = 1
    unknown = ~(high | low)[mask]
    v[unknown] = spsolve(system[unknown][:, unknown].tocsc(), -(system @ v)[unknown])
    current = (system @ v)[nodes[high]].sum()
    return 1 / current


board = json.loads(Path(sys.argv[1]).read_text())
archive = Path(sys.argv[2])
via = {e["pcb_via_id"]: e for e in board if e["type"] == "pcb_via"}
drill = runpy.run_path(str(Path(__file__).with_name("audit-channel-drills.py")))
holes = []
with ZipFile(archive) as z:
    for member, expected in drill["expected_drills"](board).items():
        if "L4" not in member and "npth" not in member:
            continue
        drill["compare"](member, z.read(member).decode().splitlines(), expected.copy())
        for diameter, points in expected:
            center = Point(points[0]) if len(points) == 1 else LineString(points)
            holes.append(center.buffer(diameter / 2, quad_segs=48))
image = artwork(archive, "B_Cu.gbr").difference(unary_union(holes))
pairs = [("upper", "bridge_upper"), ("bridge_lower", "balls")]
islands = []
for a, b in pairs:
    first, last = [via["via_ddr_supply_" + name] for name in (a, b)]
    def annulus(v):
        return Point(v["x"], v["y"]).buffer(v["outer_diameter"] / 2)
    island, = (p for p in image.geoms if p.intersection(annulus(first)).area > .001 and
               p.intersection(annulus(last)).area > .001)
    islands.append((island, first, last))
columns = "pitch_mm,upper_squares,lower_squares,total_mOhm_35um_20C,drop_mV_300mA"
if "via_ddr_supply_lower_bank" in via:
    columns += ",direct_lower_squares,direct_lower_mOhm_35um_20C"
print(columns)
for pitch in (.080, .055, .040, .030, .025):
    upper, lower = [squares(*data, pitch) for data in islands]
    resistance = (upper + lower) * .01724 / .035
    row = f"{pitch:.3f},{upper:.4f},{lower:.4f},{resistance:.4f},{.300*resistance:.4f}"
    if "via_ddr_supply_lower_bank" in via:
        sheet, _, cpu = islands[1]
        contact = via["via_ddr_supply_lower_bank"]
        direct = squares(sheet, contact, cpu, pitch)
        row += f",{direct:.4f},{direct*.01724/.035:.4f}"
    print(row)
