"""Resolve source trace connectivity across the two integrated designs."""
from collections import defaultdict


def trace_net_keys(elements):
    sources = {e["source_trace_id"]: e for e in elements if e["type"] == "source_trace"}
    keys = {i: s["subcircuit_connectivity_map_key"] for i, s in sources.items()
            if s.get("subcircuit_connectivity_map_key")}
    net_keys = {e["source_net_id"]: e["subcircuit_connectivity_map_key"] for e in elements
                if e["type"] == "source_net" and e.get("subcircuit_connectivity_map_key")}
    port_keys = defaultdict(set)
    for i, key in keys.items():
        for port in sources[i]["connected_source_port_ids"]:
            port_keys[port].add(key)
    for i in sources.keys() - keys.keys():
        candidates = set().union(*(port_keys[p] for p in sources[i]["connected_source_port_ids"]))
        candidates.update(net_keys[n] for n in sources[i]["connected_source_net_ids"] if n in net_keys)
        if len(candidates) != 1:
            raise ValueError(f"Ambiguous connectivity for {i}")
        keys[i] = candidates.pop()
    return sources, keys
