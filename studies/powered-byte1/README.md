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
