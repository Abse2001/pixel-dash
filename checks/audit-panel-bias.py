"""Check the bare ER-TFT070A2-6 supply and unused contacts against the schematic."""
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "production"))
from connectivity import trace_net_keys


def findings(board):
    connector, = [e for e in board if e["type"] == "source_component" and e.get("name") == "J_LCD"]
    pins = {e["name"]: e["source_port_id"] for e in board if e["type"] == "source_port"
            and e["source_component_id"] == connector["source_component_id"]}
    traces, keys = trace_net_keys(board)
    nets = defaultdict(set)
    for name, trace in traces.items():
        for port in trace["connected_source_port_ids"]:
            nets[port].add(keys[name])
    ground, = [e["subcircuit_connectivity_map_key"] for e in board
               if e["type"] == "source_net" and e.get("name") == "GND"]
    rails = {"GND": (5, 36, 38, 48), "VCOM": (6, 46), "DVDD": (7,), "VGH": (41,),
             "VGL": (42,), "AVDD": (43,), "LED_A": (1, 2), "LED_K": (3, 4)}
    used = {ground: "GND"}
    for rail, numbers in rails.items():
        assigned = [nets[pins[f"pin{n}"]] for n in numbers]
        if any(len(s) != 1 for s in assigned) or len(set.union(*assigned)) != 1:
            yield f"{rail} contacts {numbers} do not share a single assigned net"
            continue
        key = next(iter(assigned[0]))
        if rail == "GND" and key != ground:
            yield f"Ground contacts {numbers} are on another net"
        if key in used and used[key] != rail:
            yield f"{rail} contacts {numbers} share the {used[key]} net"
        used.setdefault(key, rail)
    for n in (45, 49, 50):
        if nets[pins[f"pin{n}"]]:
            yield f"Panel NC contact {n} has a schematic connection"


if __name__ == "__main__":
    failures = list(findings(json.loads(Path(sys.argv[1]).read_text())))
    for message in failures:
        print(message)
    print(f"{len(failures)} bare-panel bias topology findings")
    sys.exit(bool(failures))
