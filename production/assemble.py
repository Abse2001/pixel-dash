"""Build the single-board engineering candidate from the retained subsystems and routed DDR."""
import csv
import json
from math import dist
import re
import sys
from pathlib import Path
from build_retained import build
from clip_channel import add_inner2_ground, clear_handheld_copper_from_ddr, restrict_ground
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

pins = { (p["source_component_id"],hint):p for p in board if p["type"]=="source_port"
         for hint in [p["name"],*p.get("port_hints",[])] }
parts = {e["name"]:e for e in board if e["type"]=="source_component"}
if len(parts)!=len([e for e in board if e["type"]=="source_component"]):
    raise ValueError("Duplicate component reference")
balls = json.loads((root.parent/"am3354/processor-balls.json").read_text())
def port(part,pin):
    return pins[parts[part]["source_component_id"],pin]
def interface_trace(signal, origin, output, destination, terminal):
    a, b = port(origin, output), port(destination, terminal)
    sid="system_"+signal
    key=b.get("subcircuit_connectivity_map_key") or a.get("subcircuit_connectivity_map_key") or sid
    if any(p.get("subcircuit_connectivity_map_key",key)!=key for p in (a,b)):
        raise ValueError(f"Would short an assigned processor pin {signal}")
    a["subcircuit_connectivity_map_key"]=b["subcircuit_connectivity_map_key"]=key
    board.append(dict(type="source_trace",source_trace_id=sid,name=signal,
      display_name=f"{origin}.{output} to {destination}.{terminal}",connected_source_port_ids=
      [p["source_port_id"] for p in (a,b)],connected_source_net_ids=[e["source_net_id"] for e in board if e["type"]=="source_net"
          and e.get("subcircuit_connectivity_map_key")==key],subcircuit_connectivity_map_key=key))
    board.append(dict(type="pcb_trace_missing_error",error_type="pcb_trace_missing_error",
      pcb_trace_missing_error_id="open_"+sid,source_trace_id=sid,
      message=f'Handheld interface {signal} requires PCB copper'))

with (root/"interface.csv").open() as f:
    for row in csv.DictReader(f):
        ball = row["Ball"]
        if balls[ball] != row["Pad"]:
            raise ValueError(f"Wrong processor ball {row}")
        interface_trace(row["Signal"], "U1", ball, row["Peripheral"], row["Pin"])

# The bare raster panel has independent analog rails and a floating LED string.
# Bind the physical contacts independently of the pending bias and LED drivers.
panel_rails = {"GND": (5, 36, 38, 48), "LCD_VCOM": (6, 46), "LCD_DVDD": (7,),
               "LCD_VGH": (41,), "LCD_VGL": (42,), "LCD_AVDD": (43,),
               "LCD_LED_A": (1, 2), "LCD_LED_K": (3, 4)}
def bind_supply(ref, terminal, net):
    pin = port(ref, terminal)
    key = net["subcircuit_connectivity_map_key"]
    if pin.get("subcircuit_connectivity_map_key", key) != key:
        raise ValueError(f"Conflicting assignment for {ref}.{terminal}")
    pin["subcircuit_connectivity_map_key"] = key
    sid = f"rail_{ref}_{terminal}"
    board.append(dict(type="source_trace", source_trace_id=sid, name=sid,
                      connected_source_port_ids=[pin["source_port_id"]],
                      connected_source_net_ids=[net["source_net_id"]], subcircuit_connectivity_map_key=key))
    return sid

# The old FPC doubled as a ground tie for the right shoulder switch.
bind_supply("SW_R", "pin2", ground(board))
for shoulder in ("SW_L", "SW_R"):
    for tab in ("pin3", "pin4"):
        bind_supply(shoulder, tab, ground(board))
for name, numbers in panel_rails.items():
    if name == "GND":
        net = ground(board)
    else:
        net = dict(type="source_net", source_net_id="raster_" + name, name=name,
                   subcircuit_connectivity_map_key="raster_" + name)
        board.append(net)
    for number in numbers:
        terminal = f"pin{number}"
        sid = bind_supply("J_LCD", terminal, net)
        if name == "GND":
            land = one(board, "pcb_port", source_port_id=port("J_LCD", terminal)["source_port_id"])
            board.append(dict(type="pcb_via", pcb_via_id=f"pcb_raster_ground_{number}",
                              source_trace_id=sid, source_net_id=net["source_net_id"],
                              subcircuit_connectivity_map_key=net["subcircuit_connectivity_map_key"],
                              x=land["x"], y=land["y"], from_layer="top", to_layer="inner1",
                              layers=["top", "inner1"], hole_diameter=0.125, outer_diameter=0.28))
