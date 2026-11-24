# Six-layer module and handheld carrier

The module takes VSYS and ground through the DF40 connector. It generates and sequences the CPU and DDR rails locally. This keeps the regulator-to-load and bypass return paths on the same PCB as the BGA lands. The current 37.60 × 46.00 mm outline is a routed baseline. A smaller outline requires a new placement and same-export verification.

The 119 populated references comprise the AM3354, DDR3L, TPS65218D0 PMIC, switched CPU DDR supply, oscillator crystal, DF40 plug and 113 passive components. The passives set boot and regulator defaults, support the oscillator, filter regulator inputs and outputs, bypass processor and memory supplies, or set the DDR reference and calibration levels. The switch button itself lives on the carrier. Its PMIC bias stays on the module so disconnecting the carrier cannot float the power-key input.

| Carrier hardware | Module contacts | Carrier work |
|---|---|---|
| microSD socket and card bypass | 2–7, 29; sequenced 3.3 V on 71, 74, 77 | Route MMC0 clock, command, four data lines and card detect. Fit the pull-ups on the switched domain and return the socket to module ground. |
| Buttons, joystick switches and joystick ADC | 9–22, 62–63 | Terminate switches on the carrier. Connect the joystick ADC to the shared carrier I²C bus. |
| USB receptacle, protection and VBUS sensing | 24–26, 80 | Keep connector protection at the receptacle. Respect the AM3354 USB0 VBUS pin limits and check unpowered back-feed. |
| Audio output stage and backlight driver | 27–28 | Provide local power, bypass and current returns at each load. |
| Panel, panel supplies, level buffers and touch | 30–53, 55–56, 58–60, 62–64 | Keep panel logic DVDD, analog biases and backlight power on the carrier. Shared strap pins require reset-safe loading. |
| Debug UART connector or test pads | 65–66 plus ground | Connect adapter TX to module RX on 65, adapter RX to module TX on 66, and common ground. Use 3.3 V logic. Leave adapter power disconnected. |
| Battery, charger, input protection and power button | 67; VSYS on 68, 70, 73, 76, 79 and distributed grounds | Keep battery and charger current on the carrier. Deliver the specified PMIC input range under load. |

Use the individual contact and CPU pin assignments in [carrier-pinout.csv](carrier-pinout.csv). A connector assignment describes two intended endpoints. The exact module copper status is in [open-connections.csv](open-connections.csv). Carrier-to-peripheral continuity needs a separate carrier export, including its mated pin-one orientation.

## First code on hardware

Use a known-good FAT-formatted MMC0 card with a Pixel Dash AM3354-compatible ROM-loadable MLO and matching U-Boot image. The first-stage image must run from on-chip SRAM until it configures the PMIC, clocks, pinmux and EMIF for this particular DDR3L device. A different AM335x board's SPL can use incompatible rail or memory settings. Configure UART0 before external RAM initialization to distinguish failure before and after EMIF bring-up. Provide one build that prints the latched CONTROL_STATUS and stops in SRAM, then a second build that initializes and tests external memory before loading the application. These images and successful execution remain to be verified.

For the first article, begin with the panel disconnected, capture supply ramps and PWRONRSTn, save the early UART log, and confirm the latched strap word is 0x4017. Repeat from a true power removal with the panel attached. Fit reset-safe isolation, power panel DVDD, and verify the carrier loads and sequencing described in [reset-and-reference.md](reset-and-reference.md) before enabling the raster bus. Record both runs against the module and carrier revisions.
