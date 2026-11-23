"""Fill the handheld reference planes and clear board geometry on their own layers."""

from connectivity import trace_net_keys
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union


def restrict_ground(board, ground_net, layer="inner1"):
    def xy(p):
        return p["x"], p["y"]

    def ring_vertices(ring):
        return [xy(p) for p in ring["vertices"]]

    pour, = (e for e in board if e["type"] == "pcb_copper_pour" and
             e["source_net_id"] == ground_net and e["layer"] == layer)
    shape = pour["brep_shape"]
    copper = Polygon(ring_vertices(shape["outer_ring"]), [ring_vertices(r) for r in shape["inner_rings"]])
    index = {e[e["type"] + "_id"]: e for e in board if e["type"] + "_id" in e}
    ground = index[ground_net]["subcircuit_connectivity_map_key"]
    _, trace_keys = trace_net_keys(board)
    clearances = []
    if layer == "inner2":
        # Reserve the entire DDR supply island, including its internal antipads.
        supply, = (p for p in board if p["type"] == "pcb_copper_pour" and
                   p["layer"] == layer and p["source_net_id"] != ground_net)
        island = Polygon(ring_vertices(supply["brep_shape"]["outer_ring"]))
        clearances.append(island.buffer(0.16, join_style="mitre"))
    for e in board:
        kind = e["type"]
        if kind == "pcb_cutout":
            clearances.append(Polygon([xy(p) for p in e["points"]]).buffer(0.30))
        elif kind == "pcb_hole":
            assert e["hole_shape"] == "circle"
            clearances.append(Point(xy(e)).buffer(e["hole_diameter"]/2 + 0.30))
        elif kind == "pcb_keepout" and layer in e["layers"]:
            assert e["shape"] == "rect"
            x, y = xy(e["center"])
            w, h = e["width"]/2, e["height"]/2
            clearances.append(affinity.rotate(box(x-w, y-h, x+w, y+h), e.get("ccw_rotation", 0)))
        elif kind in ("pcb_via", "pcb_plated_hole") and layer in e["layers"]:
            # The channel renderer has already poured around its own lands and traces.
            if layer == "inner1" and e[kind + "_id"].startswith("channel_"):
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
        elif kind == "pcb_trace" and (layer != "inner1" or not e["pcb_trace_id"].startswith("channel_")):
            if trace_keys[e["source_trace_id"]] == ground:
                continue
            for p, q in zip(e["route"], e["route"][1:]):
                if p.get("layer", p.get("to_layer")) != layer or q.get("layer", q.get("from_layer")) != layer:
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
        raise ValueError(f"Invalid integrated {layer} ground contour")

    def ring(boundary):
        return {"vertices": [{"x": x, "y": y} for x, y in list(boundary.coords)[:-1]]}

    pour["brep_shape"] = {"outer_ring": ring(remaining.exterior), "inner_rings": [ring(r) for r in remaining.interiors]}

