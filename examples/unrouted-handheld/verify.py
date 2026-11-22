"""Check the solver's pin partitions against the complete assembled electrical design."""
import json
import sys
from collections import defaultdict
from pathlib import Path

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parents[1] / "production"))
from connectivity import trace_net_keys

original = json.loads(Path(sys.argv[1]).read_text())
fixture = json.loads((here / "board.circuit.json").read_text())
srj = json.loads((here / "simple-route.json").read_text())
via_ids = {e["source_manually_placed_via_id"] for e in original if e["type"] == "source_manually_placed_via"}
via_pins = {e["source_port_id"] for e in original if e["type"] == "source_port" and e["source_component_id"] in via_ids}
for kind in ("source_component", "pcb_component", "pcb_port", "source_net", "pcb_smtpad",
             "pcb_plated_hole", "pcb_hole", "pcb_cutout", "pcb_keepout", "pcb_board", "source_bus"):
    expected = [e for e in original if e["type"] == kind and e.get("source_component_id") not in via_ids
                and e.get("source_port_id") not in via_pins]
    assert expected == [e for e in fixture if e["type"] == kind], kind

def nets(board):
    traces, keys = trace_net_keys(board)
    pins = {e["source_port_id"]: e["pcb_port_id"] for e in board if e["type"] == "pcb_port"}
    groups = defaultdict(set)
    for tid, t in traces.items():
        groups[keys[tid]].update(pins[p] for p in t["connected_source_port_ids"] if p not in via_pins)
    return {k: v for k, v in groups.items() if v}

groups = nets(original)
assert groups == nets(fixture)
assert not srj.get("traces") and srj["layerCount"] == 4
assert not any(e["type"] in {"pcb_trace", "pcb_trace_hint", "pcb_via", "source_manually_placed_via", "pcb_copper_pour"} for e in fixture)
parent = {}
def root(p):
    while p != parent.setdefault(p, p):
        p = parent[p]
    return p

ports = {e["pcb_port_id"]: e for e in fixture if e["type"] == "pcb_port"}
for c in srj["connections"]:
    terminals = c["pointsToConnect"]
    for point in terminals:
        pid = point["pcb_port_id"]
        p = ports[pid]
        assert (point["x"], point["y"]) == (p["x"], p["y"])
        layers = point.get("layers") or [point["layer"]]
        assert set(layers) <= set(p["layers"])
        parent[root(pid)] = root(terminals[0]["pcb_port_id"])
expected = {frozenset(p) for p in groups.values() if len(p) >= 2}
actual = defaultdict(set)
for p in parent:
    actual[root(p)].add(p)
assert expected == {frozenset(p) for p in actual.values() if len(p) >= 2}
traces = {t["source_trace_id"]: t for t in fixture if t["type"] == "source_trace"}
requests = {c.get("source_trace_id"): c for c in srj["connections"]}
components = {e["source_component_id"]: e.get("name") for e in fixture if e["type"] == "source_component"}
pin_owner = {e["source_port_id"]: components[e["source_component_id"]] for e in fixture if e["type"] == "source_port"}
physical_pin = {p["source_port_id"]: pid for pid, p in ports.items()}
ddr_count = 0
for tid, t in traces.items():
    pins = t["connected_source_port_ids"]
    if {pin_owner[p] for p in pins} == {"U1", "U_DDR"} and (t.get("name") or "").startswith("DDR_"):
        assert {p["pcb_port_id"] for p in requests[tid]["pointsToConnect"]} == {physical_pin[p] for p in pins}
        ddr_count += 1
assert ddr_count == 50
for e in (e for e in fixture if e["type"] == "source_bus"):
    members = [requests[i]["name"] for i in e["source_trace_ids"]]
    if "differential_pair" in e:
        assert any(p["connectionNames"] == members and p["lengthTolerance"] == e["max_length_skew"]
                   and p["traceGap"] == e["differential_pair"]["trace_gap"] for p in srj["differentialPairs"])
    else:
        assert any(b["busId"] == e["name"] and b["connectionNames"] == members for b in srj["buses"])
print(f"{len(expected)} multi-pin nets, {sum(map(len, expected))} physical terminals, 50 DDR links verified.")
