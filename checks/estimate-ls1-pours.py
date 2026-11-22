"""Estimate L4 spreading resistance on the two LS1 islands in the Gerber/drill export."""
import argparse
from hdi_build import LEGACY, WURTH
import json
import runpy
from pathlib import Path
from zipfile import ZipFile

import numpy as np
from scipy.ndimage import label
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve
from shapely import intersects_xy, prepare
from shapely.geometry import LineString, Point, box
from shapely.ops import unary_union

from ddr_cam import artwork


def sheet_conductance(shape, terminals, pitch):
    """Finite-volume sheet with one square per face link and equipotential via lands."""
    xmin, ymin, xmax, ymax = shape.bounds
    x = np.arange(xmin + pitch / 2, xmax, pitch)
    y = np.arange(ymin + pitch / 2, ymax, pitch)
    prepare(shape)
    mask = intersects_xy(shape, x[None, :], y[:, None])
    def contact(v):
        return mask & ((x[None, :] - v["x"])**2 + (y[:, None] - v["y"])**2 <= (v["outer_diameter"]/2)**2)
    contacts = [contact(v) for v in terminals]
    pieces, _ = label(mask)
    ids = np.unique(pieces[contacts[0]])
    if len(ids) != 1 or not all(c.any() and np.all(pieces[c] == ids[0]) for c in contacts):
        raise ValueError("Mesh does not connect the terminal annuli")
    mask &= pieces == ids[0]
    nodes = np.full(mask.shape, -1, dtype=int)
    nodes[mask] = np.arange(mask.sum())
    left, right = nodes[:, :-1], nodes[:, 1:]
    down, up = nodes[:-1, :], nodes[1:, :]
    horizontal = (left >= 0) & (right >= 0)
    vertical = (down >= 0) & (up >= 0)
    a = np.r_[left[horizontal], down[vertical]]
    b = np.r_[right[horizontal], up[vertical]]
    edge = np.ones(len(a))
    system = coo_matrix((np.r_[edge, edge, -edge, -edge], (np.r_[a, b, a, b], np.r_[a, b, b, a])),
                        shape=(mask.sum(), mask.sum())).tocsr()
    # Drive each terminal in turn with the other terminals grounded.
    potentials = np.zeros((mask.sum(), len(contacts)))
    for k, c in enumerate(contacts):
        potentials[nodes[c], k] = 1
    unknown = ~np.any(potentials, axis=1)
    potentials[unknown] = spsolve(system[unknown][:, unknown].tocsc(), -(system @ potentials)[unknown])
    currents = system @ potentials
    return np.array([currents[nodes[c]].sum(axis=0) for c in contacts])


def squares(shape, first, last, pitch):
    return 1 / sheet_conductance(shape, [first, last], pitch)[0, 0]


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("board", type=Path)
parser.add_argument("archive", type=Path)
parser.add_argument("--joined", action="store_true", help="Also solve both L3/L4 feed paths together")
parser.add_argument("--wurth", action="store_true")
parser.add_argument("--return-path", action="store_true", help="screen a cropped L2 return between CPU A1 and a PMIC exposed-pad via")
args = parser.parse_args()
stack = WURTH if args.wurth else LEGACY
board = json.loads(args.board.read_text())
archive = args.archive
via = {e["pcb_via_id"]: e for e in board if e["type"] == "pcb_via"}
drill = runpy.run_path(str(Path(__file__).with_name("audit-channel-drills.py")))
holes = []
inner_holes = []
with ZipFile(archive) as z:
    for member, expected in drill["expected_drills"](board).items():
        if "L4" not in member and "npth" not in member and not (args.joined and "L2-L3" in member):
            continue
        drill["compare"](member, z.read(member).decode().splitlines(), expected.copy())
        for diameter, points in expected:
            center = Point(points[0]) if len(points) == 1 else LineString(points)
            hole = center.buffer(diameter / 2, quad_segs=48)
            if "L4" in member or "npth" in member:
                holes.append(hole)
            if args.joined:
                inner_holes.append(hole)
image = artwork(archive, "B_Cu.gbr").difference(unary_union(holes))
pairs = [("upper", "bridge_upper"), ("bridge_lower", "balls")]
islands = []
for a, b in pairs:
    first, last = [via["via_ddr_supply_" + name] for name in (a, b)]
    def annulus(v):
        return Point(v["x"], v["y"]).buffer(v["outer_diameter"] / 2)
    island, = (p for p in image.geoms if p.intersection(annulus(first)).area > .001 and
               p.intersection(annulus(last)).area > .001)
    islands.append((island, first, last))
columns = "pitch_mm,upper_squares,lower_squares,total_mOhm_{foil}um_20C,drop_mV_300mA"
if "via_ddr_supply_lower_bank" in via:
    columns += ",direct_lower_squares,direct_lower_mOhm_{foil}um_20C"
print(columns.format(foil=f"{stack.foil*1000:g}"))
for pitch in (.080, .055, .040, .030, .025):
    upper, lower = [squares(*data, pitch) for data in islands]
    resistance = (upper + lower) * .01724 / stack.foil
    row = f"{pitch:.3f},{upper:.4f},{lower:.4f},{resistance:.4f},{.300*resistance:.4f}"
    if "via_ddr_supply_lower_bank" in via:
        sheet, _, cpu = islands[1]
        contact = via["via_ddr_supply_lower_bank"]
        direct = squares(sheet, contact, cpu, pitch)
        row += f",{direct:.4f},{direct*.01724/stack.foil:.4f}"
    print(row)

