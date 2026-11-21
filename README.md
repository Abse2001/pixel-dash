# Pixel Dash

AM3354 handheld with a 1 GiB Micron DDR3L, four-layer HDI board and the existing LiPo tub. Engineering development only.

The retained handheld was extracted from checkpoint `5b7d96d`. The coupled DDR channel starts at `611f7d9`. The original dual-RP2350 hardware and historical routing branches are separate fallbacks.

The first production checkpoint removes 91 old processor and support designators. The peripheral snapshot omits ground pours pending integration. Nine local trace edits eliminate the nine 6 mil via-to-unrelated-trace findings on this retained subset. Future work on the integrated board must rerun the audit including the AM3354 and memory.

`python production/build_retained.py /tmp/retained.circuit.json` materializes the retained copper. Run `python checks/audit-via-clearance.py /tmp/retained.circuit.json` with Shapely 2.

## Integrated engineering build

Install Bun and Python with Shapely 2. Run `bun install --frozen-lockfile` and `bun run build`. The production design entry is `dist/index.circuit.json`. The build renders the editable processor/memory circuit and combines it with the retained handheld. It keeps the LiPo enclosure, board notch and three NTC cutouts. Legacy ground pours require regeneration with finished system routing. The imported DDR L2 ground is limited to the DDR region.

The original integrated checkpoint has 46 source-level links for the panel, controls, MMC0, USB0, PWM audio and backlight. Their PCB copper is outstanding. The ILI9488 selects 16-bit DBI Type B on IM2:0 = 010. Firmware must select this mode before panel reset release. LCDC LIDD uses the 16 data pins, PCLK for RD, HSYNC for WR and VSYNC for D/C. Panel CS is strapped low. The SYSBOOT resistor network, read-strobe pull-up and the behavior of the panel during strap sampling still require integration. [ILI9488 Table 1](https://www.displayfuture.com/Display/datasheet/controller/ILI9488.pdf) · [TI AM335x TRM, Table 13-2 and Chapter 26](https://www.ti.com/lit/ug/spruh73q/spruh73q.pdf)

The first combined export passed the all-layer Gerber shorts check. The BOM and pick-and-place each contain 183 designators. Run `python checks/check-removed-parts.py dist/index.circuit.json engineering.zip` to verify removed-part identities and placement absence. Of the 50 DDR links, 39 have copper. The independent whole-board 6 mil audit finds 87 DDR findings. The build's absence of a native skew message does not certify timing. Use the independent length audit. Assembly rotations, full power and peripheral circuitry, routing, plane returns and fabrication signoff remain open.

The next copper checkpoint removes 40 DDR via-edge clearance findings with local trace edits. The combined audit now lists 47 findings. The CAD checks on the revised channel report the same 11 missing signals, their corresponding opens, and two byte-skew errors. All three VREF bypass paths pass the copper connectivity audit. See `checks/current-clearance.csv` and `checks/current-timing.txt`.

The production source now includes sixteen 10 kΩ SYSBOOT straps. Five pull up to the planned sequenced 3.3 V I/O domain and eleven pull down to ground. Each sense terminal shares its corresponding LCD data signal. The pin-level check decodes 0x4017 from the built netlist. The 24 MHz clock source, sequenced rail, power-on reset and physical strap routing still need verification. Run `python checks/check-sysboot.py dist/index.circuit.json`. [TI boot configuration, Table 26-7](https://www.ti.com/lit/ug/spruh73q/spruh73q.pdf)
