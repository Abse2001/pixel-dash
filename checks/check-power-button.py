"""Check the replacement power key, protected inputs, PMIC and RTC controls."""
import json
import sys
from pathlib import Path

elements = json.loads(Path(sys.argv[1]).read_text())
components = {p["name"]: p for p in elements if p["type"] == "source_component"}
assert not {"J_PWR_SW", "J_PWR_SW_body", "J_PWR_SW_actuator", "Q_LIPO_OFF",
            "Q_AA_OFF", "D_CONTROL_AA", "D_CONTROL_LIPO", "R_CONTROL_PULLUP"} & components.keys()
assert {"Q_LIPO_USB_OFF","U_LIPO_UVLO","U_LIPO_CHARGER","Q_USB_BOOST_OFF","U_USB_VALID"} <= components.keys()
assert components["SW_POWER"]["supplier_part_numbers"]["jlcpcb"] == ["C110293"]
assert components["U_PMIC"]["supplier_part_numbers"]["jlcpcb"] == ["C2659099"]
assert components["R_POWER_PB"]["resistance"] == 100000
ports = {(p["source_component_id"], hint):p for p in elements if p["type"] == "source_port"
         for hint in (p["name"], *p.get("port_hints", []))}
def key(ref, terminal):
    p = ports[components[ref]["source_component_id"], terminal]
    return p["subcircuit_connectivity_map_key"]
nets = {e["name"]: e["subcircuit_connectivity_map_key"] for e in elements if e["type"] == "source_net"}
assert "BAT_OFF_GATE" not in nets and "BAT_CONTROL_OR" not in nets
assert key("R_POWER_PB","pin2") == key("U_PMIC","IN_BIAS") == nets["VSYS"]
assert key("SW_POWER","pin1") == key("SW_POWER","pin3") == nets["GND"]
assert key("SW_POWER","pin2") == key("U_PMIC","PB") == key("R_POWER_PB","pin1")
assert key("U_PMIC","PB") not in {nets["VSYS"],nets["GND"]}
for signal, ball in (("PWR_EN","C6"), ("nWAKEUP","C5"), ("nINT","T14"), ("SCL","C16"), ("SDA","C17")):
    assert key("U_PMIC", signal) == key("U1", ball), signal
assert key("R_PMIC_WAKE","pin2") == nets["VDDS_RTC_1V8"]
assert key("R_PMIC_IRQ","pin2") == nets["VDD_IO_3V3_SEQ"]
print("Momentary key, PMIC wake/hold/IRQ/I2C and retained battery protections verified in source.")
