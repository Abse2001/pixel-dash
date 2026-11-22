"""Check the TI Table 7-63 non-DDR signal setback at the routed DDR copper.

The default measures nearest copper. The optional convex-envelope screen also
checks space between routes and looks for uncategorized reference-plane gaps.
"""
import argparse
import csv
import json
import runpy
import sys
from pathlib import Path

from shapely import STRtree, prepare
from shapely.geometry import GeometryCollection
from shapely.ops import unary_union


def audit(board):
    copper = runpy.run_path(str(Path(__file__).with_name("audit-copper-contacts.py")))["copper"](board)
    by_id = {e[e["type"] + "_id"]: e for e in board if e["type"] + "_id" in e}
    signals = {e["subcircuit_connectivity_map_key"]: e["name"] for e in board
               if e["type"] == "source_trace" and (e.get("name") or "").startswith("DDR_")}
    if len(signals) != 50:
        raise ValueError("Expected 50 distinct DDR signal nets")
    support = {e["subcircuit_connectivity_map_key"] for e in board if e["type"] == "source_net"
               and e["name"] in {"GND", "VDDS_DDR", "DDR_VREF", "DDR_VREF_CA", "DDR_VTP", "DDR_ZQ"}}
    for layer in ("top", "bottom"):
        ddr = [(key, shape, max(p["width"] for p in by_id[oid]["route"] if p.get("layer") == layer))
               for oid, key, shape in copper[layer]
               if key in signals and by_id[oid]["type"] == "pcb_trace"]
        tree = STRtree([shape for _, shape, _ in ddr])
        search = 4 * max(width for _, _, width in ddr)
        for oid, key, shape in copper[layer]:
            if key in signals or key in support or by_id[oid]["type"] not in ("pcb_trace", "pcb_via"):
                continue
            worst = None
            for index in tree.query(shape, predicate="dwithin", distance=search):
                bus_key, neighbor, width = ddr[index]
                gap, limit = shape.distance(neighbor), 4 * width
                if gap < limit - 1e-7:
                    candidate = (gap - limit, gap, limit, signals[bus_key])
                    if worst is None or candidate < worst:
                        worst = candidate
            if worst:
                _, gap, limit, signal = worst
                yield layer, oid, signal, f"{gap:.6f}", f"{limit:.6f}"


def envelope_audit(board, archive=None):
    """Conservative common envelope for both routing faces, including the RAM lands."""
    copper = runpy.run_path(str(Path(__file__).with_name("audit-copper-contacts.py")))["copper"](board)
    by_id = {e[e["type"] + "_id"]: e for e in board if e["type"] + "_id" in e}
    signals = {e["subcircuit_connectivity_map_key"] for e in board
               if e["type"] == "source_trace" and (e.get("name") or "").startswith("DDR_")}
    if len(signals) != 50:
        raise ValueError("Expected 50 distinct DDR signal nets")
    support = {e["subcircuit_connectivity_map_key"] for e in board if e["type"] == "source_net"
               and e["name"] in {"GND", "VDDS_DDR", "DDR_VREF", "DDR_VREF_CA", "DDR_VTP", "DDR_ZQ"}}
    ram, = (e for e in board if e["type"] == "source_component" and e.get("name") == "U_DDR")
    ram_pcb, = (e["pcb_component_id"] for e in board if e["type"] == "pcb_component"
                and e["source_component_id"] == ram["source_component_id"])
    boundary_parts = []
    widths = set()
    for layer in ("top", "bottom"):
        for oid, key, shape in copper[layer]:
            item = by_id[oid]
            if key in signals or item.get("pcb_component_id") == ram_pcb:
                boundary_parts.append(shape)
                if item["type"] == "pcb_trace":
                    widths.update(p["width"] for p in item["route"] if p.get("layer") == layer)
    region = GeometryCollection(boundary_parts).convex_hull
    clearance = 4 * max(widths)
    margin = region.buffer(clearance, quad_segs=64)
    if archive:
        import ddr_cam
    for layer, reference in (("inner1", "GND"), ("inner2", "VDDS_DDR")):
        (plane_key, plane), = ((key, shape) for oid, key, shape in copper[layer]
                  if by_id[oid]["type"] == "pcb_copper_pour" and by_id[by_id[oid]["source_net_id"]]["name"] == reference)
        if archive:
            # A point inside the design pour identifies its connected CAM island.
            seed = plane.intersection(region).representative_point()
            member = {"inner1": "In1_Cu.gbr", "inner2": "In2_Cu.gbr"}[layer]
            plane = ddr_cam.reference(archive, member, seed)
        # Count signal and power via antipads separately from missing or split reference copper.
        antipads = unary_union([shape.buffer(0.16, quad_segs=64) for oid, key, shape in copper[layer]
                                if by_id[oid]["type"] in ("pcb_via", "pcb_plated_hole")
                                and key != plane_key and shape.distance(region) < 0.16])
        missing = region.difference(plane)
        residual = missing.difference(antipads).area
        print(f"{layer} {reference}: envelope {region.area:.4f} mm², uncovered {missing.area:.4f} mm², "
              f"uncovered outside nominal via antipads {residual:.4f} mm².", file=sys.stderr)
        if residual > 1e-6:
            yield layer, "reference_plane", reference, f"{residual:.6f}", ""
    for layer in ("top", "bottom"):
        if archive:
            member = {"top": "F_Cu.gbr", "bottom": "B_Cu.gbr"}[layer]
            # 1 µm absorbs coordinate rounding and polygonization of round lands.
            image = ddr_cam.artwork(archive, member).intersection(margin.envelope).buffer(0.001, quad_segs=16)
            prepare(image)
            prepare(margin)
        for oid, key, shape in copper[layer]:
            item = by_id[oid]
            if archive and margin.intersects(shape) and item["type"] in ("pcb_trace", "pcb_smtpad", "pcb_via", "pcb_plated_hole"):
                local = shape.intersection(margin)
                if not image.covers(local) and local.difference(image).area > 1e-6:
                    raise ValueError(f"{member} is missing copper on {oid} inside the screened region")
            if key in signals or key in support or item["type"] not in ("pcb_trace", "pcb_via", "pcb_plated_hole"):
                continue
            if shape.distance(region) < clearance - 1e-7:
                yield layer, oid, key, f"{shape.intersection(region).area:.6f}", f"{shape.intersection(margin).area:.6f}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("circuit", type=Path)
    parser.add_argument("--envelope", action="store_true", help="Screen a convex envelope around DDR routing and RAM lands")
    parser.add_argument("--gerbers", type=Path, help="Reconstruct copper from the exported Gerber ZIP (requires gerbonara)")
    args = parser.parse_args()
    if args.gerbers and not args.envelope:
        parser.error("--gerbers requires --envelope")
    board = json.loads(args.circuit.read_text())
    out = csv.writer(sys.stdout)
    if args.envelope:
        findings = sorted(envelope_audit(board, args.gerbers))
        out.writerow(("layer", "copper_or_plane", "net", "finding_area_in_region_mm2", "finding_area_including_margin_mm2"))
        print(f"{len(findings)} findings across signal and reference layers in the conservative envelope screen.", file=sys.stderr)
    else:
        findings = sorted(audit(board))
        out.writerow(("layer", "non_ddr_copper", "adjacent_ddr_signal", "edge_gap_mm", "four_widths_mm"))
        print(f"{len(findings)} unrelated signal trace/via and layer combinations inside the 4w setback.", file=sys.stderr)
    out.writerows(findings)
    sys.exit(bool(findings))
