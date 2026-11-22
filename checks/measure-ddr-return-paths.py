"""Measure how far each DDR layer transition is from both vias of one high-speed bypass."""
import argparse
import csv
import json
import math
import sys
from pathlib import Path


def xy(item):
    return item["x"], item["y"]


def measurements(board, selected=()):
    parts = {e["source_component_id"]: e for e in board if e["type"] == "source_component"}
    nets = {e["source_net_id"]: e["name"] for e in board if e["type"] == "source_net"}
    ports = {e["source_port_id"]: e for e in board if e["type"] == "source_port"}
    lands = {e["source_port_id"]: e for e in board if e["type"] == "pcb_port"}
    vias = {p: e for e in board if e["type"] == "pcb_via" for p in e.get("pcb_port_ids", [])}
    via_at = {(xy(v), layer, v.get("source_net_id")): v
              for v in board if v["type"] == "pcb_via" for layer in v["layers"]}
    inner_links = {}
    for trace in board:
        if trace["type"] != "pcb_trace" or not trace["route"]:
            continue
        route = trace["route"]
        layer = route[0].get("layer")
        if layer not in {"inner1", "inner2"} or any(
            p["route_type"] != "wire" or p["layer"] != layer for p in route
        ):
            continue
        for start, end in ((route[0], route[-1]), (route[-1], route[0])):
            inner_links.setdefault((xy(start), layer), []).append(xy(end))
    names = {}
    assignments = json.loads((Path(__file__).resolve().parents[1] / "am3354/bypass-placement.json").read_text())
    # Only these loads bridge the DRAM reference rail to ground. The CPU and switch bias use other rails.
    high_speed = {f"C_DDR{i}" for i, entry in enumerate(assignments, 1)
                  if (entry["chip"], entry["kind"]) in {("U_DDR", "highSpeed"), ("channel", "return")}}
    fitted = {part.get("name") for part in parts.values()
              if part.get("manufacturer_part_number") == "CL05B104KO5NNNC"}
    if not high_speed or high_speed - fitted:
        raise ValueError(f"Missing specified high-speed reference capacitors: {sorted(high_speed - fitted)}")
    bypass = {}
    for e in board:
        if e["type"] != "source_trace":
            continue
        names[e["source_trace_id"]] = e.get("name") or ""
        pins = e["connected_source_port_ids"]
        if len(pins) != 2:
            continue
        for cap_id, via_id in (pins, reversed(pins)):
            pin = ports[cap_id]
            cap = parts.get(pin["source_component_id"], {})
            ref = cap.get("name", "")
            if ref not in high_speed:
                continue
            via = vias.get(lands.get(via_id, {}).get("pcb_port_id"))
            if via is None:
                continue
            net = nets[via["source_net_id"]]
            if net not in ("GND", "VDDS_DDR"):
                raise ValueError(f"Unexpected return rail on {ref}: {net}")
            plane = "inner1" if net == "GND" else "inner2"
            leg = [xy(via)]
            if plane not in via["layers"]:
                inner, = set(via["layers"]) & {"inner1", "inner2"}
                mates = [mate for end in inner_links.get((xy(via), inner), [])
                         if (mate := via_at.get((end, inner, via["source_net_id"]))) and plane in mate["layers"]]
                if len(mates) != 1:
                    raise ValueError(f"{ref} lacks a unique routed transition to {plane}")
                leg.append(xy(mates[0]))
            legs = bypass.setdefault(ref, {})
            if net in legs:
                raise ValueError(f"Ambiguous {net} via on {ref}")
            legs[net] = leg
    if not high_speed or set(bypass) != high_speed or any(set(legs) != {"GND", "VDDS_DDR"} for legs in bypass.values()):
        raise ValueError("Incomplete high-speed bypass via pair")
    for e in board:
        if e["type"] != "pcb_trace":
            continue
        signal = names[e["source_trace_id"]]
        if not signal.startswith("DDR_") or (selected and signal not in selected):
            continue
        for p in e["route"]:
            if p["route_type"] != "via":
                continue
            if {p["from_layer"], p["to_layer"]} != {"top", "bottom"}:
                raise ValueError(f"Review the reference layers for {signal}")
            location = xy(p)
            # Both legs must belong to the same capacitor for a plane-to-plane return.
            choices = []
            for ref, legs in bypass.items():
                gnd = max(math.dist(location, point) for point in legs["GND"])
                vdd = max(math.dist(location, point) for point in legs["VDDS_DDR"])
                choices.append((max(gnd, vdd), ref, gnd, vdd))
            far, ref, gnd, vdd = min(choices)
            yield signal, *location, ref, gnd, vdd, far


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("board", type=Path)
    parser.add_argument("--signal", action="append", default=[], help="screen a selected outer-layer signal; repeat for a pair")
    args = parser.parse_args()
    rows = sorted(measurements(json.loads(args.board.read_bytes()), args.signal), key=lambda row: -row[-1])
    if set(args.signal) - {row[0] for row in rows}:
        raise ValueError("A selected signal has no outer-layer transition")
    out = csv.writer(sys.stdout)
    out.writerow(("signal", "x_mm", "y_mm", "bypass", "to_ground_via_mm", "to_supply_via_mm", "farther_via_mm"))
    for signal, x, y, ref, gnd, vdd, far in rows:
        out.writerow((signal, f"{x:.5f}", f"{y:.5f}", ref, f"{gnd:.4f}", f"{vdd:.4f}", f"{far:.4f}"))
    if not rows:
        raise ValueError("No DDR layer transitions found")
    print(f"{len(rows)} transitions. Longest distance to the farther via of the nearest bypass pair "
          f"{rows[0][-1]:.3f} mm on {rows[0][0]}.", file=sys.stderr)
