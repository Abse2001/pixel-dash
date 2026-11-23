# Powered handheld I/O

The two amplifier control pads previously occupied separate physical nets from each other and from the V3V3_INTERNAL output. Two top-side connections join U_SPK_AMP.MUTE and U_SPK_AMP.SHND to C_3V3_OUT_B. These are the existing logic bias connections in the source design.

The drilled export retains 45 distinct DDR connections and reports 38 split whole-board nets, down from 39. All 21 DCDC4 CPU lands, all seven switched DDR CPU lands, direct DRAM supply, VTP, ZQ, VREF and the sequenced card supply retain their CAM connections. The DDR timing CSV matches e5fd49f byte for byte. No findings in the 0.102 mm copper, 0.1524 mm via-edge, drill spacing, self-contact, full-width DDR/MMC0/raster references, local DDR return or common-envelope checks. Startup and DDR timing remain open. [Physical land report](amp-logic-cam.txt)
