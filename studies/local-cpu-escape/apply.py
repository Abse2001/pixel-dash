"""Apply the authorized CPU-side wire edits while retaining every data via and terminal."""
import json
import sys
from pathlib import Path

board=json.loads(Path(sys.argv[1]).read_bytes())
waypoints=json.loads(Path(__file__).with_name("waypoints.json").read_bytes())
if set(waypoints)!={"DDR_D12","DDR_D14"}:
    raise ValueError("Unexpected trial signals")
links={e["name"]:e["source_trace_id"] for e in board if e["type"]=="source_trace" and e.get("name")}
for net, points in waypoints.items():
    trace, = [t for t in board if t["type"]=="pcb_trace" and t["source_trace_id"]==links[net]]
    prefix=trace["route"][:len(points)]
    if any(p["route_type"]!="wire" or p["layer"]!="top" for p in prefix):
        raise ValueError(f"{net} crosses the permitted layer span")
    for i, (p, (x,y)) in enumerate(zip(prefix,points,strict=True)):
        if i in (0,len(points)-1) and (p["x"],p["y"])!=(x,y):
            raise ValueError(f"Moved fixed endpoint on {net}")
        p.update(x=x,y=y)
Path(sys.argv[2]).write_text(json.dumps(board,separators=(",",":")))
