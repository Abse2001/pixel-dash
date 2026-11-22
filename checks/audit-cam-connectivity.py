"""Walk connected copper and plated barrels in the exported four-layer board."""
import argparse
import csv
import json
import math
import re
import runpy
from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile

from shapely import STRtree
from shapely.geometry import Point, LineString
from shapely.ops import unary_union

from ddr_cam import artwork
from hdi_build import WURTH


LAYERS = ("top", "inner1", "inner2", "bottom")
MEMBERS = ("F_Cu.gbr", "In1_Cu.gbr", "In2_Cu.gbr", "B_Cu.gbr")
CHECKS = Path(__file__).parent


def processor_power(terminals):
    """Compare package balls with the intended power sources in TI SLVUAA9B Table 1."""
    balls = json.loads((CHECKS.parent / "am3354/processor-balls.json").read_text())
    cpu_ddr = "U_DDR_SWITCH.VOUT1"
    groups = {
        "TP_UART_GND.pin1": {"VSS", "VSS_OSC", "VSS_RTC", "VSSA_USB", "VSSA_ADC"},
        "C_PMIC_CORE.pin1": {"VDD_CORE"},
        "C_PMIC_MPU.pin1": {"VDD_MPU"},
        "C_PMIC_RTC_CORE.pin1": {"CAP_VDD_RTC"},
        "C_PMIC_RTC_IO.pin1": {"VDDS_RTC", "RTC_KALDO_ENn"},
        cpu_ddr: {"VDDS_DDR"},
        "U_PMIC.DCDC4": {"VDDSHV1", "VDDSHV2", "VDDSHV3", "VDDSHV4", "VDDSHV5", "VDDSHV6", "VDDA3P3V_USB0", "VDDA3P3V_USB1"},
        "U_PMIC.LDO1": {"VDDS", "VDDS_PLL_DDR", "VDDS_PLL_MPU", "VDDS_PLL_CORE_LCD",
                        "VDDS_OSC", "VDDS_SRAM_CORE_BG", "VDDS_SRAM_MPU_BB",
                        "VDDA_ADC", "VDDA1P8V_USB0", "VDDA1P8V_USB1"},
    }
    failed = False
    for anchor, labels in groups.items():
        expected = sorted(ball for ball, label in balls.items() if label in labels)
        missing = [b for b in expected if terminals["U1." + b] != terminals[anchor]]
        print(f"Processor supply/return to {anchor}: {len(expected) - len(missing)}/{len(expected)} balls connected."
              + (" Open " + ", ".join(missing) if missing else ""))
        failed |= bool(missing)
    memory = json.loads((CHECKS.parent / "am3354/memory-balls.json").read_text())
    dram_balls = sorted(b for b, name in memory.items() if name in {"VDD", "VDDQ"})
    cpu_balls = sorted(b for b, name in balls.items() if name == "VDDS_DDR")
    if not dram_balls or len(cpu_balls) != 7:
        raise ValueError("Unexpected DDR supply ball map")
    dram_nodes = {terminals["U_DDR." + b] for b in dram_balls}
    cpu_nodes = {terminals["U1." + b] for b in cpu_balls}
    direct = sum(terminals["U_DDR." + b] == terminals["C_PMIC_DDR.pin1"] for b in dram_balls)
    separate = not (dram_nodes & cpu_nodes)
    print(f"DDR memory supply to DCDC3 output capacitor: {direct}/{len(dram_balls)} VDD/VDDQ balls connected.")
    print(f"DDR memory supply isolation from CPU VDDS_DDR: {'PASS' if separate else 'SHORT between the two domains'}.")
    failed |= direct != len(dram_balls) or not separate
    bypass = json.loads((CHECKS.parent / "am3354/bypass-placement.json").read_text())
    for ref, anchor, wrong in (("U1", cpu_ddr, dram_nodes), ("U_DDR", "C_PMIC_DDR.pin1", cpu_nodes)):
        caps = [f"C_DDR{i}.pin1" for i, cap in enumerate(bypass, 1) if cap["chip"] == ref]
        fed = sum(terminals[cap] == terminals[anchor] for cap in caps)
        aliased = [cap for cap in caps if terminals[cap] in wrong]
        print(f"{ref} DDR bypass to {anchor}: {fed}/{len(caps)} supplied, "
              f"{len(aliased)} on copper shared with the other load domain.")
        failed |= fed != len(caps) or bool(aliased)
    returns = [f"C_DDR{i}" for i, cap in enumerate(bypass, 1)
               if (cap["chip"], cap["kind"]) in {("U_DDR", "highSpeed"), ("channel", "return")}]
    missing_returns = [ref for ref in returns
                       if terminals[ref + ".pin1"] != terminals["C_PMIC_DDR.pin1"]
                       or terminals[ref + ".pin2"] != terminals["TP_UART_GND.pin1"]]
    print(f"DDR reference bypasses with both DCDC3 and ground lands connected: "
          f"{len(returns) - len(missing_returns)}/{len(returns)}."
          + (f" Open {', '.join(missing_returns)}." if missing_returns else ""))
    failed |= not returns or bool(missing_returns)
    switch_rails = {
        "C_PMIC_DDR.pin1": ["U_DDR_SWITCH.VIN1", "U_DDR_SWITCH.VIN2", "C_DDR_SW_IN.pin1", "U_PMIC.IN_LS1"],
        "U_PMIC.LS1": ["U_DDR_SWITCH.ON", "C_DDR_SW_EN.pin1", "R_DDR_SW_EN.pin1"],
        cpu_ddr: ["U_DDR_SWITCH.VOUT2", "R_DDR_SW_OUT.pin1", "C_DDR_SW_LOAD.pin1"],
        "C_LIPO_BOOST_OUT.pin1": ["U_DDR_SWITCH.VBIAS", "C_DDR_SW_BIAS.pin1"],
        "U_DDR_SWITCH.CT": ["C_DDR_SW_CT.pin1"],
        "TP_UART_GND.pin1": ["U_DDR_SWITCH.EP", "U_DDR_SWITCH.GND", "C_DDR_SW_IN.pin2",
                             "C_DDR_SW_EN.pin2", "C_DDR_SW_BIAS.pin2", "C_DDR_SW_CT.pin2",
                             "R_DDR_SW_EN.pin2", "R_DDR_SW_OUT.pin2", "C_DDR_SW_LOAD.pin2"],
    }
    if len({terminals[k] for k in switch_rails}) != len(switch_rails):
        raise ValueError("DDR switch input, output, enable, CT, bias or ground share copper")
    for anchor, loads in switch_rails.items():
        missing = [p for p in loads if terminals[p] != terminals[anchor]]
        print("DDR switch", anchor, "open: " + ", ".join(missing) if missing else "all terminals connected")
        failed |= bool(missing)
    supply = "C_LIPO_BOOST_OUT.pin1"
    for label in ("C_3V3_IN.pin1", "C_AMP_VDD.pin1", "R_POWER_PB.pin2", "U_PMIC.IN_BU",
                  "U_PMIC.IN_BIAS", "U_PMIC.IN_DCDC1", "U_PMIC.IN_DCDC2", "U_PMIC.IN_DCDC3", "U_PMIC.IN_DCDC4",
                  "U_PMIC.IN_LDO1", "U_PMIC.AC_DET"):
        connected = terminals[label] == terminals[supply]
        print(f"System supply copper {'PASS' if connected else 'OPEN'} {supply} to {label}.")
        failed |= not connected
    ldo = terminals["U_PMIC.LDO1"]
    ldo_ground = terminals["TP_UART_GND.pin1"]
    if "C_PMIC_LDO1.pin1" in terminals:
        correct = (terminals["C_PMIC_LDO1.pin1"] == ldo and
                   terminals["C_PMIC_LDO1.pin2"] == ldo_ground and
                   len({ldo, ldo_ground, terminals["U_PMIC.IN_LDO1"]}) == 3)
        print(f"LDO1 output capacitor, ground and input isolation: {'PASS' if correct else 'FAIL'}.")
        failed |= not correct
    else:
        print("LDO1 output capacitor missing.")
        failed = True
    return failed


