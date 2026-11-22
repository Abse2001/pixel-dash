"""Compare board flight time to the associated DDR3L strobe or clock on the 1.491 mm reference build."""
import argparse
import csv
import json
import math
import runpy
import sys
from pathlib import Path

from shapely.ops import unary_union

from hdi_build import WURTH

SINGLE, ODD, BARREL = 5.769, 5.617, 6.600  # ps/mm, reference-build sensitivity
DEPTH = {"top": 0., "inner1": WURTH.outer_to_inner,
         "inner2": WURTH.outer_to_outer-WURTH.outer_to_inner, "bottom": WURTH.outer_to_outer}


def routed_flights(board, proximity):
    pair_audit = runpy.run_path(str(Path(__file__).with_name("measure-ddr-pair-spacing.py")))
    pairs = pair_audit["PAIRS"]
    segments = pair_audit["pair_segments"](board)
    coupled = {}
    for positive, negative in pairs:
        for name, mate in ((positive, negative), (negative, positive)):
            length = 0.
            for layer, edges in segments[name].items():
                envelope = unary_union(segments[mate].get(layer, [])).buffer(proximity, quad_segs=48)
                length += sum(line.intersection(envelope).length for line in edges)
            coupled[name] = length

    names = {e["source_trace_id"]: e.get("name", "") for e in board if e["type"] == "source_trace"}
    rows = {}
    for trace in board:
        if trace["type"] != "pcb_trace":
            continue
        name = names[trace["source_trace_id"]]
        if not name.startswith("DDR_"):
            continue
        route = trace["route"]
        xy = [(p["x"],p["y"]) for p in route]
        planar = sum(math.dist(a, b) for a,b in zip(xy,xy[1:]))
        barrels = [abs(DEPTH[p["from_layer"]]-DEPTH[p["to_layer"]]) for p in route if p["route_type"]=="via"]
        if name in rows:
            raise ValueError(f"Multiple paths on {name}")
        isolated = planar*SINGLE + sum(barrels)*BARREL
        near = coupled.get(name, 0.)
        rows[name] = (planar, len(barrels), sum(barrels), near, isolated, isolated-near*(SINGLE-ODD))
    return rows


def flights(board, proximity):
    rows = routed_flights(board, proximity)
    if len(rows) != 50:
        raise ValueError("The full-bus comparison requires 50 physically routed nets")
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("board", type=Path)
    parser.add_argument("--pair-center-mm", type=float, default=.42, help="threshold for the mixed coupled/isolated sensitivity")
    args = parser.parse_args()
    rows = flights(json.loads(args.board.read_text()), args.pair_center_mm)
    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow(("signal","planar_mm","transitions","traversed_mm","near_mate_mm",
                     "isolated_ps","mixed_ps","reference","mixed_max_abs_delta_ps","all_odd_max_abs_delta_ps"))
    failed = False
    pairs = [("DDR_DQS0","DDR_DQSn0"),("DDR_DQS1","DDR_DQSn1")]
    for name,(planar,count,depth,near,single,mixed) in sorted(rows.items()):
        ref = ()
        for i,pair in enumerate(pairs):
            if name in {f"DDR_D{j}" for j in range(8*i,8*i+8)} | {f"DDR_DQM{i}"}:
                ref = pair
        if not ref and name not in {s for pair in pairs for s in pair} | {"DDR_CK","DDR_CKn","DDR_RESETn"}:
            ref = ("DDR_CK", "DDR_CKn")
        deltas = []
        if ref:
            dm = max(abs(mixed-rows[n][5]) for n in ref)
            do = max(abs(single-(rows[n][4]-rows[n][0]*(SINGLE-ODD))) for n in ref)
            deltas = [f"{dm:.3f}", f"{do:.3f}"]
            if ref in pairs:
                failed |= max(dm,do,*(abs(single-rows[n][4]) for n in ref)) > SINGLE*.635
        writer.writerow([name,f"{planar:.4f}",count,f"{depth:.4f}",f"{near:.4f}",f"{single:.3f}",f"{mixed:.3f}",
                         "/".join(ref),*(deltas or ["",""])])
    print("Board delay sensitivity. Each via uses its contacted layer span. The mixed case uses the odd-mode rate "
          "within the specified center distance and the isolated rate elsewhere. Package delay, dielectric tolerance "
          "and launch discontinuities require separate evaluation.",file=sys.stderr)
    return failed


if __name__ == "__main__":
    sys.exit(main())
