# Pixel Dash gameplay energy budget

This estimate sets the battery search range for the single-PCB wide handheld. The design point is a representative game at 800 MHz, 75% backlight PWM and the built-in speaker. Ambient temperature, speaker volume, workload and converter efficiency affect the result. The two columns are design allowances, pending battery-side measurements.

| Average load | Representative game | Heavier game and louder audio |
|---|---:|---:|
| 7-inch ER-TFT070A2-6 backlight, 9.6 V × 180 mA × 0.75 | 1.30 W | 1.30 W |
| AM3354, memory and associated I/O | 1.35 W | 1.70 W |
| Panel logic, analog rails and touch allowance | 0.35 W | 0.55 W |
| Audio | 0.45 W | 0.80 W |
| microSD, controls and other board loads | 0.25 W | 0.30 W |
| Total at the loads | 3.70 W | 4.65 W |
| Assumed aggregate conversion efficiency | 86% | 83% |
| **Average at the battery** | **4.30 W** | **5.60 W** |

BuyDisplay specifies 135 mA typical and 180 mA maximum for the bare panel backlight. The table uses 180 mA during the on portion of each PWM cycle as a conservative power estimate. At 135 mA on-state current, 9.6 V and 75% duty, the backlight uses 0.97 W. The driver design must keep peak current, including tolerance, within the 180 mA rating. Actual luminance at 75% PWM depends on the driver and optics. TI's AM335x reference measurements give 0.953 W total at 800 MHz under Dhrystone. This is a bench reference for the processor allowance. The table includes an additional allowance for the Pixel Dash memory and graphics workload. [BuyDisplay panel datasheet](https://www.buydisplay.com/download/manual/ER-TFT070A2-6_Datasheet.pdf) · [TI AM335x power measurements](https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/791/AM335x-Power-Consumption-Summary-_2D00_-Texas-Instruments-Wiki.pdf)

