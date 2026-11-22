# Pixel Dash paired data breakout

The two bytes run together between the AM3354 and the rotated Micron x16. The RAM center is at (−65.00, 11.55) mm. The RAM pin remap exchanges only data bits within their original byte. All 22 data, mask and strobe conductors use two 1.420 mm layer 1–4 transitions on the 1.491 mm reference stack.

On the native breakout, 22/22 pass the TI data/mask matching limit of 0.635 mm and the applicable strobe pair matching limit of 0.127 mm. The worst modeled data skews are +2.957 ps on D4 and +2.878 ps on DQM1, against ±3.663 ps. Placement-derived project ceilings are 19.400 and 20.200 mm on this mapping. The per-signal report compares against the complete bf75444 fallback, including lengths, via spans, modeled flights and signed residuals. Signal flight is estimated from the reference stack. These measurements qualify route geometry only.

Reproduce the component-level check with bun studies/data-bytes/render-breakout.tsx /tmp/breakout.json followed by PYTHONPATH=checks python studies/data-bytes/check-lanes.py BASELINE_JSON /tmp/breakout.json. Use the complete bf75444 handheld build as BASELINE_JSON. The breakout rendering contains the two populated footprints. The separate full-handheld source retains the surrounding parts, including the 28 other DDR schematic nets requiring rerouting after the RAM move.