for touch in ("SCL", "SDA", "IRQ"):
    bind_supply("R_TOUCH_" + touch, "pin2", one(board, "source_net", name="VDD_IO_3V3_SEQ"))

for index, axis in enumerate(("LX", "LY", "RX", "RY")):
    interface_trace("ADC_" + axis, "U_JOY_ADC", f"AIN{index}", "C_JOY_" + axis, "pin1")
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
for saved_name, plan in paths.items():
    if saved_name.startswith(("system_", "rail_")):
        source = one(board, "source_trace", source_trace_id=saved_name)
    else:
        source = one(board, "source_trace", display_name=saved_name)
    sid = source["source_trace_id"]
    pads = [one(board, "pcb_port", source_port_id=pid) for pid in source["connected_source_port_ids"]]
    if len(pads) == 1 and isinstance(plan, dict) and "end_at" in plan:
        rail, = source["connected_source_net_ids"]
        if one(board, "source_net", source_net_id=rail)["subcircuit_connectivity_map_key"] != source["subcircuit_connectivity_map_key"]:
            raise ValueError(f"Inconsistent rail assignment on {saved_name}")
        start = pads[0]
        ref, terminal = plan["end_at"].split(".")
        end = one(board, "pcb_port", source_port_id=port(ref, terminal)["source_port_id"])
    else:
        start, end = pads
    if isinstance(plan, dict) and "join_trace" in plan:
        retained = one(board, "pcb_trace", pcb_trace_id=plan["join_trace"], source_trace_id=sid)
        anchor = retained["route"][0]
        end = one(board, "pcb_port", pcb_port_id=anchor["start_pcb_port_id"])
        if dist((end["x"], end["y"]), (anchor["x"], anchor["y"])) > 1e-5:
            raise ValueError(f"Retained endpoint moved on {saved_name}")
        sections = plan["sections"]
    else:
        sections = plan["sections"] if isinstance(plan, dict) else plan
        if isinstance(plan, dict) and ("end_at" in plan or "start_at" in plan):
            field = "end_at" if "end_at" in plan else "start_at"
            ref, terminal = plan[field].split(".")
            alternate = port(ref, terminal)
            if alternate["subcircuit_connectivity_map_key"] != source["subcircuit_connectivity_map_key"]:
                raise ValueError(f"Alternate terminal has the wrong net on {saved_name}")
            alternate_land = one(board, "pcb_port", source_port_id=alternate["source_port_id"])
            if field == "end_at":
                end = alternate_land
            else:
                start = alternate_land
        if any(e["type"] == "pcb_trace" and e.get("source_trace_id") == sid for e in board):
            raise ValueError(f"Saved copper duplicates existing routing on {saved_name}")
    if not sections or any(len(section) < 2 for section in sections):
        raise ValueError(f"Empty route section on {sid}")
    first_layer = "top" if "top" in start["layers"] else "bottom"
    outer_layers = (first_layer, "bottom" if first_layer == "top" else "top")
    last_layer = outer_layers[(len(sections) - 1) % 2]
    for pad, point, layer in ((start, sections[0][0], first_layer), (end, sections[-1][-1], last_layer)):
        if layer not in pad["layers"] or dist(point, (pad["x"], pad["y"])) > 1e-5:
            raise ValueError(f"Saved route no longer lands on a terminal of {sid}")
    width = plan.get("width", 0.102) if isinstance(plan, dict) else 0.102
    route = []
    trace_id = "pcb_" + sid
    key = source["subcircuit_connectivity_map_key"]
    for index, section in enumerate(sections):
        layer = outer_layers[index % 2]
        if index:
            x, y = section[0]
            if dist((x, y), sections[index-1][-1]) > 1e-7:
                raise ValueError(f"Mismatch at via {index} on {sid}")
            previous = outer_layers[(index - 1) % 2]
            route.append(dict(route_type="via", x=x, y=y, from_layer=previous, to_layer=layer))
            board.append(dict(type="pcb_via", pcb_via_id=f"{trace_id}_via_{index}", pcb_trace_id=trace_id,
                              source_trace_id=sid, subcircuit_connectivity_map_key=key, x=x, y=y,
                              from_layer=previous, to_layer=layer, layers=list(layers),
                              hole_diameter=0.15, outer_diameter=0.30))
        route.extend(dict(route_type="wire", layer=layer, width=width, x=x, y=y) for x, y in section)
    route[0]["start_pcb_port_id"] = start["pcb_port_id"]
    route[-1]["end_pcb_port_id"] = end["pcb_port_id"]
    board.append(dict(type="pcb_trace", pcb_trace_id=trace_id, source_trace_id=sid,
                      subcircuit_connectivity_map_key=key, route=route))
    if saved_name.startswith("system_"):
        board.remove(one(board, "pcb_trace_missing_error", pcb_trace_missing_error_id="open_" + sid))
    else:
        board = [e for e in board if not (e["type"] == "pcb_trace_missing_error" and e.get("source_trace_id") == sid)]
