// The CM4 module's circuit beyond the routed DDR block: CM4 connector pin map, processor pin assignment,
// power (TPS65217D + two SY8089 bucks), Ethernet PHY (LAN8720A), boot straps, pull-ups.
// Sources: CM4 datasheet (pin table, section 2), AM3354 datasheet SPRS717 (ball/mux table), AM335x TRM SPRUH73
// Table 26-7 (SYSBOOT), TPS65217 datasheet SLVSB64I (pins, section 9.2.2.2 case 2: 5 V on AC, no battery),
// LAN8720A datasheet DS00002165B (straps, REF_CLK-out mode).

/** CM4 connector pin -> module net ("" = not connected). Pins 1-100 on J1, 101-200 on J2. */
export const CM4: Record<number, string> = {}
const GND = [1, 2, 7, 8, 13, 14, 22, 23, 32, 33, 42, 43, 52, 53, 59, 60, 65, 66, 71, 74, 98, 107, 108, 113, 114, 119, 120, 125, 126, 131, 132, 137, 138, 144, 150, 155, 156, 161, 162, 167, 168, 173, 174, 179, 180, 185, 186, 191, 192, 197, 198]
for (let p = 1; p <= 200; p++) CM4[p] = ""
for (const p of GND) CM4[p] = "GND"
for (const p of [77, 79, 81, 83, 85, 87]) CM4[p] = "VIN5"
for (const p of [84, 86]) CM4[p] = "VDD_3V3"
for (const p of [88, 90]) CM4[p] = "VDD_1V8"

