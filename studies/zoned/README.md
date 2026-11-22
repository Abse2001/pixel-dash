# Zoned CPU escape study

Starting at e6b5c4c, reserve the power and reset routes, ground returns and
fixed-package DDR region before admitting outer-layer DDR tracks. Keep
this partial build on the study branch. The production branch still
carries all 50 DDR links. Build with the normal `bun run build` entry point.

The first pass admitted 39 original DDR routes outside the four boot
corridors. The L2 slots disconnected the returns of C_DDR23 and C_DDR29.
Two L4 ground traces now join those pads to nearby verified ground pads.
The next pass routes BA2 on five sections with four plated traversals.
The originating package lands, old vias and replacement vias are checked
during assembly. Interior voids from lifted vias are refilled while
retaining relief for active copper and new plated holes.

The drilled export verifies 40/50 DDR links, B5 to PGOOD_BU, C5 to
nWAKEUP and 21/21 DCDC4 CPU/USB supply lands including N5 and P5.
All ground lands reach the ground probe. No unrelated copper falls
below 0.102 mm or the separate 0.1524 mm via-edge rule. Drill spacing,
Gerber shorts, all routed DDR full-width references, the DDR envelope,
six raster and seven MMC0 full-width references pass. The full-board
connectivity and DDR timing gates remain open. B4 now joins D7/DCDC6 and remains isolated from D6/DCDC5. Reset, wake,
power hold and both RTC returns pass the drilled export. SYSBOOT7, 10 and
12 now reach their sense resistors. Seven of sixteen straps are physical.
The C_DDR23 to C_DDR13 ground link keeps the capacitor island on the main
return. See the explicitly deferred nets, endpoint report
and incomplete timing screen in this directory.


With all movable DDR signal copper removed analytically, the fixed lands
alone leave only 0.3336 mm at the farthest point on R1 versus the required
0.408 mm DDR envelope setback. The farthest point on R2 has 0.0763 mm of
excess. Moving the RAM 1 mm in +Y in the placement calculation leaves
0.1188 mm of excess at R1 and 0.2083 mm at R2. These are upper bounds
before routing. The saved board still has the original RAM placement.
See [fixed-land placement bounds](fixed-land-bounds.csv).
