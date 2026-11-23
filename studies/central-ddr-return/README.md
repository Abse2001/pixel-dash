# Central DDR return study

C_DDR41 is a 100 nF Samsung CL05B104KO5NNNC (JLCPCB C1525) between direct DCDC3 and GND at (−56.135, 15.820) mm. It uses a top-to-L2 blind ground via and a supply connection with staggered L1–L2 and L2–L3 vias. Both capacitor lands reach the intended independent CAM networks. C_DDR39 and C_DDR40 remain fitted.

The nearest same-capacitor return-via distances improve on 24 of 74 reference changes. D1 improves from 9.4851 to 4.5564 mm and from 9.0596 to 3.7197 mm. D14 improves from 8.7167 to 5.3908 mm. The new longest distance is DQSn0 at 7.2801 mm. C_DDR39 remains closest for 17 transitions. These distances cover the farther of the two legs, including the buried supply transition. Frequency-dependent transfer impedance, capacitor ESL and the spreading inductance of the planes still require assessment.

Independent drilled CAM connects 36 of 50 DDR nets and 1,117 plated barrels, with 40 split whole-board nets. Both bytes and clocks match the lock. The A6 geometry from d2c2dca passes on this same export at 36.37120 mm with a 36.14999–38.68999 mm length window. Its modeled signed skew is +38.227 ps. At DDR3L-800 and the 2.0 V/ns command, 1.0 V/ns differential-clock sensitivity point, CPU launch requires 511.227 ps setup and 341.773 ps hold. The input excursion beyond the AC threshold must persist for at least 213 ps. Actual receiver margin remains open.

Full-width DDR and MMC0 references, supply continuity, MMC0, the 0.102 mm copper and 0.1524 mm via-edge screens, drill spacing and same-side component courtyards pass. The conservative common envelope retains 57 findings. L2 uncovered area outside nominal antipads increases from 2.815160 to 2.816909 mm² at the staggered supply connection. L3 remains at 84.781019 mm². The exporter flags C_DDR41 supplier pin-one rotation as unverified. This study remains separate from the accepted PCB.

To reproduce the export, decompress handheld.circuit.json.gz, export Gerbers from the decompressed circuit, and run checks/audit-cam-connectivity.py against that circuit and archive with --with-c-ddr41 and --ddr-checkpoint followed by the fourteen opens recorded in drilled-cam.txt. The decompressed SHA-256 is d389d7e77110bf0fa1ae73c1fa5dce5729e2e7f5dfaac27f987121c15da091ae.

[Drilled endpoints](drilled-cam.txt) · [Reference changes](reference-transitions.csv) · [Receiver slew screens](receiver-slew.csv) · [Common envelope](envelope.txt)
