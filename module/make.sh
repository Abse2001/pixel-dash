#!/bin/bash
# Rebuilds the compute module from the verified DDR block (ddr-route/out/module9) to fabrication files.
set -e
cd "$(dirname "$0")/.."
bun module/plan.ts                 # parts, vias, connector pins around the fixed DDR copper
module/route.sh                    # handheld signals: boxed-in balls on layer 4, the rest on the outer layers
TOPUP=1 bun module/plan.ts         # bypass capacitors that had to wait for the signal routes
bun module/planes.ts               # inner-layer copper
bun module/build.tsx               # module/dist/module.circuit.json
bun module/check.ts                # whole-board check
bun module/export.ts               # module/fab: gerbers, drills, BOM, pick-and-place, pin map
python3 module/layers.py           # module/fab/views/*.png
