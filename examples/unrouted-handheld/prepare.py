"""Extract the populated handheld before routing from a native assembled board."""
import json
import sys
from pathlib import Path

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parents[1] / "production"))
from connectivity import trace_net_keys


def unrouted(board):
    sources, keys = trace_net_keys(board)
    via_sources = {e["source_manually_placed_via_id"] for e in board
                   if e["type"] == "source_manually_placed_via"}
    via_bodies = {e["pcb_component_id"] for e in board if e["type"] == "pcb_component"
                  and e["source_component_id"] in via_sources}
    via_ports = {e["source_port_id"] for e in board if e["type"] == "source_port"
                 and e["source_component_id"] in via_sources}
    removed = {"pcb_trace", "pcb_via", "pcb_trace_hint", "source_manually_placed_via",
               "pcb_copper_pour"}
    empty = set()
    for trace_id, trace in sources.items():
        pins = trace["connected_source_port_ids"]
        if via_ports.intersection(pins):
            trace["connected_source_port_ids"] = [p for p in pins if p not in via_ports]
            if not trace["connected_source_port_ids"]:
                assert len(trace["connected_source_net_ids"]) == 1
                empty.add(trace_id)
        trace["subcircuit_connectivity_map_key"] = keys[trace_id]

    for e in board:
        kind = e["type"]
        if kind in removed or kind.endswith(("_error", "_warning")):
            continue
        if e.get("source_component_id") in via_sources or e.get("pcb_component_id") in via_bodies:
            continue
        if e.get("source_port_id") in via_ports or e.get("source_trace_id") in empty:
            continue
        if "pcb_component_ids" in e:
            e["pcb_component_ids"] = [i for i in e["pcb_component_ids"] if i not in via_bodies]
        if kind == "source_bus":
            assert empty.isdisjoint(e["source_trace_ids"])
        yield e


if __name__ == "__main__":
    source = Path(sys.argv[1])
    result = list(unrouted(json.loads(source.read_text())))
    (here / "board.circuit.json").write_text("[\n" + ",\n".join(
        json.dumps(e, separators=(",", ":")) for e in result) + "\n]\n")
