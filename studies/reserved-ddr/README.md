# Byte-1 escape with the strobe and mask reserved

This isolated copper study starts from c9be947. The CPU, RAM, byte-0 wiring, strobes and mask stayed in place. Routing from the RAM back toward the CPU with separate via search stages selected two L1–L4 transitions per signal. The first bundle of D8 and D9 passed copper spacing, interlayer drill spacing, via-edge spacing and full-width return coverage with both DQS1 legs and DQM1 reserved. D12 and D14 subsequently routed through the south channel. Length tuning used separate pockets bounded by existing pads, vias, reference copper and other conductors.

The current export connects **46 of 50** DDR nets. Original D10, D11 and D13 intersect the new southern escapes. D15 intersects the D8/D9 bundle. All five temporarily lifted command nets returned to their existing paths. The drilled Gerber audit verifies the 46 independent CPU-to-RAM links, the exact four expected opens, 1,000 plated barrels and MMC0 card power plus seven signals. The independent Gerber shorts, 0.102 mm copper, 0.1524 mm via-edge, drill spacing and full-width reference checks found zero violations. This study is excluded from the complete board candidate.

D8, D9, D12 and D14 meet the 22.090–22.674 mm joint window for the reserved strobes and a total via depth of 2.840 mm. The routed data-to-data and data-to-strobe limits are 0.635 mm, the strobe-pair limit is 0.127 mm, and the separate model limit is ±3.663 ps. Data-to-data matching covers only physically routed data signals. The per-net report identifies missing links. Positive skew means the signal arrives after its reference. The command fields give required source-valid intervals at the Micron AC135/DC90 speed-bin reference slew. Receiver setup and hold residuals need launch and waveform bounds.

[Per-net timing and residuals](timing.csv) · [CAM verification](verification.txt)

To reproduce the study, run `python studies/reserved-ddr/build.py BASELINE.json STUDY.json` on the assembled c9be947 circuit. Export STUDY.json with the project's native Gerber exporter. Pass `--study-open-ddr studies/reserved-ddr/open.json` to the CAM-connectivity and full-width reference checks when auditing this deliberately partial export. The normal audits require the full interface.

## First stage with 49 physical connections

Use `--pair-first` with the builder and `pair-first/open.json` with the two partial-study audits. This stage replaces only D8 and D9 and lifts D15. The assembled board retains the baseline paths for D12 and D14. Independent checks on this export counted 49 distinct DDR paths and 1,006 plated barrels. The exact open is D15. Reference coverage, copper spacing, via-edge spacing, drill spacing and shorts checks passed, as did sequenced MMC0 power and its seven links. The old D15 route occupies copper needed for both D8 and D9. Twelve alternative three-signal assignment/order trials did not recover all three together.

[First-stage per-net timing](pair-first/timing.csv) · [First-stage CAM verification](pair-first/verification.txt)

## Other bounded trials

The northward 1 mm RAM placement reduced the two-via byte-1 target to 17.484–18.277 mm. The reserved mask failed to escape. At the alternate offset the measured strobe lengths were 24.255 and 24.355 mm. The 0.635 mm matching tolerance then requires at least 23.720 mm against a placement ceiling of 23.500 mm. Neither placement advanced.

On byte 0 a D2/D4/D3/D5/D7 escape order found five two-via paths measuring 12.807, 16.067, 20.825, 24.377 and 23.363 mm respectively. All five missed the 19.590–20.220 mm joint window for that via depth. A D4-first order yielded only four paths. The command study found two-via paths for A1/A11/CKE/A10/A6 of 15.96/16.52/23.01/18.68/19.94 mm with additional command copper lifted. None reached the 28.550–31.090 mm project window. These preliminary lengths came from geometric search before a Gerber acceptance check. The complete exported board retains its original byte-0 and command routes.
