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
connectivity and DDR timing gates remain open. B4 and twelve SYSBOOT
straps remain open. See the explicitly deferred nets, endpoint report
and incomplete timing screen in this directory.
