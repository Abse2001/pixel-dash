#!/usr/bin/env bash
# Engineering comparison of exported planar copper on the 1080B study.
set -euo pipefail
cd "$(dirname "$0")/../.."
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
stem=pixel-dash-module
mkdir "$work/films"
cp "$stem.kicad_pro" "$work/"
python3 - "$stem.kicad_pcb" "$work/$stem.kicad_pcb" <<'PY'
from pathlib import Path
import re
import sys

source, target = map(Path, sys.argv[1:])
s = source.read_text()
for index, original, proposed in [(2, ".55", ".1"), (3, ".2104", "1.1208"), (4, ".55", ".1")]:
    pattern = rf'(\(layer "dielectric {index}"\s*\(type "[^"]+"\)\s*\(thickness )0{re.escape(original)}\)'
    s, count = re.subn(pattern, lambda m: m[1] + str(float(proposed)) + ")", s)
    if count != 1:
        raise ValueError(f"Unexpected input stack at dielectric {index}")
target.write_text(s)
PY
board="$work/$stem.kicad_pcb"
kicad-cli pcb drc --format json -o "$work/drc.json" "$board"
"${KICAD_PYTHON:-/usr/bin/python3}" extract-geometry.py "$board" >"$work/geom.json"
kicad-cli pcb export gerbers --disable-aperture-macros -o "$work/films/" \
  -l F.Cu,In1.Cu,In2.Cu,In3.Cu,In4.Cu,B.Cu,Edge.Cuts "$board"
kicad-cli pcb export drill -o "$work/films/" "$board"
python3 check-cam.py "$work/films" "$work/geom.json" "$work/islands.json" >"$work/physical.txt"
python3 check-via-spacing.py "$work/geom.json" >"$work/spacing.csv"
python3 check-reset-vref.py "$work/islands.json" >"$work/reset.txt"
python3 check-launch-reservations.py "$work/geom.json"
python3 check-open-connections.py "$work/islands.json" "$work/drc.json" >"$work/opens.csv"
python3 check-carrier-contacts.py "$work/islands.json" >"$work/contacts.csv"
python3 - "$work/drc.json" <<'PY'
import sys, json
with open(sys.argv[1]) as f:
    report = json.load(f)
if report["violations"]:
    raise SystemExit(report["violations"])
PY
diff -u drilled-cam.txt "$work/physical.txt"
diff -u via-spacing-findings.csv "$work/spacing.csv"
diff -u reset-vref.txt "$work/reset.txt"
diff -u open-connections.csv "$work/opens.csv"
diff -u carrier-continuity.csv "$work/contacts.csv"
