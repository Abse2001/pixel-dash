"""Reclaim interior plane voids left by lifted signal holes in this partial escape study."""
from pathlib import Path
import runpy
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

def reclaim_drills(channel, lifted, added):
    items = {e[e["type"] + "_id"]: e for e in channel if e["type"] + "_id" in e}
    copper = runpy.run_path(str(Path(__file__).resolve().parents[2] / "checks/audit-copper-contacts.py"))["copper"](channel)
    def xy(point):
        return point["x"], point["y"]
    def ring(boundary):
        return {"vertices": [dict(x=x, y=y) for x, y in list(boundary.coords)[:-1]]}
    for pour in (e for e in channel if e["type"] == "pcb_copper_pour"):
        layer = pour["layer"]
        if (layer, items[pour["source_net_id"]].get("name")) not in [("inner1","GND"),("inner2","VDDS_DDR")]:
            continue
        bores = [Point(xy(v)).buffer(v["outer_diameter"]/2 + .162, quad_segs=96)
                 for v in lifted if layer in v["layers"]]
        shape = pour["brep_shape"]
        original = Polygon([xy(p) for p in shape["outer_ring"]["vertices"]],
                           [[xy(p) for p in r["vertices"]] for r in shape["inner_rings"]])
        key = items[pour["source_net_id"]]["subcircuit_connectivity_map_key"]
        patch = unary_union(bores).intersection(Polygon(original.exterior))
        keep = [g.buffer(.16, quad_segs=96) for oid, n, g in copper[layer]
                if n != key and patch.distance(g) < .162]
        if keep:
            patch = patch.difference(unary_union(keep))
        final = original.union(patch)
        final = final.difference(unary_union([Point(xy(v)).buffer(v["outer_diameter"]/2 + .16, quad_segs=96) for v in added if layer in v["layers"]]))
        if final.geom_type != "Polygon":
            parts = [g for g in final.geoms if g.intersection(original).area > 1e-9]
            if len(parts) != 1:
                raise ValueError("Disconnected existing reference")
            final = parts[0]
        pour["brep_shape"] = dict(outer_ring=ring(final.exterior), inner_rings=[ring(r) for r in final.interiors])

def replace_paths(channel, sources, paths, originals):
    """Materialize alternate outer-layer sections against the original package lands."""
    by_port = {p["source_port_id"]: p for p in channel if p["type"] == "pcb_port" and p.get("source_port_id")}
    added = []
    for name, sections in paths.items():
        trace = dict(originals[sources[name]["source_trace_id"]])
        pads = [by_port[p] for p in sources[name]["connected_source_port_ids"]]
        route = []
        for i, section in enumerate(sections):
            layer = ("top", "bottom")[i % 2]
            if i:
                if section[0] != sections[i - 1][-1]:
                    raise ValueError("Discontinuous via on " + name)
                x, y = section[0]
                route.append(dict(route_type="via", x=x, y=y, from_layer=route[-1]["layer"], to_layer=layer))
                via = dict(type="pcb_via", pcb_via_id=f"zoned_{name}_{i}", pcb_trace_id=trace["pcb_trace_id"],
                           x=x, y=y, hole_diameter=.15, outer_diameter=.3, layers=["top", "inner1", "inner2", "bottom"],
                           from_layer="top", to_layer="bottom", subcircuit_connectivity_map_key=sources[name]["subcircuit_connectivity_map_key"])
                added.append(via)
            route.extend(dict(route_type="wire", x=x, y=y, width=.102, layer=layer) for x,y in section)
        for wire, pad, field in [(route[0], pads[0], "start_pcb_port_id"), (route[-1], pads[1], "end_pcb_port_id")]:
            if Point(wire["x"],wire["y"]).distance(Point(pad["x"],pad["y"])) > 1e-5 or wire["layer"] not in pad["layers"]:
                raise ValueError("Misplaced endpoint on " + name)
            wire[field] = pad["pcb_port_id"]
        trace["route"] = route
        channel.append(trace)
    channel.extend(added)
    return added
