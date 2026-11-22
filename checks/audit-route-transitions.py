"""Require a same-net plated conductor spanning each inline trace transition."""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "production"))
from connectivity import trace_net_keys


def inspect(board):
    traces, keys = trace_net_keys(board)
    port_keys = {port: keys[i] for i, trace in traces.items() for port in trace["connected_source_port_ids"]}
    elements = {e[e["type"] + "_id"]: e for e in board if e["type"] + "_id" in e}
    plated = defaultdict(list)
    def location(point):
        return round(point["x"], 6), round(point["y"], 6)

    for e in board:
        if e["type"] in ("pcb_via", "pcb_plated_hole"):
            port = elements.get(e.get("pcb_port_id"), {})
            source = elements.get(port.get("source_port_id"), {})
            parent = elements.get(e.get("pcb_trace_id"), {})
            net = elements.get(e.get("source_net_id"), {})
            assigned = {k for k in (e.get("subcircuit_connectivity_map_key"), net.get("subcircuit_connectivity_map_key"),
                        keys.get(e.get("source_trace_id")), keys.get(parent.get("source_trace_id")),
                        port_keys.get(port.get("source_port_id")), source.get("subcircuit_connectivity_map_key")) if k}
            if len(assigned) > 1:
                raise ValueError(f"Conflicting net identities for {e[e['type'] + '_id']}")
            plated[location(e)].append((assigned, set(e["layers"])))
    for trace in board:
        if trace["type"] != "pcb_trace":
            continue
        for point in trace["route"]:
            if point["route_type"] != "via":
                continue
            span = {point["from_layer"], point["to_layer"]}
            if not any(keys[trace["source_trace_id"]] in assigned and span <= layers
                       for assigned, layers in plated[location(point)]):
                yield (trace["pcb_trace_id"], *location(point), point["from_layer"], point["to_layer"])


if __name__ == "__main__":
    errors = list(inspect(json.loads(Path(sys.argv[1]).read_text())))
    writer = csv.writer(sys.stdout)
    writer.writerow(("trace", "x_mm", "y_mm", "from_layer", "to_layer"))
    writer.writerows(errors)
    print(f"{len(errors)} route transitions lack a matching plated span", file=sys.stderr)
    sys.exit(bool(errors))
