"""Install saved regulator output routes between L1, L3 and the processor lands."""
from math import dist

LAYERS = ["top", "inner1", "inner2", "bottom"]


def add_processor_feeds(board, feeds, port):
    nets = {e["name"]: e for e in board if e["type"] == "source_net"}
    lands = {e["source_port_id"]: e for e in board if e["type"] == "pcb_port" and e.get("source_port_id")}
    traces = [e for e in board if e["type"] == "source_trace"]

    for feed in feeds:
        rail = nets[feed["rail"]]
        key = rail["subcircuit_connectivity_map_key"]
        prefix = "pcb_feed_" + feed["rail"]

        def terminal(label):
            pin = port(*label.split("."))
            if pin.get("subcircuit_connectivity_map_key") != key:
                raise ValueError(f"{label} does not belong to {feed['rail']}")
            return lands[pin["source_port_id"]]

        def source_for(land):
            source, = (s for s in traces if land["source_port_id"] in s["connected_source_port_ids"]
                       and rail["source_net_id"] in s["connected_source_net_ids"])
            return source["source_trace_id"]

        def via(label, point, drill, diameter):
            board.append(dict(type="pcb_via", pcb_via_id=prefix + "_" + label, x=point[0], y=point[1],
                              from_layer="top", to_layer="bottom", layers=LAYERS.copy(),
                              source_net_id=rail["source_net_id"], subcircuit_connectivity_map_key=key,
                              hole_diameter=drill, outer_diameter=diameter))

        cap, cpu = terminal(feed["cap"]), terminal(feed["cpu"])
        stages = feed["sections"]
        if len(stages) % 2 != 1 or len(stages) != len(feed["widths"]) or len(stages)-1 != len(feed["vias"]):
            raise ValueError(f"Invalid layer and drill sequence for {feed['rail']}")
        for point, land in ((stages[0][0], cap), (stages[-1][-1], cpu)):
            if dist(point, (land["x"], land["y"])) > 1e-5:
                raise ValueError(f"{feed['rail']} feed no longer lands at its terminal")
        route = []
        for i, (points, width) in enumerate(zip(stages, feed["widths"])):
            layer = "inner2" if i % 2 else "top"
            if i:
                start = points[0]
                if start != stages[i-1][-1]:
                    raise ValueError(f"{feed['rail']} layer change lacks a common via site")
                via(str(i), start, *feed["vias"][i-1])
                route.append(dict(route_type="via", x=start[0], y=start[1], from_layer=route[-1]["layer"], to_layer=layer))
            route.extend(dict(route_type="wire", x=x, y=y, width=width, layer=layer) for x, y in points)
        route[0]["start_pcb_port_id"] = cap["pcb_port_id"]
        route[-1]["end_pcb_port_id"] = cpu["pcb_port_id"]
        board.append(dict(type="pcb_trace", pcb_trace_id=prefix, source_trace_id=source_for(cap),
                          subcircuit_connectivity_map_key=key, route=route))

        for label, branch in feed["branches"].items():
            land = terminal(label)
            start, end = branch["points"]
            # The BGA land radius is 0.18 mm and the finished via land radius is 0.15 mm.
            if dist((land["x"], land["y"]), start) > 0.030001:
                raise ValueError(f"Power via no longer fits inside {label}")
            via(label, start, 0.15, 0.30)
            board.append(dict(type="pcb_trace", pcb_trace_id=prefix+"_branch_"+label,
                              source_trace_id=source_for(land), subcircuit_connectivity_map_key=key,
                              route=[dict(route_type="wire", x=x, y=y, width=branch["width"], layer="inner2")
                                     for x, y in (start, end)]))
