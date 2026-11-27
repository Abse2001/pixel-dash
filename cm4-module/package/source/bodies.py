# Physical body clearance: every part as its MAXIMUM outline from the manufacturer's dimensions and tolerances
# (terminations and leads included), at its rendered position and rotation, against every other part on the same
# side. tscircuit's courtyard check uses generic outlines with margin; this answers whether two real parts can touch.
# Usage: python3 bodies.py  (reads dist/module.circuit.json, plan.json, design/pads.json) -> bodies-results.txt
import json, math, os, collections
from shapely.geometry import Polygon
from shapely.strtree import STRtree
D = os.path.dirname(os.path.abspath(__file__))
cj = json.load(open(D + "/dist/module.circuit.json")); plan = json.load(open(D + "/plan.json")); FPS = json.load(open(D + "/design/pads.json"))
from_parts = {q["name"]: q["part"] for q in plan["parts"]}
# maximum outline (long side, short side) in mm and where it comes from
MAX = {
    "C100N_0201": (0.63, 0.33, "0201: 0.6 +-0.03 x 0.3 +-0.03"), "R240_0201": (0.63, 0.33, "0201"),
    "C100N_0402": (1.10, 0.60, "0402: 1.0 +-0.1 x 0.5 +-0.1"), "C1U_0402": (1.10, 0.60, "0402"), "C2U2_0402": (1.10, 0.60, "0402"),
    "C4U7_0402": (1.10, 0.60, "0402"), "C10U_0402": (1.10, 0.60, "0402"), "C15P_0402": (1.10, 0.60, "0402"),
    "R10K": (1.10, 0.60, "0402"), "R100K": (1.10, 0.60, "0402"), "R1K": (1.10, 0.60, "0402"), "R2K2": (1.10, 0.60, "0402"), "R4K7": (1.10, 0.60, "0402"),
    "R1K_0402": (1.10, 0.60, "0402"), "R49R9_0402": (1.10, 0.60, "0402"), "R22K": (1.10, 0.60, "0402"), "R200K": (1.10, 0.60, "0402"),
    "C10U_0603": (1.70, 0.90, "CL10: 1.6 +-0.1 x 0.8 +-0.1"), "C22U_0603": (1.70, 0.90, "CL10"), "C4U7_0603": (1.70, 0.90, "CL10"),
    "C22U_0805": (2.15, 1.40, "CL21 code Q: 2.0 +-0.15 x 1.25 +-0.15"), "IND": (2.20, 1.80, "2016: 2.0 +-0.2 x 1.6 +-0.2"),
    "BUCK": (3.10, 3.00, "Silergy SOT23-5: body 2.8-3.1, over leads 2.7-3.0"), "NFET": (3.04, 2.64, "Vishay SOT-23: 2.80-3.04 x 2.10-2.64 over leads"),
    "PMIC": (6.10, 6.10, "VQFN-48 6.0 +-0.1"), "XTAL_24M": (3.30, 2.60, "3225: 3.2 +-0.1 x 2.5 +-0.1"),
    "CM4_HDR": (21.72, 3.37, "21.52 +-0.2 long, leads to the 3.37 mm pad edge"), "U1": (15.10, 15.10, "NFBGA-324 15 x 15 +-0.1"), "U_DDR": (14.10, 9.10, "FBGA-96 9 x 14 +-0.1"),
}
FP_OF = {"C100N_0201": "C0201", "R240_0201": "R0201"}
sc = {e["source_component_id"]: e["name"] for e in cj if e["type"] == "source_component"}
pads = collections.defaultdict(list)
for e in cj:
    if e["type"] == "pcb_smtpad" and e.get("pcb_component_id"): pads[e["pcb_component_id"]].append(e)
items = []
for c in (e for e in cj if e["type"] == "pcb_component"):
    name = sc[c["source_component_id"]]; part = from_parts.get(name, name)
    L, W, src = MAX[part]
    # long axis: along the spread of the part's own rendered pads (two-terminal parts, SOT, connector); the BGAs and the
    # QFN from the component's rendered extent
    ps = pads[c["pcb_component_id"]]; cx, cy = c["center"]["x"], c["center"]["y"]
    if part in ("U1", "U_DDR", "PMIC"): along_x = (c.get("width") or 1) >= (c.get("height") or 1)
    elif part in ("BUCK", "NFET"):  # SOT: the long body side runs along the pin rows, the leads across them
        xs = sorted({round(p["x"], 2) for p in ps}); ys = sorted({round(p["y"], 2) for p in ps}); along_x = len(xs) >= len(ys)
    else:
        xs = [p["x"] for p in ps]; ys = [p["y"] for p in ps]; along_x = (max(xs) - min(xs)) >= (max(ys) - min(ys))
    if part in ("U1", "U_DDR", "PMIC"): bx, by = cx, cy
    else: bx, by = (sum(p["x"] for p in ps) / len(ps), sum(p["y"] for p in ps) / len(ps)) if ps else (cx, cy)
    if part == "CM4_HDR": bx, by = cx, cy
    hx, hy = (L / 2, W / 2) if along_x else (W / 2, L / 2)
    items.append(dict(name=name, part=part, layer=c["layer"], poly=Polygon([(bx - hx, by - hy), (bx + hx, by - hy), (bx + hx, by + hy), (bx - hx, by + hy)]), src=src))
out = []
def say(s): print(s); out.append(s)
say(f"{len(items)} parts, maximum outlines from the manufacturers' tolerances (terminations and leads included)")
worst = []
for layer in ("top", "bottom"):
    its = [i for i in items if i["layer"] == layer]; tree = STRtree([i["poly"] for i in its])
    for a, ia in enumerate(its):
        for b in tree.query(ia["poly"].buffer(0.3)):
            b = int(b)
            if b <= a: continue
            ib = its[b]; g = ia["poly"].distance(ib["poly"]); ov = ia["poly"].intersection(ib["poly"]).area
            worst.append((g if ov == 0 else -math.sqrt(ov), layer, ia["name"], ib["name"], ia["part"], ib["part"]))
worst.sort()
touch = [w for w in worst if w[0] <= 0]
say(f"pairs within 0.3 mm of each other: {len(worst)}; touching or overlapping: {len(touch)}")
for th in (0.05, 0.1, 0.15, 0.2):
    say(f"  body gap below {th:.2f} mm: {sum(1 for w in worst if w[0] < th)}")
say("closest pairs (gap in mm, negative = overlap):")
for g, layer, a, b, pa, pb in worst[:25]: say(f"  {g:+.3f}  {layer:6s} {a} ({pa}) / {b} ({pb})")
open(D + "/bodies-results.txt", "w").write("\n".join(out) + "\n")
