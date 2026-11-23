# Connect touch IRQ and verify all handheld ground lands on the rotated study

Drilled CAM on the populated board gives these connectivity results.

- Startup copper PASS U1.B4 to U1.D7.
- Startup copper PASS U_PMIC.PGOOD_BU to U1.B5.
- Startup copper PASS U_PMIC.nWAKEUP to U1.C5.
- RTC isolation PASS U1.B4 from U1.D6.
- SYSBOOT07 bias=0 CPU_to_resistor=True sense_isolated=True
- Physical SYSBOOT[15:0] 010000??0??????1, expected 0100000000010111.
- U1 DDR bypass to U_DDR_SWITCH.VOUT1: 22/22 supplied, 0 on copper shared with the other load domain.
- U_DDR DDR bypass to C_PMIC_DDR.pin1: 14/14 supplied, 0 on copper shared with the other load domain.
- MMC0 sequenced card power and seven distinct links: PASS
- 50 mapped land nets have multiple physical networks.
- 26 distinct DDR ball pairs connected. 1064 plated barrels checked. No shorts between mapped land nets.

The CPU and RAM power lands, all 71 local DDR reference terminals and the prior passing bootstrap and bypass connections remain physically intact. The full DDR timing CSV is byte-identical to the D1-restored checkpoint. Physical startup connectivity is one prerequisite for first-article testing. Sequencing waveforms, cold boot, full-byte and receiver timing, and complete board connectivity remain open.

[Assembled board](handheld.circuit.json.gz) · [Exact CAM](drilled-cam.txt) · [Geometry and regression checks](geometry-checks.txt) · [Unchanged DDR timing](../d1-restored/timing.csv)

The reset escape preserves continuous L2 ground paths from the CPU bypass return vias to the main ground plane. Independent drilled CAM verifies that all mapped handheld ground lands and barrels join the UART ground probe.

![Full handheld front copper in amber and back copper in blue](handheld-copper.png)

[Whole-board ground and startup CAM](whole-ground-cam.txt)
- Touch pull-ups on sequenced DCDC4: 3/3 (SDA, SCL, IRQ).
- Touch SDA U1.D16 to R_TOUCH_SDA.pin1: OPEN
- Touch SCL U1.D15 to R_TOUCH_SCL.pin1: OPEN
- Touch IRQ U1.V14 to R_TOUCH_IRQ.pin1: PASS

The IRQ route reaches its fitted bias resistor. The capacitive touch interface still requires a verified connection to the panel. A combined IRQ and SDA trial split the ground plane into two physical networks and was rejected.