def internal_bypass(board, terminals, labels):
    """Inspect fitted capacitor lands on the drilled Gerber networks, TI SPRS717L §5.9."""
    components = {e.get("name"): e for e in board if e["type"] == "source_component"}
    locations = {labels[p["pcb_port_id"]]: (p["x"], p["y"]) for p in board
                 if p["type"] == "pcb_port" and p["pcb_port_id"] in labels}
    paths = {t["source_trace_id"]: t for t in board if t["type"] == "pcb_trace"}
    local = {s["name"]: paths.get(s["source_trace_id"]) for s in board
             if s["type"] == "source_trace" and (s.get("name") or "").startswith("LOCAL_BYPASS_")}
    ground, supply = terminals["TP_UART_GND.pin1"], terminals["U_PMIC.LDO1"]
    stack = WURTH
    depths = dict(top=0, inner1=stack.outer_to_inner,
                  inner2=stack.outer_to_outer-stack.outer_to_inner, bottom=stack.outer_to_outer)
    via_index = {(round(v["x"], 5), round(v["y"], 5)): v for v in board if v["type"] == "pcb_via"}
    ground_key = next(e["subcircuit_connectivity_map_key"] for e in board
                      if e["type"] == "source_net" and e["name"] == "GND")
    outputs = {terminals["U1." + ball] for ball in ("C10", "D9", "D11")}
    isolated = len(outputs | {ground, supply}) == 5
    print("Internal regulator output separation from one another, LDO1 and GND:", "PASS" if isolated else "FAIL")
    passed = isolated
    for ball, nominal, ref in (("C10", 1, "C_VBB_MPU"), ("D9", 1, "C_SRAM_CORE"),
                               ("D11", 1, "C_SRAM_MPU"), ("D10", 10, "C_SRAM_MPU_IN"),
                               ("E9", 10, "C_SRAM_CORE_IN")):
        ball_name = "U1." + ball
        node = terminals[ball_name]
        candidates = []
        for name, part in components.items():
            if not math.isclose(part.get("capacitance", 0), nominal * 1e-6, rel_tol=1e-5):
                continue
            for signal, ret in (("pin1","pin2"), ("pin2","pin1")):
                sig = f"{name}.{signal}"
                if terminals.get(sig) == node and terminals.get(f"{name}.{ret}") == ground:
                    candidates.append((math.dist(locations[ball_name], locations[sig]), name))
        ok = any(name == ref for _, name in candidates) and (nominal == 1 or node == supply)
        nearest = min(candidates) if candidates else None
        print(f"{ball_name} {nominal} uF {ref}: {'CONNECTED' if ok else 'MISSING'}; "
              + (f"nearest qualifying {nearest[1]} at {nearest[0]:.3f} mm land-center distance"
                 if nearest else "no fitted capacitor of this value across the ball and ground"))
        trace = local.get("LOCAL_BYPASS_" + ball)
        if trace:
            route = trace["route"]
            ends = [labels.get(route[0].get("start_pcb_port_id")), labels.get(route[-1].get("end_pcb_port_id"))]
            widths = [p["width"] for p in route if p["route_type"] == "wire"]
            length = sum(math.hypot(a["x"]-b["x"], a["y"]-b["y"]) for a,b in zip(route,route[1:]))
            vias = [p for p in route if p["route_type"] == "via"]
            print(f"  Dedicated path {ends}: {length:.3f} mm planar, {len(vias)} transitions, "
                  f"{min(widths):.3f} mm minimum width.")
            ok &= set(ends) == {ball_name, ref + ".pin1"}
            squares = sum(math.hypot(a["x"]-b["x"], a["y"]-b["y"])/a["width"]
                          for a,b in zip(route, route[1:]) if a["route_type"] == b["route_type"] == "wire")
            resistance = squares * .01724 / stack.foil
            for change in vias:
                v = via_index[round(change["x"], 5), round(change["y"], 5)]
                traversal = abs(depths[change["from_layer"]] - depths[change["to_layer"]])
                resistance += .01724*traversal/(math.pi*stack.wall*(v["hole_diameter"]+stack.wall))
            xy = tuple(round(value, 5) for value in locations[ref + ".pin2"])
            ret = via_index.get(xy, {})
            local_return = (set(ret.get("layers", ())) == {"top", "inner1"} and
                            ret.get("subcircuit_connectivity_map_key") == ground_key and
                            terminals[ref + ".pin2"] == ground)
            ok &= local_return
            print(f"  Forward line and contacted barrel resistance at 20 C: {resistance:.2f} mOhm; "
                  f"L1–L2 ground via in capacitor return land: {local_return}.")
        passed &= ok and trace is not None
    return not passed


