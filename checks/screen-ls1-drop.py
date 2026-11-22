"""Screen the DCDC3–LS1–CPU path with explicit copper and load assumptions."""
import argparse
from hdi_build import LEGACY, WURTH
import csv
import json
import math
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("board", type=Path)
parser.add_argument("--pour-mohm", type=float, help="L4 spreading resistance from the same export at 35 um and 20 C")
parser.add_argument("--direct-pour-mohm", type=float, help="Resistance from the direct L4 feed to the CPU supply via in the same export")
parser.add_argument("--sheet-network-report", type=Path, help="Gerber/drill sheet solve from estimate-ls1-pours.py --joined")
parser.add_argument("--wurth", action="store_true")
args = parser.parse_args()
stack = WURTH if args.wurth else LEGACY
inner_cases = (stack.foil,) if args.wurth else (.035, .0175)
if args.wurth and (args.pour_mohm is not None or args.direct_pour_mohm is not None):
    parser.error("Use a matching --sheet-network-report for the Würth profile")
if args.direct_pour_mohm is not None and not (math.isfinite(args.direct_pour_mohm) and args.direct_pour_mohm > 0):
    parser.error("Direct-feed spreading resistance must be positive and finite")
if args.pour_mohm is not None and not (math.isfinite(args.pour_mohm) and args.pour_mohm > 0):
    parser.error("Spreading resistance must be positive and finite")
board = json.loads(args.board.read_text())
parts = {e["name"]: e for e in board if e["type"] == "source_component"}
pmic = parts["U_PMIC"]["source_component_id"]
source, = (e for e in board if e["type"] == "source_port" and
           e["source_component_id"] == pmic and e["name"] == "IN_LS1")
land, = (e for e in board if e["type"] == "pcb_port" and e.get("source_port_id") == source["source_port_id"])
traces = [e for e in board if e["type"] == "pcb_trace"]
upstream, = (e for e in traces if any(p.get("start_pcb_port_id") == land["pcb_port_id"]
                                      or p.get("end_pcb_port_id") == land["pcb_port_id"] for p in e["route"]))
downstream = [e for e in traces if e["pcb_trace_id"].startswith("pcb_ddr_supply_")]
direct = [e for e in downstream if e["pcb_trace_id"].startswith("pcb_ddr_supply_lower_bank_")]
downstream = [e for e in downstream if e not in direct]
if args.direct_pour_mohm is not None and not direct:
    parser.error("This layout has no direct feed to the lower LS1 bank")
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
            thickness = stack.foil if a["layer"] in ("top", "bottom") else inner_mm
            total += 1000 * rho * length / (thickness * a["width"])
    return total

# Model the contacted depth, even when the drilled barrel continues beyond L3.
# The 1.530 mm span and 0.0764 mm L3-to-L4 separation are provisional.
vias = [e for e in board if e["type"] == "pcb_via"]
barrels = []
for p in upstream["route"]:
    if p["route_type"] == "via":
        via, = (v for v in vias if math.hypot(v["x"] - p["x"], v["y"] - p["y"]) < 1e-5
                and {p["from_layer"], p["to_layer"]} <= set(v["layers"]))
        span = {p["from_layer"], p["to_layer"]}
        depth = {frozenset(("top","inner1")): stack.outer_to_inner,
                 frozenset(("top","bottom")): stack.outer_to_outer}[frozenset(span)]
        barrels.append((via["hole_diameter"], depth))
if len(barrels) != 2:
    raise ValueError("Update the IN_LS1 barrel model for the changed upstream topology")
by_id = {v["pcb_via_id"]: v for v in vias}
for name, depth in [("output", stack.outer_to_outer - stack.outer_to_inner), ("upper", stack.outer_to_inner),
                    ("bridge_upper", stack.outer_to_inner), ("bridge_lower", stack.outer_to_inner), ("balls", stack.outer_to_outer)]:
    barrels.append((by_id["via_ddr_supply_" + name]["hole_diameter"], depth))
# Treat the design hole diameter as the finished bore and assume 20 um copper plating.
via_mohm = sum(1000 * rho * depth / (math.pi * stack.wall * (bore + stack.wall)) for bore, depth in barrels)

assignments = json.loads((Path(__file__).resolve().parents[1] / "am3354/bypass-placement.json").read_text())
caps = [parts[f"C_DDR{i}"] for i, item in enumerate(assignments, 1) if item["chip"] == "U1"]
for cap in caps:
    if cap["manufacturer_part_number"] not in ("CL21A226MAQNNNE", "CL05B104KO5NNNC"):
        raise ValueError(f"Verify the LS1 X5R/X7R dielectric and derating for {cap['name']}")
nominal = sum(c["capacitance"] for c in caps) * 1e6
print(f"LS1 bank: {len(caps)} capacitors, {nominal:.2f} uF nominal. TI nominal window 10–100 uF.")
if not 10 <= nominal <= 100:
    raise ValueError("LS1 nominal output capacitance outside TI window")
print("DCDC3 setpoint 1.350 V, screening at -2%; CPU minimum 1.283 V. LS1 110 mOhm at 300 mA.")
print(f"Copper screen, {stack.foil*1000:g} um outer foil. Whole CPU load carried through the series feed to L5.")
print("inner_um,temp_C,input_mOhm,output_mOhm,load_mA,trace_drop_mV,barrel_drop_mV,remaining_mV")
for inner in inner_cases:
    for temp in (20, 80):
        scale = 1 + .00393 * (temp - 20)
        rin = trace_mohm([upstream], inner) * scale
        rout = trace_mohm(downstream, inner) * scale
        for load in (.150, .225, .250, .300):
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
    resistance = trace_mohm([copper], stack.foil)
    even_load += resistance * index / len(order)
    farthest_load += resistance
