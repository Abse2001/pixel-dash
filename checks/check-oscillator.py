"""Verify the fitted clock path, evaluation footprint, and five L2 ground returns."""
import json
import sys
from math import dist
from pathlib import Path

from shapely.geometry import Point, Polygon

board = json.loads(Path(sys.argv[1]).read_text())
def rows(kind):
    return [e for e in board if e["type"] == kind]
def xy(element):
    return element["x"], element["y"]

parts = {p["name"]: p for p in rows("source_component")}
pcb_parts = {p.get("source_component_id"): p for p in rows("pcb_component")}
pcb_ports = {p.get("source_port_id"): p for p in rows("pcb_port")}
pins = {(p["source_component_id"], p["name"]): p for p in rows("source_port")}
def pin(ref, terminal):
    return pins[parts[ref]["source_component_id"], terminal]

for ref, supplier in (("Y_OSC0", "C439045"), ("C_OSC0_IN", "C285151"),
                      ("C_OSC0_OUT", "C285151"), ("R_OSC0_DRIVE", "C21189"),
                      ("R_OSC0_BIAS", "C525710")):
    part = parts[ref]
    assert part["supplier_part_numbers"]["jlcpcb"] == [supplier]
    assert bool(pcb_parts[part["source_component_id"]].get("do_not_place")) == (ref == "R_OSC0_BIAS")
clock = {t["name"]:t for t in rows("source_trace") if (t.get("name") or "").startswith("OSC0_")}
groups = [
    ("OSC0_INPUT", "OSC0_IN_LOAD", "OSC0_BIAS_IN"),
    ("OSC0_OUTPUT", "OSC0_BIAS_OUT"),
    ("OSC0_DRIVE", "OSC0_OUT_LOAD"),
]
assert len(clock) == 7
keys = []
for group in groups:
    key, = {clock[name]["subcircuit_connectivity_map_key"] for name in group}
    keys.append(key)
    for name in group:
        source = clock[name]
        trace, = [t for t in rows("pcb_trace") if t.get("source_trace_id") == source["source_trace_id"]]
        route = trace["route"]
        assert all(p["route_type"] == "wire" and p["layer"] == "top" for p in route), name
        ends = [xy(pcb_ports[i]) for i in source["connected_source_port_ids"]]
        assert all(dist(xy(node), end) < 1e-5 for node,end in zip((route[0], route[-1]),ends)), name
assert len(set(keys)) == len(groups)
gnd, = [n for n in rows("source_net") if n["name"] == "GND"]
pour, = [p for p in rows("pcb_copper_pour") if p["source_net_id"] == gnd["source_net_id"] and p["layer"] == "inner1"]
shape = pour["brep_shape"]
boundary = lambda ring: [xy(v) for v in ring["vertices"]]
plane = Polygon(boundary(shape["outer_ring"]), [boundary(r) for r in shape["inner_rings"]])
for ref, terminal in (("U1","V11"),("Y_OSC0","pin2"),("Y_OSC0","pin4"),
                      ("C_OSC0_IN","pin2"),("C_OSC0_OUT","pin2")):
    port = pin(ref,terminal)
    pp = pcb_ports[port["source_port_id"]]
    pad, = [p for p in rows("pcb_smtpad") if p.get("pcb_port_id") == pp["pcb_port_id"]]
    for via in rows("pcb_via"):
        if set(via["layers"]) != {"top","inner1"} or via.get("subcircuit_connectivity_map_key") != gnd["subcircuit_connectivity_map_key"]:
            continue
        dx,dy = abs(via["x"]-pad["x"]), abs(via["y"]-pad["y"])
        if "radius" in pad:
            inside = dist(xy(via),xy(pad)) <= pad["radius"]
        else:
            inside = dx <= pad["width"]/2 and dy <= pad["height"]/2
        if inside and plane.covers(Point(*xy(via)).buffer(via["outer_diameter"]/2)):
            break
    else:
        raise ValueError(f"No L2 ground contact for {ref}.{terminal}")
print("OSC0 has seven top-layer routes, five local L2 ground contacts and a DNP bias resistor.")
