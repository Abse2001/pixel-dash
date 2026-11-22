"""Measure how far each DDR layer transition is from both vias of one high-speed bypass."""
import csv
import json
import math
import sys
from pathlib import Path


def xy(item):
    return item["x"], item["y"]


def measurements(board):
    parts = {e["source_component_id"]: e for e in board if e["type"] == "source_component"}
    nets = {e["source_net_id"]: e["name"] for e in board if e["type"] == "source_net"}
    ports = {e["source_port_id"]: e for e in board if e["type"] == "source_port"}
    lands = {e["source_port_id"]: e for e in board if e["type"] == "pcb_port"}
    vias = {p: e for e in board if e["type"] == "pcb_via" for p in e.get("pcb_port_ids", [])}
    names = {}
    high_speed = {e["name"] for e in parts.values() if e.get("name", "").startswith("C_DDR")
                  and e.get("manufacturer_part_number") == "CL05B104KO5NNNC"}
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
            if plane not in via["layers"]:
                raise ValueError(f"{ref} bypass via does not reach {plane}")
            legs = bypass.setdefault(ref, {})
            if net in legs:
                raise ValueError(f"Ambiguous {net} via on {ref}")
            legs[net] = xy(via)
    if not high_speed or set(bypass) != high_speed or any(set(legs) != {"GND", "VDDS_DDR"} for legs in bypass.values()):
        raise ValueError("Incomplete high-speed bypass via pair")
    for e in board:
        if e["type"] != "pcb_trace":
            continue
        signal = names[e["source_trace_id"]]
        if not signal.startswith("DDR_"):
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
                gnd = math.dist(location, legs["GND"])
                vdd = math.dist(location, legs["VDDS_DDR"])
                choices.append((max(gnd, vdd), ref, gnd, vdd))
            far, ref, gnd, vdd = min(choices)
            yield signal, *location, ref, gnd, vdd, far


if __name__ == "__main__":
    rows = sorted(measurements(json.loads(Path(sys.argv[1]).read_text())), key=lambda row: -row[-1])
    out = csv.writer(sys.stdout)
    out.writerow(("signal", "x_mm", "y_mm", "bypass", "to_ground_via_mm", "to_supply_via_mm", "farther_via_mm"))
    for signal, x, y, ref, gnd, vdd, far in rows:
        out.writerow((signal, f"{x:.5f}", f"{y:.5f}", ref, f"{gnd:.4f}", f"{vdd:.4f}", f"{far:.4f}"))
    if not rows:
        raise ValueError("No DDR layer transitions found")
    print(f"{len(rows)} transitions. Longest distance to the farther via of the nearest bypass pair "
          f"{rows[0][-1]:.3f} mm on {rows[0][0]}.", file=sys.stderr)
