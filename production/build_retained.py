"""Materialize retained peripheral copper including the reviewed local edits."""
import gzip
import json
import sys
from pathlib import Path
from raster_panel import clear_dbi_interface

def correct_shoulder_terminals(board):
    # Omron B3F-3152 top view. Pins 1 and 2 are the contacts, 3 and 4 the case.
    parts = {e["source_component_id"] for e in board if e["type"] == "source_component"
             and e.get("name") in ("SW_L", "SW_R") and e.get("manufacturer_part_number") == "B3F-3152"}
    corrected = {}
    swap = {2: 4, 4: 2}
    for e in board:
        if e["type"] == "source_port" and e["source_component_id"] in parts and e["pin_number"] in swap:
            number = swap[e["pin_number"]]
            e["pin_number"], e["name"], e["port_hints"] = number, f"pin{number}", [f"pin{number}", str(number)]
            corrected[e["source_port_id"]] = number
    if len(corrected) != 4:
        raise ValueError("Unexpected shoulder switch pin map")
    lands = {e["pcb_port_id"]: corrected[e["source_port_id"]] for e in board
             if e["type"] == "pcb_port" and e.get("source_port_id") in corrected}
    for e in board:
        if e["type"] == "schematic_port" and e.get("source_port_id") in corrected:
            e["pin_number"] = corrected[e["source_port_id"]]
        if e["type"] == "pcb_plated_hole" and e.get("pcb_port_id") in lands:
            e["port_hints"] = [f"pin{lands[e['pcb_port_id']]}" if h in ("pin2", "pin4") else h
                               for h in e["port_hints"]]


def align_power_lands(board):
    # JLCPCB C5349662 and C2071868, top-view copper from their EasyEDA packages.
    # Both installed patterns have horizontal rows in the retained board coordinates.
    patterns = {"L_BAT_BUCKBOOST": ("C5349662", 2.02794, 1.4000, 2.1200, 2),
                "U_3V3": ("C2071868", 1.35001, 1.1000, 0.6000, 6)}
    parts = {e["name"]: e for e in board if e["type"] == "source_component"}
    ports = {e["pcb_port_id"]: e for e in board if e["type"] == "pcb_port"}
    moved = {}
    for name, (code, half_pitch, width, height, count) in patterns.items():
        part = parts[name]
        if part["supplier_part_numbers"]["jlcpcb"] != [code]:
            raise ValueError(f"Unexpected supplier footprint for {name}")
        footprint, = (e for e in board if e["type"] == "pcb_component"
                      and e["source_component_id"] == part["source_component_id"])
        pads = [e for e in board if e["type"] == "pcb_smtpad"
                and e["pcb_component_id"] == footprint["pcb_component_id"]]
        if len(pads) != count or footprint["rotation"] not in (0, 180):
            raise ValueError(f"Unexpected land orientation or count for {name}")
        cx = footprint["center"]["x"]
        for pad in pads:
            new_x = cx + (half_pitch if pad["x"] > cx else -half_pitch)
            port = ports[pad["pcb_port_id"]]
            moved[pad["pcb_port_id"]] = (port["x"], port["y"], new_x)
            port["x"] = pad["x"] = new_x
            pad["width"], pad["height"] = width, height

    for trace in board:
        if trace["type"] != "pcb_trace":
            continue
        for index, field in ((0, "start_pcb_port_id"), (-1, "end_pcb_port_id")):
            point = trace["route"][index]
            if point.get(field) in moved:
                old_x, old_y, new_x = moved[point[field]]
                if abs(point["x"] - old_x) < 1e-5 and abs(point["y"] - old_y) < 1e-5:
                    point["x"] = new_x


def build():
    root = Path(__file__).parent
    board = json.loads(gzip.decompress((root / "retained.circuit.json.gz").read_bytes()))
    # The two inherited tracks have no physical contact with any remaining
    # land, via or trace on any layer. Their old endpoint ports were retired.
    detached = {"pcb_trace_1161", "pcb_trace_1437"}
    board = [item for item in board if not (item["type"] == "pcb_trace" and item["pcb_trace_id"] in detached)]
    edits = json.loads((root / "peripheral-route-edits.json").read_text())
    for element in board:
        if element["type"] == "pcb_trace" and element["pcb_trace_id"] in edits:
            route = edits.pop(element["pcb_trace_id"])
            if any(route[i] != element["route"][i] for i in (0, -1)):
                raise ValueError("Route edit changed endpoint")
            element["route"] = route
    if edits:
        raise ValueError(f"Unapplied route edits: {list(edits)}")
    align_power_lands(board)
    correct_shoulder_terminals(board)
    return clear_dbi_interface(board)

if __name__ == "__main__":
    Path(sys.argv[1]).write_text(json.dumps(build(), separators=(",", ":")))