gnd = ground(board)
def add_ground_return(trace, point, via_id):
    board.append(dict(type="pcb_via", pcb_via_id=via_id, pcb_trace_id=trace["pcb_trace_id"],
                      source_trace_id=trace["source_trace_id"], source_net_id=gnd["source_net_id"],
                      subcircuit_connectivity_map_key=gnd["subcircuit_connectivity_map_key"],
                      x=point["x"], y=point["y"], from_layer="top", to_layer="inner1",
                      layers=["top", "inner1"], hole_diameter=0.125, outer_diameter=0.28))

# Ground the low SYSBOOT strap resistors at their own bias pads.
for bit in range(16):
    source = one(board, "source_trace", name=f"SYSBOOT{bit}_BIAS")
    if source["connected_source_net_ids"] != [gnd["source_net_id"]]:
        continue
    land = one(board, "pcb_port", source_port_id=port(f"R_SYSBOOT{bit}", "pin1")["source_port_id"])
    dx, dy = {5: (-0.25, 0.25), 15: (0.2, -0.1)}.get(bit, (0, 0))
    x, y = land["x"] + dx, land["y"] + dy
    if dx or dy:
        board.append(dict(type="pcb_trace", pcb_trace_id=f"pcb_boot_ground_stub_{bit}",
                          source_trace_id=source["source_trace_id"], route=[
                              dict(route_type="wire", x=land["x"], y=land["y"], width=0.24, layer="top",
                                   start_pcb_port_id=land["pcb_port_id"]),
                              dict(route_type="wire", x=x, y=y, width=0.24, layer="top")]))
    board.append(dict(type="pcb_via", pcb_via_id=f"pcb_boot_ground_{bit}",
                      source_trace_id=source["source_trace_id"], source_net_id=gnd["source_net_id"],
                      subcircuit_connectivity_map_key=gnd["subcircuit_connectivity_map_key"],
                      x=x, y=y, from_layer="top", to_layer="inner1",
                      layers=["top", "inner1"], hole_diameter=0.125, outer_diameter=0.28))

# The microSD bulk capacitor now returns directly to L2 at its ground pad.
sd_cap_ground = port("C_SD_BULK", "pin2")
sd_land = one(board, "pcb_port", source_port_id=sd_cap_ground["source_port_id"])
sd_return = one(board, "source_trace", name="SD_BULK_GND")
if (sd_return["connected_source_port_ids"] != [sd_cap_ground["source_port_id"]]
        or sd_return["connected_source_net_ids"] != [gnd["source_net_id"]]):
    raise ValueError("Unexpected microSD bulk return assignment")
board.append(dict(type="pcb_via", pcb_via_id="pcb_sd_bulk_ground",
                  source_trace_id=sd_return["source_trace_id"], source_net_id=gnd["source_net_id"],
                  subcircuit_connectivity_map_key=gnd["subcircuit_connectivity_map_key"],
                  x=sd_land["x"], y=sd_land["y"], from_layer="top", to_layer="inner1",
                  layers=["top", "inner1"], hole_diameter=0.125, outer_diameter=0.28))

# These filter returns ended at vias owned by the removed processor circuitry.
# Terminate each retained top trace in a blind via to the L2 ground plane.
for number in (1265, 1266, 1267, 1322):
    trace = one(board, "pcb_trace", pcb_trace_id=f"pcb_trace_{number}")
    route = trace["route"]
    transition, endpoint = route[-2:]
    if (transition["route_type"] != "via" or transition["from_layer"] != "top"
            or endpoint.get("layer") != "bottom" or route[-3].get("layer") != "top"):
        raise ValueError(f"Unexpected joystick ground return {number}")
    if number in (1265, 1266):
        # Place the via in the grounded capacitor pad, clear of SD_DAT1 and ADC_RX.
        for point in route[1:]:
            point.update(x=route[0]["x"], y=route[0]["y"])
        trace["route"] = [route[0], transition, endpoint]
    transition["to_layer"] = endpoint["layer"] = "inner1"
    endpoint.pop("end_pcb_port_id", None)
    add_ground_return(trace, transition, f"pcb_joystick_ground_{number}")
