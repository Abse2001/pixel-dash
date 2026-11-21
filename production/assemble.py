"""Build the single-board engineering candidate from the retained subsystems and routed DDR."""
import csv
import json
from math import dist
import re
import sys
from pathlib import Path
from build_retained import build
from clip_channel import add_inner2_ground, restrict_ground
from wide_layout import apply_wide_layout

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

# Route checkpoints use fixed world coordinates. A layout pass that moves this
# group invalidates both its stored copper and the enclosure clearance review.
for ref, expected in (("U1", (-44.8,15.15)), ("U_DDR", (-65.0,15.15))):
    package = one(channel, "source_component", name=ref)
    center = one(channel, "pcb_component", source_component_id=identity(package))["center"]
    if dist((center["x"],center["y"]),expected)>1e-4:
        raise ValueError(f"{ref} placement moved from {expected} to {center}")

# Prefix the imported channel's IDs, including keys referenced in nested routes.
# GND and the protected system input are shared across both source designs.
mapping = {}
for e in channel:
    for key in (e["type"] + "_id", "subcircuit_id", "subcircuit_connectivity_map_key"):
        if e.get(key):
            mapping[e[key]] = "channel_" + e[key]
shared_supplies = {}
for name in ("GND", "VSYS"):
    new = one(channel, "source_net", name=name)
    retained = one(board, "source_net", name=name)
    shared_supplies[identity(new)] = retained
    for k in ("source_net_id", "subcircuit_connectivity_map_key"):
        mapping[new[k]] = retained[k]
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
    if e["type"] in {"source_board", "pcb_board", "source_project_metadata"} or identity(e) in shared_supplies:
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
# Each LCD_DATA terminal samples its matching SYSBOOT resistor on reset.
# Tie its open resistor terminal to the actual data net after the two source
# namespaces have been joined; preserve both the LCD and MMC assignments.
for bit in range(16):
    signal = f"LCD_D{bit}"
    target = one(board, "source_trace", source_trace_id="system_" + signal)
    resistor = port(f"R_SYSBOOT{bit}", "pin2")
    key = target["subcircuit_connectivity_map_key"]
    binding = "system_boot_tap_" + str(bit)
    assert not resistor.get("subcircuit_connectivity_map_key"), resistor
    resistor["subcircuit_connectivity_map_key"] = key
    board.append(dict(type="source_trace", source_trace_id=binding,
        name=f"SYSBOOT{bit}_SENSE", connected_source_net_ids=target["connected_source_net_ids"],
        connected_source_port_ids=[target["connected_source_port_ids"][0],resistor["source_port_id"]],
        subcircuit_connectivity_map_key=key))
    board.append(dict(type="pcb_trace_missing_error", error_type="pcb_trace_missing_error",
        pcb_trace_missing_error_id="open_" + binding, source_trace_id=binding,
        message=f"R_SYSBOOT{bit} requires copper to {signal}"))
for e in board:
    if e["type"]=="source_board":
        e["title"]="Pixel Dash AM3354 handheld"
apply_wide_layout(board)
# The saved sections alternate between top and bottom in assembled-board coordinates.
# Check their endpoints before reusing them after a placement change.
paths = json.loads((root / "system-paths.json").read_text())
layers = ("top", "inner1", "inner2", "bottom")
for sid, sections in paths.items():
    source = one(board, "source_trace", source_trace_id=sid)
    start, end = [one(board, "pcb_port", source_port_id=pid) for pid in source["connected_source_port_ids"]]
    if not sections or any(len(section) < 2 for section in sections):
        raise ValueError(f"Empty route section on {sid}")
    last_layer = layers[-1] if len(sections) % 2 == 0 else layers[0]
    for pad, point, layer in ((start, sections[0][0], "top"), (end, sections[-1][-1], last_layer)):
        if layer not in pad["layers"] or dist(point, (pad["x"], pad["y"])) > 1e-5:
            raise ValueError(f"Saved route no longer lands on a terminal of {sid}")
    route = []
    trace_id = "pcb_" + sid
    key = source["subcircuit_connectivity_map_key"]
    for index, section in enumerate(sections):
        layer = "bottom" if index % 2 else "top"
        if index:
            x, y = section[0]
            if dist((x, y), sections[index-1][-1]) > 1e-7:
                raise ValueError(f"Mismatch at via {index} on {sid}")
            previous = "top" if index % 2 else "bottom"
            route.append(dict(route_type="via", x=x, y=y, from_layer=previous, to_layer=layer))
            board.append(dict(type="pcb_via", pcb_via_id=f"{trace_id}_via_{index}", pcb_trace_id=trace_id,
                              source_trace_id=sid, subcircuit_connectivity_map_key=key, x=x, y=y,
                              from_layer=previous, to_layer=layer, layers=list(layers),
                              hole_diameter=0.15, outer_diameter=0.30))
        route.extend(dict(route_type="wire", layer=layer, width=0.102, x=x, y=y) for x, y in section)
    route[0]["start_pcb_port_id"] = start["pcb_port_id"]
    route[-1]["end_pcb_port_id"] = end["pcb_port_id"]
    board.append(dict(type="pcb_trace", pcb_trace_id=trace_id, source_trace_id=sid,
                      subcircuit_connectivity_map_key=key, route=route))
    board.remove(one(board, "pcb_trace_missing_error", pcb_trace_missing_error_id="open_" + sid))
restrict_ground(board,ground(board)["source_net_id"])
add_inner2_ground(board, ground(board)["source_net_id"])
Path(sys.argv[2]).write_text(json.dumps(board,separators=(",",":")))