def rtc_startup(terminals):
    """Audit the external RTC regulator and sequencer wiring on physical CAM nodes."""
    paths = [
        ("U1.B4", "U1.D7"), ("U1.D7", "C_PMIC_RTC_IO.pin1"),
        ("U1.D6", "C_PMIC_RTC_CORE.pin1"),
        ("U_PMIC.FB5", "C_PMIC_RTC_CORE.pin1"), ("U_PMIC.FB6", "C_PMIC_RTC_IO.pin1"),
        ("U_PMIC.PGOOD_BU", "U1.B5"), ("U_PMIC.nWAKEUP", "U1.C5"),
        ("R_PMIC_WAKE.pin2", "C_PMIC_RTC_IO.pin1"), ("U_PMIC.PWR_EN", "U1.C6"),
        ("U_PMIC.PGOOD", "R_PMIC_POR.pin1"), ("R_PMIC_POR.pin2", "U_PMIC.DCDC4"),
        ("U_PMIC.PGOOD", "U1.B15"), ("U_PMIC.GPIO3", "U1.A10"),
        ("C_PMIC_RTC_CORE.pin2", "TP_UART_GND.pin1"), ("C_PMIC_RTC_IO.pin2", "TP_UART_GND.pin1"),
    ]
    failed = False
    for start, end in paths:
        connected = terminals[start] == terminals[end]
        print(f"Startup copper {'PASS' if connected else 'OPEN'} {start} to {end}.")
        failed |= not connected
    for start, end in [("U1.B4", "U1.D6"), ("U1.D7", "U1.D6"),
                       ("C_PMIC_RTC_IO.pin1", "C_PMIC_RTC_CORE.pin1")]:
        isolated = terminals[start] != terminals[end]
        print(f"RTC isolation {'PASS' if isolated else 'SHORT'} {start} from {end}.")
        failed |= not isolated
    return failed


