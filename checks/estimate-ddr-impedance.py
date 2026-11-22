"""Estimate long, uniform outer-layer DDR cross sections on the provisional JLC 1080 stack."""
import argparse
import json
import math
from pathlib import Path

import numpy as np
from hdi_build import LEGACY, WURTH
from scipy.sparse import diags
from scipy.sparse.linalg import spsolve


def capacitance(width, edge_gap, pitch, dielectric_height, dielectric_er, vacuum, stack=LEGACY):
    # Grid dimensions are millimetres. In a two-dimensional capacitance per
    # unit length, face width divided by cell spacing is dimensionless.
    x = np.arange(-round(1.1 / pitch), round(1.1 / pitch) + 1) * pitch
    y = np.arange(round(0.74 / pitch) + 1) * pitch
    xx, yy = np.meshgrid(x, y)
    ny, nx = xx.shape
    thickness = stack.foil
    trace_centers = [0.] if edge_gap is None else [-(edge_gap + width) / 2, (edge_gap + width) / 2]
    potential = np.zeros_like(xx)
    conductors = []
    mask = (yy >= dielectric_height) & (yy < dielectric_height + stack.mask)
    for index, center in enumerate(trace_centers):
        above_trace = abs(xx - center) < width / 2
        metal = above_trace & (yy >= dielectric_height) & (yy < dielectric_height + thickness)
        conductors.append(metal)
        potential[metal] = 1 if index == 0 else -1
        mask |= above_trace & (yy >= dielectric_height + thickness) & (yy < dielectric_height + thickness + (.01524 if stack == LEGACY else stack.mask))

    er = np.where(yy < dielectric_height, dielectric_er, np.where(mask, 3.8, 1.))
    if vacuum:
        er.fill(1.)
    # Harmonic mean of adjacent cells enforces normal displacement continuity.
    ex = 2 * er[:, :-1] * er[:, 1:] / (er[:, :-1] + er[:, 1:])
    ey = 2 * er[:-1] * er[1:] / (er[:-1] + er[1:])
    sx, sy = np.zeros_like(xx), np.zeros_like(xx)
    sx[:, :-1], sy[:-1] = ex, ey
    diagonal = sx + sy + np.roll(sx, 1, axis=1) + np.roll(sy, 1, axis=0)
    matrix = diags([diagonal.ravel(), -sx.ravel()[:-1], -sx.ravel()[:-1],
                    -sy.ravel()[:-nx], -sy.ravel()[:-nx]], [0, 1, -1, nx, -nx], format="csr")
    fixed = np.logical_or.reduce(conductors)
    fixed[[0, -1], :] = True
    fixed[:, [0, -1]] = True
    free = ~fixed.ravel()
    potential.ravel()[free] = spsolve(matrix[free][:, free], -(matrix @ potential.ravel())[free])
    positive = conductors[0].astype(int)
    charge = sum(np.sum(faces * np.diff(potential, axis=axis) * np.diff(positive, axis=axis))
                 for axis, faces in [(1, ex), (0, ey)])
    return charge * 8.8541878128e-12


def routed_width(board):
    names = {e["source_trace_id"]: e.get("name") for e in board if e["type"] == "source_trace"}
    routes = [e for e in board if e["type"] == "pcb_trace" and (names[e["source_trace_id"]] or "").startswith("DDR_")]
    if len(routes) != 50 or len({names[e["source_trace_id"]] for e in routes}) != 50:
        raise ValueError("Expected all 50 DDR signal routes")
    widths = {p["width"] for t in routes for p in t["route"] if p["route_type"] == "wire"}
    if len(widths) != 1 or min(widths) <= 0:
        raise ValueError(f"Calculate each distinct cross section separately: {widths}")
    return widths.pop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("circuit", type=Path)
    parser.add_argument("--mesh-mm", type=float, choices=[.002, .003], default=.002)
    parser.add_argument("--wurth", action="store_true", help="use the documented Würth 1-2b-1 cross section")
    parser.add_argument("--er", type=float, default=3.91, help="assumed prepreg dielectric constant")
    args = parser.parse_args()
    if not math.isfinite(args.er) or args.er <= 1:
        parser.error("Expected a finite dielectric constant above one")
    stack = WURTH if args.wurth else LEGACY
    width = routed_width(json.loads(args.circuit.read_text()))
    print(f"{stack.name}: dielectric {stack.prepreg:g} mm, assumed Er {args.er:g}, copper {stack.foil:g} mm.")
    print(f"Measured trace width {width:g} mm. Mesh {args.mesh_mm:g} mm. Ideal solid adjacent reference.")
    for gap, name in [(None, "Isolated"), (.18, "Odd mode, 0.18 mm pair edge gap")]:
        filled, air = [capacitance(width, gap, args.mesh_mm, stack.prepreg, args.er, vacuum, stack) for vacuum in (False, True)]
        impedance = (1 if gap is None else 2) / (299792458 * math.sqrt(filled * air))
        delay = math.sqrt(filled / air) / 299792458 * 1e9  # ps/mm
        print(f"{name}: {impedance:.2f} ohms, {delay:.3f} ps/mm.")
