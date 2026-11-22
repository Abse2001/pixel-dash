"""Check the TI Table 7-63 non-DDR signal setback at the routed DDR copper.

This is a necessary lower bound on the keepout. It does not certify the entire
enclosing DDR region, the space between bus traces or the reference planes.
"""
import csv
import json
import runpy
import sys
from pathlib import Path

from shapely import STRtree


def audit(board):
    copper = runpy.run_path(str(Path(__file__).with_name("audit-copper-contacts.py")))["copper"](board)
    by_id = {e[e["type"] + "_id"]: e for e in board if e["type"] + "_id" in e}
    signals = {e["subcircuit_connectivity_map_key"]: e["name"] for e in board
               if e["type"] == "source_trace" and (e.get("name") or "").startswith("DDR_")}
    if len(signals) != 50:
        raise ValueError("Expected 50 distinct DDR signal nets")
    support = {e["subcircuit_connectivity_map_key"] for e in board if e["type"] == "source_net"
               and e["name"] in {"GND", "VDDS_DDR", "DDR_VREF", "DDR_VREF_CA", "DDR_VTP", "DDR_ZQ"}}
    for layer in ("top", "bottom"):
        ddr = [(key, shape, max(p["width"] for p in by_id[oid]["route"] if p.get("layer") == layer))
               for oid, key, shape in copper[layer]
               if key in signals and by_id[oid]["type"] == "pcb_trace"]
        tree = STRtree([shape for _, shape, _ in ddr])
        search = 4 * max(width for _, _, width in ddr)
        for oid, key, shape in copper[layer]:
            if key in signals or key in support or by_id[oid]["type"] not in ("pcb_trace", "pcb_via"):
                continue
            worst = None
            for index in tree.query(shape, predicate="dwithin", distance=search):
                bus_key, neighbor, width = ddr[index]
                gap, limit = shape.distance(neighbor), 4 * width
                if gap < limit - 1e-7:
                    candidate = (gap - limit, gap, limit, signals[bus_key])
                    if worst is None or candidate < worst:
                        worst = candidate
            if worst:
                _, gap, limit, signal = worst
                yield layer, oid, signal, f"{gap:.6f}", f"{limit:.6f}"


if __name__ == "__main__":
    board = json.loads(Path(sys.argv[1]).read_text())
    findings = sorted(audit(board))
    out = csv.writer(sys.stdout)
    out.writerow(("layer", "non_ddr_copper", "adjacent_ddr_signal", "edge_gap_mm", "four_widths_mm"))
    out.writerows(findings)
    print(f"{len(findings)} unrelated signal trace/via and layer combinations inside the 4w setback.", file=sys.stderr)
    sys.exit(bool(findings))
