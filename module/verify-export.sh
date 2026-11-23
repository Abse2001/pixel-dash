#!/usr/bin/env bash
# Check the saved board, without refilling or changing the candidate.
set -euo pipefail
cd "$(dirname "$0")"
out=$(mktemp -d)
mkdir "$out/films"
board=pixel-dash-module.kicad_pcb
echo "Engineering verification directory $out"
kicad-cli pcb drc --format json -o "$out/drc.json" "$board"
python3 - "$out/drc.json" <<'PY'
import json, sys
from pathlib import Path
report = json.loads(Path(sys.argv[1]).read_text())
print(f"{len(report['unconnected_items'])} unconnected items")
if report["violations"]:
    raise SystemExit(f"{len(report['violations'])} DRC violations")
PY
"${KICAD_PYTHON:-/usr/bin/python3}" extract-geometry.py "$board" > "$out/geometry.json"
kicad-cli pcb export gerbers --disable-aperture-macros -o "$out/films/" -l F.Cu,In1.Cu,In2.Cu,In3.Cu,In4.Cu,B.Cu,Edge.Cuts "$board"
kicad-cli pcb export drill -o "$out/films/" "$board"
python3 check-cam.py "$out/films" "$out/geometry.json" "$out/pad-islands.json" > "$out/drilled-cam.txt"
python3 check-via-spacing.py "$out/geometry.json" > "$out/via-spacing-findings.csv"
python3 check-timing.py "$out/geometry.json" > "$out/timing.csv"
diff -u drilled-cam.txt "$out/drilled-cam.txt"
diff -u timing.csv "$out/timing.csv"
diff -u via-spacing-findings.csv "$out/via-spacing-findings.csv"
cat "$out/drilled-cam.txt"
