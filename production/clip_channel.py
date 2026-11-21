"""Limit the imported memory ground fill to its reviewed region on the new board."""
from shapely.geometry import Polygon, box


def restrict_ground(board, ground_net):
    pour, = (e for e in board if e["type"] == "pcb_copper_pour" and
             e["source_net_id"] == ground_net and e["layer"] == "inner1")
    shape = pour["brep_shape"]
    def vertices(ring):
        return [(p["x"],p["y"]) for p in ring["vertices"]]
    polygon = Polygon(vertices(shape["outer_ring"]), [vertices(r) for r in shape["inner_rings"]])
    edge, = (e for e in board if e["type"]=="pcb_board")
    outline = Polygon([(p["x"],p["y"]) for p in edge["outline"]])
    clipped = polygon.intersection(box(-72,4,-34,30)).intersection(outline.buffer(-0.30))
    if clipped.geom_type != "Polygon":
        raise ValueError("DDR ground area split into islands")
    def ring(boundary):
        return {"vertices":[{"x":x,"y":y} for x,y in list(boundary.coords)[:-1]]}
    pour["brep_shape"]={"outer_ring":ring(clipped.exterior),"inner_rings":[ring(r) for r in clipped.interiors]}