def sysboot(terminals):
    """Read the bias and sense ends of the 16 fitted strap locations from CAM."""
    balls = json.loads((CHECKS.parent / "am3354/processor-balls.json").read_text())
    ground, high = (terminals[label] for label in ("TP_UART_GND.pin1", "U_PMIC.DCDC4"))
    if ground == high:
        raise ValueError("SYSBOOT bias rails share copper")
    senses = []
    for bit in range(16):
        ball, = [name for name, function in balls.items() if function == f"LCD_DATA{bit}"]
        senses.append(terminals[f"U1.{ball}"])
    digits = []
    for bit, sense in enumerate(senses):
        bias = terminals[f"R_SYSBOOT{bit}.pin1"]
        tap = terminals[f"R_SYSBOOT{bit}.pin2"]
        bias_bit = {ground: "0", high: "1"}.get(bias, "?")
        isolated = sense not in (ground, high) and senses.count(sense) == 1
        connected = sense == tap
        digits.append(bias_bit if connected and isolated else "?")
        print(f"SYSBOOT{bit:02d} bias={bias_bit} CPU_to_resistor={connected} sense_isolated={isolated}")
    word = "".join(reversed(digits))
    print(f"Physical SYSBOOT[15:0] {word}, expected {0x4017:016b}.")
    return word != f"{0x4017:016b}"


