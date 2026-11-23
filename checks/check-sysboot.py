"""Decode SYSBOOT from the actual source ports, resistor pins, and rail nets."""
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("board", type=Path)
parser.add_argument("--control-status", type=lambda s: int(s, 0),
                    help="Cold-latched AM3354 CONTROL_STATUS value read at 0x44E10040")
args = parser.parse_args()
circuit = json.loads(args.board.read_text())
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

if args.control_status is not None:
    if not 0 <= args.control_status <= 0xffffffff:
        parser.error("CONTROL_STATUS must be an unsigned 32-bit register value")
    # TRM Table 9-14 places straps 15:8 in register bits 23:16.
    latched = ((args.control_status >> 8) & 0xff00) | (args.control_status & 0xff)
    changed = [bit for bit in range(16) if (latched ^ word) & (1 << bit)]
    if changed:
        raise SystemExit(f"Latched SYSBOOT {latched:#06x} differs at bits {changed}")
    print(f"Latched SYSBOOT {latched:#06x} matches the fitted strap intent.")
