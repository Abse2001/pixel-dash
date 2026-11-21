"""Build the single-board engineering candidate from the retained subsystems and routed DDR."""
import csv
import json
import re
import sys
from pathlib import Path
from build_retained import build
from clip_channel import restrict_ground

root = Path(__file__).resolve().parent
board = build()
# Legacy schematic routing also used synthetic IDs composed of two pin IDs.
schematic_pins={e["schematic_port_id"] for e in board if e["type"]=="schematic_port"}
board=[e for e in board if e["type"]!="schematic_trace" or
       all(p in schematic_pins for p in re.findall(r"schematic_port_\d+",e.get("source_trace_id","")))]
channel = json.loads(Path(sys.argv[1]).read_text())
def one(elements, kind, **attributes):
    matches = [e for e in elements if e["type"] == kind and
               all(e.get(k) == v for k, v in attributes.items())]
    if len(matches) != 1:
        raise ValueError(f"Expected one {kind} matching {attributes}, found {len(matches)}")
    return matches[0]

def rename(value, table):
    if isinstance(value, dict):
        return {k: rename(v, table) for k, v in value.items()}
    if isinstance(value, list):
        return [rename(v, table) for v in value]
    if isinstance(value, str):
        return table.get(value, value)
    return value

def ground(elements):
    return one(elements, "source_net", name="GND")
def identity(e):
    return e.get(e["type"] + "_id")

# Prefix the imported channel's IDs, including keys referenced in nested routes.
# The one shared net at this stage is the actual GND electrical domain.
mapping = {}
for e in channel:
    for key in (e["type"] + "_id", "subcircuit_id", "subcircuit_connectivity_map_key"):
        if e.get(key):
            mapping[e[key]] = "channel_" + e[key]
for k in ("source_net_id", "subcircuit_connectivity_map_key"):
    mapping[ground(channel)[k]] = ground(board)[k]
for kind in ("source_board", "pcb_board"):
    mapping[identity(one(channel, kind))] = identity(one(board, kind))
board_spec = one(board, "pcb_board")
channel_spec = one(channel, "pcb_board")
if any(spec["num_layers"] != 4 for spec in (channel_spec, board_spec)):
    raise ValueError("Expected a four-layer board")
# The retained board has the qualified mechanical notch absent on the older
# channel outline. Keep the complete retained board contour and all cutouts.
for k in ("allow_blind_and_buried_vias","is_via_in_pad_allowed","min_via_hole_diameter","min_via_pad_diameter"):
    board_spec[k] = channel_spec[k]
for e in channel:
    if e["type"] in {"source_board", "pcb_board", "source_project_metadata"} or e is ground(channel):
        continue
    board.append(rename(e,mapping))

# Give panel passives functional designators and preserve pin/net identities.
panel_names = {"R_GPU_LCD_WR":"R_LCD_WR","R_GPU_LCD_RD":"R_LCD_RD"}
def panel_name(value):
    if isinstance(value, str):
        for k, v in panel_names.items():
            value=value.replace(k,v)
    elif isinstance(value, list):
        return [panel_name(v) for v in value]
    elif isinstance(value, dict):
        return {k:panel_name(v) for k,v in value.items()}
    return value
board = panel_name(board)
restrict_ground(board,ground(board)["source_net_id"])
pins = { (p["source_component_id"],hint):p for p in board if p["type"]=="source_port"
         for hint in [p["name"],*p.get("port_hints",[])] }
parts = {e["name"]:e for e in board if e["type"]=="source_component"}
if len(parts)!=len([e for e in board if e["type"]=="source_component"]):
    raise ValueError("Duplicate component reference")
balls = json.loads((root.parent/"am3354/processor-balls.json").read_text())
def port(part,pin):
    return pins[parts[part]["source_component_id"],pin]
with (root/"interface.csv").open() as f:
    for row in csv.DictReader(f):
        ball=row["Ball"]
        if balls[ball]!=row["Pad"]:
            raise ValueError(f"Wrong processor ball {row}")
        a,b=port("U1",ball),port(row["Peripheral"],row["Pin"])
        sid="system_"+row["Signal"]
        key=b.get("subcircuit_connectivity_map_key") or a.get("subcircuit_connectivity_map_key") or sid
        if any(p.get("subcircuit_connectivity_map_key",key)!=key for p in (a,b)):
            raise ValueError(f"Would short an assigned processor pin {row}")
        a["subcircuit_connectivity_map_key"]=b["subcircuit_connectivity_map_key"]=key
        board.append(dict(type="source_trace",source_trace_id=sid,name=row["Signal"],
          display_name=f'U1.{ball} to {row["Peripheral"]}.{row["Pin"]}',connected_source_port_ids=
          [p["source_port_id"] for p in (a,b)],connected_source_net_ids=[e["source_net_id"] for e in board if e["type"]=="source_net"
              and e.get("subcircuit_connectivity_map_key")==key],subcircuit_connectivity_map_key=key))
        board.append(dict(type="pcb_trace_missing_error",error_type="pcb_trace_missing_error",
          pcb_trace_missing_error_id="open_"+sid,source_trace_id=sid,
          message=f'Handheld interface {row["Signal"]} requires PCB copper'))
for e in board:
    if e["type"]=="source_board":
        e["title"]="Pixel Dash AM3354 handheld"
Path(sys.argv[2]).write_text(json.dumps(board,separators=(",",":")))
