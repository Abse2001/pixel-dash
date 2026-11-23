# Isolated 90° RAM placement and two-transition breakouts

The powered 45-link layout remains at d8461d7. The compressed circuit in this directory is an experimental assembled board with eight routed signals and 42 open DDR links. Decompress it with `gzip -dc byte0-study.circuit.json.gz > board.circuit.json`. The copper in this study does not qualify for adoption.

## Why test another orientation?

The minimum possible common DDR envelope contains the convex hull of the AM3354 DDR signal lands and the DRAM footprint lands, even with every signal trace removed. At the original placement, the center of SYSBOOT0 (U1.R1) is 0.153566 mm outside this hull. Its 0.180 mm land radius limits the farthest usable point to 0.333566 mm. The required separation of unrelated routing from the DDR envelope is 0.408 mm. Even an infinitesimal trace touching the far edge would miss by at least 0.074434 mm. Widening the trace or adding DDR copper cannot improve that bound.

Rotating the RAM +90° at its existing center (−65.00, 15.15 mm) increases the R1 center distance to 0.620100 mm. This clears the necessary placement screen with 0.212100 mm at the center. It does not prove a routed SYSBOOT0 strap. The study rotates the RAM's local termination, bypass and blind-via structures with the package and extends the L3 DDR reference west to cover them.

## Physical results

The drilled export resolves all eight remapped lower-byte data lands as distinct CPU–RAM connections. Each uses two L1–L4 transitions. The data traces pass the full-width reference check. The mapped connectivity audit checks 999 plated barrels and finds zero shorts. N5/P5, all 21 DCDC4 CPU lands, seven switched CPU DDR lands, 18 direct DDR supply lands, VTP, VREF and MMC0 remain physically connected. Copper, via-edge and drill checks pass.

Two independent gates reject this geometry. N5 copper has 0.011965 mm² in the 0.408 mm envelope margin. A signal antipad cuts into the required L3 reference land at C_DDR6 pin 1. DQS0 and CK are open, so the signed strobe skew, TI data matching and receiver timing cannot be evaluated. The original 45-link layout's 19.7115–20.4313 mm joint window cannot qualify this rotated placement.

[Eight physical routes and lengths](byte0-escape.csv) · [Exact drilled CAM](byte0-drilled-cam.txt) · [Envelope finding](byte0-envelope.csv) · [Assembled study](byte0-study.circuit.json.gz)

## Breakout with power and return clearances reserved

A second export removes both findings above. Its legal routing area includes the existing CPU-to-RAM VREF track, protects the full blind-via reference lands from new antipads and reserves the 0.408 mm envelope clearance to N5. All eight lower-byte data signals connect with two full-depth transitions each. All 71 return terminals pass. Full-width reference, envelope, copper, 6 mil via-edge, drill and class spacing pass. The longest cumulative run below nominal class spacing is 2.707 mm on D2, within the 31.750 mm allowance. The byte strobes, masks, clock and command group still need routes. This study does not supersede the powered 45-link board.

[Verified eight-link study](reserved-power-and-returns/byte0.circuit.json.gz) · [Prior and current lengths, flight estimates and limits](reserved-power-and-returns/lengths-and-delay.csv) · [Drilled CAM](reserved-power-and-returns/drilled-cam.txt) · [Geometry checks](reserved-power-and-returns/geometry-checks.txt)
