"""Estimate flights on the existing artwork using each 1080B dielectric/foil corner."""
import csv
import sys
from pathlib import Path

here = Path(__file__).resolve().parent
with (here / "corners.csv").open() as source:
    sections = [row for row in csv.DictReader(source) if float(row["mesh_mm"]) == .0025]
with Path(sys.argv[1]).open() as source:
    routes = {row["net"]: row for row in csv.DictReader(source)}

layers = ("F.Cu", "In1.Cu", "In2.Cu", "In3.Cu", "In4.Cu", "B.Cu")
writer = csv.writer(sys.stdout, lineterminator="\n")
writer.writerow(["corner", "net", "length_mm", "barrel_mm", "estimated_flight_ps",
                 "signed_skew_ps", "model_limit_ps", "model_screen"])
for outer in (row for row in sections if row["layer"] == "outer"):
    corner = outer["corner"]
    inner = next(row for row in sections if row["layer"] == "inner" and row["corner"] == corner)
    height, foil = float(outer["height_scale"]), float(outer["foil_scale"])
    thickness = [mm * foil for mm in (.035, .0152, .0152, .0152, .0152, .035)]
    depth = dict.fromkeys(layers, 0.)
    for i, dielectric in enumerate((.0764, .100, 1.1208, .100, .0764)):
        depth[layers[i+1]] = depth[layers[i]] + dielectric * height + (thickness[i] + thickness[i+1]) / 2
    times = {}
    barrels = {}
    for net, row in routes.items():
        barrel = 0.
        for span in row["via_contacts"].split(";") if row["via_contacts"] else ():
            first, last = span.split("/")
            barrel += abs(depth[first] - depth[last])
        barrels[net] = barrel
        length, internal = float(row["length_mm"]), float(row["inner_mm"])
        external = length - internal
        old_uncoupled = external * 5.884 + internal * 6.671 + float(row["traversed_barrel_mm"]) * 6.600
        coupling = float(row["flight_ps"]) - old_uncoupled
        uncoupled = external * float(outer["delay_ps_per_mm"]) + internal * float(inner["delay_ps_per_mm"]) + barrel * 6.600
        paired = net.startswith("DDR_DQS") or net in ("DDR_CK", "DDR_CKn")
        times[net] = (uncoupled, uncoupled + coupling, uncoupled - length * .145 if paired else uncoupled)
    for net, row in routes.items():
        limit = row["model_limit_ps"]
        skew = None
        if net.startswith("DDR_D"):
            lane = int(net[-1]) if net.startswith(("DDR_DQS", "DDR_DQM")) else int(net[5:]) // 8
            strobes = (f"DDR_DQS{lane}", f"DDR_DQSn{lane}")
            skew = max((a-b for peer in strobes if peer != net for a,b in zip(times[net],times[peer])), key=abs)
        elif net in ("DDR_CK", "DDR_CKn"):
            mate = "DDR_CKn" if net == "DDR_CK" else "DDR_CK"
            skew = times[net][1]-times[mate][1]
        elif net != "DDR_RESETn":
            skew = times[net][1]-(times["DDR_CK"][1]+times["DDR_CKn"][1])/2
        status = ("PASS" if abs(skew) <= float(limit) else "FAIL") if limit else "receiver required"
        writer.writerow([corner, net, row["length_mm"], round(barrels[net],5), round(times[net][1],5),
                         round(skew,5) if skew is not None else "", limit, status])
