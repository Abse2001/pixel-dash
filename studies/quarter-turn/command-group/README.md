# First address and control group

The drilled handheld export has 24 distinct DDR links, 1,033 plated barrels and zero shorts between mapped land nets. This adds ODT, BA1, A11, A7, A3, A13, A4, A6 and WEn to the 15-link study. It keeps both byte strobes, the clock pair and all seven routed data bits unchanged. Full-width reference, the common margin, copper, via-edge and drill checks pass. A6 has the longest below-nominal class-spacing run, 26.231 mm against a 31.750 mm allowance. The export retains all 71 local returns, switched and direct DDR power, N5/P5, VTP, VREF, a physically high SYSBOOT0 and the sequenced MMC0 connections.

There are 26 open DDR links and 56 split mapped nets on the handheld. The data/strobe subset passes its current matching and modeled skew screens. The project command window for this placement is 34.950–37.490 mm. The report includes each routed command's signed arrival relative to mean CK, its project-window residual, and the source setup/hold requirements. Actual receiver timing remains open. These physical connections do not supersede the 45-link powered fallback.

[Assembled board](handheld.circuit.json.gz) · [All 50 signal statuses and actual timing](timing.csv) · [CAM land groups](drilled-cam.txt) · [Geometry checks](geometry-checks.txt)
