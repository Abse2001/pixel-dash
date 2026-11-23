"""Screen command capture on this module at the direct DRAM divider's DC corners."""
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
        model["screen"](components, io.StringIO(channel.getvalue()), Path(sys.argv[1]), response,
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