def clear_handheld_copper_from_ddr(board):
    """Clear added routed copper and plated transitions from the already rendered DDR power island."""
    island, = (e for e in board if e["type"] == "pcb_copper_pour" and e["layer"] == "inner2")
    shape = island["brep_shape"]
    def coords(ring):
        return [(p["x"], p["y"]) for p in ring["vertices"]]
    original = Polygon(coords(shape["outer_ring"]), [coords(r) for r in shape["inner_rings"]])
    # A 1 mm L3 bridge joins the direct DCDC3 feed at the east edge to
    # the RAM reference copper. It crosses no bottom-layer track.
    bridge = LineString([(-43.5, 27.4), (-46.0, 27.4)]).buffer(.5)
    original = original.union(bridge)
    supply, = (e for e in board if e.get("source_net_id") == island["source_net_id"] and e["type"] == "source_net")
    antipads = []
    for via in board:
        if via["type"] != "pcb_via" or via["pcb_via_id"].startswith("channel_") or "inner2" not in via["layers"]:
            continue
        if via.get("subcircuit_connectivity_map_key") == supply["subcircuit_connectivity_map_key"]:
            continue
        relief = Point(via["x"], via["y"]).buffer(via["outer_diameter"] / 2 + 0.16, quad_segs=96)
        if original.intersects(relief):
            antipads.append(relief)
    for trace in board:
        if trace["type"] != "pcb_trace" or trace["pcb_trace_id"].startswith("channel_"):
            continue
        if trace.get("subcircuit_connectivity_map_key") == supply["subcircuit_connectivity_map_key"]:
            continue
        for a, b in zip(trace["route"], trace["route"][1:]):
            if a.get("layer") != "inner2" or b.get("layer") != "inner2":
                continue
            line = LineString([(a["x"], a["y"]), (b["x"], b["y"])])
            relief = line.buffer(max(a["width"], b["width"])/2 + 0.16)
            if original.intersects(relief):
                antipads.append(relief)
    if antipads:
        result = original.difference(unary_union(antipads))
        if result.geom_type == "MultiPolygon":
            # Keep the common component at the direct feed and reject loss
            # of any powered contact or of the DDR routing envelope.
            feed = Point(-39.395, 25.395)
            main, = [piece for piece in result.geoms if piece.covers(feed)]
            discarded = result.difference(main)
            signal_ids = {e["source_trace_id"] for e in board if e["type"] == "source_trace"
                          and (e.get("name") or "").startswith("DDR_")}
            routes = [LineString([(v["x"], v["y"]) for v in e["route"]]).buffer(.20)
                      for e in board if e["type"] == "pcb_trace" and e["source_trace_id"] in signal_ids]
            routed_ids = {e["source_trace_id"] for e in board if e["type"] == "pcb_trace"}
            missing = {e["name"] for e in board if e["type"] == "source_trace"
                       and e["source_trace_id"] in signal_ids - routed_ids}
            if missing != {"DDR_A10", "DDR_A14", "DDR_D1", "DDR_D11", "DDR_D12", "DDR_D14"}:
                raise ValueError(f"Unexpected open nets on the four-route breakout study: {sorted(missing)}")
            if unary_union(routes).convex_hull.intersects(discarded):
                raise ValueError("An isolated L3 fragment overlaps the routed DDR region")
            for v in board:
                if (v["type"] == "pcb_via" and "inner2" in v["layers"] and
                    (v.get("source_net_id") == supply["source_net_id"] or
                     v.get("subcircuit_connectivity_map_key") == supply["subcircuit_connectivity_map_key"])):
                    land = Point(v["x"], v["y"]).buffer(v["outer_diameter"]/2)
                    if discarded.intersects(land):
                        raise ValueError(f"Isolated DDR supply land {v['pcb_via_id']}")
            result = main
        if result.geom_type != "Polygon" or not result.is_valid:
            raise ValueError("Handheld copper divides the DDR supply island")
        def ring(boundary):
            return {"vertices": [{"x": x, "y": y} for x, y in list(boundary.coords)[:-1]]}
        island["brep_shape"] = {"outer_ring": ring(result.exterior), "inner_rings": [ring(r) for r in result.interiors]}


def add_inner2_ground(board, ground_net):
    board_outline, = (e for e in board if e["type"] == "pcb_board")
    # Gerber clear polarity affects all previously drawn copper on this layer.
    # Clear the ground keepout before drawing the nested DDR supply island.
    island_index, = (i for i, e in enumerate(board)
                     if e["type"] == "pcb_copper_pour" and e["layer"] == "inner2")
    board.insert(island_index, dict(type="pcb_copper_pour", pcb_copper_pour_id="system_inner2_ground",
                      shape="brep", layer="inner2", source_net_id=ground_net,
                      covered_with_solder_mask=True,
                      brep_shape={"outer_ring": {"vertices": board_outline["outline"]}, "inner_rings": []}))
    restrict_ground(board, ground_net, "inner2")
