"""Check MMC card-detect and optional panel touch wiring at both IC and connector."""
import json
import sys
from pathlib import Path

elements = json.loads(Path(sys.argv[1]).read_text())
components = {p["name"]: p["source_component_id"] for p in elements if p["type"] == "source_component"}
ports = {(p["source_component_id"], p["name"]): p["source_port_id"] for p in elements if p["type"] == "source_port"}
source = [t for t in elements if t["type"] == "source_trace"]
keys = set()
for net, ball, part, pin, pull in [
    ("TOUCH_SCL", "D15", "J_LCD", "pin44", "R_TOUCH_SCL"),
    ("TOUCH_SDA", "D16", "J_LCD", "pin45", "R_TOUCH_SDA"),
    ("TOUCH_IRQ", "V14", "J_LCD", "pin46", "R_TOUCH_IRQ"),
    ("SD_DETECT", "C15", "J_SD", "CD", None),
]:
    cpu = ports[components["U1"], ball]
    endpoint = ports[components[part], pin]
    system, = [t for t in source if t["source_trace_id"] == "system_" + net]
    assert {cpu, endpoint} == set(system["connected_source_port_ids"]), net
    key = system["subcircuit_connectivity_map_key"]
    assert key not in keys
    keys.add(key)
    if pull:
        pull_pin = ports[components[pull], "pin1"]
        assert any({pull_pin,endpoint}.issubset(t["connected_source_port_ids"]) and
                   t["subcircuit_connectivity_map_key"] == key for t in source), net
sd_data3, = [t for t in source if t["source_trace_id"] == "system_SD_DAT3"]
assert sd_data3["subcircuit_connectivity_map_key"] not in keys
print("Panel I2C1, touch interrupt and separate MMC0 card-detect endpoints verified in source.")
