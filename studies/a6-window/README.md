# A6 timing checkpoint

This populated study changes one L1 segment of A6 on the 36-link board at 45733a8. Three new wire vertices add 0.26015 mm between the RAM-side transition and the RAM. Every other circuit element and all drilled spans are identical. Decompress populated-handheld.circuit.json.gz to reproduce the checked circuit.

A6 measures 36.37120 mm, previously 36.11105 mm. It clears the 36.14999–38.68999 mm placement window by 0.22121 mm at the lower end. The six transitions contact 7.950 mm of barrel. Estimated flight is 274.697 ps and skew to mean CK is +38.227 ps, previously +36.726 ps. The reference-slew DDR3L-800 calculation requires 403.227 ps of setup and 246.773 ps of hold at the CPU. Available launch margin, jitter, package behavior and slew remain unverified.

The export connects 36 distinct DDR pairs and has 40 split whole-board nets. Full-width DDR and MMC0 reference checks, both complete byte groups, supply lands and MMC0, 0.102 mm copper and 0.1524 mm via-edge clearance and drill spacing passed. The common envelope still has 57 findings. The furthest reference transfer is D1 at 9.4851 mm to the farther via of the nearest qualifying capacitor. This distance is a geometric screen.

A10 is open here. In a separate search with A10 installed, relaxing the via cost and spacing produced a 47.84947 mm A6 path, 9.15948 mm above the upper length gate, with an unusable zero-length intermediate section. A separate RESETn study found a 42.89544 mm path while holding both D12 drill locations and lifting its L1 and L4 conductors. Releasing either layer alone gave no route. Restoring D12 on L4 failed the fixed-via search with RESETn installed. Neither trial qualifies for adoption.
