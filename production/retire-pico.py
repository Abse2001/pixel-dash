"""Extract retained physical subsystems from the verified 5b7d96d handheld."""
import csv
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from shapely.geometry import LineString, Point
from shapely.strtree import STRtree

raw = Path(sys.argv[1]).read_bytes()
if hashlib.sha256(raw).hexdigest() != "820e642e8f1458844f6975471faaa5e4b34993c9776c1c19faacebe051199b58":
    raise ValueError("Expected the verified handheld before processor replacement")
root = Path(sys.argv[2])
root.mkdir(parents=True, exist_ok=True)
board = json.loads(raw)
def items(kind):
    return [e for e in board if e["type"] == kind]
def eid(e):
    return e.get(e["type"] + "_id")
retired_parts = {}
manual = {
    "retired battery hard-off control": "J_PWR_SW J_PWR_SW_body J_PWR_SW_actuator Q_AA_OFF Q_LIPO_OFF D_CONTROL_AA D_CONTROL_LIPO R_CONTROL_PULLUP",
    "compute and memory": "U1 U2 U_PSRAM R_PSRAM_CE C_FLASH C_PSRAM C_PSRAM_BULK C_QSPI_USB",
    "oscillator": "U_XTAL C_XIN C_XOUT R_XOUT",
    "processor reset and programming": "U_BOOTSEL U_RUN R_RUN R_BOOT R_BOOTSEL TP_SWDIO TP_SWCLK",
    "on-chip regulator and bypass": "U_CORE_INDUCTOR R_VREG_AVDD C_VREG_IN C_CORE C_VREG_AVDD C_ADC",
    "USB transceiver series termination": "R_USB_DM R_USB_DP",
}
for reason, names in manual.items():
    retired_parts.update(dict.fromkeys(names.split(), reason))
for e in items("source_component"):
    name = e["name"]
    if "GPU" in name and name not in {"R_GPU_LCD_WR", "R_GPU_LCD_RD"}:
        retired_parts[name] = "second processor and dedicated support"
    if name.startswith(("C_IOVDD", "C_DVDD")):
        retired_parts[name] = "processor supply bypass"
parts = {e["name"]: e for e in items("source_component")}
assert not retired_parts.keys() - parts.keys()
with (root/"removed-parts.csv").open("w") as f:
    writer = csv.writer(f)
    writer.writerow(["Former designator", "Manufacturer part", "JLCPCB part", "Function removed"])
    for name, reason in sorted(retired_parts.items()):
        e = parts[name]
        writer.writerow([name, e.get("manufacturer_part_number"), " ".join(e.get("supplier_part_numbers", {}).get("jlcpcb", [])), reason])

dead = {eid(parts[n]) for n in retired_parts}
old_net = re.compile(r"^(?:V1V1$|BAT_OFF_GATE$|BAT_CONTROL_OR$|GPU_|GRAPHICS_|THROUGH_(?:QSPI|PSRAM|SWD|SWCLK|BOOTSEL|RUN_PULLUP))")
dead.update(eid(e) for e in items("source_net") if old_net.search(e["name"]))
dead.update(eid(e) for e in items("source_bus") if not e["name"].startswith("BAT_"))
retired_sheets = {"processor", "core-power", "flash", "psram", "gpu", "gpu-power", "gpu-memory"}
sheets = {e["name"]: eid(e) for e in items("schematic_sheet")}
old_sheets = {sheets[name] for name in retired_sheets}
dead.update(old_sheets)
# The panel series resistor, read pull-up and mode strap were drawn on GPU
# sheets. Move their symbols, labels and pin graphics with the components.
symbol_ids = {eid(e) for e in items("schematic_component")
              if e.get("source_component_id") not in dead and e.get("schematic_sheet_id") in old_sheets}
for e in board:
    if e.get("schematic_sheet_id") in old_sheets and (eid(e) in symbol_ids or e.get("schematic_component_id") in symbol_ids):
        e["schematic_sheet_id"] = sheets["display"]
for e in items("source_board"):
    e["title"] = "Pixel Dash AM3354 handheld"
# Remove shared ground fills for regeneration on the integrated board. Old
# negative clearances and isolated thermal islands cannot represent new parts.
dead.update(eid(e) for e in items("pcb_copper_pour"))
def references(e):
    for key, value in e.items():
        if key == e["type"] + "_id":
            continue
        if key.endswith("_id") and isinstance(value, str):
            yield value
        if key.endswith("_ids") and isinstance(value, list):
            yield from value
def propagate():
    while True:
        new = {eid(e) for e in board if eid(e) and eid(e) not in dead and any(i in dead for i in references(e))}
        if not new:
            break
        dead.update(new)
propagate()
# A manually placed via on a shared net can belong to a retired processor.
# Keep it only if retained trace copper reaches its land on a spanned layer.
segments = defaultdict(list)
for t in items("pcb_trace"):
    if eid(t) in dead:
        continue
    for p,q in zip(t["route"],t["route"][1:]):
        layer = p.get("layer",p.get("to_layer"))
        if layer != q.get("layer",q.get("from_layer")) or (p["x"],p["y"]) == (q["x"],q["y"]):
            continue
        segments[layer].append(LineString([(p["x"],p["y"]),(q["x"],q["y"])]).buffer(p.get("width",q.get("width"))/2))
trees = {l:STRtree(g) for l,g in segments.items()}
for v in items("pcb_via"):
    if eid(v) in dead:
        continue
    p = Point(v["x"],v["y"])
    if not any(len(trees[l].query(p,predicate="dwithin",distance=v["outer_diameter"]/2)) for l in v["layers"] if l in trees):
        dead.add(eid(v))
        if v.get("source_trace_id"):
            dead.add(v["source_trace_id"])
propagate()
# Printed legends/fabrication graphics without component ownership are rebuilt
# at assembly review, since some are only anonymous vector strokes.
keep = []
for e in board:
    kind = e["type"]
    if eid(e) in dead or kind.endswith(("_error","_warning")) or kind=="source_project_metadata":
        continue
    if kind.startswith(("pcb_silkscreen","pcb_fabrication_note")) and not e.get("pcb_component_id"):
        continue
    if kind in {"schematic_text","schematic_line","schematic_path","schematic_rect","schematic_circle"} and not e.get("schematic_component_id"):
        continue
    keep.append(e)
(root/"retained.circuit.json").write_text(json.dumps(keep,separators=(",",":")))
print(f"{len(retired_parts)} retired designators, {len(keep)} retained circuit elements")
