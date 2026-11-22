# DDR command routing on the populated handheld

Start from the tagged 2f9ecdf populated layout. The native build applies these routes after restoring the locked byte geometry. Every new plated transition cuts a 0.16 mm radial relief around its 0.30 mm land in the inner planes.

The first phase connects A10, A15, BA0 and BA2. Exported Gerbers and Excellon show 26 distinct CPU-to-RAM links, no mapped-land shorts and zero full-width reference findings. The 0.102 mm copper gap, 0.1524 mm via-edge gap, drilled spacing, DDR self-contact and MMC0 checks pass. The two bytes reproduce the frozen timing report. This phase qualifies connectivity. Command flight timing against CK is open.

Using the actual two clock terminals, the tscircuit fanout solver could not meet 0.127 mm skew at the CPU's boundary and found no two-conductor fanout at the RAM boundary. The bus-lanes pipeline exceeded its 90-second solve budget on the populated input. The phased alternative searched both outer layers while reserving existing copper, drill clearance and full-width references.

The second phase adds A5 and WEn, bringing the drilled total to 28/50. It reconnects all six previously open RAM ground balls to L2 and five RAM supply balls to the direct DCDC3 island. The remaining isolated VDD/VDDQ balls are A8, C9, D9 and E9. The CPU calibration resistor ground remains open. Full-width references, signal and drill spacing, MCU-to-RAM isolation between unrelated nets, locked byte geometry, per-signal byte timing and MMC0 pass the same checks on this export.

The third phase connects A0 and A7 on L1/L3, taking the exported board to 30/50 distinct signal pairs. Each L1/L3 transition uses a drilled L1–L4 barrel. The full-width reference test includes the L2 ground under L3 tracks. On the native Gerber and drill export, 1,028 plated barrels were checked. The mapped-land shorts, copper, 6 mil via-edge, drill spacing, full-width reference and MMC0 gates pass. The locked byte report reproduces exactly. Whole-board CAM still finds 58 nets with separate physical islands.

All 18 RAM VDD/VDDQ balls reach the direct DCDC3 output, and all 21 VSS/VSSQ balls reach main ground. The seven CPU VDDS_DDR balls reach their separate switched feed. The D8 ground escape and D9 power escape were coordinated. The ground side of R_VTP reaches the main ground. R_VTP to CPU J3, RAM L8 to R_ZQ, and VREF still need work. Copper continuity alone does not qualify rail drop or transient response.

[Per-command status](command-status.csv) lists the open links, lengths, transitions and outer-layer flight estimates. CK and CKn are open, so receiver skew and its residual are unknown. The clock trial missed the placement window of 36.150–38.690 mm despite meeting TI’s 0.127 mm pair mismatch. The byte results retain their separate TI and reference-stack model columns in [the frozen per-net report](../data-bytes/breakout-timing.csv).

The next two phases reserve the installed routes and add A8, followed by A6 and BA1. Native CAM verifies **33/50 distinct pairs**, 1,046 plated barrels and zero mapped-land shorts. All 22 locked byte routes and their 44 via spans reproduce exactly. The complete per-net byte report matches the frozen result byte for byte. The MMC0 sequenced-power and seven-link audit, full-width DDR references, 0.102 mm copper, 0.1524 mm via edge, drill spacing, self-contact and four-layer stroke checks pass. Whole-board CAM reports 55 nets on separate islands. L2 signal sections are checked against L3 VDDS_DDR and L3 signals against L2 ground. The three new routes require receiver timing and transition-return qualification.

[Full populated PCB, top view](populated-handheld.png) · [Verified native board, gzip-compressed](populated-handheld.circuit.json.gz)
