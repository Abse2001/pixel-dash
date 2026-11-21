"""Materialize retained peripheral copper including the reviewed local edits."""
import gzip
import json
import sys
from pathlib import Path

def build():
    root = Path(__file__).parent
    board = json.loads(gzip.decompress((root / "retained.circuit.json.gz").read_bytes()))
    edits = json.loads((root / "peripheral-route-edits.json").read_text())
    for element in board:
        if element["type"] == "pcb_trace" and element["pcb_trace_id"] in edits:
            route = edits.pop(element["pcb_trace_id"])
            if any(route[i] != element["route"][i] for i in (0, -1)):
                raise ValueError("Route edit changed endpoint")
            element["route"] = route
    if edits:
        raise ValueError(f"Unapplied route edits: {list(edits)}")
    return board

if __name__ == "__main__":
    Path(sys.argv[1]).write_text(json.dumps(build(), separators=(",", ":")))
