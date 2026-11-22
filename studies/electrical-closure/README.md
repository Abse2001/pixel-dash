# Physical DDR reconciliation

Gerbers and plated drills were exported again from the archived native boards at e503b63 and e4c906f. The same CAM reader resolved the 50 CPU and DRAM terminal pairs on both. All 50 logical names map to identical balls in both designs. [All land pairs and physical results](physical-ddr-links.csv)

At e503b63 there were 33 distinct routed pairs and 1,046 plated barrels. At e4c906f there were 36 distinct routed pairs and 1,086 plated barrels. A0 (U1.F3 to U_DDR.N3) and A10 (U1.F4 to U_DDR.L7) lost connectivity at 7c574ec, which removed their geometry from inner-routes.json and routes.json. CK, CKn, CKE, A9 and A14 gained connectivity between the two exported boards. The net gain is three. Each export passed the mapped-land shorts and distinct-pair tests.

The trial build verifies the complete copper objects and physical pin mappings for the 22 byte nets and both clock conductors against the e4c906f fingerprints. This includes all 48 plated transitions.

## N5 and P5 on DCDC4

Two 0.18 mm L1 traces join U1.N5 to P5 and P5 to the live DCDC4 land at P6. A local clearance cut in the top switched-DDR pour accommodates the new path. Exported copper and plating prove 21/21 DCDC4 CPU lands, 7/7 separate CPU DDR supply lands and 18/18 direct DRAM supply lands. All 36 existing DDR links pass the full-width reference and distinct-pair audits. The 0.102 mm copper, 0.1524 mm via edge, drill spacing, per-layer strokes, self-contact, MMC0 and byte matching checks pass. The locked clocks and bytes match e4c906f. Whole-board CAM finds 44 split nets and zero mapped-land shorts. [Exported power and strap checks](physical-power-and-straps.txt)

The local L1 sheet comparison uses the exported top copper minus the plated bores, 30 µm foil and 20 °C copper. All seven DDR lands still share the feed. With 0.016 mm mesh and 0.23 mm terminal diameters, the worst driving-point resistance from the existing DDR feed via to E5 changes from 6.782 to 6.806 mΩ. At 0.025 mm pitch it changes from 6.901 to 6.906 mΩ. This is a local spreading-resistance estimate. Rail dynamics and regulator margin still require separate qualification.

## J3 calibration resistor

The existing R_VTP now sits at the reverse-side exit of the J3 through via. The 0.102 mm CPU-side trace threads between the frozen byte traces. The bottom trace reaches pin 1 and pin 2 connects to an existing ground barrel. The relocated pads have their own clearance in the switched DDR supply pour. CAM independently resolves the J3 and resistor lands, proves the grounded return and verifies isolation of the sense terminal from power and ground. The 236 placed courtyards have no overlaps. At this checkpoint there are 1,087 plated barrels, 36 distinct DDR signals and 43 board-wide split nets. The physical route enables first-article testing of the AM3354 VTP calibration sequence.

## SYSBOOT8 and the populated return-path screen

CPU U1.U1 now reaches the low-bias resistor R_SYSBOOT8 and the existing LCD D8 connection. Seven physical reset straps pass (0, 8, 11, 12, 13, 14, 15). The new export has 1,093 plated barrels and 42 board-wide split nets. Full-width DDR references, the two clearance thresholds, drill spacing, locked clocks and bytes, command timing comparison, RTC and MMC0 copper checks retain the preceding results. LCD receiver timing and the sampled strap during cold boot remain unqualified.

The previous L2 sheet solver clipped the ground path between the CPU and PMIC at the edge of its local rectangle. The solver now expands that rectangle until both terminals lie on one connected exported region. On this artwork the 0.05 mm mesh gives 4.983 mΩ for the three-via return at 20 °C. The load-switch screen at 105 °C, 80% effective conductor area and 40 mΩ switch corner gives 15.828 mV DC headroom and 4.928 mV after the modeled transient. Component and copper tolerances, source and load step response and hardware operation remain unverified. [CAM sheet solve](bit8-ddr-sheet.txt) · [Voltage assumptions and sensitivities](bit8-ddr-voltage.txt)

