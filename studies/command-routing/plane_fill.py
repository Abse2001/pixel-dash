"""Keep the connected fill after subtracting route antipads and isolation gaps."""
from shapely.geometry import Point
from shapely.ops import unary_union

def connected_fill(filled, pour, board):
    if filled.geom_type == "Polygon":
        return filled
    if filled.geom_type != "MultiPolygon":
        raise ValueError(f"Unexpected pour geometry on {pour['pcb_copper_pour_id']}")
    main, *islands = sorted(filled.geoms, key=lambda region: region.area, reverse=True)
    detached = unary_union(islands)
    lands = (Point(v["x"], v["y"]).buffer(v["outer_diameter"]/2) for v in board
             if v["type"] == "pcb_via" and pour["layer"] in v["layers"])
    if detached.area > .01 or any(detached.intersects(land) for land in lands):
        raise ValueError(f"Plane split on {pour['pcb_copper_pour_id']}, detached {detached.area:.6f} mm2")
    return main
