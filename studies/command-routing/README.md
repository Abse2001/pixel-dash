# DDR command routing on the populated handheld

Start from the tagged 2f9ecdf populated layout. The native build applies these routes after restoring the locked byte geometry. Every new plated transition cuts a 0.16 mm radial relief around its 0.30 mm land in the inner planes.

The first phase connects A10, A15, BA0 and BA2. Exported Gerbers and Excellon show 26 distinct CPU-to-RAM links, no mapped-land shorts and zero full-width reference findings. The 0.102 mm copper gap, 0.1524 mm via-edge gap, drilled spacing, DDR self-contact and MMC0 checks pass. The two bytes reproduce the frozen timing report. This phase qualifies connectivity. Command flight timing against CK is open.

Using the actual two clock terminals, the tscircuit fanout solver could not meet 0.127 mm skew at the CPU's boundary and found no two-conductor fanout at the RAM boundary. The bus-lanes pipeline exceeded its 90-second solve budget on the populated input. The phased alternative searched both outer layers while reserving existing copper, drill clearance and full-width references.

The second phase adds A5 and WEn, bringing the drilled total to 28/50. It reconnects all six previously open RAM ground balls to L2 and five RAM supply balls to the direct DCDC3 island. The remaining isolated VDD/VDDQ balls are A8, C9, D9 and E9. The CPU calibration resistor ground remains open. Full-width references, signal and drill spacing, MCU-to-RAM isolation between unrelated nets, locked byte geometry, per-signal byte timing and MMC0 pass the same checks on this export.
