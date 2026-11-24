# AM3354 + DDR3L compute module

A 50 x 36 mm, 6-layer, 1.0 mm board that carries only what needs six layers: the AM3354BZCZD80 (U1), the
MT41K512M16VRP DDR3L (U_DDR), the DDR3 routing between them, their decoupling, the DDR reference/calibration
parts and the 24 MHz crystal. Everything else (power chip, boot straps, SD, USB, display, buttons, debug) lives on
the handheld and reaches the module through two Hirose DF40C-100DS-0.4V connectors (J1, J2, bottom side; the
handheld carries DF40C-100DP, LCSC C531031).

| Layer | Use |
|---|---|
| L1 top | DDR + handheld signals, both BGAs, crystal |
| L2 | ground |
| L3 | VDDS_DDR (west, the processor's north and south rows and its core-ball interior, with the DDR_VREF link embedded), 3V3 (the processor's middle rows and the east edge) |
| L4 | VDD_CORE, VDD_MPU, part of 1V8, DDR_VREF (between the chips), the 23 handheld signals whose balls sit inside the DDR fan-out |
| L5 | ground |
| L6 bottom | DDR + handheld signals, decoupling, connectors |

Through vias only, no blind or buried vias: 0.1 mm holes in 0.3 mm pads, via-in-pad throughout. The 0.1 mm hole keeps every hole wall at least 0.2 mm from other copper on the outer layers and 0.225 mm on the planes (JLCPCB: 0.2 mm); it needs a board of 1 mm or less with ENIG.

## What the handheld has to provide

Rails, through the connector pins listed in `fab/pinmap.csv`:

| Rail | Pins | Notes |
|---|---|---|
| VDD_CORE 1.1 V | J2, 4 | |
| VDD_MPU 1.1-1.26 V | J2, 6 | |
| VDDS_DDR 1.35 V (1.5 V) | J1, 4 | feeds the processor's DDR I/O, the memory and the VREF divider |
| VDD_3V3 | J1, 3 | VDDSHVx and USB 3.3 V |
| VDD_1V8 | J1, 2 | VDDS, PLL, oscillator, USB and ADC 1.8 V balls (ADC unused: VREFP on 1.8 V, VREFN on ground) |
| VDDS_RTC 1.8 V | J2, 1 | RTC domain; the internal RTC regulator is enabled (RTC_KALDO_ENn grounded, 1 uF on CAP_VDD_RTC) |
| GND | 55 | |

Follow the AM335x power-up sequence on the handheld (SPRS717L section 6.1) and drive `PWRONRSTn` and
`RTC_PWRONRSTn` from it. `LCD_D0..LCD_D15` are the SYSBOOT pins: the boot-mode resistors go on the handheld.
I2C0 needs its pull-ups there too. 75 signals are wired, 50 connector pins are spare.

## Files

- `fab/module-gerbers.zip` (and `fab/gerbers/`), `fab/bom.csv`, `fab/cpl.csv`: what a fab/assembly quote needs.
- `fab/pinmap.csv`: every connector pin with its net, processor ball and position.
- `fab/views/*.png`: one picture per copper layer.
- `dist/module.circuit.json`: the board as tscircuit circuit JSON.

Ordering notes (JLCPCB): 6 layers, 1.0 mm, ENIG, minimum hole 0.1 mm / via pad 0.3 mm, trace/space 0.1 mm,
vias epoxy-filled and capped (via-in-pad), both sides assembled. Outer prepreg (L1-L2, L5-L6) 1080 or 3313, not 7628:
that puts the 0.102 mm outer traces at 56-63 ohm (TI: 50-75); 7628 would give 89 ohm (`si/zo_results.txt`).
Bring-up: set the processor's DDR command/address/clock drive to 40 ohm or weaker (`si/README.md`).

## Rebuilding

`module/make.sh` runs the whole chain and ends with the whole-board check:

1. `plan.ts` loads the routed, verified DDR block (`ddr-route/out/module9`) and places every other part and via.
2. `route.sh` (`route-signals.ts`) routes the handheld signals to free connector pins.
3. `TOPUP=1 plan.ts` adds the bypass capacitors that had to wait for those routes.
4. `planes.ts` builds the inner-layer copper; `build.tsx` renders `dist/module.circuit.json`.
5. `check.ts` checks the rendered board: pad positions, clearances, shorts, every net one piece.
6. `export.ts` and `layers.py` write `fab/`.

