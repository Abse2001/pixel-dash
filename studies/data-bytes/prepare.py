"""Postpone conflicting physical routes for a byte-first layout iteration. Keep every land and logical net."""
import argparse
import csv
import json
import runpy
from collections import defaultdict
from pathlib import Path

from shapely import STRtree, union_all
from shapely.geometry import Polygon

ROOT = Path(__file__).resolve().parents[2]
geometry = runpy.run_path(str(ROOT / "checks/audit-copper-contacts.py"))
drills = runpy.run_path(str(ROOT / "checks/audit-via-hole-spacing.py"))


def prepare_board(board, lanes):
    signals = {f"DDR_D{8*lane+bit}" for lane in lanes for bit in range(8)}
    signals |= {f"DDR_{label}{lane}" for lane in lanes for label in ("DQM", "DQS", "DQSn")}
    ids = {e[e["type"] + "_id"]: e for e in board if e["type"] + "_id" in e}
    sources = {e["subcircuit_connectivity_map_key"]: e["name"] for e in board
               if e["type"] == "source_trace" and e.get("name") in signals}
    copper = geometry["copper"](board)
    reasons = defaultdict(set)
    linked = defaultdict(set)
    for item in board:
        if item["type"] == "pcb_via" and item.get("pcb_trace_id"):
            linked[item["pcb_trace_id"]].add(item["pcb_via_id"])
            linked[item["pcb_via_id"]].add(item["pcb_trace_id"])
    # Some native channel vias identify their route only by an exact transition coordinate.
    at = {(v["x"], v["y"]): v["pcb_via_id"] for v in board if v["type"] == "pcb_via"}
    for trace in board:
        if trace["type"] == "pcb_trace":
            for p in trace["route"]:
                if p["route_type"] == "via":
                    vid = at[p["x"], p["y"]]
                    linked[trace["pcb_trace_id"]].add(vid)
                    linked[vid].add(trace["pcb_trace_id"])

    def defer(oid, key, reason):
        if key in sources or ids[oid]["type"] not in ("pcb_trace", "pcb_via"):
            raise ValueError(f"Required copper {oid} conflicts with {reason}")
        reasons[oid].add(reason)

    keys = {o: k for layer in copper.values() for o, k, _ in layer}
    for outer, inner, rail in (("top", "inner1", "GND"), ("bottom", "inner2", "VDDS_DDR")):
        reference_key, = (e["subcircuit_connectivity_map_key"] for e in board
                          if e["type"] == "source_net" and e["name"] == rail)
        for layer in (outer, inner):
            objects = [entry for entry in copper[layer] if ids[entry[0]]["type"] != "pcb_copper_pour"]
            tree = STRtree([g for _, _, g in objects])
            for oid, key, g in copper[outer]:
                typ = ids[oid]["type"]
                if key not in sources or typ not in ("pcb_trace", "pcb_via"):
                    continue
                for ix in tree.query(g, predicate="dwithin", distance=.162):
                    other, other_key, shape = objects[ix]
                    if key == other_key:
                        continue
                    if layer == inner:
                        if typ != "pcb_trace" or other_key == reference_key:
                            continue
                        limit = .16005
                    else:
                        types = {typ, ids[other]["type"]}
                        limit = .1524 if types == {"pcb_trace", "pcb_via"} else .102
                    if g.distance(shape) < limit - 1e-7:
                        defer(other, other_key, sources[key] + " " + layer)
    # A relocated land can also touch old power or peripheral copper.
    for layer in ("top", "bottom"):
        objects = [entry for entry in copper[layer] if ids[entry[0]]["type"] in ("pcb_smtpad", "pcb_plated_hole")]
        tree = STRtree([g for _, _, g in objects])
        for oid, key, shape in copper[layer]:
            if ids[oid]["type"] not in ("pcb_trace", "pcb_via"):
                continue
            for ix in tree.query(shape, predicate="dwithin", distance=.102):
                land, land_key, pad = objects[ix]
                if key != land_key and shape.distance(pad) < .102 - 1e-7:
                    defer(oid, key, "land clearance " + land)
    for a, b, _, _ in drills["audit"](board):
        for active, other in ((a,b), (b,a)):
            if keys[active] in sources:
                defer(other, keys[other], sources[keys[active]] + " drill")
    queue = list(reasons)
    while queue:
        first = queue.pop()
        for other in linked[first]:
            if other not in reasons:
                defer(other, keys[other], "connected to postponed " + first)
                queue.append(other)

    for layer, rail in (("inner1", "GND"), ("inner2", "VDDS_DDR")):
        pour, = (e for e in board if e["type"] == "pcb_copper_pour" and e["layer"] == layer
                 and ids[e["source_net_id"]]["name"] == rail)
        oid = pour["pcb_copper_pour_id"]
        ref_key = keys[oid]
        original, = (g for o, _, g in copper[layer] if o == oid)
        # Refill only former reliefs, bounded by the original plane outline and all retained copper.
        fills = union_all([g.buffer(.1601, quad_segs=96) for o, k, g in copper[layer]
                           if o in reasons and k != ref_key])
        if fills.is_empty:
            continue
        adds = fills.intersection(Polygon(original.exterior))
        obstacles = [g.buffer(.16, quad_segs=96) for o, k, g in copper[layer]
                     if k != ref_key and o not in reasons and g.distance(adds) < .161]
        shape = original.union(adds.difference(union_all(obstacles)))
        if shape.geom_type == "MultiPolygon":
            shape, = [part for part in shape.geoms if part.covers(original.representative_point())]
        def ring(line):
            return {"vertices": [{"x": x, "y": y} for x, y in line.coords]}
        pour["brep_shape"] = {"outer_ring": ring(shape.exterior), "inner_rings": [ring(r) for r in shape.interiors]}
    return [e for e in board if e.get(e["type"] + "_id") not in reasons], reasons


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("deferred", type=Path)
    p.add_argument("--byte", action="append", required=True, type=int, choices=(0, 1))
    args = p.parse_args()
    board, deferred = prepare_board(json.loads(args.input.read_bytes()), args.byte)
    args.output.write_text(json.dumps(board, separators=(",", ":")))
    with args.deferred.open("w") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["postponed_copper", "reason"])
        w.writerows((o, ", ".join(sorted(reasons))) for o, reasons in sorted(deferred.items()))