/** signals: net -> processor ball, pinmux mode, CM4 pin (if any), what it is */
export type Sig = { net: string; ball: string; mode: number; fn: string; cm4?: number }
export const SIGNALS: Sig[] = [
  // 40-pin header functions (Raspberry Pi numbering) on the processor's matching peripherals
  { net: "GPIO2_SDA1", ball: "D18", mode: 3, fn: "I2C2_SDA", cm4: 58 },
  { net: "GPIO3_SCL1", ball: "D17", mode: 3, fn: "I2C2_SCL", cm4: 56 },
  { net: "ID_SD", ball: "E18", mode: 3, fn: "I2C1_SDA (UART0_CTSn pad)", cm4: 36 },
  { net: "ID_SC", ball: "E17", mode: 3, fn: "I2C1_SCL (UART0_RTSn pad)", cm4: 35 },
  { net: "GPIO14_TXD", ball: "E16", mode: 0, fn: "UART0_TXD (boot console)", cm4: 55 },
  { net: "GPIO15_RXD", ball: "E15", mode: 0, fn: "UART0_RXD (boot console)", cm4: 51 },
  { net: "GPIO11_SCLK", ball: "A17", mode: 0, fn: "SPI0_SCLK", cm4: 38 },
  { net: "GPIO10_MOSI", ball: "B16", mode: 0, fn: "SPI0_D1", cm4: 44 },
  { net: "GPIO9_MISO", ball: "B17", mode: 0, fn: "SPI0_D0", cm4: 40 },
  { net: "GPIO8_CE0", ball: "A16", mode: 0, fn: "SPI0_CS0", cm4: 39 },
  { net: "GPIO7_CE1", ball: "C15", mode: 0, fn: "SPI0_CS1", cm4: 37 },
  { net: "GPIO18_PCM_CLK", ball: "A13", mode: 0, fn: "MCASP0_ACLKX", cm4: 49 },
  { net: "GPIO19_PCM_FS", ball: "B13", mode: 0, fn: "MCASP0_FSX", cm4: 26 },
  { net: "GPIO20_PCM_DIN", ball: "B12", mode: 2, fn: "MCASP0_AXR2 (MCASP0_ACLKR pad)", cm4: 27 },
  { net: "GPIO21_PCM_DOUT", ball: "A14", mode: 2, fn: "MCASP0_AXR3 (MCASP0_AHCLKX pad)", cm4: 25 },
  { net: "GPIO12_PWM0", ball: "U14", mode: 6, fn: "EHRPWM1A", cm4: 31 },
  { net: "GPIO13_PWM1", ball: "T14", mode: 6, fn: "EHRPWM1B", cm4: 28 },
  // SD card on the carrier (CM4 Lite pins), MMC0, the boot device
  { net: "SD_CLK", ball: "G17", mode: 0, fn: "MMC0_CLK", cm4: 57 },
  { net: "SD_CMD", ball: "G18", mode: 0, fn: "MMC0_CMD", cm4: 62 },
  { net: "SD_DAT0", ball: "G16", mode: 0, fn: "MMC0_DAT0", cm4: 63 },
  { net: "SD_DAT1", ball: "G15", mode: 0, fn: "MMC0_DAT1", cm4: 67 },
  { net: "SD_DAT2", ball: "F18", mode: 0, fn: "MMC0_DAT2", cm4: 69 },
  { net: "SD_DAT3", ball: "F17", mode: 0, fn: "MMC0_DAT3", cm4: 61 },
  // I2C0: PMIC, and the CM4's SDA0/SCL0 carrier bus
  { net: "I2C0_SDA", ball: "C17", mode: 0, fn: "I2C0_SDA", cm4: 82 },
  { net: "I2C0_SCL", ball: "C16", mode: 0, fn: "I2C0_SCL", cm4: 80 },
  // USB 2.0 OTG
  { net: "USB0_DP", ball: "N17", mode: 0, fn: "USB0_DP", cm4: 105 },
  { net: "USB0_DM", ball: "N18", mode: 0, fn: "USB0_DM", cm4: 103 },
  { net: "USB0_ID", ball: "P16", mode: 0, fn: "USB0_ID", cm4: 101 },
  { net: "USB0_VBUS", ball: "P15", mode: 0, fn: "USB0_VBUS (from the module's 5 V through R_VBUS)" },
  // reset and PMIC control
  { net: "PWRONRSTn", ball: "B15", mode: 0, fn: "power-on reset from PMIC PGOOD (1 kOhm), CM4 RUN_PG", cm4: 92 },
  { net: "RTC_PWRONRSTn", ball: "B5", mode: 0, fn: "from PMIC LDO_PGOOD" },
  { net: "PMIC_POWER_EN", ball: "C6", mode: 0, fn: "to PMIC PWR_EN" },
  { net: "EXT_WAKEUP", ball: "C5", mode: 0, fn: "from PMIC nWAKEUP" },
  { net: "NMIn", ball: "B18", mode: 0, fn: "EXTINTn, from PMIC nINT" },
  // RMII to the LAN8720A
  { net: "RMII_REFCLK", ball: "H18", mode: 0, fn: "RMII1_REF_CLK (50 MHz from the PHY)" },
  { net: "RMII_CRS_DV", ball: "H17", mode: 1, fn: "RMII1_CRS_DV" },
  { net: "RMII_RXER", ball: "J15", mode: 1, fn: "RMII1_RXER" },
  { net: "RMII_TXEN", ball: "J16", mode: 1, fn: "RMII1_TXEN" },
  { net: "RMII_TXD0", ball: "K17", mode: 1, fn: "RMII1_TXD0" },
  { net: "RMII_TXD1", ball: "K16", mode: 1, fn: "RMII1_TXD1" },
  { net: "RMII_RXD0", ball: "M16", mode: 1, fn: "RMII1_RXD0" },
  { net: "RMII_RXD1", ball: "L15", mode: 1, fn: "RMII1_RXD1" },
  { net: "MDIO", ball: "M17", mode: 0, fn: "MDIO_DATA" },
  { net: "MDC", ball: "M18", mode: 0, fn: "MDIO_CLK" },
  // boot straps: LCD_DATA[15:0] = SYSBOOT[15:0]
  ...Array.from({ length: 16 }, (_, i) => ({ net: `SYSBOOT${i}`, ball: ["R1", "R2", "R3", "R4", "T1", "T2", "T3", "T4", "U1", "U2", "U3", "U4", "V2", "V3", "V4", "T5"][i], mode: 0, fn: `LCD_DATA${i} (SYSBOOT${i}), strap` })),
]
/** plain GPIOs (mode 7): CM4 pins whose ball is chosen by plan.ts from POOL (shortest assignment) */
export const GPIO_PINS: Record<string, number> = {
  GPIO4: 54, GPIO5: 34, GPIO6: 30, GPIO16: 29, GPIO17: 50, GPIO22: 46, GPIO23: 47, GPIO24: 45, GPIO25: 41, GPIO26: 24, GPIO27: 48,
  LED_nACT: 21, LED_nPWR: 95, CAM_GPIO: 97, SD_PWR_ON: 75, nEXTRST: 100, ETH_nLED1: 19, ETH_nLED2: 17, ETH_nLED3: 15,
}
/** GPIO-capable balls left free by the functions above (mode 7 = gpio) */
export const POOL = ["A15", "C12", "C13", "C18", "D14", "F15", "F16", "H16", "J17", "J18", "K15", "K18", "L16", "L17", "L18", "R13", "V14", "R14", "V15", "U15", "T15", "V16", "U16", "T16", "V17", "U18", "T13", "V12"]
/** a GPIO that is not a CM4 pin */
export const EXTRA_GPIO = ["PHY_nRST"]
for (const s of SIGNALS) if (s.cm4) CM4[s.cm4] = s.net
for (const [n, p] of Object.entries(GPIO_PINS)) CM4[p] = n
// Ethernet: TX pair on CM4 pair 0 (RJ45 1/2), RX pair on pair 1 (RJ45 3/6); pairs 2 and 3 are not used at 100 Mbit/s
Object.assign(CM4, { 12: "ETH_TX_P", 10: "ETH_TX_N", 4: "ETH_RX_P", 6: "ETH_RX_N", 93: "nRPIBOOT", 99: "GLOBAL_EN" })