print(f"L5 to E5 at 20 C and {stack.foil*1000:g} um top copper: additional {even_load * .300:.3f} mV with "
      f"300 mA split equally across seven balls; {farthest_load * .300:.3f} mV if all current enters E5.")
if args.pour_mohm is not None:
    series = trace_mohm([upstream, *downstream], .035) + via_mohm + args.pour_mohm + even_load
    available = 1000 * (1.350 * .98 - 1.283)
    print("AM335x Table 5-10 estimates 250 mA worst-case VDDS_DDR current. TPS65218D0 specifies 110 mOhm at 300 mA, 1.35 V, DDR3L at 333 MHz.")
    print(f"35 um, 20 C, equal ball loads: board series resistance to E5 {series:.3f} mOhm including {args.pour_mohm:.3f} mOhm in L4.")
    for load in (.250, .300):
        headroom = available - load * 110
        print(f"  {load*1000:.0f} mA: pre-board allowance {headroom:.3f} mV, modeled board drop {series*load:.3f} mV, remaining {headroom-series*load:.3f} mV.")
    print(f"Zero-margin current in this DC scenario: {1000*available/(110+series):.1f} mA before return drop, package, ripple and transients.")
common = [upstream] + [e for e in downstream if e["pcb_trace_id"] in {
        "pcb_ddr_supply_ls1", "pcb_ddr_supply_ls1_flare", "pcb_ddr_supply_cpu"}]
if args.direct_pour_mohm is not None:
    # Screen one complete path to avoid crediting overlapping copper twice.
    # First two barrels are the IN_LS1 feed. The source and ball barrels are common to both routes.
    direct_barrels = barrels[:2] + [(by_id["via_ddr_supply_" + name]["hole_diameter"], depth)
        for name, depth in [("output", stack.outer_to_outer-stack.outer_to_inner), ("lower_bank", stack.outer_to_inner), ("balls", stack.outer_to_outer)]]
    rbarrel = sum(1000*rho*depth/(math.pi*stack.wall*(bore+stack.wall)) for bore, depth in direct_barrels)
    print("Direct L3-to-lower-bank feed to E5, with the original parallel path omitted, equal CPU ball loads:")
    for inner, temp in [(.035,20), (.035,80), (.0175,20), (.0175,80)]:
        scale = 1+.00393*(temp-20)
        series = (trace_mohm([*common, *direct],inner) + rbarrel + args.direct_pour_mohm + even_load)*scale
        print(f"  inner {inner*1000:g} um, {temp} C: {series:.3f} mOhm; remaining at 250 mA {40-.250*(110+series):.3f} mV, at 300 mA {40-.300*(110+series):.3f} mV before return and transient losses.")
if args.sheet_network_report is not None:
    lines = args.sheet_network_report.read_text().splitlines()
    header = "pitch_mm,inner_um,outer_um,joined_L3_output_to_L4_balls_mOhm_at_20C"
    table = lines[lines.index(header):]
    rows = csv.DictReader(table[:next((i for i, line in enumerate(table) if line.startswith(("drill", "Single L2 return"))), len(table))])
    by_foil = {}
    for row in rows:
        foil = float(row["inner_um"])
        pitch = float(row["pitch_mm"])
        resistance = float(row["joined_L3_output_to_L4_balls_mOhm_at_20C"])
        if float(row["outer_um"]) != stack.foil*1000 or not (pitch > 0 and resistance > 0):
            raise ValueError("Invalid copper mesh result")
        if foil not in by_foil or pitch < by_foil[foil][0]:
            by_foil[foil] = (pitch, resistance)
    if set(by_foil) != {v*1000 for v in inner_cases} or not direct:
        raise ValueError("Expected matching foil cases and both physical feeds")
    common_barrels = barrels[:2] + [(by_id["via_ddr_supply_output"]["hole_diameter"], stack.outer_to_outer-stack.outer_to_inner),
                                    (by_id["via_ddr_supply_balls"]["hole_diameter"], stack.outer_to_outer)]
    rbarrel = sum(1000*rho*depth/(math.pi*stack.wall*(bore+stack.wall)) for bore, depth in common_barrels)
    print(f"Both physical feeds with their shared copper counted once, {stack.foil*1000:g} um outer foil, equal ball loads:")
    for foil, (pitch, resistance) in sorted(by_foil.items(), reverse=True):
        cold = trace_mohm(common, foil/1000) + resistance + rbarrel + even_load
        for temp in (20,80):
            board_r = cold*(1+.00393*(temp-20))
            print(f"  inner {foil:g} um, {temp} C, grid {pitch:g} mm: {board_r:.3f} mOhm; remaining at 250 mA {40-.250*(110+board_r):.3f} mV, at 300 mA {40-.300*(110+board_r):.3f} mV before return and transient losses.")
print("Sensitivity to a 100 mA step lasting 1 us, before regulator response, ESR and ESL:")
for retention in (.5, .75, 1.):
    effective = nominal * retention
    print(f"  {retention:.0%} effective: {effective:.2f} uF, ideal capacitive droop {100/effective:.2f} mV")
print(f"{stack.name}. Assumed barrel wall {stack.wall*1000:g} um, full span {stack.outer_to_outer:g} mm, L3-to-L4 {stack.outer_to_inner:g} mm. The trace/barrel table excludes L4 spreading, return path, package and transient parasitics. "
      "Load, effective capacitance, finished stack and copper temperature are unverified.")
