# Clock and A10/A14 physical escape

A10 and A14, both open on the powered 45-link board, now connect on the rotated study alongside all seven previously verified DQ conductors, both byte strobes and CK/CKn. Exact drilled CAM resolves 15 distinct DDR connections, 1,015 plated barrels and zero mapped shorts. SYSBOOT0, the physical CPU and RAM power lands, VREF, VTP, ZQ, MMC0 and all 71 local DDR returns pass. Data and strobes retain their previous copper.

Clock matching passes with CK/CKn at 20.2825 mm each. The pair's worst signed modeled mismatch is ±0.0641 ps against ±0.7134 ps. The clock fails the rotated placement's 34.950–37.490 mm project command window by 14.6675 mm. A10 measures 23.9758 mm at 157.0606 ps, +23.8777 ps after mean CK and 10.9742 mm short of the window. A14 measures 29.2578 mm at 187.5322 ps, +54.3493 ps and 5.6922 mm short. Each of the four uses two full-depth transitions totaling 2.840 mm. Actual receiver margins require source launch and receiver waveform information. The full CSV uses the complete reference layout for its prior columns.

[Assembled board](handheld.circuit.json.gz) · [Lengths, timing, residuals and receiver requirements](timing.csv) · [Physical connectivity](drilled-cam.txt) · [Geometry](geometry-checks.txt)
