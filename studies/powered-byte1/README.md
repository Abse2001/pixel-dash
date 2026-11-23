# Powered byte-1 breakout

This study keeps the N5/P5 feeds, moves the VTP resistor ground return to a local plated barrel, and jointly reallocates D12 and D14. The complete 50-signal handheld remains available at 4b3d1c5. The repoured 46-signal power fallback is ff755ca.

| Net | Prior → current length (mm) | Barrel span | Estimated flight (ps) | Worst signed DQS skew, prior → current (ps) | Largest planar DQS mismatch (mm) |
|---|---:|---|---:|---:|---:|
| D12 | 23.6978 → 22.6622 | 2 × L1–L4, 2.840 mm total | 149.4821 | +7.6998 → −1.7710 | 0.3070 |
| D14 | 23.3728 → 22.5901 | 2 × L1–L4, 2.840 mm total | 149.0665 | +5.8252 → −2.1866 | 0.3790 |

The TI data-to-strobe matching limit is 0.635 mm. The project model screens the two strobe legs across isolated, mixed and odd-mode delay at ±3.6633 ps. Both nets have zero excess on these gates and fall inside the current two-through-via joint window of 22.3342–22.9981 mm. The separate 22.9998 mm ceiling is placement-derived. Model uncertainty includes the actual manufactured stack and waveform. The TI all-DQ peer gate of 0.635 mm requires a complete byte.

Drilled export verifies 43/50 distinct DDR links, no mapped shorts, 21/21 DCDC4 lands, 7/7 switched CPU DDR lands, J3/VTP and ZQ calibration, VREF divider and returns, local returns and sequenced MMC0. Both inner-plane residuals outside nominal antipads are below 0.000001 mm². Full-width DDR, MMC0 and routed raster references pass. The 0.102 mm copper, 6 mil via-edge, drill-spacing and nonlocal self-contact checks have zero findings. Seven DDR nets and 41 whole-board physical nets remain open. [Per-net timing and open signals](pair-first-timing.csv) · [Drilled land report](pair-first-cam.txt)

## Restored D13

The 44-link checkpoint brings D13 around the back of C_DDR34 and keeps the exported D12/D14 paths. D13 is 22.3511 mm with two L1–L4 transitions and 2.8400 mm total barrel. Estimated flight is 147.6875 ps. Worst signed skew against DQS1 is −3.5656 ps against ±3.6633 ps, leaving 0.0977 ps model headroom. Its largest planar strobe mismatch is 0.6181 mm against TI's 0.6350 mm, leaving 0.0169 mm. Both are narrow screening margins. The all-peer check remains open.

CAM verifies 44/50 distinct DDR connections, 1,077 plated barrels, zero mapped shorts, all 21 DCDC4 lands and all seven switched CPU DDR lands. The copper, drill, via-edge, full-width DDR/MMC0/raster, common-envelope and local return gates pass for this stage. Both plane residuals are below 0.000001 mm². There are 40 split mapped land nets. The six open DDR signals are A10, A14, D1, D10, D11 and D15. [Complete per-net timing](d13-timing.csv) · [Physical audit](d13-cam.txt)

## Restored D15

The D15 route detours around the ground-plane relief of D13's DRAM-side through via. It restores 45/50 distinct DDR signals while retaining the three passing data-to-strobe routes, N5/P5, J3 and separate switched and direct memory feeds. D15's length changes from 22.4276 mm to 23.3000 mm, with two L1–L4 transitions and 2.8400 mm of barrel. Estimated flight is 153.1616 ps. Its maximum planar strobe mismatch is 0.3317 mm against 0.6350 mm. Worst modeled signed strobe skew is +5.4050 ps against ±3.6633 ps, excess 1.7416 ps. It exceeds the 22.9981 mm joint upper bound. D15 timing and whole-byte matching remain open.

The cached-channel engineering export repours both layers with the pinned tscircuit copper-pour solver, then runs the normal board assembly and Gerber/drill export. The solver reproduced both reference polygons of the canonical pair-first channel identically before use. CAM finds 1,079 plated barrels, no mapped shorts, 39 split logical nets, complete switched and direct DDR power, and sequenced MMC0. The 0.102 mm copper, 6 mil via-edge, drill, full-width reference, local return and common-envelope checks pass. The missing DDR signals are A10, A14, D1, D10 and D11. [Full timing and targets](d15-timing.csv) · [Drilled physical audit](d15-cam.txt)

A clean native `bun run build` of 178dd63 independently reproduced the 45-link result. The per-net timing, class-spacing, full-width reference, and envelope CSVs matched the cached-channel export byte for byte. Drilled CAM reproduced all 39 split networks and the same land membership. Both 369.0434 mm² plane envelopes had 0.000000003 mm² residual outside nominal via antipads. Copper, via-edge, self-contact, drill, return, MMC0-reference and routed raster-reference checks passed. The strict 50-link and complete timing gates remain open.

## Shorter D5 on the powered baseline

With the original D3 crossing retained, a new D5 path reduces its length from 26.3833 to 25.7789 mm. It still uses two L1–L4 vias with 2.8400 mm total barrel. Estimated flight falls from 170.9494 to 167.4622 ps and worst signed skew from +38.0002 to +34.5131 ps. The model limit is ±3.6633 ps, leaving 30.8498 ps excess. TI data-to-strobe mismatch is 5.4468 mm against 0.6350 mm. The joint length window for the current DQS0 and two through vias is 19.7115–20.4313 mm. [All timing gates, including unresolved and missing signals](d5-timing.csv)

Exported CAM retained all 45 previously distinct links, 39 split nets board-wide, both DDR power paths and sequenced MMC0. Copper, via-edge, drill, local returns and full-width reference checks passed. [Complete physical audit](d5-cam.txt)
