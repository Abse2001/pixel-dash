# Powered handheld I/O

The two amplifier control pads previously occupied separate physical nets from each other and from the V3V3_INTERNAL output. Two top-side connections join U_SPK_AMP.MUTE and U_SPK_AMP.SHND to C_3V3_OUT_B. These are the existing logic bias connections in the source design.

The drilled export retains 45 distinct DDR connections and reports 38 split whole-board nets, down from 39. All 21 DCDC4 CPU lands, all seven switched DDR CPU lands, direct DRAM supply, VTP, ZQ, VREF and the sequenced card supply retain their CAM connections. The DDR timing CSV matches e5fd49f byte for byte. No findings in the 0.102 mm copper, 0.1524 mm via-edge, drill spacing, self-contact, full-width DDR/MMC0/raster references, local DDR return or common-envelope checks. Startup and DDR timing remain open. [Physical land report](amp-logic-cam.txt)

## SYSBOOT10 and panel backlight control

U1.U3 now reaches R_SYSBOOT10.pin2 and the existing LCD_D10 panel copper. The bias is physically low and the sense net is isolated from the supply planes. U1.C18 reaches the backlight MOSFET gate through R_LCD_BL_PULLDOWN.pin1 on the same physical net. The chosen PWM path avoids an L2 segment that disconnected the A18 local return in a rejected trial. This verifies copper continuity; boot sampling, PWM operation and panel operation require first-article measurements.

Drilled CAM reports 36 split mapped nets, 45 distinct DDR links and no shorts between mapped lands. All 71 local DDR return terminals are covered by the connected plane, including A18. DDR timing is byte-for-byte identical to e5fd49f. There are zero copper, via-edge, drill, self-contact, DDR/MMC0/raster full-width reference and envelope findings. The 21 DCDC4 lands, seven switched supply balls, direct DRAM rail, both calibration resistors and sequenced MMC0 retain their physical connections. [Drilled CAM land report](sysboot10-backlight-cam.txt)

## SYSBOOT12 CPU tap

Drilled CAM joins U1.V2 to R_SYSBOOT12.pin2 and confirms isolated low bias. The panel-side LCD D12 FPC contact remains on a separate island. Six of the sixteen strap states are now physically resolved. This checkpoint retains the preceding SYSBOOT10 and PWM connections, all 45 distinct DDR links, the same timing CSV, full-width DDR/MMC0/raster reference and all 71 local return terminals. Copper, via-edge, drill, self-contact and envelope checks pass. [Exact land memberships and boot word](sysboot12-cam.txt)

## SYSBOOT7 CPU tap

U1.T4 now reaches R_SYSBOOT7.pin2. Drilled CAM confirms an isolated low strap and seven resolved strap states. The remaining panel-side LCD D7 land is listed in the physical report. The exported board retains the same 45 DDR links and timing, powered N5/P5, calibration and all 71 reference terminals. Full-width DDR, MMC0 and raster coverage pass, as do copper, drill, via-edge, self-contact and common-envelope checks. [Exact boot straps and physical land groups](sysboot7-cam.txt)

## Touch IRQ on the powered 45-link orientation

The exported copper connects U1.V14 to R_TOUCH_IRQ.pin1, and the resistor bias joins the sequenced 3.3 V rail. The IRQ route from the rotated study clears the powered board's SYSBOOT10 and SYSBOOT12 traces. Reusing the IRQ from 4b3d1c5 instead crossed both traces on L3. The verified export has 35 split mapped nets, previously 36. All mapped ground lands and barrels still join the UART ground probe. The IRQ connection alone does not qualify the touch panel.

The previous 45 DDR links, full timing CSV, N5/P5, VTP, MMC0 and 71 DDR local return terminals remain intact. All full-width reference, class spacing, drill, 0.102 mm copper and separate 6 mil via-edge checks pass on this partial DDR design. [Drilled endpoint audit](touch-irq-powered-cam.txt) · [Geometry and regression checks](touch-irq-powered-checks.txt)

## Panel-side LCD D4 connection

R_SYSBOOT4 pin 2 now reaches the panel's LCD D4 contact. The number of panel data contacts connected to their strap sense nodes is 11/16. The CPU land for this bit is still on its own island. Seven strap levels reach the CPU and 35 mapped board nets remain split. All 45 DDR links, the timing CSV, powered lands, 71 local DDR returns, handheld ground, and sequenced MMC0 remain intact. Full-width raster and DDR references, class and copper spacing, and separate drill and via-edge checks pass. [Drilled endpoints](panel-tap-4-cam.txt) · [Physical gates](panel-tap-4-geometry.txt)

## Panel-side LCD D3 connection

R_SYSBOOT3 pin 2 now reaches the panel's LCD D3 contact. The number of panel data contacts connected to their strap sense nodes is 12/16. The CPU land for this bit is still on its own island. Seven strap levels reach the CPU and 35 mapped board nets remain split. All 45 DDR links, the timing CSV, powered lands, 71 local DDR returns, handheld ground, and sequenced MMC0 remain intact. Full-width raster and DDR references, class and copper spacing, and separate drill and via-edge checks pass. [Drilled endpoints](panel-tap-3-cam.txt) · [Physical gates](panel-tap-3-geometry.txt)
