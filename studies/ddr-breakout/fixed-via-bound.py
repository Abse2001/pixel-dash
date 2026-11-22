"""Compute relaxed planar length bounds for byte-1 routes at fixed via sites."""
import argparse
import heapq
import itertools
import json
import math

from shapely import get_parts
from shapely.geometry import LineString, Point
from shapely.ops import unary_union


def read_routes(board):
    names = {s["source_trace_id"]: s.get("name", "") for s in board
             if s["type"] == "source_trace"}
    keys = {s["subcircuit_connectivity_map_key"] for s in board
            if s["type"] == "source_trace" and names[s["source_trace_id"]].startswith("DDR_")}
    for via in board:
        if via["type"] == "pcb_via" and via.get("subcircuit_connectivity_map_key") in keys:
            assert via["outer_diameter"] >= 0.30 and len(via["layers"]) == 4
    routes = {}
    for trace in board:
        if trace["type"] != "pcb_trace":
            continue
        name = names.get(trace.get("source_trace_id"), "")
        if not name.startswith("DDR_"):
            continue
        sections = [[]]
        for point in trace["route"]:
            xy = point["x"], point["y"]
            if not sections[-1] or sections[-1][-1] != xy:
                sections[-1].append(xy)
            if point["route_type"] == "via":
                sections.append([xy])
            elif point["route_type"] == "wire":
                assert point["width"] >= 0.102
                assert point["layer"] == ("top", "bottom")[(len(sections) - 1) % 2]
        assert name not in routes
        routes[name] = sections
    assert len(routes) == 50
    return routes


def obstacles(routes, excluded, side):
    polygons = []
    for name, sections in routes.items():
        if name in excluded:
            continue
        for section in sections[side::2]:
            for a, b in zip(section, section[1:]):
                # Inscribed octagons deliberately relax the real clearances.
                polygons.append(LineString([a, b]).buffer(0.2035, quad_segs=2))
        for section in sections[:-1]:
            polygons.append(Point(section[-1]).buffer(0.352, quad_segs=2))
    return polygons


def shortest_path(start, end, polygons):
    vertices = [start, end]
    region = unary_union(polygons)
    for polygon in get_parts(region):
        for ring in [polygon.exterior, *polygon.interiors]:
            vertices.extend(ring.coords[:-1])
    vertices = list(dict.fromkeys(vertices))
    edges = [[] for _ in vertices]
    for i, j in itertools.combinations(range(len(vertices)), 2):
        line = LineString([vertices[i], vertices[j]])
        if line.relate_pattern(region, "T********"):
            continue
        length = line.length
        edges[i].append((j, length))
        edges[j].append((i, length))
    best = {0: 0}
    previous = {}
    queue = [(0, 0)]
    while queue:
        distance, vertex = heapq.heappop(queue)
        if vertex == 1:
            path = [end]
            while vertex:
                vertex = previous[vertex]
                path.append(vertices[vertex])
            return LineString(path[::-1])
        if distance != best[vertex]:
            continue
        for neighbor, length in edges[vertex]:
            cost = distance + length
            if cost < best.get(neighbor, math.inf):
                best[neighbor] = cost
                previous[neighbor] = vertex
                heapq.heappush(queue, (cost, neighbor))
    raise ValueError("An endpoint is enclosed by an inflated obstacle")


def section_bound(start, end, polygons):
    path = LineString([start, end])
    active = set()
    while True:
        hits = {i for i, poly in enumerate(polygons) if i not in active
                and path.relate_pattern(poly, "T********")}
        if not hits:
            return path.length
        active.update(hits)
        path = shortest_path(start, end, [polygons[i] for i in sorted(active)])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("circuit_json")
    parser.add_argument("signal", choices=["DDR_D12", "DDR_D14"])
    parser.add_argument("--lift", nargs="*", default=[])
    args = parser.parse_args()
    with open(args.circuit_json) as source:
        routes = read_routes(json.load(source))
    sections = routes[args.signal]
    bounds = []
    for index, section in enumerate(sections):
        polygons = obstacles(routes, {args.signal, *args.lift}, index % 2)
        bounds.append(section_bound(section[0], section[-1], polygons))
    print(f"{args.signal} section bounds (mm):", *(f"{value:.5f}" for value in bounds))
    print(f"Total lower bound: {sum(bounds):.5f} mm")
