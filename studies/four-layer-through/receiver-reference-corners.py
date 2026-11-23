"""Screen 0x318 at nominal CPU drive against independent DRAM DC reference corners."""
import csv
import gzip
import io
import json
import runpy
import sys
from pathlib import Path

study = Path(__file__).resolve().parent
model = runpy.run_path(str(study.parents[1] / "checks/command-source-echo.py"))
with gzip.open(study / "board.circuit.json.gz", "rt") as src:
    board = json.load(src)
writer = csv.writer(sys.stdout, lineterminator="\n")
writer.writerow(("cpu_fixture_V", "dram_supply_V", "vref_fraction", "dram_vref_V", "eligible", "tested",
                 "common_start_ps", "common_end_ps", "min_VIX_margin_mV", "setup_room_to_1250_ps", "hold_room_to_1250_ps"))
# These nominal-TX slices include Micron's two DC VREFCA limits (Table 24).
# The higher DRAM rail permits drop between DCDC3 and the switched CPU rail.
for supply in (1.35, 1.377):
    for ratio in (.49, .5, .51):
        result = io.StringIO()
        with (study / "jlc1080-command-timing.csv").open() as timing:
            model["screen"](board, timing, Path(sys.argv[1]), result, 0x318, receiver_window=True,
                            jlc_channel=True, receiver_vref=supply*ratio)
        rows = list(csv.DictReader(io.StringIO(result.getvalue())))
        eligible = [r for r in rows if r["earliest_capture_ps"]]
        bounds = ["", ""]
        room = ["", ""]
        if len(eligible) == len(rows):
            bounds = [max(float(r["earliest_capture_ps"]) for r in rows),
                      min(float(r["latest_capture_ps"]) for r in rows)]
            room = [round(1250-bounds[0], 3), round(bounds[1]-1250, 3)]
        writer.writerow((1.35, supply, ratio, round(supply*ratio, 6), len(eligible), len(rows), *bounds,
                         min(float(r["VIX_margin_mV"]) for r in rows), *room))