# Stitch the existing converter and audio ground tracks wherever they change
# between their surface pads and the main ground plane.
for number in (3, 98, 108, 109):
    trace = one(board, "pcb_trace", pcb_trace_id=f"pcb_trace_{number}")
    for index, point in enumerate(trace["route"]):
        if point["route_type"] != "via":
            continue
        if {point["from_layer"], point["to_layer"]} != {"top", "inner1"}:
            raise ValueError(f"Unexpected ground transition in {number}")
        add_ground_return(trace, point, f"pcb_retained_ground_{number}_{index}")
# The left joystick signal crosses the two main regulator filters on L4.
joystick = one(board, "pcb_trace", pcb_trace_id="pcb_trace_1439")
joystick_source = one(board, "source_trace", source_trace_id=joystick["source_trace_id"])
for index, via in enumerate(p for p in joystick["route"] if p["route_type"] == "via"):
    if {via["from_layer"], via["to_layer"]} != {"top", "bottom"}:
        raise ValueError("Unexpected left joystick signal span")
    board.append(dict(type="pcb_via", pcb_via_id=f"pcb_left_joystick_crossing_{index}",
                      pcb_trace_id=joystick["pcb_trace_id"], source_trace_id=joystick["source_trace_id"],
                      subcircuit_connectivity_map_key=joystick_source["subcircuit_connectivity_map_key"],
                      x=via["x"], y=via["y"], from_layer=via["from_layer"], to_layer=via["to_layer"],
                      layers=list(layers), hole_diameter=0.15, outer_diameter=0.30))
# Both L1-L2 transitions on the retained backlight gate need plated lands.
gate = one(board, "pcb_trace", pcb_trace_id="pcb_trace_14")
gate_source = one(board, "source_trace", source_trace_id=gate["source_trace_id"])
for index, via in enumerate(p for p in gate["route"] if p["route_type"] == "via"):
    if {via["from_layer"], via["to_layer"]} != {"top", "inner1"}:
        raise ValueError("Unexpected backlight gate span")
    board.append(dict(type="pcb_via", pcb_via_id=f"pcb_backlight_gate_{index}",
                      pcb_trace_id=gate["pcb_trace_id"], source_trace_id=gate_source["source_trace_id"],
                      subcircuit_connectivity_map_key=gate_source["subcircuit_connectivity_map_key"],
                      x=via["x"], y=via["y"], from_layer="top", to_layer="inner1",
                      layers=["top", "inner1"], hole_diameter=0.125, outer_diameter=0.28))
for index, (x, y) in enumerate(json.loads((root / "system-ground-stitches.json").read_text())):
    board.append(dict(type="pcb_via", pcb_via_id=f"pcb_mmc0_return_{index}",
                      source_net_id=gnd["source_net_id"],
                      subcircuit_connectivity_map_key=gnd["subcircuit_connectivity_map_key"],
                      x=x, y=y, from_layer="top", to_layer="bottom", layers=list(layers),
                      hole_diameter=0.20, outer_diameter=0.40))
# Filled blind vias connect the retained handheld ground lands to the adjacent plane.
for index, site in enumerate(json.loads((root / "ground-land-vias.json").read_text())):
    ref, terminal = site["terminal"].split(".")
    source = port(ref, terminal)
    if source["subcircuit_connectivity_map_key"] != gnd["subcircuit_connectivity_map_key"]:
        raise ValueError(f"Return via terminal is no longer ground: {site['terminal']}")
    surface = site["side"]
    adjacent = {"top": "inner1", "bottom": "inner2"}[surface]
    board.append(dict(type="pcb_via", pcb_via_id=f"pcb_handheld_ground_land_{index}",
                      source_net_id=gnd["source_net_id"],
                      subcircuit_connectivity_map_key=gnd["subcircuit_connectivity_map_key"],
                      x=site["x"], y=site["y"], from_layer=surface, to_layer=adjacent,
                      layers=[surface, adjacent], hole_diameter=0.125, outer_diameter=0.28))
    if "escape" in site:
        land = one(board, "pcb_port", source_port_id=source["source_port_id"])
        connection, = (t for t in board if t["type"] == "source_trace"
                       and source["source_port_id"] in t["connected_source_port_ids"]
                       and gnd["source_net_id"] in t["connected_source_net_ids"])
        x, y = site["escape"]
        board.append(dict(type="pcb_trace", pcb_trace_id=f"pcb_ground_escape_{index}",
                          source_trace_id=connection["source_trace_id"],
                          subcircuit_connectivity_map_key=gnd["subcircuit_connectivity_map_key"],
                          route=[dict(route_type="wire", x=x, y=y, layer=surface, width=site["width"],
                                      start_pcb_port_id=land["pcb_port_id"]),
                                 dict(route_type="wire", x=site["x"], y=site["y"],
                                      layer=surface, width=site["width"])]))
