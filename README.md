# Pixel Dash

## Fully connected DDR candidate

The complete candidate at 4b3d1c5 connects the handheld IRQ pull-up, keeps the 50 DDR routes and their vias identical to a4a71e2 and reduces the whole-board split-net count from 35 to 34. Drilled CAM explicitly verifies J3/VTP, RAM ZQ, the CPU and RAM VREF networks, divider rails, local bypass returns and their mutual isolation. [Complete candidate and physical land groups](https://github.com/Abse2001/pixel-dash/blob/4b3d1c5/checks/current-touch-irq-cam.txt)

The powered 45-link study at 185af66 routes touch IRQ and connects panel LCD D4 to its boot-bias resistor. Eleven of 16 panel strap taps and seven CPU strap states are verified. N5/P5, VTP, full-width DDR/MMC0/raster references and all handheld grounds pass. The DDR timing is unchanged. With D0 fixed, even completely removing A1 leaves at least two RAM-side DQ vias 0.168437 mm short of their required center spacing on every D2/D3/D4 permutation. The original powered d8461d7, fully connected 4b3d1c5 and rotated b0317c2 remain separate. [Powered physical endpoints](https://github.com/Abse2001/pixel-dash/tree/185af66/studies/powered-cpu-io) · [Joint landing bound](https://github.com/Abse2001/pixel-dash/tree/0164ece/studies/byte0-two-transition)

The rotated study at b0317c2 connects U1.V14 to the touch IRQ pull-up and preserves all mapped handheld ground connections. Fifty mapped whole-board nets remain split. The powered 45-link baseline stays at d8461d7. The 26-link study passes relative matching for its eight routed data lines, but all four routed upper-byte data lines and both upper strobes exceed the 14.200 mm project length gate. No in-byte remap alone can raise it beyond 14.99986 mm at this placement. [Full PCB snapshot and CAM](https://github.com/Abse2001/pixel-dash/tree/b0317c2/studies/quarter-turn/touch-irq) · [Per-net gate and remap bounds](https://github.com/Abse2001/pixel-dash/blob/b0317c2/studies/quarter-turn/d1-restored/remap-length-bound.csv)

The rotated study at b5e1c20 physically connects B5 (RTC reset) to PMIC PGOOD_BU, C5 to wake, and B4 to the 1.8 V D7/DCDC6 rail. B4 remains isolated from D6/DCDC5. All mapped ground lands and barrels join the UART ground probe, including the two nearby bypass returns. Twenty-six DDR signals, eight physical SYSBOOT straps, 22 CPU DDR bypasses, 14 DRAM bypasses and 71 local reference terminals pass their connectivity checks. The export still has 51 split mapped nets. [Full PCB snapshot, drilled CAM and timing](https://github.com/Abse2001/pixel-dash/tree/b5e1c20/studies/quarter-turn/rtc-reset)

The rotated populated study at 5494ca2 now connects 26 DDR signals. D1, D2, D3, D4, D10, D11, D12 and D14 pass present-peer and strobe matching plus the reference-stack delay screen together. All 71 local return terminals and both CPU supply feeds pass. Twenty-four DDR signals and whole-board closure remain open. [Full PCB snapshot, per-net limits and physical CAM](https://github.com/Abse2001/pixel-dash/tree/5494ca2/studies/quarter-turn/d1-restored)

The rotated RAM study at 9c71554 connects 25 distinct DDR signals on the powered handheld. D2/D3/D4 and D10/D11/D12/D14 pass their local TI length and modeled skew screens together. A10, A14, BA2 and CK/CKn are physically connected, with command timing still open. SYSBOOT0 reaches the CPU, its high strap and panel. All 71 local DDR return terminals pass. The powered 45-link baseline remains separate. [Full-board copper, per-net timing and drilled CAM](https://github.com/Abse2001/pixel-dash/tree/9c71554/studies/quarter-turn/ba2-breakout)

A separate 90° RAM placement at f7b27e7 routes D2, D3 and D4 together with a matched DQS0 pair. All five use two full-depth transitions, pass drilled CAM, and retain the local power and return paths. Worst modeled data skew is +1.7561 ps against ±3.6633 ps. This five-link study reserves startup space at SYSBOOT0. The unchanged RAM orientation leaves the entire SYSBOOT0 pad inside the required margin even if all DDR routes are lifted. [Timing, geometry, assembled study and drilled CAM](https://github.com/Abse2001/pixel-dash/tree/f7b27e7/studies/quarter-turn/timed-d234) · [Placement measurements](https://github.com/Abse2001/pixel-dash/tree/fcbf70b/studies/quarter-turn)

The powered board at d8461d7 also connects SYSBOOT7 and SYSBOOT12 to their bias resistors. Seven straps have verified physical states. The DDR bus remains at 45/50, with its full timing CSV and reference checks preserved. [Current powered board and drilled strap results](https://github.com/Abse2001/pixel-dash/tree/d8461d7/studies/powered-cpu-io)

The powered I/O checkpoint at 8c7bccf closes physical SYSBOOT10, panel D10, backlight PWM and amplifier logic bias. It retains the 45 DDR links, their complete timing CSV and the two power feeds. CAM reports 36 split whole-board nets. On the unchanged e5fd49f copper, the independent two-transition screen finds all nine D2/D3/D4 pin assignments disconnected within 20.4313 mm with their neighbors fixed. Releasing D0 or A1 restores individual reachability. [Powered I/O checkpoint and CAM](https://github.com/Abse2001/pixel-dash/tree/8c7bccf/studies/powered-cpu-io) · [Length-bounded topology screen](https://github.com/Abse2001/pixel-dash/tree/aa53c0e/studies/byte0-two-transition)

The powered baseline at 4fd6b86 shortens D5 to 25.7789 mm and retains its 45 distinct DDR links. On the alternative D15-passing branch, e5fd49f also removes two D7 transitions. D7 improves from +38.5076 to +16.5431 ps against the ±3.6633 ps model screen. Neither byte is complete. [Powered baseline timing](https://github.com/Abse2001/pixel-dash/blob/4fd6b86/studies/powered-byte1/d5-timing.csv) · [Alternative D5/D7 report and CAM](https://github.com/Abse2001/pixel-dash/tree/e5fd49f/studies/powered-byte1)

The native build of the powered 45-link board is verified at fc8c13c. A separate crossing trial at 354eaf8 brings D15 to 22.6549 mm with −1.8131 ps worst signed skew against the ±3.6633 ps model gate. It preserves the physical supplies and all 45 links, but moving the intermediate D3 bridge increases its skew to +54.1593 ps. Both byte lanes still have open signals. [Passing D15, D3 regression and exact CAM results](https://github.com/Abse2001/pixel-dash/tree/354eaf8/studies/powered-byte1)

The powered byte-1 study at 178dd63 has 45/50 distinct DDR connections. D12, D13 and D14 meet their TI strobe matching and model skew gates. D13 has just 0.0977 ps of modeled headroom. D15 is connected and retains full reference coverage, but its +5.4050 ps worst modeled skew exceeds the ±3.6633 ps screen. A10, A14, D1, D10 and D11 still need copper. Both N5/P5 and the VTP resistor return pass drilled CAM. [Timing, exact physical lands and intermediate fallbacks](https://github.com/Abse2001/pixel-dash/tree/178dd63/studies/powered-byte1)

The separate four-route breakout moves the switched DDR feed to make room for N5/P5. It physically connects 21/21 DCDC4 lands and 7/7 switched CPU DDR lands, with D1, D12, A10 and A14 lifted. [Boot-power study and screening results](https://github.com/Abse2001/pixel-dash/tree/ff755ca/studies/boot-ddr-breakout)

The four-layer AM3354 handheld at a4a71e2 retains 50 distinct CPU-to-RAM signals. BA2 shortened from 29.7914 to 28.6872 mm inside its 28.550–31.090 mm project window. Modeled arrival relative to mean CK improved from +10.7705 to +4.4005 ps. All DDR vias and the other 49 routes are unchanged. D11 and D15 now have continuous exported raster reference, including the strap traces. Independent CAM passes the common DDR envelope and full-width DDR, MMC0 and raster checks. Data-byte timing, command receiver signoff, N5/P5 power, physical straps and whole-board release remain open. [Full PCB snapshot](https://github.com/Abse2001/pixel-dash/blob/a4a71e2/previews/handheld.png) · [Per-net timing](https://github.com/Abse2001/pixel-dash/blob/a4a71e2/checks/current-ddr-change.csv) · [Physical land report](https://github.com/Abse2001/pixel-dash/blob/a4a71e2/checks/current-raster-taps-cam.txt)

The isolated D12/D1 trial retains all 50 distinct DDR pairs and passes copper, drilling and full-width reference checks. Both shortened signals still miss the TI and model matching targets. On the full board, A10/A14 also bound the N5/P5 escape. With D12/D1 entirely removed, neither supply pad has any exposed copper beyond the DDR margin. [Trial, timing targets and physical lands](https://github.com/Abse2001/pixel-dash/tree/12332c9/studies/d12-d1-breakout)

The separate boot study connects all 21 DCDC4 lands and SYSBOOT12. Its N5 and P5 copper and the V2 strap escape fail the common keepout. Both power pads are wholly inside even the smaller envelope defined by the locked bytes and clock. [Boot study and CAM findings](https://github.com/Abse2001/pixel-dash/tree/8c27acf/studies/complete-boot-escape)


The protected populated board has 36/50 distinct CPU–RAM signals and all 22 original byte routes. A8 measures 36.533 mm in its 36.150–38.690 mm placement window and arrives an estimated 0.107 ps before mean CK. RTC reset, wake, power hold and the isolated DCDC5/DCDC6 core and I/O connections pass drilled CAM. Six of sixteen SYSBOOT bits reach the CPU. [Protected board and timing](https://github.com/Abse2001/pixel-dash/tree/076b815/studies/clock-first) · [Protected full-board snapshot](https://github.com/Abse2001/pixel-dash/blob/076b815/studies/clock-first/populated-handheld.png)

The populated CPU escape trial connects the driven VREF divider and bypass to J4, J3 to the grounded calibration resistor, and all 21 CPU DCDC4 lands including N5/P5. Eight reset straps reach the CPU. Raster D12 reaches panel pin 15. Panel D3 reaches its strap resistor and still needs CPU ball R4. Twelve of sixteen panel data pins reach the strap pads, with 25 existing raster reference findings. Exported CAM resolves 36/50 distinct DDR pairs. A0 and A10 lost connectivity during clock routing, with identical CPU and DRAM pin assignments at both checkpoints. The 22 byte routes and clock pair retain the e4c906f geometry. Fourteen open DDR links, receiver timing and remaining boot and board-level checks keep fabrication on hold. [Physical evidence](https://github.com/Abse2001/pixel-dash/tree/b5356e7/studies/electrical-closure) · [Full-board PCB](https://github.com/Abse2001/pixel-dash/blob/b5356e7/studies/j4-vref/populated-handheld.png) · [Rejected A7/A10 exchange and exact CAM results](https://github.com/Abse2001/pixel-dash/tree/470c8be/studies/a7-a10-corridor)

## Populated handheld DDR data checkpoint

The tagged populated layout preserves all 22 passing byte 0 and byte 1 routes through 44 plated vias. The handheld Gerbers verify each distinct CPU-to-RAM pair, full-width reference coverage and zero mapped-land shorts. All 236 component courtyards clear after relocating eight passives. The other 28 DDR links remain open on this checkpoint. [Saved populated circuit and checks](https://github.com/Abse2001/pixel-dash/tree/pixel-dash-populated-ddr-locked/studies/data-bytes) · [Preserved breakout](https://github.com/Abse2001/pixel-dash/tree/pixel-dash-ddr-bytes-verified-2dc2af8)

## DDR timing study

The complete routed candidate at bf75444 has 50 distinct drilled CPU-to-DDR3L connections. All 71 local blind-via lands reach connected inner-layer Gerber copper. A staggered 100 nF bypass shortens the return distance at 21 DDR transitions. ODT improves from 9.504 to 7.123 mm, and the worst remaining transition is A1 at 8.718 mm. Byte 0's worst modeled data skew is +38.508 ps on D7 and byte 1's is +7.700 ps on D12, against ±3.663 ps. DQS0's pair mismatch is 0.0145 mm against TI's 0.127 mm limit. A6 now measures 28.647 mm and A4 measures 28.650 mm against the 28.550–31.090 mm command window. Both use two full-depth vias. A10 and CKE still miss that window, and receiver timing remains open. The separate 47-link candidate meets matching on the complete upper byte but has three open lower-byte nets. Fabrication remains on hold. [Complete routed layout](https://github.com/Abse2001/pixel-dash/tree/bf75444) · [All 50 lengths, delays and targets](https://github.com/Abse2001/pixel-dash/blob/bf75444/checks/current-ddr-change.csv) · [Drilled whole-board connectivity](https://github.com/Abse2001/pixel-dash/blob/bf75444/checks/current-raster-taps-cam.txt) · [Upper-byte routing study](https://github.com/Abse2001/pixel-dash/tree/a4307c5)

Both active-low PAM8403 controls now reach the 3.3 V output. The drilled connectivity audit counts 34 open mapped nets across the handheld. The JLCPCB land patterns for the battery inductor and auxiliary 3.3 V regulator now match the routed candidate. All eight affected lands have verified external connections in drilled CAM. [Assembly placement audit](https://github.com/Abse2001/pixel-dash/blob/bf75444/checks/current-assembly-angles.csv)

## Wide handheld checkpoint

**Fabrication is on hold.** DCDC4 supplies 19/21 assigned 3.3 V CPU/USB
lands, including both supply balls of VDDSHV1, VDDSHV2 and VDDSHV4.
Banks 2 and 4 power the upper raster data signals and MMC0 respectively.
N5 and P5 are open. LDO1 reaches all 16 assigned 1.8 V loads. Only four
CPU straps reach their bias resistors. Five of sixteen panel contacts now
reach their strap sense pads, including D0. The joystick ADC and its
bypass draw from DCDC4 and share the main ground. CAM finds 6/29
CPU-to-panel and 7/7
CPU-to-card signal paths, with 38 mapped nets still open across the board.
[Top copper from the current Gerber export](previews/wide-top-copper.png) · [Physical connectivity](checks/current-cam-connectivity.txt)

The north-RAM study connects all 16 SYSBOOT straps (0x4017), RTC and boot power, 25 DDR links and 9/29 panel signals together. Both strobe pairs are length matched. D14 still has six full-depth traversals and exceeds its timing window. The study’s hot transient reserve is only +0.073 mV in the reference calculation. Production retains all 50 DDR links. [Study geometry and verification](https://github.com/Abse2001/pixel-dash/tree/0e92db1/studies/zoned)

MMC0 card power, both VDDSHV4 balls (H14/J14) and the five 10 kΩ
CMD/DAT pulls share DCDC4. Its default SEQ4 setting enables DCDC4 at
STROBE7. The independent retained regulator has no copper path to the
socket supply. The 0.75 mm card feed is 74.81 mm with three plated
transitions. The local 100 nF and 1 µF bypasses and socket VSS reach the
main return. Run the drilled-Gerber audit with `--mmc0-power` for each
socket, CPU, capacitor and resistor terminal and rail isolation. Use
`--mmc0-only` for the focused pass/fail exit code.

TI rates DCDC4 at 1.0 A at 2.8 V input, 1.3 A at 3.6 V and 1.6 A at 5 V
for 3.3 V output. The six CPU I/O banks total 350 mA at their listed
maximums, plus 80 mA for both USB analog supplies. Allocate 200 mA to a
qualified 3.3 V default-speed card and 50 mA for pull resistors, ADC and
other low-current loads. This totals 680 mA and leaves 320 mA against
the lowest listed continuous rating. These are design allocations.
Qualify the actual card, input sag, inrush, temperature and load steps.
At reset keep MMC0 at 3.3 V. Hold host lines inactive until VDD settles
and shut the host down before the common rail falls. Scope both supply
ends and signal voltages on ramp and discharge to check injection and
regulator limits. [TPS65218D0 electrical characteristics and SEQ4](https://www.ti.com/lit/ds/symlink/tps65218d0.pdf) · [AM3354 maximum current ratings](https://www.ti.com/lit/ds/symlink/am3354.pdf)

B4, B5, C5, N5 and P5 cannot accept unrelated copper outside the saved
DDR envelope at the required 0.408 mm setback. Running
`checks/screen-ddr-placement.py <board.json> --routed --balls B4 B5 C5 N5 P5`
gives maximum distances of 0.0000, 0.0259, 0.0000, 0.0574 and 0.2086 mm
over their entire lands. Even a zero-width connection fails this bound on
the current routing. The older protected copper is available in git.
A separate launch search samples a 0.102 mm wire at the edge of each
power land. For B5 the 25° direction requires relocating A14, A6 and A8.
For N5 the 353° direction requires relocating A10, D1, D12 and D14.
B4 and C5 share six blocking command nets. The search tests only the DDR
envelope and lists candidates for a coordinated reroute. It does not
establish an obstacle-free route to the PMIC.
[Boot escape directions and blocking nets](checks/current-boot-escape-corridors.csv)

The [offset placement](https://github.com/Abse2001/pixel-dash/tree/488aee8)
has cleared all 25 original copper-spacing findings. Its 50 physical DDR
links pass, with 13 full-width reference gaps and both byte windows still open. Würth
HDI4_1-2b-1_149_35_2V13 is the pinned engineering cross section.
DDR timing, hot LS1 margin and supplier acceptance remain open.

DCDC3 supplies the memory directly. At the next strobe LS1 enables a
TPS22975DSGR (JLCPCB C524777) that supplies the seven CPU VDDS_DDR lands.
VSYS biases the switch. LS1 drives its ON pin and a 22 µF / 220 Ω control
network. A 1 nF CT capacitor controls turn-on. A 47 Ω output bleed and
the switch discharge path provide controlled shutdown. CAM tests input,
bias, control, CT, output, ground and the separate memory rail.
[TI TPS22975 electrical characteristics and timing](https://www.ti.com/lit/ds/symlink/tps22975.pdf)

At 250 mA CPU load plus 29.6 mA bleed, the 105 °C sensitivity with
80% conductor area and 40 mΩ switch resistance leaves **13.89 mV DC**
above the CPU minimum. Combining the −2.5% source case with a 100 mA,
1 µs step, 46.5 µF effective output capacitance and a 2 mV parasitic
allowance leaves **2.991 mV** of modeled transient reserve. Mask-covered top copper follows the seven supply lands and their input via. It reduces the drilled L1 resistance to a 0.150 mm E5 contact from 13.352 to 7.570 mΩ. Additional input copper joins the DCDC3 bypass to VIN1. The drilled input path measures 2.871 mΩ at 20 °C and the screened complete board loop is 32.010 mΩ at 20 °C. Gerber payload comparison shows only top copper changed. Capture bias, enable, input and voltage at
the CPU on cold start, hot load steps, commanded shutdown and abrupt
input loss. Measure reverse current during collapse. These results depend
on the reference stack, load, switch resistance and capacitor impedance.
Reproduce with `checks/estimate-ls1-pours.py BOARD GERBERS --wurth --return-path`
and `checks/screen-ls1-drop.py BOARD --wurth --sheet-network-report REPORT --require-hot-reserve`.
[Corner results](checks/current-ls1-budget.txt) · [Drilled sheet solve](checks/current-ls1-pours.txt)

The [coordinated seven-net trial](https://github.com/Abse2001/pixel-dash/tree/214365f)
opened both the B5 and N5 corridors and shortened D1 and A10, but the trial
copper shorts nets together and loses full-width reference. It stays separate.

### AM3354 SRAM and back-bias capacitors

The four copper layers and plated drills verify these five dedicated connections.
Each capacitor has an L1–L2 microvia inside its ground land. The three internal
outputs are electrically separate from each other and from PMIC LDO1. D10 and
E9 draw from LDO1 and each has its own 10 µF capacitor.

| ZCZ ball | Function | Fitted capacitor | Planar path | Modeled forward copper and barrel resistance at 20 °C |
| --- | --- | --- | ---: | ---: |
| C10 | CAP_VBB_MPU | C_VBB_MPU, 1 µF | 6.05 mm | 15.69 mΩ |
| D9 | CAP_VDD_SRAM_CORE | C_SRAM_CORE, 1 µF | 7.36 mm | 25.38 mΩ |
| D11 | CAP_VDD_SRAM_MPU | C_SRAM_MPU, 1 µF | 6.31 mm | 19.70 mΩ |
| D10 | VDDS_SRAM_MPU_BB | C_SRAM_MPU_IN, 10 µF | 9.78 mm | 20.99 mΩ |
| E9 | VDDS_SRAM_CORE_BG | C_SRAM_CORE_IN, 10 µF | 10.41 mm | 22.76 mΩ |

The two input paths widen from 0.20 to 0.65 mm where clearance permits.
The 1 µF and 10 µF parts carry JLCPCB codes C15849 and C19702 respectively.
The estimates use the engineering cross section and exclude capacitor
derating, ESR, loop inductance and package drop. Dynamic bypass impedance,
regulator stability and SRAM inrush remain unverified. The 1 mm L3 supply
bridge retains the direct DCDC3 feed to all 18 DRAM supply balls and
preserves full-width signal reference. At the preceding capacitor checkpoint all 227 fitted placements and 7,716
routed copper strokes match the engineering export.
[TI SPRS717L §5.9, Tables 5-14 and 5-15](https://www.ti.com/lit/ds/symlink/am3354.pdf)

Of the twelve open SYSBOOT lands, eleven have maximum pad-edge distance
below the 0.408 mm saved DDR setback. V2 (bit 12) has 0.0272 mm excess
at its farthest edge. The sampled blind-via escape search did not find
a legal launch. The full set of sixteen straps is still a fabrication gate.
[Physical strap envelope](checks/current-sysboot-envelope.csv)

### Panel reset

J_LCD pin 44 now connects to AM3354 J18 (MII1_TXD3, mode 7, GPIO0_16).
This spare VDDSHV5 pin has a low reset state in TI Table 4-2. Firmware
must use GPIO0_16 for panel reset and release it only after valid panel
bias and the panel’s reset timing. The four copper layers and plated drill
files verify the connection. The full-width ground-reference screen checks
L1 against L2, L4 against L3 and the inner reset runs against the adjacent
inner ground. The routed reset, five other raster signals and all seven
card signals pass this geometric check. Panel bias sequencing and the
other 23 panel endpoints remain open.
[AM3354 pin attributes](https://www.ti.com/lit/ds/symlink/am3354.pdf)

### Pending cold-boot bench test

With power and backup energy fully removed between runs, repeat cold starts
with the 7-inch panel disconnected, then with it connected while unpowered.
Capture 3.3 V, RTC rails, PGOOD_BU and PWRONRSTn from power application.
Record all sixteen strap voltages at the rising PWRONRSTn edge against the
applicable TI input thresholds and setup/hold limits. Early bring-up firmware
must log the latched CONTROL_STATUS SYSBOOT field (expected 0x4017) on UART0
before switching LCD pins to raster. Record the boot source, MMC0 boot
result, DDR initialization and panel/backlight supply state on each run.
Use a known-good, write-verified 3.3 V microSD with a recorded image hash,
a compatible AM335x ROM MLO and a unique early UART build marker. Prove
the media works on a reference target with its compatible image. With
USB boot disconnected and no UART download host, capture the ROM MMC0
clock/CMD exchange, boot-device report and marker on each cold start.
Repeat without the card as a negative control. Record socket VDD vs VSS,
VDDSHV4 and the first clock at power-on, then signal and rail discharge
at shutdown. Repeat this test with the panel fitted and removed.
This is pending hardware verification. CAM currently confirms only bits
11, 13, 14 and 15. TI section 5.9 local capacitors have a separate
endpoint check under `--cpu-power`.

### Routing and verification history

All 50 AM3354-to-DDR3L signals reach their intended balls on 50 distinct electrical nodes. The adjacent plane covers the full trace width for all 50 signals outside their own via launch antipads. The board-wide 0.102 mm unrelated-copper, 0.1524 mm via-edge and drill-spacing checks pass. Each of the 7,491 routed strokes matches the copper Gerbers, and all five drill files match the board.

The L3 ground pour now clears the DDR island area before the exporter draws the supply copper. In older archives the final clear aperture erased the supply island. To verify a new export, install Gerbonara and Shapely 2 and run both `python checks/audit-ddr-reference-planes.py dist/index.circuit.json --full-width --gerbers engineering.zip` and `python checks/audit-ddr-keepout.py dist/index.circuit.json --envelope --gerbers engineering.zip`. The first check passes on all 50 DDR routes outside their own launches. The second reports zero signal or reference-layer findings across the reconstructed DDR region and setback. [CAM envelope results](checks/current-ddr-cam-envelope.csv) The CPU VREF link formerly cut a 1.152 mm² slot through the L3 reference. Two through vias now carry the link across the outer layers. The 0.32 mm bottom section and both top escapes clear unrelated copper, and all three VREF bypass connections pass continuity. The Gerber polarity check uses the connected reference island, preserving flashed lands, clearance apertures and draw order.

TI Table 7-63 also specifies a setback around the entire DDR routing region. Run `python checks/audit-ddr-keepout.py dist/index.circuit.json --envelope` to screen the convex hull of the DDR signal copper and RAM lands. The SYSBOOT11 and SYSBOOT13 copper clears the region after rerouting the D12 and D14 trunks together at their existing plated transitions. The left joystick click signal crosses between its two outer-layer sections on L3 outside the four-width margin. After narrowing the D2 and R1 RAM supply escape links to 0.165 mm, direct 512-segment-per-quadrant relief circles bound the remaining reconstructed CAM area outside nominal antipads to 0.000000004 mm² on L2 and 0.000000003 mm² on L3 (values rounded to nine decimals). Both are below the existing 0.000001 mm² screen. The 387.1561 mm² envelope and its 0.408 mm margin clear unrelated signal copper in the exported files. The convex hull is a candidate engineering boundary. [TI AM335x datasheet, section 7.7.2.3.3.5](https://www.ti.com/lit/ds/symlink/am3354.pdf)

The AM3354 ZCZ IBIS model includes all 50 routed signal balls in its package pin list and provides 1.35 V choices for each associated selector. Reproduce the pin check with `python checks/check-ddr-pinmap.py dist/index.circuit.json --ti-ibis sprm552c.ibs`. TI's model notes flag validation status and warn that some selector choices are invalid for particular pins. Drive, termination and slew choices must agree with the device configuration before waveform simulation. [TI ZCZ IBIS archive, SPRM552C](https://www.ti.com/lit/zip/SPRM552)

The exported signal topology has 120 full-depth DDR transitions with 0.30 mm lands and 0.15 mm drills. Sixty centers lie inside a nominal BGA body, 28 at the CPU and 32 at the RAM. TI Table 7-62 lists an 18 mil land and 10 mil drill as typical; note 5 calls for the 18 mil land for minimum-layer-count via-channel escape. The saved four-layer HDI escape differs from this reference. An in-memory trial changing the 60 in-package vias to 18/10 mil at their current positions produces 92 violations of the 6 mil via-to-unrelated-trace rule. The manufacturing candidate retains the checked geometry. Reproduce the comparison with `python checks/compare-ddr-escape-vias.py dist/index.circuit.json`. The comparison does not establish launch impedance or electrical equivalence. [TI AM335x datasheet, Table 7-62](https://www.ti.com/lit/ds/symlink/am3354.pdf)

The fitted MT41K512M16VRP-107 IT:P is one rank made from two x8 dies. Its 16 row bits, 10 column bits, eight banks and 16-bit data bus give 1 GiB. The board uses one chip select and one external 240 Ω ZQ resistor. For read/write simulations, Micron Table 7 gives package loads of 2.4–4.0 pF per CK input, 2.4–4.6 pF for command/address/control, and 2.8–4.2 pF for DQ, DM and DQS under the stated test conditions. TI specifies a 2.5–3.3 ns clock period. The memory's 1866 MT/s speed grade is distinct from the AM3354 interface ceiling of 800 MT/s. [Micron part listing](https://www.micron.com/products/memory/dram-components/ddr3-sdram/part-catalog/part-detail/mt41k512m16vrp-107-it-p) · [Micron TwinDie datasheet](https://datasheet.lcsc.com/datasheet/pdf/1a552aaada9c9cb5685b5fb937531c2e.pdf) · [TI AM335x datasheet, Table 7-58](https://www.ti.com/lit/ds/symlink/am3354.pdf)

Three 1 mm probe lands on the underside expose UART0 RX (U1.E15), UART0 TX (U1.E16) and ground at 2.54 mm pitch. Connect adapter TX to RX, adapter RX to TX, and ground to ground. Use a 3.3 V logic adapter with its supply lead disconnected, and power the board before driving RX. SYSBOOT selects UART0 as a fallback after MMC0 and SPI0. All three lands have mask openings and no stencil apertures. The console still requires powered VDDSHV6, valid reset and boot sequencing. [TI AM335x boot configuration](https://www.ti.com/lit/ug/spruh73q/spruh73q.pdf)

Run `python checks/audit-cam-connectivity.py dist/index.circuit.json engineering.zip --pmic-controls --handheld-ground --cpu-power --sysboot --panel-storage` to reconstruct the four finished copper layers and walk the plated barrels. The 50 DDR links and the three UART probe connections pass. The whole-board screen reports 39 schematic land nets with multiple disconnected copper networks. [CAM connectivity report](checks/current-cam-connectivity.txt)

CAM verifies the 0.30 mm DCDC3 output-capacitor link to IN_LS1, the nWAKEUP pull-up connection, nINT to U1.T14 and PGOOD to U1.B15. The 10 kΩ cold-reset pull-up joins PGOOD to the sequenced 3.3 V rail through its two separate lands. RTC reset and the processor wake signal still need copper. The five routed raster signals pass full-width exported reference coverage. Local changes to CLK, CMD, DAT1, DAT3 and DETECT keep the entire width of each routed microSD trace above connected ground outside its own launches. Run the exported reference check with `--micro-sd --full-width --gerbers engineering.zip`.

The inherited ground had 56 disconnected copper networks. Eighty-one new L1–L2 blind vias bring the 55 isolated networks onto the main ground, including the card socket shields, controls, battery regulator, speaker amplifier and bypass capacitors. The exported copper and drill check finds one network for all mapped ground lands and barrels. The buck-boost PGND connection has three local 0.25 mm escape tracks. The 0.125 mm drills and 0.28 mm lands at assembly pads require filled and capped HDI vias. Ground continuity alone does not establish current capacity or power-loop inductance.

Eight short L1 links join adjacent VDD_CORE and VDD_MPU balls under the AM3354. The six core links reduce its disconnected groups from 21 to 15, and two MPU links reduce its groups from eight to six. The MPU regulator reaches all seven MPU supply balls. The links are 0.245–0.36 mm wide and introduce no new vias.

The processor supply check follows the individual BGA lands to their intended regulator terminals, including lands whose schematic still lacks a rail assignment. Four new blind vias connect VSS_RTC (A5), VSSA_ADC (E8) and VSSA_USB (M14 and N14) to L2. All 43 checked processor return balls now reach physical ground. All 20 core supply balls and all seven MPU supply balls reach their respective regulator outputs. Two 0.13 mm top traces feed F6 and G6 from G7. A 0.80 mm L1 link from K6 to L6 uses a 0.13 mm width and clears the DDR envelope by 0.415 mm against the 0.408 mm setback. All seven CPU VDDS_DDR balls reach LS1 through an L1 connection between balls and dedicated L4 copper. The rail check covers the selected I/O domains, analog supplies and RTC outputs; remaining I/O-bank assignments and internal-regulator capacitor requirements need their own checks. [TI AM335x power guide, Table 1](https://www.ti.com/lit/ug/slvuaa9b/slvuaa9b.pdf)

At the BuyDisplay FPC, pins 1 and 2 share the LED anode, pins 3 and 4 share the cathode, and pins 6 and 46 share VCOM. The two 0.30 mm backlight links and 0.22 mm VCOM route close three split nets in the exported artwork. The panel still needs its bias sources, regulated LED current and the remaining data and control signals.

The RTC and CORE escape moves A6, A10, A13 and A14. A13, A14 and A6 now fall short of the planar address window by 7.053, 4.004 and 5.485 mm. A10 exceeds it by 8.142 mm. The previous geometry remains available at 1fb8fbe. The VTP resistor returns along 0.13 mm bottom copper to the existing ground barrel beside C_DDR39. CAM verifies the ground connection and reconstructs continuous DDR references on both inner layers.

The first VDD_CORE feed uses 0.65 mm copper on L3 and a 0.99 mm L1 crossing. The crossing preserves the narrow L3 DDR supply connection to its bypass vias. The L3 distribution branches are 0.32–0.50 mm wide. The core regulator output capacitor and all 20 processor balls share a physical network in the exported copper. IR drop, barrel current, transient response and the remaining core distribution still require verification.

The external RTC configuration assigns B4 (RTC_KALDO_ENn) and D7 (VDDS_RTC) to DCDC6 at 1.8 V. D6 (CAP_VDD_RTC) takes DCDC5 at 1.0 V. AM3354 Figure 6-5 note B gives 1.1 V nominal for the external core source. Its recommended input range is 0.900–1.250 V, and the paired TPS65218D0 guide specifies 1.0 V on this pin. The voltage at the processor must stay within the operating range through startup, ripple and load steps. [AM3354 datasheet](https://www.ti.com/lit/ds/symlink/am3354.pdf) · [TPS65218D0 paired guide, Figure 1 and Table 1](https://www.ti.com/lit/ug/slvuaa9b/slvuaa9b.pdf)

The paired startup sequence brings up DCDC6, then DCDC5. PGOOD_BU monitors both backup rails and drives RTC reset at B5. PGOOD drives cold reset at B15, GPIO3 connects to warm reset at A10, and C6 must assert PWR_EN within the PMIC’s 20 s window. The `--cpu-power` CAM check reports the copper for each connection, the nWAKEUP and PGOOD pull-ups, both RTC capacitor returns, and the isolation of D6 from B4 and D7. D7 and the 100 kΩ nWAKEUP resistor now reach the DCDC6 output capacitor. D6 now reaches the DCDC5 output and stays isolated from B4 and D7. B4 still needs its DCDC6 connection. Two blind L1–L2 vias route C6 to PWR_EN. Static CAM cannot measure reset release time or rail settling. [TI paired guide, Figures 1 and 4](https://www.ti.com/lit/ug/slvuaa9b/slvuaa9b.pdf) · [TPS65218D0 datasheet, backup power-good and state machine](https://www.ti.com/lit/ds/symlink/tps65218d0.pdf)

The same CAM check audits DDR power separately from its 50 signal nets. TI Figure 1 supplies the memory VDD/VDDQ balls from DCDC3 and the processor VDDS_DDR balls through LS1. CAM verifies the two physical load domains are isolated. The DCDC3 output reaches all 18 RAM VDD/VDDQ balls and its 14 bypass capacitors. The LS1 output reaches all seven processor VDDS_DDR balls and its 22 bypass capacitors. The two L4 switched-supply areas join through a 0.60 mm L3 bridge. This verifies copper continuity; rail ramp, load step and voltage drop at the balls still require evaluation. [TI paired connection diagram](https://www.ti.com/lit/ug/slvuaa9b/slvuaa9b.pdf)

Run `python checks/screen-ls1-drop.py dist/index.circuit.json` for the LS1 screening budget. At 300 mA, 1.35 V minus 2%, and 110 mΩ switch resistance, the CPU's 1.283 V minimum leaves 7 mV for the board. With 35 µm foil at 20 °C the widened feed models 9.630 mV of trace drop and 2.798 mV in seven barrel sections. This case misses the minimum by 5.428 mV before plane spreading, return drop and transients. The input feed now widens from 0.30 mm in its constrained sections to 1.40 mm where clearance permits. This lowers its modeled trace resistance from 18.502 to 10.785 mΩ at 35 µm and 20 °C. The 300 mA figure is the switch's recommended operating ceiling. A measured CPU DDR current profile or validated workload estimate is still needed. The switched bank is 46 µF nominal. Its two 22 µF bulk parts are Samsung CL21A226MAQNNNE, 25 V X5R, JLCPCB C45783. As a sensitivity case, 50% retained capacitance would give 4.35 mV ideal droop for 100 mA over 1 µs. DC bias, tolerance, temperature, aging, ESR, ESL and enable inrush require verification with the fitted parts. [TI TPS65218D0 electrical characteristics](https://www.ti.com/lit/ds/symlink/tps65218d0.pdf) · [TI AM335x recommended operating conditions](https://www.ti.com/lit/ds/symlink/am3354.pdf)

The sequenced 3.3 V DCDC4 buck-boost now has its 1.5 µH TDK inductor between L4A and L4B, two 47 µF ceramic output capacitors and eight local ground-return vias. CAM checks both ends of the inductor, both capacitors and the isolation of the two switch nodes, output, input and ground. The output feeds the PGOOD pull-up supply, the boot-high resistor bank and nineteen of the twenty-one processor supply lands. Both cold-reset pull-up terminals pass the exported connectivity check. Effective output capacitance, input bypass, source distribution, load capability and startup remain open. [TI DCDC4 pin functions and electrical characteristics](https://www.ti.com/lit/ds/symlink/tps65218d0.pdf)

A 0.81 mm MPU branch from F10 to F11 opens space for a 0.18 mm 3.3 V link from E12 to E11. E10 and E11 now join the powered I/O bank. CAM verifies every MPU ball and nineteen of twenty-one 3.3 V balls. The remaining lands are N5 and P5 in VDDSHV6. The SYSBOOT source checker decodes 0x4017, selecting 24 MHz and MMC0, SPI0, UART0 and USB0 in sequence. Open strap copper prevents treating that word as a verified latched boot configuration.

Two 1.20 mm VSYS routes with 0.35 mm drills and 0.65 mm via lands now connect the battery boost output to the handheld regulator input, amplifier input, power-button bias, backup converter input and DCDC4 input. Four 0.30 mm branches bring VSYS to IN_BIAS, IN_DCDC1, IN_DCDC2 and IN_DCDC3. All nine checked supply endpoints now pass CAM. Local input bypass, distribution losses at load and source changeover still require verification.

The L4 LS1 pour extends to Y = 35 mm. Run `python checks/estimate-ls1-pours.py dist/index.circuit.json board.zip` to measure the two copper islands from the artwork and drilled holes. At 35 µm and 20 °C the 0.025 mm grid estimates 11.477 mΩ total, or 3.443 mV at 300 mA. The 0.030 mm grid gives 11.580 mΩ. The earlier Y = 31 mm layout gave 13.502 mΩ on the 0.025 mm grid before the new VSYS trunks. With the widened feed, modeled barrels and equally loaded CPU balls, E5 screens about 9.5 mV below the 1.283 V minimum at the 300 mA corner. Ground-return and transient losses remain to be added. The calculation assumes equipotential via lands and provisional foil and plating.

TI gives a 250 mA worst-case estimate for the processor VDDS_DDR domain in Table 5-10, note 1. Run `python checks/screen-ls1-drop.py dist/index.circuit.json --pour-mohm 11.4768` with the resistance from this export. At 250 mA the provisional 110 mΩ switch model leaves 12.5 mV for the board. The modeled board drop is 13.72 mV at E5, leaving a 1.22 mV deficit before return, ripple and transient losses. The 110 mΩ specification is at 1.35 V, 300 mA and DDR3L at 333 MHz. These are screening conditions. Workload current, effective capacitance and behavior across frequency and temperature remain unmeasured. [AM335x datasheet, Table 5-10](https://www.ti.com/lit/ds/symlink/am3354.pdf) · [TPS65218D0 electrical characteristics](https://www.ti.com/lit/ds/symlink/tps65218d0.pdf)

A second L3 feed runs from the LS1 output barrel to a 0.30 mm drill on the lower bypass bank. It widens to 5 mm in open space. The direct L4 path from that landing to the CPU via measures 10.507 mΩ at 35 µm and 20 °C on a 0.025 mm grid. The original distribution remains connected. Run `python checks/screen-ls1-drop.py dist/index.circuit.json --pour-mohm 11.4768 --direct-pour-mohm 10.5067`. Screening the direct path alone gives 0.711 mV above the processor minimum at 250 mA with 35 µm foil at 20 °C, falling to 2.068 mV below at 80 °C. With 17.5 µm inner foil at 20 °C it falls 0.055 mV below. At 300 mA even the 35 µm, 20 °C case falls 7.146 mV below. These calculations exclude ground return, package drop and transient losses.

The four-sheet solve uses both L3 and L4 paths, their shared copper and the four intervening plated barrel sections. Reproduce it with `python checks/estimate-ls1-pours.py dist/index.circuit.json board.zip --joined` and pass its output file to `checks/screen-ls1-drop.py --sheet-network-report` alongside the board JSON. At 35 µm inner foil the L3 source land to L4 CPU land models 10.856 mΩ at 0.035 mm grid pitch and 10.701 mΩ at 0.025 mm. Including the common traces and plated depths gives 44.218 mΩ to E5 with 35 µm copper at 20 °C. The 250 mA screen leaves 1.445 mV at 20 °C and misses the minimum by 1.161 mV at 80 °C. At 300 mA it misses by 6.265 mV at 20 °C. The 100 mA, 1 µs load-step example consumes 4.35 mV at 23 µF effective capacitance before ESR, ESL and ground-return losses. [Copper solve](checks/current-ls1-pours.txt) · [Processor supply budget](checks/current-ls1-budget.txt)

The native PCB checker and the independent same-net copper audit both clear the four corrected DDR bends. The local PMIC feedback, RTC switch and joystick ADC supply traces also clear their native endpoint checks. Whole-board opens and bus constraints remain.

The byte-0 and byte-1 planar spreads measure 6.269 and 1.333 mm against the 0.635 mm limit. With 1.53 mm per full-depth transition the estimated spreads are 6.269 and 3.128 mm. Clock, DQS0 and DQS1 planar mismatch measures 0.095, 0.110 and 0.090 mm against 0.127 mm. A0 and A3 now measure 28.632 and 28.650 mm, inside the address/control window of 28.550 to 31.090 mm. A10 measures 39.232 mm and CKE measures 33.841 mm. D12 and D14 measure 23.843 and 23.459 mm against a 23.000 mm planar upper bound. D8 has four full-depth transitions and becomes the worst byte-1 signal when the provisional barrel depth is included. The provisional length screen that counts 1.53 mm per L1–L4 traversal places all 22 byte signals and 26 of 27 clock/address/control signals outside their nominal window. The uniform-line sensitivity calculation uses 5.884 ps/mm for isolated traces, 5.739 ps/mm for a nominal odd-mode pair, and 6.596 ps/mm for an illustrative homogeneous barrel dielectric with relative permittivity 3.91. With the observed via counts, byte-0 D7 and byte-1 D8 give the largest modeled data-to-strobe differences. Reproduce the two strobe scenarios with `checks/audit-lengths.py dist/index.circuit.json --through-span-mm 1.53 --delay-rates 5.884 5.739 6.596`. These scenarios omit package, launch and local field effects. An electrical delay model for the actual stackup, BGA launches and packages is still required. The engineering export contains 221 fitted references. The assembly orientation screen flags six references for review. The plated-span audit finds zero missing transitions. The four raster connector ground contacts reach L2. All 24 RGB888 source assignments follow TI SPRZ360 Figure 2; pixel clock, data enable, sync signals and reset have new source assignments. Remaining raster signals, panel bias and LED drivers, touch flex, system power, boot-strap copper and the fabrication package remain open.

LCD_D11, D13, D14, D15 and the pixel clock now have continuous copper from the AM3354 to the display connector. All five pass the full-width adjacent ground check outside their own via antipads. Run `python checks/audit-ddr-reference-planes.py dist/index.circuit.json --raster --full-width` to reproduce the check. The physical connectivity audit finds 35 of 77 tracked handheld connections complete. Panel timing and power remain open.

Three 100 nF return capacitors connect L2 ground to the L3 DDR supply beside the channel. Across 120 top-to-bottom DDR transitions, the worst center distance to the farther via of the nearest reference capacitor is 9.504 mm at ODT. The switched processor capacitors supply a different rail and cannot bridge the RAM reference to ground. This geometry measurement informs return-path review. Capacitor ESL, spreading inductance and discontinuities still need electrical evaluation. Moving the bulk C_DDR34 supply via 0.10 mm placed its entire land inside L3 copper. Moving the N10 ground via 0.010 mm restores complete L2 land coverage. The local escape check passes at 71 terminals on 70 blind vias.

The two Omron B3F-3152 shoulder switches now use contacts 1 and 2. The copper check verifies that contact 1 reaches the assigned CPU ball and that contact 2 and both case tabs reach ground. Both footprints match the Omron 4.5 mm contact pitch, 7 mm tab pitch and exported orientation. The JLCPCB C231320 library uses a 7.62 mm tab pitch and labels the bonded tabs in the opposite order, so supplier assembly review remains open. [Omron B3F datasheet, page 5](https://omronfs.omron.com/en_US/ecb/products/pdf/en-b3f.pdf)

The TPS65218D0 DCDC1 (CORE) and DCDC2 (MPU) switch nodes now reach their respective 1.5 µH inductors on the top layer. Each output reaches its 47 µF capacitor and feedback input. Four blind vias per capacitor connect its return to L2. Two joystick traces and the Start and Right button traces clear both filters. Run `python checks/audit-vref.py dist/index.circuit.json --processor-filters --joysticks` to check these copper connections and the CPU ball assignments. Distribution from both filters to the CPU and the regulator input power paths remain open.

The revised D12 escape clears SYSBOOT11, SYSBOOT13 and SYSBOOT15. The four-width setback screen now reports zero findings, including after routing three additional raster signals. The setback screen measures unrelated routed traces and vias against the actual DDR trace copper on each outer layer. The full enclosing DDR keepout requires a separate region review. [Setback findings](checks/current-ddr-setback.csv) · [TI AM335x datasheet, Table 7-63 and Figure 7-51](https://www.ti.com/lit/ds/symlink/am3354.pdf)

The 50 rendered DDR signals use 0.102 mm copper. On the provisional JLC04161H-1080 geometry, a two-dimensional coated-microstrip calculation gives 54.16 Ω for an isolated trace and 99.26 Ω differential for parallel traces with a 0.18 mm edge gap. The corresponding delays are 5.884 and 5.739 ps/mm. Run `python checks/estimate-ddr-impedance.py dist/index.circuit.json` to reproduce the 0.002 mm mesh result. A 0.003 mm mesh gives 54.99 and 99.42 Ω. These estimates assume 0.0764 mm dielectric, relative permittivity 3.91, 0.035 mm rectangular copper and solid adjacent reference. Pair escapes, via discontinuities, fabrication tolerance and the actual HDI build still require verification. [JLCPCB reference stackups](https://jlcpcb.com/impedance) · [JLCPCB HDI capabilities](https://jlcpcb.com/help/article/hdi-pcb-capabilities-faq)

CPU D3 now connects to RAM DQ7, and CPU D7 connects to RAM DQ3. Both use the low byte's original mask and strobe pair. This shortened D3 from 23.720 to 22.535 mm and D7 from 24.587 to 23.411 mm without changing their via counts. D5 remains the limiting byte-0 data signal. Run `python checks/check-ddr-pinmap.py dist/index.circuit.json` to verify the permutation and the fixed address, control, mask, clock and strobe functions. [TI on AM335x DDR3 data-bit mapping](https://e2e.ti.com/support/processors-group/processors/f/processors-forum/1223941/am3359-ddr3-swapping-data-lanes)

All 16 SYSBOOT resistors now have routed bias-side pads. Bits 0, 1, 2, 4 and 14 share copper with the PMIC I²C pull-up supply pads, and the eleven low straps reach L2 ground. The five high pads still need an energized 3.3 V I/O supply, and the processor-side strap connections require completion. The source decoder reads 0x4017. Verify the two bias nodes with `checks/audit-vref.py --control-bus --retained-returns` and the strap word with `checks/check-sysboot.py`, passing the assembled circuit to each.

The AM3354 warm-reset ball A10 now reaches TPS65218D0 GPIO3. The PMIC interrupt reaches its pull-up, and the new PGOOD pull-up shares its I/O-side copper. Two DDR bypass bodies moved 0.35 mm while their plated returns stayed in place. The L3 outline leaves room for the CPU reset escapes. The current audit checks both supply domains independently and verifies the bypass returns to L2. The exported copper now connects cold-reset PGOOD to B15. Backup reset and regulator input and load distribution still require copper. [TI TPS65218D0 power guide, Figure 7 and Section 12](https://www.ti.com/lit/ug/slvuaa9b/slvuaa9b.pdf)

[Current PCB snapshot, top and bottom copper](previews/handheld.png) · [Current DDR timing measurements](checks/current-timing.txt)

I²C0 now reaches the PMIC, joystick ADC and both pull-ups from the processor. The clock escape uses a local recess in the L3 DDR island, and the audio PWM trace still reaches its input resistor. Run `python checks/audit-vref.py dist/index.circuit.json --control-bus` to verify the two bus nodes. Both pull-ups still depend on completion of the sequenced I/O supply.

This branch builds a **232 × 82 mm single four-layer PCB** for the wider handheld. The d-pad, face buttons, shoulders and joystick connectors moved into the fixed side grips. Start and Select sit below the main controls. Nine modeled controls clear the centered 164.9 × 100.0 mm bare BuyDisplay ER-TFT070A2-6 panel envelope in plan view. The full display assembly, cover lens, bezel, FPC bend and replacement rear shell still require integration. The raster connector is assigned to the 7-inch panel. Bias, scan straps and the constant-current backlight driver still require integration.

The placement pass removes 20 displaced control traces and records each as an open. DDR copper and component centers stay fixed. The all-layer Gerber shorts check passes and the placement-stage via clearance count was 25. The smaller case, battery tub and running design history are preserved on [am3354-production](https://github.com/Abse2001/pixel-dash/tree/am3354-production). No fabrication release has been made.

The DDR address-reference route now clears four more vias at its original 0.4 mm width. Moving the C_DDR34 bulk bypass 0.10 mm clears the adjacent D12 trace. A four-via chip-select route brings the DDR channel to 40 of 50 signals connected. Shifting the F5 and K5 DDR supply escapes clears A13 and D5 on bottom copper. A shorter D5 route reduces its length from 49.892 to 32.066 mm and the routed byte-0 spread from 35.711 to 17.885 mm. The integrated 6 mil audit lists 17 remaining findings. The VREF bypass and all-layer Gerber shorts checks pass.

The [runtime budget](power/runtime-budget.md) sizes candidate packs at 75% backlight PWM. The keyed PCB battery header uses contact 1 for BAT and 2 for GND. A battery-specific mating check is required once a supplier is selected. [BuyDisplay panel](https://www.buydisplay.com/7-inch-1024x600-ips-tft-lcd-display-high-brightness-full-viewing-angle)

## Earlier compact design checkpoints


AM3354 handheld with a 1 GiB Micron DDR3L, four-layer HDI board and the existing LiPo tub. Engineering development only.

The retained handheld was extracted from checkpoint `5b7d96d`. The coupled DDR channel starts at `611f7d9`. The original dual-RP2350 hardware and historical routing branches are separate fallbacks.

The first production checkpoint removes 91 old processor and support designators. The peripheral snapshot omits ground pours pending integration. Nine local trace edits eliminate the nine 6 mil via-to-unrelated-trace findings on this retained subset. Future work on the integrated board must rerun the audit including the AM3354 and memory.

`python production/build_retained.py /tmp/retained.circuit.json` materializes the retained copper. Run `python checks/audit-via-clearance.py /tmp/retained.circuit.json` with Shapely 2.

## Integrated engineering build

Install Bun and Python with Shapely 2. Run `bun install --frozen-lockfile` and `bun run build`. The production design entry is `dist/index.circuit.json`. The build renders the editable processor/memory circuit and combines it with the retained handheld. It keeps the LiPo enclosure, board notch and three NTC cutouts. Legacy ground pours require regeneration with finished system routing. The initial imported L2 ground was limited to the DDR region.

The original integrated checkpoint has 46 source-level links for the panel, controls, MMC0, USB0, PWM audio and backlight. Their PCB copper is outstanding. The ILI9488 selects 16-bit DBI Type B on IM2:0 = 010. Firmware must select this mode before panel reset release. LCDC LIDD uses the 16 data pins, PCLK for RD, HSYNC for WR and VSYNC for D/C. Panel CS is strapped low. The SYSBOOT resistor network, read-strobe pull-up and the behavior of the panel during strap sampling still require integration. [ILI9488 Table 1](https://www.displayfuture.com/Display/datasheet/controller/ILI9488.pdf) · [TI AM335x TRM, Table 13-6 and Chapter 26](https://www.ti.com/lit/ug/spruh73q/spruh73q.pdf)

The first combined export passed the all-layer Gerber shorts check. The BOM and pick-and-place each contain 183 designators. Run `python checks/check-removed-parts.py dist/index.circuit.json engineering.zip` to verify removed-part identities and placement absence. Of the 50 DDR links, 39 have copper. The independent whole-board 6 mil audit finds 87 DDR findings. The build's absence of a native skew message does not certify timing. Use the independent length audit. Assembly rotations, full power and peripheral circuitry, routing, plane returns and fabrication signoff remain open.

The next copper checkpoint removes 40 DDR via-edge clearance findings with local trace edits. The combined audit now lists 47 findings. The CAD checks on the revised channel report the same 11 missing signals, their corresponding opens, and two byte-skew errors. All three VREF bypass paths pass the copper connectivity audit. See `checks/current-clearance.csv` and `checks/current-timing.txt`.

The production source now includes sixteen 10 kΩ SYSBOOT straps. Five pull up to the planned sequenced 3.3 V I/O domain and eleven pull down to ground. Each sense terminal shares its corresponding LCD data signal. The pin-level check decodes 0x4017 from the built netlist. The 24 MHz clock source, sequenced rail, power-on reset and physical strap routing still need verification. Run `python checks/check-sysboot.py dist/index.circuit.json`. [TI boot configuration, Table 26-7](https://www.ti.com/lit/ug/spruh73q/spruh73q.pdf)

Moving 14 signal vias within their existing escape routes reduced the combined 6 mil count from 47 to 31. The three coupled pairs retained their original vertices. The independent length audit has the same out-of-window signals and reported skew, the VREF copper check passes, and the integrated Gerber shorts check passes.

The 24 MHz OSC0 uses JLCPCB C439045 with a 12 pF specified load, two provisional 15 pF C0G capacitors, a fitted zero-ohm drive link and an unpopulated 1 MΩ evaluation resistor. All seven signal traces are on top copper. The two case lands, both load capacitors and VSS_OSC each reach L2 ground through a local blind via. Run `python checks/check-oscillator.py dist/index.circuit.json`. The integrated Gerber shorts check passes and the 6 mil audit remains at 31 findings. BOM and placement each contain 203 fitted references. Crystal startup margin, effective load and frequency require prototype measurements. [TI AM335x datasheet, section 6.2.2.1 and Figure 6-9](https://www.ti.com/lit/ds/symlink/am3354.pdf) · [JLCPCB crystal listing](https://jlcpcb.com/partdetail/437836-S3B24000000F1210F30/C439045)

The touch-capable panel connector now maps FPC44 and FPC45 to I2C1 on D15/D16 (mode 3), and FPC46 to GPIO1_17 on V14. The retained three pull-ups share the respective connector nets. microSD mechanical card detect uses C15 in mode 5 and is separate from DAT3. These four connections still require copper. The retained pull-up supply must be reviewed together with processor I/O power sequencing. Run `python checks/check-panel-storage.py dist/index.circuit.json`. [TI AM335x ZCZ pin attributes](https://www.ti.com/lit/ds/symlink/am3354.pdf) · [BuyDisplay FPC assignment](https://www.buydisplay.com/download/manual/ER-TFT035IPS-6_Datasheet.pdf)

## Momentary power control

The integrated board replaces the slide switch and its two battery hard-off gates with the ALPS SKRTLAE010 momentary key (C110293) and the TPS65218D0PHPR (C2659099). The two battery converters retain their input protection, USB interlocks and undervoltage control. The PB contact and its bias branch have saved top copper. The PMIC-to-processor controls are present in the netlist. Regulator filters, power distribution, sequencing, standby current and system connections still need qualification. In particular, the inherited USB supervisor inhibits the battery converters on valid VBUS. Aggregate USB draw requires a power-path review.

The PMIC recognizes a 600 ms press for cold start. During operation firmware can use the PB status interrupt for a shutdown request, flush the microSD and release RTC_PMIC_EN. Holding the button for the PMIC hardware timeout initiates a reset (8 seconds by default, 15 seconds when configured). Firmware and button timing have yet to be tested on hardware. [TI TPS65218D0 sections 5.3.1.15 and 5.4](https://www.ti.com/lit/ds/symlink/tps65218d0.pdf) · [TI AM335x PMIC guide](https://www.ti.com/lit/ug/slvuaa9b/slvuaa9b.pdf)

The separate push cap in `mechanical/power-button.scad` fits through the existing slider slot from inside the case. At the nominal CAD dimensions the cap reaches the supplier's 0.2 mm stroke with 0.25 mm of inward travel. Shell clearance at rest is 0.204 mm. The stroke, return and print tolerances require a physical fit test. Export the SCAD to STL and run `checks/check-power-button-fit.py` with the STL, the C110293 supplier OBJ and the original handheld checkout.

Run `checks/check-power-button.py` against the built circuit. The BOM and placement export contain 202 fitted references. The slide, two slide CAD bodies and five dedicated battery-control components have been added to the retirement inventory. The four-layer JLCPCB geometry remains provisional. Fabrication signoff is on hold pending the actual stackup.

Six DDR ground escapes now end on L2. The CPU H6/H7/G8, RAM D8/E8/T1 and C_DDR12 ground lands reach the solid reference plane, including the shared via for RAM D8/E8. The whole-board 6 mil audit falls from 31 to 25 findings. Signal routes and length measurements are unchanged. The integrated shorts check passes. Run `checks/check-local-ddr-returns.py` on the production circuit and `checks/audit-channel-drills.py` on the same circuit and its Gerber ZIP. The drill audit covers plated and nonplated round holes and all six connector slots, including both endpoints of each G85 command.

Run `python checks/audit-ddr-reference-planes.py dist/index.circuit.json` to screen the routed outer-layer DDR centerlines against the finished L2 ground and L3 DDR supply polygons. The report excludes the nominal launch and landing antipad distances. Review each uncovered span and verify high-frequency return paths and local layer-transition bypass separately.

I2C0 now has two 2.2 kΩ pull-ups (JLCPCB C2906920) at the TPS65218D0. Both resistors tap the planned sequenced 3.3 V I/O rail. The two PMIC signal branches and the connection between the resistor supply pads have top copper. The long SCL/SDA connections to the processor, sequenced rail distribution, bus capacitance and rise time still require verification. [TI AM335x power guide, section 12](https://www.ti.com/lit/ug/slvuaa9b/slvuaa9b.pdf)

R_DDR_VSEL (JLCPCB C281773, 12.1 kΩ ±0.1%) selects 1.35 V at PMIC startup. The DC34_SEL pin has a top copper branch to the resistor. Its ground terminal now has a blind via into L2. The DCDC3 switching stage, rail distribution and startup measurement remain open. [TI memory voltage selection, table 5](https://www.ti.com/lit/ug/slvuaa9b/slvuaa9b.pdf)

The integrated L2 ground plane now extends into both fixed grips and the PMIC region. It retains antipads around unrelated vias and slots, and clears the routed NTC breakaway. Run `python checks/check-main-ground.py dist/index.circuit.json` to check the main contour and retained vias. The exported Gerber shorts check passes across all four layers. The DDR centerline coverage findings and layer-transition return paths still need individual review.

The exposed PMIC pad has 25 plated 0.254 mm holes into the main ground plane. Two inherited 0.8 mm L3 supply traces pass around the via field with their original endpoints. The separate 6 mil audit remains at 17 findings. The exported drills match 415 through holes on the plated L1–L4 file plus six slots, and the complete Gerber shorts check passes. Fabricator confirmation of the under-pad via finish, paste design and thermal performance is pending. [TI TPS65218D0 layout guidelines, section 8.1](https://www.ti.com/lit/ds/symlink/tps65218d0.pdf)

The DDR signal through vias use a 0.20 mm mechanical drill and a 0.35 mm copper pad. At the provisional 1.6 mm board thickness the drill aspect ratio is 8:1. JLCPCB publishes a 16:1 HDI maximum and a minimum 0.10 mm difference between pad and through-hole diameters. This size uses its small-via pricing option. The integrated 6 mil audit drops from 17 to four findings and the all-layer Gerber shorts check passes. [JLCPCB HDI capabilities](https://jlcpcb.com/help/article/hdi-pcb-capabilities-faq) · [JLCPCB mechanical via sizes and pricing options](https://jlcpcb.com/capabilities/pcb-capabilities)

The N9 RAM supply escape, processor VTP calibration via and RAM VREFCA escape now clear the remaining four via-to-trace findings. On this 40-signal checkpoint the board-wide 6 mil audit reports zero failures. The native VREF bypass connectivity and all-layer Gerber shorts checks pass.

Ground escapes from the top BGA lands now terminate directly at L2. Each bypass capacitor has a blind via on the terminal facing its adjacent reference plane (top ground to L2 or bottom DDR supply to L3). The 83 additional shortened vias release copper on the opposite side. The pad-to-plane audit verifies 90 terminals through 89 laser vias, including one shared escape. The 6 mil audit and all-layer Gerber shorts check pass.

Run `python checks/audit-via-hole-spacing.py dist/index.circuit.json` for the separate drill-to-drill test. It checks 0.20 mm between mechanical vias and the published blind-via limits of 0.13 mm on the same net and 0.24 mm on different nets where spans meet. Coaxial same-net stacks on adjacent drill spans require fabrication review. This checkpoint passes both the drill-spacing test and the 6 mil copper-edge test. [JLCPCB HDI rules](https://jlcpcb.com/help/article/hdi-pcb-capabilities-faq) · [JLCPCB mechanical drill spacing](https://jlcpcb.com/capabilities/pcb-capabilities)

Run `python checks/measure-ddr-pair-spacing.py dist/index.circuit.json --center-distance-mm 0.42` to locate layers where CK or DQS conductors separate from their mates. The report measures both conductors along their full planar routes, including package escapes. The 0.42 mm center distance reproduces the earlier layout comparison. It is a diagnostic threshold. Differential impedance and allowed uncoupled escape lengths still require stackup and timing verification.

Run `python checks/check-through-via-sizes.py dist/index.circuit.json --board-thickness-mm 1.6` to screen each mechanical through via for a 0.15 mm minimum hole, 0.10 mm pad diameter allowance and 16:1 maximum aspect ratio. The thickness is provisional. Blind and buried via aspect ratios depend on the fabricator's buildup and core thicknesses. [JLCPCB HDI capabilities](https://jlcpcb.com/help/article/hdi-pcb-capabilities-faq)

Run `python checks/audit-integrated-trace-spacing.py dist/index.circuit.json` to check the 0.102 mm copper gap between traces in the processor circuit and retained handheld traces on the same layer. This check caught a PMIC supply branch approaching a joystick trace outside the processor-only render.

The length audit accepts `--through-span-mm 1.6` to estimate total geometric spread when existing DDR signals make different numbers of L1–L4 traversals. It reports this alongside the planar routing limits and rejects partial-depth vias in this mode. Replace the provisional span with the actual outer-copper separation when available. Electrical delay also depends on the stackup, pad capacitance and via structure.

Run `python checks/audit-copper-contacts.py dist/index.circuit.json` in addition to the Gerber shorts check. It intersects actual trace strokes, via lands, SMT pads, plated-hole lands and finished pours on every occupied layer, compares them to schematic net identities and reports the two copper object IDs. It also checks electrically unassigned lands. On the earlier 44-signal trial it independently identified two contacts from the retained joystick trace into the PMIC pull-up pads. The 6 mil via-edge audit and manufacturing clearance checks remain separate.

The earlier wide engineering layout routed 44 of 50 DDR signals. D1, DQM0, CKE and RESETn have stored paths. D2 and D11 moved to make room for DQM0. D5, D12 and D13 now have continuous reference coverage under the audit's launch/landing assumptions. A8 meets the planar address/control window. Mechanical DDR signal vias use 0.15 mm drills and 0.30 mm pads. Their provisional 1.6 mm through-span gives a 10.67:1 aspect ratio. [JLCPCB HDI capabilities](https://jlcpcb.com/help/article/hdi-pcb-capabilities-faq)

The PMIC pull-ups sit horizontally and the manual supply trace passes clear of both joystick signals. Each momentary-key ground contact has its own top trace and blind via to L2. The all-layer Gerber shorts check and independent filled-copper intersection report are clear. The board-wide 6 mil check, via drill spacing, spacing between new and retained traces, all 90 audited DDR reference landings and VREF bypass connectivity pass. The drill files match the board and 205 fitted references appear in each assembly table. Preserve the 40-route fallback at 8000ab8.

At that 44-signal checkpoint A0, A1, A7, D0, D8 and D14 were open. Skew, absolute lengths and reference-plane gaps remain in the saved measurements. System power sequencing, display, storage, full-board connectivity, pick-and-place orientation, enclosure fit and fabrication stackup signoff remain open. This checkpoint is for engineering review.

Run `python checks/check-ddr-bypass-placement.py dist/index.circuit.json` after moving a DDR capacitor. It checks the fitted high-speed parts, nominal capacitance and distance from each capacitor center to the nearest relevant supply and ground balls. The CPU has 20 capacitors totaling 2.00 µF, with a worst distance of 7.725 mm against 10.16 mm. The RAM has 12 totaling 1.20 µF, with a worst distance of 3.493 mm against 3.81 mm. The four bulk capacitors are excluded from those totals. Verification of effective capacitance and layer-transition return current is separate. [TI AM335x DDR3 high-speed bypass specifications](https://www.ti.com/lit/ds/symlink/am3354.pdf)

Add `--ddr-power` to the VREF audit to check physical copper connectivity from all AM3354 VDDS_DDR and VSS balls, RAM VDD/VDDQ and VSS/VSSQ balls, and both ends of every DDR bypass capacitor. On the verified wide checkpoint, 61 terminals reach L3 VDDS_DDR and 95 reach L2 GND. This checks continuity into the planes. PMIC rail generation and sequencing require separate verification.

The filled-copper audit also accepts `--clearance-mm 0.102` to report near misses between unlike nets, including pad-to-trace and trace-to-trace gaps. On the 44-signal layout, the contact check passes and this tighter screen identifies 11 sub-limit pairs, with the smallest measured gap 0.1007474 mm. These are open clearance findings. The separate 0.1524 mm via-edge rule also applies.

Use `python checks/audit-vref.py dist/index.circuit.json --ddr-power --ddr-signals` to walk actual copper between each pair of processor and memory lands across traces, plated transitions and layers. The signal check requires 50 distinct connected nodes and rejects connections into the DDR supplies or references. It identified all six open nets on the earlier 44-signal layout.

Run `python checks/check-ddr-gerber-strokes.py dist/index.circuit.json engineering.zip` to match every saved DDR segment to a dark circular-aperture draw of the same width on the correct exported copper layer. The positional allowance is one Gerber coordinate unit (1 nm). The complete routing trial matched all 3,640 segments. Deleting one draw from a test copy identified the affected DQSn1 segment.

Run `python checks/audit-ddr-self-contacts.py dist/index.circuit.json` after manual length tuning. It screens contacts between parts of the same path, including via lands and narrow return bends. The check identified three BA0 bends where copper overlapped beyond the local bend allowance. Beveling these bends cleared all three findings on the saved layout. A same-net shortcut can reduce effective delay even when all signals are isolated.

The 7-inch bare panel and the previous display use incompatible connector assignments. On the inherited J_LCD wiring, contacts 41 and 42 share a rail. The new panel needs +18 V and −6 V there. Its AVDD contact 43 is grounded, and reserved contact 45 is wired. Run `python checks/audit-panel-bias.py dist/index.circuit.json` during the display migration. The current design has eight ground, supply, LED and no-connect topology findings. This check covers schematic grouping and isolation. Rail voltage, sequencing, rated load, flex orientation and the separate touch flex still need verification. [BuyDisplay panel specification, sections 3.3 and 4.1–4.4](https://www.buydisplay.com/download/manual/ER-TFT070A2-6_Datasheet.pdf)

The physical connectivity audit accepts `--system-io` to walk the handheld interface and SYSBOOT connections between their actual lands. At the start of peripheral routing, all 66 have schematic assignments and none has a complete copper path. The individual terminal pairs are printed on failure.

Four SYSBOOT sense lines now have saved top-layer copper from the AM3354 balls to their strap resistors. The physical system audit verifies four of the 66 system connections. On the combined board all 50 DDR links remain isolated, the 0.102 mm copper and 0.1524 mm via-edge clearance checks pass, and the all-layer Gerber shorts check passes.

MMC0 clock and DAT1 now reach the microSD connector on top copper. The complete interface and SYSBOOT continuity count is six of 66. The clock measures 84.83 mm and DAT1 measures 103.67 mm in this first placement. The other card contacts, matching, return paths and SD clock operating margin are open. Both clearance checks and the all-layer Gerber shorts check pass with these traces installed.

Run `python checks/check-placement-export.py dist/index.circuit.json engineering.zip` to compare every fitted reference, side, centroid and rotation with the exported placement file, and compare assigned JLCPCB codes with the BOM. All 205 fitted references match on the wide board. A test that rotated only the memory in the exported table was detected. Supplier placement-library zero angles, pin-one orientation in the assembler preview and connector mating direction still require reconciliation.

L3 now has a ground fill outside the DDR supply island to provide a return for bottom-side handheld signals. The island's eastern edge moved 3.8 mm toward the RAM. All 61 supply terminals still connect to VDDS_DDR, all 95 audited grounds connect to GND, and the DDR reference screen passes. The connected L3 ground covers 17,120.8 mm², clears the reserved supply island by 0.160 mm, and shares 32 complete plated via lands with L2 ground. Run `python checks/check-main-ground.py dist/index.circuit.json --both`. The whole-board Gerber and independent copper clearance checks pass.

The MMC0 clock and DAT1 traces now avoid the ground-plane gaps on their earlier top routes. The finished-plane screen dropped from 2.178 mm uncovered on clock and 0.564 mm on DAT1 to zero on both. Use `python checks/audit-ddr-reference-planes.py dist/index.circuit.json --micro-sd` to screen the populated card routes against L2 and L3 ground as routing progresses.

MMC0 DAT0, DAT3, CMD and card detect now reach their card contacts. The independent copper walk verifies six of seven card lines and ten of 66 handheld connections. The two outside copper layers carry these routes. The card-route ground coverage screen, 0.102 mm copper clearance, 0.1524 mm via-edge clearance, drill-spacing and all-layer Gerber shorts checks pass on this checkpoint.

Run `python checks/audit-ddr-class-spacing.py dist/index.circuit.json` to measure cumulative closely spaced centerline length for each clock, address/control and byte-lane signal. Overlapping intervals on a trace count once. The longest cumulative closely spaced length is 19.502 mm on WEn against a 31.750 mm allowance. All 49 screened signals pass the one-width minimum in this layout. Differential mate spacing and return-current continuity require separate checks. [TI AM335x datasheet, Tables 7-68 and 7-69](https://www.ti.com/lit/ds/symlink/am3354.pdf)

MMC0 DAT2 completes the seventh card signal. The physical continuity audit now verifies all six electrical bus lines plus mechanical card detect and 11 of 66 total system connections. All routed card traces pass the adjacent ground coverage check. The board-wide copper, via-edge, drill-spacing and all-layer Gerber shorts checks pass. Local return stitching and interface timing are separate from this continuity result.

Sixteen new ground vias link the two ground planes near the MMC0 signal layer changes. Run `python checks/check-main-ground.py dist/index.circuit.json --both --mmc0` to verify the complete via lands on both finished planes and measure the nearest ground return at each transition. Across all 18 transitions, the maximum center-to-center distance decreased from 40.951 mm to 1.270 mm. The four-layer export includes all 400 plated through drill hits and six plated through slots. All 3,967 DDR copper strokes still match the Gerbers.

Left joystick click now connects AM3354 T12 to J_JOY_L contact 3 through two plated transitions. Twelve of 66 system connections have verified continuity. All seven card connections and all 50 DDR connections remain continuous, and whole-board clearance and Gerber shorts checks pass.

Run `python checks/audit-copper-outline.py dist/index.circuit.json --clearance-mm .20` to measure copper against the routed perimeter and internal cutouts, including the battery tub geometry represented by those cuts. All four copper layers clear the 0.20 mm screening distance and stay within the substrate. This screen measures nominal CAD geometry before router tolerance.

The PWM audio path now runs from AM3354 A17 to the input resistor of the retained amplifier. The populated board passes the 0.102 mm copper and 6 mil via-edge audits, and the Gerber shorts check. Thirteen of the 66 system links have pad-to-pad copper. Audio output level, filtering, grounding under load and speaker operation still require verification.

The PMIC internal LDO has a dedicated 1 µF Samsung CL10A105KB8NNNC (JLCPCB C15849). The copper walk verifies pin 35 to the capacitor and its opposite land to the L2 ground plane. Removing the positive trace in a test copy produces an open. Run `python checks/audit-vref.py dist/index.circuit.json --pmic-hold`. TI uses this capacitor to hold up the sequencer during input power loss. Effective capacitance and power-down waveforms require hardware verification. [TI TPS65218D0, section 5.3.1.6](https://www.ti.com/lit/ds/symlink/tps65218d0.pdf)

Manual length adjustments with the existing vias fixed reduced byte-0 spread from 12.559 to 7.214 mm and byte-1 spread from 12.215 to 9.977 mm. Seven of 27 clock/address/control signals remain outside the nominal length window, down from 16. The 0.635 mm byte target remains open. Four nonlocal same-net contacts found in the trial were removed by beveling the returns before saving this checkpoint. Whole-board unrelated-copper clearance, via-edge clearance, DDR reference coverage and Gerber shorts checks pass.

The PMIC backup converters use the main system supply with the unused coin-cell input grounded. IN_BU has a dedicated 4.7 µF C19666 input capacitor and SYS_BU a 1 µF C15849 capacitor. Run the copper audit with `--pmic-backup --pmic-hold` to verify the local connections and ground returns. The upstream VSYS feed and the DCDC5/6 output networks remain open. [TI TPS65218D0, Figure 6-1](https://www.ti.com/lit/ds/symlink/tps65218d0.pdf)

With the data-lane layer changes fixed, the latest D9 adjustment and shorter paths on the long data lines reduce the byte spreads to 7.180 and 7.246 mm. Six of 27 clock/address/control signals remain outside their target. Independent same-net and unrelated-copper audits, actual plane coverage, all-layer Gerber shorts, drill matching and assembly-table checks pass.

Six controls now use mode-7 GPIO pads outside LCD_DATA18–23. Start, Select, the two shoulders and both stick clicks have continuous copper. The source assignments are A13/GPIO3_14, B12/GPIO3_18, B17/GPIO0_3, B13/GPIO3_15, V17/GPIO1_27 and D18/GPIO0_12 respectively. V17 belongs to VDDSHV3 and the other five to VDDSHV6. Both banks require a sequenced 3.3 V supply for these controls. The full-board copper walk verifies 18 of 66 assigned system links. Two top-layer shorts from an earlier combined routing trial were fixed before export. [TI AM335x Table 4-2](https://www.ti.com/lit/ds/symlink/am3354.pdf)

Relocating the PMIC backup input capacitor to the bottom and moving the hold-up capacitor 0.15 mm cleared three component overlaps. Run `python checks/audit-assembly-courtyards.py dist/index.circuit.json` to check the polygons on both sides. All 208 fitted courtyards clear one another. The copper walk confirms both capacitor connections and returns, and the placement export records the new side and rotation. VDDSHV3 and VDDSHV6 now share the sequenced 3.3 V assignment. Physical delivery of that rail is pending.

Use `python checks/check-ddr-gerber-strokes.py dist/index.circuit.json <export.zip> --all-traces` to compare each routed segment, layer and width against draws in the four manufacturing copper files. This complements the independent filled-copper contact and clearance audits, the drill comparison and the Gerber shorts check.

The four D-pad directions now reach their switch lands from V16/GPIO1_24, U16/GPIO1_25, C12/GPIO3_17 and D17/GPIO0_13. The copper walk finds 22 of 66 assigned system connections complete. The assembly export has 6,870 matching routed strokes, zero Gerber shorts and zero 6 mil via-edge findings. Extending the Up trace to the neighboring switch land in a disposable negative control produced a 0 mm unrelated-copper finding at that land.

Face button A connects through AM3354 V15 (GPMC_A5 in mode 7) to SW_A. The physical audit measures 23 of 66 system links connected. All four copper Gerbers and the board-wide copper clearance and via-edge checks pass on this revision.

The DDR centerline screen passes on the face-A checkpoint. A separate full-width screen projects the finished trace width onto the adjacent reference plane and excludes each trace's own nominal via openings. Run `python checks/audit-ddr-reference-planes.py dist/index.circuit.json --full-width`. On this checkpoint it reports 41 signal/layer combinations with some uncovered copper above 0.000001 mm². The largest is D14 on the top layer at 0.01660 mm². These findings require review against the finished antipad shapes during tuning.

All four face buttons now have pad-to-pad continuity. B, X and Y use M18/GPIO0_1, L18/GPIO3_10 and K18/GPIO3_9. VDDSHV5 joins the sequenced 3.3 V assignment. Across the board, 26 of 66 tracked system links reach their endpoints. Shortening D12 and D14 reduces byte-1 spread to 6.870 mm. A change at the D12 via restores centerline reference coverage. All four Gerbers pass the shorts and stroke comparisons, and the separate 6 mil via-edge and 0.102 mm copper screens have zero findings.

The TPS65218D0 DCDC5 and DCDC6 filters each use a 10 µH Murata LQM21FN100M80L (C162582) and a 47 µF Samsung CL31A476MPHNNNE (C96123). Each switch node reaches its own inductor. Each filtered output reaches its capacitor and its own feedback pin, and both capacitor returns reach L2. Run `python checks/audit-vref.py dist/index.circuit.json --rtc-filters --pmic-backup --pmic-hold`. Moving the FB6 via restored the 6 mil gap to the adjacent switching trace. All 212 courtyards clear, and the BOM, placements, drill files and copper Gerbers match the CAD. Delivery to the RTC supply balls and the CPU-local bypass still require copper. [TI TPS65218D0](https://www.ti.com/lit/ds/symlink/tps65218d0.pdf)

Manual tuning of A2 and A12 brings both into the address/control length window. Four of the 27 signals in that group still miss the window. Byte 1 now measures 5.407 mm of spread after adding length to D9. Runs that introduced same-net copper shortcuts were removed before export. The four-layer Gerber shorts, reference centerlines, independent copper clearance and 6 mil via-edge checks pass.

The four joystick filter outputs now reach separate ADS1115 analog inputs. The TI ADS1115IDGSR uses the sequenced 3.3 V I/O supply so that the existing 3.3 V sticks have a compatible input range. JLCPCB C37593 supplies the ADC, which has a local 100 nF bypass and a ground-strapped address of 0x48. The copper walk finds 30 of 70 tracked handheld endpoints connected, including the four filter-to-ADC links. The relocated stick connectors still need continuity through the upstream filters, and I2C0 and rail delivery require verification before joystick operation. [TI ADS1115](https://www.ti.com/lit/ds/symlink/ads1115.pdf)

Both joystick connectors now reach the four input filter resistors. All four filtered outputs reach their assigned ADS1115 channels. Run `python checks/audit-vref.py dist/index.circuit.json --joysticks` to check each side of each resistor, the ADC bypass and its I2C address strap. The added copper joins each retained axis trace at its original plated endpoint. SDA reaches the processor, PMIC and ADC. The processor's SCL connection still requires an escape.

The DCDC3 local filter uses a TDK SPM3012T-1R5M inductor (JLCPCB C3221570) and a 47 µF output capacitor. FB3 senses the output capacitor at its positive land. Four blind vias return the capacitor to L2. The momentary power-key trace changes layers to clear the regulator. The `--ddr-regulator` audit verifies both inductor terminals, the feedback connection, the capacitor return and the power-key circuit. The rail input, distribution to the processor and memory, and sequencing are still open. [TI AM335x power connection diagram, figure 1](https://www.ti.com/lit/ug/slvuaa9b/slvuaa9b.pdf)

This checkpoint has 216 fitted references and 7,265 routed copper strokes verified against the four Gerbers. The component courtyard, copper contact, 0.102 mm clearance, 6 mil via-edge, drill, copper shorts and CAD placement checks pass. JLCPCB library pin-one orientation is a separate assembly check. Large filled-plane exports in the current CLI require a larger Node stack, e.g. `node --stack-size=4096 <tsci-cli-entry> export dist/index.circuit.json -f gerbers -o engineering.zip`.

The independent JLCPCB placement screen compares numbered copper lands in the 74 selected supplier footprints to the board at each exported angle. Run `python checks/audit-jlcpcb-placement.py dist/index.circuit.json <export.zip>`. On the 216-part build, 210 match at their exported angle within 0.075 mm after centering the numbered lands. This tolerance screens library differences. J_USB uses a different pad numbering convention, and the two shoulders, volume potentiometer, legacy 3.3 V regulator and battery converter inductor differ in land geometry. Their assembly review remains open. This screen checks relative land geometry and rotation. Final assembly-origin offsets, JLCPCB preview and physical fit require separate verification.

The reference file records the selected JLCPCB order code, EasyEDA footprint UUID, SHA-256 of the source footprint data and neutral numbered land coordinates in millimeters. The inputs are the EasyEDA component records for those order codes, converted using `easyeda` 0.0.389. [Example supplier component record for the joystick ADC](https://easyeda.com/api/products/C37593/components?version=6.5.51)

Four restored blind ground vias connect the retained joystick filter capacitors to L2. The copper connectivity check with `--joysticks` includes the return of each filter. The engineering export matches 7,284 strokes across four copper files and all five drill files. Run `python checks/audit-route-transitions.py dist/index.circuit.json` to detect layer changes without a same-net plated conductor at the specified board position. This screen found 34 inherited transitions before these four repairs. The other 30 require repair or removal when their circuits are replaced.

Seven restored L1–L2 ground vias connect the speaker amplifier bulk return, PGND2, speaker connector ground, converter input capacitor and the two retained ground-side resistors to the main plane. The physical copper walk with `--retained-returns` verifies all six terminals. After these repairs 23 inherited transitions still lack matching plated spans.

Two detached tracks, pcb_trace_1161 and pcb_trace_1437, touched no surviving trace, via, component land or plane. Removing them drops the inherited missing-transition count to 19. The processor-to-amplifier PWM signal has its own saved route. The export now matches 7,212 strokes from 540 PCB traces.

The independent copper check reconstructs schematic nodes from connected source ports and named nets, then cross-checks PCB trace, pad and via net assignments. This catches inconsistent labels that could make two unrelated conductors appear to share a net. Deliberately merging two source net labels and mislabeling a routed via in separate test copies both triggered errors.

Reserved panel contacts 49 and 50 are isolated in the source, schematic and copper. The microSD bulk capacitor has a dedicated L1–L2 ground via in its pad. The `--retained-returns` screen walks from that pad to the main ground plane. All 50 DDR signals retain full-width reference coverage.

The approved wide-board lower mounts and rear-carrier bores are at X = ±70 mm, Y = −29 mm. The upper mounts remain at X = ±60 mm, Y = 31 mm. All four physical holes match the Excellon export. The original tub and compact shell are separate fallbacks.

All eleven low SYSBOOT bias terminals reach L2 ground. Two ground vias are offset to clear retained audio routing. The high-side bias, remaining processor sense connections and powered reset sampling still require verification.

The fixed component lands constrain the LCD_DATA0/SYSBOOT0 escape at U1.R1. Run `python checks/screen-ddr-placement.py dist/index.circuit.json` to reproduce the optimistic pad-only bound. With the current RAM placement, even the far edge of R1 lies just 0.334 mm from the convex hull of the CPU DDR lands and RAM lands, inside the 0.408 mm envelope setback. A hypothetical +1.0 mm RAM Y shift raises the upper bound to 0.527 mm. This screen ignores tracks, vias and landing width. A placement change would require a new 50-link route and reference audit.

### LDO1 input and physical boot-strap checkpoint

The added 0.24 mm VSYS feed joins IN_LDO1 to IN_DCDC2 through two plated
L1–L4 vias. Independent CAM walking confirms the input reaches the boost
output, sharing the supply with IN_BU, IN_BIAS and IN_DCDC1–4. IN_LS1
reaches the direct DCDC3 output. The LDO1 output still has 0/16 processor
loads connected. The input assignment follows TI SLVUAA9B Figure 1.

Run checks/audit-cam-connectivity.py with the assembled JSON, Gerber ZIP and
--cpu-power --pmic-controls --handheld-ground --sysboot. The 16 fitted
10 kΩ straps have the expected physical bias rails. Only bits 15, 14, 13
and 11 reach the corresponding CPU balls. The resulting reset word is
010?0??????????? (bit 15 first). Source decoding alone gives 0x4017.

The four-layer export retains 50 physically distinct DDR links and separate
CPU and memory power feeds. The 0.102 mm clearance, separate 6 mil via-edge
audit, short check, full-width DDR and envelope reference checks passed.
All 7,350 trace strokes matched the four copper files and all 221 placements
matched the assembly export. Whole-board CAM still finds 39 disconnected
mapped nets. Fabrication remains on hold.

### Supplier construction used for electrical screening

The engineering cross section is Würth Elektronik HDI4_1-2b-1_149_35_2V13,
revision 10/2023. Its drawing shows outer microvias on both faces, a buried
core and through plating. The supplier separately documents copper-filled
microvias and IPC-4761 Type VII filled and capped holes. The nominal finished
board is 1.491 mm including ENIG and mask, with ±10% board thickness tolerance.
The three dielectric intervals are 0.065, 1.200 and 0.065 mm. All four finished
copper layers are 0.030 mm. This gives 0.095, 1.230 and 0.095 mm between
adjacent copper centerlines and 1.420 mm from L1 to L4.

[Supplier buildup drawing](https://www.we-online.com/files/pdf1/en_hdi4_1-2b-1_149_35_2v13.pdf)
· [HDI via and pad rules](https://www.we-online.com/files/pdf1/design-rules-poster-hdi-microvia-cbt-en.pdf)

Supplier acceptance is open. The ordinary microvia example uses a 0.100 mm
finished hole and 0.300 mm pad. Pixel Dash uses 0.125/0.280 mm exterior
microvias, 0.200/0.360 mm buried vias and 0.150/0.300 mm through vias among
other sizes. The published construction does not grant acceptance of those
geometries. The stack drawing specifies IPC-4101/21 material and finished
foil. Lot dielectric constant, etched conductor shape and barrel-wall
thickness are unconfirmed. The wide CAD uses the drawing’s 1.491 mm nominal finished thickness. The four copper layers span 1.420 mm between outer copper centerlines.

For board 77e38f1, use --wurth with checks/estimate-ddr-impedance.py,
checks/estimate-ls1-pours.py --joined, and checks/screen-ls1-drop.py
--sheet-network-report with the corresponding sheet output. At assumed Er
3.91 and 0.002 mm mesh, the 0.102 mm line screens at 51.53 Ω single-ended.
The 0.180 mm gap screens at 96.73 Ω differential. The modeled surface rates
are 5.769 and 5.617 ps/mm. Using 6.60 ps/mm for a barrel as a sensitivity
case, the worst data-to-strobe differences are 39.729 ps and 22.556 ps for
uniform odd-mode strobes. D7 and D8 are limiting. A10 and CKE trail the
modeled clock mean by 65.681 and 53.327 ps. These calculations exclude
package and launch discontinuities.

On this same export the 0.025 mm CAM sheet mesh gives 12.489 mΩ between
the L3 source and L4 CPU bank. The loop budget assumes 20 µm barrel walls,
equally loaded CPU balls, 110 mΩ LS1 and DCDC3 at −2%. With an ideal return
and before transient droop the remaining 250 mA margin is +0.149 mV at
20 °C and −2.764 mV at 80 °C. Each additional milliohm of return consumes
0.250 mV. At 80 °C there is already a deficit with a zero-ohm return.
A 100 mA increment held for 1 µs requires 2.17–4.35 mV from the capacitors
alone assuming 46–23 µF effective and no regulator response. Return
impedance, fitted effective capacitance, package drop and load-step
response remain unverified. LS1 fails this hot-load screen.

### First LDO1 output distribution checkpoint

The 1.8 V LDO1 output reaches C_PMIC_LDO1 (Samsung CL21A226MAQNNNE,
22 µF nominal, JLCPCB C45783) and ten CPU loads in exported copper. The
capacitor return reaches system ground. CAM independently separates the
output, input and return. All sixteen intended package balls now have a
source net assignment. The remaining physical opens are E14, H15, N16,
P14, P9 and R16. Datasheet capacitance under bias, high-frequency bypass at
each load and supply noise at the four DPLL domains remain to be verified.

Using L1–L2 microvias on the CPU feeds preserved both DDR supply domains,
the CPU and memory ground returns, and full-width reference coverage.
The single-net and 6 mil spacing checks passed. The Gerber short check
passed and 7,436 strokes matched. Whole-board CAM still flags 40 open nets,
including the partially distributed LDO1 rail.

Six additional 0.13 mm branches with L1–L2 microvias complete the LDO1
distribution to E14, H15, N16, P14, P9 and R16. Four-layer CAM now finds
**16/16 LDO1 loads** on the capacitor's supply node, with input and ground
isolated. The short, clearance, independent 6 mil, return and reference
checks passed. CAM verified 960 plated barrels, 50 distinct DDR pairs and
7,466 matching trace strokes. The 39 remaining disconnected mapped nets
include boot straps and raster signals. B4, B5, C5, N5 and P5 still lack
their required feeds. Voltage tolerance, local decoupling and analog noise
at the LDO1 loads remain separate outstanding checks.

At 374a690 the joined LS1 feed and cropped return model use the same 30 µm
copper. The L2 return screen uses one digital VSS ball, U1.A1, its plated
via and the exposed-pad via at (−22.30, 23.20) mm. Copper comes from the
drilled L2 Gerber. With current constrained to this single return, the
0.050/0.075 mm meshes give 4.601/4.635 mΩ at 20 °C. At 250 mA and 80 °C
the finer mesh adds 1.421 mV to the drop, taking the modeled DC margin to
−4.185 mV. Other ground lands provide parallel paths in hardware. At
50% effective capacitance, a further 100 mA step for 1 µs gives a 4.35 mV
ideal capacitive term before ESR, ESL and regulation. A measured transient
waveform and actual via plating are still unavailable. Use --return-path on
the Würth sheet solve to reproduce the single-return case.

### Push-button enable and retained raster routing

AC_DET now reaches IN_BIAS on VSYS. TI SLDS234B §5.3.1.16 documents this
connection for PB/PWR_EN control. Plugging in a charger can supply the board
independently of issuing a PMIC wake request. Charger power sharing and
switch-over behavior still need whole-system validation. Exported CAM shows
IN_BU, IN_BIAS, all four main buck inputs, IN_LDO1 and AC_DET on VSYS;
IN_LS1 is on DCDC3. Cold reset, warm reset and C6 power hold pass.
The RTC mode, backup reset and CPU wake checks still fail at B4, B5 and C5.
The latest four-layer check covers 962 plated barrels and 7,472 trace
strokes. The board remains on fabrication hold.

A raster search over X = −58 to 65 mm and Y = −40 to 40.4 mm found no
additional complete exterior-layer routes with existing copper and the
current continuous ground reference. At a 0.07 mm search grid D16, D17,
DE and HSYNC each have zero legal through-via sites reachable within the
CPU-side L1 region screened by this router. The display-side regions for
all four have via candidates. A wider search around the display does not
resolve these CPU escapes. Five existing raster paths remain in the layout.

The --panel-storage option on the CAM connectivity audit walks all 29 LCD
connections and all seven microSD connections between the package and their
connector contacts. At 59b63fc the physical LCD paths are D11, D13, D14,
D15 and PCLK. All six MMC0 bus signals and card detect reach the card socket.
Socket power and the physical boot straps still gate card boot.
