"""Intersect modeled command capture windows across the DRAM divider and rail cases."""
import csv
import gzip
import io
import json
import runpy
import sys
from collections import defaultdict
from pathlib import Path

here = Path(__file__).resolve().parent
repo = here.parents[2]
screen = runpy.run_path(str(repo / "checks/command-source-echo.py"))["screen"]
with gzip.open(repo / "studies/four-layer-through/board.circuit.json.gz", "rt") as source:
    mapping = json.load(source)
with (here / "flight.csv").open() as source:
    rows = list(csv.DictReader(source))
with (here / "corners.csv").open() as source:
    uniform = [r for r in csv.DictReader(source) if float(r["mesh_mm"]) == .0025]
writer = csv.writer(sys.stdout, lineterminator="\n")
writer.writerow(["stack_corner", "net", "eligible", "cases", "capture_start_ps",
                 "capture_end_ps", "min_VIX_margin_mV", "receiver_signoff"])
for corner in dict.fromkeys(row["corner"] for row in rows):
    channel = io.StringIO()
    routes = csv.writer(channel, lineterminator="\n")
    routes.writerow(["net","current_mm","estimated_flight_ps"])
    for row in rows:
        if row["corner"] == corner and not row["net"].startswith("DDR_D"):
            routes.writerow([row["net"],row["length_mm"],row["estimated_flight_ps"]])
    z = {r["layer"]: float(r["Z_ohm"]) for r in uniform if r["corner"] == corner}
    nets = defaultdict(list)
    for vdd in (1.323, 1.350, 1.377):
        for ratio in (.49,.50,.51):
            for ca in ("outer", "inner"):
                for ck in ("outer", "clock_odd"):
                    impedance = {r["net"]: z[ck] if r["net"] in ("DDR_CK", "DDR_CKn") else z[ca]
                                 for r in rows if r["corner"] == corner}
                    output = io.StringIO()
                    screen(mapping, io.StringIO(channel.getvalue()), Path(sys.argv[1]), output,
                           0x318, receiver_window=True, receiver_vref=vdd * ratio, line_impedances=impedance)
                    for r in csv.DictReader(io.StringIO(output.getvalue())):
                        nets[r["net"]].append(r)
    for name, cases in sorted(nets.items()):
        valid = [r for r in cases if r["earliest_capture_ps"] and float(r["VIX_margin_mV"]) >= 0]
        window = ("","")
        if len(valid) == len(cases):
            window = (max(float(r["earliest_capture_ps"]) for r in valid),
                      min(float(r["latest_capture_ps"]) for r in valid))
        writer.writerow([corner,name,len(valid),len(cases),*window,
                         min(float(r["VIX_margin_mV"]) for r in cases),"OPEN"])
