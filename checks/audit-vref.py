"""Check physical DDR reference and bypass connectivity in native circuit JSON (Shapely 2)."""
import json
from collections import defaultdict
from pathlib import Path

from shapely import STRtree, affinity, unary_union
from shapely.geometry import LineString, Point, Polygon, box


def verify(elements, check_ddr_power=False, check_ddr_signals=False, check_system_io=False, check_pmic_hold=False, check_pmic_backup=False):
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
    if check_pmic_hold or check_pmic_backup:
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
        ground = ["plane.inner1.GND"]
        for ref, filename in (("U1", "processor-balls.json"), ("U_DDR", "memory-balls.json")):
            balls = json.loads((base / filename).read_text())
            for ball, signal in balls.items():
                if signal in ({"VDDS_DDR"} if ref == "U1" else {"VDD", "VDDQ"}):
                    supply.append(f"{ref}.{ball}")
                if signal in {"VSS", "VSSQ"}:
                    ground.append(f"{ref}.{ball}")
        bypass = json.loads((base / "bypass-placement.json").read_text())
        supply.extend(f"C_DDR{i}.pin1" for i in range(1, len(bypass)+1))
        ground.extend(f"C_DDR{i}.pin2" for i in range(1, len(bypass)+1))
        for group in (supply, ground):
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
    args = parser.parse_args()
    verify(json.loads(args.circuit.read_text()), args.ddr_power, args.ddr_signals, args.system_io, args.pmic_hold, args.pmic_backup)
