"""Measure reset strap and reference endpoints on the module's drilled copper islands."""
import argparse
import csv
import json
from pathlib import Path

here = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("islands", type=Path)
parser.add_argument("--control-status", type=lambda value: int(value, 0))
args = parser.parse_args()
islands = json.loads(args.islands.read_text())
pin_net = {pin: (net, index) for net, groups in islands.items()
           for index, group in enumerate(groups) for pin in group}
def connected(*pins):
    return len({pin_net[pin] for pin in pins}) == 1

with (here / "carrier-pinout.csv").open() as stream:
    connector = {row["signal"]: row for row in csv.DictReader(stream)}
word = 0
print("bit  target  CPU ball  contact  pull-to-CPU  CPU-to-carrier  pull-to-carrier  pull-to-source")
for bit in range(16):
    row = connector[f"LCD_D{bit}"]
    cpu = row["module_terminal"]
    carrier = "J_CARRIER." + row["contact"]
    resistor = f"R_SYSBOOT{bit}"
    expected = (resistor + ".pin2", cpu, carrier)
    assert {pin_net[pin][0] for pin in expected} == {f"SYSBOOT{bit}_SENSE"}
    rail = pin_net[resistor + ".pin1"][0]
    assert rail in {"GND_INTERNAL", "VDD_IO_3V3_SEQ"}
    high = rail == "VDD_IO_3V3_SEQ"
    word |= int(high) << bit
    source = "U_PMIC.DCDC4" if high else "U_PMIC.EP"
    print(bit, int(high), cpu, row["contact"], connected(expected[0], cpu),
          connected(cpu, carrier), connected(expected[0], carrier), connected(resistor + ".pin1", source))
assert word == 0x4017, hex(word)
print(f"Fitted word 0x{word:04x}. VDDSHV6 N5/P5 to DCDC4:",
      connected("U1.N5", "U_PMIC.DCDC4"), connected("U1.P5", "U_PMIC.DCDC4"))
print("PGOOD to PWRONRSTn:", connected("U_PMIC.PGOOD", "U1.B15"))
if args.control_status is not None:
    raw = args.control_status
    if not 0 <= raw <= 0xffffffff:
        parser.error("CONTROL_STATUS must be an unsigned 32-bit word")
    latched = ((raw >> 8) & 0xff00) | (raw & 0xff)
    if latched != word:
        raise SystemExit(f"Cold-latched word 0x{latched:04x}. Mismatch mask 0x{latched ^ word:04x}")
    print(f"Supplied cold-latched register matches fitted word 0x{latched:04x}.")
checks = {
    "CPU switched rail to divider": ["U_DDR_SWITCH.VOUT1", "R_CPU_VREF_HIGH.pin2"],
    "CPU divider bottom return": ["R_CPU_VREF_LOW.pin2", "U_PMIC.EP"],
    "CPU midpoint to bypass and J4": ["R_CPU_VREF_HIGH.pin1", "R_CPU_VREF_LOW.pin1", "C_CPU_VREF.pin1", "U1.J4"],
    "CPU reference bypass return": ["C_CPU_VREF.pin2", "U_PMIC.EP"],
    "DRAM direct DCDC3 to divider": ["L_PMIC_DDR.pin2", "R_VREF_HIGH.pin2"],
    "DRAM divider bottom return": ["R_VREF_LOW.pin2", "U_PMIC.EP"],
    "DRAM divider to DQ bypass, H1 and CA feed": ["R_VREF_HIGH.pin1","R_VREF_LOW.pin1","C_VREF_DQ.pin1","U_DDR.H1","R_VREF_CA.pin2"],
    "DRAM CA feed to bypass and M8": ["R_VREF_CA.pin1","C_VREF_CA.pin1","U_DDR.M8"],
    "DRAM DQ/CA bypass returns": ["C_VREF_DQ.pin2", "C_VREF_CA.pin2", "U_PMIC.EP"],
}
for name, pins in checks.items():
    print(name, connected(*pins))
assert connected("C_H1_VREF.pin1", "U_DDR.H1")
assert connected("C_H1_VREF.pin2", "U_PMIC.EP")
print("DRAM H1 local DQ reference bypass and return: connected")
assert connected(*checks["DRAM divider bottom return"])
assert connected("R_VREF_LOW.pin1", "C_VREF_DQ.pin1")
assert connected(*checks["CPU midpoint to bypass and J4"])
assert connected("C_CPU_VREF.pin2", "U_PMIC.EP")
print("CPU J4 local reference bypass and return: connected")
assert pin_net["U1.J4"][0] != pin_net["U_DDR.H1"][0]
assert pin_net["U_DDR_SWITCH.VOUT1"][0] != pin_net["L_PMIC_DDR.pin2"][0]
