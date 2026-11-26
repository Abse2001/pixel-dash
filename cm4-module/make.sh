#!/bin/bash
# Rebuilds the CM4 module from the verified DDR block (external/ddr-route/out/module9) to fabrication files.
# AUTOROUTER=<tscircuit-autorouter checkout> routes with that source tree (see AUTOROUTER-NOTES.md); without it the
# installed @tscircuit/capacity-autorouter package is used.
set -e
cd "$(dirname "$0")"
bun design/pads.tsx > /dev/null    # pad geometry of the new parts as tscircuit renders them
PREPLACE=1 bun plan.ts             # every part, via and fixed trace, bypass capacitors included, around the fixed DDR copper
EFFORT=${EFFORT:-2} bun autoroute.ts  # signal nets: tscircuit autorouter, default pipeline (top, layer 4, bottom)
bun planes.ts                      # inner-layer copper
bun build.tsx                      # dist/module.circuit.json
bun check.ts                       # whole-board check
bun export.ts                      # fab: gerbers, drills, BOM, pick-and-place, CM4 pin map
python3 layers.py                  # fab/views/*.png