/** two-pin passives and ICs: ref -> part type, pin -> net */
export type Part = { ref: string; part: string; nets: Record<string, string>; note?: string }
export const PARTS: Part[] = []
const P = (ref: string, part: string, nets: Record<string, string>, note?: string) => PARTS.push({ ref, part, nets, note })
const two = (ref: string, part: string, a: string, b: string, note?: string) => P(ref, part, { pin1: a, pin2: b }, note)
// ---- TPS65217D (5 V on AC, battery pins tied and open, TS open; datasheet 9.2.2.2 case 2) ----
P("U_PMIC", "PMIC", {
  pin1: "LDO2_OUT", pin2: "SYS", pin3: "VDDS_RTC", pin4: "PMIC_BAT", pin5: "PMIC_BAT", pin6: "PMIC_BAT", pin7: "SYS", pin8: "SYS", pin9: "PMIC_POWER_EN", pin10: "VIN5", pin11: "", pin12: "GND",
  pin13: "EXT_WAKEUP", pin14: "", pin15: "", pin16: "", pin17: "", pin18: "VDDS_RTC", pin19: "VDDS_DDR", pin20: "LX1", pin21: "SYS", pin22: "SYS", pin23: "LX2", pin24: "VDD_MPU",
  pin25: "PMIC_PB", pin26: "PMIC_PGOOD", pin27: "I2C0_SDA", pin28: "I2C0_SCL", pin29: "VDD_CORE", pin30: "GND", pin31: "LX3", pin32: "SYS", pin33: "", pin34: "", pin35: "", pin36: "",
  pin37: "", pin38: "", pin39: "SYS", pin40: "LDO3_OUT", pin41: "GND", pin42: "SYS", pin43: "LDO4_OUT", pin44: "GLOBAL_EN", pin45: "NMIn", pin46: "RTC_PWRONRSTn", pin47: "PMIC_BYPASS", pin48: "PMIC_INTLDO", pin49: "GND",
}, "TPS65217D: DCDC1 1.35 V VDDS_DDR, DCDC2 1.1 V VDD_MPU, DCDC3 1.1 V VDD_CORE, LDO1 1.8 V VDDS_RTC; LDO3/LDO4 switch the 1.8 V/3.3 V bucks on in their sequence slots")
two("L_DCDC1", "IND", "LX1", "VDDS_DDR"); two("L_DCDC2", "IND", "LX2", "VDD_MPU"); two("L_DCDC3", "IND", "LX3", "VDD_CORE")
two("C_DCDC1", "C22U_0603", "VDDS_DDR", "GND"); two("C_DCDC2", "C22U_0603", "VDD_MPU", "GND"); two("C_DCDC3", "C22U_0603", "VDD_CORE", "GND")
two("C_SYS", "C22U_0805", "SYS", "GND"); two("C_VIN12", "C10U_0603", "SYS", "GND"); two("C_VIN3", "C10U_0603", "SYS", "GND"); two("C_VINLDO", "C4U7_0402", "SYS", "GND")
two("C_AC", "C4U7_0603", "VIN5", "GND"); two("C_LDO1", "C2U2_0402", "VDDS_RTC", "GND"); two("C_LDO2", "C2U2_0402", "LDO2_OUT", "GND")
two("C_LDO3", "C2U2_0402", "LDO3_OUT", "GND"); two("C_LDO4", "C2U2_0402", "LDO4_OUT", "GND")
two("C_INTLDO", "C100N_0402", "PMIC_INTLDO", "GND"); two("C_BYPASS", "C10U_0402", "PMIC_BYPASS", "GND")
two("R_PB", "R100K", "PMIC_PB", "SYS", "PB_IN high: no push-button (the AC input wakes the PMIC)")
two("R_GLOBAL_EN", "R100K", "GLOBAL_EN", "SYS", "nRESET pull-up; the carrier pulls GLOBAL_EN low to power off (CM4: 100 k to +5 V)")
two("R_WAKE", "R100K", "EXT_WAKEUP", "VDDS_RTC"); two("R_INT", "R10K", "NMIn", "VDD_3V3")
two("R_PGOOD", "R1K", "PMIC_PGOOD", "PWRONRSTn", "lets the carrier pull RUN_PG low (CM4: through 220 ohm) against the push-pull PGOOD")
two("R_SDA0", "R2K2", "I2C0_SDA", "VDD_3V3"); two("R_SCL0", "R2K2", "I2C0_SCL", "VDD_3V3")
// ---- 3.3 V and 1.8 V bucks from 5 V, switched on by the PMIC's LDO4 / LDO3 outputs ----
for (const [b, en, out, rt, rb] of [["3V3", "LDO4_OUT", "VDD_3V3", "R100K", "R22K"], ["1V8", "LDO3_OUT", "VDD_1V8", "R200K", "R100K"]]) {
  P(`U_${b}`, "BUCK", { pin1: en, pin2: "GND", pin3: `LX_${b}`, pin4: "VIN5", pin5: `FB_${b}` }, `SY8089A1AAC ${b}`)
  two(`L_${b}`, "IND", `LX_${b}`, out); two(`C_IN_${b}`, "C10U_0603", "VIN5", "GND"); two(`C_OUT_${b}`, "C22U_0603", out, "GND")
  two(`R_FBT_${b}`, rt, out, `FB_${b}`); two(`R_FBB_${b}`, rb, `FB_${b}`, "GND")
}
// ---- LAN8720A, REF_CLK-out mode (nINTSEL low), PHY address 0, MODE 111 from its internal pull-ups ----
P("U_PHY", "PHY", {
  pin1: "VDD_3V3", pin2: "PHY_LED2", pin3: "", pin4: "PHY_XO", pin5: "PHY_XI", pin6: "PHY_VDDCR", pin7: "RMII_RXD1", pin8: "RMII_RXD0", pin9: "VDD_3V3", pin10: "RMII_RXER", pin11: "RMII_CRS_DV", pin12: "MDIO",
  pin13: "MDC", pin14: "RMII_REFCLK", pin15: "PHY_nRST", pin16: "RMII_TXEN", pin17: "RMII_TXD0", pin18: "RMII_TXD1", pin19: "VDD_3V3", pin20: "ETH_TX_N", pin21: "ETH_TX_P", pin22: "ETH_RX_N", pin23: "ETH_RX_P", pin24: "PHY_RBIAS", pin25: "GND",
}, "LAN8720A 10/100 PHY")
P("Y_PHY", "XTAL_25M", { pin1: "PHY_XI", pin3: "PHY_XO", pin2: "GND", pin4: "GND" })
two("C_PHY_XI", "C15P_0402", "PHY_XI", "GND"); two("C_PHY_XO", "C15P_0402", "PHY_XO", "GND")
two("R_PHY_RBIAS", "R12K1", "PHY_RBIAS", "GND"); two("R_PHY_LED2", "R10K", "PHY_LED2", "GND", "nINTSEL low: pin 14 is the 50 MHz REF_CLK output")
two("R_PHY_RST", "R10K", "PHY_nRST", "GND", "PHY held in reset until software releases it (straps then come from the PHY's own pull-ups)")
two("R_MDIO", "R1K5", "MDIO", "VDD_3V3")
for (const n of ["ETH_TX_P", "ETH_TX_N", "ETH_RX_P", "ETH_RX_N"]) two(`R_${n}`, "R49R9", n, "VDD_3V3", "LAN8720A line termination and bias")
two("C_PHY_VDDCR1", "C1U_0402", "PHY_VDDCR", "GND"); two("C_PHY_VDDCR2", "C470P_0402", "PHY_VDDCR", "GND")
for (const n of ["1", "2", "3"]) two(`C_PHY_${n}`, "C100N_0402", "VDD_3V3", "GND"); two("C_PHY_BULK", "C4U7_0402", "VDD_3V3", "GND")
// ---- boot straps: SYSBOOT = 0x4017 (24 MHz; MMC0, SPI0, UART0, USB0); nRPIBOOT low clears bits 2 and 0: 10010b = NAND, NANDI2C, USB0, UART0 ----
const WORD = 0x4017
for (let i = 0; i < 16; i++) two(`R_SB${i}`, "R10K", `SYSBOOT${i}`, WORD & (1 << i) ? "VDD_3V3" : "GND")
two("R_RPB0", "R1K", "SYSBOOT0", "nRPIBOOT"); two("R_RPB2", "R1K", "SYSBOOT2", "nRPIBOOT")
// ---- pull-ups ----
for (const n of ["SD_CMD", "SD_DAT0", "SD_DAT1", "SD_DAT2", "SD_DAT3"]) two(`R_${n}`, "R10K", n, "VDD_3V3")
two("R_SD_PWR_ON", "R10K", "SD_PWR_ON", "VDD_3V3", "CM4: pull-up so the carrier's SD power switch defaults to on")
two("R_SDA2", "R2K2", "GPIO2_SDA1", "VDD_3V3"); two("R_SCL2", "R2K2", "GPIO3_SCL1", "VDD_3V3")
two("R_ID_SD", "R4K7", "ID_SD", "VDD_3V3"); two("R_ID_SC", "R4K7", "ID_SC", "VDD_3V3")
two("R_VBUS", "R0", "VIN5", "USB0_VBUS", "USB0 VBUS sense from the module's 5 V (CM4 carriers do not bring VBUS to the module)")

export const PLANE_NETS = ["GND", "VDDS_DDR", "VDD_CORE", "VDD_MPU", "VDD_3V3", "VDD_1V8", "VDDS_RTC", "DDR_VREF", "VIN5", "SYS"]