def mmc0_power(terminals):
    """Require the sequenced card supply, pull networks and returns in drilled artwork."""
    supply = terminals["U_PMIC.DCDC4"]
    ground = terminals["TP_UART_GND.pin1"]
    legacy = terminals["C_3V3_OUT_A.pin1"]
    passed = len({supply, ground, legacy, terminals["U_PMIC.IN_DCDC4"]}) == 4
    print("MMC0 rail isolation (DCDC4, GND, legacy regulator, VSYS):", "PASS" if passed else "FAIL")
    for node, labels in (
        (supply, ["U1.H14", "U1.J14", "J_SD.VDD", "C_SD.pin1", "C_SD_BULK.pin1"]),
        (ground, ["J_SD.VSS", "C_SD.pin2", "C_SD_BULK.pin2"]),
    ):
        for label in labels:
            ok = terminals[label] == node
            print("MMC0 " + label, "PASS" if ok else "OPEN")
            passed &= ok
    signals = []
    for suffix, contact, ball in (("CMD", "CMD", "G18"), ("DAT0", "DAT0", "G16"),
                                 ("DAT1", "DAT1", "G15"), ("DAT2", "DAT2", "F18"),
                                 ("CS", "CD_DAT3", "F17")):
        signal = terminals["J_SD." + contact]
        signals.append(signal)
        ok = (terminals["R_SD_" + suffix + ".pin2"] == supply
              and terminals["R_SD_" + suffix + ".pin1"] == signal == terminals["U1." + ball])
        print("MMC0 " + contact + " pull, socket and CPU", "PASS" if ok else "OPEN")
        passed &= ok
    for contact, ball in (("CLK", "G17"), ("CD", "C15")):
        signals.append(terminals["J_SD." + contact])
        passed &= signals[-1] == terminals["U1." + ball]
    passed &= len(set(signals) | {supply, ground, legacy, terminals["U_PMIC.IN_DCDC4"]}) == 11
    print("MMC0 sequenced card power and seven distinct links:", "PASS" if passed else "FAIL")
    return not passed


