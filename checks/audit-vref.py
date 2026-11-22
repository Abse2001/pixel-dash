"""Check physical DDR reference and bypass connectivity in native circuit JSON (Shapely 2)."""
import json
from collections import defaultdict
from pathlib import Path

from shapely import STRtree, affinity, unary_union
from shapely.geometry import LineString, Point, Polygon, box


def verify(elements, check_ddr_power=False, check_ddr_signals=False, check_system_io=False, check_pmic_hold=False, check_pmic_backup=False, check_rtc_filters=False, check_joysticks=False, check_control_bus=False, check_ddr_regulator=False, check_retained_returns=False, check_processor_filters=False, check_warm_reset=False):
    names = {e["source_component_id"]: e.get("name") for e in elements if e["type"] == "source_component"}
    pins = {e["source_port_id"]: f"{names.get(e['source_component_id'])}.{e['name']}"
            for e in elements if e["type"] == "source_port"}
    pads = {e["pcb_port_id"]: pins.get(e.get("source_port_id")) for e in elements if e["type"] == "pcb_port"}
    required = [
        ["U1.J4", "U_DDR.H1", "R_VREF_HIGH.pin1", "R_VREF_LOW.pin1", "R_VREF_CA.pin2",
         "C_CPU_VREF.pin1", "C_VREF_DQ.pin1"],
        ["U_DDR.M8", "R_VREF_CA.pin1", "C_VREF_CA.pin1"],
        ["plane.inner1.GND", "R_VREF_LOW.pin2", "C_CPU_VREF.pin2", "C_VREF_DQ.pin2", "C_VREF_CA.pin2"],
        ["plane.inner2.VDDS_DDR", "R_VREF_HIGH.pin2"],
    ]
    if check_pmic_hold or check_pmic_backup or check_rtc_filters or check_ddr_regulator or check_processor_filters:
        def pmic_pin(name):
            pin, = [e for e in elements if e["type"] == "source_port" and
                    names.get(e["source_component_id"]) == "U_PMIC" and
                    name in (e["name"], *e.get("port_hints", []))]
            return pin

        def bypass(name, terminal, capacitance, code):
            cap, = [e for e in elements if e["type"] == "source_component" and e.get("name") == name]
            if cap["capacitance"] != capacitance or cap["supplier_part_numbers"]["jlcpcb"] != [code]:
                raise ValueError(f"Unexpected value or assembly part for {name}")
            required.append([pins[pmic_pin(terminal)["source_port_id"]], f"{name}.pin1"])
            required[2].append(f"{name}.pin2")

        if check_pmic_hold:
            bypass("C_PMIC_INT_LDO", "INT_LDO", 1e-6, "C15849")
        if check_pmic_backup:
            bypass("C_PMIC_IN_BU", "IN_BU", 4.7e-6, "C19666")
            bypass("C_PMIC_SYS_BU", "SYS_BU", 1e-6, "C15849")
            required[2].append(pins[pmic_pin("CC")["source_port_id"]])
            vsys, = [e for e in elements if e["type"] == "source_net" and e["name"] == "VSYS"]
            if pmic_pin("IN_BU")["subcircuit_connectivity_map_key"] != vsys["subcircuit_connectivity_map_key"]:
                raise ValueError("PMIC backup input has the wrong system supply assignment")
        if check_rtc_filters:
            for rail, index in (("CORE", 5), ("IO", 6)):
                cap = f"C_PMIC_RTC_{rail}"
                coil = f"L_PMIC_RTC_{rail}"
                bypass(cap, f"FB{index}", 47e-6, "C96123")
                required[-1].append(f"{coil}.pin2")
                required.append([pins[pmic_pin(f"L{index}")["source_port_id"]], f"{coil}.pin1"])
                part, = [e for e in elements if e["type"] == "source_component" and e.get("name") == coil]
                if part.get("supplier_part_numbers", {}).get("jlcpcb") != ["C162582"]:
                    raise ValueError(f"Unexpected RTC inductor for {rail}")
        if check_processor_filters:
            balls = json.loads((Path(__file__).resolve().parents[1] / "am3354/processor-balls.json").read_text())
            for rail, index in (("CORE", 1), ("MPU", 2)):
                cap, coil = f"C_PMIC_{rail}", f"L_PMIC_{rail}"
                bypass(cap, f"FB{index}", 47e-6, "C96123")
                required[-1].append(f"{coil}.pin2")
                required.append([pins[pmic_pin(f"L{index}")["source_port_id"]], f"{coil}.pin1"])
                inductor, = [e for e in elements if e["type"] == "source_component" and e.get("name") == coil]
                if inductor.get("supplier_part_numbers", {}).get("jlcpcb") != ["C3221570"]:
                    raise ValueError(f"Incorrect DCDC{index} inductor")
                net, = [e for e in elements if e["type"] == "source_net" and e["name"] == f"VDD_{rail}"]
                key = net["subcircuit_connectivity_map_key"]
                expected = {f"U1.{ball}" for ball, supply in balls.items() if supply == net["name"]}
                assigned = {pins[e["source_port_id"]] for e in elements if e["type"] == "source_port"
                            and names.get(e["source_component_id"]) == "U1"
                            and e.get("subcircuit_connectivity_map_key") == key}
                if not expected or assigned != expected or pmic_pin(f"FB{index}").get("subcircuit_connectivity_map_key") != key:
                    raise ValueError(f"Incorrect processor or feedback assignment to {net['name']}")
        if check_ddr_regulator:
            bypass("C_PMIC_DDR", "FB3", 47e-6, "C96123")
            required[3].extend(required.pop())
            required[3].extend(["L_PMIC_DDR.pin2", "U_PMIC.IN_LS1"])
            required.append([pins[pmic_pin("L3")["source_port_id"]], "L_PMIC_DDR.pin1"])
            required.append([pins[pmic_pin("PB")["source_port_id"]], "SW_POWER.pin2", "R_POWER_PB.pin1"])
            part, = [e for e in elements if e["type"] == "source_component" and e.get("name") == "L_PMIC_DDR"]
            if part.get("supplier_part_numbers", {}).get("jlcpcb") != ["C3221570"]:
                raise ValueError("Incorrect DCDC3 inductor")
    if check_joysticks:
        adc, = [e for e in elements if e["type"] == "source_component" and e.get("name") == "U_JOY_ADC"]
        if adc["supplier_part_numbers"]["jlcpcb"] != ["C37593"]:
            raise ValueError("Incorrect joystick ADC")
        required[2].extend(["U_JOY_ADC.ADDR", "U_JOY_ADC.GND", "C_JOY_ADC.pin2"])
        required.append(["U_JOY_ADC.VDD", "C_JOY_ADC.pin1"])
        for index, axis in enumerate(("LX", "LY", "RX", "RY")):
            required[2].append(f"C_JOY_{axis}.pin2")
            required.append([f"U_JOY_ADC.AIN{index}", f"C_JOY_{axis}.pin1", f"R_JOY_{axis}.pin2"])
            connector = "J_JOY_" + axis[0]
            terminal = "pin1" if axis[1] == "X" else "pin4"
            required.append([f"{connector}.{terminal}", f"R_JOY_{axis}.pin1"])
    if check_retained_returns:
        for switch, ball in (("SW_L", "B17"), ("SW_R", "B13")):
            required[2].extend(f"{switch}.pin{pin}" for pin in (2, 3, 4))
            required.append([f"{switch}.pin1", f"U1.{ball}"])
        required[2].extend(f"R_SYSBOOT{b}.pin1" for b in (3,5,6,7,8,9,10,11,12,13,15))
        required[2].extend([*(f"J_LCD.pin{n}" for n in (5, 36, 38, 48)), "C_SD_BULK.pin2", "R_LOGIC_FB_BOTTOM.pin2", "C_AMP_VDD_BULK.pin2", "U_SPK_AMP.PGND2",
                            "J_SPK.pin3", "C_3V3_IN.pin2", "R_LCD_BL_PULLDOWN.pin2"])
    if check_control_bus:
        for signal, ball in (("SCL", "C16"), ("SDA", "C17")):
            required.append([f"U1.{ball}", "U_PMIC." + signal, "U_JOY_ADC." + signal,
                             f"R_PMIC_{signal}.pin1"])
        required.append(["R_PMIC_SCL.pin2", "R_PMIC_SDA.pin2",
                         *(f"R_SYSBOOT{bit}.pin1" for bit in (0, 1, 2, 4, 14))])
    if check_warm_reset:
        required.extend([["U1.A10", "U_PMIC.GPIO3"], ["U_PMIC.nINT", "R_PMIC_IRQ.pin1"],
                         ["R_PMIC_IRQ.pin2", "R_PMIC_POR.pin2"]])
        por, = [e for e in elements if e["type"] == "source_component" and e.get("name") == "R_PMIC_POR"]
        if por["resistance"] != 10000 or por["supplier_part_numbers"]["jlcpcb"] != ["C25744"]:
            raise ValueError("Incorrect open-drain PGOOD pull-up")
    labels = defaultdict(list)
    copper = defaultdict(list)
    parent = []

    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def metal(layers, geometry, label=None):
        i = len(parent)
        parent.append(i)
        for layer in layers:
            copper[layer].append((geometry, i))
        if label:
            labels[label].append(i)

    net_names = {e["source_net_id"]: e["name"] for e in elements if e["type"] == "source_net"}
    xy = lambda p: (p["x"], p["y"])
    def pill(w, h):
        r = min(w,h)/2
        if w == h:
            return Point(0,0).buffer(r)
        dx, dy = (w/2-r), (h/2-r)
        return LineString([(-dx,-dy),(dx,dy)]).buffer(r)

    for e in elements:
        kind = e["type"]
        if kind == "pcb_smtpad":
            if e["shape"] == "circle":
                g = Point(xy(e)).buffer(e["radius"])
            elif e["shape"] == "polygon":
                g = Polygon([xy(p) for p in e["points"]])
            elif e["shape"] in ("pill", "rotated_pill"):
                g = affinity.translate(affinity.rotate(pill(e["width"], e["height"]), e.get("ccw_rotation",0), origin=(0,0)), *xy(e))
            elif e["shape"] in ("rect", "rotated_rect"):
                w, h = e["width"]/2, e["height"]/2
                g = affinity.translate(affinity.rotate(box(-w, -h, w, h), e.get("ccw_rotation", 0)), *xy(e))
            else:
                raise ValueError(f"Unsupported channel pad shape {e['shape']}")
            metal([e["layer"]], g, pads.get(e.get("pcb_port_id")))
        elif kind == "pcb_plated_hole":
            if e["shape"] == "circle":
                g = Point(0,0).buffer(e["outer_diameter"]/2)
            elif e["shape"] == "pill":
                g = pill(e["outer_width"],e["outer_height"])
            elif e.get("pad_shape") == "rect":
                w,h = e["rect_pad_width"]/2,e["rect_pad_height"]/2
                g = box(-w,-h,w,h)
            else:
                raise ValueError(f"Unsupported plated hole {e['shape']}")
            g = affinity.translate(affinity.rotate(g,e.get("rect_ccw_rotation",e.get("ccw_rotation",0)),origin=(0,0)),*xy(e))
            # Use the full land on the surface layers. An inner-layer connection
            # needs the actual plated barrel, which is smaller than the land.
            layer_set = set(e["layers"])
            outer = layer_set & {"top","bottom"}
            metal(outer, g, pads.get(e.get("pcb_port_id")))
            if "hole_diameter" in e:
                barrel = Point(xy(e)).buffer(e["hole_diameter"]/2)
            else:
                barrel = affinity.translate(affinity.rotate(pill(e["hole_width"],e["hole_height"]),e.get("hole_ccw_rotation",e.get("ccw_rotation",0)),origin=(0,0)),*xy(e))
            metal(layer_set,barrel)
        elif kind == "pcb_trace":
            groups = defaultdict(list)
            for a, b in zip(e["route"], e["route"][1:]):
                layer = a.get("layer", a.get("to_layer"))
                if layer == b.get("layer", b.get("from_layer")) and xy(a) != xy(b):
                    groups[layer].append(LineString([xy(a), xy(b)]).buffer(a.get("width", b.get("width"))/2))
            for layer, parts in groups.items():
                shape = unary_union(parts)
                for island in getattr(shape, "geoms", [shape]):
                    metal([layer], island)
        elif kind == "pcb_via":
            metal(e["layers"], Point(xy(e)).buffer(e["outer_diameter"]/2))
        elif kind == "pcb_copper_pour":
            brep = e["brep_shape"]
            ring = lambda r: [xy(p) for p in r["vertices"]]
            g = Polygon(ring(brep["outer_ring"]), [ring(r) for r in brep["inner_rings"]])
            metal([e["layer"]], g, f"plane.{e['layer']}.{net_names.get(e.get('source_net_id'))}")

    for members in copper.values():
        shapes = [g for g, _ in members]
        tree = STRtree(shapes)
        for (g, i) in members:
            for k in tree.query(g, predicate="intersects"):
                parent[root(members[k][1])] = root(i)

    if check_ddr_power:
        base = Path(__file__).resolve().parents[1] / "am3354"
        supply = ["plane.inner2.VDDS_DDR"]
        switched = ["U_PMIC.LS1"]
        ground = ["plane.inner1.GND"]
        for ref, filename in (("U1", "processor-balls.json"), ("U_DDR", "memory-balls.json")):
            balls = json.loads((base / filename).read_text())
            for ball, signal in balls.items():
                if signal in ({"VDDS_DDR"} if ref == "U1" else {"VDD", "VDDQ"}):
                    (switched if ref == "U1" else supply).append(f"{ref}.{ball}")
                if signal in {"VSS", "VSSQ"}:
                    ground.append(f"{ref}.{ball}")
        bypass = json.loads((base / "bypass-placement.json").read_text())
        supply.append("C_PMIC_DDR.pin1")
        for i, capacitor in enumerate(bypass, 1):
            (switched if capacitor["chip"] == "U1" else supply).append(f"C_DDR{i}.pin1")
        ground.extend(f"C_DDR{i}.pin2" for i in range(1, len(bypass)+1))
        if {root(i) for i in labels[supply[0]]} & {root(i) for i in labels[switched[0]]}:
            raise ValueError("DDR regulator input and switched output domains share copper")
        for group in (supply, switched, ground):
            plane, *terminals = group
            plane_id, = labels[plane]
            disconnected = [label for label in terminals
                            if not labels[label] or any(root(i) != root(plane_id) for i in labels[label])]
            if disconnected:
                raise ValueError(f"{len(disconnected)} terminals disconnected from {plane}: {', '.join(disconnected)}")
            print(f"{len(terminals)} BGA and bypass terminals physically reach {plane}.")

    components = []
    for group in required:
        for label in group:
            if not labels[label]:
                raise ValueError(f"Missing copper for {label}")
        roots = {root(i) for label in group for i in labels[label]}
        if len(roots) != 1:
            raise ValueError(f"Open connection in {group}")
        components.extend(roots)
    if len(set(components)) != len(required):
        raise ValueError("Short between reference, supply, ground or opposite sides of R_VREF_CA")
    if check_pmic_hold:
        print("PMIC INT_LDO reaches its 1 µF hold-up capacitor and the opposite land reaches L2 ground.")
    if check_pmic_backup:
        print("IN_BU and SYS_BU reach distinct local capacitors. Both returns and CC reach L2 ground.")
    if check_rtc_filters:
        print("Both RTC switch nodes reach their inductors. Each output reaches its own capacitor and feedback pin, with its return on L2.")
    if check_joysticks:
        print("All four stick axes reach their filter inputs, and the four filter outputs reach their assigned ADC lands. The bypass and address strap reach their local nodes.")
    if check_control_bus:
        print("Both I2C lines reach the CPU, PMIC, joystick ADC and their pull-up lands. The five high SYSBOOT bias pads reach the shared I/O rail copper.")
    if check_ddr_regulator:
        print("DCDC3 switch and output nodes reach separate inductor terminals. FB3 reaches the output capacitor and its return reaches L2. The power key and bias resistor reach PB.")
    if check_processor_filters:
        print("DCDC1 and DCDC2 each reach their inductor, capacitor, feedback and L2 return. CPU supply assignments match the ball map.")
    if check_warm_reset:
        print("AM3354 A10 reaches PMIC GPIO3. The IRQ pull-up reaches nINT, and the two bias pads share copper.")
    if check_ddr_signals:
        signal_roots = {}
        opens = []
        signals = [e for e in elements if e["type"] == "source_trace" and (e.get("name") or "").startswith("DDR_")]
        if len({e["name"] for e in signals}) != 50 or len(signals) != 50:
            raise ValueError("Expected 50 individually named DDR signal connections")
        for trace in signals:
            ends = [pins[port_id] for port_id in trace["connected_source_port_ids"]]
            if len(ends) != 2 or {label.split(".")[0] for label in ends} != {"U1", "U_DDR"}:
                raise ValueError(f"Unexpected terminals for {trace['name']}: {ends}")
            connected = {root(i) for label in ends for i in labels[label]}
            if not all(labels[label] for label in ends) or len(connected) != 1:
                opens.append(trace["name"])
                continue
            node, = connected
            if node in components or node in signal_roots:
                raise ValueError(f"{trace['name']} shares copper with {signal_roots.get(node, 'a DDR rail or reference')}")
            signal_roots[node] = trace["name"]
        if opens:
            raise ValueError("No continuous pad-to-pad copper on " + ", ".join(sorted(opens)))
        print("All 50 DDR signal ball pairs have continuous copper and occupy distinct electrical nodes.")

    if check_system_io:
        system = [e for e in elements if e["type"] == "source_trace" and e["source_trace_id"].startswith("system_")]
        if not system:
            raise ValueError("No handheld system connections in this build")
        opens = []
        for trace in sorted(system, key=lambda e: e["source_trace_id"]):
            ends = [pins[port_id] for port_id in trace["connected_source_port_ids"]]
            if len(ends) < 2:
                raise ValueError(f"Expected at least two system terminals on {trace['source_trace_id']}")
            nodes = {root(i) for end in ends for i in labels[end]}
            if any(not labels[end] for end in ends) or len(nodes) != 1:
                opens.append((trace["source_trace_id"], ends))
        for signal, ends in opens:
            print(f"{signal}: open between {', '.join(ends)}")
        print(f"{len(system)-len(opens)} of {len(system)} handheld system connections have physical continuity.")
        if opens:
            raise SystemExit(1)

    print("CPU J4, RAM H1 and RAM M8 each reach their local bypass. All three bypass grounds reach L2.")
    print("Divider ends reach L3 VDDS_DDR and L2 GND. R_VREF_CA separates the two reference copper nets.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("circuit", type=Path)
    parser.add_argument("--ddr-power", action="store_true")
    parser.add_argument("--ddr-signals", action="store_true")
    parser.add_argument("--system-io", action="store_true")
    parser.add_argument("--pmic-hold", action="store_true")
    parser.add_argument("--pmic-backup", action="store_true")
    parser.add_argument("--rtc-filters", action="store_true")
    parser.add_argument("--retained-returns", action="store_true")
    parser.add_argument("--joysticks", action="store_true")
    parser.add_argument("--control-bus", action="store_true")
    parser.add_argument("--ddr-regulator", action="store_true")
    parser.add_argument("--processor-filters", action="store_true")
    parser.add_argument("--warm-reset", action="store_true")
    args = parser.parse_args()
    verify(json.loads(args.circuit.read_text()), args.ddr_power, args.ddr_signals, args.system_io, args.pmic_hold, args.pmic_backup, args.rtc_filters, args.joysticks, args.control_bus, args.ddr_regulator, args.retained_returns, args.processor_filters, args.warm_reset)
