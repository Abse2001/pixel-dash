# Pixel Dash paired data breakout

## Populated handheld checkpoint

The compressed native circuit is a saved copy of the populated board after integration. Decompress it to a file ending in `.circuit.json` to open it in the PCB viewer. [Populated circuit](populated-handheld.circuit.json.gz) · [Top view](populated-handheld.png) · [Both byte lanes in detail](pcb-data-routing.png)

The populated layout moves eight parts around the locked routes: R_VTP, R_VREF_CA, R_VREF_HIGH, R_VREF_LOW, C_CPU_VREF, C_VREF_DQ, C_DDR6 and C_DDR33. All 236 placed courtyards clear one another. The default build rejects any change to the protected ball mapping, trace widths, ordered segment coordinates, via locations, drill or layer spans. The native geometry fingerprints use millimetres rounded to nine decimal places. The populated timing report reproduces every value in the breakout report.

Fifty conflicting copper objects outside the protected data routes were deferred. All parts and logical connections are retained. The 28 DDR clock, address, command and reset connections remain open on this branch. Fabrication remains on hold. [Deferred copper inventory](populated-deferred.csv) · [Per-signal timing](breakout-timing.csv) · [Verification record](populated-verification.txt)

## Saved breakout

The two bytes run together between the AM3354 and the rotated Micron x16. The RAM center is at (−65.00, 11.55) mm. The RAM pin remap exchanges only data bits within their original byte. All 22 data, mask and strobe conductors use two 1.420 mm layer 1–4 transitions on the 1.491 mm reference stack.

On the native breakout, 22/22 pass the TI data/mask matching limit of 0.635 mm and the applicable strobe pair matching limit of 0.127 mm. The worst modeled data skews are +2.957 ps on D4 and +2.878 ps on DQM1, against ±3.663 ps. Placement-derived project ceilings are 19.400 and 20.200 mm on this mapping. The per-signal report compares against the complete bf75444 fallback, including lengths, via spans, modeled flights and signed residuals. Signal flight is estimated from the reference stack. These measurements qualify route geometry only.

Reproduce the component-level check with bun studies/data-bytes/render-breakout.tsx /tmp/breakout.json followed by PYTHONPATH=checks python studies/data-bytes/check-lanes.py BASELINE_JSON /tmp/breakout.json. Use the complete bf75444 handheld build as BASELINE_JSON. The breakout rendering contains the two populated footprints. The separate full-handheld source retains the surrounding parts, including the 28 other DDR schematic nets requiring rerouting after the RAM move.

The independent copper walk on the breakout Gerbers found 22 distinct CPU-to-RAM networks, including all 44 plated through barrels, with zero shorts between mapped lands. The 0.102 mm copper gap, 0.1524 mm via-edge gap and drill-spacing checks each returned zero findings. These results cover the two populated BGA footprints. Export the rendered .circuit.json and run checks/audit-cam-connectivity.py with the JSON, Gerber ZIP and --byte-lanes-only to repeat the drilled connectivity check.
