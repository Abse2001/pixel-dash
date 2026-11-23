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

## Isolated D3 and D15 crossing trial

D15 previously crossed the region occupied by the intermediate L1 bridge on D3. Moving the two middle D3 vias together opened a shorter D15 approach to the RAM. The final D15 bend and local tuning use its existing two L1–L4 vias. The N5/P5 supplies and calibration routes remain in place. The powered baseline is fc8c13c.

- **D15 passes its local gates.** From the powered baseline its planar length changes from 23.3000 to 22.6549 mm and its estimated flight changes from 153.1616 to 149.4400 ps. Worst signed strobe skew improves from +5.4050 to −1.8131 ps against ±3.6633 ps. The largest TI data-to-strobe mismatch is 0.3143 mm against 0.6350 mm. Total barrel depth remains 2.8400 mm. The two-via joint window is 22.3342–22.9981 mm.
- **D3 fails.** Its planar length changes from 22.5348 to 25.9353 mm and estimated flight from 167.4912 to 187.1085 ps. Four L1–L4 transitions contribute 5.6800 mm of barrel. Worst signed skew increases from +34.5421 to +54.1593 ps, exceeding the model limit by 50.4960 ps. Its strobe mismatch exceeds the TI limit by 4.9682 mm. The current four-transition geometry has no simultaneous length and delay window. At two full-depth transitions the target becomes 19.7115–20.4313 mm for the present strobes.
- **Byte 1 remains incomplete.** D8, D9, D12, D13, D14, D15 and DQM1 pass their local strobe and delay screens. DQS1 and DQSn1 pass the 0.127 mm pair screen. D10 and D11 remain open, so all-peer matching is unresolved.
- **Byte 0 remains incomplete.** D0, D6 and DQM0 pass their local strobe and delay screens. DQS0 and DQSn0 pass the pair screen. D2, D3, D4, D5 and D7 fail at least one local gate. D1 remains open.

The placed-stack flight model uses 1.420 mm per L1–L4 transition. Material tolerance, actual plating and waveform timing remain unverified. The per-net file uses the complete handheld reference for its prior columns. [All signal lengths, via counts, flight estimates, signed skew, targets and residuals](d3-d15-timing.csv)

The independent plated-drill and four-layer Gerber check found 45 distinct DDR links and 39 split mapped nets. A10, A14, D1, D10 and D11 remain open. The 0.102 mm copper, 0.1524 mm via-edge, drill, self-contact, local return, full-width reference and common-envelope checks passed. Both inner layers had 0.000000003 mm² residual outside nominal antipads across the 369.9218 mm² envelope. MMC0 and both DDR power feeds retained their verified connections. The trial stays separate because of the D3 timing regression. [Drilled CAM and whole-board physical land report](d3-d15-cam.txt)

### Two-transition D7 with shorter D5

The new D7 escape uses two L1–L4 transitions in place of four. Its total barrel depth falls from 5.6800 to 2.8400 mm. Planar length falls from 23.2222 to 22.6639 mm and estimated flight from 171.4567 to 149.4922 ps. Worst signed skew improves from +38.5076 to +16.5431 ps. It still exceeds the model limit by 12.8797 ps. TI data-to-strobe mismatch is 2.3319 mm against 0.6350 mm. The current two-transition joint window is 19.7115–20.4313 mm.

D5 improves from 26.3833 to 25.7789 mm with two L1–L4 transitions, 2.8400 mm barrel depth and 167.4622 ps flight. Worst signed skew falls from +38.0002 to +34.5131 ps, leaving 30.8498 ps excess. TI data-to-strobe mismatch is 5.4468 mm against 0.6350 mm. D15 retains its local pass. D3 retains its timing regression. The Gerber and drill audit found 45 distinct DDR links, 1,077 plated barrels, zero mapped shorts, both physical DDR power paths and the sequenced MMC0 network. Full-width DDR references, the 0.102 mm copper and 6 mil via-edge screens, drill spacing, local returns and common envelope passed. [Per-net timing, targets and residuals](d5-d7-timing.csv) · [Whole-board drilled connectivity](d5-d7-cam.txt)
