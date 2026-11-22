# Populated J4 VREF routing trial

The CPU J4 ball reaches the driven DDR midpoint on exported Gerbers and Excellon. A 0.30 mm pad with a 0.15 mm through drill launches the feed. This branch starts at the protected SYSBOOT checkpoint 076b815. Run `bun run build:j4-vref` for the populated trial. The original board is still produced by the ordinary build.

Only the D12 and D14 CPU-side L1 prefixes changed. All 44 original data vias remain in place. D12 measures 19.93982 mm and D14 19.94089 mm, previously 19.93994 mm for both. They use L1–L4–L1 and 2.840 mm of contacted barrel. D12 flight is 133.777 ps with +1.664 ps worst signed strobe skew. D14 flight is 133.783 ps with +1.670 ps skew. Both pass the 0.635 mm TI matching screen and the ±3.663 ps reference-stack screen. The shortest remaining model headroom for these two signals is 1.993 ps. All 22 byte signals pass their respective screens. [Complete byte timing](byte-timing.csv)

Drilled CAM confirms 36 distinct CPU-to-RAM signals, 1,086 plated barrels and no mapped-land shorts. Copper at 0.102 mm, via edge at 0.1524 mm, drill gaps, full-width reference, DDR self-contact, four-layer trace strokes, byte timing, RTC connectivity and MMC0 pass. All 18 DRAM supply balls, 21 ground balls and seven switched CPU supply balls reach their physical rails. CPU VREF is isolated from the supply and ground. The existing local capacitor's sense terminal still lacks a connection in this checkpoint. Whole-board CAM reports 47 split nets. Analog noise, source and receiver timing, and fabrication release remain open.

[Populated board snapshot](populated-handheld.png) · [Native populated circuit](populated-handheld.circuit.json.gz)
