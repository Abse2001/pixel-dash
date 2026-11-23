"""Unloaded shared-divider tracking at CPU E5, using the DC feed to a lumped CPU load."""
import csv
import gzip
import json
import re
import sys
from pathlib import Path

study = Path(__file__).resolve().parent
with gzip.open(study / "board.circuit.json.gz", "rt") as src:
    parts = {p["name"]: p for p in json.load(src) if p["type"] == "source_component"}
for name in ("R_VREF_HIGH", "R_VREF_LOW"):
    assert parts[name]["manufacturer_part_number"] == "0402WGF1001TCE"
    assert parts[name]["resistance"] == 1000

mesh = (study / "cpu-feed-mesh.txt").read_text()
def finest_mesh(label):
    matches = re.findall(label + r" mesh ([\d.]+) mm: ([\d.]+) mOhm", mesh)
    return min((float(pitch), float(r)) for pitch, r in matches)[1]

# Only downstream switched L4 and E5-row L1 copper. Ground offsets, transient
# effects, input/feed traces, other series elements and bleed current are omitted.
partial_mohm = finest_mesh("buffered") + finest_mesh("CPU row")
writer = csv.writer(sys.stdout, lineterminator="\n")
writer.writerow(("rail_V", "divider_ratio", "allowed_drop_mV", "switch_sensitivity_mOhm",
                 "partial_E5_path_mOhm", "load_A", "drop_mV", "J4_upper_margin_mV"))
for rail in (1.323, 1.350, 1.377):
    for top, bottom in ((1010, 990), (1000, 1000), (990, 1010)):
        ratio = bottom / (top + bottom)
        for switch in (25, 34, 40):
            load = .250
            drop = load * (switch + partial_mohm)
            margin = .51 * (1000 * rail - drop) - 1000 * rail * ratio
            writer.writerow((rail, ratio, round(1000 * rail * (1 - ratio / .51), 5),
                             switch, round(partial_mohm, 4), load, round(drop, 5), round(margin, 5)))
