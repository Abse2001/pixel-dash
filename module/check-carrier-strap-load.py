"""Enumerate real carrier RGB loads and screen reset-strapping assumptions per pin."""
import csv
import gzip
import json
import math
import sys
from pathlib import Path

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent / "production"))
from connectivity import trace_net_keys

with gzip.open(here.parent / "studies/four-layer-through/board.circuit.json.gz") as stream:
    source = json.load(stream)
traces, keys = trace_net_keys(source)
port_net = {port: keys[key] for key, trace in traces.items() for port in trace["connected_source_port_ids"]}
components = {e["source_component_id"]: e["name"] for e in source if e["type"] == "source_component" and "name" in e}
terminal = {e["source_port_id"]: components[e["source_component_id"]] + "." + e["name"]
            for e in source if e["type"] == "source_port" and e.get("source_component_id") in components}
net = {terminal[port]: value for port, value in port_net.items() if port in terminal}
islands = json.loads(Path(sys.argv[1]).read_text())
connector = {row["signal"]: row for row in csv.DictReader((here / "carrier-pinout.csv").open())}
bom = {row["reference"]: row["MPN"] for row in csv.DictReader((here / "module-bom.csv").open())}
writer = csv.writer(sys.stdout, lineterminator="\n")
writer.writerow(("bit","pull","cpu","contact","panel","source_to_cpu_pull_contact","carrier_case",
                 "dc_V","margin_V","settle_us_at_100pF","assessment"))
for bit in range(16):
    row = connector[f"LCD_D{bit}"]
    cpu, contact, resistor = row["module_terminal"], "J_CARRIER." + row["contact"], f"R_SYSBOOT{bit}"
    endpoints = {pin for pin, key in net.items() if key == net[cpu]}
    panel, = [pin for pin in endpoints if pin.startswith("J_LCD.")]
    assert endpoints == {cpu, panel, resistor + ".pin2"} and bom[resistor] == "0402WGF1002TCE"
    high = bool(0x4017 & (1 << bit))
    bias_net, source_pin = ("VDD_IO_3V3_SEQ", "U_PMIC.DCDC4") if high else ("GND_INTERNAL", "U_PMIC.EP")
    bias = any({source_pin, resistor + ".pin1"} <= set(group) for group in islands[bias_net])
    tap = any({cpu,contact,resistor+".pin2"} <= set(group) for group in islands[row["module_net"]])
    prefix = [bit, int(high), cpu, contact, panel, bool(bias and tap)]
    for case in ("direct_powered","direct_unpowered","direct_panel_reset_low","direct_ramping"):
        writer.writerow(prefix+[case,"","","","OPEN: panel input load at this state unbounded"])
    for case, load_uA in (("panel_disconnected",0),("buffer_powered",20),
                           ("buffer_at_0V",20),("buffer_powered_panel_reset_low",20)):
        # 5 uA is a design allowance for board/connector leakage. 100 pF is a trial load.
        volts = (18 + 5 + load_uA)*1e-6 * 10100
        final = 3.135-volts if high else volts
        threshold, initial = (2.,0.) if high else (.8,3.465)
        margin = (final-threshold) if high else (threshold-final)
        assert margin > 0
        settle_us = -10100 * 100e-12 * math.log((threshold-final)/(initial-final)) * 1e6
        writer.writerow(prefix+[case,f"{final:.4f}",f"{margin:.4f}",f"{settle_us:.3f}","CONDITIONAL"])
