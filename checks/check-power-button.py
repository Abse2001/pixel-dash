"""Check the replacement power key, protected inputs, PMIC and RTC controls."""
import json
import math
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
for line, ball in (("SCL", "C16"), ("SDA", "C17")):
    ref = "R_PMIC_" + line
    assert components[ref]["resistance"] == 2200
    assert components[ref]["supplier_part_numbers"]["jlcpcb"] == ["C2906920"]
    assert key(ref, "pin1") == key("U_PMIC", line) == key("U1", ball)
    assert key(ref, "pin2") == nets["VDD_IO_3V3_SEQ"]
assert len({key("U_PMIC", "SCL"), key("U_PMIC", "SDA"), nets["VDD_IO_3V3_SEQ"], nets["GND"]}) == 4

pcb_ports = {e["source_port_id"]: e for e in elements if e["type"] == "pcb_port" and "source_port_id" in e}
def pcb_port(ref, pin):
    return pcb_ports[ports[components[ref]["source_component_id"], pin]["source_port_id"]]

for ref_a, pin_a, ref_b, pin_b in (
    ("U_PMIC", "SCL", "R_PMIC_SCL", "pin1"),
    ("U_PMIC", "SDA", "R_PMIC_SDA", "pin1"),
    ("R_PMIC_SCL", "pin2", "R_PMIC_SDA", "pin2"),
):
    a, b = pcb_port(ref_a, pin_a), pcb_port(ref_b, pin_b)
    for t in elements:
        if t["type"] != "pcb_trace":
            continue
        path = t["route"]
        first, last = path[0], path[-1]
        pads = (first.get("start_pcb_port_id"), last.get("end_pcb_port_id"))
        if set(pads) != {a["pcb_port_id"], b["pcb_port_id"]}:
            continue
        assert all(p.get("layer") == "top" for p in path)
        for end, expected in zip((first, last), (a, b) if pads[0] == a["pcb_port_id"] else (b, a)):
            # tscircuit clips wide PMIC lands to their edge and keeps the small resistor lands centered.
            pad, = [p for p in elements if p["type"] == "pcb_smtpad" and p.get("pcb_port_id") == expected["pcb_port_id"]]
            delta = complex(end["x"]-pad["x"], end["y"]-pad["y"])
            angle = math.radians(-pad.get("ccw_rotation", 0))
            local = delta * complex(math.cos(angle), math.sin(angle))
            assert abs(local.real) <= pad["width"]/2 + 0.001 and abs(local.imag) <= pad["height"]/2 + 0.001
        break
    else:
        raise ValueError(f"Missing copper between {ref_a}.{pin_a} and {ref_b}.{pin_b}")
print("PMIC I2C0 pull-ups connect to the sequenced I/O net and have three local top-copper traces.")

ball_map = json.loads((Path(__file__).resolve().parents[1] / "am3354/processor-balls.json").read_text())
bank = {ball for ball, signal in ball_map.items() if signal == "VDDSHV6"}
assert len(bank) == 9
assert all(key("U1", ball) == nets["VDD_IO_3V3_SEQ"] for ball in bank)
print("All nine VDDSHV6 lands share the I2C0 pull-up supply in the source netlist.")