def panel_and_storage(terminals):
    with (CHECKS.parent / "production/interface.csv").open() as f:
        mapped = list(csv.DictReader(f))
    expected = [{f"LCD_D{i}" for i in range(24)} | {"LCD_PCLK", "LCD_DE", "LCD_HSYNC", "LCD_VSYNC", "LCD_RESET"},
                {"SD_CLK", "SD_CMD", "SD_DAT0", "SD_DAT1", "SD_DAT2", "SD_DAT3", "SD_DETECT"}]
    failed = False
    for names, prefix in zip(expected, ("LCD_", "SD_")):
        rows = [r for r in mapped if r["Signal"].startswith(prefix)]
        if {r["Signal"] for r in rows} != names or len(rows) != len(names):
            raise ValueError(f"Incomplete or duplicate {prefix} interface entries")
        reached = []
        for row in rows:
            source = terminals["U1." + row["Ball"]]
            target = terminals[row["Peripheral"] + "." + row["Pin"]]
            if source == target:
                reached.append(row["Signal"])
        print(f"{prefix[:-1]} CPU-to-connector copper {len(reached)}/{len(rows)}. Reached " +
              (", ".join(reached) or "none") + ". Open " + (", ".join(sorted(names - set(reached))) or "none") + ".")
        failed |= len(reached) != len(rows)
    panel_taps = []
    for bit in range(16):
        row, = [r for r in mapped if r["Signal"] == f"LCD_D{bit}"]
        if terminals[f"R_SYSBOOT{bit}.pin2"] == terminals["J_LCD." + row["Pin"]]:
            panel_taps.append(bit)
    print(f"Raster data connector to strap sense pads: {len(panel_taps)}/16; bits {panel_taps}.")
    touch_bias = [pin for pin in ("SDA", "SCL", "IRQ")
                  if terminals[f"R_TOUCH_{pin}.pin2"] == terminals["U_PMIC.DCDC4"]]
    print(f"Touch pull-ups on sequenced DCDC4: {len(touch_bias)}/3 ({', '.join(touch_bias)}).")
    failed |= len(touch_bias) != 3
    for side, ball in (("L", "V17"), ("R", "D18")):
        sense = terminals[f"U1.{ball}"]
        bias = terminals[f"R_JOY_{side}_CLICK.pin2"]
        reaches_switch = sense == terminals[f"J_JOY_{side}.pin3"] == terminals[f"R_JOY_{side}_CLICK.pin1"]
        sequenced = bias == terminals["U_PMIC.DCDC4"]
        isolated = len({sense, bias, terminals["TP_UART_GND.pin1"], terminals["C_3V3_OUT_A.pin1"]}) == 4
        click_ok = reaches_switch and sequenced and isolated
        print(f"Joystick {side} click input, separate switch and sequenced pull-up: {'PASS' if click_ok else 'OPEN'}")
        failed |= not click_ok
        grip_supply = {terminals[f"J_JOY_{side}.pin5"], terminals[f"C_JOY_{side}_VDD.pin1"],
                       terminals[f"C_JOY_{side}_BULK.pin1"], terminals["U_PMIC.DCDC4"], terminals["U_JOY_ADC.VDD"]}
        grip_return = {terminals[f"J_JOY_{side}.pin2"], terminals[f"C_JOY_{side}_VDD.pin2"],
                       terminals[f"C_JOY_{side}_BULK.pin2"], terminals["TP_UART_GND.pin1"]}
        bypass_ok = len(grip_supply) == len(grip_return) == 1 and grip_supply.isdisjoint(grip_return)
        bypass_ok &= terminals["C_3V3_OUT_A.pin1"] not in grip_supply
        print(f"Joystick {side} sequenced ADC supply to connector and both bypasses, and ground returns: "
              f"{'PASS' if bypass_ok else 'OPEN'}")
        failed |= not bypass_ok
    legacy_probe = terminals["TP_3V3.pin1"]
    probe_output = legacy_probe == terminals["C_3V3_OUT_A.pin1"] == terminals["C_3V3_OUT_B.pin1"]
    probe_isolated = legacy_probe not in (terminals["U_PMIC.DCDC4"], terminals["TP_UART_GND.pin1"])
    print("Legacy 3.3 V output capacitors to isolated bring-up probe:",
          "PASS" if probe_output and probe_isolated else "OPEN")
    failed |= not (probe_output and probe_isolated)
    adc_supply = terminals["U_PMIC.DCDC4"] == terminals["U_JOY_ADC.VDD"] == terminals["C_JOY_ADC.pin1"]
    adc_return = terminals["U_JOY_ADC.GND"] == terminals["C_JOY_ADC.pin2"] == terminals["TP_UART_GND.pin1"]
    print("Joystick ADC supply and bypass return:", "PASS" if adc_supply and adc_return else "OPEN")
    failed |= len(panel_taps) != 16 or not adc_supply or not adc_return
    return failed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("circuit", type=Path)
    parser.add_argument("gerbers", type=Path)
    parser.add_argument("--pmic-controls", action="store_true", help="require routed PMIC supply, wake pull-up, interrupt and cold-reset connections")
    parser.add_argument("--handheld-ground", action="store_true", help="require all mapped ground lands and barrels to share the UART ground network")
    parser.add_argument("--cpu-power", action="store_true", help="check assigned CPU supply domains and returns against their physical sources")
    parser.add_argument("--sysboot", action="store_true", help="decode physical reset straps from resistor lands and CPU balls")
    parser.add_argument("--panel-storage", action="store_true", help="verify CPU-to-FPC and CPU-to-card physical endpoints")
    parser.add_argument("--mmc0-power", action="store_true", help="require card supply, ground, pull-ups and all seven links")
    parser.add_argument("--mmc0-only", action="store_true",
                        help="return the drilled MMC0 result independently of other open nets")
    args = parser.parse_args()
    if args.mmc0_only and any((args.pmic_controls, args.handheld_ground, args.cpu_power, args.sysboot, args.panel_storage)):
        parser.error("--mmc0-only cannot be combined with whole-handheld checks")
    board = json.loads(args.circuit.read_text())
    drill = runpy.run_path(str(CHECKS / "audit-channel-drills.py"))
    expected = drill["expected_drills"](board)
    bores = defaultdict(list)
    plating = []
    with ZipFile(args.gerbers) as archive:
        if set(expected) != {name for name in archive.namelist() if name.endswith(".drl")}:
            raise ValueError("Excellon span files differ from the board")
        for name, holes in expected.items():
            drill["compare"](name, archive.read(name).decode().splitlines(), holes.copy())
            span = [int(v) for v in re.findall(r"L(\d+)", name)]
            sides = LAYERS[span[0]-1:span[1]] if span else LAYERS
            for diameter, ends in holes:
                path = Point(ends[0]) if len(ends) == 1 else LineString(ends)
                hole = path.buffer(diameter / 2, quad_segs=64)
                for layer in sides:
                    bores[layer].append(hole)
                if span:
                    plating.append((sides, hole.boundary))
    pieces = {}
    trees = {}
    parents = {}

    def root(node):
        while parents[node] != node:
            parents[node] = parents[parents[node]]
            node = parents[node]
        return node

    for layer, member in zip(LAYERS, MEMBERS):
        copper = artwork(args.gerbers, member).difference(unary_union(bores[layer]))
        pieces[layer] = list(copper.geoms) if copper.geom_type == "MultiPolygon" else [copper]
        trees[layer] = STRtree(pieces[layer])
        for i in range(len(pieces[layer])):
            parents[layer, i] = layer, i

    for sides, wall in plating:
        contacts = []
        for layer in sides:
            for i in trees[layer].query(wall, predicate="intersects"):
                if pieces[layer][i].intersection(wall).length > 0.001:
                    contacts.append((layer, i))
        if not contacts:
            raise ValueError(f"Plated drill touches no copper near {wall.centroid.wkt}")
        for node in contacts[1:]:
            parents[root(node)] = root(contacts[0])

    geometry = runpy.run_path(str(CHECKS / "audit-copper-contacts.py"))
    by_id = {e[e["type"] + "_id"]: e for e in board if e["type"] + "_id" in e}
    copper = geometry["copper"](board)
    owners = defaultdict(set)
    nodes_by_net = defaultdict(set)
    by_pad = {}
    port_labels = {}
    members = defaultdict(lambda: defaultdict(set))
    for port in board:
        if port["type"] == "pcb_port" and port.get("source_port_id"):
            source = by_id[port["source_port_id"]]
            component = by_id[source["source_component_id"]]
            port_labels[port["pcb_port_id"]] = f"{component.get('name', source['source_component_id'])}.{source['name']}"
    for layer, lands in copper.items():
        for oid, key, land in lands:
            item = by_id[oid]
            if item["type"] not in ("pcb_smtpad", "pcb_plated_hole", "pcb_via"):
                continue
            hits = {root((layer, i)) for i in trees[layer].query(land, predicate="intersects")
                    if land.intersection(pieces[layer][i]).area > 0.00001}
            if len(hits) != 1:
                raise ValueError(f"{oid} on {layer} touches {len(hits)} connected CAM networks")
            node, = hits
            owners[node].add(key)
            nodes_by_net[key].add(node)
            if item.get("pcb_port_id"):
                by_pad[item["pcb_port_id"]] = node
                if item["pcb_port_id"] in port_labels:
                    members[key][node].add(port_labels[item["pcb_port_id"]])

    for node, keys in owners.items():
        if len(keys) > 1:
            raise ValueError(f"CAM short at {node} joins {sorted(keys)}")
    terminals = {port_labels[pid]: node for pid, node in by_pad.items() if pid in port_labels}
    if args.mmc0_only:
        return mmc0_power(terminals)
    ports = {e["source_port_id"]: e["pcb_port_id"] for e in board if e["type"] == "pcb_port" and e.get("source_port_id")}
    ddr_nodes = set()
    ddr_open = []
    ddr = [t for t in board if t["type"] == "source_trace" and (t.get("name") or "").startswith("DDR_")]
    if len(ddr) != 50 or len({t["name"] for t in ddr}) != 50:
        raise ValueError("Expected 50 uniquely named DDR source links")
    for trace in ddr:
        cpu, ram = (ports[pid] for pid in trace["connected_source_port_ids"])
        a, z = by_pad[cpu], by_pad[ram]
        if a != z:
            ddr_open.append(f"{trace['name']} ({port_labels[cpu]} to {port_labels[ram]})")
            continue
        if a in ddr_nodes:
            raise ValueError(f"Exported copper aliases {trace['name']}")
        ddr_nodes.add(a)
    print(f"{len(ddr_nodes)} distinct DDR ball pairs connected. {len(plating)} plated barrels checked. No shorts between mapped land nets.")
    if ddr_open:
        print("Open DDR links: " + ", ".join(sorted(ddr_open)))
    if "TP_UART_RX.pin1" in terminals:
        probes = (("U1.E15", "TP_UART_RX.pin1"), ("U1.E16", "TP_UART_TX.pin1"), ("TP_UART_GND.pin1", "C_DDR25.pin2"))
        networks = {terminals[a] for a, _ in probes}
        if len(networks) != 3 or any(terminals[a] != terminals[b] for a, b in probes):
            raise ValueError("UART probe pads have a short or an open")
        print("UART0 RX, TX and ground reach three distinct probe networks.")
    if args.cpu_power:
        converters = {
            "U_BAT_BUCKBOOST.L1": ["L_BAT_BUCKBOOST.pin1"],
            "U_BAT_BUCKBOOST.L2": ["L_BAT_BUCKBOOST.pin2"],
            "U_3V3.VIN": ["U_3V3.EN", "C_3V3_IN.pin1"],
            "U_3V3.GND": ["TP_UART_GND.pin1"],
            "U_3V3.SW": ["L_3V3.pin1", "C_3V3_BST.pin2"],
            "U_3V3.BST": ["C_3V3_BST.pin1"],
            "U_3V3.FB": ["R_LOGIC_FB_TOP.pin2", "R_LOGIC_FB_BOTTOM.pin1"],
        }
        if len({terminals[anchor] for anchor in converters}) != len(converters):
            raise ValueError("Battery or 3.3 V converter terminals share unrelated CAM copper")
        for anchor, lands in converters.items():
            for land in lands:
                if terminals[land] != terminals[anchor]:
                    raise ValueError(f"Converter connection open between {anchor} and {land}")
        print("Battery inductor and 3.3 V regulator: all eight lands reach the intended external copper.")
    if args.pmic_controls:
        for start, end in (
            ("U_PMIC.L4A", "L_PMIC_IO.pin1"), ("U_PMIC.L4B", "L_PMIC_IO.pin2"),
            ("U_PMIC.DCDC4", "C_PMIC_IO_A.pin1"), ("U_PMIC.DCDC4", "C_PMIC_IO_B.pin1"),
            ("TP_UART_GND.pin1", "C_PMIC_IO_A.pin2"), ("TP_UART_GND.pin1", "C_PMIC_IO_B.pin2"),
            ("C_PMIC_DDR.pin1", "U_PMIC.IN_LS1"),
            ("U_PMIC.nWAKEUP", "R_PMIC_WAKE.pin1"),
            ("U_PMIC.nINT", "U1.T14"),
            ("U_PMIC.PGOOD", "U1.B15"),
        ):
            if terminals[start] != terminals[end]:
                raise ValueError(f"PMIC connection open between {start} and {end}")
            print(f"PMIC copper verified between {start} and {end}.")
        if len({terminals["U_PMIC." + name] for name in ("L4A", "L4B", "DCDC4", "IN_DCDC4", "EP")}) != 5:
            raise ValueError("Exported DCDC4 switch, output, input or ground nodes are shorted")
    ground_failed = False
    if args.handheld_ground:
        ground, = (e for e in board if e["type"] == "source_net" and e["name"] == "GND")
        ground_nodes = nodes_by_net[ground["subcircuit_connectivity_map_key"]]
        if ground_nodes != {terminals["TP_UART_GND.pin1"]}:
            ground_failed = True
            print(f"Handheld ground has {len(ground_nodes)} separate CAM networks")
        else:
            print("All mapped handheld ground lands and barrels join the UART ground probe.")
    startup_failed = args.cpu_power and rtc_startup(terminals)
    power_failed = args.cpu_power and processor_power(terminals)
    straps_failed = args.sysboot and sysboot(terminals)
    caps_failed = args.cpu_power and internal_bypass(board, terminals, port_labels)
    interfaces_failed = args.panel_storage and panel_and_storage(terminals)
    card_failed = (args.mmc0_power or args.panel_storage) and mmc0_power(terminals)
    opens = {k: len(v) for k, v in nodes_by_net.items() if len(v) > 1}
    for key, count in sorted(opens.items()):
        examples = [", ".join(sorted(members[key][node])[:3]) or "via only" for node in sorted(nodes_by_net[key])]
        print(f"OPEN {key} has {count} separate CAM networks: " + " | ".join(examples))
    print(f"{len(opens)} mapped land nets have multiple physical networks.")
    return bool(ddr_open or opens) or power_failed or startup_failed or straps_failed or interfaces_failed or caps_failed or card_failed or ground_failed


if __name__ == "__main__":
    raise SystemExit(main())
