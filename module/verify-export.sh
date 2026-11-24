#!/usr/bin/env bash
# Check the saved board, without refilling or changing the candidate.
set -euo pipefail
cd "$(dirname "$0")"
case "${1:-}" in
    ""|--require-connected) ;;
    *) echo "Usage: $0 [--require-connected]" >&2; exit 2 ;;
esac
if (( $# > 1 )); then exit 2; fi
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
python3 check-open-connections.py "$out/pad-islands.json" "$out/drc.json" "${1:-}" > "$out/open-connections.csv"
diff -u open-connections.csv "$out/open-connections.csv"
python3 check-carrier-contacts.py "$out/pad-islands.json" > "$out/carrier-continuity.csv"
diff -u carrier-continuity.csv "$out/carrier-continuity.csv"
python3 check-via-spacing.py "$out/geometry.json" > "$out/via-spacing-findings.csv"
python3 check-timing.py "$out/geometry.json" > "$out/timing.csv"
python3 check-reset-vref.py "$out/pad-islands.json" > "$out/reset-vref.txt"
python3 check-bypass-placement.py "$out/geometry.json" "$out/pad-islands.json" > "$out/bypass-placement.csv"
diff -u bypass-placement.csv "$out/bypass-placement.csv"
python3 check-carrier-strap-load.py "$out/pad-islands.json" > "$out/carrier-strap-load.csv"
python3 check-carrier-strap-load.py "$out/pad-islands.json" --panel-context > "$out/panel-reset-path.txt"
diff -u panel-reset-path.txt "$out/panel-reset-path.txt"
diff -u carrier-strap-load.csv "$out/carrier-strap-load.csv"
diff -u reset-vref.txt "$out/reset-vref.txt"
OPENBLAS_NUM_THREADS=1 python3 check-impedance.py "$out/geometry.json" > "$out/impedance-screen.csv"
diff -u impedance-screen.csv "$out/impedance-screen.csv"
diff -u drilled-cam.txt "$out/drilled-cam.txt"
OPENBLAS_NUM_THREADS=1 python3 check-core-drop.py "$out/geometry.json" > "$out/core-drop.csv"
diff -u core-drop.csv "$out/core-drop.csv"
python3 check-signal-paths.py "$out/geometry.json" "$out/timing.csv"
diff -u timing.csv "$out/timing.csv"
diff -u via-spacing-findings.csv "$out/via-spacing-findings.csv"
cat "$out/drilled-cam.txt"
