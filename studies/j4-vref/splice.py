"""Replace the two approved L1 prefixes and preserve their original splice points."""
import json
import sys
from pathlib import Path

board = json.loads(Path(sys.argv[1]).read_bytes())
points = json.loads(Path(__file__).with_name("waypoints.json").read_bytes())
ids = {t.get(t["type"] + "_id"): t for t in board}
prefix_sizes = {"DDR_D12": 7, "DDR_D14": 10}
if points.keys() != prefix_sizes.keys():
    raise ValueError("Unexpected data-byte edits")
for name, size in prefix_sizes.items():
    trace, = [t for t in board if t["type"] == "pcb_trace" and ids[t["source_trace_id"]].get("name") == name]
    old = trace["route"]
    template = {k: v for k, v in old[1].items() if k not in ("x", "y")}
    if template.get("route_type") != "wire" or template.get("layer") != "top":
        raise ValueError(f"{name} starts on an unexpected layer")
    for p in old[1:size-1]:
        if {k: v for k,v in p.items() if k not in ("x","y")} != template:
            raise ValueError(f"Unexpected copper or terminal in the {name} prefix")
    new = points[name]
    for a, z in [(new[0],old[0]), (new[-1],old[size-1])]:
        if a != [z["x"],z["y"]]:
            raise ValueError(f"{name} terminal or splice has moved")
    trace["route"] = [old[0]] + [dict(template,x=x,y=y) for x,y in new[1:-1]] + old[size-1:]
Path(sys.argv[2]).write_text(json.dumps(board, separators=(",", ":")))
