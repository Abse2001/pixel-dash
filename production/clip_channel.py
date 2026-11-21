"""Clear the rendered L2 ground plane around retained geometry on the integrated board."""

from connectivity import trace_net_keys
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union


def restrict_ground(board, ground_net):
    def xy(p):
        return p["x"], p["y"]

    def ring_vertices(ring):
        return [xy(p) for p in ring["vertices"]]

    pour, = (e for e in board if e["type"] == "pcb_copper_pour" and
             e["source_net_id"] == ground_net and e["layer"] == "inner1")
    shape = pour["brep_shape"]
    copper = Polygon(ring_vertices(shape["outer_ring"]), [ring_vertices(r) for r in shape["inner_rings"]])
    index = {e[e["type"] + "_id"]: e for e in board if e["type"] + "_id" in e}
    ground = index[ground_net]["subcircuit_connectivity_map_key"]
    _, trace_keys = trace_net_keys(board)
    clearances = []
    for e in board:
        kind = e["type"]
        if kind == "pcb_cutout":
            clearances.append(Polygon([xy(p) for p in e["points"]]).buffer(0.30))
        elif kind == "pcb_hole":
            assert e["hole_shape"] == "circle"
            clearances.append(Point(xy(e)).buffer(e["hole_diameter"]/2 + 0.30))
        elif kind == "pcb_keepout" and "inner1" in e["layers"]:
            assert e["shape"] == "rect"
            x, y = xy(e["center"])
            w, h = e["width"]/2, e["height"]/2
            clearances.append(affinity.rotate(box(x-w, y-h, x+w, y+h), e.get("ccw_rotation", 0)))
        elif kind in ("pcb_via", "pcb_plated_hole") and "inner1" in e["layers"]:
            # The channel renderer has already poured around its own lands and traces.
            if e[kind + "_id"].startswith("channel_"):
                continue
            key = e.get("subcircuit_connectivity_map_key")
            if not key and "source_trace_id" in e:
                key = trace_keys[e["source_trace_id"]]
            if not key and e.get("pcb_port_id"):
                port = index[e["pcb_port_id"]]
                key = index.get(port.get("source_port_id"), {}).get("subcircuit_connectivity_map_key")
            if key == ground:
                continue
            x, y = xy(e)
            if "outer_diameter" in e:
                pad = Point(x, y).buffer(e["outer_diameter"]/2, quad_segs=32)
            else:
                # Enclosing the complete land also clears the semicircular ends of slots.
                w, h = e["outer_width"]/2, e["outer_height"]/2
                pad = affinity.rotate(box(x-w, y-h, x+w, y+h), e.get("rect_ccw_rotation", e.get("ccw_rotation", 0)))
            clearances.append(pad.buffer(0.16))
        elif kind == "pcb_trace" and not e["pcb_trace_id"].startswith("channel_"):
            if trace_keys[e["source_trace_id"]] == ground:
                continue
            for p, q in zip(e["route"], e["route"][1:]):
                if p.get("layer", p.get("to_layer")) != "inner1" or q.get("layer", q.get("from_layer")) != "inner1":
                    continue
                if xy(p) != xy(q):
                    clearances.append(LineString([xy(p), xy(q)]).buffer(max(t["width"] for t in (p,q) if "width" in t)/2 + 0.16))
    outline, = (e for e in board if e["type"] == "pcb_board")
    board_area = Polygon([xy(p) for p in outline["outline"]]).buffer(-0.30)
    remaining = copper.intersection(board_area).difference(unary_union(clearances))
    if remaining.geom_type == "MultiPolygon":
        # The NTC breakaway and other isolated fill cannot carry a return to main-board ground.
        remaining = max(remaining.geoms, key=lambda g: g.area)
    if remaining.geom_type != "Polygon" or not remaining.is_valid:
        raise ValueError("Invalid integrated L2 ground contour")

    def ring(boundary):
        return {"vertices": [{"x": x, "y": y} for x, y in list(boundary.coords)[:-1]]}

    pour["brep_shape"] = {"outer_ring": ring(remaining.exterior), "inner_rings": [ring(r) for r in remaining.interiors]}
