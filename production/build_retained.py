"""Materialize retained peripheral copper including the reviewed local edits."""
import gzip
import json
import sys
from pathlib import Path

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
    # ER-TFT070A2-6 reserves contacts 49 and 50. The old panel grounded them,
    # including a redundant bridge from the microSD bulk capacitor return.
    lcd, = [e for e in board if e["type"] == "source_component" and e.get("name") == "J_LCD"]
    nc = {e["source_port_id"] for e in board if e["type"] == "source_port"
          and e["source_component_id"] == lcd["source_component_id"] and e["pin_number"] in (49, 50)}
    if len(nc) != 2:
        raise ValueError("Missing reserved LCD contacts")
    traces = {e["source_trace_id"] for e in board if e["type"] == "source_trace"
              and nc.intersection(e["connected_source_port_ids"])}
    symbols = {e["schematic_port_id"] for e in board if e["type"] == "schematic_port"
               and e.get("source_port_id") in nc}
    board = [e for e in board if e.get("source_trace_id") not in traces and not
             (e["type"] == "schematic_trace" and symbols.intersection(e.get("source_trace_id", "").split("-")))]
    for e in board:
        if e.get("source_port_id") in nc:
            e.pop("subcircuit_connectivity_map_key", None)
            if e["type"] == "schematic_port":
                e["is_connected"] = False
    return board

if __name__ == "__main__":
    Path(sys.argv[1]).write_text(json.dumps(build(), separators=(",", ":")))
