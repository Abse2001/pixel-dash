# Populated J4 VREF routing trial

The CPU J4 ball reaches the driven DDR midpoint on exported Gerbers and Excellon. A 0.30 mm pad with a 0.15 mm through drill launches the feed. This branch starts at the protected SYSBOOT checkpoint 076b815. Run `bun run build:j4-vref` for the populated trial. The original board is still produced by the ordinary build.

Only the D12 and D14 CPU-side L1 prefixes changed. All 44 original data vias remain in place. D12 measures 19.93982 mm and D14 19.94089 mm, previously 19.93994 mm for both. They use L1–L4–L1 and 2.840 mm of contacted barrel. D12 flight is 133.777 ps with +1.664 ps worst signed strobe skew. D14 flight is 133.783 ps with +1.670 ps skew. Both pass the 0.635 mm TI matching screen and the ±3.663 ps reference-stack screen. The shortest remaining model headroom for these two signals is 1.993 ps. All 22 byte signals pass their respective screens. [Complete byte timing](byte-timing.csv)

## Initial J4 breakout

Drilled CAM at the initial breakout confirmed 36 distinct CPU-to-RAM signals, 1,086 plated barrels and no mapped-land shorts. Copper at 0.102 mm, via edge at 0.1524 mm, drill gaps, full-width reference, DDR self-contact, four-layer trace strokes, byte timing, RTC connectivity and MMC0 pass. All 18 DRAM supply balls, 21 ground balls and seven switched CPU supply balls reach their physical rails. CPU VREF is isolated from the supply and ground. The existing local capacitor's sense terminal still lacks a connection in this checkpoint. Whole-board CAM reports 47 split nets. Analog noise, source and receiver timing, and fabrication release remain open.

[Populated board snapshot](populated-handheld.png) · [Native populated circuit](populated-handheld.circuit.json.gz)

## Local bypass iterations

The next export places the original CPU VREF bypass on the reverse face close to J4. CAM now proves the driven divider, CPU J4 and the sense side of C_CPU_VREF share copper. Its other terminal reaches main ground, with VREF isolated from both supply and ground. The sense trace from the J4 via measures 0.100 mm. The ground trace to its plated return via measures 3.993 mm. The effective bypass loop inductance and VREF noise under switching load remain open. The new export passes copper, via-edge, drill, self-contact, all copper-layer stroke, full-width reference, assembly courtyard and MMC0 checks. It has 36 distinct DDR links, 1,087 plated barrels, 46 board-wide split nets and zero mapped-land shorts. All 22 byte signals retain the previous trial timing and all 44 data vias reproduce exactly.

The latest bypass return uses an L4–L3 blind via at the ground terminal and an L3–L2 buried via to the ground plane. Planar ground-return length fell from 3.993 mm to 0.4155 mm. Sense-side length remains 0.100 mm. These lengths exclude contacted barrel depth. The full-width DDR reference and net-aware CAM checks pass after both cuts. The driven J4 midpoint, local bypass ground and two-rail isolation all pass. CAM also confirms the RAM H1 and M8 bias and bypass networks. The obsolete copper at the former M8 bypass site was removed, including two plated vias and three trace stubs. The new export contains 1,086 plated barrels and 45 mapped nets with separate physical islands. Both data bytes reproduce the preceding timing results exactly. Analog VREF noise remains unmeasured.

## Populated electrical checkpoint

The relocated 49.9 Ω calibration resistor now reaches U1.J3 and the ground return on drilled CAM. N5 and P5 reach DCDC4 along with the other nineteen CPU lands on that rail. The 22 data routes and clock pair match the locked e4c906f geometry. The archived board and snapshot above follow the latest accepted electrical checkpoint. [Electrical checks and open signals](../electrical-closure/README.md) · [Current physical land report](../electrical-closure/physical-power-and-straps.txt)

Earlier A2 and A12 trials detached 103.621 and 2.616 mm² of plane copper respectively. Both signals remain open.
