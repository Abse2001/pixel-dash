"""Verify every DDR signal stroke against its manufacturing-layer Gerber draw."""
import argparse
import json
import re
from collections import Counter
from itertools import product
from pathlib import Path
from zipfile import ZipFile


def segment(a, b, width):
    return (*sorted((a, b)), width)


def draws(data):
    if "%FSLAX46Y46*%" not in data or "%MOMM*%" not in data:
        raise ValueError("Unsupported Gerber format or units")
    circles = {}
    result = Counter()
    point = aperture = None
    dark = True
    region = False
    for row in data.splitlines():
        if match := re.fullmatch(r"%ADD(\d+)C,([\d.]+)\*%", row):
            circles[match[1]] = round(float(match[2]) * 1e6)
        elif match := re.fullmatch(r"D(\d+)\*", row):
            aperture = match[1]
        elif row in ("%LPC*%", "%LPD*%"):
            dark = row == "%LPD*%"
        elif row in ("G36*", "G37*"):
            region = row == "G36*"
        elif match := re.fullmatch(r"X(-?\d+)Y(-?\d+)D(0[123])\*", row):
            end = (int(match[1]), int(match[2]))
            if match[3] == "01" and point != end and dark and not region and aperture in circles:
                result[segment(point, end, circles[aperture])] += 1
            point = end
    return result


def gerber_point(vertex):
    return tuple(round(vertex[key] * 1e6) for key in ("x", "y"))


def main():
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("circuit", type=Path)
    args.add_argument("archive", type=Path)
    files = args.parse_args()
    board = json.loads(files.circuit.read_text())
    names = {e["source_trace_id"]: e.get("name") or "" for e in board if e["type"] == "source_trace"}
    with ZipFile(files.archive) as archive:
        layers = {layer: draws(archive.read(member).decode()) for layer, member in
                  (("top", "F_Cu.gbr"), ("bottom", "B_Cu.gbr"))}
    tested = Counter()
    for trace in board:
        if trace["type"] != "pcb_trace":
            continue
        name = names[trace["source_trace_id"]]
        if not name.startswith("DDR_"):
            continue
        for a, b in zip(trace["route"], trace["route"][1:]):
            p, q = gerber_point(a), gerber_point(b)
            if p == q:
                continue
            layer = a.get("layer", a.get("to_layer"))
            width = a["width"] if "width" in a else b["width"]
            key = segment(p, q, round(width * 1e6))
            if layer not in layers or layer != b.get("layer", b.get("from_layer")):
                raise ValueError(f"Invalid DDR stroke layer on {name}")
            # The exporter rounds half-grid ties differently. One Gerber unit is 1 nm.
            if layers[layer][key] < 1:
                for ax, ay, bx, by in product((-1, 0, 1), repeat=4):
                    nearby = segment((p[0]+ax, p[1]+ay), (q[0]+bx, q[1]+by), key[2])
                    if layers[layer][nearby]:
                        key = nearby
                        break
            if layers[layer][key] < 1:
                raise ValueError(f"Missing {name} stroke on {layer} at {p} to {q}, width {width} mm")
            layers[layer][key] -= 1
            tested[name] += 1
    if len(tested) != 50:
        raise ValueError(f"Expected 50 exported DDR signals, found {len(tested)}")
    print(f"Verified {sum(tested.values())} DDR strokes on {len(tested)} signals against Gerber coordinates and widths.")


if __name__ == "__main__":
    main()
