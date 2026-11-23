"""Witness a path in drilled reference copper from a byte launch to its nominated bypass."""
import argparse
import contextlib
import csv
import json
import math
import re
import runpy
import sys
from pathlib import Path
from zipfile import ZipFile

import numpy as np
from shapely import get_parts, intersects_xy, prepare, union_all
from shapely.geometry import LineString, Point, Polygon, box
from skimage.graph import MCP_Geometric

from ddr_cam import artwork

HERE = Path(__file__).resolve().parent
LAYERS = ("top", "inner1", "inner2", "bottom")
REFERENCE = {"top": "GND", "bottom": "VDDS_DDR"}


def physical_sheet(board, archive, layer, rail, bounds):
    """Find the connected Gerber island after drilling, then clip to the search region."""
    nets = {e["source_net_id"]: e["name"] for e in board if e["type"] == "source_net"}
    pour, = [e for e in board if e["type"] == "pcb_copper_pour" and e["layer"] == layer
             and nets[e["source_net_id"]] == rail]
    rings = pour["brep_shape"]
    def vertices(r):
        return [(p["x"], p["y"]) for p in r["vertices"]]
    design = Polygon(vertices(rings["outer_ring"]), [vertices(r) for r in rings["inner_rings"]])
    drill = runpy.run_path(str(HERE / "audit-channel-drills.py"))
    holes = []
    with ZipFile(archive) as files:
        expected = drill["expected_drills"](board)
        if set(expected) != {n for n in files.namelist() if n.endswith(".drl")}:
            raise ValueError("Mismatched drill span files")
        for name, hits in expected.items():
            span = [int(v) for v in re.findall(r"L(\d+)", name)]
            if span and layer not in LAYERS[span[0] - 1:span[1]]:
                continue
            with contextlib.redirect_stdout(sys.stderr):
                drill["compare"](name, files.read(name).decode().splitlines(), hits.copy())
            for diameter, ends in hits:
                center = Point(ends[0]) if len(ends) == 1 else LineString(ends)
                holes.append(center.buffer(diameter / 2, quad_segs=64))
    member = {"inner1": "In1_Cu.gbr", "inner2": "In2_Cu.gbr"}[layer]
    sheet = artwork(archive, member).difference(union_all(holes))
    seed = design.intersection(bounds).difference(union_all(holes)).representative_point()
    island, = [s for s in get_parts(sheet) if s.covers(seed)]
    return island.intersection(bounds)


def sheet_grid(sheet, step):
    x0, y0, x1, y1 = sheet.bounds
    xs, ys = np.arange(x0, x1, step), np.arange(y0, y1, step)
    # Every point on a grid diagonal is within step/sqrt(2) of one of its endpoints.
    interior = sheet.buffer(-step / math.sqrt(2))
    prepare(interior)
    mask = intersects_xy(interior, xs[None, :], ys[:, None])
    return sheet, xs, ys, mask


def witness(start, via, grid):
    """Return the length of an explicitly covered polyline ending on a plated annulus."""
    sheet, xs, ys, mask = grid
    gx, gy = via["x"], via["y"]
    rr = (xs[None, :] - gx)**2 + (ys[:, None] - gy)**2
    annulus = (rr <= (via["outer_diameter"]/2)**2) & (rr >= (via["hole_diameter"]/2)**2)
    sources = list(zip(*np.nonzero(mask & annulus)))
    if not sources:
        raise ValueError("No sampled contact on the bypass via annulus")
    candidates = sorted((math.dist(start, (xs[j], ys[i])), (i, j))
                        for i, j in zip(*np.nonzero(mask & ((xs[None, :] - start[0])**2
                                                            + (ys[:, None] - start[1])**2 <= (.12)**2))))
    end = next((n for _, n in candidates if sheet.covers(LineString([start, (xs[n[1]], ys[n[0]])]))), None)
    if end is None:
        raise ValueError("Launch cannot reach the copper grid")
    solver = MCP_Geometric(np.where(mask, 1., np.inf))
    distances, _ = solver.find_costs(sources, ends=[end])
    if not np.isfinite(distances[end]):
        raise ValueError("No path in the local reference island")
    line = LineString([(xs[j], ys[i]) for i, j in solver.traceback(end)] + [start])
    if not sheet.covers(line):
        raise ValueError("Reconstructed path leaves the drilled reference copper")
    return line.length


def screen(board, grids, selected):
    model = runpy.run_path(str(HERE / "measure-ddr-return-paths.py"))
    names, caps = model["return_network"](board)
    choices = {(n, x, y): cap for n, x, y, cap, *_ in model["measurements"](board, selected, True)}
    vias = {(e["x"], e["y"], layer): e for e in board if e["type"] == "pcb_via" for layer in e["layers"]}
    layers = {"GND": "inner1", "VDDS_DDR": "inner2"}
    for trace in board:
        if trace["type"] != "pcb_trace" or names[trace["source_trace_id"]] not in selected:
            continue
        name = names[trace["source_trace_id"]]
        path = trace["route"]
        for i, p in enumerate(path):
            if p["route_type"] != "via":
                continue
            x, y = p["x"], p["y"]
            cap = choices[name, x, y]
            for direction, layer in [(-1, p["from_layer"]), (1, p["to_layer"])]:
                rail = REFERENCE[layer]
                inner = layers[rail]
                v = vias[x, y, inner]
                radius = v["outer_diameter"]/2 + .16
                points = [(x,y)]
                for point in (reversed(path[:i]) if direction < 0 else path[i+1:]):
                    points.append((point["x"], point["y"]))
                    if point["route_type"] == "via":
                        break
                line = LineString(points)
                # Use the actual signal tangent outside its antipad, with 60 µm
                # of radial clearance to make both grid resolutions comparable.
                outside = line.difference(Point(x, y).buffer(radius + .06, quad_segs=128))
                if outside.is_empty:
                    yield name, round(x, 6), round(y, 6), cap, inner, "", "segment ends within launch region"
                    continue
                start = list(get_parts(outside))[0].coords[0]
                target = caps[cap][rail][-1]
                terminal = vias[*target, inner]
                length = witness(start, terminal, grids[inner])
                yield name, round(x, 6), round(y, 6), cap, inner, round(length, 4), "covered path"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("board", type=Path)
    parser.add_argument("archive", type=Path)
    parser.add_argument("signals", nargs="+", choices=[f"DDR_D{i}" for i in range(16)]+[
        f"DDR_{t}{i}" for t in ("DQM","DQS","DQSn") for i in range(2)])
    parser.add_argument("--step-mm", type=float, choices=(.025, .05), default=.025)
    args = parser.parse_args()
    board = json.loads(args.board.read_bytes())
    bounds = box(-77, 2, -35, 30)
    grids = {layer: sheet_grid(physical_sheet(board, args.archive, layer, rail, bounds), args.step_mm)
              for layer, rail in (("inner1", "GND"), ("inner2", "VDDS_DDR"))}
    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow(("signal", "via_x_mm", "via_y_mm", "bypass", "plane", "witness_length_mm", "status"))
    writer.writerows(screen(board, grids, args.signals))
