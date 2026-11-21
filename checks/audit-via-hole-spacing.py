"""Check JLCPCB's published via drill-edge spacing for shared layer spans."""
import argparse
import csv
import json
import math
import sys
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "production"))
from connectivity import trace_net_keys


def audit(board):
    _, trace_keys = trace_net_keys(board)
    trace_nets = {e["pcb_trace_id"]: trace_keys[e["source_trace_id"]]
                  for e in board if e["type"] == "pcb_trace"}
    holes = []
    for via in board:
        if via["type"] != "pcb_via":
            continue
        net = (via.get("subcircuit_connectivity_map_key")
               or trace_keys.get(via.get("source_trace_id"))
               or trace_nets.get(via.get("pcb_trace_id")))
        if net is None:
            raise ValueError(f"Unknown net for {via['pcb_via_id']}")
        span = set(via["layers"])
        blind = len(span) == 2 and bool(span & {"top", "bottom"})
        holes.append((via, net, span, blind))

    for (a, net_a, span_a, blind_a), (b, net_b, span_b, blind_b) in combinations(holes, 2):
        common = span_a & span_b
        if not common:
            continue
        centers = math.hypot(a["x"]-b["x"], a["y"]-b["y"])
        # Coaxial same-net transitions on adjoining drill spans are stacked vias.
        if len(common) == 1 and net_a == net_b and centers < 1e-6:
            continue
        if blind_a or blind_b:
            minimum = 0.13 if net_a == net_b else 0.24
        else:
            minimum = 0.20
        gap = centers - (a["hole_diameter"] + b["hole_diameter"])/2
        if gap < minimum - 1e-6:
            yield a["pcb_via_id"], b["pcb_via_id"], gap, minimum


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("circuit", type=Path)
    failures = list(audit(json.loads(parser.parse_args().circuit.read_text())))
    out = csv.writer(sys.stdout)
    out.writerow(("via_a", "via_b", "drill_edge_gap_mm", "required_mm"))
    for a, b, gap, minimum in failures:
        out.writerow((a, b, f"{gap:.6f}", f"{minimum:.2f}"))
    print(f"{len(failures)} via drill-spacing findings", file=sys.stderr)
    sys.exit(bool(failures))
