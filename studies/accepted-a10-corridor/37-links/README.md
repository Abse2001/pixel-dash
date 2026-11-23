# 37-link electrical routing study

Drilled CAM connects every DDR ball pair present on the accepted board plus A10. Both byte groups and both clock legs retain their accepted copper, pin mapping and via fingerprints. The export has 1,123 plated barrels, no mapped-land shorts, and 39 split whole-board nets. Qualification remains open because A6 exceeds the placement window and command receiver margins remain unproven.

| Signal | Planar length (mm) | Contacted barrel (mm) | Modeled flight (ps) | Signed skew to mean CK (ps) | 36.14999–38.68999 mm project window |
| --- | ---: | ---: | ---: | ---: | --- |
| A7 | 38.23230 | 5.680 | 258.050 | +21.580 | Pass |
| A10 | 36.47853 | 2.650 | 260.268 | +23.798 | Pass |
| A14 | 37.52889 | 10.410 | 300.435 | +63.964 | Pass |
| A6 | 50.14447 | 0.380 | 297.313 | +60.842 | Fail by 11.45448 mm |

A6 has four adjacent L1/L2 transitions. On the accepted board A6 measured 36.11105 mm with 7.950 mm contacted barrel and +36.726 ps skew. The replacement recovers the terminal pair while losing timing margin. A14 also has greater delay despite fitting the nominal length window. Full-width routed DDR and MMC0 reference checks, both byte groups, copper, drill, via-edge and DDR class spacing pass on this export. Main ground and DDR power land checks pass. The accepted board stays on its separate branch.

[Drilled endpoints and open nets](cam.txt) · [All byte checks](bytes.txt) · [All command lengths, transitions, skew and required receiver timing](command-timing.csv)
