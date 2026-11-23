# Powered handheld I/O

The two amplifier control pads previously occupied separate physical nets from each other and from the V3V3_INTERNAL output. Two top-side connections join U_SPK_AMP.MUTE and U_SPK_AMP.SHND to C_3V3_OUT_B. These are the existing logic bias connections in the source design.

The drilled export retains 45 distinct DDR connections and reports 38 split whole-board nets, down from 39. All 21 DCDC4 CPU lands, all seven switched DDR CPU lands, direct DRAM supply, VTP, ZQ, VREF and the sequenced card supply retain their CAM connections. The DDR timing CSV matches e5fd49f byte for byte. No findings in the 0.102 mm copper, 0.1524 mm via-edge, drill spacing, self-contact, full-width DDR/MMC0/raster references, local DDR return or common-envelope checks. Startup and DDR timing remain open. [Physical land report](amp-logic-cam.txt)

## SYSBOOT10 and panel backlight control

U1.U3 now reaches R_SYSBOOT10.pin2 and the existing LCD_D10 panel copper. The bias is physically low and the sense net is isolated from the supply planes. U1.C18 reaches the backlight MOSFET gate through R_LCD_BL_PULLDOWN.pin1 on the same physical net. The chosen PWM path avoids an L2 segment that disconnected the A18 local return in a rejected trial. This verifies copper continuity; boot sampling, PWM operation and panel operation require first-article measurements.

Drilled CAM reports 36 split mapped nets, 45 distinct DDR links and no shorts between mapped lands. All 71 local DDR return terminals are covered by the connected plane, including A18. DDR timing is byte-for-byte identical to e5fd49f. There are zero copper, via-edge, drill, self-contact, DDR/MMC0/raster full-width reference and envelope findings. The 21 DCDC4 lands, seven switched supply balls, direct DRAM rail, both calibration resistors and sequenced MMC0 retain their physical connections. [Drilled CAM land report](sysboot10-backlight-cam.txt)
