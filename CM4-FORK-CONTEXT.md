# Context for the AM3354 -> CM4 module fork

This branch (`am3354-cm4-base`) is `module-board` at commit 56b9468, the AM3354 + DDR3L module **0.4.4**, plus
two things a fresh session needs and that were only on the original machine:

- `external/ddr-route/out/module9/` and `external/ddr-route/net-names.json`: the routed, verified DDR block
  `module/plan.ts` reads. The original code reads them from `/home/user/ddr-route/...`; point it at
  `external/ddr-route/...` (or copy them to that path) in the fork.
- This file.

## Goal (from the user)

Fork the routed AM3354 module and improve it so it plugs into a Raspberry Pi **CM4 carrier board**. Do not change
the existing routed module: the published `abse/am3354-ddr3-module@0.4.4` on tscircuit.com, the `module-board`
branch and `module/` stay as they are. Work in a new folder (e.g. `cm4-module/`) on a new branch.

## The existing module (see `module/README.md`)

- 50 x 36 mm, 6 layers, 1.0 mm, ENIG. AM3354BZCZD80 (U1) + MT41K512M16VRP DDR3L (U_DDR), DDR routing,
  decoupling, DDR VREF/ZQ parts, 24 MHz crystal. No power chip on board: the handheld supplies VDD_CORE,
  VDD_MPU, VDDS_DDR, 3V3, 1V8, VDDS_RTC through two DF40C-100DS-0.4V connectors (J1, J2, bottom).
- Through vias only: 0.1 mm hole / 0.3 mm pad, via-in-pad, filled and capped.
- Build chain `module/make.sh`: plan.ts (places parts around the fixed DDR copper) -> route.sh / route-signals.ts
  -> TOPUP plan.ts -> planes.ts -> build.tsx -> check.ts (whole-board check) -> export.ts + layers.py (fab/).

## What a CM4 module needs (work done for the RK3566 CM4 module, same user)

Repo `Abse2001/rk3566-lpddr4-module`, branch `wip/full-module` (public on GitHub), folder `source/`:

- Frame: 40 x 55 mm, board x -3.5..36.5, y -51.5..3.5, M2.5 holes at (0,0) (33,0) (0,-48) (33,-48).
- Connectors: two Hirose DF40C-100DP-0.4V(51) on the **bottom**: J1 at (-0.46,-21.5) (CM4 pins 1-100),
  J2 at (33.46,-21.5) (pins 101-200), oddSide=1. Footprint: `cm4HeaderFootprint()` in `source/parts.tsx`.
- Pin data: `source/design/cm4-soquartz-pins.json`, `source/design/make-cm4-map.py` -> `cm4-map.json`
  (200 pins: power, GND, signals, NC). `source/design/rails.py` for power groups.
- A real CM4 takes **+5 V** (pins 77/79/81/83/85/87 on J1) and makes its own rails; it also outputs
  +3.3 V and +1.8 V to the carrier, and has GLOBAL_EN, RUN_PG, nRPIBOOT, LED pins, ID_SD/ID_SC EEPROM I2C.

So the fork needs, at minimum:
1. CM4 outline, holes and the two DF40C-100**DP** headers in CM4 positions (the current module uses DS
   receptacles at its own positions).
2. A power tree on the module from 5 V: VDD_CORE 1.1 V, VDD_MPU 1.1-1.26 V, VDDS_DDR 1.35 V, 3V3, 1V8,
   VDDS_RTC, with the AM335x power-up sequence (SPRS717L 6.1) and PWRONRSTn / RTC_PWRONRSTn driven correctly.
   A TPS65217 (the BeagleBone PMIC for AM335x) or discrete regulators; check JLCPCB/LCSC stock.
3. Boot straps (SYSBOOT on LCD_D0..15) on the module, I2C0 pull-ups, an eMMC or rely on the carrier's SD
   (CM4 Lite style: SD pins on the connector), and the CM4 pin map for what AM335x can provide:
   GPIO on the 40-pin header pins, UARTs, I2C, SPI, SD/MMC, USB0/USB1 (USB 2.0), LEDs.
   AM335x has no HDMI, MIPI CSI/DSI or PCIe: those pins are NC; list them in the README.
   Ethernet: the CM4 carries its PHY on the module and exposes MDI pairs; decide (and ask the user) whether
   to add a PHY on the module (AM3354 RGMII/RMII -> PHY -> MDI on the CM4 pins) or leave Ethernet NC.
4. Re-place and re-route around the unchanged DDR block (move it as a rigid block if needed), planes, the
   whole-board check, fab files, README with status and open items.

## Rules (user: "no hacks", cheapest JLCPCB 6-layer that works)

- Never relax a rule to make routing pass. Final board: 0 clearance violations, every net connected,
  pairs within skew, independent checker.
- JLCPCB 6-layer (capabilities page, checked 2026-11-25): trace/space 0.09 mm min (use 0.1), SMD pad to pad
  0.15 mm, pad to track 0.1 mm, via hole to inner copper 0.2 mm, via hole to hole 0.2 mm, routed edge 0.2 mm,
  mask bridge 0.10 mm, BGA pad >= 0.2 mm (0.2-0.25 needs ENIG), annular ring 0.15 mm min.
  Via-in-pad (epoxy or copper filled and capped) is the default for 6+ layers. Vias with a 0.1 or 0.15 mm hole,
  or 0.2/0.25 mm hole with a pad under 0.45 mm, cost extra; 0.3/0.4 mm does not. The AM3354 ZCZ (0.8 mm pitch)
  module already uses 0.1/0.3 mm vias on a 1.0 mm board; keep or revisit with the cost in mind. HASL is not
  offered on 6+ layers: ENIG.
- Double-sided assembly is fine (connectors must be on the bottom for CM4).

## Practical notes

- tscircuit: bottom-side parts are mirrored in x; rotated pads report unrotated w/h; set schX/schY on every
  part or rendering is very slow; `tsci import --jlcpcb` imports parts; `tsci push` publishes (ask the user
  first, and never publish from a dirty tree).
- Commit and push only your new branch; do not push to `module-board`, `main` or other existing branches.
- Ask the user before creating a GitHub repo or publishing to tscircuit.com.
