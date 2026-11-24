# Six-layer module and handheld carrier

The module takes VSYS and ground through the DF40 connector. It generates and sequences the CPU and DDR rails locally. This keeps the regulator-to-load and bypass return paths on the same PCB as the BGA lands. The current 38.20 × 46.60 mm outline is a routed baseline. A smaller outline requires a new placement and same-export verification.

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

KEY_UP uses DF40 contact 9 and AM3354 ZCZ V12 (GPMC_CLK, mode 7, GPIO2_1 on VDDSHV2). Configure the pad as an input with its receiver enabled and set GPIO2 bit 1 as an input before sampling the switch. V12 resets in mode 7 with a pull-down. Configure the run-time bias for the carrier switch wiring. The module-specific pin assignment supersedes V16 in the original handheld interface. [TI AM335x datasheet, Table 4-2](https://www.ti.com/lit/ds/symlink/am3354.pdf)

KEY_RIGHT uses contact 12 and ZCZ T13 (GPMC_CSn3, mode 7, GPIO2_0 on VDDSHV2). Enable the input receiver and configure GPIO2 bit 0 as an input for the carrier switch. T13 resets in mode 7 with a pull-up. Its centered 0.15/0.30 mm through via requires nonconductive resin fill and copper cap at assembly.

## First code on hardware

For the first cold-boot test, disconnect the panel, remove the MMC0 card and leave SPI0 without a valid boot image. With the intended 0x4017 strap word, ROM tries MMC0, SPI0, UART0 and USB0 in that order. A device that presents a bootable but faulty first stage can prevent fallback. Use the carrier UART connections above. Configure 115200 baud, 8 data bits, no parity, one stop bit and no flow control. Arm the host's XMODEM-CRC sender before applying module power.

1. Capture the ROM's repeated XMODEM requests on contact 66. ROM makes ten requests in three seconds. Send a board-specific SRAM-only diagnostic through contact 65 within that window. For a GP device the peripheral download starts at 0x402F0400 and is limited to 109 KB. Use the peripheral-boot binary built for that address. A memory-card MLO has a different boot-image framing.
2. Record transfer completion and a distinctive UART message emitted by the downloaded diagnostic. Have it read and print the raw CONTROL_STATUS before altering pad configuration, then halt in internal SRAM. A ROM request proves transmit activity. The diagnostic's output after a successful download also exercises the receive contact, ROM transfer, and execution in SRAM.
3. Cold boot a board-specific SPL from a known-good MMC0 card. First enable UART logging and verify the PMIC, clock and pinmux settings in SRAM. Next initialize the exact fitted DDR3L part and run address- and data-pattern checks before loading external-memory application code.

Record supply ramps, PWRONRSTn, raw register values, transfer logs, and the tested carrier and module revisions. Repeat from full power removal with the panel attached after panel DVDD and strap isolation are electrically verified. Compare both latched strap words with 0x4017. These are first-article tests pending assembled hardware. [TI AM335x TRM, §§26.1.6 and 26.1.9](https://www.ti.com/lit/ug/spruh73q/spruh73q.pdf)

### Building the UART0 SRAM diagnostic

From the repository root, build the raw GP peripheral-boot payload with GNU Arm binutils. It reads CONTROL_STATUS once, selects UART0's operational register bank, waits for transmit-ready before each byte, prints the raw word and halts. It uses registers and internal SRAM throughout. The ROM must have initialized UART0 by taking the UART boot path.

```sh
arm-none-eabi-as -mcpu=cortex-a8 -o /tmp/pixel-uart0.o module/bringup/uart0-sram.S
arm-none-eabi-ld -Ttext=0x402f0400 -e _start -o /tmp/pixel-uart0.elf /tmp/pixel-uart0.o
arm-none-eabi-objcopy -O binary /tmp/pixel-uart0.elf /tmp/pixel-uart0.bin
```

Send `pixel-uart0.bin` in the cold-boot XMODEM test above. Expect `Pixel Dash SRAM CONTROL_STATUS=0x` followed by eight hexadecimal digits on contact 66. Save the complete word. Decode SYSBOOT as `((word >> 8) & 0xff00) | (word & 0xff)`. Device and revision fields can make two raw words differ while the strap bits agree. Build the MMC0 SPL separately once the module and carrier are ready for power-on testing.
