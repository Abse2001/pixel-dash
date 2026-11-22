"""Apply the phased routes with their actual plated drill spans and plane reliefs."""
import json
import sys
from pathlib import Path

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

layers = ["top", "inner1", "inner2", "bottom"]
board = json.loads(Path(sys.argv[1]).read_bytes())
routes = json.loads(Path(sys.argv[3]).read_bytes())
cuts = {layer: [] for layer in layers}
ports = {e["source_port_id"]: e for e in board if e["type"] == "pcb_port" and e.get("source_port_id")}
sources = {e.get("name"): e for e in board if e["type"] == "source_trace"}
existing = {e["source_trace_id"] for e in board if e["type"] == "pcb_trace"}

for name, sections in routes.items():
    source = sources[name]
    source_id = source["source_trace_id"]
    if name.startswith("DDR_D") or source_id in existing:
        raise ValueError(f"Occupied route on {name}")
    route = []
    trace_id = "pcb_command_" + name
    key = source["subcircuit_connectivity_map_key"]
    for i, (layer_index, points) in enumerate(sections):
        layer = layers[layer_index]
        if i:
            previous, previous_points = sections[i - 1]
            if previous_points[-1] != points[0] or previous == layer_index:
                raise ValueError(f"Invalid transition on {name}")
            x, y = points[0]
            a, z = sorted([previous, layer_index])
            if z - a == 1:
                span = layers[a:z + 1]
                diameter, drill = (.36, .20) if a == 1 else (.28, .125)
            else:
                span, diameter, drill = layers, .30, .15
            board.append(dict(type="pcb_via", pcb_via_id=f"{trace_id}_via_{i}", pcb_trace_id=trace_id,
                              x=x, y=y, from_layer=span[0], to_layer=span[-1], layers=span,
                              outer_diameter=diameter, hole_diameter=drill, subcircuit_connectivity_map_key=key))
            route.append(dict(route_type="via", x=x, y=y, from_layer=layers[previous], to_layer=layer))
            for drilled_layer in span:
                cuts[drilled_layer].append(Point(x, y).buffer(diameter / 2 + .16, quad_segs=192))
        if len(points) > 1:
            cuts[layer].append(LineString(points).buffer(.051 + .16, quad_segs=96))
        route.extend(dict(route_type="wire", x=x, y=y, layer=layer, width=.102) for x, y in points)
    for end, field, source_port in zip((route[0], route[-1]), ("start_pcb_port_id", "end_pcb_port_id"),
                                       source["connected_source_port_ids"], strict=True):
        port = ports[source_port]
        if (end["x"], end["y"]) != (port["x"], port["y"]) or end["layer"] not in port["layers"]:
            raise ValueError(f"Missed terminal on {name}")
        end[field] = port["pcb_port_id"]
    board.append(dict(type="pcb_trace", pcb_trace_id=trace_id, source_trace_id=source_id,
                      subcircuit_connectivity_map_key=key, route=route))

def coordinates(ring):
    return [(p["x"], p["y"]) for p in ring["vertices"]]

def vertices(ring):
    return {"vertices": [dict(x=x, y=y) for x, y in list(ring.coords)[:-1]]}

for pour in board:
    if pour["type"] != "pcb_copper_pour":
        continue
    shape = pour["brep_shape"]
    original = Polygon(coordinates(shape["outer_ring"]), [coordinates(r) for r in shape["inner_rings"]])
    reliefs = unary_union(cuts[pour["layer"]])
    if original.intersects(reliefs):
        filled = original.difference(reliefs)
        if filled.geom_type != "Polygon":
            if filled.geom_type != "MultiPolygon":
                raise ValueError(f"Unexpected pour geometry on {pour['pcb_copper_pour_id']}")
            main, *islands = sorted(filled.geoms, key=lambda region: region.area, reverse=True)
            detached = unary_union(islands)
            lands = (Point(v["x"], v["y"]).buffer(v["outer_diameter"]/2) for v in board
                     if v["type"] == "pcb_via" and pour["layer"] in v["layers"])
            if detached.area > .01 or any(detached.intersects(land) for land in lands):
                raise ValueError(f"Plane split on {pour['pcb_copper_pour_id']}")
            filled = main
        pour["brep_shape"] = dict(outer_ring=vertices(filled.exterior), inner_rings=[vertices(r) for r in filled.interiors])
Path(sys.argv[2]).write_text(json.dumps(board, separators=(",", ":")))
