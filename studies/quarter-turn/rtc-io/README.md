# RTC I/O rail on the rotated 26-link board

The new northern route connects U1.B4 (RTC_KALDO_ENn) to the DCDC6 RTC I/O supply at C_PMIC_RTC_IO. Drilled CAM verifies B4-to-D7 continuity, D7 to the 1.8 V output network, D6 to the separate DCDC5 1.0 V network, and isolation between B4 and D6. All 71 DDR return terminals, including U1.G12, retain full land coverage. Two blind transitions avoid the earlier cut through the main ground connection.

The whole-board split-net count falls from 54 to 53. All 26 DDR links, their full timing report, N5/P5, VTP, VREF and MMC0 are preserved. The checks include exact drilled endpoints, every exported trace stroke, via-edge and copper clearance, drilling and full-width reference. RTC reset/wake, remaining data and command routing, receiver timing and system qualification still need work.

[Assembled circuit](handheld.circuit.json.gz) · [Power and isolation CAM](drilled-cam.txt) · [Physical checks](geometry-checks.txt) · [Unchanged DDR results](../d1-restored/timing.csv)
