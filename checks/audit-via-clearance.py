"""Audit via copper edges to unrelated trace copper (mm), using Shapely 2."""
import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

from shapely.geometry import LineString, Point
from shapely.strtree import STRtree


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "production"))
from connectivity import trace_net_keys


def audit(elements):
    sources, keys = trace_net_keys(elements)

    layers = defaultdict(list)
    inline_nets = defaultdict(set)
    for t in elements:
        if t["type"] != "pcb_trace":
            continue
        key = keys[t["source_trace_id"]]
        for p in t["route"]:
            if p["route_type"] == "via":
                inline_nets[p["x"], p["y"]].add(key)
        for a, b in zip(t["route"], t["route"][1:]):
            layer = a.get("layer", a.get("to_layer"))
            if layer != b.get("layer", b.get("from_layer")):
                continue
            p, q = (a["x"], a["y"]), (b["x"], b["y"])
            if p == q:
                continue
            width = a.get("width", b.get("width"))
            if width is None:
                raise ValueError(f"Missing trace width on {t['pcb_trace_id']}")
            name = sources[t["source_trace_id"]].get("name") or sources[t["source_trace_id"]].get("display_name")
            layers[layer].append((LineString([p, q]), key, name, width / 2))

    trees = {l: STRtree([s[0] for s in segments]) for l, segments in layers.items()}
    half_width = {l: max(s[3] for s in segments) for l, segments in layers.items()}
    results = {}
    for v in elements:
        if v["type"] != "pcb_via":
            continue
        point = Point(v["x"], v["y"])
        key = v.get("subcircuit_connectivity_map_key") or keys.get(v.get("source_trace_id"))
        if not key:
            matches = inline_nets[v["x"], v["y"]]
            if len(matches) != 1:
                raise ValueError(f"Unresolved via net for {v['pcb_via_id']}")
            key = next(iter(matches))
        radius = v["outer_diameter"] / 2
        for layer in v["layers"]:
            if layer not in trees:
                continue
            reach = radius + 0.1524 + half_width[layer]
            for i in trees[layer].query(point, predicate="dwithin", distance=reach):
                segment, other_key, name, trace_radius = layers[layer][i]
                if other_key == key:
                    continue
                gap = point.distance(segment) - radius - trace_radius
                if gap >= 0.1524 - 1e-8:
                    continue
                pair = (v["pcb_via_id"], layer, other_key)
                if pair not in results or gap < results[pair][0]:
                    results[pair] = (gap, v["x"], v["y"], name)
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("circuit", type=Path)
    args = parser.parse_args()
    failures = audit(json.loads(args.circuit.read_text()))
    writer = csv.writer(sys.stdout)
    writer.writerow(("via", "layer", "unrelated_net", "edge_gap_mm", "via_x_mm", "via_y_mm", "trace"))
    for pair, (gap, x, y, name) in sorted(failures.items(), key=lambda row: row[1][0]):
        writer.writerow((*pair, f"{gap:.7f}", x, y, name))
    print(f"{len(failures)} via/layer/unrelated-net pairs below 0.1524 mm", file=sys.stderr)
    sys.exit(bool(failures))
