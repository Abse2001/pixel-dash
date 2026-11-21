"""Verify electrical polarity and the keyed physical orientation of the PCB PH header."""
import json
import math
import sys
from pathlib import Path

a = json.loads(Path(sys.argv[1]).read_text())
parts = {e["name"]:e for e in a if e["type"]=="source_component"}
header = parts["J_LIPO"]
assert header["supplier_part_numbers"]["jlcpcb"] == ["C173752"]
foot, = [p for p in a if p["type"]=="pcb_component" and p.get("source_component_id")==header["source_component_id"]]
pins = {(p["source_component_id"],p["name"]):p for p in a if p["type"]=="source_port"}
def pin(part, label):
    return pins[parts[part]["source_component_id"],label]
ground, = [n for n in a if n["type"]=="source_net" and n["name"]=="GND"]
plus, minus = pin("J_LIPO","pin1"), pin("J_LIPO","pin2")
assert plus["subcircuit_connectivity_map_key"] == pin("U_LIPO_CHARGER","BAT")["subcircuit_connectivity_map_key"]
assert minus["subcircuit_connectivity_map_key"] == ground["subcircuit_connectivity_map_key"]
assert plus["subcircuit_connectivity_map_key"] != minus["subcircuit_connectivity_map_key"]
def location(pin):
    pp, = [p for p in a if p["type"]=="pcb_port" and p.get("source_port_id")==pin["source_port_id"]]
    pad, = [p for p in a if p["type"]=="pcb_plated_hole" and p.get("pcb_port_id")==pp["pcb_port_id"]]
    return complex(pad["x"],pad["y"])
pos, neg = location(plus), location(minus)
insertion = foot["cable_insertion_center"]
toward_cable = complex(insertion["x"],insertion["y"]) - (pos+neg)/2
# Adafruit BQ24074 reference footprint in its top view has the cable on +Y
# and BATT.1 on +X. A proper PCB rotation preserves this signed area.
assert (toward_cable.conjugate() * (pos-neg)).imag < 0
assert math.isclose(abs(pos-neg),2.0,abs_tol=0.001)
print("J_LIPO keyed header: contact 1 battery positive, contact 2 ground, 2 mm pitch.")
