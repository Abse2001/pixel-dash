# Powered byte-1 breakout

This study keeps the N5/P5 feeds, moves the VTP resistor ground return to a local plated barrel, and jointly reallocates D12 and D14. The complete 50-signal handheld remains available at 4b3d1c5. The repoured 46-signal power fallback is ff755ca.

| Net | Prior → current length (mm) | Barrel span | Estimated flight (ps) | Worst signed DQS skew, prior → current (ps) | Largest planar DQS mismatch (mm) |
|---|---:|---|---:|---:|---:|
| D12 | 23.6978 → 22.6622 | 2 × L1–L4, 2.840 mm total | 149.4821 | +7.6998 → −1.7710 | 0.3070 |
| D14 | 23.3728 → 22.5901 | 2 × L1–L4, 2.840 mm total | 149.0665 | +5.8252 → −2.1866 | 0.3790 |

The TI data-to-strobe matching limit is 0.635 mm. The project model screens the two strobe legs across isolated, mixed and odd-mode delay at ±3.6633 ps. Both nets have zero excess on these gates and fall inside the current two-through-via joint window of 22.3342–22.9981 mm. The separate 22.9998 mm ceiling is placement-derived. Model uncertainty includes the actual manufactured stack and waveform. The TI all-DQ peer gate of 0.635 mm requires a complete byte.

Drilled export verifies 43/50 distinct DDR links, no mapped shorts, 21/21 DCDC4 lands, 7/7 switched CPU DDR lands, J3/VTP and ZQ calibration, VREF divider and returns, local returns and sequenced MMC0. Both inner-plane residuals outside nominal antipads are below 0.000001 mm². Full-width DDR, MMC0 and routed raster references pass. The 0.102 mm copper, 6 mil via-edge, drill-spacing and nonlocal self-contact checks have zero findings. Seven DDR nets and 41 whole-board physical nets remain open. [Per-net timing and open signals](pair-first-timing.csv) · [Drilled land report](pair-first-cam.txt)