The DDR block itself is produced and checked in `ddr-route` (`route-staged.ts`, two-layer mode, seed 5, `exactViasByBus` = 2 for
both bytes and address/control/clock, keepouts `runs/mod8.keepouts.json`; then `clean-wiggles.ts`, `verify.ts`,
`spec-check.ts` with `THROUGH=1`, `selfgap.ts`).

## Checks behind this build

- DDR block (`ddr-route/out/module9`): connectivity/clearance, TI SPRS717L Tables 7-68/7-69 lengths and skews,
  spacing allowance (also with the module's other traces as neighbours), same-net gaps: all pass.
- Whole board (`check.ts`): 141/141 nets one piece, no shorts, minimum clearance 0.100 mm, drill walls >= 0.30 mm apart,
  hole wall to other copper >= 0.200 mm (outer) / 0.225 mm (planes), through vias only.
- Independent audit from the Gerbers and the drill file (own parser): 0 shorts, 0 opens, every pour present,
  mask/paste on all 794 pads, vias tented, bypass counts and distances per Table 7-64/7-65 met
  (processor 20 x 100 nF within 306 mil of 400, memory 12 within 61 mil of 150, 2 x 10 uF bulk each).
- Plane voltage drop (`irdrop3d.py`: all four inner layers joined at the vias, 17.5 um copper, plated 0.1 mm barrels;
  `power-results.txt`): VDD_CORE 2.5 mV at 0.4 A, VDD_MPU 5.1 mV at 1 A, VDDS_DDR 7.4 mV at 0.6 A, VDD_1V8 14 mV at
  0.2 A, VDD_3V3 15 mV at 0.25 A (all under 1 % of the rail).
- DDR bypass connection (`hs_loop.py`): all 20 processor HS capacitors have their VDDS_DDR via in VDDS_DDR copper on
  layer 3 (L3 carries VDDS_DDR in the processor's north/south rows and core-ball interior for this); plane spreading
  inductance 0.69-2.4 nH each, 72 pH for the twenty in parallel including their vias.
- DDR: every net has exactly two vias and runs on the outer layers only, so the via length is the same for every
  net of every matched group, and the in-plane lengths and skews meet TI's tables.
- No VTT termination on address/control/clock: TI's Figure 7-48 topology for one memory device. Coupled-line
  simulation of the worst net with its neighbours, losses, vias and packages (`si/`): passes the DDR3L levels with
  the drive at 40 ohm or weaker on every usable prepreg. No IBIS models; measure on the first boards.
- D3 and D7 are swapped at the memory (within byte 0, deliberate, DQ0 untouched).
- Via-in-pad everywhere: every handheld-signal via inside the processor's ball field sits exactly on its ball centre
  or >= 0.45 mm from every ball centre; no via pad overlaps a pad of another net (bypass-capacitor vias keep
  >= 0.104 mm to the ball pads). Order epoxy-filled and capped vias.
- USB0 D+/D- run side by side (11 mm, equal length) but not as an impedance-controlled pair.
- 1.8 V PLL/oscillator/USB supply balls share the 1.8 V plane without ferrites.
- Connector pin numbers in `fab/pinmap.csv` follow the LCSC footprint (1-50 outer row, 51-100 inner row).
  Lay out the handheld from the X/Y positions, not from pin numbers. The land pattern follows Hirose's drawing
  is the JLCPCB/LCSC footprint of C597931 as imported (rows 3.90 mm outside, 2.50 mm inside; Hirose draws 3.78 / 2.38, the contacts land inside both).
- C_VREF_CPU (0.1 uF on the processor's DDR_VREF) sits 5.9 mm from the J4 ball (TI: "near", no number); closer
  sites are inside the bottom-side DDR fan-out.
- Crystal Y_OSC0: LCSC C362341 (24 MHz, 10 pF, 30 ohm, +/-10/+/-20 ppm, -40..85 C) replaced C439045 (out of stock);
  same land pattern. With the 15 pF capacitors and the short routed traces the load is about 9-10 pF, which suits a
  10 pF crystal (TI Table 6-2: ESR <= 48 ohm, +/-50 ppm total, C1/C2 12-24 pF).
- BOM part numbers and pick-and-place rotations need the usual review in the assembly preview.
  Stock at the time of writing: AM3354BZCZD80 27 pcs, MT41K512M16VRP-107 IT:P 281 pcs (about 70 USD each).
