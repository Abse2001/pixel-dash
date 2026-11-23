"""Screen TI SPRS717L Table 7-65 rows 2 and 6 on the saved board and drill export."""
import csv
import json
import math
import re
import sys
from pathlib import Path

geometry = json.load(open(sys.argv[1]))
islands = json.load(open(sys.argv[2]))
pads = {f"{p['ref']}.{p['pin']}": p for p in geometry if p['kind'] == 'pad'}
island = {pin: (net, index) for net, groups in islands.items()
          for index, group in enumerate(groups) for pin in group}
with Path(__file__).with_name("module-bom.csv").open() as stream:
    hs_parts = {r["reference"] for r in csv.DictReader(stream) if r["MPN"] == "CL05B104KO5NNNC"}
references = sorted({p['ref'] for p in pads.values() if p['ref'] in hs_parts and re.fullmatch(r'C_DDR\d+', p['ref'])},
                    key=lambda ref: int(ref[5:]))
out = csv.writer(sys.stdout, lineterminator="\n")
out.writerow(("capacitor", "face", "receiver", "nearest_supply_ball", "supply_mm",
              "nearest_ground_ball", "ground_mm", "TI_limit_mm", "excess_mm", "placement"))
for ref in references:
    vp, gp = ref + ".pin1", ref + ".pin2"
    rail = pads[vp]['net']
    if rail not in {"VDDS_DDR_CPU", "VDDS_DDR"}:
        continue
    cpu = rail == "VDDS_DDR_CPU"
    receiver = "U1" if cpu else "U_DDR"
    center = [(a + b) / 2 for a, b in zip(pads[vp]['pos'], pads[gp]['pos'])]
    def nearest(pin):
        return min((math.dist(center, p['pos']), name) for name, p in pads.items()
                   if p['ref'] == receiver and island.get(name) == island[pin])
    supply, vball = nearest(vp)
    ground, gball = nearest(gp)
    limit = 10.16 if cpu else 3.81
    excess = max(0., max(supply, ground) - limit)
    out.writerow((ref, pads[vp]['layer'], receiver, vball, f"{supply:.4f}", gball,
                  f"{ground:.4f}", limit, f"{excess:.4f}", "FAIL" if excess else "PASS"))