## SYSBOOT9

Exported copper joins CPU U2, the low-bias SYSBOOT9 resistor and raster D9. Eight of sixteen physical straps pass (0, 8, 9, 11, 12, 13, 14, 15). Independent CAM finds 36 distinct DDR pairs, 1,096 plated barrels, 41 split design nets and zero shorts between mapped lands. The 24 locked routes and their 48 vias match the e4c906f fingerprints. Copper, via-edge, drill, full-width reference, DDR byte and clock matching, CPU I/O power and MMC0 checks retain their passing results. The populated-board snapshot and compressed circuit describe this export.

At the SYSBOOT9 checkpoint the three-via PMIC return measures 4.988 mΩ in the 20 °C sheet model. At the 105 °C, 80% conductor-area and 40 mΩ switch corner the estimated DC reserve is 15.826 mV and the dynamic reserve is 4.926 mV. [Sheet calculation](sysboot9-ddr-sheet.txt) · [Voltage calculation](sysboot9-ddr-voltage.txt)

The raster reference screen now follows the electrical net through strap taps that have separate source trace IDs. For support copper stored as separate wire sections it recognizes a launch only at the exact center of a same-net via spanning the reference layer and having trace endpoints on at least two of its drilled layers. The populated SYSBOOT9 export has 25 raster trace/layer findings on 13 routed raster signals. The DDR full-width screen is independent. [Raster findings](sysboot9-raster-reference.txt) · [DDR command lengths, transitions, flight and signed skew to CK](command-timing.csv)

In an unadopted breakout trial, removing A6/A7/A8 opened an A10 path at 27.43544 mm with two layer transitions, 199.866 ps estimated flight and −36.604 ps skew to CK. That path is 8.71455 mm below the 36.14999–38.68999 mm project window. Restoring A6 and A7 consumed the A8 launch region. Releasing only A6 yielded no continuous legal A0 or A10 corridor in the searched region. The accepted layout retains A6/A7/A8 and continues to count A0/A10 as open.

## Raster D12 on the populated board

CPU V2 and R_SYSBOOT12 now reach J_LCD pin 15 in exported copper. Eleven of sixteen panel data pins reach their strap sense pads, eight straps reach the CPU, and 40 design nets still span multiple CAM islands. The independent raster audit gives exactly the same 25 findings as the SYSBOOT9 parent, including the two inherited D12 findings. The added D12 branch has full-width reference after correcting its top-layer approach to the buried section. DDR, clock, MMC0, copper clearance and drill checks pass on the same archive; 36 DDR pairs and 1,102 plated barrels are present. [Sheet calculation](panel12-ddr-sheet.txt) · [Hot-load voltage screen](panel12-ddr-voltage.txt)

A direct replay of the negotiated A10 path alongside all accepted routes found no new trace or via spacing conflict in the copper geometry. It would sever 40.820853 mm² from the L3 DDR supply pour. The plane-fill check rejected the candidate before export.

## Raster D3 strap branch

Panel pin 29 reaches R_SYSBOOT3 pin 2 through eight plated transitions. The thirteen-transition trial was discarded. The CPU R4 land still needs its own escape. Twelve panel data pins now reach the corresponding strap sense pad and eight strap bits reach the CPU. All 25 inherited full-width raster reference findings reproduce to the reported area on the new export. The added D3 branch has no uncovered copper. Full-width DDR return, clock and byte matching, physical power, MMC0, 0.102 mm copper, drill and separate 0.1524 mm via-edge screens pass. The new board has 1,110 plated barrels, 36 distinct DDR signals, 40 split logical nets and zero shorts between mapped lands. [Current physical nets](physical-power-and-straps.txt) · [Raster reference](panel3-raster-reference.txt) · [Drilled power network](panel3-ddr-sheet.txt) · [Hot-load screen](panel3-ddr-voltage.txt)
