# AM3354 + DDR3L module in Raspberry Pi CM4 format

A 40 x 55 mm, 6-layer, 1.0 mm board that plugs into a CM4 carrier (the CM4 IO board or a custom one) through the CM4's
two 100-pin connectors. It carries the AM3354BZCZD80 (U1), the MT41K512M16VRP DDR3L (U_DDR) with the DDR routing of
the original module unchanged, a TPS65217D power chip and two SY8089 bucks, the boot straps and the pull-ups, and
maps what the AM3354 can do onto the CM4 pins (`fab/pinmap.csv`).

Status: routed, whole-board check passes (`check.ts`: MODULE RESULT PASS). See "Before ordering" for what still
needs a decision or a check outside this repository.

## What it does on a CM4 carrier

| CM4 function | Here |
|---|---|
| +5 V in (J1 77-87) | VIN5: the module makes every rail itself (TPS65217D: VDD_CORE, VDD_MPU, VDDS_DDR, RTC; SY8089: 3.3 V, 1.8 V) |
| +3.3 V / +1.8 V out (J1 84/86, 88/90) | the module's 3.3 V and 1.8 V rails |
| GLOBAL_EN (99), RUN_PG (92), nRPIBOOT (93) | PMIC enable; RUN_PG as on a CM4 (3.3 V, 10 k pull-up, high = running, pull low to reset) through a MOSFET level shifter to PWRONRSTn; USB boot (see straps) |
| GPIO2-27 on the 40-pin header | GPIO / UART0 (console) / I2C2 / SPI0 / McASP0 (PCM) / EHRPWM1, per `fab/pinmap.csv` |
| ID_SD / ID_SC (HAT EEPROM) | I2C1 |
| SD card (CM4 Lite pins) | MMC0, the boot device (SD_PWR_ON on a GPIO) |
| USB 2.0 (J2 103/105), USB_OTG_ID (101) | USB0; OTG_ID read on a GPIO with a 10 k pull-up, the role set in software |
| LED_nACT, LED_nPWR, CAM_GPIO, nEXTRST | GPIOs |
| Ethernet, HDMI, MIPI CSI/DSI, PCIe, WiFi | not connected (the AM3354 has none of these, and Ethernet was dropped on purpose; networking is over USB) |

200 CM4 pins: 47 signals, 51 ground, 10 power, 92 not connected.

Boot straps: SYSBOOT[15:0] = 0x4017 (24 MHz crystal; boot order MMC0, SPI0, UART0, USB0), one 10 k resistor per bit.
nRPIBOOT pulls bits 0 and 2 low through 1 k: 10010b = NAND, NANDI2C, USB0, UART0, so the carrier's USB-boot
button/jumper boots the AM3354 from USB.

## Board

