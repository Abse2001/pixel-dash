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

# Match the three polarity strokes to their numbered lands and to the actual
# top legend artwork. Keep the ordinary netlist-only invocation available.
if len(sys.argv) > 2:
    import re
    from zipfile import ZipFile

    with ZipFile(sys.argv[2]) as package:
        artwork = package.read("F_SilkScreen.gbr").decode()
    assert "%FSLAX46Y46*%" in artwork and "%MOMM*%" in artwork
    widths = {code: float(diameter) for code, diameter in
              re.findall(r"%ADD(\d+)C,([\d.]+)\*%", artwork)}
    segments = set()
    aperture = previous = None
    for line in artwork.splitlines():
        select = re.fullmatch(r"D(\d+)\*", line)
        if select:
            aperture = select[1]
        command = re.fullmatch(r"X(-?\d+)Y(-?\d+)D0([12])\*", line)
        if command:
            point = (int(command[1]), int(command[2]))
            if command[3] == "1" and previous and aperture in widths:
                segments.add((frozenset((previous, point)), widths[aperture]))
            previous = point

    marks = {"+": [], "-": []}
    for e in a:
        if e["type"] != "pcb_silkscreen_path" or e.get("pcb_component_id") != foot["pcb_component_id"]:
            continue
        label = e["pcb_silkscreen_path_id"]
        if not label.startswith("ntc_verified_mark_J_LIPO_"):
            continue
        polarity = label.split("_")[-2]
        p, q = (complex(pt["x"], pt["y"]) for pt in e["route"])
        midpoint = (p + q) / 2
        correct, opposite = (pos, neg) if polarity == "+" else (neg, pos)
        assert abs(midpoint - correct) < abs(midpoint - opposite)
        vertices = frozenset((round(z.real * 1e6), round(z.imag * 1e6)) for z in (p, q))
        assert e["layer"] == "top" and (vertices, e["stroke_width"]) in segments, label
        marks[polarity].append((p, q))
    assert len(marks["+"]) == 2 and len(marks["-"]) == 1
    from shapely.geometry import LineString
    strokes = [LineString([(p.real, p.imag), (q.real, q.imag)]) for p, q in marks["+"]]
    assert strokes[0].crosses(strokes[1])
    print("Exported top legend has the plus cross beside BAT and the minus stroke beside GND.")
