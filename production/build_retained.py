"""Materialize retained peripheral copper including the reviewed local edits."""
import gzip
import json
import sys
from pathlib import Path
from raster_panel import clear_dbi_interface

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
    return clear_dbi_interface(board)

if __name__ == "__main__":
    Path(sys.argv[1]).write_text(json.dumps(build(), separators=(",", ":")))
