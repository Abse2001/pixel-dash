"""Check physical DDR reference and bypass connectivity in native circuit JSON (Shapely 2)."""
import json
import sys
from collections import defaultdict
from pathlib import Path

from shapely import STRtree, affinity, unary_union
from shapely.geometry import LineString, Point, Polygon, box


def verify(elements):
    names = {e["source_component_id"]: e.get("name") for e in elements if e["type"] == "source_component"}
    pins = {e["source_port_id"]: f"{names.get(e['source_component_id'])}.{e['name']}"
            for e in elements if e["type"] == "source_port"}
    pads = {e["pcb_port_id"]: pins.get(e.get("source_port_id")) for e in elements if e["type"] == "pcb_port"}
    required = [
        ["U1.J4", "U_DDR.H1", "R_VREF_HIGH.pin1", "R_VREF_LOW.pin1", "R_VREF_CA.pin2",
         "C_CPU_VREF.pin1", "C_VREF_DQ.pin1"],
        ["U_DDR.M8", "R_VREF_CA.pin1", "C_VREF_CA.pin1"],
        ["plane.inner1.GND", "R_VREF_LOW.pin2", "C_CPU_VREF.pin2", "C_VREF_DQ.pin2", "C_VREF_CA.pin2"],
        ["plane.inner2.VDDS_DDR", "R_VREF_HIGH.pin2"],
    ]
    labels = defaultdict(list)
    copper = defaultdict(list)
    parent = []

    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def metal(layers, geometry, label=None):
        i = len(parent)
        parent.append(i)
        for layer in layers:
            copper[layer].append((geometry, i))
        if label:
            labels[label].append(i)

    net_names = {e["source_net_id"]: e["name"] for e in elements if e["type"] == "source_net"}
    xy = lambda p: (p["x"], p["y"])
    for e in elements:
        kind = e["type"]
        if kind == "pcb_smtpad":
            if e["shape"] == "circle":
                g = Point(xy(e)).buffer(e["radius"])
            elif e["shape"] == "polygon":
                g = Polygon([xy(p) for p in e["points"]])
            elif e["shape"] in ("rect", "rotated_rect"):
                w, h = e["width"]/2, e["height"]/2
                g = affinity.translate(affinity.rotate(box(-w, -h, w, h), e.get("ccw_rotation", 0)), *xy(e))
            else:
                raise ValueError(f"Unsupported channel pad shape {e['shape']}")
            metal([e["layer"]], g, pads.get(e.get("pcb_port_id")))
        elif kind == "pcb_trace":
            groups = defaultdict(list)
            for a, b in zip(e["route"], e["route"][1:]):
                layer = a.get("layer", a.get("to_layer"))
                if layer == b.get("layer", b.get("from_layer")) and xy(a) != xy(b):
                    groups[layer].append(LineString([xy(a), xy(b)]).buffer(a.get("width", b.get("width"))/2))
            for layer, parts in groups.items():
                shape = unary_union(parts)
                for island in getattr(shape, "geoms", [shape]):
                    metal([layer], island)
        elif kind == "pcb_via":
            metal(e["layers"], Point(xy(e)).buffer(e["outer_diameter"]/2))
        elif kind == "pcb_copper_pour":
            brep = e["brep_shape"]
            ring = lambda r: [xy(p) for p in r["vertices"]]
            g = Polygon(ring(brep["outer_ring"]), [ring(r) for r in brep["inner_rings"]])
            metal([e["layer"]], g, f"plane.{e['layer']}.{net_names.get(e.get('source_net_id'))}")

    for members in copper.values():
        shapes = [g for g, _ in members]
        tree = STRtree(shapes)
        for (g, i) in members:
            for k in tree.query(g, predicate="intersects"):
                parent[root(members[k][1])] = root(i)

    components = []
    for group in required:
        for label in group:
            if not labels[label]:
                raise ValueError(f"Missing copper for {label}")
        roots = {root(i) for label in group for i in labels[label]}
        if len(roots) != 1:
            raise ValueError(f"Open connection in {group}")
        components.extend(roots)
    if len(set(components)) != len(required):
        raise ValueError("Short between reference, supply, ground or opposite sides of R_VREF_CA")
    print("CPU J4, RAM H1 and RAM M8 each reach their local bypass. All three bypass grounds reach L2.")
    print("Divider ends reach L3 VDDS_DDR and L2 GND. R_VREF_CA separates the two reference copper nets.")


if __name__ == "__main__":
    verify(json.loads(Path(sys.argv[1]).read_text()))