# The core feed crosses a DDR supply neck on L1 to keep the L3 island continuous.
feed = json.loads((root / "core-feed.json").read_text())
before, after = feed["before"], feed["after"]
rail = one(board, "source_net", name="VDD_CORE")
cap, ball = port("C_PMIC_CORE", "pin1"), port("U1", "G7")
cap_land, ball_land = [one(board, "pcb_port", source_port_id=p["source_port_id"]) for p in (cap, ball)]
if any(p["subcircuit_connectivity_map_key"] != rail["subcircuit_connectivity_map_key"] for p in (cap, ball)):
    raise ValueError("The core feed terminals no longer share VDD_CORE")
source, = (t for t in board if t["type"] == "source_trace"
           and cap["source_port_id"] in t["connected_source_port_ids"]
           and rail["source_net_id"] in t["connected_source_net_ids"])
stages = [
    ("top", 0.40, [(cap_land["x"], cap_land["y"]), before[0]]),
    ("inner2", 0.65, before),
    ("top", 0.65, [before[-1], after[0]]),
    ("inner2", 0.65, after),
    ("top", 0.24, [after[-1], (ball_land["x"], ball_land["y"])]),
]
route = []
for index, (layer, width, points) in enumerate(stages):
    if index:
        x, y = points[0]
        hole, outer = [(0.18, 0.38), (0.20, 0.38), (0.20, 0.38), (0.15, 0.30)][index-1]
        board.append(dict(type="pcb_via", pcb_via_id=f"pcb_core_feed_{index}", x=x, y=y,
                          from_layer="top", to_layer="bottom", layers=list(layers),
                          source_net_id=rail["source_net_id"], subcircuit_connectivity_map_key=rail["subcircuit_connectivity_map_key"],
                          hole_diameter=hole, outer_diameter=outer))
        route.append(dict(route_type="via", x=x, y=y, from_layer=stages[index-1][0], to_layer=layer))
    route.extend(dict(route_type="wire", x=x, y=y, width=width, layer=layer) for x, y in points)
route[0]["start_pcb_port_id"] = cap_land["pcb_port_id"]
route[-1]["end_pcb_port_id"] = ball_land["pcb_port_id"]
board.append(dict(type="pcb_trace", pcb_trace_id="pcb_core_supply_feed", source_trace_id=source["source_trace_id"],
                  subcircuit_connectivity_map_key=rail["subcircuit_connectivity_map_key"], route=route))
for terminal, branch in feed["branches"].items():
    ref, pin = terminal.split(".")
    pad = port(ref, pin)
    land = one(board, "pcb_port", source_port_id=pad["source_port_id"])
    source, = (t for t in board if t["type"] == "source_trace"
               and pad["source_port_id"] in t["connected_source_port_ids"]
               and rail["source_net_id"] in t["connected_source_net_ids"])
    start, end = branch["points"]
    if dist((land["x"], land["y"]), start) > 0.035:
        raise ValueError(f"Power via is no longer at {terminal}")
    board.append(dict(type="pcb_via", pcb_via_id="pcb_core_tap_"+pin, x=start[0], y=start[1],
                      from_layer="top", to_layer="bottom", layers=list(layers),
                      source_net_id=rail["source_net_id"], subcircuit_connectivity_map_key=rail["subcircuit_connectivity_map_key"],
                      hole_diameter=0.15, outer_diameter=0.30))
    board.append(dict(type="pcb_trace", pcb_trace_id="pcb_core_branch_"+pin,
                      source_trace_id=source["source_trace_id"], subcircuit_connectivity_map_key=rail["subcircuit_connectivity_map_key"],
                      route=[dict(route_type="wire", x=x, y=y, width=branch["width"], layer="inner2")
                             for x, y in (start, end)]))
# Bare probe lands need exposed copper without stencil apertures.
probe_parts = {e["source_component_id"] for e in board
               if e["type"] == "source_component" and e.get("ftype") == "simple_test_point"}
probe_footprints = {e["pcb_component_id"] for e in board
                    if e["type"] == "pcb_component" and e.get("source_component_id") in probe_parts}
board = [e for e in board if e["type"] != "pcb_solder_paste" or e.get("pcb_component_id") not in probe_footprints]
restrict_ground(board, gnd["source_net_id"])
clear_handheld_copper_from_ddr(board)
add_inner2_ground(board, ground(board)["source_net_id"])
Path(sys.argv[2]).write_text(json.dumps(board,separators=(",",":")))
