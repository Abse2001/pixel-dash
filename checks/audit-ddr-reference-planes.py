"""Screen routed outer-layer DDR centerlines against finished reference-plane polygons."""
import csv
import json
import sys
from pathlib import Path

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import substring, unary_union


def xy(point):
    return point["x"], point["y"]


def polygon(pour):
    shape = pour["brep_shape"]
    rings = [shape["outer_ring"], *shape["inner_rings"]]
    outer, *holes = [[xy(p) for p in ring["vertices"]] for ring in rings]
    return Polygon(outer, holes)


def audit(board, microsd=False, full_width=False):
    nets = {e["source_net_id"]: e["name"] for e in board if e["type"] == "source_net"}
    names = {e["source_trace_id"]: e.get("name", "") for e in board if e["type"] == "source_trace"}
    ref = {"top": ("inner1", "GND"), "bottom": ("inner2", "GND" if microsd else "VDDS_DDR")}
    pours = [e for e in board if e["type"] == "pcb_copper_pour"]
    vias = {xy(e): e for e in board if e["type"] == "pcb_via"}
    planes = {}
    # ReferencePlanes sets both pour clearances to 0.16 mm. The rendered BREP omits that field.
    launch_clearance = 0.16
    for layer, (inner, net) in ref.items():
        matches = [p for p in pours if p["layer"] == inner and nets[p["source_net_id"]] == net]
        if len(matches) != 1:
            raise ValueError(f"Expected one finished {inner} {net} pour, found {len(matches)}")
        planes[layer] = polygon(matches[0])
    for trace in board:
        if trace["type"] != "pcb_trace":
            continue
        name = names[trace["source_trace_id"]]
        if microsd:
            if not trace["source_trace_id"].startswith("system_SD_"):
                continue
        elif not name.startswith("DDR_"):
            continue
        gaps_by_layer = {layer: [] for layer in ref}
        section = [trace["route"][0]]
        for end in trace["route"][1:]:
            section.append(end)
            if end["route_type"] != "via" and end is not trace["route"][-1]:
                continue
            start = section[0]
            layer = start.get("layer", start.get("to_layer"))
            if layer not in ref or any(p.get("layer", layer) != layer for p in section):
                raise ValueError(f"Unsupported trace span on {name}")
            line = LineString([xy(p) for p in section])
            # Exclude the nominal antipad radius along the route at each transition.
            # Measure from the transition even when a short wire segment follows it.
            def launch_length(point):
                if point["route_type"] != "via":
                    return 0
                return vias[xy(point)]["outer_diameter"] / 2 + launch_clearance

            first, last = launch_length(start), line.length - launch_length(end)
            if full_width:
                strokes = []
                for a, b in zip(section, section[1:]):
                    if xy(a) != xy(b):
                        width = a["width"] if "width" in a else b["width"]
                        strokes.append(LineString([xy(a), xy(b)]).buffer(width/2, quad_segs=64))
                # Only the antipads of this section's plated transitions are exempt.
                copper = unary_union(strokes)
                for point in (start, end):
                    radius = launch_length(point)
                    if radius:
                        copper = copper.difference(Point(xy(point)).buffer(radius, quad_segs=128))
                uncovered = copper.difference(planes[layer])
                if uncovered.area > 1e-6:
                    gaps_by_layer[layer].append(uncovered)
            elif first < last:
                uncovered = substring(line, first, last).difference(planes[layer])
                if uncovered.length > 0.001:
                    gaps_by_layer[layer].append(uncovered)
            section = [end]
        for layer, gaps in gaps_by_layer.items():
            if gaps:
                combined = unary_union(gaps)
                yield name, layer, ref[layer][0], combined.area if full_width else combined.length


if __name__ == "__main__":
    full_width = "--full-width" in sys.argv[2:]
    failures = sorted(audit(json.loads(Path(sys.argv[1]).read_text()), "--micro-sd" in sys.argv[2:], full_width))
    out = csv.writer(sys.stdout)
    out.writerow(("signal", "signal_layer", "reference_layer", "uncovered_copper_mm2" if full_width else "uncovered_centerline_mm"))
    for name, layer, ref, length in failures:
        out.writerow((name, layer, ref, f"{length:.7f}" if full_width else f"{length:.4f}"))
    print(f"{len(failures)} signal/layer reference-coverage findings", file=sys.stderr)
    sys.exit(bool(failures))
