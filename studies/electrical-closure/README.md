# Physical DDR reconciliation

Gerbers and plated drills were exported again from the archived native boards at e503b63 and e4c906f. The same CAM reader resolved the 50 CPU and DRAM terminal pairs on both. All 50 logical names map to identical balls in both designs. [All land pairs and physical results](physical-ddr-links.csv)

At e503b63 there were 33 distinct routed pairs and 1,046 plated barrels. At e4c906f there were 36 distinct routed pairs and 1,086 plated barrels. A0 (U1.F3 to U_DDR.N3) and A10 (U1.F4 to U_DDR.L7) lost connectivity at 7c574ec, which removed their geometry from inner-routes.json and routes.json. CK, CKn, CKE, A9 and A14 gained connectivity between the two exported boards. The net gain is three. Each export passed the mapped-land shorts and distinct-pair tests.

The trial build verifies the complete copper objects and physical pin mappings for the 22 byte nets and both clock conductors against the e4c906f fingerprints. This includes all 48 plated transitions.

## N5 and P5 on DCDC4

Two 0.18 mm L1 traces join U1.N5 to P5 and P5 to the live DCDC4 land at P6. A local clearance cut in the top switched-DDR pour accommodates the new path. Exported copper and plating prove 21/21 DCDC4 CPU lands, 7/7 separate CPU DDR supply lands and 18/18 direct DRAM supply lands. All 36 existing DDR links pass the full-width reference and distinct-pair audits. The 0.102 mm copper, 0.1524 mm via edge, drill spacing, per-layer strokes, self-contact, MMC0 and byte matching checks pass. The locked clocks and bytes match e4c906f. Whole-board CAM finds 44 split nets and zero mapped-land shorts. [Exported power and strap checks](physical-power-and-straps.txt)

The local L1 sheet comparison uses the exported top copper minus the plated bores, 30 µm foil and 20 °C copper. All seven DDR lands still share the feed. With 0.016 mm mesh and 0.23 mm terminal diameters, the worst driving-point resistance from the existing DDR feed via to E5 changes from 6.782 to 6.806 mΩ. At 0.025 mm pitch it changes from 6.901 to 6.906 mΩ. This is a local spreading-resistance estimate. Rail dynamics and regulator margin still require separate qualification.

## J3 calibration resistor

The existing R_VTP now sits at the reverse-side exit of the J3 through via. The 0.102 mm CPU-side trace threads between the frozen byte traces. The bottom trace reaches pin 1 and pin 2 connects to an existing ground barrel. The relocated pads have their own clearance in the switched DDR supply pour. CAM independently resolves the J3 and resistor lands, proves the grounded return and verifies isolation of the sense terminal from power and ground. The 236 placed courtyards have no overlaps. At this checkpoint there are 1,087 plated barrels, 36 distinct DDR signals and 43 board-wide split nets. The physical route enables first-article testing of the AM3354 VTP calibration sequence.
