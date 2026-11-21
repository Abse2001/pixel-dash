# Pixel Dash

## Wide handheld checkpoint

This branch builds a **232 × 82 mm single four-layer PCB** for the wider handheld. The d-pad, face buttons, shoulders and joystick connectors moved into the fixed side grips. Start and Select sit below the main controls. Nine modeled controls clear the centered 164.9 × 100.0 mm bare BuyDisplay ER-TFT070A2-6 panel envelope in plan view. The full display assembly, cover lens, bezel, FPC bend and replacement rear shell still require integration. The native display circuit still describes the earlier panel. The 7-inch panel needs an RGB raster interface and a constant-current backlight driver.

The placement pass removes 20 displaced control traces and records each as an open. DDR copper and component centers stay fixed. The all-layer Gerber shorts check passes and the placement-stage via clearance count was 25. The smaller case, battery tub and running design history are preserved on [am3354-production](https://github.com/Abse2001/pixel-dash/tree/am3354-production). No fabrication release has been made.

The DDR address-reference route now clears four more vias at its original 0.4 mm width. Moving the C_DDR34 bulk bypass 0.10 mm clears the adjacent D12 trace. A four-via chip-select route brings the DDR channel to 40 of 50 signals connected. The integrated 6 mil audit lists 20 remaining findings. The VREF bypass and all-layer Gerber shorts checks pass.

The [runtime budget](power/runtime-budget.md) sizes candidate packs at 75% backlight PWM. The keyed PCB battery header uses contact 1 for BAT and 2 for GND. A battery-specific mating check is required once a supplier is selected. [BuyDisplay panel](https://www.buydisplay.com/7-inch-1024x600-ips-tft-lcd-display-high-brightness-full-viewing-angle)

## Earlier compact design checkpoints


AM3354 handheld with a 1 GiB Micron DDR3L, four-layer HDI board and the existing LiPo tub. Engineering development only.

The retained handheld was extracted from checkpoint `5b7d96d`. The coupled DDR channel starts at `611f7d9`. The original dual-RP2350 hardware and historical routing branches are separate fallbacks.

The first production checkpoint removes 91 old processor and support designators. The peripheral snapshot omits ground pours pending integration. Nine local trace edits eliminate the nine 6 mil via-to-unrelated-trace findings on this retained subset. Future work on the integrated board must rerun the audit including the AM3354 and memory.

`python production/build_retained.py /tmp/retained.circuit.json` materializes the retained copper. Run `python checks/audit-via-clearance.py /tmp/retained.circuit.json` with Shapely 2.

## Integrated engineering build

Install Bun and Python with Shapely 2. Run `bun install --frozen-lockfile` and `bun run build`. The production design entry is `dist/index.circuit.json`. The build renders the editable processor/memory circuit and combines it with the retained handheld. It keeps the LiPo enclosure, board notch and three NTC cutouts. Legacy ground pours require regeneration with finished system routing. The imported DDR L2 ground is limited to the DDR region.

The original integrated checkpoint has 46 source-level links for the panel, controls, MMC0, USB0, PWM audio and backlight. Their PCB copper is outstanding. The ILI9488 selects 16-bit DBI Type B on IM2:0 = 010. Firmware must select this mode before panel reset release. LCDC LIDD uses the 16 data pins, PCLK for RD, HSYNC for WR and VSYNC for D/C. Panel CS is strapped low. The SYSBOOT resistor network, read-strobe pull-up and the behavior of the panel during strap sampling still require integration. [ILI9488 Table 1](https://www.displayfuture.com/Display/datasheet/controller/ILI9488.pdf) · [TI AM335x TRM, Table 13-6 and Chapter 26](https://www.ti.com/lit/ug/spruh73q/spruh73q.pdf)

The first combined export passed the all-layer Gerber shorts check. The BOM and pick-and-place each contain 183 designators. Run `python checks/check-removed-parts.py dist/index.circuit.json engineering.zip` to verify removed-part identities and placement absence. Of the 50 DDR links, 39 have copper. The independent whole-board 6 mil audit finds 87 DDR findings. The build's absence of a native skew message does not certify timing. Use the independent length audit. Assembly rotations, full power and peripheral circuitry, routing, plane returns and fabrication signoff remain open.

The next copper checkpoint removes 40 DDR via-edge clearance findings with local trace edits. The combined audit now lists 47 findings. The CAD checks on the revised channel report the same 11 missing signals, their corresponding opens, and two byte-skew errors. All three VREF bypass paths pass the copper connectivity audit. See `checks/current-clearance.csv` and `checks/current-timing.txt`.

The production source now includes sixteen 10 kΩ SYSBOOT straps. Five pull up to the planned sequenced 3.3 V I/O domain and eleven pull down to ground. Each sense terminal shares its corresponding LCD data signal. The pin-level check decodes 0x4017 from the built netlist. The 24 MHz clock source, sequenced rail, power-on reset and physical strap routing still need verification. Run `python checks/check-sysboot.py dist/index.circuit.json`. [TI boot configuration, Table 26-7](https://www.ti.com/lit/ug/spruh73q/spruh73q.pdf)

Moving 14 signal vias within their existing escape routes reduced the combined 6 mil count from 47 to 31. The three coupled pairs retained their original vertices. The independent length audit has the same out-of-window signals and reported skew, the VREF copper check passes, and the integrated Gerber shorts check passes.

The 24 MHz OSC0 uses JLCPCB C439045 with a 12 pF specified load, two provisional 15 pF C0G capacitors, a fitted zero-ohm drive link and an unpopulated 1 MΩ evaluation resistor. All seven signal traces are on top copper. The two case lands, both load capacitors and VSS_OSC each reach L2 ground through a local blind via. Run `python checks/check-oscillator.py dist/index.circuit.json`. The integrated Gerber shorts check passes and the 6 mil audit remains at 31 findings. BOM and placement each contain 203 fitted references. Crystal startup margin, effective load and frequency require prototype measurements. [TI AM335x datasheet, section 6.2.2.1 and Figure 6-9](https://www.ti.com/lit/ds/symlink/am3354.pdf) · [JLCPCB crystal listing](https://jlcpcb.com/partdetail/437836-S3B24000000F1210F30/C439045)

The touch-capable panel connector now maps FPC44 and FPC45 to I2C1 on D15/D16 (mode 3), and FPC46 to GPIO1_17 on V14. The retained three pull-ups share the respective connector nets. microSD mechanical card detect uses C15 in mode 5 and is separate from DAT3. These four connections still require copper. The retained pull-up supply must be reviewed together with processor I/O power sequencing. Run `python checks/check-panel-storage.py dist/index.circuit.json`. [TI AM335x ZCZ pin attributes](https://www.ti.com/lit/ds/symlink/am3354.pdf) · [BuyDisplay FPC assignment](https://www.buydisplay.com/download/manual/ER-TFT035IPS-6_Datasheet.pdf)

## Momentary power control

The integrated board replaces the slide switch and its two battery hard-off gates with the ALPS SKRTLAE010 momentary key (C110293) and the TPS65218D0PHPR (C2659099). The two battery converters retain their input protection, USB interlocks and undervoltage control. The PB contact and its bias branch have saved top copper. The PMIC-to-processor controls are present in the netlist. Regulator filters, power distribution, sequencing, standby current and system connections still need qualification. In particular, the inherited USB supervisor inhibits the battery converters on valid VBUS. Aggregate USB draw requires a power-path review.

The PMIC recognizes a 600 ms press for cold start. During operation firmware can use the PB status interrupt for a shutdown request, flush the microSD and release RTC_PMIC_EN. Holding the button for the PMIC hardware timeout initiates a reset (8 seconds by default, 15 seconds when configured). Firmware and button timing have yet to be tested on hardware. [TI TPS65218D0 sections 5.3.1.15 and 5.4](https://www.ti.com/lit/ds/symlink/tps65218d0.pdf) · [TI AM335x PMIC guide](https://www.ti.com/lit/ug/slvuaa9b/slvuaa9b.pdf)

The separate push cap in `mechanical/power-button.scad` fits through the existing slider slot from inside the case. At the nominal CAD dimensions the cap reaches the supplier's 0.2 mm stroke with 0.25 mm of inward travel. Shell clearance at rest is 0.204 mm. The stroke, return and print tolerances require a physical fit test. Export the SCAD to STL and run `checks/check-power-button-fit.py` with the STL, the C110293 supplier OBJ and the original handheld checkout.

Run `checks/check-power-button.py` against the built circuit. The BOM and placement export contain 202 fitted references. The slide, two slide CAD bodies and five dedicated battery-control components have been added to the retirement inventory. The four-layer JLCPCB geometry remains provisional. Fabrication signoff is on hold pending the actual stackup.

Six DDR ground escapes now end on L2. The CPU H6/H7/G8, RAM D8/E8/T1 and C_DDR12 ground lands reach the solid reference plane, including the shared via for RAM D8/E8. The whole-board 6 mil audit falls from 31 to 25 findings. Signal routes and length measurements are unchanged. The integrated shorts check passes. Run `checks/check-local-ddr-returns.py` on the production circuit and `checks/audit-channel-drills.py` on the same circuit and its Gerber ZIP. The drill audit covers plated and nonplated round holes and all six connector slots, including both endpoints of each G85 command.
