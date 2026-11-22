"""Remove the abandoned two-via CAM island at the previous RAM VREFCA capacitor site."""
import json
import sys
from pathlib import Path

board = json.loads(Path(sys.argv[1]).read_bytes())
ids = {e.get(e["type"]+"_id"):e for e in board}
stubs = {"channel_pcb_trace_169","channel_pcb_trace_172","channel_pcb_trace_173"}
vias = {"channel_pcb_via_146","channel_pcb_via_147"}
ports = {p for vid in vias for p in ids[vid]["pcb_port_ids"]}
expected = {"channel_pcb_port_798","channel_pcb_port_799","channel_pcb_port_800","channel_pcb_port_801"}
if ports != expected:
    raise ValueError("Unexpected VREFCA via terminals")
for tid, a, z in [("channel_pcb_trace_169","799","801"),("channel_pcb_trace_172","802","801"),("channel_pcb_trace_173","803","603")]:
    route = ids[tid]["route"]
    if (route[0].get("start_pcb_port_id"), route[-1].get("end_pcb_port_id")) != ("channel_pcb_port_"+a,"channel_pcb_port_"+z):
        raise ValueError(f"Unexpected old copper at {tid}")
for t in board:
    if t["type"] == "pcb_trace" and t["pcb_trace_id"] not in stubs:
        if any(p.get("start_pcb_port_id") in ports or p.get("end_pcb_port_id") in ports for p in t["route"]):
            raise ValueError("An active trace still needs the obsolete via")
drop = stubs | vias | ports
Path(sys.argv[2]).write_text(json.dumps([e for e in board if e.get(e["type"]+"_id") not in drop],separators=(",",":")))
