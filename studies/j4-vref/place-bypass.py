"""Mirror the existing nonpolar 0201 CPU VREF bypass to the reverse face."""
import json
import sys
from pathlib import Path

board = json.loads(Path(sys.argv[1]).read_bytes())
placement = json.loads(Path(sys.argv[3]).read_bytes())
ids = {e.get(e["type"]+"_id"):e for e in board}
part, = [e for e in board if e["type"] == "pcb_component" and ids[e["source_component_id"]].get("name") == "C_CPU_VREF"]
old = dict(part["center"])
if old != {"x":-55.6739735, "y":15.9660265} or part["layer"] != "top":
    raise ValueError("Unexpected source bypass placement")
a, z = placement["a"], placement["z"]
center = [(i+j)/2 for i,j in zip(a,z)]
def place(point):
    point["x"] = center[0] + point["x"] - old["x"]
    point["y"] = center[1] - point["y"] + old["y"]

stub = ids["channel_pcb_trace_175"]
if stub["route"][0].get("start_pcb_port_id") != "channel_pcb_port_805" or len(stub["route"]) != 2:
    raise ValueError("Unexpected legacy ground escape")
board.remove(stub)
for e in board:
    if e.get("pcb_component_id") != part["pcb_component_id"]:
        continue
    if "layer" in e:
        e["layer"] = "bottom"
    if "layers" in e:
        e["layers"] = ["bottom"]
    if "x" in e and "y" in e:
        place(e)
    for field in ("center","footprint_origin","anchor_position","position"):
        if field in e:
            place(e[field])
    for field in ("route", "outline", "points"):
        for point in e.get(field,[]):
            place(point)
    if e["type"] == "pcb_courtyard_outline":
        e["outline"].reverse()
    if "ccw_rotation" in e:
        e["ccw_rotation"] = (-e["ccw_rotation"]) % 360
    if e["type"] == "cad_component":
        e["rotation"] = {"x":0,"y":180,"z":45}
        e["position"]["z"] = -abs(e["position"]["z"])
part["rotation"] = 315
for i,k in enumerate(("x","y")):
    f = "display_offset_"+k
    part[f] = f"{float(part[f].removesuffix('mm'))+center[i]-old[k]:.9f}mm"
for pid, coords in [("channel_pcb_port_804",a),("channel_pcb_port_805",z)]:
    if max(abs(ids[pid][k]-v) for k,v in zip(("x","y"),coords)) > 1e-7:
        raise ValueError("Reverse-face capacitor terminal mismatch")
Path(sys.argv[2]).write_text(json.dumps(board,separators=(",",":")))
