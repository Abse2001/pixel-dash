"""Apply local passive translations in PCB, paste, assembly and 3D coordinates."""
import json
import sys
from pathlib import Path

board = json.loads(Path(sys.argv[1]).read_bytes())
ids = {e.get(e["type"] + "_id"): e for e in board}
moves = json.loads(Path(sys.argv[3]).read_bytes())
for name, plan in moves.items():
    component, = [c for c in board if c["type"] == "pcb_component" and ids[c["source_component_id"]].get("name") == name]
    x, y = plan["from"]
    if component["center"] != {"x": x, "y": y}:
        raise ValueError(f"Unexpected starting position on {name}")
    dx, dy = plan["to"][0] - x, plan["to"][1] - y
    turn = plan.get("rotation_deg", 0)
    if turn not in (0, 180):
        raise ValueError("Only translations and half turns are supported")
    for trace_id in plan["obsolete_stubs"]:
        trace = ids[trace_id]
        if trace["type"] != "pcb_trace" or not any(
                ids[v]["pcb_component_id"] == component["pcb_component_id"]
                for p in trace["route"] for k, v in p.items() if k in ("start_pcb_port_id", "end_pcb_port_id")):
            raise ValueError(f"Unexpected stub {trace_id}")
        board.remove(trace)
    def shift(point):
        point["x"] = x + dx + (point["x"] - x) * (-1 if turn else 1)
        point["y"] = y + dy + (point["y"] - y) * (-1 if turn else 1)
    for obj in board:
        if obj.get("pcb_component_id") != component["pcb_component_id"]:
            continue
        if turn:
            for field in ("rotation", "ccw_rotation", "rect_ccw_rotation"):
                if isinstance(obj.get(field), (int, float)):
                    obj[field] = (obj[field] + turn) % 360
            if obj["type"] == "cad_component":
                obj["rotation"]["z"] = (obj["rotation"]["z"] + turn) % 360
        if "x" in obj and "y" in obj:
            shift(obj)
        for field in ("center", "footprint_origin", "position", "anchor_position"):
            if field in obj:
                shift(obj[field])
        for field in ("route", "outline", "points"):
            for point in obj.get(field, []):
                shift(point)
    for axis, delta in (("x", dx), ("y", dy)):
        field = "display_offset_" + axis
        if field in component:
            component[field] = f"{float(component[field].removesuffix('mm')) + delta:.9f}mm"
Path(sys.argv[2]).write_text(json.dumps(board, separators=(",", ":")))
