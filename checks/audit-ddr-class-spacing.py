"""Measure same-layer DDR spacing against TI AM335x Tables 7-68 and 7-69."""
import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from shapely import STRtree
from shapely.geometry import LineString


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "production"))
from connectivity import trace_net_keys


def net_class(name):
    if name in ("DDR_CK", "DDR_CKn"):
        return "CK"
    if match := re.fullmatch(r"DDR_DQSn?([01])", name):
        return "DQS" + match[1]
    if match := re.fullmatch(r"DDR_DQM([01])", name):
        return "DQ" + match[1]
    if match := re.fullmatch(r"DDR_D(\d+)", name):
        return "DQ" + str(int(match[1]) // 8)
    if re.fullmatch(r"DDR_(A\d+|BA[012]|CKE|CSn0|RASn|CASn|WEn|ODT)", name):
        return "ADDR_CTRL"
    return ""


def covered_length(line, intersections):
    # Normalize to distances on the measured segment. Floating-point overlays
    # can represent coincident portions as slightly different parallel lines.
    intervals = []
    for shape in intersections:
        if shape.geom_type != "LineString" or shape.is_empty:
            continue
        a, b = shape.boundary.geoms
        intervals.append(sorted((line.project(a), line.project(b))))
    end = total = 0.0
    for a, b in sorted(intervals):
        total += max(0, b - max(a, end))
        end = max(b, end)
    return total


def main(board, study_open=()):
    traces, keys = trace_net_keys(board)
    sections = defaultdict(list)
    for trace in board:
        if trace["type"] != "pcb_trace":
            continue
        sid = trace["source_trace_id"]
        name = traces[sid].get("name") or ""
        for a, b in zip(trace["route"], trace["route"][1:]):
            p, q = [(v["x"], v["y"]) for v in (a, b)]
            if p == q:
                continue
            layer = a.get("layer", a.get("to_layer"))
            if layer != b.get("layer", b.get("from_layer")):
                raise ValueError(f"Ambiguous segment layer on {sid}")
            sections[layer].append((name, keys[sid], net_class(name), LineString((p, q)),
                                    a["width"] if "width" in a else b["width"]))
    restricted = defaultdict(float)
    below_minimum = defaultdict(float)
    for items in sections.values():
        tree = STRtree([s[3] for s in items])
        for name, key, group, line, width in items:
            if not group:
                continue
            relaxed = []
            below = []
            for j in tree.query(line, predicate="dwithin", distance=4 * width):
                other, other_key, peer, seg, _ = items[j]
                if key == other_key:
                    continue
                if group.startswith(("CK", "DQS")):
                    if peer == group:  # The differential mate uses the impedance-derived pair spacing.
                        continue
                    limit = 4 * width
                else:
                    if not peer and other != "DDR_RESETn":
                        continue
                    limit = (3 if group == peer else 4) * width
                if line.distance(seg) < limit - 1e-7:
                    relaxed.append(line.intersection(seg.buffer(limit, quad_segs=32)))
                if line.distance(seg) < width - 1e-7:
                    below.append(line.intersection(seg.buffer(width, quad_segs=32)))
            restricted[name] += covered_length(line, relaxed)
            below_minimum[name] += covered_length(line, below)
    declared = {t["name"] for t in board if t["type"] == "source_trace" and net_class(t.get("name") or "")}
    if len(declared) != 49 or declared - restricted.keys() != set(study_open):
        raise ValueError(f"Expected 49 signals subject to the class spacing tables, found {len(restricted)}")
    out = csv.writer(sys.stdout)
    out.writerow(("signal", "below_nominal_mm", "below_1w_mm"))
    for name in sorted(restricted):
        out.writerow((name, f"{restricted[name]:.4f}", f"{below_minimum[name]:.4f}"))
    worst = max(restricted, key=restricted.get)
    print(f"Longest cumulative below-nominal run is {restricted[worst]:.3f} mm on {worst}; "
          f"TI allowance 31.750 mm.", file=sys.stderr)
    return any(x > 31.75001 for x in restricted.values()) or any(x > 1e-6 for x in below_minimum.values())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("circuit", type=Path)
    parser.add_argument("--study-open", nargs="+", default=[], help="Exact missing class-checked DDR signals on a partial board")
    args = parser.parse_args()
    sys.exit(main(json.loads(args.circuit.read_text()), args.study_open))
