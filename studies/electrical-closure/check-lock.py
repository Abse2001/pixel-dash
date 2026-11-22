"""Check the e4c906f CPU/RAM pin mapping, signal copper and drills for both bytes and CK."""
import hashlib
import json
import sys
from pathlib import Path

NAMES = {f"DDR_D{i}" for i in range(16)} | {
    f"DDR_{kind}{i}" for kind in ("DQM", "DQS", "DQSn") for i in range(2)
} | {"DDR_CK", "DDR_CKn"}
LOCK = Path(__file__).with_name("e4c906f-fingerprints.json")

def fingerprints(board):
    ids = {e[e["type"]+"_id"]: e for e in board if e["type"]+"_id" in e}
    result = {}
    for signal in board:
        if signal["type"] != "source_trace" or signal.get("name") not in NAMES:
            continue
        name = signal["name"]
        key = signal["subcircuit_connectivity_map_key"]
        copper = [e for e in board if e["type"] in ("pcb_via", "pcb_trace")
                  and (e.get("subcircuit_connectivity_map_key") == key or
                       e.get("source_trace_id") == signal["source_trace_id"])]
        endpoints = []
        for pid in signal["connected_source_port_ids"]:
            p = ids[pid]
            endpoints.append([ids[p["source_component_id"]]["name"], p["name"]])
        if name in result or sum(e["type"] == "pcb_via" for e in copper) != 2:
            raise ValueError(f"Unexpected signal or drill count on {name}")
        raw = json.dumps([endpoints, sorted(copper, key=lambda e:e[e["type"]+"_id"])],
                         sort_keys=True, separators=(",", ":"))
        result[name] = hashlib.sha256(raw.encode()).hexdigest()
    if result.keys() != NAMES:
        raise ValueError("Incomplete protected signal set")
    return result

if __name__ == "__main__":
    result = fingerprints(json.loads(Path(sys.argv[1]).read_bytes()))
    expected = json.loads(LOCK.read_bytes())
    changed = sorted(n for n in NAMES if result[n] != expected[n])
    if changed:
        raise ValueError(f"Changed protected copper, barrels or ball mapping: {changed}")
    print("22 byte routes, both clocks and 48 plated transitions match e4c906f.")
