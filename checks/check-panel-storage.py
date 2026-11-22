"""Validate raster pinmux, FPC color order, MMC card detect and touch bias connections."""
import csv
import json
import sys
from pathlib import Path

board = json.loads(Path(sys.argv[1]).read_text())
root = Path(__file__).resolve().parents[1]
parts = {e["name"]: e["source_component_id"] for e in board if e["type"] == "source_component"}
ports = {(e["source_component_id"], e["name"]): e["source_port_id"] for e in board if e["type"] == "source_port"}
traces = {e["source_trace_id"]: e for e in board if e["type"] == "source_trace"}
with (root / "production/interface.csv").open() as f:
    rows = {r["Signal"]: r for r in csv.DictReader(f)}
balls = json.loads((root / "am3354/processor-balls.json").read_text())
# TI SPRZ360 section 3.1.1 Figure 2, in LCD_DATA0 through LCD_DATA23 order.
colors = "R3 R4 R5 R6 R7 G2 G3 G4 G5 G6 G7 B3 B4 B5 B6 B7 R2 B2 R1 G1 B1 R0 G0 B0".split()
contacts = {f"{color}{bit}": start+7-bit for color,start in (("B",12),("G",20),("R",28)) for bit in range(8)}
keys = set()
def check(signal, ball, mode, part, pin):
    row = rows[signal]
    assert (row["Ball"], row["Pad"], int(row["Mode"])) == (ball, balls[ball], mode), signal
    trace = traces["system_" + signal]
    assert set(trace["connected_source_port_ids"]) == {ports[parts["U1"],ball], ports[parts[part],pin]}, signal
    key = trace["subcircuit_connectivity_map_key"]
    assert key not in keys, signal
    keys.add(key)

upper = ["U13","V13","R12","T12","U12","T11","T10","U10"]
for i,color in enumerate(colors):
    ball = next(b for b,p in balls.items() if p == f"LCD_DATA{i}") if i < 16 else upper[i-16]
    check(f"LCD_D{i}", ball, int(i >= 16), "J_LCD", f"pin{contacts[color]}")
for signal,ball,contact,mode in (("PCLK","V5",37,0),("HSYNC","R5",11,0),("VSYNC","U5",10,0),
                                  ("DE","R6",9,0),("RESET","J18",44,7)):
    check("LCD_"+signal, ball, mode, "J_LCD", f"pin{contact}")
for sig,ball,mode in (("SCL","D15",3),("SDA","D16",3),("IRQ","V14",7)):
    check("TOUCH_"+sig,ball,mode,"R_TOUCH_"+sig,"pin1")
check("SD_DETECT","C15",5,"J_SD","CD")
assert traces["system_SD_DAT3"]["subcircuit_connectivity_map_key"] not in keys
print("Validated 24 RGB888 pin assignments, raster timing pads, reset, touch pull-up signal ends and MMC0 detect.")