if args.joined:
    inner = artwork(archive, "In2_Cu.gbr").difference(unary_union(inner_holes))
    sheets = []
    for layer, image_layer, names in [
        ("L3", inner, ["output", "upper", "lower_bank"]),
        ("L3", inner, ["bridge_upper", "bridge_lower"]),
        ("L4", image, ["upper", "bridge_upper"]),
        ("L4", image, ["bridge_lower", "lower_bank", "balls"]),
    ]:
        contacts = [via["via_ddr_supply_" + name] for name in names]
        sheet, = (g for g in image_layer.geoms if all(g.intersection(annulus(v)).area > .001 for v in contacts))
        sheets.append((layer, names, contacts, sheet))
    # Nodes represent the lands on each side of the four short plated barrel sections.
    labels = [(layer, name) for layer, names, _, _ in sheets for name in names]
    high = labels.index(("L3", "output"))
    low = labels.index(("L4", "balls"))
    print("pitch_mm,inner_um,outer_um,joined_L3_output_to_L4_balls_mOhm_at_20C")
    for pitch in (.05, .035, .025):
        blocks = [sheet_conductance(sheet, contacts, pitch) for _, _, contacts, sheet in sheets]
        for inner_um in ((30,) if args.wurth else (35, 17.5)):
            network = np.zeros((len(labels), len(labels)))
            for (layer, names, _, _), block in zip(sheets, blocks):
                indices = [labels.index((layer, name)) for name in names]
                foil_mm = inner_um / 1000 if layer == "L3" else stack.foil
                network[np.ix_(indices, indices)] += block * foil_mm / .01724
            for name in ("upper", "bridge_upper", "bridge_lower", "lower_bank"):
                a, b = (labels.index((layer, name)) for layer in ("L3", "L4"))
                drill_mm = via["via_ddr_supply_" + name]["hole_diameter"]
                conductance = np.pi * stack.wall * (drill_mm + stack.wall) / (.01724 * stack.outer_to_inner)
                network[np.ix_([a,b],[a,b])] += conductance * np.array([[1., -1.], [-1., 1.]])
            # Apply 1 A between the source and sink lands. Potentials are in millivolts.
            free = np.arange(len(labels)) != low
            current = np.zeros(len(labels))
            current[high] = 1
            volts = np.zeros(len(labels))
            volts[free] = np.linalg.solve(network[np.ix_(free,free)], current[free])
            if not np.allclose(network @ volts, current - (np.arange(len(labels)) == low), atol=1e-7):
                raise ValueError("Sheet network fails terminal current conservation")
            print(f"{pitch:.3f},{inner_um:g},{1000*stack.foil:g},{volts[high]:.4f}", flush=True)

if args.return_path:
    components = {e["name"]: e["source_component_id"] for e in board if e["type"] == "source_component"}
    pin = next(e for e in board if e["type"] == "source_port" and
               e["source_component_id"] == components["U1"] and e["name"] == "A1")
    pad = next(e for e in board if e["type"] == "pcb_port" and e.get("source_port_id") == pin["source_port_id"])
    ep = next(e for e in board if e["type"] == "source_port" and
              e["source_component_id"] == components["U_PMIC"] and e["name"] == "EP")
    ep_port = next(e for e in board if e["type"] == "pcb_port" and e.get("source_port_id") == ep["source_port_id"])
    ep_land, = [e for e in board if e["type"] == "pcb_smtpad" and e.get("pcb_port_id") == ep_port["pcb_port_id"]]
    ground = next(e for e in board if e["type"] == "source_net" and e["name"] == "GND")["subcircuit_connectivity_map_key"]
    balls = json.loads((Path(__file__).resolve().parents[1] / "am3354/processor-balls.json").read_text())
    if balls[pin["name"]] != "VSS" or ep.get("subcircuit_connectivity_map_key") != ground:
        raise ValueError("Return endpoints are not assigned to ground")
    gnd_vias = [v for v in via.values() if v.get("subcircuit_connectivity_map_key") == ground and
                {"top","inner1"} <= set(v["layers"])]
    cpu_via, = [v for v in gnd_vias if np.hypot(v["x"]-pad["x"], v["y"]-pad["y"]) < .001]
    thermal = [v for v in gnd_vias if abs(v["x"]-ep_land["x"]) + v["outer_diameter"]/2 < ep_land["width"]/2
               and abs(v["y"]-ep_land["y"]) + v["outer_diameter"]/2 < ep_land["height"]/2]
    end = min(thermal, key=lambda v: np.hypot(v["x"]-cpu_via["x"], v["y"]-cpu_via["y"]))
    crop = box(min(cpu_via["x"],end["x"])-4, min(cpu_via["y"],end["y"])-5,
               max(cpu_via["x"],end["x"])+4, max(cpu_via["y"],end["y"])+5)
    bores = []
    with ZipFile(archive) as z:
        for member, expected in drill["expected_drills"](board).items():
            if member == "drill-L3-L4.drl":
                continue
            drill["compare"](member, z.read(member).decode().splitlines(), expected.copy())
            for diameter, points in expected:
                center = Point(points[0]) if len(points) == 1 else LineString(points)
                if crop.distance(center) <= diameter/2:
                    bores.append(center.buffer(diameter/2, quad_segs=48))
    sheet = artwork(archive, "In1_Cu.gbr").intersection(crop).difference(unary_union(bores))
    barrel = sum(.01724*stack.outer_to_inner/(np.pi*stack.wall*(v["hole_diameter"]+stack.wall))
                 for v in (cpu_via,end))
    print(f"Single L2 return from U1.A1 to EP via at ({end['x']:.4f}, {end['y']:.4f}); both barrels included.")
    for pitch in (.075, .05):
        resistance = squares(sheet,cpu_via,end,pitch)*.01724/stack.foil + barrel
        print(f"  mesh {pitch:g} mm: {resistance:.3f} mOhm at 20 C, "
              f"{resistance*(1+.00393*60)*.25:.3f} mV at 250 mA and 80 C.")
