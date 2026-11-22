"""Remove the old DBI interface before binding the shared FPC lands to the raster panel."""
import re

LEGACY_PARTS = {"R_GPU_LCD_WR", "R_GPU_LCD_RD", "R_LCD_MODE_PD", "R_LCD_LED", "C_LCD_VCI", "C_LCD_VDDI"}
TOUCH_PULLS = {"R_TOUCH_SCL", "R_TOUCH_SDA", "R_TOUCH_IRQ"}


def clear_dbi_interface(board):
    parts = {e["name"]: e["source_component_id"] for e in board if e["type"] == "source_component"}
    dead = {parts[name] for name in LEGACY_PARTS}
    touch = {parts[name] for name in TOUCH_PULLS}
    ports = {e["source_port_id"] for e in board if e["type"] == "source_port" and
             (e["source_component_id"] in touch or
              (e["source_component_id"] == parts["J_LCD"] and 1 <= e["pin_number"] <= 50))}
    disconnected_symbols = {e["schematic_port_id"] for e in board if e["type"] == "schematic_port"
                            and e.get("source_port_id") in ports}
    dead.update(e["source_trace_id"] for e in board if e["type"] == "source_trace"
                and ports.intersection(e["connected_source_port_ids"]))
    while True:
        removed = set()
        for e in board:
            kind = e["type"]
            identity = kind + "_id"
            if identity not in e or e[identity] in dead:
                continue
            if any((key.endswith("_id") and isinstance(value, str) and value in dead)
                   or (key.endswith("_ids") and isinstance(value, list) and dead.intersection(value))
                   for key, value in e.items() if key != identity):
                removed.add(e[identity])
        if not removed:
            break
        dead.update(removed)
    result = []
    for e in board:
        if e.get(e["type"] + "_id") in dead:
            continue
        if e["type"] == "schematic_trace" and disconnected_symbols.intersection(
                re.findall(r"schematic_port_\d+", e.get("source_trace_id", ""))):
            continue
        if e.get("source_port_id") in ports:
            e.pop("subcircuit_connectivity_map_key", None)
            if e["type"] == "schematic_port":
                e["is_connected"] = False
        result.append(e)
    return result
