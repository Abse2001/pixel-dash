"""Screen command capture on this module at the direct DRAM divider's DC corners."""
import argparse
import csv
import gzip
import io
import json
import runpy
import sys
from pathlib import Path

here = Path(__file__).resolve().parent
repo = here.parent
model = runpy.run_path(str(repo / "checks/command-source-echo.py"))
with gzip.open(repo / "studies/four-layer-through/board.circuit.json.gz", "rt") as stream:
    components = json.load(stream)  # IBIS package and I/O mapping only
with (here / "timing.csv").open() as stream:
    routes = [r for r in csv.DictReader(stream) if not r["net"].startswith("DDR_D")]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("archive", type=Path, help="TI SPRM552C IBIS archive")
parser.add_argument("--stack-delay", action="store_true",
                    help="substitute the finest-mesh isolated trace delays from impedance-screen.csv")
args = parser.parse_args()
if args.stack_delay:
    with (here / "impedance-screen.csv").open() as stream:
        impedance = list(csv.DictReader(stream))
    pitch = min(float(r["mesh_mm"]) for r in impedance)
    sections = [r for r in impedance if float(r["mesh_mm"]) == pitch]
    if len(sections) != 2 or any(float(r["width_mm"]) != .102 for r in sections):
        raise ValueError("This aggregate delay comparison requires one 0.102 mm width per section")
    rates = {r["section"]: float(r["flight_ps_per_mm"]) for r in sections}
    for r in routes:
        outer = float(r["length_mm"]) - float(r["inner_mm"])
        # Replace only the uniform-line parts of the original flight estimate.
        # Retain its barrel delay and nominal CK odd-mode correction.
        delta = (outer * (rates["outer"] - 5.884)
                 + float(r["inner_mm"]) * (rates["inner_ideal_two_planes"] - 6.671))
        r["flight_ps"] = float(r["flight_ps"]) + delta
channel = io.StringIO()
fields = ("net", "current_mm", "estimated_flight_ps")
writer = csv.DictWriter(channel, fieldnames=fields, lineterminator="\n")
writer.writeheader()
for r in routes:
    writer.writerow(dict(net=r["net"], current_mm=r["length_mm"] or "open", estimated_flight_ps=r["flight_ps"]))
out = csv.writer(sys.stdout, lineterminator="\n")
out.writerow(("net", "cpu_fixture_V", "dram_VDD_V", "dram_VREFCA_V", "ioctrl_assumed",
              "valid_cases", "total_cases", "common_capture_start_ps", "common_capture_end_ps",
              "minimum_VIX_headroom_mV", "receiver_signoff"))
# DCDC3 output tolerance only. Local drop, transients and the independent
# AM3354 transmitting supply require additional channel and PDN analysis.
for supply in (1.323, 1.350, 1.377):
    for fraction in (.49, .50, .51):
        vref = supply * fraction
        response = io.StringIO()
        model["screen"](components, io.StringIO(channel.getvalue()), args.archive, response,
                        0x318, receiver_window=True, receiver_vref=vref)
        results = list(csv.DictReader(io.StringIO(response.getvalue())))
        for name in sorted({r["net"] for r in results}):
            samples = [r for r in results if r["net"] == name]
            eligible = [r for r in samples if r["earliest_capture_ps"] and float(r["VIX_margin_mV"]) >= 0]
            window = ("", "")
            if len(eligible) == len(samples):
                window = (max(float(r["earliest_capture_ps"]) for r in eligible),
                          min(float(r["latest_capture_ps"]) for r in eligible))
            out.writerow((name, 1.35, supply, round(vref, 6), "0x318", len(eligible), len(samples),
                          *window, min(float(r["VIX_margin_mV"]) for r in samples), "OPEN"))