The bare panel also requires DVDD at 3.0–3.6 V, AVDD at 9.4–9.8 V, VGH at 17–19 V, VGL at −6.6 to −5.4 V and VCOM at 3.0–3.5 V. Design targets are 3.3 V, 9.6 V, 18 V, −6 V and 3.2 V respectively. AVDD and the constant-current LED output serve separate loads even though their typical operating voltages coincide. The panel logic allowance above includes the bias rails provisionally. Their converter losses and load currents need verification on the integrated board. [BuyDisplay bare-panel datasheet, sections 4.3 and 4.4](https://www.buydisplay.com/download/manual/ER-TFT070A2-6_Datasheet.pdf)

At 3.7 V nominal and 90% usable nameplate energy, required capacity in Ah is average battery watts × hours / (3.7 × 0.90). The usable-energy allowance covers cutoff and capacity variation for a new pack. Aging requires a separate margin.

| Goal | Representative | Heavier |
|---|---:|---:|
| 6 hours | 7.75 Ah / 28.7 Wh | 10.09 Ah / 37.3 Wh |
| 8 hours | 10.33 Ah / 38.2 Wh | 13.45 Ah / 49.8 Wh |

A nominal 10 Ah pack projects 7.7 or 5.9 hours across these scenarios. A 12 Ah pack projects 9.3 or 7.1 hours. A 13.5 Ah minimum capacity targets eight hours at the heavier design point. At 85% backlight the LEDs add 0.173 W before conversion, or about 0.5 Ah extra over eight hours. Qualify by integrating battery voltage and current during sustained representative gameplay at the agreed brightness and volume, from full charge to normal shutdown.

## Sourcing comparisons

The wide handheld now targets a single nominal 3.7 V, 10,000 mAh pack. The working candidate is the YELUFT listing below. Its mechanical envelope, discharge rating and mating polarity still need confirmation. US one-unit prices below exclude tax and shipping. The battery supplier and connector have not been frozen.

| Pack | Source | Observations |
|---|---|---|
| YELUFT, 10 Ah advertised | [Amazon B0GTLW7SFW](https://www.amazon.com/dp/B0GTLW7SFW), $17.99 in the supplied listing | 37 Wh nominal. A buyer reports 9.786 Ah at 0.5 A down to 3 V. Another reports opposite plug polarity to their device. Neither identifies a guaranteed keyed pinout for Pixel Dash. Before selecting the pack, verify the supplier drawing, maximum dimensions and continuous-current rating, then meter a sample against the numbered PCB connector contacts before mating. |
| MakerFocus 9065115, 10 Ah | Amazon ASIN B093WS6C66 | MakerFocus lists $20.79 direct for one flat pack, nominal 112 × 65 × 8.8 mm. Current Amazon checkout price and keyed plug polarity unverified. Manufacturer lists 3 A maximum working current and a 1.8–2.1 A protection threshold. Resolve that discrepancy against low-state-of-charge gaming peaks. |
| Adafruit 5035 / PKCELL, 10.05 Ah typical | DigiKey 1528-5035-ND, $29.95 | Manufacturer minimum 9.5 Ah, maximum envelope 69 × 56.5 × 19 mm, 3 A continuous discharge. The vendor confirms compatibility with its charger wiring. The BQ24074 reference board connects BATT contact 1 to VLIPO and 2 to GND. |
| PiJuice PIS-1129, 12 Ah | DigiKey, $47.28 | Listed 135 × 68 × 9 mm. Different connector/harness requires its own drawing and PCB pin-map verification. |

[MakerFocus specifications](https://www.makerfocus.com/products/makerfocus-3-7v-lipo-battery-10000mah-lithium-rechargeable-battery-9065115-with-micro-ph2-0-plug-for-raspberry-pi-ups-board) · [Amazon listing](https://www.amazon.com/dp/B093WS6C66) · [DigiKey 5035](https://www.digikey.com/en/products/detail/adafruit-industries-llc/5035/14625568) · [PKCELL pack drawing, p. 8](https://cdn-shop.adafruit.com/product-files/5035/5035_10050mAh_3.7V_A1____20210511.pdf) · [Adafruit charger board](https://github.com/adafruit/Adafruit-BQ24074-PCB/blob/844404b10e1a87820ee9cb9024d85f67f4bc4bfd/Adafruit_BQ24074.brd) · [DigiKey PiJuice battery listings](https://www.digikey.com/en/products/filter/batteries-rechargeable-secondary/maker-emporium-ltd/91)

## Battery pocket on the preserved compact shell

The modeled original pack occupies 61.0 × 47.7 × 7.9 mm. A horizontal slice of the rear-shell mesh at Z = −8.0 mm gives a 62.0 × 48.7 mm rectangular pack bay (X = −31.0 to +31.0 mm, Y = −22.35 to +26.35 mm). The opening to the right leads into the cable bay. The MakerFocus 112 × 65 mm and PKCELL 69 × 56.5 mm packs both exceed the rectangular pack bay in plan. The complete compact rear shell is 157 mm wide, while the wide PCB is 232 mm wide. The old shell remains a fallback.

The YELUFT listing does not give a guaranteed maximum envelope including its protection board and lead exit. Its fit in a revised shell and polarity at the keyed header remain open. The nominal capacity alone cannot determine the required pocket dimensions.

## Charger sizing for the 10 Ah pack

The integrated BQ25185 has 18 kΩ from ILIM/VSET to ground and 620 Ω from ISET to ground. These select 4.2 V, a 500 mA USB input limit and approximately 484 mA fast charge (300 AΩ / 620 Ω). A full 10 Ah recharge would need at least 20.7 hours at that current before taper and system load. TI revision B lists a 360-minute typical fast-charge safety timer. At nominal current six hours adds at most 2.9 Ah. This configuration cannot serve as the final charger for the selected capacity. [TI BQ25185 electrical characteristics and sections 6.3.7.7 and 7.2.2](https://www.ti.com/lit/ds/symlink/bq25185.pdf)

The BQ25606RGER is a replacement candidate available as JLCPCB C374063. Its switching power path prioritizes SYS and can supplement limited input with battery power. A 5 V, 500 mA source delivers at most 2.5 W before losses, below the 4.3 W representative play budget. On that source the battery supplies the deficit during play. On a sufficiently rated supply the charger can power the game and charge with the surplus. The charge setpoint awaits the pack manufacturer's rating, USB current detection, timer budget and thermal design. The wide-board netlist still contains the BQ25185 and an independent USB-to-system path. [TI BQ25606 sections 9.3.2, 9.3.4 and 9.3.5](https://www.ti.com/lit/ds/symlink/bq25606.pdf) · [JLCPCB C374063](https://jlcpcb.com/partdetail/C374063)

## Wide-shell pocket study

[Pocket and mounting-hole drawing](../previews/battery-pocket.png)

The separate parametric insert in `mechanical/wide/battery-pocket.scad` preserves the compact shell and its tub. The default flat profile uses the MakerFocus 9065115 supplier tolerance of ±2 mm on 112 × 65 × 8.8 mm, giving a maximum study envelope of **114 × 67 × 10.8 mm**. The YELUFT listing picture shows MakerFocus branding, but provides no model or tolerance tying the shipped pack to that envelope. The compact profile uses the PKCELL drawing maxima of **69 × 56.5 × 19 mm**. Neither profile selects a new battery SKU. [MakerFocus product specifications](https://www.makerfocus.com/products/makerfocus-3-7v-lipo-battery-10000mah-lithium-rechargeable-battery-9065115-with-micro-ph2-0-plug-for-raspberry-pi-ups-board) · [PKCELL drawing, page 8](https://cdn-shop.adafruit.com/product-files/5035/5035_10050mAh_3.7V_A1____20210511.pdf)

The flat insert measures 119 × 72 × 14.3 mm outside. Its provisional clearances are 1 mm per side and 2 mm in depth. An open-top lead slot faces the connector side. Swelling allowance, pack retention, cable bend, protection board, NTC placement, connector polarity and vertical separation from the PCB still require verification for the selected pack. The flat profile overlaps the lower two existing PCB mounting bosses in plan. A symmetric alternative at X = ±70, Y = −29 mm clears the pocket and existing NTC cutouts. On the right the nearest non-pour copper is KEY_START, 4.709 mm from the proposed center. The compact insert measures 74 × 61.5 × 22.5 mm and clears all four boss envelopes in plan.

To reproduce the geometry check, export the SCAD with OpenSCAD twice using `profile="flat"` and `profile="compact"`, then run `python checks/check-battery-pocket.py dist/index.circuit.json flat.stl compact.stl`. The screen tests closed solids, maximum pack dimensions and screw-boss overlap. Assembly Z placement and rear-shell integration are pending.
