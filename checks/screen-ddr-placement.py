"""Bound the possible space for a non-DDR CPU escape before spending time on routing."""
import argparse
import json
from pathlib import Path
import runpy

from shapely.affinity import translate
from shapely.geometry import Point
from shapely.ops import unary_union


def screen(board, ram_y, pins):
    copper = runpy.run_path(str(Path(__file__).with_name("audit-copper-contacts.py")))["copper"](board)
    elements = {e[e["type"] + "_id"]: e for e in board if e["type"] + "_id" in e}
    components = {e["name"]: e["source_component_id"] for e in board if e["type"] == "source_component"}
    pcb = {e["source_component_id"]: e["pcb_component_id"] for e in board if e["type"] == "pcb_component"}
    signals = {e["subcircuit_connectivity_map_key"] for e in board
               if e["type"] == "source_trace" and (e.get("name") or "").startswith("DDR_")}
    if len(signals) != 50:
        raise ValueError("Expected 50 distinct DDR signal nets")
    widths = [p["width"] for t in board if t["type"] == "pcb_trace"
              and elements.get(t.get("source_trace_id"), {}).get("subcircuit_connectivity_map_key") in signals
              for p in t["route"] if p.get("route_type") == "wire"]
    setback = 4 * max(widths)
    cpu_lands, ram_lands, escape_lands = [], [], {}
    for oid, net, shape in copper["top"]:
        item = elements[oid]
        if item["type"] != "pcb_smtpad":
            continue
        if item["pcb_component_id"] == pcb[components["U_DDR"]]:
            ram_lands.append(shape)
        elif item["pcb_component_id"] == pcb[components["U1"]]:
            if net in signals:
                cpu_lands.append(shape)
            source = elements[elements[item["pcb_port_id"]]["source_port_id"]]
            escape_lands[source["name"]] = shape
    cpu = unary_union(cpu_lands).convex_hull
    ram = unary_union(ram_lands).convex_hull
    print("ram_delta_y_mm,ball,max_pad_edge_distance_mm,required_setback_mm,headroom_mm")
    for dy in ram_y:
        hull = cpu.union(translate(ram, yoff=dy)).convex_hull
        for pin in pins:
            # Distance to a convex set is convex, so its maximum on a polygon is at a vertex.
            distance = max(hull.distance(Point(xy)) for xy in escape_lands[pin].exterior.coords)
            print(f"{dy:.3f},{pin},{distance:.4f},{setback:.4f},{distance-setback:.4f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("board", type=Path)
    parser.add_argument("--ram-dy", type=float, nargs="+", default=[0, .5, 1, 1.5])
    parser.add_argument("--balls", nargs="+", default=["R1", "B4", "B5", "C5", "C6"])
    args = parser.parse_args()
    screen(json.loads(args.board.read_text()), args.ram_dy, args.balls)
