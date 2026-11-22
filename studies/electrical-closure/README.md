# Physical DDR reconciliation

Gerbers and plated drills were exported again from the archived native boards at e503b63 and e4c906f. The same CAM reader resolved the 50 CPU and DRAM terminal pairs on both. All 50 logical names map to identical balls in both designs. [All land pairs and physical results](physical-ddr-links.csv)

At e503b63 there were 33 distinct routed pairs and 1,046 plated barrels. At e4c906f there were 36 distinct routed pairs and 1,086 plated barrels. A0 (U1.F3 to U_DDR.N3) and A10 (U1.F4 to U_DDR.L7) lost connectivity at 7c574ec, which removed their geometry from inner-routes.json and routes.json. CK, CKn, CKE, A9 and A14 gained connectivity between the two exported boards. The net gain is three. Each export passed the mapped-land shorts and distinct-pair tests.

The trial build verifies the complete copper objects and physical pin mappings for the 22 byte nets and both clock conductors against the e4c906f fingerprints. This includes all 48 plated transitions.
