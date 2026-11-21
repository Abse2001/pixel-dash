"""Measure same-layer pair proximity on planar copper, including BGA escapes."""
import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

from shapely.geometry import LineString
from shapely.ops import unary_union

PAIRS = (("DDR_CK", "DDR_CKn"), ("DDR_DQS0", "DDR_DQSn0"), ("DDR_DQS1", "DDR_DQSn1"))


def pair_segments(elements):
    names = {e["source_trace_id"]: e.get("name") for e in elements if e["type"] == "source_trace"}
    wanted = {name for pair in PAIRS for name in pair}
    segments = {}
    for trace in elements:
        if trace["type"] != "pcb_trace":
            continue
        name = names[trace["source_trace_id"]]
        if name not in wanted:
            continue
        if name in segments:
            raise ValueError(f"Multiple routed traces for {name}")
        layers = defaultdict(list)
        for a, b in zip(trace["route"], trace["route"][1:]):
            start, end = (a["x"], a["y"]), (b["x"], b["y"])
            if start == end:
                continue
            layer = a.get("layer", a.get("to_layer"))
            if layer != b.get("layer", b.get("from_layer")):
                raise ValueError(f"Planar segment changes layer on {name}")
            layers[layer].append(LineString((start, end)))
        if not layers:
            raise ValueError(f"Empty route for {name}")
        segments[name] = layers
    if wanted != segments.keys():
        raise ValueError(f"Missing pair conductors {sorted(wanted - segments.keys())}")
    return segments


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("circuit", type=Path)
    parser.add_argument("--center-distance-mm", type=float, required=True)
    args = parser.parse_args()
    if args.center_distance_mm <= 0:
        parser.error("Center distance must be positive")
    routes = pair_segments(json.loads(args.circuit.read_text()))
    writer = csv.writer(sys.stdout)
    writer.writerow(("signal", "mate", "layer", "center_distance_mm", "planar_mm", "within_mm", "outside_mm"))
    for p, n in PAIRS:
        for name, mate in ((p, n), (n, p)):
            for layer, segments in sorted(routes[name].items()):
                envelope = unary_union(routes[mate].get(layer, [])).buffer(args.center_distance_mm, quad_segs=32)
                total = sum(segment.length for segment in segments)
                near = sum(segment.intersection(envelope).length for segment in segments)
                writer.writerow((name, mate, layer, args.center_distance_mm, f"{total:.4f}",
                                 f"{near:.4f}", f"{total - near:.4f}"))


if __name__ == "__main__":
    main()
