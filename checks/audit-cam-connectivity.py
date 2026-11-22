"""Walk connected copper and plated barrels in the exported four-layer board."""
import argparse
import json
import re
import runpy
from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile

from shapely import STRtree
from shapely.geometry import Point, LineString
from shapely.ops import unary_union

from ddr_cam import artwork


LAYERS = ("top", "inner1", "inner2", "bottom")
MEMBERS = ("F_Cu.gbr", "In1_Cu.gbr", "In2_Cu.gbr", "B_Cu.gbr")
CHECKS = Path(__file__).parent


def processor_power(terminals):
    """Compare package balls with the intended power sources in TI SLVUAA9B Table 1."""
    balls = json.loads((CHECKS.parent / "am3354/processor-balls.json").read_text())
    groups = {
        "TP_UART_GND.pin1": {"VSS", "VSS_OSC", "VSS_RTC", "VSSA_USB", "VSSA_ADC"},
        "C_PMIC_CORE.pin1": {"VDD_CORE"},
        "C_PMIC_MPU.pin1": {"VDD_MPU"},
        "C_PMIC_RTC_CORE.pin1": {"CAP_VDD_RTC"},
        "C_PMIC_RTC_IO.pin1": {"VDDS_RTC"},
        "U_PMIC.LS1": {"VDDS_DDR"},
        "U_PMIC.DCDC4": {"VDDSHV3", "VDDSHV5", "VDDSHV6", "VDDA3P3V_USB0", "VDDA3P3V_USB1"},
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
    return failed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("circuit", type=Path)
    parser.add_argument("gerbers", type=Path)
    parser.add_argument("--pmic-controls", action="store_true", help="require routed PMIC supply, wake pull-up, interrupt and cold-reset connections")
    parser.add_argument("--handheld-ground", action="store_true", help="require all mapped ground lands and barrels to share the UART ground network")
    parser.add_argument("--cpu-power", action="store_true", help="check assigned CPU supply domains and returns against their physical sources")
    args = parser.parse_args()
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
    ports = {e["source_port_id"]: e["pcb_port_id"] for e in board if e["type"] == "pcb_port" and e.get("source_port_id")}
    ddr_nodes = set()
    for trace in board:
        if trace["type"] == "source_trace" and (trace.get("name") or "").startswith("DDR_"):
            a, z = (by_pad[ports[pid]] for pid in trace["connected_source_port_ids"])
            if a != z or a in ddr_nodes:
                raise ValueError(f"Exported copper opens or aliases {trace['name']}")
            ddr_nodes.add(a)
    if len(ddr_nodes) != 50:
        raise ValueError(f"Expected 50 physically distinct DDR links, found {len(ddr_nodes)}")
    print(f"50 distinct DDR ball pairs connected. {len(plating)} plated barrels checked. No shorts between mapped land nets.")
    terminals = {port_labels[pid]: node for pid, node in by_pad.items() if pid in port_labels}
    if "TP_UART_RX.pin1" in terminals:
        probes = (("U1.E15", "TP_UART_RX.pin1"), ("U1.E16", "TP_UART_TX.pin1"), ("TP_UART_GND.pin1", "C_DDR25.pin2"))
        networks = {terminals[a] for a, _ in probes}
        if len(networks) != 3 or any(terminals[a] != terminals[b] for a, b in probes):
            raise ValueError("UART probe pads have a short or an open")
        print("UART0 RX, TX and ground reach three distinct probe networks.")
    if args.pmic_controls:
        for start, end in (
            ("C_PMIC_DDR.pin1", "U_PMIC.IN_LS1"),
            ("U_PMIC.nWAKEUP", "R_PMIC_WAKE.pin1"),
            ("U_PMIC.nINT", "U1.T14"),
            ("U_PMIC.PGOOD", "U1.B15"),
        ):
            if terminals[start] != terminals[end]:
                raise ValueError(f"PMIC connection open between {start} and {end}")
            print(f"PMIC copper verified between {start} and {end}.")
    if args.handheld_ground:
        ground, = (e for e in board if e["type"] == "source_net" and e["name"] == "GND")
        ground_nodes = nodes_by_net[ground["subcircuit_connectivity_map_key"]]
        if ground_nodes != {terminals["TP_UART_GND.pin1"]}:
            raise ValueError(f"Handheld ground has {len(ground_nodes)} separate CAM networks")
        print("All mapped handheld ground lands and barrels join the UART ground probe.")
    power_failed = args.cpu_power and processor_power(terminals)
    opens = {k: len(v) for k, v in nodes_by_net.items() if len(v) > 1}
    for key, count in sorted(opens.items()):
        examples = [", ".join(sorted(members[key][node])[:3]) or "via only" for node in sorted(nodes_by_net[key])]
        print(f"OPEN {key} has {count} separate CAM networks: " + " | ".join(examples))
    print(f"{len(opens)} mapped land nets have multiple physical networks.")
    return bool(opens) or power_failed


if __name__ == "__main__":
    raise SystemExit(main())
