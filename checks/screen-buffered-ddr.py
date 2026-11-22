"""Hot-load and shutdown screen for the sequenced TPS22975 DDR interface supply."""
import argparse
import json
import math
import re
from pathlib import Path

from hdi_build import WURTH

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("board", type=Path)
parser.add_argument("sheet_report", type=Path)
args = parser.parse_args()
board = json.loads(args.board.read_text())
parts = {e["name"]: e for e in board if e["type"] == "source_component"}
assert parts["U_DDR_SWITCH"]["manufacturer_part_number"] == "TPS22975DSGR"
assert parts["U_DDR_SWITCH"]["supplier_part_numbers"]["jlcpcb"] == ["C524777"]
assert parts["R_DDR_SW_OUT"]["resistance"] == 47 and parts["R_DDR_SW_EN"]["resistance"] == 220
assert math.isclose(parts["C_DDR_SW_CT"]["capacitance"], 1e-9)
assert math.isclose(parts["C_DDR_SW_EN"]["capacitance"], 22e-6)
assert math.isclose(parts["C_DDR_SW_IN"]["capacitance"], 10e-6)
caps = json.loads((Path(__file__).resolve().parents[1] / "am3354/bypass-placement.json").read_text())
cap_uf = sum(parts[f"C_DDR{i}"]["capacitance"] * 1e6 for i, x in enumerate(caps, 1) if x["chip"] == "U1")
assert math.isclose(parts["C_DDR_SW_LOAD"]["capacitance"], 47e-6)
cap_uf += parts["C_DDR_SW_LOAD"]["capacitance"]*1e6
report = args.sheet_report.read_text()
def finest(pattern):
    rows = [(float(h), float(r)) for h,r in re.findall(pattern, report)]
    if len(rows) < 2:
        raise ValueError("Missing mesh refinement results")
    return min(rows)[1]

sheet = finest(r"buffered mesh ([\d.]+) mm: ([\d.]+) mOhm")
ret = finest(r"three EP returns, mesh ([\d.]+) mm: ([\d.]+) mOhm")
traces = {e["pcb_trace_id"]: e for e in board if e["type"] == "pcb_trace"}
vias = {e["pcb_via_id"]: e for e in board if e["type"] == "pcb_via"}
def trace_r(trace):
    r = 0
    for a,b in zip(trace["route"], trace["route"][1:]):
        if a["route_type"] != "wire" or b["route_type"] != "wire" or a["layer"] != b["layer"]:
            raise ValueError(f"Update resistance model for {trace['pcb_trace_id']}")
        r += math.hypot(a["x"]-b["x"],a["y"]-b["y"]) / a["width"] * .01724/WURTH.foil
    return r

input_sheet = finest(r"switch input mesh ([\d.]+) mm: ([\d.]+) mOhm")
forward = trace_r(traces["pcb_ddr_supply_switch_output"])
for via_name in ("lower_bank", "balls"):
    v = vias["via_ddr_supply_" + via_name]
    assert len(v["layers"]) == 4
    forward += .01724 * WURTH.outer_to_outer / (math.pi * WURTH.wall * (v["hole_diameter"] + WURTH.wall))
row = finest(r"CPU row mesh ([\d.]+) mm: ([\d.]+) mOhm")
loop = input_sheet + forward + sheet + ret + row
# Worst bleed current calculated at the high rail and low resistor tolerance.
total = .250 + 1.350*1.02/(47*.99)
print(f"Full current to E5 through one VIN and one VOUT land. 20 C traces/barrels {forward:.3f}, "
      f"drilled VIN feed {input_sheet:.3f}, L4 feed {sheet:.3f}, drilled L1 CPU row {row:.3f}, CPU-to-regulator return {ret:.3f}, loop {loop:.3f} mOhm.")
print(f"CPU 250 mA plus worst output bleed; screen all series sections at {total*1000:.2f} mA.")
print("TPS22975 upper tabulated hot RON at 5 V VBIAS near this VIN is 25 mOhm; 34/40 mOhm screens "
      "bracket published bias corners and an added sensitivity. Data-sheet test current is 200 mA.")
print("temp_C,conductance_fraction,switch_mOhm,loop_mOhm,dc_reserve_mV,dynamic_reserve_mV")
worst = math.inf
for temp in (80,105):
    for fraction in (1., .8):
        board_r = loop*(1+.00393*(temp-20))/fraction
        for ron in (34,40):
            drop = total*(board_r+ron)
            dc = 40-drop
            # TI's separate -2.5% dynamic-source case, plus an illustrative local cap step
            # and 2 mV allocated to ESR/ESL. These require measurement on the actual assembly.
            dynamic = 1000*(1.350*.975-1.283)-drop-100/(cap_uf*.5)-2
            print(f"{temp},{fraction:.2f},{ron},{board_r:.3f},{dc:.3f},{dynamic:.3f}")
            worst = min(worst, dc-5, dynamic)
enable_ms = 220*1.01*parts["C_DDR_SW_EN"]["capacitance"]*1.2*1e3*math.log(1.377/.5)
discharge_ms = 47*1.01*cap_uf*1.2/1000
residual = 1.377*math.exp(-(20-enable_ms)/discharge_ms)
print(f"Sequenced shutdown, ignoring QOD: control below 0.5 V by {enable_ms:.2f} ms; "
      f"CPU rail at next 20 ms strobe {residual*1000:.2f} mV. Verify collapse and reverse current during hard VSYS loss.")
print(f"1 nF CT: TI typical 10–90% ramp 495–595 us at 1.2–1.5 V and 5 V bias. "
      f"At {cap_uf*1.2:.1f} uF and 495 us, 10–90% average capacitive current {(.8*1.377*cap_uf*1.2/495)*1000:.0f} mA.")
print("Engineering headroom screen", "PASS" if worst >= 0 else "FAIL")
print("The 80% conductor area, 50% effective capacitance and 2 mV parasitic allowance are sensitivities. "
      "Confirm input bias, sequencing, source/load steps, effective impedance and heat on hardware.")
raise SystemExit(worst < 0)
