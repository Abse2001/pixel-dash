"""Compare plated DDR signal escapes with TI SPRS717L Table 7-62 at their saved positions."""
import argparse
import json
import runpy
from collections import Counter
from pathlib import Path

from shapely import affinity
from shapely.geometry import Point, box

CHECKS = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("circuit", type=Path)
    args = parser.parse_args()
    board = json.loads(args.circuit.read_text())
    signals = {e["source_trace_id"] for e in board if e["type"] == "source_trace" and (e.get("name") or "").startswith("DDR_")}
    if len(signals) != 50:
        raise ValueError("Expected all 50 DDR signal assignments")
    # Use the package body dimensions, so the first and last rows of balls are included.
    bodies = {"U1": (15, 15), "U_DDR": (8, 14)}
    refdes = {e["source_component_id"]: e.get("name") for e in board if e["type"] == "source_component"}
    outlines = {}
    for part in board:
        if part["type"] != "pcb_component" or refdes.get(part.get("source_component_id")) not in bodies:
            continue
        name = refdes[part["source_component_id"]]
        w, h = bodies[name]
        body = affinity.rotate(box(-w/2, -h/2, w/2, h/2), part["rotation"])
        outlines[name] = affinity.translate(body, part["center"]["x"], part["center"]["y"])
    if outlines.keys() != bodies.keys():
        raise ValueError("Missing CPU or RAM body")
    transitions = {(v["x"], v["y"]) for t in board if t["type"] == "pcb_trace" and t.get("source_trace_id") in signals
                   for v in t["route"] if v["route_type"] == "via"}
    vias = {(e["x"], e["y"]): e for e in board if e["type"] == "pcb_via" and set(e["layers"]) == {"top", "inner1", "inner2", "bottom"}}
    counts = Counter()
    candidate = []
    for pos in sorted(transitions):
        via = vias[pos]
        name = next((n for n, body in outlines.items() if body.covers(Point(pos))), "outside both bodies")
        counts[name, via["outer_diameter"], via["hole_diameter"]] += 1
        if name in bodies:
            candidate.append(via)
    for (name, pad, hole), count in sorted(counts.items()):
        print(f"{name}: {count} DDR through vias, {pad:g} mm land, {hole:g} mm drill.")
    for via in candidate:
        via["outer_diameter"], via["hole_diameter"] = 0.4572, 0.254
    edge = runpy.run_path(str(CHECKS / "audit-via-clearance.py"))["audit"]
    drills = runpy.run_path(str(CHECKS / "audit-via-hole-spacing.py"))["audit"]
    print(f"In-memory comparison with 18 mil lands and 10 mil holes at {len(candidate)} in-package sites:")
    print(f"  {len(edge(board))} via/layer/unrelated-net pairs below 6 mil.")
    print(f"  Drill-edge spacing findings: {sum(1 for _ in drills(board))}.")


if __name__ == "__main__":
    main()
