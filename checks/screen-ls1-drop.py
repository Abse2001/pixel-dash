"""Screen the DCDC3–LS1–CPU path with explicit copper and load assumptions."""
import json
import math
import sys
from pathlib import Path

board = json.loads(Path(sys.argv[1]).read_text())
parts = {e["name"]: e for e in board if e["type"] == "source_component"}
pmic = parts["U_PMIC"]["source_component_id"]
source, = (e for e in board if e["type"] == "source_port" and
           e["source_component_id"] == pmic and e["name"] == "IN_LS1")
land, = (e for e in board if e["type"] == "pcb_port" and e.get("source_port_id") == source["source_port_id"])
traces = [e for e in board if e["type"] == "pcb_trace"]
upstream, = (e for e in traces if any(p.get("start_pcb_port_id") == land["pcb_port_id"]
                                      or p.get("end_pcb_port_id") == land["pcb_port_id"] for p in e["route"]))
downstream = [e for e in traces if e["pcb_trace_id"].startswith("pcb_ddr_supply_")]
if not downstream:
    raise ValueError("Missing LS1 output route")

# rho in ohm mm, finished foil thickness in mm. One-dimensional series-path estimate.
rho = 1.724e-5
def trace_mohm(group, inner_mm):
    total = 0
    for trace in group:
        route = trace["route"]
        for a, b in zip(route, route[1:]):
            if a["route_type"] != "wire" or b["route_type"] != "wire":
                continue
            if a["layer"] != b["layer"]:
                raise ValueError("Missing layer transition")
            length = math.hypot(a["x"] - b["x"], a["y"] - b["y"])
            thickness = .035 if a["layer"] in ("top", "bottom") else inner_mm
            total += 1000 * rho * length / (thickness * a["width"])
    return total

# Model the contacted depth, even when the drilled barrel continues beyond L3.
# The 1.530 mm span and 0.0764 mm L3-to-L4 separation are provisional.
vias = [e for e in board if e["type"] == "pcb_via"]
barrels = []
for p in upstream["route"]:
    if p["route_type"] == "via":
        via, = (v for v in vias if math.hypot(v["x"] - p["x"], v["y"] - p["y"]) < 1e-5
                and {"top", "bottom"} <= set(v["layers"]))
        barrels.append((via["hole_diameter"], 1.530))
by_id = {v["pcb_via_id"]: v for v in vias}
for name, depth in [("output", 1.530 - .0764), ("upper", .0764),
                    ("bridge_upper", .0764), ("bridge_lower", .0764), ("balls", 1.530)]:
    barrels.append((by_id["via_ddr_supply_" + name]["hole_diameter"], depth))
# Treat the design hole diameter as the finished bore and assume 20 um copper plating.
via_mohm = sum(1000 * rho * depth / (math.pi * .020 * (bore + .020)) for bore, depth in barrels)

assignments = json.loads((Path(__file__).resolve().parents[1] / "am3354/bypass-placement.json").read_text())
caps = [parts[f"C_DDR{i}"] for i, item in enumerate(assignments, 1) if item["chip"] == "U1"]
nominal = sum(c["capacitance"] for c in caps) * 1e6
print(f"LS1 bank: {len(caps)} capacitors, {nominal:.2f} uF nominal. TI nominal window 10–100 uF.")
if not 10 <= nominal <= 100:
    raise ValueError("LS1 nominal output capacitance outside TI window")
print("DCDC3 setpoint 1.350 V, screening at -2%; CPU minimum 1.283 V. LS1 110 mOhm at 300 mA.")
print("Copper screen, 35 um outer foil. Whole CPU load carried through the series feed to L5.")
print("inner_um,temp_C,input_mOhm,output_mOhm,load_mA,trace_drop_mV,barrel_drop_mV,remaining_mV")
for inner in (.035, .0175):
    for temp in (20, 80):
        scale = 1 + .00393 * (temp - 20)
        rin = trace_mohm([upstream], inner) * scale
        rout = trace_mohm(downstream, inner) * scale
        for load in (.150, .225, .300):
            drop = load * (rin + rout)
            remaining = 1000 * (1.350 * .98 - 1.283) - load * 110 - drop - load * via_mohm * scale
            print(f"{inner*1000:g},{temp},{rin:.3f},{rout:.3f},{load*1000:.0f},{drop:.3f},{load * via_mohm * scale:.3f},{remaining:.3f}")
cpu = parts["U1"]["source_component_id"]
ball_ids = {e["name"]: e["source_port_id"] for e in board if e["type"] == "source_port"
            and e["source_component_id"] == cpu}
order = ["E5", "F5", "G5", "H5", "J5", "K5", "L5"]
even_load = farthest_load = 0
for index, (a, b) in enumerate(zip(order, order[1:]), 1):
    branch, = (e for e in board if e["type"] == "source_trace" and
               set(e["connected_source_port_ids"]) == {ball_ids[a], ball_ids[b]})
    copper, = (e for e in traces if e["source_trace_id"] == branch["source_trace_id"])
    resistance = trace_mohm([copper], .035)
    even_load += resistance * index / len(order)
    farthest_load += resistance
print(f"L5 to E5 at 20 C and 35 um top copper: additional {even_load * .300:.3f} mV with "
      f"300 mA split equally across seven balls; {farthest_load * .300:.3f} mV if all current enters E5.")
print("Sensitivity to a 100 mA step lasting 1 us, before regulator response, ESR and ESL:")
for retention in (.5, .75, 1.):
    effective = nominal * retention
    print(f"  {retention:.0%} effective: {effective:.2f} uF, ideal capacitive droop {100/effective:.2f} mV")
print("Barrels assume 20 um plating, 1.530 mm full span, 0.0764 mm L3-to-L4. Excludes L4 spreading, return path, package and transient parasitics. "
      "Load, effective capacitance, finished stack and copper temperature are unverified.")
