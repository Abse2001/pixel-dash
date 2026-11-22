"""Bound the possible space for a non-DDR CPU escape before spending time on routing."""
import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
import runpy

from shapely.affinity import translate
from shapely.geometry import Point
from shapely.ops import unary_union


def screen(board, ram_y, pins, routed=False, cpu_only=False, corridors=False):
    copper = runpy.run_path(str(Path(__file__).with_name("audit-copper-contacts.py")))["copper"](board)
    elements = {e[e["type"] + "_id"]: e for e in board if e["type"] + "_id" in e}
    components = {e["name"]: e["source_component_id"] for e in board if e["type"] == "source_component"}
    pcb = {e["source_component_id"]: e["pcb_component_id"] for e in board if e["type"] == "pcb_component"}
    signals = {e["subcircuit_connectivity_map_key"] for e in board
               if e["type"] == "source_trace" and (e.get("name") or "").startswith("DDR_")}
    if len(signals) != 50:
        raise ValueError("Expected 50 distinct DDR signal nets")
    widths = [p["width"] for t in board if t["type"] == "pcb_trace"
              and elements.get(t.get("source_trace_id"), {}).get("subcircuit_connectivity_map_key") in signals
              for p in t["route"] if p.get("route_type") == "wire"]
    setback = 4 * max(widths)
    cpu_lands, ram_lands, escape_lands = [], [], {}
    for oid, net, shape in copper["top"]:
        item = elements[oid]
        if item["type"] != "pcb_smtpad":
            continue
        if item["pcb_component_id"] == pcb[components["U_DDR"]]:
            ram_lands.append(shape)
        elif item["pcb_component_id"] == pcb[components["U1"]]:
            if net in signals:
                cpu_lands.append(shape)
            source = elements[elements[item["pcb_port_id"]]["source_port_id"]]
            escape_lands[source["name"]] = shape
    cpu = unary_union(cpu_lands).convex_hull
    ram = unary_union(ram_lands).convex_hull
    if corridors:
        # Reserve a 0.102 mm wide ray launched wholly within each land. A separating
        # line perpendicular to the ray keeps the complete convex envelope
        # on the other side. Sample whole degrees; this is a candidate search.
        by_net = defaultdict(list)
        for layer in ("top", "bottom"):
            for oid, net, shape in copper[layer]:
                if net in signals and elements[oid]["type"] != "pcb_smtpad":
                    by_net[net].append(shape)
        names = {e["subcircuit_connectivity_map_key"]: e["name"] for e in board
                 if e["type"] == "source_trace" and e.get("name") and e["name"].startswith("DDR_")}
        vertices = {names[net]: unary_union(shapes).convex_hull.exterior.coords[:]
                    for net, shapes in by_net.items()}
        vertices["fixed"] = cpu.union(ram).convex_hull.exterior.coords[:]
        launches = {pin: escape_lands[pin].buffer(-0.051).exterior.coords[:] for pin in pins}
        # Include a separating plane normal at every launch vertex. A narrow
        # corridor between package lands can fall between two whole degrees.
        fixed = cpu.union(ram).convex_hull
        angles = set(range(360))
        for ring in launches.values():
            for x, y in ring:
                target = Point(x, y)
                nearest = fixed.exterior.interpolate(fixed.exterior.project(target))
                if not fixed.covers(target):
                    angles.add(math.degrees(math.atan2(y - nearest.y, x - nearest.x)) % 360)
        best = {}
        for angle in sorted(angles):
            dx, dy = math.cos(math.radians(angle)), math.sin(math.radians(angle))
            supports = {key: max(x*dx + y*dy for x, y in points) for key, points in vertices.items()}
            for pin in pins:
                x, y = max(launches[pin], key=lambda xy: xy[0]*dx + xy[1]*dy)
                limit = x*dx + y*dy - setback - 0.051
                if supports["fixed"] > limit:
                    continue
                offenders = sorted(key for key in vertices if supports[key] > limit)
                excess = sum(supports[key] - limit for key in offenders)
                candidate = len(offenders), excess, angle, x, y, offenders
                if pin not in best or candidate < best[pin]:
                    best[pin] = candidate
        print("ball,direction_degrees_from_positive_x,launch_x_mm,launch_y_mm,number_of_routes_to_move,interfering_routes")
        for pin in pins:
            if pin in best:
                count, _, angle, x, y, offenders = best[pin]
                print(f"{pin},{angle:.4f},{x:.5f},{y:.5f},{count},{' '.join(offenders)}")
            else:
                print(f"{pin},,,,,fixed lands block all sampled directions")
        return
    print("ram_delta_y_mm,ball,max_pad_edge_distance_mm,required_setback_mm,headroom_mm")
    if routed:
        saved = [shape for layer in ("top", "bottom") for oid, net, shape in copper[layer]
                 if net in signals or elements[oid].get("pcb_component_id") == pcb[components["U_DDR"]]]
        trials = [(0, unary_union(saved).convex_hull)]
    elif cpu_only:
        trials = [(0, cpu)]
    else:
        trials = [(dy, cpu.union(translate(ram, yoff=dy)).convex_hull) for dy in ram_y]
    for dy, hull in trials:
        for pin in pins:
            # Distance to a convex set is convex, so its maximum on a polygon is at a vertex.
            distance = max(hull.distance(Point(xy)) for xy in escape_lands[pin].exterior.coords)
            print(f"{dy:.3f},{pin},{distance:.4f},{setback:.4f},{distance-setback:.4f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("board", type=Path)
    parser.add_argument("--ram-dy", type=float, nargs="+", default=[0, .5, 1, 1.5])
    parser.add_argument("--balls", nargs="+", default=["R1", "B4", "B5", "C5", "C6"])
    geometry = parser.add_mutually_exclusive_group()
    geometry.add_argument("--corridors", action="store_true", help="find directional escape candidates and identify interfering DDR nets")
    geometry.add_argument("--cpu-only", action="store_true", help="test the fixed CPU DDR ball hull without RAM or routes")
    geometry.add_argument("--routed", action="store_true", help="bound escapes using both saved copper faces and the current RAM lands")
    args = parser.parse_args()
    screen(json.loads(args.board.read_text()), args.ram_dy, args.balls, args.routed, args.cpu_only, args.corridors)
