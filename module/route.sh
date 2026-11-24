#!/bin/bash
# Handheld signals: first the balls the DDR copper boxes in (via-in-pad, layer 4), then everything else on the outer layers.
# Each pass tries seeds until one converges; the seed used is printed.
cd "$(dirname "$0")/.."
rm -f module/routes.json
for mode in inner outer; do ok=0
  for seed in $(seq 1 ${SEEDS:-12}); do out=$(MODE=$mode SEED=$seed MAXIT=${MAXIT:-70} bun module/route-signals.ts | grep "SOLVED")
    case "$out" in SOLVED*) echo "$mode pass, seed $seed: $out"; ok=1; break;; esac
    echo "$mode pass, seed $seed: ${out:0:90}"; done
  [ $ok = 1 ] || { echo "$mode pass did not converge"; exit 1; }
done
