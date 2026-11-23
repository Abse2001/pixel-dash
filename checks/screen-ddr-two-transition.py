"""Necessary-condition screen for an L1–L4–L1 data route within a planar length cap."""
import argparse
import csv
import json
import math
import runpy
import sys
from itertools import combinations, permutations, product
from pathlib import Path

from shapely import affinity, union_all
from shapely.geometry import Point

copper = runpy.run_path(str(Path(__file__).with_name("audit-copper-contacts.py")))["copper"]
SIGNAL_RADIUS = 0.051
VIA_RADIUS = 0.15
HOLE_RADIUS = 0.075
RELAXATION = 0.002


def budget_ellipse(start, end, limit):
    distance = math.dist(start, end)
    if distance > limit:
        return None
    # Circumscribe the analytic ellipse. Inscribing it could falsely reject a path on the boundary.
    a = (limit + 0.0001) / 2
    b = math.sqrt(a*a - distance*distance/4)
    circle = Point(0, 0).buffer(1/math.cos(math.pi/384), quad_segs=96)
    ellipse = affinity.scale(circle, a, b)
    angle = math.atan2(end[1]-start[1], end[0]-start[0])
    return affinity.translate(affinity.rotate(ellipse, angle, use_radians=True),
                              (start[0]+end[0])/2, (start[1]+end[1])/2)


def polygons(shape):
    if shape.geom_type == "Polygon":
        yield shape
    elif hasattr(shape, "geoms"):
        for part in shape.geoms:
            yield from polygons(part)


def landing_regions(board, bits, additionally_movable, limit):
    by_id = {e.get(e["type"] + "_id"): e for e in board}
    sources = {e["name"]: e for e in board if e["type"] == "source_trace" and e.get("name")}
    ports = {e["source_port_id"]: e for e in board if e["type"] == "pcb_port" and e.get("source_port_id")}
    moved = {sources[name]["subcircuit_connectivity_map_key"] for name in set(bits) | set(additionally_movable)}
    lands = {name: [ports[pid] for pid in sources[name]["connected_source_port_ids"]] for name in bits}
    endpoint_ids = {land["pcb_port_id"] for pair in lands.values() for land in pair}
    pads = {}
    obstacles = {"top": [], "bottom": [], "via": []}
    search_box = union_all([budget_ellipse((a["x"], a["y"]), (z["x"], z["y"]), limit)
                            for a, _ in lands.values() for _, z in lands.values()]).envelope.buffer(2)
    holes_seen = set()
    for layer, objects in copper(board).items():
        for oid, key, shape in objects:
            if not search_box.intersects(shape):
                continue
            part = by_id[oid]
            kind = part["type"]
            if kind == "pcb_copper_pour" or (key in moved and kind in ("pcb_trace", "pcb_via")):
                continue
            if part.get("pcb_port_id") in endpoint_ids:
                if layer == "top":
                    pads[part["pcb_port_id"]] = shape
                continue
            if layer in ("top", "bottom"):
                spacing = 0.1524 if kind == "pcb_via" else 0.102
                obstacles[layer].append(shape.buffer(SIGNAL_RADIUS + spacing - RELAXATION, quad_segs=16))
            spacing = 0.1524 if kind == "pcb_trace" else 0.102
            obstacles["via"].append(shape.buffer(VIA_RADIUS + spacing - RELAXATION, quad_segs=16))
            if kind == "pcb_via" and oid not in holes_seen:
                blind = len(part["layers"]) == 2 and bool(set(part["layers"]) & {"top", "bottom"})
                minimum = 0.24 if blind else 0.20
                radius = HOLE_RADIUS + part["hole_diameter"]/2 + minimum - RELAXATION
                obstacles["via"].append(Point(part["x"], part["y"]).buffer(radius, quad_segs=16))
                holes_seen.add(oid)
    if pads.keys() != endpoint_ids:
        raise ValueError("All studied signals must terminate at identified top-side lands")
    blocked = {layer: union_all(pieces) for layer, pieces in obstacles.items()}
    for cpu, ram in product(bits, repeat=2):
        a, z = lands[cpu][0], lands[ram][1]
        start, end = (a["x"], a["y"]), (z["x"], z["y"])
        ellipse = budget_ellipse(start, end, limit)
        first_regions, last_regions = [], []
        if ellipse is not None:
            unrelated = union_all([s for pid, s in pads.items() if pid not in (a["pcb_port_id"], z["pcb_port_id"])])
            top = list(polygons(ellipse.difference(blocked["top"]).difference(
                unrelated.buffer(SIGNAL_RADIUS + 0.102 - RELAXATION))))
            launch = next((r for r in top if r.covers(Point(start))), None)
            receive = next((r for r in top if r.covers(Point(end))), None)
            if launch is not None and receive is not None:
                land = ellipse.difference(blocked["via"]).difference(unrelated.buffer(VIA_RADIUS + 0.102 - RELAXATION))
                first = launch.intersection(land)
                last = receive.intersection(land)
                for c in polygons(ellipse.difference(blocked["bottom"])):
                    if c.intersects(first) and c.intersects(last):
                        first_regions.append(c.intersection(first))
                        last_regions.append(c.intersection(last))
        yield cpu, ram, union_all(first_regions), union_all(last_regions)


