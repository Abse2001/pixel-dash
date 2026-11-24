# MPU feed from DCDC2 to the seven AM3354 balls

**The accepted module fails the hot forward-drop screen at OPP100.** The problem is present on the pre-PWM board. On the 0.025 mm grid, at 600 mA, the worst feedback-to-ball drop is 117.47 mV if the load is concentrated at J13, or 114.74 mV when current is shared equally. The available forward-plus-return DC budget is 22 mV at a 1.100 V setpoint, a −2% regulator corner and a 1.056 V minimum. Even the equal-share case exceeds the entire budget by 92.74 mV before return loss. At 300 MHz OPP100, TI's 380 mA estimate gives 74.40 mV at J13 on the same grid. These are screening conditions, not measurements or an assertion of application current.

TI gives the OPP voltages for the ZCZ package in Table 5-7 and maximum current estimates in Table 5-10. For TPS65218D0 DCDC2, the ±2% DC specification applies over 2.7–5.5 V input and 0–1.8 A load. Its 1.8 A regulator rating is not the processor current. [AM335x datasheet](https://www.ti.com/lit/ds/symlink/am3354.pdf) · [TPS65218D0 datasheet](https://www.ti.com/lit/ds/symlink/tps65218d0.pdf)

## Film comparison

Both saved PCBs were matched byte-for-byte to their checkpoint before comparison. The assembled-copper model walks the six Gerbers and plated drills, solves from the output pad of L_PMIC_MPU, samples FB2, and applies unit current to each of F10, F11, F12, F13, G13, H13 and J13 in turn. It uses the resulting seven-by-seven transfer matrix to evaluate all nonnegative current shares with fixed total current. For that linear model the worst combination is attained at a single-ball injection. Equal sharing provides a second screen. There is no simulated package current redistribution.

| Grid | 58a4c29 worst FB2 to ball at 600 mA | 9b4ccde worst FB2 to ball at 600 mA | Equal share, either board | Highest-loss 1 mm tile, PCB coordinates |
|---|---:|---:|---:|---|
| 0.060 mm | 116.714 mV | 116.714 mV | 113.992 mV | X 36–37, Y 27–28 |
| 0.045 mm | 120.615 mV | 120.615 mV | 117.794 mV | X 36–37, Y 27–28 |
| 0.035 mm | 122.270 mV | 122.270 mV | 119.607 mV | X 36–37, Y 27–28 |
| 0.025 mm | 117.468 mV | 117.468 mV | 114.740 mV | X 36–37, Y 27–28 |

The hot spot is common to all seven-ball worst-case comparisons across the four grids. At 0.025 mm it dissipates 4.90% of total forward-path loss under the worst load. The four-grid range shows discretization sensitivity. The placement of the hotspot and the DC failure survive that variation. The PWM copper does not measurably change the computed results at the reported precision.

The screen assumes copper at 105 °C, 28 µm outer and 12 µm inner copper, and an 18 µm via wall. These are engineering stress assumptions without supplier-specific tolerance acceptance. Lateral geometry comes from the drilled films. Vertical distances use the saved KiCad six-layer stack. The mesh uses four-neighbor sheet conductances, a plated cylinder with low-resistance contacts to the local annular copper, a fixed-potential source contact and averaged pad contacts. Finished etch variation, package impedance, BGA solder, contact resistance and the physical ground return remain outside this calculation. No positive headroom can be inferred from those omissions.

Run `python module/analyze-mpu-feed.py CAM_DIRECTORY GEOMETRY_JSON` with the dependencies of the module CAM walk and SciPy. It prints concentrated loads, equal sharing, FB2-relative drop and the hottest tile at each resolution.

## Transient evidence still required

Close the DC feed and return first. Then evaluate output and local capacitors using effective capacitance at operating bias, temperature, tolerance and age, plus ESR, ESL and mounting inductance. Include the inductor, DCDC2 control loop and feedback pickup, the actual load-step amplitude and slew, via pairs, ground spreading, package impedance and rail transitions between the intended operating points. Compare both overshoot and undershoot at the balls with the applicable OPP window. The PMIC's ±2.5% dynamic figure applies to the specified 50–450 mA step in less than 1 µs with at least 10 µF. First-article differential probing at the regulator and nearest CPU supply/return pair under boot and stepped workload is still required.

## Parallel outer-copper trial

A separate refill added VDD_MPU copper on L1 and L6 around the existing inductor and CPU feed barrels, with 0.35 mm clearance. The trial retained the same complete drilled pad partition, full-width checked ground references and zero native DRC violations. At 0.025 mm pitch, the worst 600 mA drop fell from 117.468 to 117.295 mV. The same 1 mm tile remained hottest. This experiment is excluded from accepted copper. A parallel feed has to bypass the high-resistance section electrically to recover the approximately 95 mV deficit.
