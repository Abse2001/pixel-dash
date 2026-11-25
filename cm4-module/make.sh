#!/bin/bash
# Rebuilds the CM4 module from the verified DDR block (external/ddr-route/out/module9) to fabrication files.
set -e
cd "$(dirname "$0")"
bun design/pads.tsx > /dev/null    # pad geometry of the new parts as tscircuit renders them
bun plan.ts                        # parts, vias, connector pins, power/PHY/strap circuits around the fixed DDR copper
rm -f routes.json                  # signals: first the nets that start at balls the DDR copper boxes in, then the rest
for mode in inner outer; do ok=0
  for seed in $(seq 1 ${SEEDS:-8}); do out=$(MODE=$mode SEED=$seed MAXIT=${MAXIT:-80} bun route.ts | grep "SOLVED")
    case "$out" in SOLVED*) echo "$mode pass, seed $seed: $out"; ok=1; break;; esac
    echo "$mode pass, seed $seed: ${out:0:100}"; done
  [ $ok = 1 ] || { echo "$mode pass did not converge"; exit 1; }
done
TOPUP=1 bun plan.ts                # bypass capacitors that had to wait for the signal routes
bun planes.ts                      # inner-layer copper
bun build.tsx                      # dist/module.circuit.json
bun check.ts                       # whole-board check
bun export.ts                      # fab: gerbers, drills, BOM, pick-and-place, CM4 pin map
python3 layers.py                  # fab/views/*.png
