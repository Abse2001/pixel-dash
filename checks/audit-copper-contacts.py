"""Independently intersect the filled copper on each layer of the integrated handheld."""
import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union
from shapely.strtree import STRtree

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "production"))
from connectivity import trace_net_keys


def xy(p):
    return p["x"], p["y"]


def pad_shape(p):
    shape = p.get("pad_shape", p.get("shape"))
    if shape == "polygon":
        return Polygon([xy(vertex) for vertex in p["points"]])
    center = xy(p)
    if shape == "circle":
        radius = p["radius"] if "radius" in p else p["outer_diameter"] / 2
        return Point(center).buffer(radius, quad_segs=64)
    w = p["width"] if "width" in p else p["outer_width"]
    h = p["height"] if "height" in p else p["outer_height"]
    if shape in ("rect", "rotated_rect"):
        land = box(-w/2, -h/2, w/2, h/2)
    elif shape in ("pill", "rotated_pill"):
        dx, dy = max(w-h, 0)/2, max(h-w, 0)/2
        land = LineString([(-dx, -dy), (dx, dy)]).buffer(min(w, h)/2, quad_segs=64)
    else:
        raise ValueError(f"Unsupported land shape {shape}")
    angle = p.get("rect_ccw_rotation", p.get("ccw_rotation", 0))
    return affinity.translate(affinity.rotate(land, angle, origin=(0, 0)), *center)


def copper(elements):
    by_id = {e[e["type"]+"_id"]: e for e in elements if e["type"]+"_id" in e}
    traces, keys = trace_net_keys(elements)
    port_nets = {}
    for trace_id, trace in traces.items():
        for source_port_id in trace["connected_source_port_ids"]:
            net = keys[trace_id]
            if port_nets.setdefault(source_port_id, net) != net:
                raise ValueError(f"Conflicting schematic nets for {source_port_id}")
    result = defaultdict(list)

    def add(layer, element_id, key, shape):
        if shape.is_empty or not shape.is_valid:
            raise ValueError(f"Invalid copper geometry on {element_id}")
        result[layer].append((element_id, key, shape))

    for e in elements:
        kind = e["type"]
        if kind == "pcb_trace":
            strokes = defaultdict(list)
            for a, b in zip(e["route"], e["route"][1:]):
                if xy(a) == xy(b):
                    continue
                layer = a.get("layer", a.get("to_layer"))
                if layer != b.get("layer", b.get("from_layer")):
                    raise ValueError(f"Ambiguous segment layer in {e['pcb_trace_id']}")
                width = a["width"] if "width" in a else b["width"]
                strokes[layer].append(LineString([xy(a), xy(b)]).buffer(width/2, quad_segs=64))
            for layer, pieces in strokes.items():
                add(layer, e["pcb_trace_id"], keys[e["source_trace_id"]], unary_union(pieces))
        elif kind in ("pcb_smtpad", "pcb_plated_hole", "pcb_via"):
            element_id = e[kind+"_id"]
            port = by_id.get(e.get("pcb_port_id"), {})
            source = by_id.get(port.get("source_port_id"), {})
            trace = by_id.get(e.get("pcb_trace_id"), {})
            key = (e.get("subcircuit_connectivity_map_key") or source.get("subcircuit_connectivity_map_key")
                   or port_nets.get(source.get("source_port_id"))
                   or keys.get(e.get("source_trace_id", trace.get("source_trace_id"))))
            # An unconnected land remains conductive and must be tested against every other net.
            key = key or port.get("pcb_port_id") or element_id
            shape = Point(xy(e)).buffer(e["outer_diameter"]/2, quad_segs=64) if kind == "pcb_via" else pad_shape(e)
            for layer in ([e["layer"]] if kind == "pcb_smtpad" else e["layers"]):
                add(layer, element_id, key, shape)
        elif kind == "pcb_copper_pour":
            rings = e["brep_shape"]
            outer, *holes = [[xy(p) for p in r["vertices"]] for r in [rings["outer_ring"], *rings["inner_rings"]]]
            add(e["layer"], e["pcb_copper_pour_id"], by_id[e["source_net_id"]]["subcircuit_connectivity_map_key"],
                Polygon(outer, holes))
        elif kind.startswith("pcb_copper_"):
            raise ValueError(f"Unhandled copper primitive {kind}")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("circuit", type=Path)
    parser.add_argument("--clearance-mm", type=float, help="Report unrelated copper closer than this distance")
    args = parser.parse_args()
    if args.clearance_mm is not None and not (math.isfinite(args.clearance_mm) and args.clearance_mm > 0):
        parser.error("Clearance must be finite and positive")
    limit = args.clearance_mm if args.clearance_mm is not None else 0.0001
    layers = copper(json.loads(args.circuit.read_text()))
    failures = []
    for layer, items in layers.items():
        shapes = [s for _, _, s in items]
        tree = STRtree(shapes)
        for i, (element, key, shape) in enumerate(items):
            # 0.0001 mm covers polygon approximation at rounded lands and trace caps.
            for j in tree.query(shape, predicate="dwithin", distance=limit):
                if j <= i or items[j][1] == key:
                    continue
                gap = shape.distance(shapes[j])
                if args.clearance_mm is not None and gap >= limit - 1e-8:
                    continue
                failures.append((layer, element, items[j][0], round(gap, 7)))
    writer = csv.writer(sys.stdout)
    writer.writerow(("layer", "copper_a", "copper_b", "copper_gap_mm"))
    writer.writerows(sorted(failures))
    if args.clearance_mm is None:
        print(f"{len(failures)} unrelated copper contacts or gaps within 0.0001 mm", file=sys.stderr)
    else:
        print(f"{len(failures)} unrelated copper pairs below {limit:g} mm", file=sys.stderr)
    sys.exit(bool(failures))


if __name__ == "__main__":
    main()
