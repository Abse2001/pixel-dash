# A11 escape with both byte lanes frozen

This populated study routes CPU F2 to DRAM R7 on A11. Both A14 via sites and its original L1 CPU launch and L4 run were reserved during the search. A14's final L1 run conflicted in two places. Seven attempts to bridge the conflicts or replace that run, including a replacement from its original second via to the DRAM, yielded no legal path on the 0.027 mm search grid. A14 is physically open on the saved export. This 36-link exchange does not qualify for the accepted board.

A11 is 37.67498 mm against the 36.14999–38.68999 mm project window. It has 2.840 mm of contacted barrel across L1–L2, L2–L3, L3–L4 and L4–L1. Its estimated flight is 237.403 ps and signed skew to mean CK is +0.933 ps. The reference-slew screen requires 365.933 ps setup and 284.067 ps hold at the CPU. The 2.0 V/ns command and 1.0 V/ns differential-clock screen requires 473.933 ps and 379.067 ps. Waveform and source margins remain open.

Two old A14 antipad boundaries rounded to self-intersections in the initial Gerbers. The saved board rebuilds those boundaries at the source. Its exported CAM connects 36 distinct DDR pairs across 1,119 plated barrels, with A11 connected and A14 open. Both frozen bytes, the A6 timing edit, the C_DDR41 supply and return lands, DDR power, MMC0, full-width return coverage and the three spacing checks were rechecked on this circuit.

A3 measured 38.2235 mm when A5 was lifted, but its inner-layer route cut the L2 return at the A5 CPU launch. Reserving even the first 0.18 mm of A5 and its corresponding RAM approach blocked the A3 path in that 0.032 mm grid search. Neither study changes a byte.

A separate L3 cross-section study tested the shared A7 and RASn escape from Y = 11.95 to 16.85 mm in X = −51 to −46 mm. The strip-width limit was 0.2410 mm for a continuous uniform strip including the constraints from the L2 reference and protected DDR projections. Two 0.102 mm tracks with a 0.102 mm gap require 0.306 mm. This bounds only that side-by-side corridor. At a 0.012 mm grid, removing any single one of the 45 modeled obstacle objects still failed to connect the two ends at that width.

[Drilled CAM](drilled-cam.txt) · [Timing for all command nets](command-timing.csv) · [Byte results](byte-timing.csv) · [Conditional receiver requirements](receiver-slew.csv)
