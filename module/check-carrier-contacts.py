"""Check every DF40 contact against its designated module endpoint on drilled CAM."""
import csv
import json
import sys
from pathlib import Path

here = Path(__file__).resolve().parent
with (here / "carrier-pinout.csv").open() as stream:
    contacts = list(csv.DictReader(stream))
islands = json.loads(Path(sys.argv[1]).read_text())
locations = {}
for net, groups in islands.items():
    for island, group in enumerate(groups):
        for land in group:
            if land in locations:
                raise SystemExit(f"Land occurs on multiple islands: {land}")
            locations[land] = (net, island)

expected = {f"J_CARRIER.{n}" for n in range(1, 81)}
exported = {land for land in locations if land.startswith("J_CARRIER.")}
assigned = {"J_CARRIER." + row["contact"] for row in contacts}
if len(contacts) != 80 or assigned != expected or exported != expected:
    raise SystemExit("DF40 assignment and exported lands must each contain contacts 1 through 80")

writer = csv.writer(sys.stdout, lineterminator="\n")
writer.writerow(("contact", "function", "module_terminal", "drilled_continuity"))
for row in contacts:
    contact = "J_CARRIER." + row["contact"]
    terminal = row["module_terminal"]
    for land in (contact, terminal):
        if land not in locations or locations[land][0] != row["module_net"]:
            raise SystemExit(f"{land}: expected {row['module_net']}, found {locations.get(land)}")
    status = "CONNECTED" if locations[contact] == locations[terminal] else "OPEN"
    writer.writerow((row["contact"], row["signal"], terminal, status))
