"""Screen routed outer-layer DDR centerlines against finished reference-plane polygons."""
import argparse
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


def audit(board, microsd=False, full_width=False, raster=False, archive=None):
    nets = {e["source_net_id"]: e["name"] for e in board if e["type"] == "source_net"}
    names = {e["source_trace_id"]: e.get("name", "") for e in board if e["type"] == "source_trace"}
    ref = {"top": ("inner1", "GND"), "bottom": ("inner2", "GND" if microsd or raster else "VDDS_DDR")}
    if raster:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "production"))
        from connectivity import trace_net_keys
        _, keys = trace_net_keys(board)
        panel = {key: source for source, key in keys.items() if source.startswith("system_LCD_")}
        raster_sources = {source: panel[key] for source, key in keys.items() if key in panel}
        ref.update(inner1=("inner2", "GND"), inner2=("inner1", "GND"))
    pours = [e for e in board if e["type"] == "pcb_copper_pour"]
    vias = {xy(e): e for e in board if e["type"] == "pcb_via"}
    planes = {}
    # ReferencePlanes sets both pour clearances to 0.16 mm. The rendered BREP omits that field.
    launch_clearance = 0.16
    for layer, (inner, net) in ref.items():
        matches = [p for p in pours if p["layer"] == inner and nets[p["source_net_id"]] == net]
        if len(matches) != 1:
            raise ValueError(f"Expected one finished {inner} {net} pour, found {len(matches)}")
        plane = polygon(matches[0])
        if archive:
            from ddr_cam import reference
            member = {"inner1": "In1_Cu.gbr", "inner2": "In2_Cu.gbr"}[inner]
            plane = reference(archive, member, plane.representative_point())
        planes[layer] = plane
    seen = set()
    for trace in board:
        if trace["type"] != "pcb_trace":
            continue
        name = names[trace["source_trace_id"]]
        if raster:
            name = raster_sources.get(trace["source_trace_id"])
            if name is None:
                continue
        elif microsd:
            name = trace["source_trace_id"]
            if not name.startswith("system_SD_"):
                continue
        elif not name.startswith("DDR_"):
            continue
        seen.add(name)
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

    if not microsd and not raster and len(seen) != 50:
        raise ValueError(f"Expected 50 routed DDR signals, found {len(seen)}")
    if raster and not seen:
        raise ValueError("The assembled board contains no routed raster signals")
    if raster:
        print(f"Screened {len(seen)} routed raster signals.", file=sys.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("circuit", type=Path)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--micro-sd", action="store_true")
    group.add_argument("--raster", action="store_true")
    parser.add_argument("--full-width", action="store_true")
    parser.add_argument("--gerbers", type=Path, help="Check the connected reference copper reconstructed from the manufacturing archive")
    args = parser.parse_args()
    full_width = args.full_width
    failures = sorted(audit(json.loads(args.circuit.read_text()), args.micro_sd, full_width, args.raster, args.gerbers))
    out = csv.writer(sys.stdout)
    out.writerow(("signal", "signal_layer", "reference_layer", "uncovered_copper_mm2" if full_width else "uncovered_centerline_mm"))
    for name, layer, ref, length in failures:
        out.writerow((name, layer, ref, f"{length:.7f}" if full_width else f"{length:.4f}"))
    print(f"{len(failures)} signal/layer reference-coverage findings", file=sys.stderr)
    sys.exit(bool(failures))
