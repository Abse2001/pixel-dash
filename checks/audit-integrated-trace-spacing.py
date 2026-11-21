"""Measure trace-edge spacing where the CPU circuit meets retained handheld copper."""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

from shapely.geometry import LineString
from shapely.strtree import STRtree

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "production"))
from connectivity import trace_net_keys


def segments(trace):
    for a, b in zip(trace["route"], trace["route"][1:]):
        p, q = (a["x"], a["y"]), (b["x"], b["y"])
        layer = a.get("layer", a.get("to_layer"))
        if p == q or layer != b.get("layer", b.get("from_layer")):
            continue
        width = a.get("width", b.get("width"))
        if width is None:
            raise ValueError(f"Missing width on {trace['pcb_trace_id']}")
        yield layer, (LineString((p, q)), width / 2)


def audit(elements, limit):
    _, keys = trace_net_keys(elements)
    retained, channel = defaultdict(list), defaultdict(list)
    for trace in elements:
        if trace["type"] != "pcb_trace":
            continue
        trace_id = trace["pcb_trace_id"]
        group = channel if trace_id.startswith("channel_") else retained
        for layer, (line, radius) in segments(trace):
            group[layer].append((line, radius, trace_id, keys[trace["source_trace_id"]]))
    if not channel or not retained:
        raise ValueError("Expected a rendered, integrated handheld with both trace groups")
    findings = {}
    for layer in channel.keys() & retained.keys():
        other = retained[layer]
        tree = STRtree([item[0] for item in other])
        largest = max(item[1] for item in other)
        for line, radius, trace_id, net in channel[layer]:
            for index in tree.query(line, predicate="dwithin", distance=limit + radius + largest):
                ref, half_width, other_id, other_net = other[index]
                if net == other_net:
                    continue
                gap = line.distance(ref) - radius - half_width
                if gap < limit - 1e-8:
                    key = layer, trace_id, other_id
                    findings[key] = min(gap, findings.get(key, gap))
    return findings


if __name__ == "__main__":
    findings = audit(json.loads(Path(sys.argv[1]).read_text()), 0.102)
    writer = csv.writer(sys.stdout)
    writer.writerow(("layer", "channel_trace", "retained_trace", "edge_gap_mm"))
    for key, gap in sorted(findings.items(), key=lambda item: item[1]):
        writer.writerow((*key, f"{gap:.6f}"))
    print(f"{len(findings)} cross-design trace pairs below 0.102 mm", file=sys.stderr)
    sys.exit(bool(findings))
