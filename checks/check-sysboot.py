"""Decode SYSBOOT from the actual source ports, resistor pins, and rail nets."""
import json
import sys
from pathlib import Path

circuit = json.loads(Path(sys.argv[1]).read_text())
parts = {e["name"]:e for e in circuit if e["type"] == "source_component"}
pins = {(e["source_component_id"],e["name"]):e for e in circuit if e["type"] == "source_port"}
balls = json.loads((Path(__file__).resolve().parents[1]/"am3354/processor-balls.json").read_text())
rails = {e["name"]:e for e in circuit if e["type"]=="source_net"}
traces = [e for e in circuit if e["type"]=="source_trace"]
seen = set()
word = 0
for bit in range(16):
    name = f"R_SYSBOOT{bit}"
    resistor = parts[name]
    assert resistor["resistance"] == 10000, (name, resistor)
    def pin(part, label):
        return pins[part["source_component_id"],label]["source_port_id"]
    a = pin(resistor, "pin1")
    b = pin(resistor, "pin2")
    bias, = [t for t in traces if a in t["connected_source_port_ids"]]
    rail, = [r for r in ("GND","VDD_IO_3V3_SEQ") if rails[r]["source_net_id"] in bias["connected_source_net_ids"]]
    if rail == "VDD_IO_3V3_SEQ":
        word |= 1 << bit
    ball, = [p for p, signal in balls.items() if signal == f"LCD_DATA{bit}"]
    cpu = pin(parts["U1"], ball)
    # RGB888 Figure 2 assigns the low word to R[7:3], G[7:2], B[7:3].
    panel_contact = (32,31,30,29,28,25,24,23,22,21,20,16,15,14,13,12)[bit]
    panel = pin(parts["J_LCD"], f"pin{panel_contact}")
    tap, = [t for t in traces if {cpu,b}.issubset(t["connected_source_port_ids"])]
    bus, = [t for t in traces if {cpu,panel}.issubset(t["connected_source_port_ids"])]
    key = bus["subcircuit_connectivity_map_key"]
    assert key == tap["subcircuit_connectivity_map_key"] and key not in seen
    seen.add(key)
assert word == 0x4017, hex(word)
print(f"16 distinct LCD/SYSBOOT signals decode to {word:#06x}: 24 MHz, MMC0 -> SPI0 -> UART0 -> USB0")