def run(board, bits, additionally_movable, limit):
    for cpu, ram, first, last in landing_regions(board, bits, additionally_movable, limit):
        yield cpu, ram, limit, "disconnected" if first.is_empty or last.is_empty else "survives"


def packing(board, bits, additionally_movable, limit):
    lands = {(i,j): (a,b) for i,j,a,b in landing_regions(board, bits, additionally_movable, limit)}
    required = 2*VIA_RADIUS + .102
    region_bounds = {key: [None if r.is_empty else r.bounds for r in ends] for key, ends in lands.items()}
    pair_limits = {}
    for i,j in combinations(lands, 2):
        if i[0] == j[0] or i[1] == j[1]:
            continue
        bounds = []
        for side, label in enumerate(("CPU", "RAM")):
            a,b = region_bounds[i][side], region_bounds[j][side]
            upper = 0.
            if a is not None and b is not None:
                # All attainable center distances are bounded above by the farthest box corners.
                ax,ay,az,aw = a
                bx,by,bz,bw = b
                upper = math.hypot(max(az-bx, bz-ax), max(aw-by, bw-ay))
            bounds.append((upper, label, i[0], j[0]))
        pair_limits[i,j] = pair_limits[j,i] = min(bounds)
    for ram_order in permutations(bits):
        assignment = zip(bits, ram_order)
        bounds = (pair_limits[i,j] for i,j in combinations(assignment, 2))
        upper, label, a, b = min(bounds)
        yield "/".join(ram_order), label, a, b, f"{upper:.6f}", f"{required:.6f}", "excluded" if upper < required else "unresolved"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("board", type=Path)
    parser.add_argument("--bits", nargs="+", required=True)
    parser.add_argument("--limit-mm", type=float, required=True)
    parser.add_argument("--also-move", nargs="*", default=[])
    parser.add_argument("--packing", action="store_true", help="Bound via spacing for simultaneous DQ assignments")
    args = parser.parse_args()
    if args.packing and len(args.bits) < 2:
        parser.error("Packing requires at least two data signals")
    if args.limit_mm <= 0 or len(set(args.bits)) != len(args.bits):
        parser.error("Supply a positive length cap and distinct data nets")
    if any(not n.startswith("DDR_D") or not n[5:].isdigit() for n in args.bits):
        parser.error("Use DDR_D0 through DDR_D15")
    nums = [int(n[5:]) for n in args.bits]
    if max(nums) > 15 or len({n//8 for n in nums}) != 1:
        parser.error("All proposed bit remaps must stay in the same byte")
    writer = csv.writer(sys.stdout)
    if args.packing:
        writer.writerow(("RAM_assignment","side","CPU_net_A","CPU_net_B","upper_center_spacing_mm","required_center_spacing_mm","result"))
        writer.writerows(packing(json.loads(args.board.read_text()), args.bits, args.also_move, args.limit_mm))
        sys.exit()
    writer.writerow(("cpu_net", "original_ram_net", "length_cap_mm", "relaxed_reachability"))
    writer.writerows(run(json.loads(args.board.read_text()), args.bits, args.also_move, args.limit_mm))
