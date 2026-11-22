"""Compare each populated route against the fingerprint of the verified native breakout."""
import hashlib
import json
import sys
from pathlib import Path

SIGNALS = {f"DDR_D{i}" for i in range(16)} | {
    f"DDR_{kind}{lane}" for kind in ("DQM", "DQS", "DQSn") for lane in (0, 1)
}
LOCK = Path(__file__).with_name("locked-routes.json")

def fingerprints(board):
    ids = {p[p["type"] + "_id"]: p for p in board if p["type"] + "_id" in p}
    result = {}
    for trace in board:
        if trace["type"] != "pcb_trace":
            continue
        link = ids[trace["source_trace_id"]]
        name = link.get("name")
        if name not in SIGNALS:
            continue
        if name in result:
            raise ValueError(f"Duplicate route on {name}")
        ports = [ids[k] for k in link["connected_source_port_ids"]]
        endpoints = [(ids[p["source_component_id"]]["name"], p["name"]) for p in ports]
        route = []
        for p in trace["route"]:
            fields = ["route_type", "x", "y", "width", "layer", "from_layer", "to_layer"]
            route.append({k: round(p[k], 9) if isinstance(p[k], float) else p[k] for k in fields if k in p})
        vias = sorted((round(v["x"], 9), round(v["y"], 9), v["outer_diameter"], v["hole_diameter"],
                       v["from_layer"], v["to_layer"], v["layers"]) for v in board
                      if v["type"] == "pcb_via" and v.get("pcb_trace_id") == trace["pcb_trace_id"])
        if len(vias) != 2:
            raise ValueError(f"{name} has {len(vias)} plated transitions")
        payload = json.dumps([endpoints, route, vias], separators=(",", ":"), sort_keys=True)
        result[name] = hashlib.sha256(payload.encode()).hexdigest()
    if set(result) != SIGNALS:
        raise ValueError(f"Missing locked routes {sorted(SIGNALS-result.keys())}")
    return result

if __name__ == "__main__":
    current = fingerprints(json.loads(Path(sys.argv[1]).read_bytes()))
    expected = json.loads(LOCK.read_bytes())
    if current != expected:
        raise SystemExit("Locked geometry or pin mapping changed on " + ", ".join(sorted(n for n in SIGNALS if current[n] != expected.get(n))))
    print("22 of 22 routes match the verified breakout, including ball mapping, route vertices, widths and all 44 drilled via spans.")