| Layer | Use |
|---|---|
| L1 top | signals, the BGAs, the PMIC, crystal |
| L2 | ground |
| L3 | supply islands: VDDS_DDR, VDD_3V3, VDD_1V8, SYS, VIN5, DDR_VREF, DDR_ZQ, DDR_VTP |
| L4 | VDD_CORE and VDD_MPU islands under the processor's power core, thin 1.8 V / 3.3 V links; signals elsewhere |
| L5 | ground (slow signals may cross it away from the BGAs' reference areas) |
| L6 bottom | signals, decoupling, the bucks, CM4 connectors J1/J2 (Hirose DF40C-100DP-0.4V(51), LCSC C531031) |

Through vias only: 0.1 mm holes in 0.3 mm pads, via-in-pad throughout (epoxy-filled and capped). Trace/space 0.1/0.1 mm.

## Files

- `fab/gerbers/`, `fab/bom.csv` (162 parts, 53 top / 109 bottom), `fab/cpl.csv`: for a fab/assembly quote.
- `fab/pinmap.csv`: every CM4 pin with its net, processor ball and pinmux mode.
- `fab/views/*.png`: one picture per copper layer.
- `dist/module.circuit.json`: the board as tscircuit circuit JSON.
- `pb/routing.json`: the signal routing the board is built from.

## Rebuilding

`make.sh` runs the chain and ends with the whole-board check:

1. `plan.ts` loads the routed, verified DDR block (`external/ddr-route/out/module9`) as fixed copper and places
   every other part and via. No freely placed part goes into the processor's outer ball rows or the 2 mm band outside
   them on the three non-DDR sides (the escape ring); the SYSBOOT straps sit in the free strip above J2.
2. `planes.ts` (`ROUTES=none`) computes each supply's skeleton (its corridors); `pb/export.ts` writes the router input.
3. `pb/import.ts pb/routing.json` imports the routing; `planes.ts` builds the inner-layer copper around it.
4. `build.tsx` renders `dist/module.circuit.json`; `check.ts` checks it (pad positions, clearances, shorts, holes,
   board edge, every net one piece, every signal net joining all its terminals).
5. `export.ts` and `layers.py` write `fab/`.

Re-routing (only after a placement or netlist change): `pb/route.ts` is the negotiated-congestion router of the
RK3566 CM4 module (routing playbook). Run several seeds in parallel and keep the best:

    cd pb && OUT=_s6 SEED=6 MAXIT=100 GND_SIG=1 GND_SIG_BGA=1 bun route.ts

then re-route whatever is left in conflict strictly on the finished copper with `pb/reroute.py` (two-terminal nets;
the order matters), check, and copy the result to `pb/routing.json`. The current routing is seed 6 with GPIO7_CE1,
GPIO21_PCM_DOUT, GPIO22 and GPIO23 re-routed in that order, then the RUN_PG level shifter added with an incremental
re-route from that routing (the router's resume mode, 0 conflicts after 9 passes):

    cd pb && OUT=_q POLISH=routing.json RENEG=1 RENEG_NETS=PWRONRSTn,RUN_PG,VDDS_RTC SEED=6 MAXIT=40 GND_SIG=1 GND_SIG_BGA=1 bun route.ts

(`make.sh` exports the router's corridors with `FAT=0`: the routing was made around the thin supply skeletons; the
wide power trunks are laid around the finished routing.)

Verified for this routing: all 6570 DDR trace points and 100 DDR vias of `module9` are in the built board unchanged.

DDR signal integrity (`si/ddr_sim.py`, ngspice, results in `si/ddr_sim_results.txt`; generic I/O, no IBIS): DDR3L-800,
the routed block as lossless lines (outer microstrip 56.1 ohm from the original module's field solver, vias as 45 ohm +
0.3 pF). Data with 60 ohm ODT: eye height 810-862 mV of 1.35 V, width 1175 ps of 1250 (the rest is the edge time), for
writes (processor 40 / 34 ohm) and reads (memory 34 ohm). Address/command unterminated (one device): overshoot 0.18 V at
40 ohm and 0.29 V at 34 ohm (DDR3L limit 0.4 V). Pairs: CK/CKn crossing skew 0.19 ps, DQS0 and DQS1 0.01-0.05 ps (both
members of every pair carry the same two vias on the same layers). `module/si` has the earlier coupled-line (crosstalk)
analysis of the address/command and clock lines of the same routing: set the processor's DDR command/address drive to
40 ohm or weaker at bring-up.

## Before ordering

1. **Board thickness**: 1.0 mm (JLCPCB allows the 0.1 mm via hole only up to 1.0 mm). A real CM4 is 1.2 mm +-10 %
   (CM4 datasheet 3.1); mating is unaffected, the module sits 0.2 mm lower.
2. **Bottom-side height** (checked): on the standard 1.5 mm stacking (carrier DF40C-100DS) the gap under the module
   is 1.5 mm. Datasheet maxima of the tallest bottom parts: C_SYS 22 uF 0805 CL21A226MAQNNNE 1.40 mm (1.25 +-0.15,
   Samsung code Q), SY8089 SOT-23-5 1.30 mm (Silergy outline), 2.2 uH WIP201610P about 1.0 mm (2016-10 size), 0603
   MLCCs 0.90 mm. Everything fits; C_SYS leaves 0.1 mm. A 3.0 mm stacking carrier (DF40HC(3.0)-100DS) leaves 1.6 mm more.
3. **RUN_PG (pin 92)** (done): PWRONRSTn is driven by the PMIC's PGOOD at 1.8 V (its VIO is VDDS_RTC; PWRONRSTn
   accepts it, VIH 1.35 V, and tolerates 3.3 V). Q_RUN_PG (Si2302CDS, VGS(th) 0.40-0.85 V; gate on VDDS_RTC, source
   on PWRONRSTn, drain on RUN_PG) with R_RUN_PG 10 k to 3.3 V makes pin 92 behave as on a CM4: 3.3 V high once the
   PMIC reports power good, and a carrier pulling it low (CM4: through 220 ohm) resets the processor.
4. **Carrier current**: the module supplies 3.3 V and 1.8 V to the carrier on J1 84-90; the carrier's load on them
   must fit the SY8089 budget left after the module.
5. **USB0_VBUS** (done): abs. max and recommended max 5.25 V (AM335x datasheet), the same as the CM4's +5 V upper
   limit. R_VBUS is 1 k (was 0 ohm) to limit the current into the comparator input during an overshoot; the pin still
   sees > 4.6 V at a 4.75 V input. A carrier's +5 V must stay within the CM4 spec (4.75-5.25 V).
6. **USB pair**: D+ and D- both on the bottom layer with no vias, 16.55 and 16.43 mm.
7. **Supply drop** (checked, `irdrop.py`, results in `power-results.txt`): DC drop over the four inner layers from each
   regulator's output to its loads. VDD_MPU's layer-4 copper also fills the PMIC's SYS area (SYS is on layer 3 only),
   so its 1 A from DCDC2 no longer runs through a single thin link; VIN5 gets a 0.45 mm trunk on layer 3 (`FAT` in
   `planes.ts`). VDD_MPU 26 mV at 1.0 A (was 108 mV), VDD_CORE 6 mV at 0.4 A, VDDS_DDR 11 mV at 0.6 A, VIN5 59-69 mV
   at 1.1-1.6 A. 3.3 V and 1.8 V drop 5-7 mV to the processor; to the carrier's CM4 pins they drop 33 / 38 mV at 0.2 A
   each and 97 / 114 mV at the CM4's 0.6 A limit. **Keep the carrier's load on the module's 3.3 V and 1.8 V outputs to
   about 0.2 A each** (the CM4 itself allows 0.6 A).
8. **Decoupling**: the eight optional extra 100 nF caps (C_X_*) sit 6-7.6 mm from their balls (outside the escape
   ring); the 20 DDR high-speed caps are within TI's limit (worst 9.1 mm of 10.16 mm).
9. **Courtyards**: tscircuit reports 94 courtyard overlaps (default courtyard margins, mostly under the BGA);
   every pad pair on a side is at least 0.206 mm apart (JLCPCB 0402 spacing passes).
10. **CM4 geometry** (checked against the CM4 datasheet, figure 4): 55 x 40 mm, M2.5 holes 3.5 mm in from each
    edge, connector centres 21.5 mm from the holes, pins 1-100 along one long edge with pin 1 (outer row) at the far
    end from those holes, pin 101 on the inner row; the frame is a rotation of the CM4's, not a mirror. Connector rows
    are 3.04 mm from the long edges (CM4IO KiCad footprint; the drawing rounds to 3).
11. **CM4 connectors J1/J2** (Hirose DF40C-100DP-0.4V(51), LCSC C531031): LCSC showed 0 in stock on 2026-11-27, while
    distributors (DigiKey) list thousands. Order the genuine Hirose part through JLCPCB global sourcing (or consign
    it); no design change. In-stock fallback at LCSC: G-Switch GT-B0403MSV11-100B1101 (C42376235), a 100-pin 0.4 mm
    plug, 1.14 mm tall, 1.5 mm mated height, whose land pattern matches this footprint (rows 2.71 mm apart, 3.37 mm
    outer / 2.05 mm inner). Its datasheet does not state intermating with Hirose DF40C-100DS, so mate one with a CM4
    carrier before using it. Not suitable: JMEconn 5001-BM04100-15-00 (different land pattern, 2.40 / 3.37 mm) and
    LXWCONN LBF11-G100P-B0R01 (a receptacle).
12. **JLCPCB**: 6 layers, 1.0 mm, ENIG, 0.1 mm hole / 0.3 mm pad, via-in-pad (epoxy fill + cap), both sides
    assembled. Outer prepreg 1080 or 3313 (not 7628) to keep the 0.1 mm outer traces near 50-75 ohm.
