"""Move the fixed controls with their land patterns. Keep cross-board routes open for rerouting."""
import json
from pathlib import Path

offsets = {}
for sign, refs in ((-1,"SW_UP SW_DOWN SW_LEFT SW_RIGHT SW_L J_JOY_L C_JOY_L_VDD C_JOY_L_BULK"),
                   (1,"SW_A SW_B SW_X SW_Y SW_R J_JOY_R C_JOY_R_VDD C_JOY_R_BULK")):
    offsets.update(dict.fromkeys(refs.split(),sign*43.75))
offsets.update(SW_SELECT=-88, SW_START=88, TP_3V3=-0.7)
vertical_offsets = {"SW_SELECT": -6.4, "SW_START": -6.4, "TP_3V3": -32.9}

def apply_wide_layout(board):
    outline = json.loads(Path(__file__).with_name("wide-outline.json").read_text())
    spec, = [e for e in board if e["type"] == "pcb_board"]
    spec.update(outline)
    # Move only the two lower enclosure mounts on the wide PCB.
    for side in (-1, 1):
        hole, = [e for e in board if e["type"] == "pcb_hole" and e.get("hole_diameter") == 3.3
                 and (e["x"], e["y"]) == (side * 50, -32)]
        hole.update(x=side * 70, y=-29)
    # Shell-specific display keepers, cell models and fasteners belong to the
    # small enclosure. The wide design retains the actual controller mechanisms.
    mechanical_offsets = {
        **dict.fromkeys(("left_joystick","left_joystick_flex","left_ear_screw_0","left_ear_screw_1","dpad","SW_L_body","SW_L_actuator"),(-43.75,0)),
        **dict.fromkeys(("right_joystick","right_joystick_flex","right_ear_screw_0","right_ear_screw_1","button_a","button_b","button_x","button_y","SW_R_body","SW_R_actuator"),(43.75,0)),
        "button_start":(88,-6.4), "button_select":(-88,-6.4),
    }
    bodies = {e["source_component_id"]:e["name"] for e in board if e["type"]=="source_component" and
              (e["source_component_id"].startswith("slim_assembly_") or e["name"]=="EnclosureR43")}
    for e in board:
        name = bodies.get(e.get("source_component_id"))
        if e["type"]=="cad_component" and name in mechanical_offsets:
            dx,dy = mechanical_offsets[name]
            e["position"]["x"] += dx
            e["position"]["y"] += dy
    board[:] = [e for e in board if e.get("source_component_id") not in bodies or
                bodies[e["source_component_id"]] in mechanical_offsets]
    source = {e["source_component_id"]:offsets[e["name"]] for e in board
              if e["type"]=="source_component" and e["name"] in offsets}
    owners = {e["pcb_component_id"]:source[e["source_component_id"]] for e in board
              if e["type"]=="pcb_component" and e.get("source_component_id") in source}
    vertical_sources = {e["source_component_id"]: vertical_offsets[e["name"]] for e in board
                        if e["type"] == "source_component" and e["name"] in vertical_offsets}
    vertical_owners = {e["pcb_component_id"]: vertical_sources[e["source_component_id"]] for e in board
                       if e["type"] == "pcb_component" and e.get("source_component_id") in vertical_sources}
    ports = {e["pcb_port_id"]:owners[e["pcb_component_id"]] for e in board
             if e["type"]=="pcb_port" and e.get("pcb_component_id") in owners}
    assert len(source) == len(offsets)
    retired = set()
    opens = []
    for e in board:
        shift = owners.get(e.get("pcb_component_id"))
        if shift is not None:
            dy = vertical_owners.get(e.get("pcb_component_id"), 0)
            if "x" in e:
                e["x"] += shift
                e["y"] += dy
            for k in ("center","position","anchor_position","cable_insertion_center"):
                if k in e:
                    e[k]["x"] += shift
                    e[k]["y"] += dy
            for k in ("route","points","outline"):
                for pt in e.get(k,[]):
                    pt["x"] += shift
                    pt["y"] += dy
            if "display_offset_x" in e:
                e["display_offset_x"] += shift
                e["display_offset_y"] += dy
        if e["type"] == "pcb_trace":
            ends = {p[k] for p in e["route"] for k in ("start_pcb_port_id","end_pcb_port_id") if k in p}
            if not (ends & ports.keys()):
                continue
            # A via inside a local trace has its own plated record. Leave the old
            # run open until all branches can be checked against the new placement.
            retired.add(e["pcb_trace_id"])
            opens.append(dict(type="pcb_trace_missing_error",error_type="pcb_trace_missing_error",
                pcb_trace_missing_error_id="wide_open_"+e["pcb_trace_id"],source_trace_id=e["source_trace_id"],
                message="Moved side-control footprint requires new copper"))
    board[:] = [e for e in board if e.get("pcb_trace_id") not in retired] + opens
