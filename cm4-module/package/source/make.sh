#!/bin/bash
# Rebuilds the CM4 module from the verified DDR block (external/ddr-route/out/module9) to fabrication files, following
# the RK3566 module's routing playbook: placement and fixed copper first, supply islands and their corridors, then the
# negotiated-congestion router for everything else, then planes and an independent check.
#   ROUTE=1  also re-route (pb/route.ts; long: run several SEEDs in parallel by hand and import the best, see README.md)
set -e
cd "$(dirname "$0")"
bun design/pads.tsx > /dev/null                                   # pad geometry of the parts as tscircuit renders them
PREPLACE=1 bun plan.ts                                            # every part, via and fixed trace around the fixed DDR copper
FAT=0 ROUTES=none CORRIDORS_OUT=pb/corridors.json bun planes.ts > /dev/null  # supply islands without signals: their (thin) corridors
bun pb/export.ts                                                  # router input: pads, fixed copper, nets
if [ -n "$ROUTE" ]; then (cd pb && SEED=${SEED:-1} MAXIT=${MAXIT:-80} OUT=_make bun route.ts) && bun pb/import.ts pb/routes_make.json
else bun pb/import.ts ${PB_ROUTES:-pb/routing.json}; fi             # the chosen routing (pb/routing.json) -> routes.json
bun planes.ts                                                     # layer 2/5 ground, layer 3 islands, layer 4 core/MPU islands
bun build.tsx                                                     # dist/module.circuit.json
bun check.ts                                                      # whole-board check
bun export.ts                                                     # fab: gerbers, drills, BOM, pick-and-place, CM4 pin map
CIRCUIT=dist/module.circuit.json CPL=fab/cpl.csv bun fix-pnp.ts > fab/pnp-rotations.txt  # rotations checked against JLCPCB's footprints (exits 1 if any part is unverified)
python3 layers.py                                                 # fab/views/*.png
