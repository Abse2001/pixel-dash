# A6 timing checkpoint

This populated study changes one L1 segment of A6 on the 36-link board at 45733a8. Three new wire vertices add 0.26015 mm between the RAM-side transition and the RAM. Every other circuit element and all drilled spans are identical. Decompress populated-handheld.circuit.json.gz to reproduce the checked circuit.

A6 measures 36.37120 mm, previously 36.11105 mm. It clears the 36.14999–38.68999 mm placement window by 0.22121 mm at the lower end. The six transitions contact 7.950 mm of barrel. Estimated flight is 274.697 ps and skew to mean CK is +38.227 ps, previously +36.726 ps. The reference-slew DDR3L-800 calculation requires 403.227 ps of setup and 246.773 ps of hold at the CPU. Available launch margin, jitter, package behavior and slew remain unverified.

The export connects 36 distinct DDR pairs and has 40 split whole-board nets. Full-width DDR and MMC0 reference checks, both complete byte groups, supply lands and MMC0, 0.102 mm copper and 0.1524 mm via-edge clearance and drill spacing passed. The common envelope still has 57 findings. The furthest reference transfer is D1 at 9.4851 mm to the farther via of the nearest qualifying capacitor. This distance is a geometric screen.

A10 is open here. In a separate search with A10 installed, relaxing the via cost and spacing produced a 47.84947 mm A6 path, 9.15948 mm above the upper length gate, with an unusable zero-length intermediate section. A separate RESETn study found a 42.89544 mm path while holding both D12 drill locations and lifting its L1 and L4 conductors. Releasing either layer alone gave no route. Restoring D12 on L4 failed the fixed-via search with RESETn installed. Neither trial qualifies for adoption.

### Reset escape and receiver checks

The candidate RESETn from U1.G2 to U_DDR.T2 uses the [diagnostic waypoints](reset-diagnostic-waypoints.json), with layers numbered 0 through 3 from the top. Against the installed D12, the L1 clearance envelope intersects 0.35403 mm² of D12 copper near X −54.574 to −51.185 mm. On L4, RESETn's first via conflicts with D12 and its L3 segment removes the return under part of D12 between X −58.900 and −56.633 mm. Fixing only the top escape leaves the L4 conflict. On a 0.045 mm grid, releasing all 659 modeled non-DDR support trace/via objects together while keeping the DDR conductors and existing plane reliefs also yielded no path for RESETn, RASn, A0, A3 or CASn. These are bounded searches.

At first article, acquire at electrically representative DRAM-side points and record probe location, loading, supply ramp and clock rate. RESET# on T2 is asynchronous. The TwinDie datasheet gives a LOW ceiling of 0.2 × VDDQ and a HIGH floor of 0.8 × VDD. At nominal 1.35 V these are 0.270 V and 1.080 V. Use the recorded local rails for the actual thresholds.

1. From cold power, verify T2 is low through rail stabilization and for at least another 200 µs. Check CKE on K9 is low for at least 10 ns before reset release.
2. After release, keep CKE low for at least 500 µs minus one clock. Before CKE is sampled high, verify valid differential CK on J7/K7 for at least the greater of 10 ns and five clocks, and ODT on K1 low with its specified input setup time. At 400 MHz five clocks are 12.5 ns.
3. Decode the DRAM-side command bus. Hold CKE high through initialization, observe tXPR before MRS, verify MR2, MR3, MR1, MR0 order, then ZQCL and both tDLLK and tZQinit before normal access. Record failures independently of whether MMC0 boots.

The initialization times come from the 4 Gb x8 die specification referenced by the 8 Gb x16 TwinDie datasheet. The connector and CPU reset checks cannot establish these DRAM-side timings. [Micron 4 Gb DDR3L initialization, p. 135](https://media.digikey.com/pdf/Data%20Sheets/Micron%20Technology%20Inc%20PDFs/MT41K_DDR3L_4Gb_Rev.Q_Dec2017_DS.pdf#page=135)
